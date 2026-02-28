"""
Reflecting Pool - Plugin Loader

Discovers and loads plugins from the plugins/ directory.
Plugins register themselves using the @register decorator.
"""

import importlib.util
import sys
import traceback
from dataclasses import dataclass
from pathlib import Path
from typing import Callable, List

import pandas as pd


# ---------------------------------------------------------------------------
# Plugin context (stable interface passed to every plugin)
# ---------------------------------------------------------------------------

@dataclass
class PluginContext:
    """Everything a plugin needs to render its content.

    Fields may be added in future versions but existing fields
    will not be removed or have their types changed.
    """

    df: pd.DataFrame
    """Filtered journal DataFrame. Columns: date, text, word_count,
    char_count, sentiment."""

    rag_db_path: str
    """Path to the RAG vector database directory."""

    root: Path
    """Project root directory (where app.py lives)."""

    session_log: Callable
    """session_log(message: str) -> None"""

    section_header: Callable
    """section_header(title: str, help_text: str) -> None"""

    extract_common_words: Callable
    """extract_common_words(texts, n_words=30) -> List[Tuple[str, int]]"""

    get_sentiment: Callable
    """get_sentiment(text: str) -> float  (VADER compound score)"""

    get_rag: Callable
    """get_rag(db_path: str) -> JournalRAG  (cached instance)"""

    load_theme: Callable
    """load_theme() -> dict"""


# ---------------------------------------------------------------------------
# Plugin registry
# ---------------------------------------------------------------------------

@dataclass
class PluginInfo:
    """Metadata for a registered plugin."""
    name: str
    render: Callable
    kind: str = "tab"           # "tab" or "sidebar"
    order: int = 100
    needs_df: bool = True
    description: str = ""
    source_file: str = ""


_registry: List[PluginInfo] = []


def register(
    name: str,
    *,
    kind: str = "tab",
    order: int = 100,
    needs_df: bool = True,
    description: str = "",
):
    """Decorator that registers a function as a plugin.

    Usage::

        from plugin_loader import register

        @register("My Plugin", description="Does something cool")
        def render(ctx):
            import streamlit as st
            st.write("Hello from my plugin!")
    """
    def decorator(func: Callable) -> Callable:
        _registry.append(PluginInfo(
            name=name,
            render=func,
            kind=kind,
            order=order,
            needs_df=needs_df,
            description=description,
        ))
        return func
    return decorator


# ---------------------------------------------------------------------------
# Plugin discovery
# ---------------------------------------------------------------------------

def discover_plugins(plugins_dir: Path) -> List[PluginInfo]:
    """Scan *plugins_dir* for .py files, import each, and return
    the collected PluginInfo objects sorted by *order*.

    Files starting with ``_`` are skipped (use them as helpers).
    Errors are caught per-file so one broken plugin cannot crash the app.
    """
    _registry.clear()

    if not plugins_dir.is_dir():
        return []

    before = 0
    for py_file in sorted(plugins_dir.glob("*.py")):
        if py_file.name.startswith("_"):
            continue

        module_name = f"rp_plugin_{py_file.stem}"
        try:
            spec = importlib.util.spec_from_file_location(module_name, str(py_file))
            module = importlib.util.module_from_spec(spec)
            sys.modules[module_name] = module
            spec.loader.exec_module(module)

            # Tag newly registered plugins with their source file
            for info in _registry[before:]:
                if not info.source_file:
                    info.source_file = py_file.name
        except Exception:
            import streamlit as st
            st.sidebar.warning(
                f"Plugin failed to load: **{py_file.name}**\n\n"
                f"```\n{traceback.format_exc()[-500:]}\n```"
            )

        before = len(_registry)

    return sorted(_registry, key=lambda p: p.order)

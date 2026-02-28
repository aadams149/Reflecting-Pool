"""Tests for the plugin loader system."""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

import pytest
import pandas as pd
from plugin_loader import register, discover_plugins, PluginContext, PluginInfo, _registry


class TestRegisterDecorator:
    def setup_method(self):
        _registry.clear()

    def test_register_adds_to_registry(self):
        @register("Test Plugin", description="A test")
        def render(ctx):
            pass

        assert len(_registry) == 1
        assert _registry[0].name == "Test Plugin"
        assert _registry[0].description == "A test"
        assert _registry[0].kind == "tab"

    def test_register_sidebar(self):
        @register("Sidebar Plugin", kind="sidebar")
        def render(ctx):
            pass

        assert _registry[0].kind == "sidebar"

    def test_register_custom_order(self):
        @register("Plugin A", order=50)
        def render_a(ctx):
            pass

        @register("Plugin B", order=10)
        def render_b(ctx):
            pass

        assert _registry[0].order == 50
        assert _registry[1].order == 10

    def test_register_preserves_function(self):
        @register("Preserved")
        def my_render(ctx):
            return "hello"

        assert my_render(None) == "hello"


class TestDiscoverPlugins:
    def test_empty_directory(self, tmp_path):
        plugins = discover_plugins(tmp_path)
        assert plugins == []

    def test_nonexistent_directory(self, tmp_path):
        plugins = discover_plugins(tmp_path / "nope")
        assert plugins == []

    def test_skips_underscore_files(self, tmp_path):
        (tmp_path / "_helper.py").write_text("x = 1", encoding="utf-8")
        plugins = discover_plugins(tmp_path)
        assert plugins == []

    def test_loads_valid_plugin(self, tmp_path):
        plugin_code = (
            "from plugin_loader import register\n\n"
            '@register("Dynamic Test", order=42, description="loaded dynamically")\n'
            "def render(ctx):\n"
            "    pass\n"
        )
        (tmp_path / "test_dynamic.py").write_text(plugin_code, encoding="utf-8")
        plugins = discover_plugins(tmp_path)
        assert len(plugins) == 1
        assert plugins[0].name == "Dynamic Test"
        assert plugins[0].order == 42

    def test_broken_plugin_does_not_crash(self, tmp_path):
        (tmp_path / "broken.py").write_text(
            "raise RuntimeError('boom')", encoding="utf-8"
        )
        # Should not raise
        plugins = discover_plugins(tmp_path)
        assert plugins == []

    def test_sorted_by_order(self, tmp_path):
        (tmp_path / "aa.py").write_text(
            "from plugin_loader import register\n\n"
            '@register("Z Plugin", order=200)\n'
            "def render(ctx): pass\n",
            encoding="utf-8",
        )
        (tmp_path / "bb.py").write_text(
            "from plugin_loader import register\n\n"
            '@register("A Plugin", order=5)\n'
            "def render(ctx): pass\n",
            encoding="utf-8",
        )
        plugins = discover_plugins(tmp_path)
        assert plugins[0].name == "A Plugin"
        assert plugins[1].name == "Z Plugin"


class TestPluginContext:
    def test_instantiation(self):
        ctx = PluginContext(
            df=pd.DataFrame(),
            rag_db_path="/tmp/db",
            root=Path("/tmp"),
            session_log=lambda msg: None,
            section_header=lambda t, h: None,
            extract_common_words=lambda texts, n_words=30: [],
            get_sentiment=lambda text: 0.0,
            get_rag=lambda db: None,
            load_theme=lambda: {},
        )
        assert ctx.rag_db_path == "/tmp/db"
        assert ctx.df.empty

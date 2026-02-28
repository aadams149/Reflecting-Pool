# Reflecting Pool Plugins

Drop a `.py` file into this directory and it becomes a tab (or sidebar widget) in the app. No other configuration needed.

## Minimal Example

```python
from plugin_loader import register

@register("My Plugin", description="Does something cool")
def render(ctx):
    import streamlit as st
    st.write(f"You have {len(ctx.df)} entries!")
```

That's it. Restart the app and your plugin appears as a new tab.

## The `ctx` Object

Every plugin receives a single `PluginContext` argument with these fields:

| Field | Type | Description |
|-------|------|-------------|
| `ctx.df` | `pd.DataFrame` | Filtered journal entries. Columns: `date`, `text`, `word_count`, `char_count`, `sentiment` |
| `ctx.rag_db_path` | `str` | Path to the RAG vector database directory |
| `ctx.root` | `Path` | Project root directory (where `app.py` lives) |
| `ctx.session_log` | `Callable` | `session_log(message)` - write to the session log |
| `ctx.section_header` | `Callable` | `section_header(title, help_text)` - styled section header |
| `ctx.extract_common_words` | `Callable` | `extract_common_words(texts, n_words=30)` - returns `[(word, count), ...]` |
| `ctx.get_sentiment` | `Callable` | `get_sentiment(text)` - VADER compound score (-1 to +1) |
| `ctx.get_rag` | `Callable` | `get_rag(db_path)` - cached RAG instance for semantic search |
| `ctx.load_theme` | `Callable` | `load_theme()` - current theme dict with colors, fonts, etc. |

## `@register` Options

```python
@register(
    "Tab Name",             # Display name (required)
    kind="tab",             # "tab" (default) or "sidebar"
    order=100,              # Sort position (lower = further left)
    needs_df=True,          # If True (default), plugin is skipped when no data
    description="...",      # Shown in error messages and logs
)
```

The four sample plugins use orders 110-140. Pick any number to control where your tab appears relative to others.

## Guidelines

1. **Import heavy libraries inside `render()`**, not at module level. This keeps app startup fast and lets the plugin fail gracefully if a dependency is missing.

2. **Check `ctx.df.empty`** early and show a friendly `st.info()` message.

3. **Use unique widget keys** to avoid collisions with other plugins. Prefix with your plugin name (e.g., `key="myplugin_slider"`).

4. **Catch `ImportError`** for optional dependencies and show install instructions:
   ```python
   try:
       import fancy_lib
   except ImportError:
       st.info("Install `fancy-lib` for this feature:\n\n```\npip install fancy-lib\n```")
       return
   ```

5. **Errors are contained.** If your plugin crashes, a traceback is shown in its tab but the rest of the app keeps working.

6. **Files starting with `_`** are skipped by the loader. Use them as helper modules (e.g., `_utils.py`) that your plugins can import.

## Theme Integration

Use `ctx.load_theme()` to match the user's chosen appearance:

```python
theme = ctx.load_theme()
bg = theme.get("bg_color", "#ffffff")
text = theme.get("text_color", "#111111")
accent = theme.get("link_color", "#0066cc")
```

Available theme keys: `body_font`, `heading_font`, `font_size`, `line_height`, `text_color`, `heading_color`, `link_color`, `metric_color`, `bg_color`, `sidebar_bg`, `content_padding`, `block_gap`, `metric_font_size`, `border_radius`.

## Sample Plugins

| File | Tab | What It Does |
|------|-----|-------------|
| `word_cloud.py` | Word Cloud | Visual word frequency (uses `wordcloud` lib or HTML fallback) |
| `calendar_view.py` | Calendar | Month calendar grid with entry day highlights and preview |
| `day_of_week_sentiment.py` | Day-of-Week | Sentiment and writing volume by weekday |
| `full_entry_viewer.py` | Read Entries | Full-text reader with prev/next navigation |

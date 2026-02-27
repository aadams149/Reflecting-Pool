#!/usr/bin/env python3
"""
Reflecting Pool - Journal Analytics & Search

Single unified Streamlit application for journal analysis, search, and chat.
Combines the analytics dashboard and chat interface into one app.
"""

import sys
from pathlib import Path

# Resolve project root from this file's location
ROOT = Path(__file__).resolve().parent

# Make submodules importable
sys.path.insert(0, str(ROOT / "rag"))
sys.path.insert(0, str(ROOT / "dashboard"))

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import json
import re
from datetime import datetime, timedelta
from collections import Counter
from typing import Dict, List, Tuple

# Default paths (resolved from project root)
DEFAULT_OCR_DIR = str(ROOT / "ocr" / "ocr_output")
DEFAULT_RAG_DB = str(ROOT / "rag" / "vector_db")
THEME_FILE = ROOT / ".reflecting_pool_theme.json"


# ---------------------------------------------------------------------------
# Theme persistence
# ---------------------------------------------------------------------------

_THEME_DEFAULTS = {
    "body_font": "Georgia", "heading_font": "Garamond",
    "font_size": 16, "line_height": 1.6,
    "text_color": "#262730", "heading_color": "#0f0f23",
    "link_color": "#636EFA", "metric_color": "#1a1a2e",
    "bg_color": "#ffffff", "sidebar_bg": "#f8f9fa",
    "content_padding": 1.0, "block_gap": 1.5,
    "metric_font_size": 14, "border_radius": 8,
}


def load_theme() -> dict:
    """Load saved theme or return defaults."""
    if THEME_FILE.exists():
        try:
            with open(THEME_FILE, "r") as f:
                saved = json.load(f)
            return {**_THEME_DEFAULTS, **saved}
        except (json.JSONDecodeError, OSError):
            pass
    return dict(_THEME_DEFAULTS)


def save_theme(theme: dict):
    """Persist the current theme to disk."""
    with open(THEME_FILE, "w") as f:
        json.dump(theme, f, indent=2)


def _inject_theme_css(t: dict):
    """Inject the saved theme as page-wide CSS."""
    st.markdown(f"""<style>
html, body, [class*="css"] {{
    font-family: '{t["body_font"]}', serif !important;
    font-size: {t["font_size"]}px !important;
    line-height: {t["line_height"]} !important;
    color: {t["text_color"]} !important;
    background-color: {t["bg_color"]} !important;
}}
h1, h2, h3, h4, h5, h6,
.stMarkdown h1, .stMarkdown h2, .stMarkdown h3 {{
    font-family: '{t["heading_font"]}', serif !important;
    color: {t["heading_color"]} !important;
}}
a, a:visited {{ color: {t["link_color"]} !important; }}
[data-testid="stMetricValue"] {{
    color: {t["metric_color"]} !important;
    font-family: '{t["heading_font"]}', serif !important;
}}
[data-testid="stMetricLabel"] {{
    font-size: {t["metric_font_size"]}px !important;
    color: {t["text_color"]} !important; opacity: 0.75;
}}
[data-testid="stSidebar"] {{ background-color: {t["sidebar_bg"]} !important; }}
[data-testid="stSidebar"] * {{ color: {t["text_color"]} !important; }}
.block-container {{
    padding-left: {t["content_padding"]}rem !important;
    padding-right: {t["content_padding"]}rem !important;
}}
.element-container {{ margin-bottom: {t["block_gap"] / 2}rem !important; }}
[data-testid="stExpander"] {{ border-radius: {t["border_radius"]}px !important; }}
[data-baseweb="tab-list"] {{ font-family: '{t["body_font"]}', serif !important; }}
</style>""", unsafe_allow_html=True)


# ---------------------------------------------------------------------------
# Session logging
# ---------------------------------------------------------------------------

def _log_path() -> Path:
    """Return the session log file path (logs/ folder, timestamped per session)."""
    logs_dir = ROOT / "logs"
    logs_dir.mkdir(exist_ok=True)
    # One log file per session, keyed by the session start time
    if "log_filename" not in st.session_state:
        ts = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        st.session_state.log_filename = f"session_{ts}.log"
    return logs_dir / st.session_state.log_filename


def session_log(message: str):
    """Append a timestamped line to the session log if logging is active."""
    if not st.session_state.get("session_logging"):
        return
    try:
        with open(_log_path(), "a", encoding="utf-8") as f:
            f.write(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] {message}\n")
    except OSError:
        pass

# ---------------------------------------------------------------------------
# Page config
# ---------------------------------------------------------------------------
st.set_page_config(
    page_title="Reflecting Pool",
    page_icon=str(ROOT / "favicon.ico"),
    layout="wide",
    initial_sidebar_state="expanded",
)

# ---------------------------------------------------------------------------
# Data loading
# ---------------------------------------------------------------------------

@st.cache_data
def load_journal_data(ocr_output_dir: str) -> pd.DataFrame:
    """Load journal entries from OCR output directory."""
    ocr_path = Path(ocr_output_dir)
    text_dir = ocr_path / "text"
    metadata_dir = ocr_path / "metadata"

    if not text_dir.exists() or not metadata_dir.exists():
        return pd.DataFrame()

    entries = []
    for text_file in text_dir.glob("*.txt"):
        metadata_file = metadata_dir / f"{text_file.stem}.json"
        if not metadata_file.exists():
            continue

        text = text_file.read_text(encoding="utf-8").strip()
        with open(metadata_file, "r", encoding="utf-8") as f:
            metadata = json.load(f)

        if not text:
            continue

        entries.append({
            "date": metadata["entry_date"],
            "text": text,
            "word_count": len(text.split()),
            "char_count": len(text),
        })

    if not entries:
        return pd.DataFrame()

    df = pd.DataFrame(entries)
    df["date"] = pd.to_datetime(df["date"], format="mixed")
    return df.sort_values("date")


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def get_sentiment(text: str) -> float:
    """VADER sentiment score (-1 to +1)."""
    from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
    analyzer = SentimentIntensityAnalyzer()
    return analyzer.polarity_scores(text)["compound"]


@st.cache_data(show_spinner="Analyzing sentiment...")
def _add_sentiment(df: pd.DataFrame) -> pd.DataFrame:
    """Compute and cache sentiment scores for a dataframe."""
    if "sentiment" in df.columns:
        return df
    df = df.copy()
    df["sentiment"] = df["text"].apply(get_sentiment)
    return df


def section_header(title: str, help_text: str):
    """Section header with a collapsible help tooltip."""
    st.header(title)
    with st.expander("What does this show?"):
        st.markdown(help_text)


def extract_common_words(texts: List[str], n_words: int = 30) -> List[Tuple[str, int]]:
    """Extract most common meaningful words, filtering stop words."""
    stop_words = {
        "the", "a", "an", "and", "or", "but", "in", "on", "at", "to", "for",
        "of", "with", "by", "from", "as", "is", "was", "were", "been", "be",
        "have", "has", "had", "do", "does", "did", "will", "would", "could",
        "should", "may", "might", "must", "can", "i", "me", "my", "mine",
        "you", "your", "yours", "he", "him", "his", "she", "her", "hers",
        "it", "its", "we", "us", "our", "ours", "they", "them", "their",
        "theirs", "this", "that", "these", "those", "am", "are", "was",
        "were", "been", "being", "have", "has", "had", "having", "do",
        "does", "did", "doing", "just", "so", "than", "too", "very",
        "about", "after", "again", "also", "back", "been", "before",
        "being", "between", "both", "came", "come", "each", "even",
        "every", "first", "get", "got", "into", "know", "like", "made",
        "make", "many", "more", "most", "much", "need", "never", "next",
        "now", "only", "other", "over", "part", "really", "right", "same",
        "some", "still", "such", "take", "tell", "then", "there", "thing",
        "think", "time", "want", "well", "went", "what", "when", "where",
        "which", "while", "who", "will", "with", "work", "year",
    }
    all_words = []
    for text in texts:
        words = re.findall(r"\b\w+\b", text.lower())
        all_words.extend(w for w in words if w not in stop_words and len(w) > 3)
    return Counter(all_words).most_common(n_words)


@st.cache_resource
def _get_rag(db_path: str):
    """Lazily import and instantiate JournalRAG (cached so embeddings load once)."""
    from journal_rag import JournalRAG
    return JournalRAG(db_path=db_path)


# ---------------------------------------------------------------------------
# Sidebar
# ---------------------------------------------------------------------------

def render_sidebar(df: pd.DataFrame):
    """Render sidebar controls and return filtered dataframe + config."""
    st.sidebar.header("Configuration")

    ocr_output_dir = st.sidebar.text_input(
        "OCR Output Directory",
        value=DEFAULT_OCR_DIR,
        help="Path to your OCR output directory",
    )
    rag_db_path = st.sidebar.text_input(
        "RAG Database Path",
        value=DEFAULT_RAG_DB,
        help="Path to your RAG vector database",
    )

    # --- RAG sidebar search ---
    st.sidebar.header("Search")

    search_query = st.sidebar.text_input(
        "Search Query",
        placeholder="e.g., feeling anxious about work",
        help="Semantic search across all journal entries",
    )

    if st.sidebar.button("Search", type="primary"):
        if search_query:
            session_log(f"Sidebar search: {search_query}")
            try:
                with st.spinner("Searching..."):
                    rag = _get_rag(rag_db_path)
                    results = rag.search(search_query, n_results=5)
                if results:
                    st.sidebar.success(f"Found {len(results)} results")
                    for i, result in enumerate(results, 1):
                        with st.sidebar.expander(f"{i}. {result['date']}"):
                            st.text(result["text"][:200] + "...")
                else:
                    st.sidebar.warning("No results found")
            except FileNotFoundError:
                st.sidebar.error("RAG database not found. Run ingestion first.")
            except Exception as e:
                st.sidebar.error(f"Search error: {e}")
        else:
            st.sidebar.warning("Please enter a search query")

    if st.sidebar.button("Ingest to RAG"):
        try:
            with st.spinner("Ingesting journal entries into RAG database..."):
                rag = _get_rag(rag_db_path)
                count = rag.ingest_from_ocr(ocr_output_dir)
            st.sidebar.success(f"Ingested {count} entries!")
        except Exception as e:
            st.sidebar.error(f"Ingestion error: {e}")

    # --- Date filter ---
    filtered_df = df
    if not df.empty:
        st.sidebar.header("Filters")
        min_date = df["date"].min().date()
        max_date = df["date"].max().date()
        date_range = st.sidebar.date_input(
            "Date Range",
            value=(min_date, max_date),
            min_value=min_date,
            max_value=max_date,
        )
        if len(date_range) == 2:
            mask = (df["date"].dt.date >= date_range[0]) & (df["date"].dt.date <= date_range[1])
            filtered_df = df[mask]

    # --- Session logging ---
    st.sidebar.header("Session Log")
    if "session_logging" not in st.session_state:
        st.session_state.session_logging = False

    logging_on = st.sidebar.toggle(
        "Enable session log",
        value=st.session_state.session_logging,
        help=f"Writes activity to {_log_path()}",
    )
    if logging_on != st.session_state.session_logging:
        st.session_state.session_logging = logging_on
        if logging_on:
            session_log("Session logging started")
        else:
            session_log("Session logging stopped")

    if st.session_state.session_logging:
        log_file = _log_path()
        st.sidebar.caption(f"Logging to: {log_file}")
        if log_file.exists():
            if "show_log" not in st.session_state:
                st.session_state.show_log = False
            if st.sidebar.button("Hide log" if st.session_state.show_log else "View log"):
                st.session_state.show_log = not st.session_state.show_log
                st.rerun()
            if st.session_state.show_log:
                st.sidebar.code(log_file.read_text(encoding="utf-8")[-2000:], language="text")

    return ocr_output_dir, rag_db_path, filtered_df


# ---------------------------------------------------------------------------
# Tab: Analytics
# ---------------------------------------------------------------------------

def tab_analytics(df: pd.DataFrame):
    section_header("Sentiment Over Time", """
        Tracks the emotional tone of each entry using VADER sentiment analysis.
        Score runs from **-1** (most negative) to **+1** (most positive).
        The dashed grey line marks neutral (0). Hover over a dot for the exact
        date and score.
    """)

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=df["date"], y=df["sentiment"],
        mode="lines+markers", name="Sentiment",
        line=dict(color="rgb(99, 110, 250)", width=2),
        marker=dict(size=6),
    ))
    fig.add_hline(y=0, line_dash="dash", line_color="gray", opacity=0.5)
    fig.update_layout(
        xaxis_title="Date", yaxis_title="Sentiment Score",
        yaxis_range=[-1.1, 1.1], height=400, hovermode="x unified",
    )
    st.plotly_chart(fig, use_container_width=True)

    # --- Writing consistency ---
    section_header("Writing Consistency", """
        **Left**: entries per month. **Right**: word count per entry over time.
    """)

    col1, col2 = st.columns(2)
    with col1:
        monthly = df.groupby(df["date"].dt.to_period("M")).size()
        monthly.index = monthly.index.astype(str)
        fig_m = px.bar(x=monthly.index, y=monthly.values,
                       labels={"x": "Month", "y": "Entries"}, title="Entries per Month")
        fig_m.update_traces(marker_color="rgb(99, 110, 250)")
        st.plotly_chart(fig_m, use_container_width=True)

    with col2:
        fig_w = px.scatter(df, x="date", y="word_count",
                           title="Words per Entry",
                           labels={"date": "Date", "word_count": "Word Count"})
        st.plotly_chart(fig_w, use_container_width=True)

    # --- Heatmap ---
    section_header("Writing Frequency Heatmap", """
        GitHub-style calendar grid. Rows are days of the week, columns are weeks.
        Darker cells mean more words written that day.
    """)

    date_range_full = pd.date_range(start=df["date"].min(), end=df["date"].max(), freq="D")
    daily_words = df.groupby(df["date"].dt.date)["word_count"].sum()

    heatmap_data = []
    for d in date_range_full:
        heatmap_data.append({
            "date": d,
            "count": daily_words.get(d.date(), 0),
            "day_of_week": d.day_name(),
        })
    hm_df = pd.DataFrame(heatmap_data)
    pivot = hm_df.pivot_table(
        values="count", index="day_of_week",
        columns=hm_df["date"].dt.to_period("W"), fill_value=0,
    )
    day_order = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    pivot = pivot.reindex(day_order)
    pivot.columns = pivot.columns.astype(str)

    fig_hm = px.imshow(pivot, labels=dict(x="Week", y="Day", color="Words"),
                       color_continuous_scale="Blues", aspect="auto")
    fig_hm.update_layout(height=300)
    st.plotly_chart(fig_hm, use_container_width=True)


# ---------------------------------------------------------------------------
# Tab: Words & Themes
# ---------------------------------------------------------------------------

def tab_words(df: pd.DataFrame):
    section_header("Most Common Words", """
        Ranked by frequency with common stop words filtered out.
    """)

    col1, col2 = st.columns([2, 1])
    with col1:
        n_words = st.slider("Number of words to show", 10, 50, 30)
        common = extract_common_words(df["text"].tolist(), n_words=n_words)
        if common:
            words_df = pd.DataFrame(common, columns=["Word", "Count"])
            fig = px.bar(words_df, x="Count", y="Word", orientation="h",
                         title=f"Top {n_words} Most Common Words")
            fig.update_layout(height=600, yaxis={"categoryorder": "total ascending"})
            st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.subheader("Top Words")
        if common:
            for word, count in common[:15]:
                st.text(f"{word}: {count}")


# ---------------------------------------------------------------------------
# Tab: Music
# ---------------------------------------------------------------------------

@st.cache_data(show_spinner=False, ttl=600)
def _cached_music_search(df: pd.DataFrame) -> dict:
    """Cache iTunes lookups so they don't re-run on every interaction."""
    from music_extraction import extract_and_search_music
    entries = [
        {"date": row["date"].strftime("%Y-%m-%d"), "text": row["text"]}
        for _, row in df.iterrows()
    ]
    return extract_and_search_music(entries)


def tab_music(df: pd.DataFrame):
    section_header("Music Mentioned", """
        Songs and artists detected in your journal entries,
        linked to Apple Music / iTunes for metadata and artwork.
    """)

    try:
        from music_extraction import extract_and_search_music, format_duration

        with st.spinner("Searching for music mentions..."):
            music_data = _cached_music_search(df)

        if not music_data:
            st.info("No music mentions detected. Try writing about songs you're listening to!")
            st.markdown("""
            **Tips for detection:**
            - Use quotes: *listened to "Everlong" by Foo Fighters*
            - Mention artists: *listening to Radiohead*
            - Use colons: *Song: "Karma Police"*
            """)
            return

        sorted_music = sorted(music_data.values(), key=lambda x: x["count"], reverse=True)
        cols_per_row = 3

        for i in range(0, len(sorted_music), cols_per_row):
            cols = st.columns(cols_per_row)
            for j, col in enumerate(cols):
                if i + j >= len(sorted_music):
                    break
                item = sorted_music[i + j]
                meta = item["metadata"]

                with col:
                    if meta["artwork_url"]:
                        st.image(meta["artwork_url"], use_container_width=True)
                    st.markdown(f"**{meta['song_name']}**")
                    st.markdown(f"*{meta['artist_name']}*")
                    if meta["album_name"]:
                        st.caption(f"Album: {meta['album_name']}")

                    c1, c2 = st.columns(2)
                    with c1:
                        st.metric("Mentions", item["count"])
                    with c2:
                        last = max(item["dates"])
                        st.metric("Last", last.split("T")[0] if "T" in last else last)

                    if meta["duration_ms"]:
                        st.caption(f"Duration: {format_duration(meta['duration_ms'])}")
                    if meta["genre"]:
                        st.caption(f"Genre: {meta['genre']}")

                    lc1, lc2 = st.columns(2)
                    with lc1:
                        if meta["preview_url"]:
                            st.markdown(f"[Preview]({meta['preview_url']})")
                    with lc2:
                        if meta["itunes_url"]:
                            st.markdown(f"[iTunes]({meta['itunes_url']})")
                    st.divider()

        st.caption(f"Found {len(sorted_music)} songs/artists across {len(df)} entries")

        # --- Music export ---
        music_rows = []
        for item in sorted_music:
            meta = item["metadata"]
            music_rows.append({
                "Song": meta["song_name"],
                "Artist": meta["artist_name"],
                "Album": meta.get("album_name", ""),
                "Genre": meta.get("genre", ""),
                "Mentions": item["count"],
                "Dates Mentioned": "; ".join(sorted(item["dates"])),
                "iTunes URL": meta.get("itunes_url", ""),
            })
        music_df = pd.DataFrame(music_rows)
        st.download_button(
            "Download music data (CSV)",
            data=music_df.to_csv(index=False),
            file_name="journal_music.csv",
            mime="text/csv",
        )

    except ImportError:
        st.error("Music extraction module not found. Ensure music_extraction.py is in the dashboard folder.")
    except Exception as e:
        st.error(f"Error extracting music: {e}")


# ---------------------------------------------------------------------------
# Tab: Chat
# ---------------------------------------------------------------------------

def tab_chat(rag_db_path: str):
    st.header("Chat with Your Journals")
    st.markdown(
        "Ask questions about your journal entries. "
        "The system searches semantically and can optionally use a local LLM."
    )

    # --- LLM toggle ---
    use_llm = st.checkbox(
        "Use LLM for answers",
        value=False,
        help="Requires Ollama installed and running locally",
    )
    llm_model = "llama3.3"
    if use_llm:
        llm_model = st.selectbox("LLM Model", ["llama3.3", "mistral", "llama2"])

    # --- Check database exists ---
    if not Path(rag_db_path).exists():
        st.warning(
            "RAG database not found. Ingest entries first using the sidebar button "
            "or option 4 in Journal_System.bat."
        )
        return

    # --- Chat history ---
    if "messages" not in st.session_state:
        st.session_state.messages = []

    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
            if message.get("sources"):
                with st.expander("View Sources"):
                    for i, src in enumerate(message["sources"], 1):
                        st.markdown(f"**{i}. Entry from {src['date']}**")
                        st.text(src["text"][:300] + ("..." if len(src["text"]) > 300 else ""))
                        st.divider()

    # --- Chat input ---
    if prompt := st.chat_input("Ask a question about your journals..."):
        session_log(f"Chat question: {prompt}")
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            with st.spinner("Searching your journals..."):
                try:
                    from journal_rag import JournalRAG, OllamaLLM

                    rag = JournalRAG(db_path=rag_db_path)
                    results = rag.search(prompt, n_results=3)

                    if not results:
                        response = "I couldn't find any relevant journal entries. Try rephrasing."
                        sources = []
                    elif use_llm:
                        try:
                            with st.spinner("Generating answer with AI..."):
                                llm = OllamaLLM(model=llm_model)
                                context = [r["text"] for r in results]
                                response = llm.generate(prompt, context)
                            sources = results
                        except Exception as e:
                            response = f"LLM error: {e}\n\nShowing relevant entries instead:"
                            sources = results
                    else:
                        response = "Here are the most relevant journal entries:"
                        sources = results

                    st.markdown(response)
                    if sources:
                        with st.expander("View Sources", expanded=(not use_llm)):
                            for i, src in enumerate(sources, 1):
                                st.markdown(f"**{i}. Entry from {src['date']}**")
                                st.text(src["text"][:300] + ("..." if len(src["text"]) > 300 else ""))
                                st.divider()

                    st.session_state.messages.append({
                        "role": "assistant", "content": response, "sources": sources,
                    })
                    session_log(f"Chat response: {response[:200]}")

                except FileNotFoundError:
                    msg = "RAG database not found. Please ingest your journal entries first."
                    st.error(msg)
                    st.session_state.messages.append({"role": "assistant", "content": msg, "sources": []})
                except Exception as e:
                    msg = f"Error: {e}"
                    st.error(msg)
                    st.session_state.messages.append({"role": "assistant", "content": msg, "sources": []})

    # --- Example questions ---
    with st.expander("Example Questions"):
        st.markdown("""
        - What was I worried about last week?
        - When did I last mention [person's name]?
        - What made me happy this month?
        - How have I been sleeping lately?
        - What goals did I set recently?
        """)

    # --- Clear history ---
    if st.button("Clear Chat History"):
        st.session_state.messages = []
        st.rerun()


# ---------------------------------------------------------------------------
# Tab: Entries & Stats
# ---------------------------------------------------------------------------

def tab_entries(df: pd.DataFrame):
    section_header("Detailed Statistics", """
        Breakdown across sentiment, writing length, and journaling streaks.
        Expand any highlighted entry to preview its text.
    """)

    col1, col2, col3 = st.columns(3)

    with col1:
        st.subheader("Sentiment")
        st.metric("Average", f"{df['sentiment'].mean():.2f}")

        max_idx = df["sentiment"].idxmax()
        max_row = df.loc[max_idx]
        st.metric("Most Positive", max_row["date"].strftime("%Y-%m-%d"),
                  delta=f"{max_row['sentiment']:.2f}")
        with st.expander("Preview"):
            st.caption(f"{max_row['date'].strftime('%Y-%m-%d')} - {max_row['word_count']} words - score {max_row['sentiment']:.2f}")
            st.text(max_row["text"][:300] + ("..." if len(max_row["text"]) > 300 else ""))

        min_idx = df["sentiment"].idxmin()
        min_row = df.loc[min_idx]
        st.metric("Most Negative", min_row["date"].strftime("%Y-%m-%d"),
                  delta=f"{min_row['sentiment']:.2f}")
        with st.expander("Preview"):
            st.caption(f"{min_row['date'].strftime('%Y-%m-%d')} - {min_row['word_count']} words - score {min_row['sentiment']:.2f}")
            st.text(min_row["text"][:300] + ("..." if len(min_row["text"]) > 300 else ""))

    with col2:
        st.subheader("Writing")
        st.metric("Median Words", f"{int(df['word_count'].median()):,}")

        long_idx = df["word_count"].idxmax()
        long_row = df.loc[long_idx]
        st.metric("Longest Entry", f"{long_row['word_count']:,} words",
                  delta=long_row["date"].strftime("%Y-%m-%d"))
        with st.expander("Preview"):
            st.caption(f"{long_row['date'].strftime('%Y-%m-%d')} - {long_row['word_count']} words")
            st.text(long_row["text"][:300] + ("..." if len(long_row["text"]) > 300 else ""))

        short_idx = df["word_count"].idxmin()
        short_row = df.loc[short_idx]
        st.metric("Shortest Entry", f"{short_row['word_count']:,} words",
                  delta=short_row["date"].strftime("%Y-%m-%d"))
        with st.expander("Preview"):
            st.caption(f"{short_row['date'].strftime('%Y-%m-%d')} - {short_row['word_count']} words")
            st.text(short_row["text"][:300] + ("..." if len(short_row["text"]) > 300 else ""))

    with col3:
        st.subheader("Consistency")
        dates_set = set(df["date"].dt.date)
        sorted_dates = sorted(dates_set)

        longest_streak = temp = 1
        for i in range(1, len(sorted_dates)):
            if (sorted_dates[i] - sorted_dates[i - 1]).days == 1:
                temp += 1
            else:
                longest_streak = max(longest_streak, temp)
                temp = 1
        longest_streak = max(longest_streak, temp)

        current_streak = 0
        if sorted_dates:
            today = datetime.now().date()
            last = sorted_dates[-1]
            if last == today or (today - last).days == 1:
                current_streak = 1
                for i in range(len(sorted_dates) - 2, -1, -1):
                    if (sorted_dates[i + 1] - sorted_dates[i]).days == 1:
                        current_streak += 1
                    else:
                        break

        st.metric("Current Streak", f"{current_streak} days")
        st.metric("Longest Streak", f"{longest_streak} days")
        st.metric("Total Days Journaled", len(dates_set))

    # --- Recent entries ---
    section_header("Recent Entries", """
        Your most recent journal entries, newest first.
        Click to expand and read a preview.
    """)

    n_recent = st.slider("Entries to show", 3, 10, 5)
    recent = df.tail(n_recent).sort_values("date", ascending=False)
    for _, row in recent.iterrows():
        label = f"{row['date'].strftime('%Y-%m-%d')} - {row['word_count']} words - Sentiment: {row['sentiment']:.2f}"
        with st.expander(label):
            preview = row["text"][:300]
            if len(row["text"]) > 300:
                preview += "..."
            st.text(preview)

    # --- Data export ---
    st.divider()
    st.subheader("Export Data")
    ex1, ex2 = st.columns(2)
    with ex1:
        stats_df = df[["date", "word_count", "sentiment"]].copy()
        stats_df["date"] = stats_df["date"].dt.strftime("%Y-%m-%d")
        st.download_button(
            "Download statistics (CSV)",
            data=stats_df.to_csv(index=False),
            file_name="journal_statistics.csv",
            mime="text/csv",
        )
    with ex2:
        full_df = df[["date", "word_count", "char_count", "sentiment", "text"]].copy()
        full_df["date"] = full_df["date"].dt.strftime("%Y-%m-%d")
        st.download_button(
            "Download all entries (CSV)",
            data=full_df.to_csv(index=False),
            file_name="journal_entries.csv",
            mime="text/csv",
        )


# ---------------------------------------------------------------------------
# Tab: Appearance
# ---------------------------------------------------------------------------

def tab_appearance():
    section_header("Appearance & Styling", """
        Customise the look of this dashboard. Changes apply immediately
        and are saved automatically so they persist between launches.
    """)

    # Load saved theme as defaults
    t = load_theme()

    body_fonts = ["Georgia", "Palatino Linotype", "Garamond", "Times New Roman",
                  "Merriweather", "Source Serif 4", "sans-serif", "monospace"]
    heading_fonts = ["Georgia", "Palatino Linotype", "Garamond", "Impact",
                     "Trebuchet MS", "Verdana", "serif", "sans-serif"]

    # --- Typography ---
    st.subheader("Typography")
    fc1, fc2 = st.columns(2)
    with fc1:
        body_font = st.selectbox("Body font", body_fonts,
                                 index=body_fonts.index(t["body_font"]) if t["body_font"] in body_fonts else 0)
        font_size = st.slider("Base font size (px)", 12, 22, t["font_size"])
    with fc2:
        heading_font = st.selectbox("Heading font", heading_fonts,
                                    index=heading_fonts.index(t["heading_font"]) if t["heading_font"] in heading_fonts else 2)
        line_height = st.slider("Line height", 1.2, 2.2, t["line_height"], step=0.1)

    # --- Colours ---
    st.subheader("Colours")
    cc1, cc2, cc3 = st.columns(3)
    with cc1:
        text_color = st.color_picker("Body text", t["text_color"])
        heading_color = st.color_picker("Headings", t["heading_color"])
    with cc2:
        link_color = st.color_picker("Links / accent", t["link_color"])
        metric_color = st.color_picker("Metric values", t["metric_color"])
    with cc3:
        bg_color = st.color_picker("Page background", t["bg_color"])
        sidebar_bg = st.color_picker("Sidebar background", t["sidebar_bg"])

    # --- Spacing ---
    st.subheader("Spacing & Layout")
    sc1, sc2 = st.columns(2)
    with sc1:
        content_padding = st.slider("Content padding (rem)", 0.5, 4.0, t["content_padding"], step=0.25)
        block_gap = st.slider("Section gap (rem)", 0.5, 4.0, t["block_gap"], step=0.25)
    with sc2:
        metric_font_size = st.slider("Metric label size (px)", 10, 18, t["metric_font_size"])
        border_radius = st.slider("Border radius (px)", 0, 20, t["border_radius"])

    # --- Presets ---
    st.subheader("Quick Presets")
    presets = {
        "Dark Ink": {
            "body_font": "Georgia", "heading_font": "Garamond",
            "font_size": 16, "line_height": 1.7,
            "text_color": "#e8e8e0", "heading_color": "#f5f0e8",
            "link_color": "#c9a96e", "metric_color": "#c9a96e",
            "bg_color": "#1a1814", "sidebar_bg": "#12100e",
            "content_padding": 1.5, "block_gap": 2.0,
            "metric_font_size": 13, "border_radius": 6,
        },
        "Parchment": {
            "body_font": "Palatino Linotype", "heading_font": "Garamond",
            "font_size": 17, "line_height": 1.8,
            "text_color": "#3b2f1e", "heading_color": "#1e1208",
            "link_color": "#7a4f2e", "metric_color": "#4a3220",
            "bg_color": "#fdf6e3", "sidebar_bg": "#f5e8c8",
            "content_padding": 2.0, "block_gap": 2.0,
            "metric_font_size": 14, "border_radius": 4,
        },
        "Minimal": {
            "body_font": "sans-serif", "heading_font": "sans-serif",
            "font_size": 15, "line_height": 1.5,
            "text_color": "#111111", "heading_color": "#000000",
            "link_color": "#0066cc", "metric_color": "#0066cc",
            "bg_color": "#ffffff", "sidebar_bg": "#f4f4f4",
            "content_padding": 1.0, "block_gap": 1.5,
            "metric_font_size": 12, "border_radius": 2,
        },
        "Sage": {
            "body_font": "Georgia", "heading_font": "Georgia",
            "font_size": 16, "line_height": 1.7,
            "text_color": "#2d3a2e", "heading_color": "#1a2e1b",
            "link_color": "#4a7c59", "metric_color": "#3a6648",
            "bg_color": "#f4f8f4", "sidebar_bg": "#e8f0e8",
            "content_padding": 1.5, "block_gap": 1.75,
            "metric_font_size": 14, "border_radius": 10,
        },
    }

    preset_cols = st.columns(len(presets))
    for i, (label, p) in enumerate(presets.items()):
        with preset_cols[i]:
            if st.button(label, use_container_width=True):
                save_theme(p)
                session_log(f"Theme preset applied: {label}")
                st.rerun()

    # Build current theme dict from widget values
    current_theme = {
        "body_font": body_font, "heading_font": heading_font,
        "font_size": font_size, "line_height": line_height,
        "text_color": text_color, "heading_color": heading_color,
        "link_color": link_color, "metric_color": metric_color,
        "bg_color": bg_color, "sidebar_bg": sidebar_bg,
        "content_padding": content_padding, "block_gap": block_gap,
        "metric_font_size": metric_font_size, "border_radius": border_radius,
    }

    # Auto-save whenever theme differs from what's on disk
    if current_theme != t:
        save_theme(current_theme)

    # --- Inject CSS ---
    custom_css = f"""
<style>
html, body, [class*="css"] {{
    font-family: '{body_font}', serif !important;
    font-size: {font_size}px !important;
    line-height: {line_height} !important;
    color: {text_color} !important;
    background-color: {bg_color} !important;
}}
h1, h2, h3, h4, h5, h6,
.stMarkdown h1, .stMarkdown h2, .stMarkdown h3 {{
    font-family: '{heading_font}', serif !important;
    color: {heading_color} !important;
}}
a, a:visited {{ color: {link_color} !important; }}
[data-testid="stMetricValue"] {{
    color: {metric_color} !important;
    font-family: '{heading_font}', serif !important;
}}
[data-testid="stMetricLabel"] {{
    font-size: {metric_font_size}px !important;
    color: {text_color} !important; opacity: 0.75;
}}
[data-testid="stSidebar"] {{ background-color: {sidebar_bg} !important; }}
[data-testid="stSidebar"] * {{ color: {text_color} !important; }}
.block-container {{
    padding-left: {content_padding}rem !important;
    padding-right: {content_padding}rem !important;
}}
.element-container {{ margin-bottom: {block_gap / 2}rem !important; }}
[data-testid="stExpander"] {{ border-radius: {border_radius}px !important; }}
[data-baseweb="tab-list"] {{ font-family: '{body_font}', serif !important; }}
</style>
"""
    st.markdown(custom_css, unsafe_allow_html=True)

    # --- Preview ---
    st.subheader("Live Preview")
    st.markdown(f"""
<div style="
    font-family: '{body_font}', serif; font-size: {font_size}px;
    line-height: {line_height}; color: {text_color};
    background-color: {bg_color}; padding: 1.5rem;
    border-radius: {border_radius}px; border: 1px solid #ddd;">
  <h2 style="font-family: '{heading_font}', serif; color: {heading_color}; margin-top: 0;">
    Journal Entry &mdash; March 12
  </h2>
  <p>Today was one of those slow, contemplative days where the light came in sideways
  through the blinds and everything felt like it was happening just slightly underwater.</p>
  <p><a href="#" style="color: {link_color};">View full entry</a></p>
  <hr style="border-color: {link_color}; opacity: 0.3;" />
  <p style="font-size: {metric_font_size}px; opacity: 0.7;">
    Words: 412 &middot; Sentiment: +0.42 &middot; Streak: 14 days</p>
</div>
""", unsafe_allow_html=True)

    # --- Export / Reset ---
    st.subheader("Export CSS")
    st.caption("Copy this snippet to reuse or share your theme.")
    st.code(custom_css, language="css")

    if st.button("Reset to defaults"):
        save_theme(_THEME_DEFAULTS)
        session_log("Theme reset to defaults")
        st.rerun()


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    st.title("Reflecting Pool")

    # Apply saved theme CSS on every page (not just the Appearance tab)
    theme = load_theme()
    _inject_theme_css(theme)

    # Load data
    df = load_journal_data(DEFAULT_OCR_DIR)
    ocr_output_dir, rag_db_path, filtered_df = render_sidebar(df)

    # Reload if user changed the path
    if ocr_output_dir != DEFAULT_OCR_DIR:
        df = load_journal_data(ocr_output_dir)
        _, _, filtered_df = render_sidebar(df)

    if df.empty:
        st.warning("No journal entries found. Check the OCR output directory path in the sidebar.")
        st.info("""
        **To get started:**
        1. Process journal photos with the OCR pipeline
        2. Update the OCR Output Directory path in the sidebar
        3. Refresh this page
        """)
        # Still show the chat tab even without entries
        tab_chat(rag_db_path)
        return

    # Compute sentiment (cached to avoid re-running on every interaction)
    filtered_df = _add_sentiment(filtered_df)

    # --- Overview metrics ---
    with st.expander("About these metrics", expanded=False):
        st.markdown(
            "**Total Entries** is the number of journal entries. "
            "**Total Words** sums all words. **Avg Words/Entry** is the mean length. "
            "**Days Covered** is calendar days from first to last entry."
        )

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Total Entries", len(filtered_df))
    c2.metric("Total Words", f"{filtered_df['word_count'].sum():,}")
    c3.metric("Avg Words/Entry", f"{int(filtered_df['word_count'].mean()):,}")
    c4.metric("Days Covered", (filtered_df["date"].max() - filtered_df["date"].min()).days + 1)
    st.divider()

    # --- Tabs ---
    t_analytics, t_words, t_music, t_chat, t_entries, t_appearance = st.tabs([
        "Analytics", "Words & Themes", "Music", "Chat", "Entries & Stats", "Appearance",
    ])

    with t_analytics:
        tab_analytics(filtered_df)
    with t_words:
        tab_words(filtered_df)
    with t_music:
        tab_music(filtered_df)
    with t_chat:
        tab_chat(rag_db_path)
    with t_entries:
        tab_entries(filtered_df)
    with t_appearance:
        tab_appearance()


if __name__ == "__main__":
    main()

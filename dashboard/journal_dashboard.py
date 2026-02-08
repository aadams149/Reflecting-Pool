#!/usr/bin/env python3
"""
Journal Analytics Dashboard
Interactive visualizations and insights from journal entries
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from pathlib import Path
import json
from datetime import datetime, timedelta
from collections import Counter
import re
from typing import Dict, List, Tuple


# Page config
st.set_page_config(
    page_title="Journal Analytics",
    page_icon="📔",
    layout="wide",
    initial_sidebar_state="expanded"
)


@st.cache_data
def load_journal_data(ocr_output_dir: str) -> pd.DataFrame:
    """
    Load journal entries from OCR output
    
    Args:
        ocr_output_dir: Path to OCR output directory
        
    Returns:
        DataFrame with journal entries
    """
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
        
        # Load text
        with open(text_file, 'r', encoding='utf-8') as f:
            text = f.read().strip()
        
        # Load metadata
        with open(metadata_file, 'r', encoding='utf-8') as f:
            metadata = json.load(f)
        
        if not text:
            continue
        
        # Recalculate word count from actual text (in case OCR metadata is wrong)
        actual_word_count = len(text.split())
        
        entries.append({
            'date': metadata['entry_date'],
            'text': text,
            'word_count': actual_word_count,  # Use recalculated count
            'char_count': len(text)  # Recalculate char count too
        })
    
    if not entries:
        return pd.DataFrame()
    
    df = pd.DataFrame(entries)
    df['date'] = pd.to_datetime(df['date'], format='mixed')
    df = df.sort_values('date')
    
    return df


def get_sentiment(text: str) -> float:
    """
    VADER sentiment scoring.
    Returns a compound score between -1 (most negative) and 1 (most positive).
    
    To swap in a different method in the future, replace the body of this
    function — the rest of the dashboard just calls get_sentiment(text).
    """
    from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
    analyzer = SentimentIntensityAnalyzer()
    return analyzer.polarity_scores(text)['compound']


def section_header(title: str, help_text: str):
    """Render a section header with a collapsible ℹ️ help tooltip beneath it."""
    st.header(title)
    with st.expander("ℹ️ What does this show?"):
        st.markdown(help_text)


def extract_common_words(texts: List[str], n_words: int = 30) -> List[Tuple[str, int]]:
    """Extract most common meaningful words"""
    # Common stop words to exclude
    stop_words = {
        'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for',
        'of', 'with', 'by', 'from', 'as', 'is', 'was', 'were', 'been', 'be',
        'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could',
        'should', 'may', 'might', 'must', 'can', 'i', 'me', 'my', 'mine',
        'you', 'your', 'yours', 'he', 'him', 'his', 'she', 'her', 'hers',
        'it', 'its', 'we', 'us', 'our', 'ours', 'they', 'them', 'their',
        'theirs', 'this', 'that', 'these', 'those', 'am', 'are', 'was',
        'were', 'been', 'being', 'have', 'has', 'had', 'having', 'do',
        'does', 'did', 'doing', 'just', 'so', 'than', 'too', 'very'
    }
    
    all_words = []
    for text in texts:
        words = re.findall(r'\b\w+\b', text.lower())
        # Filter out stop words and short words
        words = [w for w in words if w not in stop_words and len(w) > 3]
        all_words.extend(words)
    
    return Counter(all_words).most_common(n_words)


def main():
    st.title("📔 Journal Analytics Dashboard")
    
    # Sidebar configuration
    st.sidebar.header("Configuration")
    
    ocr_output_dir = st.sidebar.text_input(
        "OCR Output Directory",
        value="../ocr/ocr_output",
        help="Path to your OCR output directory"
    )
    
    # RAG Search Section
    st.sidebar.header("🔍 RAG Search")
    
    rag_db_path = st.sidebar.text_input(
        "RAG Database Path",
        value="../rag/vector_db",
        help="Path to your RAG vector database"
    )
    
    search_query = st.sidebar.text_input(
        "Search Query",
        placeholder="e.g., feeling anxious about work",
        help="Semantic search across all journal entries"
    )
    
    if st.sidebar.button("🔎 Search", type="primary"):
        if search_query:
            try:
                import sys
                sys.path.insert(0, str(Path(__file__).parent.parent / "rag"))
                from journal_rag import JournalRAG
                
                with st.spinner("Searching..."):
                    rag = JournalRAG(db_path=rag_db_path)
                    results = rag.search(search_query, n_results=5)
                
                if results:
                    st.sidebar.success(f"Found {len(results)} results")
                    
                    # Display results in sidebar
                    for i, result in enumerate(results, 1):
                        with st.sidebar.expander(f"{i}. {result['date']}"):
                            st.text(result['text'][:200] + "...")
                else:
                    st.sidebar.warning("No results found")
            except FileNotFoundError:
                st.sidebar.error("RAG database not found. Run ingestion first.")
            except Exception as e:
                st.sidebar.error(f"Search error: {e}")
        else:
            st.sidebar.warning("Please enter a search query")
    
    # Ingest button
    if st.sidebar.button("📥 Ingest to RAG"):
        try:
            import sys
            sys.path.insert(0, str(Path(__file__).parent.parent / "rag"))
            from journal_rag import JournalRAG
            
            with st.spinner("Ingesting journal entries into RAG database..."):
                rag = JournalRAG(db_path=rag_db_path)
                count = rag.ingest_from_ocr(ocr_output_dir)
            
            st.sidebar.success(f"✓ Ingested {count} entries!")
        except Exception as e:
            st.sidebar.error(f"Ingestion error: {e}")
    
    # Load data
    df = load_journal_data(ocr_output_dir)
    
    if df.empty:
        st.warning("No journal entries found. Please check the OCR output directory path.")
        st.info("""
        **To get started:**
        1. Process some journal photos with the OCR pipeline
        2. Update the OCR Output Directory path in the sidebar
        3. Refresh this page
        """)
        return
    
    # Calculate sentiment for all entries
    if 'sentiment' not in df.columns:
        with st.spinner("Analyzing sentiment..."):
            df['sentiment'] = df['text'].apply(get_sentiment)
    
    # Overview metrics
    section_header("📊 Overview", """
        These are the top-level stats for your journal. **Total Entries** is the number of
        journal entries you have. **Total Words** is the sum of all words across every entry.
        **Avg Words/Entry** is the average length of an entry. **Days Covered** is the total
        number of calendar days from your first entry to your most recent one (inclusive).
        All of these numbers update automatically when you adjust the date filter in the sidebar.
    """)
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Entries", len(df))
    
    with col2:
        st.metric("Total Words", f"{df['word_count'].sum():,}")
    
    with col3:
        avg_words = int(df['word_count'].mean())
        st.metric("Avg Words/Entry", f"{avg_words:,}")
    
    with col4:
        date_range = (df['date'].max() - df['date'].min()).days + 1
        st.metric("Days Covered", date_range)
    
    # Date range selector
    st.sidebar.header("Filters")
    
    min_date = df['date'].min().date()
    max_date = df['date'].max().date()
    
    date_range = st.sidebar.date_input(
        "Date Range",
        value=(min_date, max_date),
        min_value=min_date,
        max_value=max_date
    )
    
    # Filter data by date range
    if len(date_range) == 2:
        mask = (df['date'].dt.date >= date_range[0]) & (df['date'].dt.date <= date_range[1])
        filtered_df = df[mask]
    else:
        filtered_df = df
    
    section_header("😊 Sentiment Over Time", """
        This chart tracks the emotional tone of each journal entry over time using VADER
        sentiment analysis. The score runs from **-1** (most negative) to **+1** (most positive),
        with **0** being neutral (shown as the dashed grey line). Each dot is one entry — hover
        over it to see the exact date and score. Peaks and valleys can help you spot patterns in
        your mood or what kinds of days tend to produce more positive or negative writing.
    """)
    
    fig_sentiment = go.Figure()
    
    fig_sentiment.add_trace(go.Scatter(
        x=filtered_df['date'],
        y=filtered_df['sentiment'],
        mode='lines+markers',
        name='Sentiment',
        line=dict(color='rgb(99, 110, 250)', width=2),
        marker=dict(size=6)
    ))
    
    # Add zero line
    fig_sentiment.add_hline(y=0, line_dash="dash", line_color="gray", opacity=0.5)
    
    fig_sentiment.update_layout(
        xaxis_title="Date",
        yaxis_title="Sentiment Score",
        yaxis_range=[-1.1, 1.1],
        height=400,
        hovermode='x unified'
    )
    
    st.plotly_chart(fig_sentiment, use_container_width=True)
    
    section_header("✍️ Writing Consistency", """
        Two charts side by side. The **bar chart on the left** shows how many entries you wrote
        each month — useful for seeing if your journaling habit has been picking up or slowing
        down. The **scatter plot on the right** plots the word count of each individual entry by
        date, so you can see whether your entries tend to be long or short and whether that changes
        over time.
    """)
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Entries per month
        monthly_counts = filtered_df.groupby(filtered_df['date'].dt.to_period('M')).size()
        monthly_counts.index = monthly_counts.index.astype(str)
        
        fig_monthly = px.bar(
            x=monthly_counts.index,
            y=monthly_counts.values,
            labels={'x': 'Month', 'y': 'Number of Entries'},
            title='Entries per Month'
        )
        fig_monthly.update_traces(marker_color='rgb(99, 110, 250)')
        st.plotly_chart(fig_monthly, use_container_width=True)
    
    with col2:
        # Words per entry over time
        fig_words = px.scatter(
            filtered_df,
            x='date',
            y='word_count',
            title='Words per Entry',
            labels={'date': 'Date', 'word_count': 'Word Count'}
        )
        st.plotly_chart(fig_words, use_container_width=True)
    
    section_header("📅 Writing Frequency Heatmap", """
        A calendar-style grid, similar to the GitHub contribution graph. Each **row** is a day of
        the week (Monday–Sunday) and each **column** is a week. The colour of each cell represents
        how many **words** you wrote on that day — darker blue means more writing, white or light
        means little or none. This makes it easy to spot patterns like whether you tend to journal
        more on certain days of the week, or whether there are gaps in your routine.
    """)
    
    # Create a complete date range
    date_range_full = pd.date_range(start=filtered_df['date'].min(), 
                                     end=filtered_df['date'].max(), 
                                     freq='D')
    
    # Sum words per day
    daily_counts = filtered_df.groupby(filtered_df['date'].dt.date)['word_count'].sum()
    
    # Create heatmap data
    heatmap_data = []
    for date in date_range_full:
        date_val = date.date()
        count = daily_counts.get(date_val, 0)
        heatmap_data.append({
            'date': date,
            'count': count,
            'day_of_week': date.day_name(),
            'week': date.isocalendar()[1],
            'year': date.year
        })
    
    heatmap_df = pd.DataFrame(heatmap_data)
    
    # Create pivot for heatmap
    pivot_data = heatmap_df.pivot_table(
        values='count',
        index='day_of_week',
        columns=heatmap_df['date'].dt.to_period('W'),
        fill_value=0
    )
    
    # Reorder days
    day_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    pivot_data = pivot_data.reindex(day_order)
    pivot_data.columns = pivot_data.columns.astype(str)
    
    fig_heatmap = px.imshow(
        pivot_data,
        labels=dict(x="Week", y="Day of Week", color="Words"),
        color_continuous_scale='Blues',
        aspect='auto'
    )
    
    fig_heatmap.update_layout(height=300)
    st.plotly_chart(fig_heatmap, use_container_width=True)
    
    section_header("💬 Most Common Words", """
        A ranked list of the words you use most often across your entries. Common filler words
        like "the", "and", "I" are automatically filtered out, so what you see here are the words
        that are actually meaningful to your writing. Use the slider to adjust how many words are
        shown. The list on the right is a quick-glance version of the top 15.
    """)
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        n_words = st.slider("Number of words to show", 10, 50, 30)
        common_words = extract_common_words(filtered_df['text'].tolist(), n_words=n_words)
        
        if common_words:
            words_df = pd.DataFrame(common_words, columns=['Word', 'Count'])
            
            fig_words = px.bar(
                words_df,
                x='Count',
                y='Word',
                orientation='h',
                title=f'Top {n_words} Most Common Words'
            )
            fig_words.update_layout(height=600, yaxis={'categoryorder': 'total ascending'})
            st.plotly_chart(fig_words, use_container_width=True)
    
    with col2:
        st.subheader("Word Cloud Data")
        if common_words:
            for word, count in common_words[:15]:
                st.text(f"{word}: {count}")
    
    section_header("📈 Detailed Statistics", """
        A deeper breakdown of your journal stats across three categories. **Sentiment Stats**
        shows your average emotional tone and highlights the dates of your most positive and most
        negative entries. **Writing Stats** shows the range of your entry lengths — longest,
        shortest, and median word counts. **Consistency Stats** tracks your journaling streaks:
        how many consecutive days you've journaled recently, your longest streak ever, and the
        total number of days you've written on.
    """)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.subheader("Sentiment Stats")
        st.metric("Average Sentiment", f"{filtered_df['sentiment'].mean():.2f}")
        st.metric("Most Positive Entry", 
                 filtered_df.loc[filtered_df['sentiment'].idxmax(), 'date'].strftime('%Y-%m-%d'))
        st.metric("Most Negative Entry", 
                 filtered_df.loc[filtered_df['sentiment'].idxmin(), 'date'].strftime('%Y-%m-%d'))
    
    with col2:
        st.subheader("Writing Stats")
        st.metric("Longest Entry", f"{filtered_df['word_count'].max():,} words")
        st.metric("Shortest Entry", f"{filtered_df['word_count'].min():,} words")
        st.metric("Median Words", f"{int(filtered_df['word_count'].median()):,}")
    
    with col3:
        st.subheader("Consistency Stats")
        # Calculate streaks
        dates_set = set(filtered_df['date'].dt.date)
        current_streak = 0
        longest_streak = 0
        temp_streak = 1
        
        sorted_dates = sorted(dates_set)
        for i in range(1, len(sorted_dates)):
            if (sorted_dates[i] - sorted_dates[i-1]).days == 1:
                temp_streak += 1
            else:
                longest_streak = max(longest_streak, temp_streak)
                temp_streak = 1
        
        longest_streak = max(longest_streak, temp_streak)
        
        # Check current streak
        if sorted_dates:
            last_date = sorted_dates[-1]
            today = datetime.now().date()
            
            if last_date == today or (today - last_date).days == 1:
                current_streak = 1
                for i in range(len(sorted_dates) - 2, -1, -1):
                    if (sorted_dates[i+1] - sorted_dates[i]).days == 1:
                        current_streak += 1
                    else:
                        break
        
        st.metric("Current Streak", f"{current_streak} days")
        st.metric("Longest Streak", f"{longest_streak} days")
        st.metric("Total Days Journaled", len(dates_set))
    
    section_header("📝 Recent Entries", """
        Your most recent journal entries, shown newest first. Each one is collapsible — click to
        expand and read a preview (first 300 characters). The header of each entry shows the date,
        word count, and sentiment score at a glance. Use the slider to control how many entries are
        displayed.
    """)
    
    n_recent = st.slider("Number of recent entries to show", 3, 10, 5)
    
    recent_entries = filtered_df.tail(n_recent).sort_values('date', ascending=False)
    
    for idx, row in recent_entries.iterrows():
        with st.expander(f"{row['date'].strftime('%Y-%m-%d')} - {row['word_count']} words - Sentiment: {row['sentiment']:.2f}"):
            # Show first 300 characters
            preview = row['text'][:300]
            if len(row['text']) > 300:
                preview += "..."
            st.text(preview)
    
    # Music mentions
    section_header("🎵 Music Mentioned", """
        Songs and artists you've mentioned in your journal entries, automatically detected and
        linked to Apple Music/iTunes. Each card shows how many times you mentioned the song and
        when you last mentioned it. Click the links to listen on Apple Music or view on iTunes.
        The system looks for patterns like "listened to 'Song' by Artist" or just artist names
        you've mentioned.
    """)
    
    try:
        from music_extraction import extract_and_search_music, format_duration
        
        with st.spinner("Searching for music mentions..."):
            # Prepare entries for music extraction
            entries_for_music = [
                {'date': row['date'].strftime('%Y-%m-%d'), 'text': row['text']}
                for idx, row in filtered_df.iterrows()
            ]
            
            music_data = extract_and_search_music(entries_for_music)
        
        if music_data:
            # Sort by mention count
            sorted_music = sorted(music_data.values(), key=lambda x: x['count'], reverse=True)
            
            # Display in a grid
            cols_per_row = 3
            for i in range(0, len(sorted_music), cols_per_row):
                cols = st.columns(cols_per_row)
                
                for j, col in enumerate(cols):
                    if i + j < len(sorted_music):
                        item = sorted_music[i + j]
                        metadata = item['metadata']
                        
                        with col:
                            # Album artwork
                            if metadata['artwork_url']:
                                st.image(metadata['artwork_url'], use_container_width=True)
                            
                            # Song info
                            st.markdown(f"**{metadata['song_name']}**")
                            st.markdown(f"*{metadata['artist_name']}*")
                            
                            if metadata['album_name']:
                                st.caption(f"Album: {metadata['album_name']}")
                            
                            # Metadata
                            col1, col2 = st.columns(2)
                            with col1:
                                st.metric("Mentions", item['count'])
                            with col2:
                                last_mention = max(item['dates'])
                                st.metric("Last", last_mention.split('T')[0] if 'T' in last_mention else last_mention)
                            
                            # Duration and genre
                            if metadata['duration_ms']:
                                st.caption(f"⏱️ {format_duration(metadata['duration_ms'])}")
                            if metadata['genre']:
                                st.caption(f"🎸 {metadata['genre']}")
                            
                            # Links
                            link_col1, link_col2 = st.columns(2)
                            with link_col1:
                                if metadata['preview_url']:
                                    st.markdown(f"[▶️ Preview]({metadata['preview_url']})")
                            with link_col2:
                                if metadata['itunes_url']:
                                    st.markdown(f"[🎵 iTunes]({metadata['itunes_url']})")
                            
                            st.divider()
            
            st.caption(f"Found {len(sorted_music)} songs/artists across {len(filtered_df)} entries")
        else:
            st.info("No music mentions detected yet. Try writing about songs you're listening to!")
            st.markdown("""
            **Tips to help detection:**
            - Use quotes: *listened to "Everlong" by Foo Fighters*
            - Mention artists: *listening to Radiohead*
            - Use colons: *Song: "Karma Police"*
            """)
    
    except ImportError:
        st.error("Music extraction module not found. Make sure music_extraction.py is in the dashboard folder.")
    except Exception as e:
        st.error(f"Error extracting music: {e}")


if __name__ == "__main__":
    main()

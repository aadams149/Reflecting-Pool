# Journal Analytics Dashboard

Interactive web-based visualizations and AI chat interface for exploring patterns, trends, and insights from your journal entries.

## 🎯 What This Module Does

Two powerful interfaces for analyzing your journals:
1. **Analytics Dashboard** — Charts, graphs, sentiment tracking, music detection
2. **Chat Interface** — Conversational AI search over your entries

Both run locally in your web browser with beautiful, interactive visualizations.

---

## ✨ Features

### Analytics Dashboard

- **📊 Overview Metrics** — Total entries, words, averages, date range
- **😊 Sentiment Analysis** — VADER-powered emotional tone tracking over time
- **✍️ Writing Consistency** — Entries per month, word count trends
- **📅 Heatmap** — GitHub-style activity calendar showing writing frequency
- **💬 Word Frequency** — Most common words across all entries
- **📈 Detailed Stats** — Sentiment extremes, writing stats, streak tracking
- **🎵 Music Mentions** — Automatically detect songs with iTunes links
- **📝 Recent Entries** — Quick preview of latest journals
- **ℹ️ Help Tooltips** — Click to learn what each visualization shows

### Chat Interface

- **💬 Conversational Search** — Ask questions naturally
- **📚 Source Citations** — See which entries informed answers
- **🤖 Optional LLM** — AI-generated answers via Ollama
- **💾 Chat History** — Conversation persists during session
- **📊 Statistics** — Database info in sidebar
- **💡 Example Questions** — Suggestions to get started

---

## 🚀 Quick Start

### Using Batch Files (Easiest)

**Launch Analytics Dashboard:**
- Double-click `Launch_Dashboard.bat`
- Opens in web browser automatically
- Press Ctrl+C in terminal to stop

**Launch Chat Interface:**
- Double-click `Launch_Chat.bat`
- Opens in web browser automatically
- Press Ctrl+C in terminal to stop

### Command Line

```cmd
# Analytics dashboard
python -m streamlit run journal_dashboard.py

# Chat interface
python -m streamlit run journal_chat.py
```

Both open automatically at `http://localhost:8501`

---

## 🛠️ Installation

### Prerequisites
- **Python 3.9+**
- **OCR output** from OCR module
- **RAG database** from RAG module (for chat interface)

### Install Dependencies

```cmd
cd dashboard
pip install -r requirements.txt
```

This installs:
- `streamlit` — Web app framework
- `plotly` — Interactive visualizations
- `pandas` — Data manipulation
- `vaderSentiment` — Sentiment analysis
- `requests` — iTunes API for music detection

---

## 📖 Usage

### Analytics Dashboard

1. **Launch:** Double-click `Launch_Dashboard.bat`
2. **Configure path:** Enter OCR output directory in sidebar (default: `../ocr/ocr_output`)
3. **Explore:** Scroll through visualizations
4. **Filter:** Use date range selector in sidebar
5. **Learn:** Click "ℹ️ What does this show?" expanders

#### Sections

**📊 Overview**
- Total entries, words, average length
- Date range covered

**😊 Sentiment Over Time**
- Line chart tracking emotional tone
- Score from -1 (negative) to +1 (positive)
- Hover to see date and exact score

**✍️ Writing Consistency**
- Bar chart: Entries per month
- Scatter: Word count per entry over time

**📅 Writing Frequency Heatmap**
- Calendar-style grid (rows = days, columns = weeks)
- Color intensity = words written that day
- Spot patterns in writing habits

**💬 Most Common Words**
- Bar chart of top words (stop words filtered)
- Adjustable slider for number of words shown

**📈 Detailed Statistics**
- Sentiment stats (avg, extremes)
- Writing stats (longest, shortest, median)
- Consistency (current streak, longest streak, total days)

**🎵 Music Mentioned**
- Automatically detected songs from journal text
- Album artwork, artist info, mention counts
- Preview links and iTunes store links

**📝 Recent Entries**
- Collapsible previews of latest entries
- Shows date, word count, sentiment at a glance

### Chat Interface

1. **Launch:** Double-click `Launch_Chat.bat`
2. **Configure paths:** Enter RAG database path in sidebar (default: `../rag/vector_db`)
3. **Enable LLM (optional):** Check "Use LLM for answers" and select model
4. **Ask questions:** Type in chat input at bottom
5. **View sources:** Expand "📚 View Sources" to see cited entries
6. **Clear history:** Click "🗑️ Clear Chat History" to start over

#### Search Modes

**Search-Only Mode** (LLM off):
- Shows relevant journal excerpts
- Fast, no AI processing
- Good for finding specific entries

**LLM Mode** (LLM on, requires Ollama):
- AI reads entries and generates answers
- Cites sources used
- Good for summaries and insights

#### Example Questions

- "What was I worried about last week?"
- "When did I last mention [person's name]?"
- "What patterns do I see in my anxiety?"
- "What made me happy this month?"
- "How have I been sleeping lately?"

---

## ⚙️ Configuration

### Dashboard Paths

In sidebar:
- **OCR Output Directory** — Where to find processed journal text
- **RAG Database Path** — Where vector database is stored

Default paths work if you haven't moved files.

### Sentiment Analysis

Currently uses VADER (rule-based). To swap in a different method, edit `journal_dashboard.py`:

```python
def get_sentiment(text: str) -> float:
    """Change the body of this function to swap methods"""
    # Current: VADER
    from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
    analyzer = SentimentIntensityAnalyzer()
    return analyzer.polarity_scores(text)['compound']
    
    # Alternative: TextBlob (install first: pip install textblob)
    # from textblob import TextBlob
    # return TextBlob(text).sentiment.polarity
```

### Music Detection

The `music_extraction.py` module looks for patterns:
- "listened to 'Song' by Artist"
- "listening to Artist"
- Song: "Title"
- Artist - Song

To customize patterns, edit the regex in `music_extraction.py`.

### Date Filters

Date range selector in sidebar applies to all visualizations. Reset by:
1. Selecting full range again
2. Refreshing the page

---

## 🎨 Customization

### Adding New Visualizations

Edit `journal_dashboard.py` and add after the music section:

```python
# Your new section
section_header("🆕 New Feature", """
    Description of what your new feature shows.
""")

# Your visualization code
import plotly.express as px
fig = px.bar(filtered_df, x='date', y='word_count')
st.plotly_chart(fig, use_container_width=True)
```

### Changing Color Schemes

Plotly charts use Plotly's default colors. To change:

```python
fig = px.bar(data, x='x', y='y', color_discrete_sequence=['#FF6B6B'])
```

Or use Plotly themes:
```python
fig.update_layout(template='plotly_dark')  # Dark mode
fig.update_layout(template='simple_white')  # Minimalist
```

### Adjusting Chart Heights

```python
fig.update_layout(height=600)  # Taller chart
st.plotly_chart(fig, use_container_width=True)
```

---

## 🎯 Tips for Better Insights

### Get More From Visualizations

- **Use date filters** — Focus on specific time periods
- **Hover charts** — See exact values and dates
- **Spot patterns** — Look for correlations (e.g., low sentiment on busy weeks)
- **Track streaks** — Use consistency stats to stay motivated

### Improve Music Detection

Write clearly about songs:
- ✅ "listened to 'Everlong' by Foo Fighters"
- ✅ "Song: 'Karma Police'"
- ❌ "great tune today" (too vague)

### Better Sentiment Tracking

- **Emotionally expressive entries** produce better sentiment scores
- **Neutral/factual entries** score near 0 (which is fine!)
- **Mixed emotions** average out — consider splitting entries

---

## 🐛 Troubleshooting

### Dashboard won't start
- Make sure streamlit is installed: `pip install streamlit`
- Use: `python -m streamlit run journal_dashboard.py`
- Check no other app is using port 8501

### "No journal entries found"
- Check OCR output path in sidebar
- Verify `ocr_output/text/` has `.txt` files
- Make sure metadata JSON files exist

### Chat interface "database not found"
- Run RAG ingestion first: `Ingest_Journals.bat`
- Check path in sidebar matches actual database location
- Verify `vector_db/` folder exists

### Music section shows no results
- Songs must be mentioned explicitly in journals
- Use clear patterns (see Music Detection section)
- iTunes API may not find very obscure artists

### Sentiment seems wrong
- VADER works best on emotional, expressive text
- Neutral/factual entries naturally score near 0
- Very short entries may be less accurate

### Charts not showing
- Check date filter hasn't excluded all entries
- Try refreshing the page (F5)
- Check browser console for errors (F12)

---

## 📊 Performance

**Load Time:**
- ~2-5 seconds for 100 entries
- Depends on entry length and number of visualizations
- Sentiment analysis is cached (runs once)

**Music Detection:**
- ~1-3 seconds per unique song
- iTunes API is rate-limited but generous
- Results are cached during session

**Chat Search:**
- ~100-300ms per query (RAG search)
- +2-10 seconds if using LLM
- Most time is LLM generation, not search

**Memory:**
- ~50-100MB for dashboard
- ~200-500MB if using LLM (Ollama)

---

## 🔗 Integration

### With OCR Module

```python
# Dashboard reads directly from OCR output
ocr_output_dir = "../ocr/ocr_output"
df = load_journal_data(ocr_output_dir)
```

### With RAG Module

```python
# Chat interface uses RAG for search
from journal_rag import JournalRAG
rag = JournalRAG(db_path="../rag/vector_db")
results = rag.search(query)
```

### Standalone Usage

Can be used without OCR if you have text files:

```
my_journals/
├── text/
│   ├── 2026-02-01.txt
│   └── 2026-02-02.txt
└── metadata/
    ├── 2026-02-01.json
    └── 2026-02-02.json
```

Point dashboard to `my_journals/` instead.

---

## 🚀 Advanced Features

### Sidebar RAG Search

Analytics dashboard has a mini RAG search in sidebar:
1. Enter search query
2. Click "🔎 Search"
3. Results appear in sidebar (doesn't leave analytics view)

### Direct Ingestion

From analytics dashboard sidebar:
- Click "📥 Ingest to RAG"
- Loads OCR output into RAG database
- No need to use command line

### Help Tooltips

Every section has a "ℹ️ What does this show?" expander:
- Click to see explanation
- Collapsed by default to reduce clutter
- Explains what charts mean and how to use them

---

## 🔒 Privacy & Security

- ✅ **Runs locally** — web interface is just localhost
- ✅ **No cloud** — all processing on your PC
- ✅ **No tracking** — Streamlit doesn't phone home
- ✅ **iTunes API** — Only sends song/artist names (e.g., "Everlong Foo Fighters")

**Note:** Music detection sends song names to iTunes API for metadata. No journal content or personal data is shared.

---

## 📚 Technical Stack

- **Streamlit** — Web framework (Python-based)
- **Plotly** — Interactive charts
- **Pandas** — Data manipulation
- **VADER** — Sentiment analysis
- **iTunes Search API** — Music metadata
- **ChromaDB** — Vector database (via RAG module)

---

## 🎨 Customizing the UI

### Streamlit Configuration

Create `.streamlit/config.toml`:

```toml
[theme]
primaryColor = "#FF6B6B"
backgroundColor = "#FFFFFF"
secondaryBackgroundColor = "#F0F2F6"
textColor = "#262730"
font = "sans serif"

[server]
port = 8501
headless = true
```

### Page Layout

Dashboard uses `wide` layout for more space. To change:

```python
st.set_page_config(
    page_title="Journal Analytics",
    page_icon="📔",
    layout="centered"  # or "wide"
)
```

---

## 🔄 Workflow Recommendations

### Daily

- Launch chat interface
- Ask questions about recent entries
- Get quick insights

### Weekly

- Launch analytics dashboard
- Check sentiment trends
- Review writing consistency

### Monthly

- Export insights (screenshot charts)
- Reflect on patterns
- Set journaling goals based on streaks

---

## 🛣️ Future Improvements

- [ ] Export dashboard as PDF report
- [ ] Downloadable charts as images
- [ ] Custom date comparisons (e.g., "this month vs last month")
- [ ] Topic modeling and theme extraction
- [ ] Network graphs of people/places mentioned
- [ ] Dark mode toggle
- [ ] Mobile-responsive layout

---

## 📄 Additional Files

- **`music_extraction.py`** — Music detection logic
- **`chat_interface.py`** — Helper functions for chat (legacy, not currently used)
- **`requirements.txt`** — Python dependencies

---

**For more details, see the main [README](../README.md) or other component docs.**

# Reflecting Pool

A complete, self-hosted system for digitizing, searching, and analyzing handwritten journal entries — with zero cloud dependencies.

[![Privacy First](https://img.shields.io/badge/Privacy-First-green.svg)](https://github.com) [![Self Hosted](https://img.shields.io/badge/Self-Hosted-blue.svg)](https://github.com) [![Windows](https://img.shields.io/badge/Windows-Compatible-blue.svg)](https://github.com)

## 🌟 What This Does

Transform your handwritten journals into a searchable, analyzable digital archive:

1. **📸 Digitize** — OCR handwritten journal photos (iPhone HEIC supported)
2. **🔍 Search** — Semantic search with AI-powered Q&A over all your entries
3. **📊 Analyze** — Interactive dashboards with sentiment analysis, writing patterns, and music mentions
4. **🎵 Discover** — Automatically detect and link songs mentioned in your journals
5. **🎨 Customize** — Style the dashboard to your taste with live CSS theming

Everything runs **100% locally** on your Windows PC. No cloud services. Complete privacy.

---

## 🚀 Quick Start (30 seconds)

1. **Clone or download** this repository
2. **Double-click** `Journal_System.bat` in the root folder
3. **Follow the menu** to process photos, search entries, or launch dashboards

That's it! The main launcher gives you access to everything.

---

## 📁 Project Structure

```
journal-project/
├── Journal_System.bat        # 🎯 Main launcher - start here!
├── ocr/                       # OCR pipeline for digitizing photos
│   ├── journal_ocr.py        # Core OCR processing
│   ├── auto_ocr_watcher.py   # Auto-process new photos
│   ├── Process_Photos.bat    # Batch process folders
│   ├── Process_Single_Photo.bat
│   ├── Start_Watcher.bat     # Monitor folder for new photos
│   └── README.md             # Detailed OCR setup
├── rag/                       # Semantic search & AI Q&A
│   ├── journal_rag.py        # RAG system with ChromaDB + Ollama
│   ├── Ingest_Journals.bat   # Load entries into database
│   ├── Search_Journals.bat   # Command-line search
│   ├── Manage_Database.bat   # List/delete entries
│   └── README.md             # RAG setup & usage
├── dashboard/                 # Interactive web dashboards
│   ├── journal_dashboard.py  # Analytics dashboard
│   ├── journal_chat.py       # Chatbot interface
│   ├── music_extraction.py   # Music detection module
│   ├── Launch_Dashboard.bat  # Start analytics view
│   ├── Launch_Chat.bat       # Start chat interface
│   └── README.md             # Dashboard features
└── README.md                 # 👈 You are here
```

---

## ⚡ Features

### OCR Pipeline
- **Supports all formats**: HEIC (iPhone), JPG, PNG, JPEG
- **Folder watcher**: Auto-processes new photos as they arrive
- **Batch processing**: Process hundreds of photos at once
- **Smart preprocessing**: Denoising, contrast enhancement, deskewing
- **Multiple engines**: Tesseract (default) or PaddleOCR

### RAG Search System
- **Semantic search**: Find entries by meaning, not just keywords
- **AI-powered Q&A**: Ask questions, get answers from your journals
- **Date range queries**: Filter by specific time periods
- **Interactive CLI**: Search from the command line
- **Sidebar search**: Run RAG queries directly from the dashboard sidebar without leaving the analytics view
- **Database management**: List, delete, or clear entries

### Analytics Dashboard
- **At-a-glance metrics**: Total entries, total words, average words per entry, and days covered are pinned above all tabs so they're always visible
- **Section help tooltips**: Every chart and section has a collapsible ℹ️ expander explaining exactly what it shows and how to read it
- **Sentiment analysis**: Track emotional tone over time (VADER)
- **Writing patterns**: Consistency heatmaps, word count trends
- **Most common words**: See your most-used vocabulary
- **Streak tracking**: Current and longest journaling streaks
- **Interactive charts**: Hover, zoom, filter by date range

### Music Tab
- **Automatic detection**: Finds songs and artists mentioned anywhere in your entries
- **iTunes artwork**: Each detected song is displayed as a card with album art pulled from the iTunes API
- **Rich metadata**: Shows song title, artist, album, duration, and genre
- **Mention stats**: Displays how many times each song appears and when it was last mentioned
- **Preview & links**: Links directly to Apple Music previews and iTunes pages
- **Music extraction module**: Powered by `music_extraction.py`, a standalone module that can be used independently of the dashboard

### Appearance Tab *(new)*
- **Live CSS theming**: Instantly restyle the entire dashboard without touching any code
- **Typography controls**: Choose separate fonts for body text and headings (Georgia, Garamond, Palatino, and more), set base font size, and adjust line height
- **Color pickers**: Independently control body text, headings, links/accents, metric values, page background, and sidebar background
- **Spacing & layout**: Sliders for content padding, section gaps, metric label size, and card border radius
- **Quick presets**: Four one-click themes — 🌙 Dark Ink, 📜 Parchment, 🧊 Minimal, and 🌿 Sage — to jump-start your look
- **Live preview**: A sample journal entry renders in real time as you adjust settings
- **CSS export**: Copy a ready-to-use CSS snippet to save or share your custom theme

### Chat Interface
- **Conversational search**: Ask questions naturally
- **Source citations**: See which entries informed each answer
- **LLM integration**: Optional Ollama for AI-generated responses
- **Chat history**: Conversation persists during session

---

## 🛠️ Installation

### Prerequisites
- **Python 3.9+** (tested on 3.13)
- **Windows** (10 or 11)
- **~2GB disk space** for dependencies
- **8GB+ RAM** (16GB recommended for LLM features)

### One-Time Setup

1. **Install Python dependencies:**
   ```cmd
   # OCR
   cd ocr
   pip install -r requirements.txt

   # RAG
   cd ..\rag
   pip install -r requirements.txt

   # Dashboard
   cd ..\dashboard
   pip install -r requirements.txt
   ```

2. **Install Tesseract OCR** (Windows):
   - Download from: https://github.com/UB-Mannheim/tesseract/wiki
   - Install to default location: `C:\Program Files\Tesseract-OCR`

3. **(Optional) Install Ollama** for AI Q&A:
   - Download from: https://ollama.ai
   - Run: `ollama pull llama3.3`

That's it! Now use `Journal_System.bat` for everything.

---

## 📖 Usage

### Daily Workflow

1. **Take photos** of journal pages with your iPhone
2. **Transfer photos** to your PC (OneDrive, iCloud, email, etc.)
3. **Run watcher** (option 3 in main menu) to auto-process new photos
4. **Search & chat** with your journals anytime

### Using the Main Menu

**Double-click `Journal_System.bat`** and you'll see:

```
========================================
   JOURNAL PROCESSING SYSTEM
========================================

OCR (Digitize Photos):
  1. Process folder of photos
  2. Process single photo
  3. Start auto-watcher

RAG (Search Engine):
  4. Ingest journals to database
  5. Search journals (command line)
  6. Manage database (list/delete entries)

Dashboard (Analytics):
  7. Launch analytics dashboard
  8. Launch chat interface

  0. Exit
```

### First Time Setup

1. Choose **option 1** → Enter path to your journal photos
2. Choose **option 4** → Ingest OCR'd entries into RAG database
3. Choose **option 8** → Launch chat interface to start asking questions!

---

## 🔒 Privacy & Security

- ✅ **100% self-hosted** — all processing happens on your PC
- ✅ **No cloud services** — no data leaves your machine
- ✅ **No API keys required** — except optional Ollama for local LLM
- ✅ **Works offline** — after initial setup
- ✅ **Your data, your control** — everything stored locally

**Music feature note**: Only song/artist names (e.g., "Everlong Foo Fighters") are sent to the iTunes API for metadata lookup. No journal text or context is ever shared.

---

## 🎯 Typical Use Cases

### "I want to search my old journals"
1. Process your photos (option 1)
2. Ingest to RAG (option 4)
3. Launch chat (option 8)
4. Ask: "What was I worried about last month?"

### "I want to see my writing patterns"
1. Process your photos (option 1)
2. Launch dashboard (option 7)
3. Explore sentiment trends, word frequency, writing streaks

### "I want to know what music I've been listening to"
1. Process journals where you mention songs
2. Ingest to RAG (option 4)
3. Launch dashboard (option 7)
4. Open the **🎵 Music** tab

### "I want to customize how the dashboard looks"
1. Launch dashboard (option 7)
2. Open the **🎨 Appearance** tab
3. Pick a preset or dial in your own fonts, colours, and spacing

### "I just want to automatically process new photos"
1. Set up folder watcher (option 3)
2. Point it to your iPhone sync folder
3. Let it run in the background — new photos are processed automatically

---

## 🐛 Troubleshooting

### OCR not finding files
- Make sure you selected the correct format (HEIC for iPhone)
- Check that photos are in the folder you specified
- Try processing a single photo first (option 2)

### Dashboard shows wrong word counts
- The OCR might be producing garbled text
- Manually edit the `.txt` files in `ocr_output/text/`
- Word counts will update on next dashboard refresh

### RAG database not found
- Run "Ingest journals to database" (option 4) first
- Make sure OCR has completed and `ocr_output/text/` has `.txt` files

### Sidebar search returns no results
- Make sure you've ingested entries first (option 4)
- Check that the RAG Database Path in the sidebar matches your actual `vector_db` location

### Chat interface errors
- Check that you've run ingestion (option 4)
- For LLM features, make sure Ollama is installed and running
- Try searching without LLM first

### Music not detected
- Write about songs with clear patterns:
  - `listened to "Song Title" by Artist`
  - `listening to Artist Name`
  - `Song: "Title"`

### Appearance tab styles not applying
- Make sure you click away from a colour picker or move a slider to trigger a rerun
- Preset buttons apply their values immediately to the CSS preview; use them as a starting point and adjust from there

---

## 💡 Tips for Better Results

### OCR Quality
- **Take clear photos** — good lighting, no shadows
- **Avoid blurry images** — hold phone steady
- **Straight angles** — the system can deskew slight tilts
- **One page at a time** — don't try to capture multiple pages
- **Consider manual transcription** — OCR struggles with cursive handwriting

### Search Quality
- **Be specific** — "What did I write about anxiety in January?" vs. "anxiety"
- **Use natural language** — the RAG system understands meaning
- **Date ranges help** — "Find entries about work from last month"

### Music Detection
- **Use quotes** — `listened to "Song Title"`
- **Mention artists** — `been listening to Artist Name`
- **Be explicit** — `Song: "Title"` works great

---

## 📚 Additional Documentation

- **[ocr/README.md](ocr/README.md)** — Detailed OCR setup, preprocessing, troubleshooting
- **[rag/README.md](rag/README.md)** — RAG system architecture, search tips, LLM setup
- **[dashboard/README.md](dashboard/README.md)** — Dashboard features, customization, analytics

---

## 🛣️ Roadmap

- [x] OCR Pipeline with HEIC support
- [x] Automatic folder watcher
- [x] RAG semantic search
- [x] Interactive dashboards
- [x] Chat interface
- [x] Sentiment analysis (VADER)
- [x] Music detection & linking with iTunes artwork
- [x] Database management
- [x] At-a-glance metrics pinned above tabs
- [x] Section help tooltips throughout dashboard
- [x] RAG search integrated into dashboard sidebar
- [x] Appearance tab with live CSS theming and presets
- [ ] Better handwriting OCR (exploring alternatives)
- [ ] Export features (PDF reports, data dumps)
- [ ] Mobile app companion (future)
- [ ] Cloud backup option (end-to-end encrypted)

---

## 🙏 Acknowledgments

Built with:
- **Tesseract OCR** — OCR engine
- **ChromaDB** — Vector database
- **Sentence-Transformers** — Embeddings
- **Streamlit** — Web interface
- **VADER** — Sentiment analysis
- **iTunes API** — Music metadata & artwork

---

## 📄 License

Personal use tool. Feel free to fork, modify, and adapt for your own journaling needs.

---

## 🆘 Support

This is a personal project without official support, but if you run into issues:

1. Check the troubleshooting section above
2. Review the component-specific READMEs in each folder
3. Make sure all dependencies are installed correctly
4. Try each component individually to isolate the problem

---

**Happy journaling! 📔✨**

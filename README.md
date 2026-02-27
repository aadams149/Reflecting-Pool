# Reflecting Pool

A self-hosted system for digitizing, searching, and analyzing handwritten journal entries. Everything runs locally on your PC with no cloud dependencies.

## What It Does

1. **Digitize** - OCR handwritten journal photos (HEIC, JPG, PNG)
2. **Search** - Semantic search with optional AI-powered Q&A
3. **Analyze** - Interactive dashboard with sentiment analysis, writing patterns, and music mentions
4. **Chat** - Conversational search over your journal entries

## Quick Start

```cmd
pip install -r requirements.txt
streamlit run app.py
```

Or use the menu launcher: double-click `Journal_System.bat`.

## Prerequisites

- **Python 3.9+** (tested on 3.13)
- **Tesseract OCR** - [Download for Windows](https://github.com/UB-Mannheim/tesseract/wiki), install to `C:\Program Files\Tesseract-OCR`
- **(Optional) Ollama** - [Download](https://ollama.ai) for local LLM Q&A, then `ollama pull llama3.3`

## Project Structure

```
Reflecting-Pool/
├── app.py                    # Unified Streamlit app (start here)
├── Journal_System.bat        # Windows menu launcher
├── requirements.txt          # Python dependencies
├── ocr/                      # OCR pipeline
│   ├── journal_ocr.py        # Core OCR processing
│   ├── auto_ocr_watcher.py   # Auto-process new photos
│   ├── config.py             # Tesseract path config
│   └── ocr_output/           # Processed journal entries
├── rag/                      # Semantic search engine
│   └── journal_rag.py        # RAG system (ChromaDB + embeddings)
└── dashboard/                # Standalone dashboard components
    ├── journal_dashboard.py  # Analytics dashboard (standalone)
    ├── journal_chat.py       # Chat interface (standalone)
    └── music_extraction.py   # Music detection module
```

## Usage

### The Unified App (`app.py`)

Run `streamlit run app.py` to launch the combined application with these tabs:

- **Analytics** - Sentiment over time, writing consistency, frequency heatmap
- **Words & Themes** - Most common words across entries
- **Music** - Songs/artists mentioned in entries, linked to iTunes
- **Chat** - Conversational semantic search with optional LLM
- **Entries & Stats** - Detailed stats, streaks, recent entries
- **Appearance** - Live CSS theming with presets

### Daily Workflow

1. Take photos of journal pages
2. Transfer to your PC
3. Process with OCR (option 2-4 in the batch launcher, or use the CLI)
4. Ingest into RAG database (sidebar button in the app, or option 5 in launcher)
5. Search, analyze, and chat with your journals

### OCR Processing (CLI)

```cmd
# Process a folder of photos
python ocr/journal_ocr.py path/to/photos -o ocr/ocr_output

# Process a single photo with a date
python ocr/journal_ocr.py photo.heic -d 2026-01-31 -o ocr/ocr_output

# Auto-watch a folder for new photos
python ocr/auto_ocr_watcher.py path/to/watch -o ocr/ocr_output
```

### RAG Database (CLI)

```cmd
# Ingest OCR output into the vector database
python rag/journal_rag.py ingest ocr/ocr_output

# Search from the command line
python rag/journal_rag.py search "what was I worried about"

# Interactive search session
python rag/journal_rag.py interactive --llm
```

## Privacy

- All processing happens on your PC
- No cloud services or API keys required
- Works offline after initial setup
- Only song/artist names are sent to iTunes API for music metadata

## Troubleshooting

| Problem | Fix |
|---------|-----|
| OCR not finding files | Check photo format and folder path. Try a single photo first. |
| Dashboard shows no data | Verify OCR output directory path in the sidebar. |
| RAG database not found | Run ingestion first (sidebar button or CLI). |
| Chat not working | Ensure ingestion is done. For LLM mode, check Ollama is running. |
| Music not detected | Use clear patterns like `listened to "Song" by Artist`. |

## Built With

Tesseract OCR, ChromaDB, Sentence-Transformers, Streamlit, Plotly, VADER, iTunes API

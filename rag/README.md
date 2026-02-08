# Journal RAG System

Semantic search and AI-powered Q&A over your journal entries — ask questions in natural language, get answers from your past self.

## 🎯 What This Module Does

Creates a searchable database of your journal entries using RAG (Retrieval-Augmented Generation). Instead of simple keyword search, it understands meaning — find entries about "feeling anxious" even if you wrote "stressed out" or "worried."

---

## ✨ Features

- **🔍 Semantic Search** — Find entries by meaning, not just exact words
- **🤖 AI Q&A** — Ask questions, get AI-generated answers from your journals
- **📅 Date Range Queries** — Filter by specific time periods
- **💬 Interactive CLI** — Search from the command line
- **🗄️ Database Management** — List, delete, or clear entries
- **🔒 100% Local** — All processing on your PC (optional LLM via Ollama)
- **⚡ Fast** — Powered by ChromaDB vector database

---

## 🚀 Quick Start

### Using Batch Files (Easiest)

1. **Ingest entries** — Double-click `Ingest_Journals.bat`
2. **Search** — Double-click `Search_Journals.bat`
3. **Ask questions** — Use the interactive mode

### Command Line

```cmd
# Ingest OCR output into database
python journal_rag.py ingest ../ocr/ocr_output

# Search
python journal_rag.py search "feeling anxious about work"

# Interactive mode
python journal_rag.py interactive

# With LLM (requires Ollama)
python journal_rag.py interactive --llm
```

---

## 🛠️ Installation

### Prerequisites
- **Python 3.9+**
- **OCR output** from the OCR module (text files in `../ocr/ocr_output/text/`)

### Step 1: Install Dependencies

```cmd
cd rag
pip install -r requirements.txt
```

This installs:
- `sentence-transformers` — Creates meaning-based embeddings
- `chromadb` — Vector database for semantic search
- `requests` — For optional Ollama API calls

### Step 2: (Optional) Install Ollama for AI Q&A

Ollama runs a local LLM for AI-generated answers:

1. **Download** from: https://ollama.ai
2. **Install** and run
3. **Pull a model:**
   ```cmd
   ollama pull llama3.3
   ```

Models available:
- `llama3.3` — Best quality (4GB)
- `mistral` — Faster, good quality (4GB)
- `llama2` — Older but solid (4GB)

---

## 📖 Usage

### Method 1: Batch Files (Recommended)

**Ingest journals:**
- Double-click `Ingest_Journals.bat`
- Reads from `../ocr/ocr_output`
- Creates `vector_db/` folder

**Search journals:**
- Double-click `Search_Journals.bat`
- Type commands like:
  - `search feeling anxious`
  - `dates` — List all entry dates
  - `stats` — Show database info
  - `quit` — Exit

**Manage database:**
- Double-click `Manage_Database.bat`
- Options to list, delete, or clear entries

### Method 2: Command Line

**Ingest:**
```cmd
python journal_rag.py ingest ../ocr/ocr_output
```

**Search:**
```cmd
python journal_rag.py search "what was I worried about in January"
```

**Interactive mode:**
```cmd
python journal_rag.py interactive
```

Commands in interactive mode:
- `search <query>` — Find relevant entries
- `ask <question>` — AI-generated answer (requires Ollama + --llm flag)
- `dates` — List all entry dates
- `list` — Show all entries in database
- `stats` — Database statistics
- `delete <date>` — Remove entry by date (YYYY-MM-DD)
- `clear` — Delete all entries (requires confirmation)
- `quit` — Exit

**With LLM:**
```cmd
python journal_rag.py interactive --llm --model llama3.3
```

**Date range search:**
```cmd
python journal_rag.py range 2026-01-01 2026-01-31 --query "work stress"
```

---

## 🎯 How It Works

### 1. Ingestion

When you run ingestion:
1. **Reads** OCR output text files
2. **Chunks** long entries into smaller pieces (~500 words)
3. **Embeds** each chunk using sentence-transformers
4. **Stores** embeddings in ChromaDB vector database

The embeddings capture semantic meaning, not just keywords.

### 2. Search

When you search:
1. **Embeds** your query using the same model
2. **Finds** similar chunks using vector similarity
3. **Ranks** results by relevance
4. **Returns** top matches with dates and text

### 3. LLM Q&A (Optional)

With Ollama enabled:
1. **Searches** for relevant entries (step 2)
2. **Sends** context to local Ollama LLM
3. **Generates** an answer based on your journals
4. **Cites** which entries were used

---

## 📊 Database Structure

```
vector_db/
├── chroma.sqlite3          # ChromaDB metadata
└── [embedding files]       # Vector embeddings
```

### Metadata Stored Per Chunk

```json
{
  "date": "2026-02-01",
  "chunk_index": 0,
  "word_count": 247,
  "source_file": "entry_20260201.txt"
}
```

---

## 🔍 Search Examples

### Basic Semantic Search

```cmd
> search feeling anxious
```

Finds entries about:
- "I'm stressed about..."
- "Worried about the presentation..."
- "Nervous about tomorrow's meeting..."

Even if you never used the word "anxious"!

### Date Range

```cmd
> range 2026-01-01 2026-01-31 work
```

Finds entries mentioning work in January 2026.

### Ask Questions (with LLM)

```cmd
> ask What was I worried about last month?
```

AI reads your relevant entries and generates an answer like:
> "Based on your journal entries, you were primarily worried about your upcoming work presentation and your friend's health situation. You mentioned feeling unprepared and anxious about public speaking."

---

## 🛠️ Database Management

### List All Entries

```cmd
python journal_rag.py list
```

Shows:
```
2026-02-01 - 3 chunks, ~247 words
2026-02-02 - 5 chunks, ~412 words
2026-02-03 - 2 chunks, ~189 words

Total: 3 entries
```

### Delete Specific Entry

```cmd
python journal_rag.py delete 2026-02-01
```

Removes all chunks from that date.

### Clear Entire Database

```cmd
python journal_rag.py clear
```

⚠️ Requires typing "DELETE ALL" to confirm.

### Show Statistics

```cmd
python journal_rag.py stats
```

Displays:
- Total entries
- Total chunks
- Total words
- Date range

---

## ⚙️ Configuration

### Chunking

Large entries are split into chunks for better search precision. Default: 500 words.

**Adjust chunk size:**
```cmd
python journal_rag.py ingest ../ocr/ocr_output --chunk-size 300
```

Smaller chunks = more precise search, but more database overhead.

### Embedding Model

Default model: `all-MiniLM-L6-v2` (fast, accurate, 80MB)

To use a different model, edit `journal_rag.py`:
```python
rag = JournalRAG(
    db_path="./vector_db",
    embedding_model="all-mpnet-base-v2"  # More accurate, slower, 420MB
)
```

### LLM Model

Default: `llama3.3`

**Change model:**
```cmd
python journal_rag.py interactive --llm --model mistral
```

Available models (run `ollama list`):
- `llama3.3` — Best quality
- `mistral` — Faster
- `llama2` — Older but solid

---

## 🎯 Tips for Better Results

### Writing Queries

✅ **Good queries:**
- "What was I worried about in January?"
- "Entries about my friend Sarah"
- "Times I felt happy and grateful"
- "Work stress and deadlines"

❌ **Less effective:**
- Single words: "work"
- Very vague: "stuff"
- Too specific: exact phrases that need keyword match

### Using LLM Q&A

✅ **Good questions:**
- "Summarize my main worries last month"
- "What patterns do you see in my anxiety?"
- "How did I feel about my job over time?"

❌ **Less effective:**
- "Did I mention coffee?" (use search instead)
- Questions requiring facts outside your journals

### Improving Search Quality

1. **Write descriptive journals** — More detail = better search
2. **Use consistent terminology** — Helps find related entries
3. **Include context** — Don't just list events, describe feelings
4. **Date your entries** — Enables time-based queries

---

## 🐛 Troubleshooting

### "RAG database not found"
- Run ingestion first: `python journal_rag.py ingest ../ocr/ocr_output`
- Check that `../ocr/ocr_output/text/` has `.txt` files

### "No entries found"
- Make sure OCR has completed
- Check that text files aren't empty
- Verify file paths are correct

### LLM not responding
- Check Ollama is running: `ollama list`
- Pull the model: `ollama pull llama3.3`
- Try without `--llm` flag to test search works

### Search returns nothing
- Try broader queries
- Check entries were ingested: `python journal_rag.py stats`
- Verify the date range overlaps with your entries

### "Module not found" errors
- Install dependencies: `pip install -r requirements.txt`
- Make sure you're in the `rag/` directory

---

## 🔗 Integration

### With OCR Module

```cmd
# After OCR processing
cd ..\rag
python journal_rag.py ingest ..\ocr\ocr_output
```

### With Dashboard

The chat interface uses this RAG system:
1. Launch: `Launch_Chat.bat`
2. It automatically connects to `vector_db/`
3. Chat interface is just a GUI wrapper around this module

### With External Scripts

```python
from journal_rag import JournalRAG

# Initialize
rag = JournalRAG(db_path="./vector_db")

# Search
results = rag.search("feeling anxious", n_results=5)

for r in results:
    print(f"{r['date']}: {r['text'][:200]}")
```

---

## 📈 Performance

**Ingestion:**
- 100 entries ≈ 30-60 seconds
- Depends on entry length and chunking
- One-time cost, incremental updates supported

**Search:**
- ~100-300ms per query
- Instant for most use cases
- Scales well to thousands of entries

**LLM Q&A:**
- Adds ~2-10 seconds depending on model
- Most time is LLM generation, not search

**Storage:**
- ~1-5MB per 100 entries (embeddings + metadata)
- Text is not duplicated (references OCR output)

---

## 🔄 Workflow Recommendations

### Daily

1. Journal (handwritten or typed)
2. OCR processes automatically (watcher)
3. No action needed — search works on existing database

### Weekly

1. Run re-ingestion to pick up new entries:
   ```cmd
   python journal_rag.py ingest ../ocr/ocr_output
   ```
   (It skips existing entries automatically)

### Monthly

1. Use chat interface to reflect:
   - "What themes came up this month?"
   - "How did my mood change over time?"
   - "What was I most worried about?"

---

## 📚 Technical Details

### Embedding Model

Uses `all-MiniLM-L6-v2` from sentence-transformers:
- 384-dimensional embeddings
- Trained on 1B+ sentence pairs
- Excellent semantic understanding
- Fast inference (~10ms per chunk)

### Vector Database

ChromaDB:
- SQLite-backed
- Persistent storage
- Cosine similarity search
- Metadata filtering

### LLM Integration

Ollama API:
- Local inference (no cloud)
- Streaming responses
- Customizable prompts
- Multiple model support

---

## 🚀 Advanced Usage

### Custom Prompts

Edit `journal_rag.py` to customize LLM behavior:

```python
def generate(self, question: str, context: List[str]) -> str:
    prompt = f"""You are reading journal entries.
    
Context:
{chr(10).join(context)}

Question: {question}

Answer based only on the journal entries above:"""
```

### Batch Queries

```python
from journal_rag import JournalRAG

rag = JournalRAG()
queries = [
    "work stress",
    "friend mentions",
    "happy moments"
]

for q in queries:
    results = rag.search(q, n_results=3)
    print(f"\n{q}:")
    for r in results:
        print(f"  - {r['date']}")
```

### Export Search Results

```cmd
python journal_rag.py search "anxiety" > results.txt
```

---

## 🔒 Privacy & Security

- ✅ **All processing local** — embeddings generated on your PC
- ✅ **No cloud APIs** — (except optional Ollama, which runs locally)
- ✅ **Data never leaves** — your journal text stays on disk
- ✅ **Open source** — inspect all code
- ✅ **No telemetry** — no tracking, no analytics

**Optional Ollama note:** Ollama runs 100% on your machine. The LLM never connects to the internet.

---

## 📄 Additional Resources

- **sentence-transformers docs**: https://www.sbert.net/
- **ChromaDB docs**: https://docs.trychroma.com/
- **Ollama models**: https://ollama.ai/library

---

**For more details, see the main [README](../README.md) or other component docs.**

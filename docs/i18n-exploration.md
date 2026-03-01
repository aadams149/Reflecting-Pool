# Non-English Language Support — Exploration & Options

This document surveys every language-sensitive component in Reflecting Pool and outlines what would need to change to support non-English journals.

---

## 1. OCR Engine (`ocr/journal_ocr.py`)

### Current State
- **Tesseract**: No `lang` parameter is passed to `pytesseract.image_to_string()`. Tesseract defaults to `eng` when no language is specified.
- **PaddleOCR**: Hardcoded to `lang='en'` on line 125:
  ```python
  self.paddle = PaddleOCR(use_angle_cls=True, lang='en', show_log=False)
  ```

### What Needs to Change
- Add a `language` parameter to `OCREngine.__init__()` and `JournalOCRPipeline.__init__()`.
- Pass it through to Tesseract as `lang=language` and to PaddleOCR as `lang=language`.
- Expose it as a CLI argument (`--lang`) and as a sidebar setting in the dashboard.
- **Tesseract language packs** must be installed separately. On Windows: download `.traineddata` files into the `tessdata` folder. On macOS/Linux: `apt install tesseract-ocr-<lang>` or `brew install tesseract-lang`.
- **PaddleOCR** supports ~80 languages out of the box. Language codes differ from Tesseract (e.g., PaddleOCR uses `ch` for Chinese, Tesseract uses `chi_sim`).

### Difficulty: **Low**
Both OCR engines already have multilingual support built in — this is mostly plumbing a parameter through.

---

## 2. Sentiment Analysis (`app.py`, lines 185–199)

### Current State
- Uses **VADER** (`vaderSentiment`), which is designed specifically for English social-media text. The lexicon is entirely English.
- Called via `get_sentiment(text)` → `SentimentIntensityAnalyzer().polarity_scores(text)["compound"]`

### Options for Multilingual Sentiment

| Option | Pros | Cons |
|--------|------|------|
| **A. `TextBlob` + translation** | Simple API, translate first then score | Requires internet for translation; quality varies |
| **B. `transformers` (Hugging Face)** | Models like `nlptown/bert-base-multilingual-uncased-sentiment` support 6+ languages natively; high accuracy | Heavy dependency (~500 MB+); slow on CPU without GPU |
| **C. `polyglot`** | Supports 130+ languages for sentiment | Requires system-level dependencies (ICU, libpolyglot); difficult Windows install |
| **D. Keep VADER for English, skip for others** | No new dependencies; honest about limitations | Non-English users get no sentiment analysis |
| **E. `XLM-RoBERTa` via `transformers`** | `cardiffnlp/twitter-xlm-roberta-base-sentiment-multilingual` covers 8 languages well | Same weight concerns as option B |

### Recommendation
**Option D (short-term)** + **Option B or E (long-term)**. In the near term, detect the journal language and gracefully show "Sentiment analysis is only available for English entries" for other languages. Long-term, add an optional `transformers`-based model behind a feature flag.

### Difficulty: **Medium–High**
VADER has no multilingual equivalent at the same weight/simplicity. Any real multilingual sentiment requires either a large model or a translation step.

---

## 3. Stop Words & Word Extraction (`app.py`, lines 209–234)

### Current State
- `extract_common_words()` uses a **hardcoded English stop-word set** (~130 words).
- Filters words with `len(w) > 3`, which may not be appropriate for languages like Chinese, Japanese, or Korean where meaningful words can be 1–2 characters.
- Uses `re.findall(r"\b\w+\b", text.lower())` for tokenization, which works for space-delimited languages but **fails entirely for CJK** (Chinese, Japanese, Korean) where words aren't separated by spaces.

### What Needs to Change
- Load stop words dynamically per language. Options:
  - **NLTK stop words**: `nltk.corpus.stopwords.words('spanish')` — covers 20+ languages, small dependency.
  - **`stopwordsiso`** package: covers 50+ languages, pure Python.
  - Ship a `stopwords/` directory with per-language text files.
- Replace regex tokenization with a language-aware tokenizer:
  - For European languages: current regex works fine.
  - For CJK: use `jieba` (Chinese), `MeCab`/`fugashi` (Japanese), `konlpy` (Korean), or the universal `spaCy` tokenizer.
- Adjust the `len(w) > 3` filter per language.

### Difficulty: **Medium**
Stop words are easy. Tokenization is the hard part — CJK support requires dedicated libraries.

---

## 4. RAG / Semantic Search (`rag/journal_rag.py`)

### Current State
- Embedding model: **`all-MiniLM-L6-v2`** (sentence-transformers). This is an English-optimized model.
- ChromaDB uses the default embedding function (which is `all-MiniLM-L6-v2` as well).
- Text chunking splits on characters and looks for `.!?` sentence boundaries — works for Latin-script languages but not ideal for CJK.

### Options for Multilingual Embeddings

| Model | Languages | Size | Quality |
|-------|-----------|------|---------|
| `all-MiniLM-L6-v2` (current) | English only | 80 MB | Good for English |
| `paraphrase-multilingual-MiniLM-L12-v2` | 50+ languages | 420 MB | Good general multilingual |
| `multilingual-e5-small` | 100+ languages | 470 MB | Strong retrieval quality |
| `multilingual-e5-base` | 100+ languages | 1.1 GB | Best quality, heavy |

### What Needs to Change
- Make the embedding model configurable (it already accepts `embedding_model` as a parameter — just need to change the default or add a setting).
- For users who need multilingual search, switch to `paraphrase-multilingual-MiniLM-L12-v2` — it's a drop-in replacement via sentence-transformers with the same API.
- Chunking: Add language-aware sentence splitting (e.g., `pysbd` library supports 22 languages for sentence boundary detection).

### Difficulty: **Low**
The model parameter already exists. Switching to a multilingual model is a one-line default change. The main cost is download size (~420 MB vs ~80 MB).

---

## 5. Music Extraction (`dashboard/music_extraction.py`)

### Current State
- Regex patterns assume **English phrasing**: "listened to", "listening to", "Song:", "by".
- iTunes API is used for search — iTunes supports international music catalogs.
- Pattern 4 (`Artist - Song`) relies on ASCII capitalization rules.

### What Needs to Change
- Add regex patterns for common music-mention phrases in other languages (e.g., Spanish "escuchando", French "j'écoute", German "höre gerade").
- Or take a different approach: use a lightweight NER model to detect song/artist entities regardless of language.
- The iTunes search itself works fine internationally — no changes needed there.

### Difficulty: **Medium**
Adding a few regex patterns per language is feasible but doesn't scale. A proper multilingual solution would use NER, which is a bigger lift.

---

## 6. LLM / Chat (`app.py` tab_chat, `rag/journal_rag.py` OllamaLLM)

### Current State
- The system prompt in `OllamaLLM.generate()` is in English: *"Based on the following journal entries, please answer the question..."*
- Modern LLMs (Llama 3, Mistral) handle multilingual queries reasonably well — if the journal text and user question are in Spanish, the LLM will typically respond in Spanish.

### What Needs to Change
- Minimal changes needed. The prompt template could be translated or made language-neutral.
- Optionally add a language preference setting so the LLM is instructed to respond in the user's language.

### Difficulty: **Low**

---

## 7. UI Text (Dashboard)

### Current State
- All button labels, headers, help text, and info messages are hardcoded English strings throughout `app.py`.

### What Needs to Change
- For a fully localized UI: extract all strings into a translation file (e.g., `locale/en.json`, `locale/es.json`) and load them based on a language setting.
- **However**, this is a major effort (~200+ strings across app.py) and may not be necessary if the goal is just to support non-English *journal content* rather than translating the app UI itself.

### Difficulty: **High** (full UI translation) / **Not needed** (if just supporting non-English content)

---

## Recommended Approach

### Phase 1: Quick wins (low effort, high impact)
1. **OCR language parameter** — Add `--lang` flag to OCR pipeline and a sidebar dropdown in the dashboard. This alone unlocks the core use case: processing non-English journals.
2. **Multilingual embedding model** — Change the default (or add an option) to `paraphrase-multilingual-MiniLM-L12-v2` so search works across languages.
3. **Graceful sentiment fallback** — Detect non-English text and show a message instead of incorrect VADER scores.

### Phase 2: Better multilingual support (medium effort)
4. **Language-aware stop words** — Use NLTK or `stopwordsiso` to load stop words dynamically.
5. **Music pattern expansion** — Add regex patterns for 3–5 most common languages.
6. **LLM prompt localization** — Add a language preference for chat responses.

### Phase 3: Full internationalization (high effort)
7. **Multilingual sentiment** — Integrate a `transformers`-based multilingual model behind a feature flag.
8. **CJK tokenization** — Add dedicated tokenizers for Chinese, Japanese, Korean.
9. **UI translation** — Extract strings to translation files (only if there's demand).

---

## Language Detection

A useful utility for all phases: automatic language detection. Options:
- **`langdetect`** — Port of Google's language detection, pure Python, lightweight. Detects 55 languages.
- **`lingua-py`** — More accurate than langdetect, supports 75 languages, pure Python.
- **`fasttext`** (via `fasttext-langdetect`) — Very fast and accurate, but requires a binary model (~917 KB).

Recommendation: Use `langdetect` for simplicity — it's a single `pip install` with no binary dependencies.

# Journal OCR Pipeline

Convert handwritten journal photos into searchable text — fully automated, completely private.

## 🎯 What This Module Does

Takes photos of your handwritten journal pages and extracts the text using OCR (Optical Character Recognition). Supports batch processing, automatic folder watching, and multiple image formats including iPhone's HEIC.

---

## ✨ Features

- **📸 HEIC Support** — Works with iPhone photos natively
- **🔄 Batch Processing** — Process entire folders at once
- **👁️ Folder Watcher** — Auto-process new photos as they arrive
- **🎨 Smart Preprocessing** — Denoising, contrast enhancement, deskewing
- **🔧 Multiple OCR Engines** — Tesseract (fast) or PaddleOCR (better for handwriting)
- **📊 Metadata Tracking** — JSON files with dates, word counts, processing info
- **🔒 Privacy-First** — Everything runs locally on your PC

---

## 🚀 Quick Start

### Using the Batch Files (Easiest)

1. **Double-click** `Process_Photos.bat`
2. **Enter the path** to your journal photos folder
3. **Select format** (1 for HEIC, 2 for JPG, etc.)
4. **Wait** — OCR processes all photos
5. **Done!** Text files are in `ocr_output/text/`

### Using the Folder Watcher

1. **Double-click** `Start_Watcher.bat`
2. **Enter the path** to monitor (e.g., OneDrive sync folder)
3. **Leave it running** — new photos are processed automatically
4. **Stop** with Ctrl+C when done

---

## 📁 Output Structure

After processing, you'll find:

```
ocr_output/
├── text/                    # Extracted text files
│   ├── entry_20260201.txt
│   ├── entry_20260202.txt
│   └── ...
├── metadata/                # JSON metadata
│   ├── entry_20260201.json
│   ├── entry_20260202.json
│   └── ...
└── preprocessed/            # (Optional) Preprocessed images
    ├── entry_20260201_preprocessed.png
    └── ...
```

### Metadata Format

Each `.json` file contains:
```json
{
  "original_image": "C:\\path\\to\\photo.heic",
  "entry_date": "2026-02-01",
  "processed_at": "2026-02-01T15:30:00",
  "text_file": "C:\\path\\to\\ocr_output\\text\\entry_20260201.txt",
  "word_count": 247,
  "char_count": 1543
}
```

---

## 🛠️ Installation

### Prerequisites
- **Python 3.9+**
- **Windows 10/11**

### Step 1: Install Tesseract OCR

1. **Download** from: https://github.com/UB-Mannheim/tesseract/wiki
2. **Run installer** — use default location (`C:\Program Files\Tesseract-OCR`)
3. **Restart terminal** to pick up PATH changes

### Step 2: Install Python Dependencies

```cmd
cd ocr
pip install -r requirements.txt
```

This installs:
- `pytesseract` — Python wrapper for Tesseract
- `opencv-python` — Image preprocessing
- `Pillow` — Image loading
- `pillow-heif` — HEIC format support
- `numpy` — Array operations
- `watchdog` — Folder monitoring

### Step 3: (Optional) Install PaddleOCR

PaddleOCR generally works better on handwritten text, but it's slower and larger:

```cmd
pip install paddleocr paddlepaddle
```

---

## 📖 Usage

### Method 1: Batch Files (Recommended)

**Process entire folder:**
- Double-click `Process_Photos.bat`
- Select HEIC (1) for iPhone photos
- Enter folder path

**Process single photo:**
- Double-click `Process_Single_Photo.bat`
- Enter photo path
- Optionally enter date (YYYY-MM-DD)

**Auto-monitor folder:**
- Double-click `Start_Watcher.bat`
- Enter folder to watch
- Leave running — processes new files automatically

### Method 2: Command Line

**Basic usage:**
```cmd
python journal_ocr.py path\to\photo.heic
```

**With date:**
```cmd
python journal_ocr.py photo.heic --date 2026-02-01
```

**Batch process folder (HEIC files):**
```cmd
python journal_ocr.py C:\Photos\Journals --pattern "*.heic"
```

**Use PaddleOCR instead of Tesseract:**
```cmd
python journal_ocr.py photo.heic --engine paddleocr
```

**Save preprocessed images:**
```cmd
python journal_ocr.py photo.heic --save-preprocessed
```

**Custom output directory:**
```cmd
python journal_ocr.py photo.heic --output my_output
```

### Method 3: Folder Watcher

**Start watcher:**
```cmd
python auto_ocr_watcher.py C:\Users\YourName\OneDrive\Journal_Entries
```

**With custom output:**
```cmd
python auto_ocr_watcher.py watch_folder --output custom_output
```

The watcher:
- Monitors the folder for new files
- Processes them automatically when added
- Supports HEIC, JPG, JPEG, PNG
- Runs until you press Ctrl+C

⚠️ **Important**: The watcher only processes files added *after* it starts. To process existing files, use batch processing first.

---

## ⚙️ Configuration

### Tesseract Path (Windows)

If Tesseract isn't found, edit `config.py`:

```python
import pytesseract

# Set explicit path to Tesseract executable
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
```

### Preprocessing Options

In `journal_ocr.py`, the `preprocess()` method applies:
1. **Denoising** — Removes camera noise
2. **Grayscale conversion** — Simplifies to black/white
3. **Contrast enhancement** — Makes text more distinct
4. **Binarization** — Converts to pure black/white
5. **Deskewing** — Straightens tilted images

You can adjust these in the code if needed.

---

## 🎯 Tips for Better OCR Results

### Photography
- ✅ **Use good lighting** — Natural light is best
- ✅ **Hold camera steady** — Reduce motion blur
- ✅ **Straight angle** — Minimize tilt (some deskewing is automatic)
- ✅ **One page at a time** — Don't capture multiple pages
- ✅ **Avoid shadows** — Position light source evenly
- ❌ **Don't use flash** — Can create harsh shadows

### Handwriting
- ✅ **Print letters work better** than cursive
- ✅ **Neat, spaced writing** improves accuracy
- ✅ **Dark ink** (black/blue) reads better than light colors
- ❌ **Pencil** can be challenging (graphite reflects light)
- ❌ **Very small writing** may not be detected

### Realistic Expectations

**Tesseract and PaddleOCR struggle with cursive handwriting.** If your journals are handwritten in cursive:
- Expect 30-70% accuracy depending on writing clarity
- Consider **manual transcription** for important entries
- Use OCR as a **rough draft** and edit the `.txt` files
- The RAG system can still work with imperfect text for keyword search

**For best results:** Type your journal entries directly into `.txt` files or use very neat print handwriting.

---

## 🐛 Troubleshooting

### "Tesseract not found"
- Make sure Tesseract is installed to `C:\Program Files\Tesseract-OCR`
- Check `config.py` has the correct path
- Restart your terminal after installing Tesseract

### "HEIC files not supported"
- Run: `pip install pillow-heif --break-system-packages`
- If still failing, convert HEIC to JPG first

### "No files found"
- Check you selected the right format (1 for HEIC)
- Verify files are actually in the folder
- Try absolute paths: `C:\Users\Name\Photos\` not `Photos\`

### OCR output is garbled
- This is normal for cursive handwriting
- Try PaddleOCR: `--engine paddleocr`
- Consider manual transcription
- Edit the `.txt` files in `ocr_output/text/` directly

### Watcher not processing existing files
- The watcher only processes NEW files added after it starts
- Use `Process_Photos.bat` for existing files first
- Then start the watcher for future photos

---

## 📊 Performance

**Tesseract:**
- ~2-5 seconds per image
- Good for printed text
- Struggles with handwriting

**PaddleOCR:**
- ~5-15 seconds per image
- Better for handwriting
- Still struggles with cursive
- Requires more RAM

**Batch Processing:**
- Processes images sequentially
- 100 photos ≈ 5-25 minutes depending on engine

---

## 📚 File Organization Tips

### Naming Your Photos

**Good naming conventions:**
- `entry_20260201.heic` — Date-based
- `journal_2026_02_01.heic` — Also date-based
- `IMG_1234.heic` — Camera default (use `--date` flag)

**When processing:**
```cmd
# With date flag
python journal_ocr.py IMG_1234.heic --date 2026-02-01

# Or rename files first
ren IMG_1234.heic entry_20260201.heic
python journal_ocr.py entry_20260201.heic
```

### Folder Structure Recommendation

```
Journal_Photos/
├── 2026/
│   ├── 01_January/
│   │   ├── entry_20260101.heic
│   │   ├── entry_20260102.heic
│   │   └── ...
│   └── 02_February/
│       └── entry_20260201.heic
└── 2025/
    └── ...
```

---

## 🔗 Integration

### With RAG System

After OCR processing:
1. OCR outputs go to `ocr_output/text/`
2. Run RAG ingestion: `python ..\rag\journal_rag.py ingest ocr_output`
3. Now you can search your journals semantically

### With Dashboard

The dashboard automatically reads from `ocr_output/`:
1. Launch dashboard: `Launch_Dashboard.bat`
2. Enter path: `../ocr/ocr_output`
3. Dashboard displays analytics

---

## 🔄 Workflow Recommendation

### Daily Routine

1. **Take photos** with iPhone throughout the day
2. **Photos auto-sync** to OneDrive/iCloud on your PC
3. **Watcher processes** them automatically in background
4. **Text available** for search and analytics immediately

### Setup Once

1. Install dependencies
2. Start `Start_Watcher.bat` on your sync folder
3. Optionally add watcher to Windows startup

---

## 📄 Additional Files

- **`WINDOWS_SETUP.md`** — Windows-specific setup instructions
- **`iOS_AUTOMATION_GUIDE.md`** — iPhone shortcuts for automation
- **`config.py`** — Tesseract path configuration

---

## ⚠️ Known Limitations

- **Cursive handwriting** recognition is poor (30-70% accuracy)
- **Mixed scripts** (handwritten + printed) can confuse the OCR
- **Colored backgrounds** may interfere with text detection
- **Very small text** (<10pt font equivalent) may not be detected
- **Faded ink** or pencil can be hard to read

---

## 🚀 Future Improvements

- [ ] Better handwriting recognition (exploring cloud APIs)
- [ ] GPU acceleration for faster processing
- [ ] Multi-page support (process book spreads)
- [ ] Real-time camera OCR (process as you photograph)
- [ ] Handwriting training (fine-tune models on your writing)

---

**For more details, see the main [README](../README.md) or other component docs.**

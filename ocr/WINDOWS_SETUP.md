# Windows Setup Guide for Journal OCR

This guide covers Windows-specific setup for the OCR pipeline.

## Prerequisites

### 1. Install Python

Download Python 3.9+ from: https://www.python.org/downloads/

**Important:** During installation, check "Add Python to PATH"

Verify installation:
```cmd
python --version
```

### 2. Install Tesseract OCR

**Option A: Using Installer (Recommended)**

1. Download from: https://github.com/UB-Mannheim/tesseract/wiki
2. Run the installer (tesseract-ocr-w64-setup-*.exe)
3. **Important:** Note the installation path (usually `C:\Program Files\Tesseract-OCR`)
4. Add Tesseract to PATH:
   - Search for "Environment Variables" in Windows
   - Edit "Path" in System Variables
   - Add: `C:\Program Files\Tesseract-OCR`
   - Click OK

**Option B: Using Chocolatey**
```cmd
choco install tesseract
```

**Verify installation:**
```cmd
tesseract --version
```

If this doesn't work, you'll need to set the path in the Python code (see below).

### 3. Install Python Dependencies

```cmd
cd ocr
pip install -r requirements.txt
```

## Windows-Specific Configuration

### Setting Tesseract Path (if needed)

If `tesseract --version` doesn't work from command line, you need to set the path in Python.

Create a file `ocr/config.py`:

```python
import pytesseract

# Set Tesseract path for Windows
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
```

Then modify the import in `journal_ocr.py` - at the top of the file, add:

```python
try:
    from config import *
except ImportError:
    pass  # Config file not needed if tesseract is in PATH
```

## iPhone to Windows PC Workflow

Since iCloud on Windows doesn't support the same folder structure as Mac, here are your options:

### Option 1: iCloud for Windows + Folder Watcher (Recommended)

1. **Install iCloud for Windows**
   - Download from: https://support.apple.com/en-us/HT204283
   - Sign in with your Apple ID
   - Enable iCloud Photos

2. **Set up Photos folder**
   - iCloud Photos downloads to: `C:\Users\YourName\Pictures\iCloud Photos`
   - Create album "Journal Entries" on iPhone
   - Photos in this album sync to PC

3. **Find the synced folder**
   - Navigate to: `C:\Users\YourName\Pictures\iCloud Photos\`
   - Look for your album folder (may be under "Albums" or similar)

4. **Run the watcher**
   ```cmd
   cd ocr
   python auto_ocr_watcher.py "C:\Users\YourName\Pictures\iCloud Photos\Albums\Journal Entries"
   ```

### Option 2: Google Photos (Alternative)

If iCloud sync is problematic:

1. Install Google Photos Desktop Uploader
2. Create "Journal Entries" album
3. Set to auto-upload from iPhone
4. Watch the Google Photos folder on PC:
   ```cmd
   python auto_ocr_watcher.py "C:\Users\YourName\Google Photos\Journal Entries"
   ```

### Option 3: Manual Transfer (Most Reliable)

1. **Email yourself** the journal photos
2. Save to a folder like `C:\Users\YourName\Documents\JournalPhotos`
3. Run OCR on the folder:
   ```cmd
   python journal_ocr.py "C:\Users\YourName\Documents\JournalPhotos"
   ```

### Option 4: OneDrive

1. Install OneDrive (built into Windows 10/11)
2. Install OneDrive app on iPhone
3. Create folder "Journal Entries"
4. Enable auto-upload from iPhone camera roll
5. Watch the OneDrive folder:
   ```cmd
   python auto_ocr_watcher.py "C:\Users\YourName\OneDrive\Journal Entries"
   ```

## Path Format in Windows

**Important:** Windows uses backslashes (`\`) in paths, but Python accepts both:

✅ **These all work:**
```python
"C:\\Users\\YourName\\Pictures"           # Escaped backslashes
r"C:\Users\YourName\Pictures"             # Raw string (r prefix)
"C:/Users/YourName/Pictures"              # Forward slashes (Python converts)
```

❌ **This doesn't work:**
```python
"C:\Users\YourName\Pictures"              # Unescaped backslashes
```

**Recommendation:** Use forward slashes or raw strings (r"...") for paths.

## Running Scripts on Windows

### Basic Usage

```cmd
# Navigate to project
cd C:\path\to\journal-project\ocr

# Process single image
python journal_ocr.py "C:\Users\YourName\Pictures\journal_photo.jpg"

# Process folder
python journal_ocr.py "C:\Users\YourName\Pictures\JournalPhotos"

# Start folder watcher
python auto_ocr_watcher.py "C:\Users\YourName\Pictures\JournalPhotos"
```

### Running Watcher in Background

**Option A: Keep Command Prompt Open**
Just leave the command prompt window running.

**Option B: Run as Background Task**
1. Create a batch file `start_ocr_watcher.bat`:
   ```batch
   @echo off
   cd C:\path\to\journal-project\ocr
   python auto_ocr_watcher.py "C:\Users\YourName\Pictures\Journal Entries"
   ```

2. Create a shortcut to this batch file
3. Place in Startup folder: `C:\Users\YourName\AppData\Roaming\Microsoft\Windows\Start Menu\Programs\Startup`

**Option C: Task Scheduler**
1. Open Task Scheduler
2. Create Basic Task
3. Trigger: "At log on"
4. Action: "Start a program"
5. Program: `python.exe`
6. Arguments: `C:\path\to\journal-project\ocr\auto_ocr_watcher.py "C:\Users\YourName\Pictures\Journal Entries"`
7. Start in: `C:\path\to\journal-project\ocr`

## Output Paths

The OCR output will be created at:
```
C:\path\to\journal-project\ocr\ocr_output\
  ├── text\
  ├── metadata\
  └── preprocessed\
```

Or specify custom output:
```cmd
python journal_ocr.py input_folder --output "C:\Users\YourName\Documents\OCR_Results"
```

## Common Windows Issues

### "python is not recognized"
- Python not in PATH
- Solution: Reinstall Python and check "Add to PATH" option
- Or use full path: `C:\Users\YourName\AppData\Local\Programs\Python\Python311\python.exe`

### "tesseract is not recognized"
- Tesseract not in PATH
- Solution: Add to PATH or set in config.py (see above)

### "Permission denied" errors
- Running from protected folder
- Solution: Use Documents or Pictures folder instead of Program Files

### "Module not found" errors
- Dependencies not installed
- Solution: `pip install -r requirements.txt`

### Antivirus blocking Python
- Some antivirus software flags Python scripts
- Solution: Add Python folder to antivirus exceptions

### File paths with spaces
- Use quotes around paths with spaces:
  ```cmd
  python journal_ocr.py "C:\Users\Your Name\Pictures\Journals"
  ```

## Performance on Windows

- OCR speed: Similar to Mac/Linux
- Folder watcher: Works identically
- Memory usage: Same as other platforms

**Recommended specs:**
- Windows 10/11
- 8GB+ RAM
- SSD for faster file operations

## Next Steps

After OCR is working:

1. **Set up RAG system:**
   ```cmd
   cd ..\rag
   pip install -r requirements.txt
   python journal_rag.py ingest ..\ocr\ocr_output
   ```

2. **Set up Dashboard:**
   ```cmd
   cd ..\dashboard
   pip install -r requirements.txt
   streamlit run journal_dashboard.py
   ```

## Windows Terminal Tips

For better experience, use **Windows Terminal** instead of CMD:
- Download from Microsoft Store
- Better copy/paste
- Multiple tabs
- Better colors and fonts

Or use **PowerShell** instead of CMD:
```powershell
cd C:\path\to\journal-project\ocr
python journal_ocr.py photos/
```

## Troubleshooting HEIC Images (iPhone Default Format)

iPhones save photos as HEIC by default. To handle these:

**Option 1: Convert on iPhone**
Settings → Camera → Formats → Select "Most Compatible"
This saves as JPEG instead of HEIC.

**Option 2: Handle HEIC in Python**
```cmd
pip install pillow-heif
```

Add to `journal_ocr.py`:
```python
from pillow_heif import register_heif_opener
register_heif_opener()
```

**Option 3: Batch Convert**
Use a tool like:
- iMazing HEIC Converter (free)
- XnConvert (free, batch processing)
- Or Windows built-in Photos app (right-click → Copy → Paste as JPEG)

## Summary: Complete Windows Setup

```cmd
# 1. Install Tesseract OCR
# Download from: https://github.com/UB-Mannheim/tesseract/wiki

# 2. Install Python dependencies
cd journal-project\ocr
pip install -r requirements.txt

# 3. Test OCR on a single photo
python journal_ocr.py test_photo.jpg

# 4. Set up iCloud Photos sync or use manual transfer

# 5. Start automated processing
python auto_ocr_watcher.py "C:\Users\YourName\Pictures\Journal Entries"
```

Done! Your Windows PC will now automatically process journal photos from your iPhone.

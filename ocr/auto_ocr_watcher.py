#!/usr/bin/env python3
"""
Automatic Journal OCR Watcher
Monitors a folder for new journal photos and automatically processes them
"""

import time
import argparse
from pathlib import Path
from datetime import datetime
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from journal_ocr import JournalOCRPipeline


class JournalPhotoHandler(FileSystemEventHandler):
    """Handles new journal photo events"""
    
    def __init__(self, pipeline: JournalOCRPipeline, file_extensions=None):
        """
        Initialize handler
        
        Args:
            pipeline: JournalOCRPipeline instance
            file_extensions: Tuple of valid extensions (e.g., ('.jpg', '.png'))
        """
        self.pipeline = pipeline
        self.file_extensions = file_extensions or ('.jpg', '.jpeg', '.png', '.heic')
        self.processed_files = set()  # Track already processed files
        
    def on_created(self, event):
        """Called when a new file is created"""
        if event.is_directory:
            return
        
        file_path = Path(event.src_path)
        
        # Check if it's an image file we care about
        if file_path.suffix.lower() not in self.file_extensions:
            return
        
        # Avoid processing the same file twice
        if str(file_path) in self.processed_files:
            return
        
        # Wait a moment to ensure file is fully written
        time.sleep(2)
        
        print(f"\nNew journal photo detected: {file_path.name}")
        
        try:
            # Extract date from filename if possible (e.g., IMG_2026-01-31.jpg)
            entry_date = self._extract_date_from_filename(file_path.name)
            if not entry_date:
                # Use file creation time as fallback
                entry_date = datetime.fromtimestamp(file_path.stat().st_ctime).strftime('%Y-%m-%d')
            
            # Process the image
            metadata = self.pipeline.process_image(
                str(file_path),
                entry_date=entry_date,
                save_preprocessed=False
            )
            
            self.processed_files.add(str(file_path))
            print(f"Successfully processed! Extracted {metadata['word_count']} words")
            
        except Exception as e:
            print(f"Error processing {file_path.name}: {e}")
    
    def _extract_date_from_filename(self, filename: str) -> str | None:
        """
        Try to extract date from filename
        Supports formats like: IMG_2026-01-31.jpg, journal_2026_01_31.jpg, 20260131.jpg
        """
        import re
        
        # Pattern: YYYY-MM-DD or YYYY_MM_DD or YYYYMMDD
        patterns = [
            r'(\d{4})-(\d{2})-(\d{2})',  # 2026-01-31
            r'(\d{4})_(\d{2})_(\d{2})',  # 2026_01_31
            r'(\d{4})(\d{2})(\d{2})',    # 20260131
        ]
        
        for pattern in patterns:
            match = re.search(pattern, filename)
            if match:
                year, month, day = match.groups()
                return f"{year}-{month}-{day}"
        
        return None


def watch_folder(watch_dir: str, output_dir: str, engine: str = "tesseract"):
    """
    Start watching a folder for new journal photos
    
    Args:
        watch_dir: Directory to watch for new photos
        output_dir: Directory to save OCR output
        engine: OCR engine to use
    """
    watch_path = Path(watch_dir)
    if not watch_path.exists():
        raise FileNotFoundError(f"Watch directory does not exist: {watch_dir}")
    
    print(f"Starting journal photo watcher...")
    print(f"   Watching: {watch_path.absolute()}")
    print(f"   Output: {output_dir}")
    print(f"   OCR Engine: {engine}")
    print(f"\nAdd new journal photos to the watch folder to process them automatically.")
    print(f"   Press Ctrl+C to stop.\n")
    
    # Initialize pipeline
    pipeline = JournalOCRPipeline(engine=engine, output_dir=output_dir)
    
    # Set up file system observer
    event_handler = JournalPhotoHandler(pipeline)
    observer = Observer()
    observer.schedule(event_handler, str(watch_path), recursive=False)
    observer.start()
    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n\nStopping watcher...")
        observer.stop()
    
    observer.join()
    print("Watcher stopped.")


def main():
    parser = argparse.ArgumentParser(
        description="Automatically process new journal photos as they appear in a folder"
    )
    parser.add_argument(
        "watch_dir",
        help="Directory to watch for new journal photos (e.g., iCloud Photos folder)"
    )
    parser.add_argument(
        "-o", "--output",
        default="./ocr_output",
        help="Output directory for OCR results (default: ./ocr_output)"
    )
    parser.add_argument(
        "-e", "--engine",
        choices=["tesseract", "paddleocr"],
        default="tesseract",
        help="OCR engine to use (default: tesseract)"
    )
    
    args = parser.parse_args()
    
    watch_folder(args.watch_dir, args.output, args.engine)


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""
Journal OCR Pipeline
Converts handwritten journal photos to machine-readable text
"""

import argparse
import json
import os
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, List
import cv2
import numpy as np
from PIL import Image
import pytesseract

# Load Windows-specific configuration for Tesseract path
try:
    from config import *
except ImportError:
    pass  # Config file not needed if tesseract is in PATH

# Add HEIC support for iPhone photos
try:
    from pillow_heif import register_heif_opener
    register_heif_opener()
except ImportError:
    pass  # HEIC support not available


class ImagePreprocessor:
    """Preprocessing to improve OCR accuracy on handwritten text"""
    
    @staticmethod
    def preprocess(image_path: str, output_path: Optional[str] = None) -> np.ndarray:
        """
        Apply preprocessing steps to improve OCR accuracy
        
        Args:
            image_path: Path to input image
            output_path: Optional path to save preprocessed image
            
        Returns:
            Preprocessed image as numpy array
        """
        # Read image - use PIL first to handle HEIC and other formats
        try:
            # Try PIL first (handles HEIC, JPEG, PNG, etc.)
            pil_img = Image.open(image_path)
            # Convert PIL image to RGB if needed
            if pil_img.mode != 'RGB':
                pil_img = pil_img.convert('RGB')
            # Convert PIL to numpy array for OpenCV
            img = np.array(pil_img)
            # Convert RGB to BGR (OpenCV format)
            img = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)
        except Exception as e:
            # Fallback to OpenCV
            img = cv2.imread(image_path)
            if img is None:
                raise ValueError(f"Could not read image: {image_path}. Error: {e}")
        
        # Convert to grayscale
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        
        # Denoise
        denoised = cv2.fastNlMeansDenoising(gray, h=10)
        
        # Increase contrast using CLAHE (Contrast Limited Adaptive Histogram Equalization)
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
        contrast = clahe.apply(denoised)
        
        # Binarization - Otsu's method works well for varied lighting
        _, binary = cv2.threshold(contrast, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        
        # Deskew if needed (simple rotation correction)
        angle = ImagePreprocessor._get_skew_angle(binary)
        if abs(angle) > 0.5:  # Only correct if skew is noticeable
            binary = ImagePreprocessor._rotate_image(binary, angle)
        
        # Optional: save preprocessed image for debugging
        if output_path:
            cv2.imwrite(output_path, binary)
        
        return binary
    
    @staticmethod
    def _get_skew_angle(image: np.ndarray) -> float:
        """Detect skew angle for deskewing"""
        coords = np.column_stack(np.where(image > 0))
        if len(coords) == 0:
            return 0
        angle = cv2.minAreaRect(coords)[-1]
        if angle < -45:
            angle = 90 + angle
        return -angle
    
    @staticmethod
    def _rotate_image(image: np.ndarray, angle: float) -> np.ndarray:
        """Rotate image by given angle"""
        (h, w) = image.shape[:2]
        center = (w // 2, h // 2)
        M = cv2.getRotationMatrix2D(center, angle, 1.0)
        rotated = cv2.warpAffine(image, M, (w, h), flags=cv2.INTER_CUBIC, 
                                 borderMode=cv2.BORDER_REPLICATE)
        return rotated


class OCREngine:
    """Wrapper for different OCR backends"""
    
    def __init__(self, engine: str = "tesseract"):
        """
        Initialize OCR engine
        
        Args:
            engine: OCR backend to use ('tesseract' or 'paddleocr')
        """
        self.engine = engine
        
        if engine == "paddleocr":
            try:
                from paddleocr import PaddleOCR
                self.paddle = PaddleOCR(use_angle_cls=True, lang='en', show_log=False)
            except ImportError:
                raise ImportError("PaddleOCR not installed. Install with: pip install paddleocr")
    
    def extract_text(self, image: np.ndarray, config: str = "") -> str:
        """
        Extract text from preprocessed image
        
        Args:
            image: Preprocessed image as numpy array
            config: Additional config for Tesseract (ignored for PaddleOCR)
            
        Returns:
            Extracted text as string
        """
        if self.engine == "tesseract":
            return self._tesseract_ocr(image, config)
        elif self.engine == "paddleocr":
            return self._paddle_ocr(image)
        else:
            raise ValueError(f"Unknown OCR engine: {self.engine}")
    
    def _tesseract_ocr(self, image: np.ndarray, config: str) -> str:
        """Extract text using Tesseract"""
        # PSM 6 assumes uniform block of text (good for journal pages)
        # PSM 4 assumes single column of text
        default_config = '--psm 6 --oem 3'  # oem 3 = LSTM neural network
        final_config = config if config else default_config
        
        pil_image = Image.fromarray(image)
        text = pytesseract.image_to_string(pil_image, config=final_config)
        return text.strip()
    
    def _paddle_ocr(self, image: np.ndarray) -> str:
        """Extract text using PaddleOCR"""
        result = self.paddle.ocr(image, cls=True)
        
        if not result or not result[0]:
            return ""
        
        # Extract text from results (PaddleOCR returns bounding boxes + text)
        lines = []
        for line in result[0]:
            if line and len(line) > 1:
                text = line[1][0]  # line[1] is (text, confidence)
                lines.append(text)
        
        return '\n'.join(lines)


class JournalOCRPipeline:
    """Complete pipeline for processing journal entries"""
    
    def __init__(self, engine: str = "tesseract", output_dir: str = "./ocr_output"):
        """
        Initialize pipeline
        
        Args:
            engine: OCR backend to use
            output_dir: Directory to save OCR results
        """
        self.preprocessor = ImagePreprocessor()
        self.ocr = OCREngine(engine)
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True, parents=True)
        
        # Create subdirectories
        (self.output_dir / "text").mkdir(exist_ok=True)
        (self.output_dir / "preprocessed").mkdir(exist_ok=True)
        (self.output_dir / "metadata").mkdir(exist_ok=True)
    
    def process_image(self, image_path: str, entry_date: Optional[str] = None,
                     save_preprocessed: bool = False) -> Dict:
        """
        Process a single journal image
        
        Args:
            image_path: Path to journal image
            entry_date: Date of journal entry (YYYY-MM-DD format)
            save_preprocessed: Whether to save preprocessed images
            
        Returns:
            Dictionary with processing results
        """
        image_path = Path(image_path)
        if not image_path.exists():
            raise FileNotFoundError(f"Image not found: {image_path}")
        
        # Generate output filename
        if entry_date:
            base_name = entry_date
        else:
            base_name = image_path.stem
        
        print(f"Processing {image_path.name}...")
        
        # Preprocess
        preprocessed_path = None
        if save_preprocessed:
            preprocessed_path = self.output_dir / "preprocessed" / f"{base_name}.png"
        
        preprocessed = self.preprocessor.preprocess(
            str(image_path), 
            str(preprocessed_path) if preprocessed_path else None
        )
        
        # OCR
        text = self.ocr.extract_text(preprocessed)
        
        # Save text
        text_path = self.output_dir / "text" / f"{base_name}.txt"
        text_path.write_text(text, encoding='utf-8')
        
        # Create metadata
        metadata = {
            "original_image": str(image_path.absolute()),
            "entry_date": entry_date or image_path.stem,
            "processed_at": datetime.now().isoformat(),
            "text_file": str(text_path.absolute()),
            "word_count": len(text.split()),
            "char_count": len(text)
        }
        
        # Save metadata
        metadata_path = self.output_dir / "metadata" / f"{base_name}.json"
        with open(metadata_path, 'w', encoding='utf-8') as f:
            json.dump(metadata, f, indent=2)
        
        print(f"  Extracted {metadata['word_count']} words")
        print(f"  Saved to {text_path}")
        
        return metadata
    
    def process_batch(self, image_dir: str, pattern: str = "*.jpg",
                     save_preprocessed: bool = False) -> List[Dict]:
        """
        Process a batch of journal images
        
        Args:
            image_dir: Directory containing journal images
            pattern: Glob pattern for image files
            save_preprocessed: Whether to save preprocessed images
            
        Returns:
            List of metadata dictionaries
        """
        image_dir = Path(image_dir)
        image_files = sorted(image_dir.glob(pattern))
        
        if not image_files:
            print(f"No images found matching {pattern} in {image_dir}")
            return []
        
        print(f"Found {len(image_files)} images to process\n")
        
        results = []
        for image_path in image_files:
            try:
                metadata = self.process_image(
                    str(image_path),
                    save_preprocessed=save_preprocessed
                )
                results.append(metadata)
            except Exception as e:
                print(f"  Error processing {image_path.name}: {e}")
                continue
        
        # Save batch metadata
        batch_metadata_path = self.output_dir / "batch_metadata.json"
        with open(batch_metadata_path, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2)
        
        print(f"\nProcessed {len(results)}/{len(image_files)} images successfully")
        print(f"Batch metadata saved to {batch_metadata_path}")
        
        return results


def main():
    parser = argparse.ArgumentParser(
        description="OCR pipeline for handwritten journal entries"
    )
    parser.add_argument(
        "input",
        help="Input image file or directory containing images"
    )
    parser.add_argument(
        "-o", "--output",
        default="./ocr_output",
        help="Output directory (default: ./ocr_output)"
    )
    parser.add_argument(
        "-e", "--engine",
        choices=["tesseract", "paddleocr"],
        default="tesseract",
        help="OCR engine to use (default: tesseract)"
    )
    parser.add_argument(
        "-d", "--date",
        help="Entry date in YYYY-MM-DD format (for single file processing)"
    )
    parser.add_argument(
        "-p", "--pattern",
        default="*.jpg",
        help="File pattern for batch processing (default: *.jpg)"
    )
    parser.add_argument(
        "--save-preprocessed",
        action="store_true",
        help="Save preprocessed images for debugging"
    )
    
    args = parser.parse_args()
    
    # Initialize pipeline
    pipeline = JournalOCRPipeline(engine=args.engine, output_dir=args.output)
    
    # Process input
    input_path = Path(args.input)
    
    if input_path.is_file():
        # Single file
        pipeline.process_image(
            str(input_path),
            entry_date=args.date,
            save_preprocessed=args.save_preprocessed
        )
    elif input_path.is_dir():
        # Batch processing
        pipeline.process_batch(
            str(input_path),
            pattern=args.pattern,
            save_preprocessed=args.save_preprocessed
        )
    else:
        print(f"Error: {input_path} is not a valid file or directory")
        return 1
    
    return 0


if __name__ == "__main__":
    exit(main())

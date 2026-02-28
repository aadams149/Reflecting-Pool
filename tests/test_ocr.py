"""Tests for OCR pipeline (ocr/journal_ocr.py)."""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "ocr"))

import pytest
import numpy as np

from journal_ocr import ImagePreprocessor, OCREngine, JournalOCRPipeline


class TestImagePreprocessor:
    def test_get_skew_angle_blank(self):
        blank = np.zeros((100, 100), dtype=np.uint8)
        angle = ImagePreprocessor._get_skew_angle(blank)
        assert angle == 0

    def test_get_skew_angle_with_content(self):
        img = np.zeros((100, 100), dtype=np.uint8)
        img[40:60, 10:90] = 255  # horizontal white bar
        angle = ImagePreprocessor._get_skew_angle(img)
        assert isinstance(angle, float)

    def test_rotate_image_preserves_shape(self):
        img = np.zeros((100, 200), dtype=np.uint8)
        rotated = ImagePreprocessor._rotate_image(img, 5.0)
        assert rotated.shape == img.shape

    def test_rotate_image_zero_angle(self):
        img = np.ones((50, 50), dtype=np.uint8) * 128
        rotated = ImagePreprocessor._rotate_image(img, 0.0)
        assert rotated.shape == img.shape


class TestOCREngine:
    def test_init_tesseract(self):
        engine = OCREngine(engine="tesseract")
        assert engine.engine == "tesseract"

    def test_init_invalid_engine(self):
        with pytest.raises(ValueError):
            engine = OCREngine(engine="invalid_engine")
            engine.extract_text(np.zeros((10, 10), dtype=np.uint8))


class TestPipeline:
    def test_init_creates_directories(self, tmp_path):
        out = tmp_path / "output"
        JournalOCRPipeline(output_dir=str(out))
        assert (out / "text").is_dir()
        assert (out / "preprocessed").is_dir()
        assert (out / "metadata").is_dir()

    def test_process_missing_image(self, tmp_path):
        pipeline = JournalOCRPipeline(output_dir=str(tmp_path / "out"))
        with pytest.raises(FileNotFoundError):
            pipeline.process_image(str(tmp_path / "nonexistent.jpg"))

    def test_process_batch_no_images(self, tmp_path):
        pipeline = JournalOCRPipeline(output_dir=str(tmp_path / "out"))
        empty_dir = tmp_path / "empty"
        empty_dir.mkdir()
        results = pipeline.process_batch(str(empty_dir))
        assert results == []

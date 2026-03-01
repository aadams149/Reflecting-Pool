"""Tests for the JournalRAG system (rag/journal_rag.py)."""
import sys
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "rag"))

import pytest
from journal_rag import JournalRAG


@pytest.fixture
def rag(tmp_path):
    """Create a JournalRAG instance with a temporary database."""
    return JournalRAG(db_path=str(tmp_path / "test_db"))


class TestChunkText:
    """Tests for the _chunk_text method."""

    def test_short_text_single_chunk(self, rag):
        chunks = rag._chunk_text("This is a short text.", chunk_size=500, overlap=50)
        assert len(chunks) == 1
        assert chunks[0] == "This is a short text."

    def test_long_text_multiple_chunks(self, rag):
        text = "word " * 200  # 1000 chars
        chunks = rag._chunk_text(text, chunk_size=100, overlap=10)
        assert len(chunks) > 1

    def test_empty_text(self, rag):
        chunks = rag._chunk_text("", chunk_size=500, overlap=50)
        assert len(chunks) == 1
        assert chunks[0] == ""

    def test_exact_chunk_size(self, rag):
        text = "x" * 500
        chunks = rag._chunk_text(text, chunk_size=500, overlap=50)
        assert len(chunks) == 1


class TestEmptyDatabase:
    """Tests for operations on an empty database."""

    def test_search_empty(self, rag):
        results = rag.search("anything")
        assert results == []

    def test_get_all_dates_empty(self, rag):
        assert rag.get_all_dates() == []

    def test_list_all_entries_empty(self, rag):
        assert rag.list_all_entries() == []

    def test_get_stats_empty(self, rag):
        stats = rag.get_stats()
        assert stats["total_entries"] == 0
        assert stats["total_chunks"] == 0
        assert stats["date_range"]["first"] is None

    def test_delete_nonexistent_date(self, rag):
        assert rag.delete_entry_by_date("2025-01-01") == 0

    def test_clear_empty(self, rag):
        assert rag.clear_all_entries() == 0


class TestIngest:
    """Tests for ingestion functionality."""

    def test_ingest_missing_dir(self, rag, tmp_path):
        with pytest.raises(FileNotFoundError):
            rag.ingest_from_ocr(str(tmp_path / "nonexistent"))

    def test_ingest_valid_entries(self, rag, tmp_path):
        text_dir = tmp_path / "ocr_out" / "text"
        meta_dir = tmp_path / "ocr_out" / "metadata"
        text_dir.mkdir(parents=True)
        meta_dir.mkdir(parents=True)
        (text_dir / "2025-01-15.txt").write_text(
            "Today was a good day.", encoding="utf-8"
        )
        (meta_dir / "2025-01-15.json").write_text(
            json.dumps({
                "entry_date": "2025-01-15",
                "word_count": 5,
                "source_file": "test.jpg",
            }),
            encoding="utf-8",
        )
        count = rag.ingest_from_ocr(str(tmp_path / "ocr_out"))
        assert count == 1
        assert rag.collection.count() >= 1

    def test_search_after_ingest(self, rag, tmp_path):
        text_dir = tmp_path / "ocr_out" / "text"
        meta_dir = tmp_path / "ocr_out" / "metadata"
        text_dir.mkdir(parents=True)
        meta_dir.mkdir(parents=True)
        (text_dir / "2025-02-01.txt").write_text(
            "I went hiking in the mountains today and saw beautiful scenery.",
            encoding="utf-8",
        )
        (meta_dir / "2025-02-01.json").write_text(
            json.dumps({
                "entry_date": "2025-02-01",
                "word_count": 11,
                "source_file": "t.jpg",
            }),
            encoding="utf-8",
        )
        rag.ingest_from_ocr(str(tmp_path / "ocr_out"))
        results = rag.search("hiking mountains")
        assert len(results) >= 1

"""
Tests for document parser module.
"""

import os
import sys
import pytest
from pathlib import Path

# Ensure project root is on the path
sys.path.insert(0, str(Path(__file__).parent.parent))

from document_parser import DocumentParser


@pytest.fixture
def parser():
    return DocumentParser()


@pytest.fixture
def sample_sow_path():
    return str(Path(__file__).parent / "sample_sow.txt")


@pytest.fixture
def sample_sow_text(sample_sow_path):
    with open(sample_sow_path, "r") as f:
        return f.read()


class _FakeUploadedFile:
    """Mimics a Streamlit UploadedFile for testing."""

    def __init__(self, path: str):
        self.name = os.path.basename(path)
        self._data = open(path, "rb").read()
        self._pos = 0

    def read(self, n=-1):
        if n == -1:
            data = self._data[self._pos:]
            self._pos = len(self._data)
        else:
            data = self._data[self._pos:self._pos + n]
            self._pos += n
        return data

    def seek(self, pos):
        self._pos = pos

    @property
    def type(self):
        return "text/plain"

    @property
    def size(self):
        return len(self._data)


# --- Parsing Tests ---

class TestDocumentParser:

    def test_parse_txt_file(self, parser, sample_sow_path):
        """Test that a .txt file can be parsed successfully."""
        fake_file = _FakeUploadedFile(sample_sow_path)
        result = parser.parse_document(fake_file)

        assert "raw_text" in result
        assert "sections" in result
        assert "formatting" in result
        assert result["word_count"] > 0
        assert result["paragraph_count"] > 0

    def test_extracted_text_contains_content(self, parser, sample_sow_path):
        """Test that extracted text contains expected content."""
        fake_file = _FakeUploadedFile(sample_sow_path)
        result = parser.parse_document(fake_file)

        text = result["raw_text"]
        assert "Enterprise Data Analytics Platform" in text
        assert "SCOPE OF WORK" in text
        assert "DELIVERABLES" in text

    def test_sections_detected(self, parser, sample_sow_path):
        """Test that sections are detected from the document."""
        fake_file = _FakeUploadedFile(sample_sow_path)
        result = parser.parse_document(fake_file)

        sections = result["sections"]
        assert isinstance(sections, dict)
        assert len(sections) > 0

    def test_formatting_analysis(self, parser, sample_sow_path):
        """Test that formatting is analysed."""
        fake_file = _FakeUploadedFile(sample_sow_path)
        result = parser.parse_document(fake_file)

        formatting = result["formatting"]
        assert "has_bullet_points" in formatting
        assert "has_numbered_lists" in formatting
        assert formatting["has_bullet_points"] is True  # Our sample has bullet points

    def test_word_count_reasonable(self, parser, sample_sow_path):
        """Test that word count is reasonable for the sample document."""
        fake_file = _FakeUploadedFile(sample_sow_path)
        result = parser.parse_document(fake_file)

        assert result["word_count"] > 50
        assert result["word_count"] < 10000


class TestEdgeCases:

    def test_empty_text_raises(self, parser, tmp_path):
        """Test that an empty file raises an exception."""
        empty_file = tmp_path / "empty.txt"
        empty_file.write_text("")

        fake_file = _FakeUploadedFile(str(empty_file))
        with pytest.raises(Exception):
            parser.parse_document(fake_file)

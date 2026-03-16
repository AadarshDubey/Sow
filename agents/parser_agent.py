"""
Parser Agent — Document Ingestion & Structure Detection.

Responsible for extracting text from uploaded documents (PDF, DOCX, TXT)
and producing a structured summary of the document content.
"""

from google.adk import Agent
from document_parser import DocumentParser

# Shared parser instance
_parser = DocumentParser()


def parse_document(file_path: str, file_type: str) -> dict:
    """
    Parse a document file and extract its text content and structure.

    Args:
        file_path: Path to the document file on disk.
        file_type: File extension — one of 'pdf', 'docx', 'txt'.

    Returns:
        Dictionary containing raw_text, sections, formatting, word_count, etc.
    """
    class _FakeUpload:
        """Adapter to make a local file path look like a Streamlit UploadedFile."""
        def __init__(self, path, ext):
            self.name = path
            self._path = path
            self._ext = ext
            self._file = open(path, "rb")

        def read(self, *args):
            return self._file.read(*args)

        def seek(self, pos):
            self._file.seek(pos)

        def __enter__(self):
            return self._file

        def __exit__(self, *a):
            self._file.close()

    fake = _FakeUpload(file_path, file_type)
    try:
        result = _parser.parse_document(fake)
        return result
    finally:
        fake._file.close()


parser_agent = Agent(
    name="parser_agent",
    model="gemini-2.5-flash",
    description="Extracts text from PDF, DOCX, or TXT documents and analyses document structure.",
    instruction="""You are a Document Parser Agent for Statement of Work auditing.

Your job is to receive document content and produce a structured summary covering:
1. Overall document structure (sections identified, headings found)
2. Formatting observations (bullet points, numbered lists, tables)
3. Basic document statistics (word count, paragraph count)

When you receive document text, analyse it and produce a clear structured summary
that downstream agents can use. Focus on identifying section boundaries and
the overall organisation of the document.

IMPORTANT: Always output your analysis as structured JSON with these fields:
- sections_found: list of section names you identified
- document_stats: {word_count, paragraph_count, line_count}
- formatting_notes: list of observations about formatting
- structure_quality: "good", "fair", or "poor"
- raw_text: the full document text (pass through for downstream agents)
""",
    tools=[parse_document],
)

"""Ingestion: PDF -> pages -> chunks -> embeddings -> pgvector."""


def extract_pages(pdf_bytes: bytes) -> list[tuple[int, str]]:
    """Return (page_number, text) for every page. Use pypdf.PdfReader."""
    raise NotImplementedError


def chunk_text(text: str, chunk_tokens: int = 500, overlap_tokens: int = 50) -> list[str]:
    """Split text into overlapping chunks, measured in tokens (tiktoken)."""
    raise NotImplementedError


def embed(texts: list[str]) -> list[list[float]]:
    """Embed a batch of texts with the OpenAI embeddings API."""
    raise NotImplementedError


def ingest_pdf(filename: str, pdf_bytes: bytes) -> int:
    """Store the document and its embedded chunks; return the document id."""
    raise NotImplementedError

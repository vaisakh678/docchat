"""Ingestion: PDF -> pages -> chunks -> embeddings -> pgvector."""

import io

import numpy as np
import tiktoken
from openai import OpenAI
from pypdf import PdfReader

from app.config import settings
from app.db import get_conn

client = OpenAI(api_key=settings.openai_api_key)
encoding = tiktoken.get_encoding("cl100k_base")

EMBED_BATCH_SIZE = 100


def extract_pages(pdf_bytes: bytes) -> list[tuple[int, str]]:
    """Return (page_number, text) for every page that has a text layer."""
    reader = PdfReader(io.BytesIO(pdf_bytes))
    pages = []
    for number, page in enumerate(reader.pages, start=1):
        text = (page.extract_text() or "").strip()
        if text:  # scanned pages have no text layer and would need OCR
            pages.append((number, text))
    return pages


def chunk_text(text: str, chunk_tokens: int = 500, overlap_tokens: int = 50) -> list[str]:
    """Split text into overlapping chunks, measured in tokens."""
    tokens = encoding.encode(text)
    step = chunk_tokens - overlap_tokens
    chunks = []
    for start in range(0, len(tokens), step):
        chunks.append(encoding.decode(tokens[start : start + chunk_tokens]))
        if start + chunk_tokens >= len(tokens):
            break
    return chunks


def embed(texts: list[str]) -> list[list[float]]:
    """Embed texts with the OpenAI embeddings API, in batches."""
    vectors = []
    for i in range(0, len(texts), EMBED_BATCH_SIZE):
        response = client.embeddings.create(
            model=settings.embedding_model, input=texts[i : i + EMBED_BATCH_SIZE]
        )
        vectors.extend(item.embedding for item in response.data)
    return vectors


def ingest_pdf(filename: str, pdf_bytes: bytes) -> int:
    """Store the document and its embedded chunks; return the document id."""
    chunks = [
        (page, chunk)
        for page, text in extract_pages(pdf_bytes)
        for chunk in chunk_text(text)
    ]
    vectors = embed([chunk for _, chunk in chunks])

    with get_conn() as conn:
        document_id = conn.execute(
            "INSERT INTO documents (filename) VALUES (%s) RETURNING id", (filename,)
        ).fetchone()[0]
        with conn.cursor() as cur:
            cur.executemany(
                "INSERT INTO chunks (document_id, page, content, embedding) VALUES (%s, %s, %s, %s)",
                [
                    (document_id, page, chunk, np.array(vector))
                    for (page, chunk), vector in zip(chunks, vectors)
                ],
            )
    return document_id

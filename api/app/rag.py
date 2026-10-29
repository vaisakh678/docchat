"""Question answering: embed question -> retrieve top-k chunks -> grounded answer."""

import numpy as np
from openai import OpenAI

from app.config import settings
from app.db import get_conn
from app.ingest import embed

client = OpenAI(api_key=settings.openai_api_key)

SYSTEM_PROMPT = """You answer questions using only the provided context.
Cite sources as [filename p.<page>] after each claim.
If the context does not contain the answer, say you don't know."""


def retrieve(question: str, k: int = 5) -> list[dict]:
    """Return the k chunks closest to the question by cosine distance (<=> in pgvector)."""
    query_vector = np.array(embed([question])[0])
    with get_conn() as conn:
        rows = conn.execute(
            """
            SELECT d.filename, c.page, c.content, 1 - (c.embedding <=> %s) AS similarity
            FROM chunks c
            JOIN documents d ON d.id = c.document_id
            ORDER BY c.embedding <=> %s
            LIMIT %s
            """,
            (query_vector, query_vector, k),
        ).fetchall()
    return [
        {"filename": filename, "page": page, "content": content, "similarity": round(similarity, 3)}
        for filename, page, content, similarity in rows
    ]


def build_context(chunks: list[dict]) -> str:
    return "\n\n".join(
        f"[{c['filename']} p.{c['page']}]\n{c['content']}" for c in chunks
    )


def answer(question: str, k: int = 5) -> dict:
    """Build the prompt from retrieved chunks and return {"answer", "sources"}."""
    chunks = retrieve(question, k)
    if not chunks:
        return {"answer": "No documents have been uploaded yet.", "sources": []}

    response = client.chat.completions.create(
        model=settings.chat_model,
        temperature=0,  # factual Q&A: we want the most likely answer, not creativity
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": f"Context:\n{build_context(chunks)}\n\nQuestion: {question}"},
        ],
    )
    return {
        "answer": response.choices[0].message.content,
        "sources": [
            {"filename": c["filename"], "page": c["page"], "similarity": c["similarity"]}
            for c in chunks
        ],
    }

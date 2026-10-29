from fastapi import FastAPI, UploadFile
from pydantic import BaseModel

from app import ingest, rag
from app.db import get_conn

app = FastAPI(title="DocChat")


class AskRequest(BaseModel):
    question: str
    k: int = 5


@app.get("/health")
def health():
    return {"ok": True}


@app.get("/documents")
def list_documents():
    with get_conn() as conn:
        rows = conn.execute(
            """
            SELECT d.id, d.filename, d.created_at, count(c.id) AS chunks
            FROM documents d
            LEFT JOIN chunks c ON c.document_id = d.id
            GROUP BY d.id
            ORDER BY d.created_at DESC
            """
        ).fetchall()
    return [
        {"id": id, "filename": filename, "created_at": created_at, "chunks": chunks}
        for id, filename, created_at, chunks in rows
    ]


@app.post("/documents")
async def upload_document(file: UploadFile):
    document_id = ingest.ingest_pdf(file.filename, await file.read())
    return {"document_id": document_id}


@app.post("/ask")
def ask(body: AskRequest):
    return rag.answer(body.question, body.k)

from fastapi import FastAPI, UploadFile
from pydantic import BaseModel

from app import ingest, rag

app = FastAPI(title="DocChat")


class AskRequest(BaseModel):
    question: str
    k: int = 5


@app.get("/health")
def health():
    return {"ok": True}


@app.post("/documents")
async def upload_document(file: UploadFile):
    document_id = ingest.ingest_pdf(file.filename, await file.read())
    return {"document_id": document_id}


@app.post("/ask")
def ask(body: AskRequest):
    return rag.answer(body.question, body.k)

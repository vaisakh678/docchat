# DocChat

Chat with your PDFs. Answers are grounded in the uploaded documents and cite the page they came from.

Built from scratch in Python (no LangChain) to keep every step of the RAG pipeline explicit.

## How it works

```
Upload:  PDF -> pages (pypdf) -> token chunks w/ overlap (tiktoken) -> embeddings (OpenAI) -> pgvector
Ask:     question -> embedding -> top-k cosine search (HNSW) -> grounded prompt -> answer + citations
```

## Stack

FastAPI · PostgreSQL + pgvector · OpenAI (embeddings + chat) · pypdf · tiktoken · Docker Compose

## Run locally

```bash
docker compose up -d                 # Postgres + pgvector on :5433
python3.13 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env                 # add your OPENAI_API_KEY
uvicorn app.main:app --reload
```

Open http://localhost:8000/docs to upload a PDF and ask questions.

## API

| Method | Path | Body |
|---|---|---|
| `POST` | `/documents` | multipart `file` (PDF) |
| `POST` | `/ask` | `{"question": "...", "k": 5}` |

## Design choices

- _TODO: chunk size / overlap and why_
- _TODO: why pgvector_
- _TODO: how hallucination is reduced_

# DocChat

Chat with your PDFs. Answers are grounded in the uploaded documents and cite the page they came from.

Built from scratch in Python (no LangChain) to keep every step of the RAG pipeline explicit.

## How it works

```
Upload:  PDF -> pages (pypdf) -> token chunks w/ overlap (tiktoken) -> embeddings (OpenAI) -> pgvector
Ask:     question -> embedding -> top-k cosine search (HNSW) -> grounded prompt -> answer + citations
```

## Layout

```
api/         FastAPI backend: app/ (ingest, rag, routes), eval/, db/schema.sql
web/         React + Vite + TypeScript UI
```

## Stack

FastAPI · PostgreSQL + pgvector · OpenAI (embeddings + chat) · pypdf · tiktoken · Docker Compose · React + Vite (TypeScript)

## Run locally

```bash
docker compose up -d                 # Postgres + pgvector on :5433
cd api
python3.13 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env                 # add your OPENAI_API_KEY
uvicorn app.main:app --reload
```

Open http://localhost:8000/docs to upload a PDF and ask questions.

## Frontend

React + Vite UI (start the API first; `/api` is proxied to FastAPI on :8000):

```bash
cd web && pnpm install && pnpm dev   # http://localhost:5173
```

## API

| Method | Path | Body |
|---|---|---|
| `GET` | `/documents` | — (lists documents with chunk counts) |
| `POST` | `/documents` | multipart `file` (PDF) |
| `POST` | `/ask` | `{"question": "...", "k": 5}` |

## Evaluate retrieval

Add questions with the page that holds the answer to `api/eval/questions.json`:

```json
[{"question": "What is the refund window?", "filename": "policy.pdf", "page": 3}]
```

```bash
cd api && python -m eval.run_eval --k 5      # prints hit rate@k and MRR
```

## Design choices

- **Token-based chunks, 500 tokens with 50 overlap.** Models count tokens, so token chunks are predictable. Overlap keeps a sentence that crosses a boundary whole in at least one chunk. Smaller chunks retrieve more precisely but lose context; larger ones keep context but add noise and cost.
- **Chunks keep their page number**, so every answer can cite `[file p.N]`.
- **pgvector instead of a hosted vector DB.** Embeddings live next to the relational data in one Postgres, with joins, transactions and no extra service. An HNSW index keeps cosine search fast as the table grows.
- **Grounded prompt + `temperature=0`** to reduce hallucination: the model must answer only from the retrieved context, cite sources, and say "I don't know" otherwise.
- **Batched embeddings** (100 texts per request) to cut round trips during ingestion.
- **No LangChain**, so every step of the pipeline is explicit and easy to change.
- **Schema as an init script** (`api/db/schema.sql`) since it is two tables; a growing schema would move to Alembic migrations.

## Next steps

- Hybrid search (Postgres full-text + vector) and a cross-encoder re-ranker
- Streaming answers over SSE
- OCR for scanned PDFs (pages without a text layer are skipped today)

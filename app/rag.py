"""Question answering: embed question -> retrieve top-k chunks -> grounded answer."""

SYSTEM_PROMPT = """You answer questions using only the provided context.
Cite sources as [filename p.<page>] after each claim.
If the context does not contain the answer, say you don't know."""


def retrieve(question: str, k: int = 5) -> list[dict]:
    """Return the k chunks closest to the question by cosine distance (<=> in pgvector)."""
    raise NotImplementedError


def answer(question: str, k: int = 5) -> dict:
    """Build the prompt from retrieved chunks and return {"answer", "sources"}."""
    raise NotImplementedError

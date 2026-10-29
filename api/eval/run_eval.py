"""Retrieval evaluation: for each question, is the page that holds the answer in the top-k?

api/eval/questions.json holds entries like:
    {"question": "What is the refund window?", "filename": "policy.pdf", "page": 3}

Run (from api/): python -m eval.run_eval --k 5
"""

import argparse
import json
from pathlib import Path

from app.rag import retrieve

QUESTIONS = Path(__file__).parent / "questions.json"


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--k", type=int, default=5)
    args = parser.parse_args()

    cases = json.loads(QUESTIONS.read_text())
    if not cases:
        print("eval/questions.json is empty; add questions with their expected filename and page.")
        return

    hits, reciprocal_ranks = 0, 0.0
    for case in cases:
        results = retrieve(case["question"], args.k)
        ranks = [
            rank
            for rank, r in enumerate(results, start=1)
            if r["filename"] == case["filename"] and r["page"] == case["page"]
        ]
        if ranks:
            hits += 1
            reciprocal_ranks += 1 / ranks[0]
        print(f"{'HIT ' if ranks else 'MISS'}  {case['question']}")

    print(f"\nhit rate @{args.k}: {hits / len(cases):.0%}   MRR: {reciprocal_ranks / len(cases):.2f}")


if __name__ == "__main__":
    main()

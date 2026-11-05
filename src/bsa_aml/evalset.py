"""Hand-written test set: load, resolve gold -> chunk ids, validate.

eval/test_questions.jsonl, one JSON per line:
  id, question, type, gold: [{"doc": <eCFR "§ 1020.320" | doc_id substring>, "must": [keywords]}]
A chunk is gold if it belongs to the gold doc/section AND contains every `must` keyword
(case-insensitive). `python -m bsa_aml.evalset` reports questions with no resolvable gold chunk.
"""

from __future__ import annotations

import json
from pathlib import Path

from .retrieval import load_chunks

QUESTIONS = Path(__file__).resolve().parents[2] / "eval" / "test_questions.jsonl"


def load_questions() -> list[dict]:
    return [json.loads(x) for x in QUESTIONS.read_text(encoding="utf-8").splitlines() if x.strip()]


def _in_doc(c: dict, doc: str) -> bool:
    if doc.startswith("§"):
        return c["source_type"] == "ecfr" and c["section_path"][-1].startswith(doc + " ")
    return doc in c["doc_id"]


def gold_chunks(q: dict, chunks: list[dict]) -> set[int]:
    out = set()
    for g in q["gold"]:
        for i, c in enumerate(chunks):
            t = c["body"].lower()
            if _in_doc(c, g["doc"]) and all(k.lower() in t for k in g.get("must", [])):
                out.add(i)
    return out


def main() -> None:
    chunks, qs = load_chunks(), load_questions()
    bad = 0
    for q in qs:
        n = len(gold_chunks(q, chunks))
        if n == 0:
            bad += 1
        print(f"{q['id']} gold_chunks={n:3d} {'NO GOLD ' if n == 0 else ''}{q['question'][:60]}")
    print(f"{len(qs)} questions, {bad} unresolved")


if __name__ == "__main__":
    main()

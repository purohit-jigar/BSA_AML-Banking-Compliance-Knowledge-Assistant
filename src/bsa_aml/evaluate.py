"""Retrieval evaluation: recall@k and MRR on the hand-written test set.

Usage: python -m bsa_aml.evaluate [--index base] [--modes dense,bm25,hybrid] [--label baseline]

A question is a hit at k if ANY of its gold chunks is in the top-k (gold = chunks resolved by
evalset.gold_chunks). Results are written to eval/results/<label>-<index>.json with the question
file's sha256 and whether every question is frozen, so a run on a still-draft set is visibly not a
baseline.
"""

from __future__ import annotations

import argparse
import collections
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

from .evalset import QUESTIONS, gold_chunks, load_questions
from .retrieval import INDEX, Retriever, load_chunks

KS = (1, 5, 10)
RESULTS = Path(__file__).resolve().parents[2] / "eval" / "results"


def evaluate(retriever: Retriever, questions: list[dict], mode: str) -> dict:
    chunks = retriever.chunks
    rows = []
    for q in questions:
        gold = gold_chunks(q, chunks)
        if not gold:
            raise SystemExit(f"{q['id']} has no resolvable gold chunk; fix it (python -m bsa_aml.evalset)")
        ids = {"dense": retriever.dense, "bm25": retriever.sparse, "hybrid": retriever.hybrid}[mode](
            q["question"], max(KS)
        )
        rank = next((r for r, i in enumerate(ids, 1) if i in gold), None)
        rows.append({"id": q["id"], "type": q["type"], "rank": rank, "n_gold": len(gold)})

    def agg(rs: list[dict]) -> dict:
        n = len(rs)
        out = {f"recall@{k}": round(sum(1 for r in rs if r["rank"] and r["rank"] <= k) / n, 4) for k in KS}
        out["mrr@10"] = round(sum(1 / r["rank"] for r in rs if r["rank"]) / n, 4)
        out["n"] = n
        return out

    by_type = collections.defaultdict(list)
    for r in rows:
        by_type[r["type"]].append(r)
    return {
        "overall": agg(rows),
        "by_type": {t: agg(rs) for t, rs in sorted(by_type.items())},
        "misses_at_5": [r["id"] for r in rows if not r["rank"] or r["rank"] > 5],
        "per_question": rows,
    }


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--index", default="base")
    ap.add_argument("--modes", default="dense,bm25,hybrid")
    ap.add_argument("--label", default="draft")
    a = ap.parse_args()

    questions = load_questions()
    frozen = all(q.get("status") == "frozen" for q in questions)
    retriever = Retriever(a.index, load_chunks())
    result = {
        "label": a.label,
        "index": a.index,
        "embedding_model": json.loads((INDEX / a.index / "meta.json").read_text())["model"],
        "created": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "questions_sha256": hashlib.sha256(QUESTIONS.read_bytes()).hexdigest(),
        "n_questions": len(questions),
        "questions_frozen": frozen,
        "modes": {m: evaluate(retriever, questions, m) for m in a.modes.split(",")},
    }
    RESULTS.mkdir(parents=True, exist_ok=True)
    out = RESULTS / f"{a.label}-{a.index}.json"
    out.write_text(json.dumps(result, indent=2), encoding="utf-8")

    print(f"index={a.index} questions={len(questions)} frozen={frozen}")
    print(f"{'mode':8} " + " ".join(f"R@{k:<3}" for k in KS) + "  MRR@10")
    for m, r in result["modes"].items():
        o = r["overall"]
        print(f"{m:8} " + " ".join(f"{o[f'recall@{k}']:.2f} " for k in KS) + f"  {o['mrr@10']:.3f}")
    if not frozen:
        print("WARNING: question set not frozen; these numbers are NOT the baseline.")
    print("wrote", out)


if __name__ == "__main__":
    main()

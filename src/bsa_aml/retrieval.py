"""Baseline retrieval: dense (FAISS) + BM25 + hybrid (RRF).

Build:  python -m bsa_aml.retrieval build [--model BAAI/bge-small-en-v1.5] [--name base]
Query:  python -m bsa_aml.retrieval query "what triggers a SAR filing?" [--mode hybrid]
Index dir: data/index/<name>/ (chunks order = chunks.jsonl order).
"""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

import faiss
import numpy as np

ROOT = Path(__file__).resolve().parents[2]
CHUNKS = ROOT / "data" / "processed" / "chunks.jsonl"
INDEX = ROOT / "data" / "index"
DEFAULT_MODEL = "BAAI/bge-small-en-v1.5"
QUERY_PREFIX = "Represent this sentence for searching relevant passages: "  # bge query instruction
RRF_K = 60


def load_chunks() -> list[dict]:
    return [json.loads(x) for x in CHUNKS.read_text(encoding="utf-8").splitlines()]


def tokenize(text: str) -> list[str]:
    return re.findall(r"[a-z0-9§]+(?:\.[0-9]+)*", text.lower())


def build(model_name: str = DEFAULT_MODEL, name: str = "base", batch: int = 64) -> None:
    from sentence_transformers import SentenceTransformer

    chunks = load_chunks()
    model = SentenceTransformer(model_name)
    model.max_seq_length = 512
    emb = model.encode(
        [c["text"] for c in chunks], batch_size=batch, normalize_embeddings=True,
        show_progress_bar=True,
    ).astype("float32")
    index = faiss.IndexFlatIP(emb.shape[1])  # exact search; 5k vectors needs nothing fancier
    index.add(emb)
    out = INDEX / name
    out.mkdir(parents=True, exist_ok=True)
    faiss.write_index(index, str(out / "faiss.index"))
    (out / "meta.json").write_text(
        json.dumps({"model": model_name, "n": len(chunks), "dim": emb.shape[1]}), encoding="utf-8"
    )
    print(f"built {out} ({len(chunks)} chunks, dim {emb.shape[1]})")


class Retriever:
    def __init__(self, name: str = "base", chunks: list[dict] | None = None):
        from rank_bm25 import BM25Okapi
        from sentence_transformers import SentenceTransformer

        d = INDEX / name
        meta = json.loads((d / "meta.json").read_text())
        self.chunks = chunks or load_chunks()
        assert meta["n"] == len(self.chunks), "index is stale; rebuild after re-ingesting"
        self.index = faiss.read_index(str(d / "faiss.index"))
        self.model = SentenceTransformer(meta["model"])
        self.bm25 = BM25Okapi([tokenize(c["text"]) for c in self.chunks])

    def dense(self, q: str, k: int = 50) -> list[int]:
        v = self.model.encode([QUERY_PREFIX + q], normalize_embeddings=True).astype("float32")
        return self.index.search(v, k)[1][0].tolist()

    def sparse(self, q: str, k: int = 50) -> list[int]:
        s = self.bm25.get_scores(tokenize(q))
        return np.argsort(-s)[:k].tolist()

    def hybrid(self, q: str, k: int = 50) -> list[int]:
        score: dict[int, float] = {}
        for ranking in (self.dense(q, k), self.sparse(q, k)):
            for r, i in enumerate(ranking):
                score[i] = score.get(i, 0.0) + 1.0 / (RRF_K + r + 1)
        return sorted(score, key=score.get, reverse=True)[:k]

    def search(self, q: str, k: int = 5, mode: str = "hybrid") -> list[dict]:
        ids = getattr(self, {"dense": "dense", "bm25": "sparse", "hybrid": "hybrid"}[mode])(q, k)
        return [self.chunks[i] for i in ids[:k]]


def main() -> None:
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    b = sub.add_parser("build")
    b.add_argument("--model", default=DEFAULT_MODEL)
    b.add_argument("--name", default="base")
    q = sub.add_parser("query")
    q.add_argument("text")
    q.add_argument("--name", default="base")
    q.add_argument("--mode", default="hybrid", choices=["dense", "bm25", "hybrid"])
    q.add_argument("-k", type=int, default=5)
    a = ap.parse_args()
    if a.cmd == "build":
        build(a.model, a.name)
        return
    for c in Retriever(a.name).search(a.text, a.k, a.mode):
        print(f"- {c['citation']}\n  {c['body'][:200].replace(chr(10), ' ')}")


if __name__ == "__main__":
    main()

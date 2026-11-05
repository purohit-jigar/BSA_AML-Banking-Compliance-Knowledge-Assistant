"""Synthetic question-passage pairs for embedder fine-tuning.

Pipeline (each step resumable, outputs under data/pairs/):
  plan      offline: held-out split, per-source sample, prompt + token estimate (no AWS call)
  generate  one question per sampled chunk with --gen-model          -> raw.jsonl
  judge     score each pair with a DIFFERENT --judge-model            -> judged.jsonl
  filter    keep score >= threshold, re-apply the held-out split      -> pairs.jsonl
  handcheck write 50 random kept pairs to review by hand              -> handcheck.md

Split rule: a chunk is held out if its section (doc_id + first two heading levels) contains any
chunk that is gold for a test question. Held-out chunks never become training pairs. `filter`
recomputes the split from the *current* test set, so editing gold after generating cannot leak.

Usage: python -m bsa_aml.pairs plan [--n 1500]
       python -m bsa_aml.pairs generate --gen-model <bedrock model id> [--limit 20]
"""

from __future__ import annotations

import argparse
import collections
import json
import random
import re
from pathlib import Path

from .evalset import gold_chunks, load_questions
from .retrieval import load_chunks

ROOT = Path(__file__).resolve().parents[2]
PAIRS = ROOT / "data" / "pairs"
REGION = "us-east-1"
SOURCES = ("ffiec", "ecfr", "fincen")
MIN_QUESTION_WORDS = 5


# ---- split + sampling (offline) -------------------------------------------------------------


def section_key(c: dict) -> tuple:
    return (c["doc_id"], tuple(c["section_path"][:2]))


def heldout_sections(chunks: list[dict], questions: list[dict]) -> set[tuple]:
    gold: set[int] = set()
    for q in questions:
        gold |= gold_chunks(q, chunks)
    return {section_key(chunks[i]) for i in gold}


def eligible(chunks: list[dict], questions: list[dict]) -> list[int]:
    held = heldout_sections(chunks, questions)
    return [i for i, c in enumerate(chunks) if section_key(c) not in held]


def sample(chunks: list[dict], idxs: list[int], n: int, seed: int = 0) -> list[int]:
    """n chunks, split evenly across sources; a source with too few chunks gives its slack to the
    others. Order is shuffled and reproducible."""
    rng = random.Random(seed)
    pools = {s: [i for i in idxs if chunks[i]["source_type"] == s] for s in SOURCES}
    for p in pools.values():
        rng.shuffle(p)
    quota = dict.fromkeys(SOURCES, 0)
    left = min(n, sum(len(p) for p in pools.values()))
    open_ = [s for s in SOURCES if pools[s]]
    while left and open_:
        share = max(left // len(open_), 1)
        for s in list(open_):
            take = min(share, len(pools[s]) - quota[s], left)
            quota[s] += take
            left -= take
            if quota[s] == len(pools[s]):
                open_.remove(s)
            if not left:
                break
    out = [i for s in SOURCES for i in pools[s][: quota[s]]]
    rng.shuffle(out)
    return out


# ---- prompts --------------------------------------------------------------------------------

GEN_PROMPT = """You write search questions for a bank BSA/AML compliance knowledge base.

Read the passage and write ONE question that a compliance analyst or examiner might type into a \
search box, such that this passage contains the answer.

Rules:
- Self-contained: do not say "the passage", "this document", "the text", "above" or similar.
- Do not copy a sentence from the passage; paraphrase, and prefer the analyst's own wording over \
the regulation's.
- Specific enough that this passage, not just the general topic, is needed to answer it.
- Do not mention section numbers, document titles or FIN-xxxx identifiers.
- Output only the question, nothing else.

Passage:
{passage}"""

JUDGE_PROMPT = """You are checking a synthetic training pair for a retrieval model.

Question: {question}

Passage:
{passage}

Score 1-5:
5 = the passage directly and fully answers the question, which is natural and self-contained
4 = the passage answers the question, small gaps or slightly awkward wording
3 = the passage is related but only partly answers it
2 = mostly off-topic, or the question refers to missing context ("the passage", "this rule")
1 = the passage does not answer the question

Reply with JSON only: {{"score": <1-5>, "reason": "<one short sentence>"}}"""


def gen_prompt(c: dict) -> str:
    return GEN_PROMPT.format(passage=c["text"])


def judge_prompt(question: str, c: dict) -> str:
    return JUDGE_PROMPT.format(question=question, passage=c["text"])


def parse_question(text: str) -> str | None:
    q = text.strip().strip("\"'“”").strip()
    q = re.sub(r"^(question\s*:\s*)", "", q, flags=re.IGNORECASE).strip()
    if "\n" in q or len(q.split()) < MIN_QUESTION_WORDS:
        return None
    return q


def parse_judge(text: str) -> dict | None:
    m = re.search(r"\{.*\}", text, re.DOTALL)
    if not m:
        return None
    try:
        d = json.loads(m.group(0))
        score = int(d["score"])
    except (ValueError, KeyError, TypeError):
        return None
    return {"score": score, "reason": str(d.get("reason", ""))} if 1 <= score <= 5 else None


# ---- Bedrock (lazy: nothing above needs boto3 or credentials) -------------------------------


class Bedrock:
    def __init__(self, region: str = REGION):
        import boto3
        from botocore.config import Config

        self.client = boto3.client(
            "bedrock-runtime", region_name=region,
            config=Config(retries={"max_attempts": 8, "mode": "adaptive"}),
        )

    def complete(self, model_id: str, prompt: str, max_tokens: int = 200, temperature: float = 0.7) -> str:
        r = self.client.converse(
            modelId=model_id,
            messages=[{"role": "user", "content": [{"text": prompt}]}],
            inferenceConfig={"maxTokens": max_tokens, "temperature": temperature},
        )
        return r["output"]["message"]["content"][0]["text"]


# ---- resumable steps ------------------------------------------------------------------------


def read_jsonl(path: Path) -> list[dict]:
    if not path.exists():
        return []
    return [json.loads(x) for x in path.read_text(encoding="utf-8").splitlines() if x.strip()]


def append_jsonl(path: Path, row: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(row, ensure_ascii=False) + "\n")


def generate(llm, model_id: str, chunks: list[dict], idxs: list[int], out: Path, limit: int | None) -> int:
    done = {r["chunk_id"] for r in read_jsonl(out)}
    n = 0
    for i in idxs:
        c = chunks[i]
        if c["chunk_id"] in done:
            continue
        if limit is not None and n >= limit:
            break
        q = parse_question(llm.complete(model_id, gen_prompt(c)))
        if q is None:
            continue
        append_jsonl(out, {"chunk_id": c["chunk_id"], "source_type": c["source_type"],
                           "question": q, "gen_model": model_id})
        n += 1
    return n


def judge(llm, model_id: str, chunks_by_id: dict[str, dict], raw: Path, out: Path, limit: int | None) -> int:
    done = {r["chunk_id"] for r in read_jsonl(out)}
    n = 0
    for r in read_jsonl(raw):
        if r["chunk_id"] in done:
            continue
        if limit is not None and n >= limit:
            break
        j = parse_judge(llm.complete(model_id, judge_prompt(r["question"], chunks_by_id[r["chunk_id"]]),
                                     max_tokens=120, temperature=0.0))
        if j is None:
            continue
        append_jsonl(out, {**r, **j, "judge_model": model_id})
        n += 1
    return n


def filter_pairs(chunks: list[dict], questions: list[dict], judged: list[dict], threshold: int = 4) -> tuple[list[dict], dict]:
    by_id = {c["chunk_id"]: c for c in chunks}
    held = heldout_sections(chunks, questions)
    kept, stats = [], collections.Counter()
    for r in judged:
        c = by_id.get(r["chunk_id"])
        if c is None:
            stats["chunk_missing"] += 1
        elif section_key(c) in held:
            stats["heldout"] += 1
        elif r["score"] < threshold:
            stats["low_score"] += 1
        else:
            kept.append({"query": r["question"], "positive": c["text"], "chunk_id": r["chunk_id"],
                         "source_type": r["source_type"], "score": r["score"]})
            stats["kept"] += 1
    return kept, dict(stats)


# ---- CLI ------------------------------------------------------------------------------------


def estimate_tokens(chunks: list[dict], idxs: list[int]) -> int:
    # words * 1.35 is a rough English token estimate; there is no tokenizer for Bedrock models here
    return int(sum(len(gen_prompt(chunks[i]).split()) for i in idxs) * 1.35)


def cmd_plan(a, chunks, questions) -> None:
    idxs = eligible(chunks, questions)
    picked = sample(chunks, idxs, a.n, a.seed)
    print(f"chunks {len(chunks)} | eligible after held-out split {len(idxs)} | sampled {len(picked)}")
    print("sampled by source:", dict(collections.Counter(chunks[i]["source_type"] for i in picked)))
    t_in = estimate_tokens(chunks, picked)
    t_out = len(picked) * 30
    print(f"generation: ~{t_in:,} input tokens, ~{t_out:,} output tokens")
    print(f"judging (second pass): ~{t_in + len(picked) * 40:,} input tokens, ~{len(picked) * 40:,} output tokens")
    if a.price_in is not None and a.price_out is not None:
        cost = (t_in * 2 + len(picked) * 40) / 1e6 * a.price_in + (t_out + len(picked) * 40) / 1e6 * a.price_out
        print(f"estimated cost at your prices: ${cost:.2f}")
    print("\n--- example generation prompt ---\n" + gen_prompt(chunks[picked[0]])[:900])


def main() -> None:
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    p = sub.add_parser("plan")
    p.add_argument("--n", type=int, default=1500)
    p.add_argument("--seed", type=int, default=0)
    p.add_argument("--price-in", type=float, help="USD per 1M input tokens (look up in the Bedrock console)")
    p.add_argument("--price-out", type=float, help="USD per 1M output tokens")
    g = sub.add_parser("generate")
    g.add_argument("--gen-model", required=True)
    g.add_argument("--n", type=int, default=1500)
    g.add_argument("--seed", type=int, default=0)
    g.add_argument("--limit", type=int, help="stop after this many new pairs (try 20 first)")
    j = sub.add_parser("judge")
    j.add_argument("--judge-model", required=True)
    j.add_argument("--limit", type=int)
    f = sub.add_parser("filter")
    f.add_argument("--threshold", type=int, default=4)
    sub.add_parser("handcheck").add_argument("--k", type=int, default=50)
    a = ap.parse_args()

    chunks, questions = load_chunks(), load_questions()
    raw, judged, final = PAIRS / "raw.jsonl", PAIRS / "judged.jsonl", PAIRS / "pairs.jsonl"
    if a.cmd == "plan":
        cmd_plan(a, chunks, questions)
    elif a.cmd == "generate":
        idxs = sample(chunks, eligible(chunks, questions), a.n, a.seed)
        print("new pairs:", generate(Bedrock(), a.gen_model, chunks, idxs, raw, a.limit))
    elif a.cmd == "judge":
        gen_models = {r["gen_model"] for r in read_jsonl(raw)}
        if a.judge_model in gen_models:
            raise SystemExit("judge model must differ from the generator model")
        print("judged:", judge(Bedrock(), a.judge_model, {c["chunk_id"]: c for c in chunks}, raw, judged, a.limit))
    elif a.cmd == "filter":
        kept, stats = filter_pairs(chunks, questions, read_jsonl(judged), a.threshold)
        final.write_text("".join(json.dumps(r, ensure_ascii=False) + "\n" for r in kept), encoding="utf-8")
        print(stats, "->", final)
    elif a.cmd == "handcheck":
        rows = read_jsonl(final)
        random.Random(0).shuffle(rows)
        lines = ["# Hand-check: mark each pair ok / bad (50 needed)\n"]
        for n, r in enumerate(rows[: a.k], 1):
            lines += [f"## {n}. [{r['source_type']}] score {r['score']}", f"**Q:** {r['query']}", "",
                      f"> {r['positive'][:600].replace(chr(10), ' ')}", "", "- [ ] ok  - [ ] bad", ""]
        (PAIRS / "handcheck.md").write_text("\n".join(lines), encoding="utf-8")
        print("wrote", PAIRS / "handcheck.md")


if __name__ == "__main__":
    main()

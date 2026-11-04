"""Structure-aware chunking.

A parser yields `Section`s (a heading path + ordered blocks). `chunk_section` packs the blocks
into chunks of at most MAX_WORDS body words (~400 tokens at ~1.33 tokens/word). Chunks never cross
a section boundary. When a section is split, the last block (if short) is repeated as overlap.
Each chunk's embedding text is prefixed with its heading path ("Doc > H1 > H2").
"""

from __future__ import annotations

import hashlib
import re
from dataclasses import dataclass, field

MAX_WORDS = 300
OVERLAP_WORDS = 40
MIN_WORDS = 20  # chunks smaller than this are dropped (e.g. "[Reserved]", stray headings)
SEP = " \u203a "


@dataclass
class Block:
    text: str
    page: int | None = None
    label: str = ""  # e.g. legal paragraph label "(a)(1)"


@dataclass
class Section:
    doc: dict  # doc_id, source, title, url, retrieved_at, + extras copied into each chunk
    path: list[str]
    blocks: list[Block] = field(default_factory=list)
    cite_base: str = ""  # human-readable citation prefix; label/page appended per chunk


def words(text: str) -> int:
    return len(text.split())


def _split_long(block: Block) -> list[Block]:
    """Split one oversized block at sentence boundaries."""
    sentences = re.split(r"(?<=[.!?;:])\s+(?=[A-Z(\u201c\"])", block.text)
    out, cur = [], []
    for s in sentences:
        if cur and words(" ".join(cur)) + words(s) > MAX_WORDS:
            out.append(Block(" ".join(cur), block.page, block.label))
            cur = []
        cur.append(s)
    if cur:
        out.append(Block(" ".join(cur), block.page, block.label))
    # a single sentence can still exceed the cap: hard-split on words
    final = []
    for b in out:
        w = b.text.split()
        for i in range(0, len(w), MAX_WORDS):
            final.append(Block(" ".join(w[i : i + MAX_WORDS]), b.page, b.label))
    return final


def _citation(sec: Section, blocks: list[Block]) -> str:
    first, last = blocks[0], blocks[-1]
    cite = sec.cite_base
    if first.label:
        cite += first.label
    pages = [b.page for b in blocks if b.page]
    if pages:
        p0, p1 = min(pages), max(pages)
        cite += f" (PDF p. {p0})" if p0 == p1 else f" (PDF pp. {p0}\u2013{p1})"
    return cite


def chunk_section(sec: Section) -> list[dict]:
    blocks: list[Block] = []
    for b in sec.blocks:
        if not b.text.strip():
            continue
        blocks.extend(_split_long(b) if words(b.text) > MAX_WORDS else [b])

    groups: list[list[Block]] = []
    cur: list[Block] = []
    for b in blocks:
        if cur and sum(words(x.text) for x in cur) + words(b.text) > MAX_WORDS:
            groups.append(cur)
            tail = cur[-1]
            cur = [tail] if words(tail.text) <= OVERLAP_WORDS else []
        cur.append(b)
    if cur and (not groups or any(b not in groups[-1] for b in cur)):
        groups.append(cur)

    # headings path (drop consecutive duplicates, e.g. doc title == first heading)
    path: list[str] = []
    for p in [sec.doc["title"], *sec.path]:
        if p and (not path or path[-1].lower() != p.lower()):
            path.append(p)
    prefix = SEP.join(path)

    chunks = []
    for i, g in enumerate(groups):
        body = "\n\n".join(b.text for b in g)
        if words(body) < MIN_WORDS:
            continue
        sha = hashlib.sha1(body.encode()).hexdigest()[:10]
        chunks.append(
            {
                "chunk_id": f"{sec.doc['doc_id']}#{len(chunks):04d}-{sha}",
                **sec.doc,
                "section_path": path,
                "citation": _citation(sec, g),
                "page_start": min((b.page for b in g if b.page), default=None),
                "page_end": max((b.page for b in g if b.page), default=None),
                "n_words": words(body),
                "body": body,
                "text": f"{prefix}\n\n{body}",
            }
        )
    return chunks

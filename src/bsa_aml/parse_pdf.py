"""PDF -> Sections using font geometry (PyMuPDF).

Heading = block whose spans are all bold, short, and not smaller than body text.
Heading level = rank of its font size among heading sizes in the document (largest = level 1).
Repeated running headers/footers and bare page numbers are dropped.
"""

from __future__ import annotations

import collections
import re
from pathlib import Path

import pymupdf

from .chunking import Block, Section

BULLETS = str.maketrans({"\uf0b7": "\u2022", "\u25cb": "\u2022", "\u00a0": " "})
SENTENCE_END = re.compile(r"[.!?:;\u201d\")\]]$")
FOOTER_TEXT = {"return to contents"}
FFIEC_FOOTER = re.compile(r"^FFIEC BSA/AML Examination Manual \d+ \d+/\d+/\d+\.V\d+$")


def _norm(t: str) -> str:
    return re.sub(r"\s+", " ", t.translate(BULLETS)).strip()


def _blocks(doc: pymupdf.Document):
    """Yield (page_no, text, size, bold, y) for each text block."""
    for pno, page in enumerate(doc, 1):
        for b in page.get_text("dict")["blocks"]:
            spans = [s for ln in b.get("lines", []) for s in ln["spans"] if s["text"].strip()]
            if not spans:
                continue
            text = _norm(" ".join("".join(s["text"] for s in ln["spans"]) for ln in b["lines"]))
            n = sum(len(s["text"]) for s in spans)
            size = sum(s["size"] * len(s["text"]) for s in spans) / n
            bold = all(s["flags"] & 16 or "bold" in s["font"].lower() for s in spans)
            yield pno, text, size, bold, b["bbox"][1]


def parse_pdf(path: Path, doc_meta: dict, cite_base: str, title: str | None = None) -> list[Section]:
    pdf = pymupdf.open(path)
    raw = list(_blocks(pdf))
    if not raw:
        return []
    n_pages = len(pdf)
    # body size = most common size by characters
    cnt = collections.Counter()
    for _, t, size, _, _ in raw:
        cnt[round(size)] += len(t)
    body = cnt.most_common(1)[0][0]

    # running headers/footers: same normalized text on >=40% of pages (3+ page docs)
    seen = collections.defaultdict(set)
    for pno, t, *_ in raw:
        seen[re.sub(r"\d+", "#", t.lower())].add(pno)
    repeated = {
        k for k, v in seen.items() if n_pages >= 2 and len(v) >= max(2, 0.4 * n_pages) and len(k) < 200
    }

    def drop(t: str) -> bool:
        k = re.sub(r"\d+", "#", t.lower())
        return k in repeated or FFIEC_FOOTER.match(t) is not None or t.lower() in FOOTER_TEXT or re.fullmatch(r"(page )?\d+( of \d+)?", t.lower()) is not None

    items = []  # (kind, text, page, size)
    for pno, t, size, bold, y in raw:
        if drop(t) or (y < 60 and size < body - 0.5):  # running header in the top margin
            continue
        is_head = bold and len(t) <= 150 and size >= body - 1.5 and not t.startswith("\u2022")
        items.append(("h" if is_head else "p", t, pno, size))

    head_sizes = sorted({round(s) for k, _, _, s in items if k == "h"}, reverse=True)
    level_of = {s: i for i, s in enumerate(head_sizes)}

    doc_title = title or path.stem
    sections: list[Section] = []
    stack: dict[int, str] = {}

    def new_section() -> Section:
        return Section(doc=doc_meta, path=[stack[k] for k in sorted(stack)], cite_base=cite_base)

    cur = new_section()
    last_kind, last_size = None, None
    for kind, t, pno, size in items:
        if kind == "h":
            lvl = level_of[round(size)]
            if last_kind == "h" and last_size == round(size) and not cur.blocks:
                stack[lvl] += " " + t  # heading wrapped over several blocks
            else:
                if cur.blocks:
                    sections.append(cur)
                stack = {k: v for k, v in stack.items() if k < lvl}
                stack[lvl] = t
            cur = new_section()
            last_kind, last_size = "h", round(size)
            continue
        # join paragraphs split across page/column breaks
        if (
            cur.blocks
            and cur.blocks[-1].page != pno
            and not SENTENCE_END.search(cur.blocks[-1].text)
            and t[:1].islower()
        ):
            cur.blocks[-1].text += " " + t
        else:
            cur.blocks.append(Block(t, pno))
        last_kind = "p"
    if cur.blocks:
        sections.append(cur)
    for s in sections:
        s.doc = {**doc_meta, "title": doc_title}
    return sections

"""FinCEN HTML pages -> Sections (h1 = title, h2-h4 = nesting, p/li = blocks)."""

from __future__ import annotations

import re
from pathlib import Path

from bs4 import BeautifulSoup

from .chunking import Block, Section

DATE = re.compile(
    r"\b(January|February|March|April|May|June|July|August|September|October|November|December)"
    r" \d{1,2}, \d{4}\b"
)
JUNK = re.compile(r"breadcrumb|pager|share|sidebar|related|social|skip|usa-nav|menu", re.I)


def page_info(html: str) -> dict:
    soup = BeautifulSoup(html, "html.parser")
    main = soup.find("main") or soup
    h1 = main.find("h1")
    title = h1.get_text(" ", strip=True) if h1 else ""
    m = DATE.search(main.get_text(" ", strip=True)[:600])
    canon = soup.find("link", rel="canonical")
    return {
        "title": title,
        "published": m.group(0) if m else None,
        "canonical": canon["href"] if canon and canon.get("href") else None,
        "text_len": len(main.get_text(" ", strip=True)),
    }


def parse_html(path: Path, doc_meta: dict, cite_base: str) -> list[Section]:
    soup = BeautifulSoup(path.read_text(encoding="utf-8"), "html.parser")
    main = soup.find("main") or soup
    for t in main.find_all(["script", "style", "nav", "form", "aside", "footer", "header"]):
        t.decompose()
    for t in main.find_all(class_=JUNK):
        t.decompose()
    title = doc_meta.get("title") or "FinCEN"
    sections, stack = [], {}
    cur = Section(doc=doc_meta, path=[], cite_base=cite_base)

    def flush():
        nonlocal cur
        if cur.blocks:
            sections.append(cur)

    for el in main.find_all(["h2", "h3", "h4", "p", "li", "tr"]):
        if el.name == "li" and el.find("p"):
            continue
        text = re.sub(r"\s+", " ", el.get_text(" ", strip=True)).strip()
        if not text:
            continue
        if el.name[0] == "h":
            lvl = int(el.name[1])
            flush()
            stack = {k: v for k, v in stack.items() if k < lvl}
            stack[lvl] = text
            cur = Section(doc=doc_meta, path=[stack[k] for k in sorted(stack)], cite_base=cite_base)
        elif el.name == "li" or el.name == "tr":
            cur.blocks.append(Block("\u2022 " + text if el.name == "li" else text))
        elif not (el.find_parent("li") or el.find_parent("tr")):
            cur.blocks.append(Block(text))
    flush()
    return sections

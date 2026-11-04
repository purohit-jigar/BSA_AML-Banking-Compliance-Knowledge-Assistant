"""eCFR XML (one file per CFR part) -> Sections, one per CFR section, with paragraph labels."""

from __future__ import annotations

import re
from pathlib import Path

from lxml import etree

from .chunking import Block, Section

SKIP = {"HEAD", "CITA", "AUTH", "SOURCE", "XREF", "EDNOTE", "EFFDNOTE"}
MARK = re.compile(r"^\(([A-Za-z]{1,3}|\d{1,3})\)")


def _text(el) -> str:
    return re.sub(r"\s+", " ", "".join(el.itertext())).strip()


def parse_ecfr(path: Path, doc_meta: dict, part_title: str) -> list[Section]:
    root = etree.fromstring(path.read_bytes())
    out: list[Section] = []
    for sec in root.iter("DIV8"):
        if sec.get("TYPE") != "SECTION":
            continue
        num = sec.get("N")
        head = _text(sec.find("HEAD")) if sec.find("HEAD") is not None else num
        subpart = ""
        for anc in sec.iterancestors():
            if anc.get("TYPE") == "SUBPART":
                subpart = _text(anc.find("HEAD"))
                break
        blocks: list[Block] = []
        top = sub = None
        for child in sec:
            if child.tag in SKIP:
                continue
            t = _text(child)
            if not t or re.sub(r"[\[\]\s]|Reserved", "", t) == "":
                continue
            m = MARK.match(t)
            if m:
                mk = m.group(1)
                if mk.isdigit():
                    sub = mk
                elif mk.islower() and (
                    len(mk) > 1 or mk not in "ivx" or top is None or ord(mk) == ord(top[-1]) + 1
                ):
                    top, sub = mk, None
            label = f"({top})" if top else ""
            if top and sub:
                label += f"({sub})"
            blocks.append(Block(t, None, label))
        if not blocks:
            continue
        d = {**doc_meta, "title": part_title, "url": f"https://www.ecfr.gov/current/title-31/section-{num}"}
        out.append(
            Section(
                doc=d,
                path=[p for p in [subpart, head] if p],
                blocks=blocks,
                cite_base=f"31 CFR \u00a7 {num}",
            )
        )
    return out

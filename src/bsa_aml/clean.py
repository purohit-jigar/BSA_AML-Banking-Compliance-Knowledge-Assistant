"""Post-chunking cleanup for FinCEN chunks (see docs/PROGRESS.md, FinCEN spot-check).

- repair letter-spaced PDF text ("t he F ATF") or drop the chunk if it stays garbled
- normalize letter-spaced / over-long headings
- drop footnote/reference-only chunks and tiny chunks
- old-advisory policy: advisories before CUTOFF_YEAR are kept only if they carry typology /
  red-flag content, and never if they are FATF-jurisdiction notices, UNSC/G20 attachments or
  withdrawal notices. Guidance, FAQs and rulings are always kept.
"""

from __future__ import annotations

import re

CUTOFF_YEAR = 2016
MIN_FINCEN_WORDS = 30
MAX_HEADING = 160
SUPERSEDED_NOTE = "Older advisory; may be superseded by later guidance."

_DENY = re.compile(
    r"financial action task force|\bFATF\b|security council|\bG-?20\b|summit|withdrawal|"
    r"high-risk and non-cooperative|jurisdictions? (?:with|identified)",
    re.I,
)
_KEEP = re.compile(r"red flag|typolog|suspicious activit|\bSAR\b|indicator|scheme|layering|structur", re.I)
_EXEMPT_TITLE = re.compile(r"interagency|faq|guidance", re.I)


def _frag_ratio(t: str) -> float:
    w = t.split()
    return sum(1 for x in w if len(x) == 1 and x.isalpha() and x.lower() not in "ai") / max(1, len(w))


def despace_heading(h: str) -> str:
    """'R E C O R D K E E P I N G' -> 'RECORDKEEPING' (words of single letters get joined)."""
    return re.sub(r"\b(?:[A-Za-z] ){3,}[A-Za-z]\b", lambda m: m.group(0).replace(" ", ""), h)


def repair_spacing(t: str) -> str:
    """Rejoin 1-2 letter fragments split inside words: 'c ustomer' 't he' -> 'customer' 'the'."""
    t = re.sub(r"\b([a-z]) ([a-z]{3,})\b", lambda m: m.group(1) + m.group(2), t)
    return t


def _year(c: dict) -> int | None:
    m = re.search(r"\((?:[A-Za-z]+ \d+, )?(\d{4})\)", c["citation"]) or re.search(r"fin-(\d{4})-", c["doc_id"], re.I)
    return int(m.group(1)) if m else None


def _footnote_only(body: str) -> bool:
    lines = [ln for ln in body.splitlines() if ln.strip()]
    if not lines:
        return True
    notes = sum(bool(re.match(r"\s*\d{1,3}[\.\s]+(?:See|Id\b|Ibid|Supra|http|www|FinCEN|Treasury|U\.S\.|\d)", ln)) for ln in lines)
    return notes / len(lines) >= 0.5 and len(re.findall(r"\b\d{1,3}\.\s", body)) >= 2


def clean_fincen(chunks: list[dict], dropped: dict) -> list[dict]:
    out = []
    for c in chunks:
        if c["source_type"] != "fincen":
            out.append(c)
            continue
        body = c["body"]
        if _frag_ratio(body) > 0.05:
            body = repair_spacing(body)
            if _frag_ratio(body) > 0.05:
                dropped["garbled"] += 1
                continue
        path = [despace_heading(p) for p in c["section_path"]]
        path = [p if len(p) <= MAX_HEADING else p[:MAX_HEADING].rsplit(" ", 1)[0] + "…" for p in path]
        if _footnote_only(body):
            dropped["footnote"] += 1
            continue
        if len(body.split()) < MIN_FINCEN_WORDS:
            dropped["tiny"] += 1
            continue
        c = {**c, "body": body, "section_path": path}
        if "advisory" in c["doc_id"]:
            y = _year(c)
            if y is None or y < CUTOFF_YEAR:
                head = " ".join(path[:3])
                exempt = _EXEMPT_TITLE.search(c["title"]) and not re.search(r"advisory\s*[–-]\s*fin-", c["title"], re.I)
                if not exempt and (_DENY.search(head + " " + body[:600]) or not _KEEP.search(body)):
                    dropped["old_advisory"] += 1
                    continue
            if y is not None and y < CUTOFF_YEAR:
                c["superseded_note"] = SUPERSEDED_NOTE
        c["text"] = " \u203a ".join(path) + "\n\n" + c["body"]
        c["n_words"] = len(c["body"].split())
        out.append(c)
    return out

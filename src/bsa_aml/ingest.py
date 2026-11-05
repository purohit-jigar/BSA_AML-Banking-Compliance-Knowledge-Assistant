"""Parse data/raw (via manifest.json) into data/processed/chunks.jsonl + ingest_report.json.

Usage: python -m bsa_aml.ingest [--sources ffiec,ecfr,fincen]
"""

from __future__ import annotations

import argparse
import collections
import hashlib
import json
import re
from pathlib import Path

import pymupdf

from .chunking import chunk_section
from .clean import clean_fincen
from .parse_ecfr import parse_ecfr
from .parse_fincen import page_info, parse_html
from .parse_pdf import parse_pdf

ROOT = Path(__file__).resolve().parents[2]
MANIFEST = ROOT / "data" / "raw" / "manifest.json"
OUT = ROOT / "data" / "processed"
NON_ENGLISH = re.compile(r"spanish|espa[nñ]ol|chinese|korean|vietnamese|russian|arabic|farsi|tagalog", re.I)
MIN_HTML_CHARS = 1500


def _shingles(text: str, n: int = 8) -> set[str]:
    w = re.sub(r"\W+", " ", text.lower()).split()
    return {" ".join(w[i : i + n]) for i in range(0, max(len(w) - n, 0), 3)}


def _pdf_text(path: Path) -> str:
    return " ".join(p.get_text() for p in pymupdf.open(path))


def meta(rec: dict, kind: str, title: str, **extra) -> dict:
    return {
        "doc_id": rec["id"],
        "source": rec["source"],
        "source_type": kind,
        "title": title,
        "url": rec["url"],
        "retrieved_at": rec["retrieved_at"],
        **extra,
    }


def _chapter(rec: dict) -> str:
    name = re.match(r"ffiec-\d+_(\w+)-\d+$", rec["id"]).group(1)
    name = re.sub(r"(?<=[a-z])(?=[A-Z])|(?<=[A-Z])(?=[A-Z][a-z])", " ", name)
    return name.replace("BSAAML", "BSA/AML")


def _page1_title(path: Path) -> str:
    """Clean document title printed in the top margin of page 1 (empty if absent)."""
    for b in pymupdf.open(path)[0].get_text("dict")["blocks"]:
        if b["bbox"][1] < 62 and b.get("lines"):
            t = " ".join("".join(sp["text"] for sp in ln["spans"]) for ln in b["lines"])
            t = re.sub(r"\s+", " ", t).strip()
            if t:
                return t
    return ""


def ffiec(recs, report):
    for r in recs:
        path = ROOT / r["path"]
        # PDF metadata titles are unreliable (stale "2014 ..." / "Microsoft Word - ..."), so the
        # title is the page-1 top-margin heading, else the first heading in the body.
        secs = parse_pdf(path, meta(r, "ffiec", "", chapter=_chapter(r)), "", "")
        title = _page1_title(path) or next((s.path[0] for s in secs if s.path), _chapter(r))
        base = f"FFIEC BSA/AML Examination Manual, {title}"
        for s in secs:
            s.doc = {**s.doc, "title": title}
            rest = s.path[1:] if s.path and s.path[0] == title else s.path
            s.cite_base = base + (f", {rest[-1]}" if rest else "")
        yield r, secs


def ecfr(recs, report):
    for r in recs:
        title = r["title"]
        yield r, parse_ecfr(ROOT / r["path"], meta(r, "ecfr", title, as_of=r.get("as_of")), "")


def fincen(recs, report):
    pages = {r["url"]: r for r in recs if r["path"].endswith(".html")}
    pdfs_by_parent = collections.defaultdict(list)
    for r in recs:
        if r["path"].endswith(".pdf"):
            pdfs_by_parent[r.get("parent")].append(r)
    seen_pdf: set[str] = set()
    # PDFs first, so HTML pages can be checked against their own PDFs
    pdf_text: dict[str, str] = {}
    for url, page in pages.items():
        info = page_info((ROOT / page["path"]).read_text(encoding="utf-8"))
        title = info["title"] or page["title"]
        if NON_ENGLISH.search(page["id"]) or NON_ENGLISH.search(title):
            report["skipped"].append({"id": page["id"], "why": "non-English"})
            continue
        own_pdfs = []
        for p in pdfs_by_parent.get(url, []):
            if p["sha256"] in seen_pdf:
                report["skipped"].append({"id": p["id"], "why": "duplicate PDF (same sha256)"})
                continue
            if NON_ENGLISH.search(p["path"]):
                report["skipped"].append({"id": p["id"], "why": "non-English PDF"})
                continue
            seen_pdf.add(p["sha256"])
            own_pdfs.append(p)
        extra = {"published": info["published"], "page_url": url}
        multi = len(own_pdfs) > 1
        for p in own_pdfs:
            ptitle = title if not multi else f"{title} ({Path(p['path']).stem.split('--')[-1]})"
            base = f"FinCEN, {ptitle}" + (f" ({info['published']})" if info["published"] else "")
            try:
                pdf_text[p["id"]] = _pdf_text(ROOT / p["path"])
                secs = parse_pdf(ROOT / p["path"], meta(p, "fincen", ptitle, **extra), base, ptitle)
            except Exception as e:  # corrupt / scanned PDFs
                report["skipped"].append({"id": p["id"], "why": f"pdf parse error: {e}"})
                continue
            for s in secs:
                s.cite_base = base + (f", {s.path[-1]}" if s.path else "")
            yield p, secs
        # HTML body
        if info["text_len"] < MIN_HTML_CHARS:
            continue
        html_secs = parse_html(
            ROOT / page["path"],
            meta(page, "fincen", title, **extra),
            f"FinCEN, {title}" + (f" ({info['published']})" if info["published"] else ""),
        )
        html_text = " ".join(b.text for s in html_secs for b in s.blocks)
        hs = _shingles(html_text)
        dup = max(
            (len(hs & _shingles(pdf_text[p["id"]])) / max(len(hs), 1) for p in own_pdfs if p["id"] in pdf_text),
            default=0.0,
        )
        if dup >= 0.6:
            report["skipped"].append({"id": page["id"], "why": f"HTML duplicates its PDF ({dup:.0%})"})
            continue
        yield page, html_secs


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--sources", default="ffiec,ecfr,fincen")
    args = ap.parse_args()
    wanted = set(args.sources.split(","))
    manifest = json.loads(MANIFEST.read_text())
    groups = {
        "ffiec": ("FFIEC BSA/AML Examination Manual", ffiec),
        "ecfr": ("eCFR 31 CFR Chapter X", ecfr),
        "fincen": ("FinCEN guidance", fincen),
    }
    OUT.mkdir(parents=True, exist_ok=True)
    report = {"skipped": [], "by_source": {}, "duplicate_chunks_dropped": 0}
    seen_body: set[str] = set()
    out_path = OUT / "chunks.jsonl"
    # keep other sources' chunks when re-running a subset
    kept = []
    if out_path.exists():
        kept = [json.loads(line) for line in out_path.read_text(encoding="utf-8").splitlines()]
        kept = [c for c in kept if c["source_type"] not in wanted]
    chunks = kept
    for c in kept:
        seen_body.add(hashlib.sha1(re.sub(r"\W+", "", c["body"].lower()).encode()).hexdigest())
    for key, (source, fn) in groups.items():
        if key not in wanted:
            continue
        recs = [r for r in manifest if r["source"] == source]
        n_docs = n_chunks = 0
        for rec, secs in fn(recs, report):
            n_docs += 1
            for s in secs:
                for c in chunk_section(s):
                    h = hashlib.sha1(re.sub(r"\W+", "", c["body"].lower()).encode()).hexdigest()
                    if h in seen_body:
                        report["duplicate_chunks_dropped"] += 1
                        continue
                    seen_body.add(h)
                    chunks.append(c)
                    n_chunks += 1
        report["by_source"][key] = {"docs": n_docs, "chunks": n_chunks}
        print(key, report["by_source"][key])
    dropped = collections.Counter()
    chunks = clean_fincen(chunks, dropped)
    report["cleanup_dropped"] = dict(dropped)
    print("cleanup dropped", dict(dropped))
    with out_path.open("w", encoding="utf-8") as f:
        for c in chunks:
            f.write(json.dumps(c, ensure_ascii=False) + "\n")
    w = sorted(c["n_words"] for c in chunks)
    report["total_chunks"] = len(chunks)
    report["words"] = {"min": w[0], "median": w[len(w) // 2], "p95": w[int(len(w) * 0.95)], "max": w[-1]}
    (OUT / "ingest_report.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
    print("total", len(chunks), report["words"], "skipped", len(report["skipped"]))


if __name__ == "__main__":
    main()

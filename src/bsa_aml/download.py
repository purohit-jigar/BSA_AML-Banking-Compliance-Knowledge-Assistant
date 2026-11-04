"""Register the public BSA/AML corpus in data/raw/manifest.json.

FFIEC PDFs are fetched with plain curl (the site returns 403 to Python HTTP clients);
this module hashes and validates what is on disk and records URL + retrieval date.

Each manifest record: id, source, title, url, path, sha256, bytes, retrieved_at.
Polite by design: identifying User-Agent, delay between requests, retries, resumable.
"""

from __future__ import annotations

import hashlib
import json
import re
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

import httpx

ROOT = Path(__file__).resolve().parents[2]
RAW = ROOT / "data" / "raw"
MANIFEST = RAW / "manifest.json"
UA = "Mozilla/5.0 (research; bsa-aml-assistant portfolio project)"
DELAY_S = 1.0

FFIEC_BASE = "https://bsaaml.ffiec.gov"


def discover_ffiec(client: httpx.Client) -> list[dict]:
    """The manual index links one PDF per section: /docs/manual/<NN_Section>/<MM>.pdf."""
    html = client.get(f"{FFIEC_BASE}/manual").text
    paths = sorted(set(re.findall(r'href="\s*(/docs/manual/[^"]+\.pdf)"', html)))
    records = []
    for p in paths:
        _, _, _, chapter, fname = p.split("/")
        num, _, name = chapter.partition("_")
        title = re.sub(r"(?<!^)(?=[A-Z])", " ", name)
        records.append(
            {
                "id": f"ffiec-{chapter}-{fname[:-4]}",
                "source": "FFIEC BSA/AML Examination Manual",
                "title": f"{title} ({num}/{fname[:-4]})",
                "url": FFIEC_BASE + p,
                "ext": "pdf",
            }
        )
    return records


def fetch(client: httpx.Client, rec: dict) -> dict | None:
    dest = RAW / rec["source"].split()[0].lower() / f"{rec['id']}.{rec['ext']}"
    dest.parent.mkdir(parents=True, exist_ok=True)
    if not dest.exists():
        for attempt in range(4):
            try:
                r = client.get(rec["url"])
                r.raise_for_status()
                dest.write_bytes(r.content)
                time.sleep(DELAY_S)
                break
            except httpx.HTTPError as e:
                print(f"  retry {attempt + 1} {rec['url']}: {e}", file=sys.stderr)
                time.sleep(2**attempt)
        else:
            print(f"FAILED {rec['url']}", file=sys.stderr)
            return None
    data = dest.read_bytes()
    return {
        **rec,
        "path": str(dest.relative_to(ROOT)).replace("\\", "/"),
        "sha256": hashlib.sha256(data).hexdigest(),
        "bytes": len(data),
        "retrieved_at": datetime.fromtimestamp(dest.stat().st_mtime, timezone.utc).isoformat(),
    }


def main() -> None:
    RAW.mkdir(parents=True, exist_ok=True)
    existing = json.loads(MANIFEST.read_text()) if MANIFEST.exists() else []
    done = {r["id"]: r for r in existing}
    with httpx.Client(headers={"User-Agent": UA}, follow_redirects=True, timeout=60) as client:
        recs = discover_ffiec(client)
        print(f"FFIEC: {len(recs)} PDFs discovered")
        for i, rec in enumerate(recs, 1):
            print(f"[{i}/{len(recs)}] {rec['id']}")
            out = fetch(client, rec)
            if out:
                done[out["id"]] = out
    MANIFEST.write_text(json.dumps(sorted(done.values(), key=lambda r: r["id"]), indent=2))
    print(f"manifest: {len(done)} documents")


if __name__ == "__main__":
    main()

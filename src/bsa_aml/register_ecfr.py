"""Merge eCFR 31 CFR Chapter X part files (data/raw/ecfr) into the manifest.

Files are fetched with curl --compressed from the eCFR versioner API, pinned to an as-of date:
  https://www.ecfr.gov/api/versioner/v1/full/<AS_OF>/title-31.xml?chapter=X&part=<N>
"""

from __future__ import annotations

import hashlib
import json
import re
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
RAW = ROOT / "data" / "raw"
MANIFEST = RAW / "manifest.json"
AS_OF = "2026-11-02"


def main() -> None:
    records = json.loads(MANIFEST.read_text()) if MANIFEST.exists() else []
    records = [r for r in records if not r["id"].startswith("ecfr-")]
    for f in sorted((RAW / "ecfr").glob("ecfr-31cfr-*.xml")):
        part = re.search(r"-(\d+)\.xml", f.name).group(1)
        data = f.read_bytes()
        text = data.decode("utf-8")
        title = re.search(r"<HEAD>PART \d+&#x2014;([^<\n]+)", text)
        records.append(
            {
                "id": f.stem,
                "source": "eCFR 31 CFR Chapter X",
                "title": f"31 CFR Part {part}"
                + (f" - {title.group(1).strip()}" if title else ""),
                "url": f"https://www.ecfr.gov/current/title-31/part-{part}",
                "api_url": "https://www.ecfr.gov/api/versioner/v1/full/"
                f"{AS_OF}/title-31.xml?chapter=X&part={part}",
                "as_of": AS_OF,
                "path": f.relative_to(ROOT).as_posix(),
                "sections": text.count('TYPE="SECTION"'),
                "sha256": hashlib.sha256(data).hexdigest(),
                "bytes": len(data),
                "retrieved_at": datetime.fromtimestamp(f.stat().st_mtime, timezone.utc).isoformat(),
            }
        )
    MANIFEST.write_text(json.dumps(sorted(records, key=lambda r: r["id"]), indent=2))
    print(len(records), "records total")


if __name__ == "__main__":
    main()

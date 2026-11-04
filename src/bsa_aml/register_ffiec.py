"""Build manifest records for FFIEC PDFs already downloaded to data/raw/ffiec."""

from __future__ import annotations

import hashlib
import json
import re
from datetime import datetime, timezone
from pathlib import Path

from pypdf import PdfReader

ROOT = Path(__file__).resolve().parents[2]
RAW = ROOT / "data" / "raw"
MANIFEST = RAW / "manifest.json"
BASE = "https://bsaaml.ffiec.gov/docs/manual"


def main() -> None:
    records = []
    for f in sorted((RAW / "ffiec").glob("ffiec-*.pdf")):
        m = re.fullmatch(r"ffiec-(\d+)_(\w+)-(\d+)\.pdf", f.name)
        num, name, part = m.groups()
        data = f.read_bytes()
        reader = PdfReader(f)
        records.append(
            {
                "id": f.stem,
                "source": "FFIEC BSA/AML Examination Manual",
                "title": f"{re.sub(r'(?<!^)(?=[A-Z])', ' ', name)} ({num}/{part})",
                "url": f"{BASE}/{num}_{name}/{part}.pdf",
                "path": f.relative_to(ROOT).as_posix(),
                "pages": len(reader.pages),
                "sha256": hashlib.sha256(data).hexdigest(),
                "bytes": len(data),
                "retrieved_at": datetime.fromtimestamp(f.stat().st_mtime, timezone.utc).isoformat(),
            }
        )
    MANIFEST.write_text(json.dumps(records, indent=2))
    print(f"{len(records)} docs, {sum(r['pages'] for r in records)} pages")


if __name__ == "__main__":
    main()

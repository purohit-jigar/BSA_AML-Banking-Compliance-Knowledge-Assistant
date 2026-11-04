"""Crawl FinCEN guidance/FAQ/advisory listings, save detail pages + linked PDFs, update manifest.

Scope (v1): /resources/statutes-regulations/guidance/* and
/resources/advisoriesbulletinsfact-sheets/advisories/* (see listing pages below).
Polite: honest User-Agent, 1 s delay, sequential, resumable. Stops on HTTP 403.
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
from bs4 import BeautifulSoup

ROOT = Path(__file__).resolve().parents[2]
RAW = ROOT / "data" / "raw" / "fincen"
MANIFEST = ROOT / "data" / "raw" / "manifest.json"
BASE = "https://www.fincen.gov"
UA = "bsa-aml-assistant (portfolio research project)"
DELAY_S = 1.0
LISTINGS = {
    "guidance": "/resources/statutes-regulations/guidance",
    "advisory": "/resources/advisoriesbulletinsfact-sheets/advisories",
}
MAX_PAGES = 40


class Blocked(Exception):
    pass


def get(client: httpx.Client, url: str) -> httpx.Response | None:
    for attempt in range(3):
        r = client.get(url)
        time.sleep(DELAY_S)
        if r.status_code == 403:
            raise Blocked(url)
        if r.status_code == 404:
            print(f"  404 skipped: {url}")
            return None
        if r.status_code < 400:
            return r
        time.sleep(2**attempt)
    print(f"  HTTP {r.status_code} skipped: {url}")
    return None


def listing_items(client: httpx.Client, kind: str, path: str) -> list[str]:
    seen: list[str] = []
    for page in range(MAX_PAGES):
        resp = get(client, f"{BASE}{path}?page={page}")
        if resp is None:
            break
        soup = BeautifulSoup(resp.text, "html.parser")
        found = [
            a["href"].split("#")[0]
            for a in soup.find_all("a", href=True)
            if a["href"].startswith(path + "/") or a["href"].startswith(
                "/resources/advisoriesbulletinsfact-sheets/" + ("advisories/" if kind == "advisory" else "x/")
            ) or a["href"].startswith("/resources/advisories/")
        ]
        new = [h for h in dict.fromkeys(found) if h not in seen]
        print(f"  {kind} page {page}: {len(new)} new")
        if not new:
            break
        seen += new
    return seen


def main() -> None:
    RAW.mkdir(parents=True, exist_ok=True)
    records = [r for r in json.loads(MANIFEST.read_text()) if not r["id"].startswith("fincen-")]
    with httpx.Client(headers={"User-Agent": UA}, follow_redirects=True, timeout=60) as client:
        try:
            for kind, path in LISTINGS.items():
                items = listing_items(client, kind, path)
                print(f"{kind}: {len(items)} items")
                for i, href in enumerate(items, 1):
                    slug = href.rstrip("/").split("/")[-1]
                    rec = fetch_page(client, kind, slug, href)
                    if rec:
                        records.extend(rec)
                    if i % 20 == 0:
                        print(f"  [{i}/{len(items)}]")
        except Blocked as e:
            print(f"HTTP 403 from {e}; stopping.", file=sys.stderr)
        finally:
            MANIFEST.write_text(
                json.dumps(sorted(records, key=lambda r: r["id"]), indent=2)
            )
    print(len(records), "manifest records")


def record(path: Path, **kw) -> dict:
    data = path.read_bytes()
    return {
        **kw,
        "path": path.relative_to(ROOT).as_posix(),
        "sha256": hashlib.sha256(data).hexdigest(),
        "bytes": len(data),
        "retrieved_at": datetime.fromtimestamp(path.stat().st_mtime, timezone.utc).isoformat(),
    }


def fetch_page(client: httpx.Client, kind: str, slug: str, href: str) -> list[dict]:
    out = []
    html_path = RAW / f"fincen-{kind}-{slug}.html"
    if not html_path.exists():
        resp = get(client, BASE + href)
        if resp is None:
            return out
        html_path.write_text(resp.text, encoding="utf-8")
    html = html_path.read_text(encoding="utf-8")
    soup = BeautifulSoup(html, "html.parser")
    h1 = soup.find("h1")
    title = h1.get_text(" ", strip=True) if h1 else slug
    out.append(
        record(html_path, id=f"fincen-{kind}-{slug}", source="FinCEN guidance", kind=kind,
               title=title, url=BASE + href)
    )
    # linked PDFs inside the page body (main content)
    main = soup.find("main") or soup
    pdfs = {a["href"] for a in main.find_all("a", href=True) if a["href"].lower().endswith(".pdf")}
    for p in sorted(pdfs):
        url = p if p.startswith("http") else BASE + p
        if "fincen.gov" not in url:
            continue
        name = re.sub(r"[^A-Za-z0-9._-]", "_", url.rsplit("/", 1)[-1])[:80]
        pdf_path = RAW / f"fincen-{kind}-{slug}--{name}"
        if not pdf_path.exists():
            resp = get(client, url)
            if resp is None:
                continue
            pdf_path.write_bytes(resp.content)
        out.append(
            record(pdf_path, id=pdf_path.stem, source="FinCEN guidance", kind=kind,
                   title=f"{title} (PDF: {name})", url=url, parent=BASE + href)
        )
    return out


if __name__ == "__main__":
    main()

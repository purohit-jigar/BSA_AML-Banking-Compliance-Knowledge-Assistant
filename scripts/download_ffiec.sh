#!/usr/bin/env bash
# Fetch the FFIEC BSA/AML Manual section PDFs with plain curl (the site returns 403 to Python HTTP
# clients). Sequential, 1 request/second, identifying User-Agent. Legacy 2014 files are skipped.
set -euo pipefail
cd "$(dirname "$0")/.."
UA="Mozilla/5.0 (research; bsa-aml-assistant)"
mkdir -p data/raw/ffiec
curl -sL -A "$UA" https://bsaaml.ffiec.gov/manual -o data/raw/ffiec_index.html
args=()
for p in $(grep -oE '/docs/manual/[0-9]+_[^"]+\.pdf' data/raw/ffiec_index.html | sort -u); do
  c=$(echo "$p" | cut -d/ -f4); f=$(basename "$p" .pdf)
  args+=(-o "data/raw/ffiec/ffiec-$c-$f.pdf" "https://bsaaml.ffiec.gov$p")
done
curl -sL -A "$UA" --rate 1/s --retry 2 --fail "${args[@]}"
uv run python -m bsa_aml.register_ffiec

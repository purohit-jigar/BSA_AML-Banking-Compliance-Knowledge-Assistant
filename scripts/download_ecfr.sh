#!/usr/bin/env bash
# Fetch 31 CFR Chapter X parts from the eCFR versioner API, pinned to AS_OF.
# The API requires response compression (--compressed). Part 1032 is an empty placeholder.
set -euo pipefail
cd "$(dirname "$0")/.."
AS_OF="${AS_OF:-2026-11-02}"
mkdir -p data/raw/ecfr
args=()
for p in 1010 1020 1021 1022 1023 1024 1025 1026 1027 1028 1029 1030 1031 1060; do
  args+=(-o "data/raw/ecfr/ecfr-31cfr-$p.xml" \
    "https://www.ecfr.gov/api/versioner/v1/full/$AS_OF/title-31.xml?chapter=X&part=$p")
done
curl -sL --compressed -H 'Accept: application/xml' --rate 30/m --retry 2 --fail "${args[@]}"
uv run python -m bsa_aml.register_ecfr

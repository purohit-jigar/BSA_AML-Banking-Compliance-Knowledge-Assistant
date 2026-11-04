.PHONY: setup download ingest test lint
setup:
	uv sync
download:
	bash scripts/download_ffiec.sh
	bash scripts/download_ecfr.sh
	uv run python -m bsa_aml.fincen
ingest:
	uv run python -m bsa_aml.ingest
test:
	uv run pytest
lint:
	uv run ruff check .

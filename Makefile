.PHONY: setup download ingest test lint
setup:
	uv sync
download:
	uv run python -m bsa_aml.download
ingest:
	uv run python -m bsa_aml.ingest
test:
	uv run pytest
lint:
	uv run ruff check .

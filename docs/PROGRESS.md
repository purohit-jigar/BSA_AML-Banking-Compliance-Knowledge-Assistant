# Progress & Next Steps

_Last updated: 2026-11-04. Read this first when resuming._

## Project
Citation-grounded BSA/AML RAG assistant (see `Project.txt`): LangChain + FAISS + Bedrock, RAGAS +
Guardrails AI, fine-tuned sentence-transformers embedder, FastAPI on AWS. Portfolio project; every
résumé claim must be measured (the "+18% recall@5" is a *target*, not a result; the bullet gets
rewritten to match whatever is measured).

## Decisions agreed (grilling session, Q1-Q22)
- **Corpus (v1):** FFIEC BSA/AML Manual + FinCEN guidance/FAQs/advisories + 31 CFR Chapter X. Pinned
  snapshot, no auto-refresh. Source URL + retrieval date on every chunk and in `/sources`.
- **Answers:** section-level citations on every claim; hard refusal when retrieval confidence is low.
- **Chunking:** structure-aware, <=300 words (~400 tokens), heading path prepended, overlap only when
  a section is split.
- **Retrieval:** dense FAISS + BM25 hybrid with RRF. Reranker is a later experiment. Report recall@5
  separately for dense-base, dense-fine-tuned, hybrid.
- **Fine-tuning:** base `bge-small-en-v1.5`; synthetic question-passage pairs from a cheap Bedrock
  model, LLM-judge filtered, 50 pairs hand-checked; MultipleNegativesRankingLoss + hard negatives.
  **Train/test split by section**, plus a **50-question hand-written test set** (written by the user,
  with gold sections). Report both numbers even if the gain is < 18%. Freeze the test set and record
  baseline recall@5 *before* any fine-tuning.
- **Guardrails AI:** citation required + cited IDs must exist in retrieved set; grounding check
  (NLI or LLM judge); no PII; refuse legal-advice / evasion / structuring requests; disclaimer. One
  retry with failure reason, then safe refusal; log all failures.
- **RAGAS:** ~100-question golden set (incl. ~15 unanswerable, ~10 adversarial); judge model differs
  from generator; results committed as versioned JSON.
- **API:** `POST /ask`, `GET /health`, `GET /sources`; API-key header; single-turn; no streaming.
- **Stack:** Python 3.12 (uv), pytest, ruff, Makefile. Local RTX 4060 8 GB for training.
- **AWS:** personal account, us-east-1, App Runner + S3 artifacts, IaC (Terraform/CDK), tear down
  when not demoing. Budget cap $50, alert at $25. Bedrock for generation only; embedder runs locally
  in the container.
- **Definition of done:** all `make` targets run; recall@5 reported on both test sets; RAGAS report
  committed; guardrails block the adversarial cases; live on AWS with README, demo, cost notes.
  Out of scope: UI, multi-turn, other regulators.

## Done so far
| Step | State |
|---|---|
| Repo skeleton (`pyproject.toml`, Makefile, dirs, `.gitignore`) | done |
| Download: FFIEC (81 PDFs, 363 pp), eCFR (14 parts, as of 2026-11-02), FinCEN (331 pages, ~590 PDFs) | done; manifest at `data/raw/manifest.json` (1,012 records) |
| Ingest + chunking -> `data/processed/chunks.jsonl` | **done: 7,629 chunks** (FFIEC 662, eCFR 505, FinCEN 6,462); report in `data/processed/ingest_report.json` |
| Tests | 6 passing (`uv run pytest`) |

Code: `src/bsa_aml/` -> `chunking.py`, `parse_pdf.py`, `parse_ecfr.py`, `parse_fincen.py`,
`ingest.py`, `fincen.py` (crawler), `register_ffiec.py`, `register_ecfr.py`.
Downloads: `scripts/download_ffiec.sh`, `scripts/download_ecfr.sh` (**untested as scripts**; the
same curl calls were run by hand and worked). `make download` chains them with the FinCEN crawler.

## Known issues / things to know
- **FFIEC returns 403 to Python HTTP clients**; plain `curl` with a normal User-Agent works. Do not
  rotate headers to get around blocks. A permission rule for `curl *bsaaml.ffiec.gov*` is in
  `.claude/settings.local.json`. Optionally email `ffiecinfobase@frb.gov` to confirm bulk-download
  OK (draft is in the chat history; send from your own address).
- eCFR needs `--compressed` and a pinned as-of date; Part 1032 is an empty placeholder (excluded).
- Two 2014 FFIEC files are in `data/raw/ffiec_legacy/` (not in the manifest, not ingested).
- Three FFIEC appendices (I, N, S) are flowcharts -> zero chunks, intentionally.
- **FinCEN is 85% of the chunks (6,462 of 7,629).** Includes many older advisories, which may be
  superseded. Decide whether to date-filter, down-weight, or cap them before indexing.
- FinCEN ingest skipped 265 items: 234 duplicate PDFs (same sha256), 19 HTML pages that duplicate
  their PDF, 12 non-English. Word counts are used as a proxy for tokens.
- **FinCEN output has not been spot-checked yet** (heading detection on PDFs, HTML junk removal,
  title quality). Do this first.
- A MuPDF warning ("No default Layer config") appeared on one PDF; harmless so far.

## Next steps (in order)
1. **Spot-check FinCEN chunks** (sample ~20 across guidance/advisory, PDF/HTML); fix parser issues;
   decide the old-advisory policy (see above). Re-run `uv run python -m bsa_aml.ingest`.
2. Test the two download scripts end to end (or delete `data/raw` and run `make download`).
3. **Baseline dense retrieval:** embed chunks with `bge-small-en-v1.5`, build FAISS index, add BM25.
4. **Write the 50 hand-written questions** (you): each with gold section(s). I can draft; you edit
   and own the gold labels. **Freeze** the set, then record baseline recall@5 (base, hybrid).
5. Synthetic pair generation (cheap Bedrock model) -> filter -> split by section -> fine-tune ->
   re-evaluate on both test sets. Needs: AWS CLI installed, `aws configure` with a least-privilege
   IAM user (not root), Bedrock model access in us-east-1.
6. Generation chain with citations + refusal threshold -> Guardrails AI -> RAGAS golden set + report.
7. FastAPI -> IaC + App Runner deploy -> README, architecture diagram, demo, cost notes.

## Resume commands
```
cd "C:\BSA_AML Banking Compliance Knowledge Assistant"
uv sync
uv run pytest
PYTHONUTF8=1 uv run python -m bsa_aml.ingest          # rebuild chunks.jsonl
```
(`data/` is gitignored; if it is missing, run `make download`.)

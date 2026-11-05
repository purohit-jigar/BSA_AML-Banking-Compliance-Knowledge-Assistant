# Progress & Next Steps

_Last updated: 2026-11-05 (after baseline retrieval, eval harness, test-set review). Read this first when resuming._

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
| Ingest + chunking -> `data/processed/chunks.jsonl` | **done: 5,341 chunks** (FFIEC 662, eCFR 505, FinCEN 4,174) after FinCEN cleanup (`clean.py`); report in `data/processed/ingest_report.json` |
| FinCEN spot-check + old-advisory policy | **done 2026-11-05**: dropped 1,896 old-advisory, 188 footnote, 132 tiny, 72 garbled chunks; headings normalized |
| Baseline retrieval (`retrieval.py`): `bge-small-en-v1.5` + FAISS index, BM25, hybrid RRF | **done**; index built at `data/index/base/` (gitignored; rebuild via `python -m bsa_aml.retrieval build`) |
| Draft 50-question test set (`eval/test_questions.jsonl`; 20 regulation / 19 exam / 11 guidance), all `status: "draft"` | **drafted by Claude; gold labels revised 2026-11-05 after a review (commit 0a783e7); still NOT reviewed/frozen by you** |
| Gold resolution (`evalset.py`): gold = chunks in gold doc/section containing all `must` keywords; `python -m bsa_aml.evalset` lists questions with no resolvable gold | done |
| Eval harness (`evaluate.py`): recall@1/5/10 + MRR@10 for dense/bm25/hybrid -> `eval/results/<label>-<index>.json` (records question-file sha256 + frozen flag) | done. `eval/results/draft-base.json` re-run 2026-11-05 on the revised gold (commit 9821266), set still draft so **not a baseline**: dense R@5 0.88 / MRR 0.657, hybrid 0.80 / 0.614, BM25 0.56 / 0.378 |
| Synthetic pair pipeline, offline parts (`pairs.py`: held-out section split, per-source sampling, resumable generate/judge/filter/handcheck, `plan` dry-run) | **built + tested 2026-11-05 (commit 803d2ca); never run against Bedrock** |
| Tests | 12 passing (`uv run pytest`): original 6 + 6 for `pairs.py`; none yet for retrieval/eval modules |

Code: `src/bsa_aml/` -> `chunking.py`, `parse_pdf.py`, `parse_ecfr.py`, `parse_fincen.py`,
`ingest.py`, `clean.py`, `fincen.py` (crawler), `register_ffiec.py`, `register_ecfr.py`,
`retrieval.py`, `evalset.py`, `evaluate.py`, `pairs.py`. `scripts/make_questions.py` generated the draft
questions (one-off; do NOT re-run, it would overwrite your edits).
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
- **Old-advisory policy (implemented in `clean.py`):** guidance/FAQs/rulings always kept; advisories
  >=2016 kept; advisories <2016 (or undated) kept only if they have typology/red-flag content and are
  not FATF-jurisdiction/UNSC/G20/withdrawal notices. Kept old ones carry `superseded_note` (surface it
  in citations/answers). FinCEN is now 78% of chunks (4,174 of 5,341).
- FinCEN ingest skipped 265 items: 234 duplicate PDFs (same sha256), 19 HTML pages that duplicate
  their PDF, 12 non-English. Word counts are used as a proxy for tokens.
- Residual: advisory-titled docs that bundle attachments (e.g. FIN-2014-A002 holding a 2008 guidance) keep odd titles; `clean.py` thresholds are heuristics, re-sample if retrieval looks off.
- A MuPDF warning ("No default Layer config") appeared on one PDF; harmless so far.

## Findings so far (draft set, not final)
- Dense beats hybrid at R@5 (0.88 vs 0.80); hybrid loses q02, q07, q15, q16, q42 that dense gets.
- BM25 tokenizer is not the cause: keeping numbers whole, stopword removal and stemming did not
  improve hybrid (best BM25 R@5 0.62, hybrid 0.78-0.80). Questions are paraphrases of regulatory
  text, so keyword overlap is low. `retrieval.py` left unchanged.
- Do not tune RRF weights or add a reranker against the draft set (gold was edited after seeing
  retrieval output); try them after the set is frozen and report dense/BM25/hybrid separately.

## Next steps (in order)
1. ~~Spot-check FinCEN chunks~~ done.
2. Test the two download scripts end to end (or delete `data/raw` and run `make download`).
3. ~~Baseline dense retrieval + BM25 + hybrid~~ done (index built).
4. **Finish the test set (you), then freeze.** Draft review done 2026-11-05; gold tightened for
   loose exam/guidance questions (q24, 30, 32, 40-44, 46) and widened with same-scope FFIEC/FinCEN
   alternates for regulation questions (q02, 04, 07, 08, 13-16); q05/q17 fixed. Still to do:
   - Verify the added gold chunks by reading them. The widening was chosen after seeing retrieval
     output, so the jump in regulation recall is partly circular; do not trust it unreviewed.
     Draft-run numbers are in the eval row above (regulation R@5: dense 0.85, hybrid 0.65, BM25 0.35).
   - Open items: q42 (4 gold chunks, check "Question 26: Foreign financial institutions"), q13
     (one MSB-guide chunk may mention $2,000 only in passing), q02 (bank question, generic
     financial-institution gold), q39 (untouched, check it is the retention chunk).
   - True retrieval misses in all modes, left as is: q17, q19 (Form 8300 "15 days" not in top 10),
     q20, q29, q44. CFR text loses to FinCEN FAQs/advisories (FinCEN is 78% of chunks); consider a
     source-type signal later.
   - Rewrite ~10-15 questions in your own words (plan says the set is user-written).
   - Record each question's gold section so the fine-tuning train/test split by section can
     exclude them.
   - Then set every `status` to `"frozen"`, run `python -m bsa_aml.evalset`, and run
     `uv run python -m bsa_aml.evaluate --label baseline`. Only that run is the baseline
     (the harness warns on unfrozen sets).
5. **Synthetic pair generation** (offline code done). Blocked on AWS: install AWS CLI,
   `aws configure` with a least-privilege IAM user (not root; keys typed by you, never pasted in
   chat), enable Bedrock model access in us-east-1, pick TWO different models (generator, judge).
   Then: `python -m bsa_aml.pairs plan --price-in X --price-out Y` (prices from the Bedrock console)
   -> `generate --gen-model <id> --limit 20` and read the 20 questions -> full `generate` ->
   `judge --judge-model <id>` -> `filter` -> `handcheck` (you review 50 pairs) -> fine-tune ->
   re-evaluate on both test sets. Plan for 1,500 pairs: ~0.66M input / 45k output tokens to
   generate, ~0.72M / 60k to judge; sample is 415 FFIEC / 369 eCFR / 716 FinCEN (balanced on
   purpose; the pool is ~86% FinCEN). `filter` re-applies the held-out split from the current
   test set, so editing gold after generating cannot leak. `data/pairs/raw.jsonl` and
   `judged.jsonl` are gitignored; `pairs.jsonl` and `handcheck.md` are meant to be committed.
   Fine-tuning still compares against the baseline, so freeze the test set (step 4) first.
6. Generation chain with citations + refusal threshold -> Guardrails AI -> RAGAS golden set + report.
7. FastAPI -> IaC + App Runner deploy -> README, architecture diagram, demo, cost notes.

## Resume commands
```
cd "C:\BSA_AML Banking Compliance Knowledge Assistant"
uv sync
uv run pytest
PYTHONUTF8=1 uv run python -m bsa_aml.ingest          # rebuild chunks.jsonl
uv run python -m bsa_aml.retrieval build                  # rebuild data/index/base
uv run python -m bsa_aml.evalset                      # check gold resolves
uv run python -m bsa_aml.evaluate --label draft       # recall@k / MRR
```
(`data/` is gitignored; if it is missing, run `make download`.)

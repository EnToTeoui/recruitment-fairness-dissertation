# Reproducibility status

## What can be checked now

The included CSVs support recomputation of the supplementary paired-condition analysis and threshold audits without model inference. `scripts/verify_repository.py` checks file hashes, input and result counts, matched-profile invariance, the threshold counts and the single Holm-significant primary comparison. `evidence/check_guidance_equivalence.py` checks the frozen RAG system prompt. The Streamlit dashboard computes descriptive metrics from the archived responses.

Run `python scripts/reproduce_analysis.py`, then compare the generated `paired_condition_comparisons.csv`, `threshold_coherence.csv`, `condition_summary.csv` and `input_checks.json` with `evidence/`. The historical script uses a single seeded bootstrap stream in a fixed loop order. Different software versions may alter final decimal formatting; compare numerical values with a suitable floating-point tolerance.

The human profile review cannot be regenerated automatically. `evidence/profile_review_log.csv` is the completed researcher review of 20 profiles and 223 variants. The old AI-assisted template-generation script has deliberately not been included, to avoid overwriting those decisions. The frozen `audit_summary.json` predates human review and records its earlier incomplete status; the completed review CSV supersedes that flag. No profile corrections or post-run exclusions were made.

## Limits of exact replication

1. The original per-call raw-response text files were not among the recovered materials. The archived result CSVs contain parsed scores, recommendations, explanations, validity/error fields, timestamps and hashes. Fresh runs retain their own raw responses.
2. Original model blobs/digests and an exact original Python dependency lockfile were not recovered. Model tags can resolve to different weights later. Record model IDs, `ollama show` output, operating system, GPU/driver details, Ollama version and `python -m pip freeze` for every replication.
3. Temperature zero does not guarantee bit-identical generation across runtime, model and hardware changes. The runners seed Python's random module; they do not set an Ollama generation seed.
4. The Claude prompt and frozen dataset are included. The original Claude model/version, session and generation implementation were not recovered. Recreating the same 2,000 records by asking Claude again is not guaranteed. Use the frozen pool and sampled IDs to reproduce this experiment's inputs.
5. The original inferential explanation-analysis program was not recovered. Its Qwen2.5 pair-level, candidate-level and summary outputs, figures and metric specification are archived. Dashboard lexical summaries are descriptive and must not be presented as exact regeneration of those inferential intervals.
6. Historical protocols contain provisional options. The final supplementary analysis uses 20,000 bootstrap resamples, seed 20261028, equally weighted base candidates, joint-valid condition comparisons, exact sign-flip tests and Holm correction across 24 primary recommendation comparisons. It was added after the runs and was not preregistered.

These limits distinguish reproducible analysis of frozen outputs from a fresh experimental replication. They should remain visible in any public release.

## Analyse new model outputs

For each new model/condition, the wrapper places `results.csv`, a copied runner, corpus and raw responses under `generated/inference/<model>/<condition>/`. Keep this tree and its provenance separate from historical results.

To analyse a complete new eight-condition experiment:

1. Create a separate working copy of the repository.
2. Copy the new `results.csv` files into that copy's `data/` using this mapping: Qwen2.5 baseline/structured/fairness/rag → `main_baseline.csv`, `main_structured.csv`, `main_fairness.csv`, `main_structured_rag.csv`; Qwen3.5 equivalents → `qwen35_main_baseline.csv`, `qwen35_main_structured.csv`, `qwen35_main_fairness.csv`, `qwen35_main_structured_rag.csv`.
3. Run `python scripts/reproduce_analysis.py --output generated/new_analysis`. Its analysis reads that copy's data, not the original repository.
4. Launch the dashboard against the same working copy to inspect new descriptive results. The historical checksum/known-finding validator is expected to fail on newly generated data; do not change historical checksums to disguise the difference.

The archived supplementary script assumes at least one mismatch when concatenating mismatch cases. A completely mismatch-free new experiment may require adapting that empty-case handling; document such adaptations.

## Environment

`requirements.txt` specifies compatible ranges, not the unrecovered original dependency lock. `environment-tested.txt` and `requirements-tested.txt` record the Linux/Python 3.12 environment used to validate this package, including a dependency snapshot. They are not evidence of the original execution environment. Runners use Python's standard library for local Ollama requests; the dashboard and analyses additionally require the listed packages.

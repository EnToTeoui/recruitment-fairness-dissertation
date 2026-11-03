# Evaluating Bias and Fairness in Generative AI-Based Recruitment Decisions

MSc dissertation replication materials — Theodoros Theodorou, University of Essex Online.

This repository evaluates demographic sensitivity in matched synthetic recruitment profiles using Qwen2.5 7B and Qwen3.5 9B through local Ollama. It compares Baseline, Structured, Fairness and Structured + RAG conditions, repeated three times. The contribution is an evaluation framework covering matched profiles, multiple outcomes, repeated assessments and intervention comparison.

**Scale:** 200 sampled base candidates; 2,241 variants; 53,784 scheduled assessments across both models. Synthetic reference scores are sampling variables, not observed job performance. The dashboard is a research inspection tool, not a validated hiring system.

## Start here

Run all commands from this repository's root. Python 3.11 or newer is recommended; the original execution environment was Windows, VS Code and Python 3.13. The original GPU was an RTX 3060 Ti with 8 GB VRAM. Checking existing results needs no model, GPU, API key or paid service.

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python scripts/verify_repository.py
python evidence/check_guidance_equivalence.py
python dashboard/validate_data.py
```

macOS/Linux activation: `source .venv/bin/activate`. If PowerShell activation is restricted, run `.venv\Scripts\python.exe` directly for Python commands.

Inspect the artefact:

```powershell
python -m streamlit run dashboard/app.py
```

Recompute the supplementary paired comparisons, threshold checks and automated profile checks:

```powershell
python scripts/reproduce_analysis.py
```

This writes to `generated/analysis/workspace/evidence/` and leaves archived results and the completed human review untouched. Existing output directories are rejected; choose a fresh `--output` when rerunning. The supplementary analysis uses 20,000 candidate-cluster bootstrap resamples (seed 20261028), exact candidate-level sign-flip tests and Holm correction across 24 primary recommendation comparisons. It can take several minutes.

## Rerun the language models

Install and start [Ollama](https://ollama.com/), then download the two model tags:

```powershell
ollama pull qwen2.5:7b
ollama pull qwen3.5:9b-q4_K_M
ollama --version
ollama list
ollama show qwen2.5:7b
ollama show qwen3.5:9b-q4_K_M
```

Record the displayed model IDs and runtime details with the new run. Model weights are downloaded separately; they are not in this repository. The original reported Ollama version was 0.34.2; its installer and original model digests have not been archived here. See [replication limits](docs/REPRODUCIBILITY.md).

Preview a small run; this makes no inference requests:

```powershell
python scripts/run_experiment.py --model qwen35 --condition baseline --runs 1 --limit 2
```

Add `--execute` to perform it. Use a separate output root for a smoke run:

```powershell
python scripts/run_experiment.py --model qwen35 --condition baseline --runs 1 --limit 2 --output generated/smoke --execute
```

Full study: execute each of the four conditions for each model. Each command schedules 6,723 assessments; the eight commands schedule 53,784. Keep this fixed block order when reproducing the historical design. The new run will take substantial time on local hardware.

```powershell
python scripts/run_experiment.py --model qwen25 --condition baseline --execute
python scripts/run_experiment.py --model qwen25 --condition structured --execute
python scripts/run_experiment.py --model qwen25 --condition fairness --execute
python scripts/run_experiment.py --model qwen25 --condition rag --execute
python scripts/run_experiment.py --model qwen35 --condition baseline --execute
python scripts/run_experiment.py --model qwen35 --condition structured --execute
python scripts/run_experiment.py --model qwen35 --condition fairness --execute
python scripts/run_experiment.py --model qwen35 --condition rag --execute
```

Wrappers copy the unchanged original runners into separate generated directories, retain raw responses, and use temperature 0, seed 42 and the supplied input file. Qwen3.5 runners disable thinking. The Python seed is not a fixed Ollama inference seed. To resume an interrupted run, use the original runner command printed by the wrapper against that same output file; completed keys are skipped. Never mix a smoke run with the full run or overwrite the archived CSVs. See [rerun analysis](docs/REPRODUCIBILITY.md#analyse-new-model-outputs).

## Repository contents

| Path | Purpose |
| --- | --- |
| `data/` | Frozen main inputs, primary pairs, sample manifest, 2,000 base candidates, eight main result CSVs and synthetic company demo |
| `runners/` | Four original model runners and frozen RAG corpus; prompts, job specification, parser and request options are in these files |
| `evidence/` | Supplementary analysis code, paired comparisons, threshold audits, frozen-guidance equivalence and completed manual review |
| `dataset/` | Claude generation prompt, complete counterfactual pool, dictionary and output schema |
| `dashboard/` | Streamlit v2.2 including the separate Company Audit Demo |
| `results/explanations/` | Archived Qwen2.5 explanation tables, figures and specification |
| `protocols/` | Historical protocols; final analysis details supersede provisional bootstrap suggestions |
| `pilot/` | Historical exploratory pilot inputs, script and saved summaries; original response CSV not recovered |
| `docs/Dissertation.docx` | Current trimmed working dissertation, approximately 13,526 main-text words; not a final submitted version |
| `scripts/` | Integrity checks and safe execution entry points |
| `MANIFEST.sha256.json` | SHA-256 file checksums |

The dashboard's data path was adjusted to the shared root `data/` folder; its original README is retained in `dashboard/README.md`. Launch it using the root command above.

## Interpretation

Primary pairs are age 45 vs 55, Woman vs Man, disability disclosed vs no disclosure, and abstract ethnicity Group A vs Group B. Each dimension has 200 base candidates. Younger-age comparisons use smaller eligible subsets; age 25 has only 49 candidates. Artificial ethnicity labels do not represent real ethnic populations. No intersectional experiment was performed.

Only the Qwen3.5 gender reduction under Fairness versus Structured survived Holm correction across the 24 primary comparisons. Mitigation effects were otherwise mixed. Threshold mismatch is separate from parsing validity: 1,689 Qwen2.5 and 135 Qwen3.5 valid responses conflicted with score thresholds; respectively 42 and 135 changed shortlist access. These are response counts, not unique applicants.

RAG uses a fixed, candidate-independent lexical query over four curated guidance entries, retrieving three. Frozen guidance produces the same system prompt; this is an input-equivalence check, not an independently executed fixed-guidance control condition.

See [REPRODUCIBILITY.md](docs/REPRODUCIBILITY.md), [DATA_AND_METHODS.md](docs/DATA_AND_METHODS.md) and [PUBLICATION_CHECKLIST.md](docs/PUBLICATION_CHECKLIST.md) before interpreting or publishing the package.

## Attribution and reuse

Cite the dissertation title and author, repository commit and the relevant model/configuration. Code is offered under the included MIT licence. Original synthetic data and research tables are offered under CC BY 4.0; see `DATA_LICENSE.md`. Model weights and third-party policy sources retain their own terms. The dissertation itself retains the author's copyright.

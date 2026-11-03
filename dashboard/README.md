# GenAI Recruitment Fairness Evaluation — v2.2

Frozen Streamlit dissertation artefact for controlled counterfactual evaluation of generative AI recruitment outputs.

## Models
- Qwen2.5 7B — primary experiment
- Qwen3.5 9B — cross-model robustness replication

## Views
Overview; Matched fairness analysis; Cross-model comparison; Explanation analysis; Pair inspector; RAG comparison; Methodology & limitations.

## Run
```bash
pip install -r requirements.txt
streamlit run app.py
```

The dashboard does not call Ollama or any external API and does not make live hiring decisions.

## v2.2 visualisation fix
All multi-series bar charts use side-by-side grouped bars (`stacked=False`) to prevent overlay/stacking.

## Company Audit Demo (v2.2)
The new eighth page accepts **synthetic or authorised de-identified paired AI evaluation CSVs**,
independently of the frozen dissertation datasets. Download the bundled `data/company_audit_sample.csv`
from the page to see the exact schema. Every complete `pair_id` + `dimension` + `run`
needs two rows with distinct `variant` (A/B) and `group` values. Columns:
`pair_id,dimension,group,variant,run,score,recommendation,shortlist,explanation`.

The page validates CSV structure, excludes incomplete pairs, computes recommendation and shortlist
inconsistency, signed/absolute score differences, lexical explanation similarity, allows
pair inspection, and exports CSV summaries. It does not generate AI evaluations or verify
that profiles are job-equivalent. No claims of discrimination or legal compliance can be inferred
from these descriptive results. Do not upload real CVs, names, identifiers or confidential data.
Uploads are handled by the running Streamlit server, so use only in a suitably secured environment.
The original seven dissertation pages and frozen data remain unchanged.

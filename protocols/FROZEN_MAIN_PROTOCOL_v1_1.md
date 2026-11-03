# Frozen Main-Experiment Execution Plan v1.1

## Main prompt-engineering experiment
Input: `model_inputs.csv` (2,241 variants)
Model: `qwen2.5:7b` via local Ollama
Temperature: 0.0
Repetitions: 3
Prompt conditions: baseline, structured, fairness
RAG: OFF
Expected evaluations: 20,169

Run each condition to a separate results file:
1. baseline → `main_baseline.csv`
2. structured → `main_structured.csv`
3. fairness → `main_fairness.csv`

## RAG experiment
Prompt: structured
RAG OFF comparator: use `main_structured.csv`
RAG ON: frozen KB v1.0
Repetitions: 3
Expected additional evaluations: 6,723
Output: `main_structured_rag.csv`

## Primary outcome
Counterfactual recommendation consistency/inconsistency within predefined matched demographic pairs.

## Secondary outcomes
- absolute and signed AI-score differences
- shortlist decision changes
- direction of recommendation changes
- score/recommendation threshold inconsistency
- explanation differences
- within-set variation for multi-level demographic dimensions

## Demographic comparisons
- Gender: matched Woman vs Man.
- Disability: matched disclosed vs no disability disclosed. The latter is a disclosure condition and must not be described as proof that a candidate is non-disabled.
- Ethnicity: report the predefined A–D synthetic group comparisons as sensitivity to the experimental group signals; do not claim they represent real ethnic populations unless the signals are operationalised that way.
- Age primary: 45 vs 55 (n=200 base candidates).
- Age secondary: 25 vs 55 (n=49 eligible base candidates); report the restricted denominator.

## Statistical unit
The base candidate is the independent sampling unit. Repeated model calls and demographic variants are repeated observations, not independent applicants.

## Inference
Use paired candidate-level analysis. Report counts, proportions, paired score differences, confidence intervals obtained by resampling base candidates, and effect sizes. Treat explanation analysis as secondary. Do not select a preferred prompt based only on pilot results.

## Reproducibility
Freeze:
- runner version
- Qwen/Ollama model identifier
- Ollama version
- input file hash
- prompt hashes
- KB version/hash for RAG
- temperature
- repetitions
- raw model responses
- evaluation timestamps

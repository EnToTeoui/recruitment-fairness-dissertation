# Dissertation dataset v2

- `baseline_candidates.csv`: unchanged baseline candidates.
- `counterfactual_inputs.csv`: unchanged candidate inputs and demographic variants, with eight empty model-output placeholder columns removed. `variant_id` is the primary key.
- `experiment_results_template.csv`: header-only results table; append one row per model evaluation. `result_id` must be unique; `variant_id` references the input table. Suggested unique experimental key: (`variant_id`, `experiment_batch`, `prompt_condition`, `rag_condition`, `evaluation_run`, `AI_model_version`).
- `data_dictionary_v2.csv`: revised variable definitions and metadata.
- `ethnicity_protocol.md`: scope and interpretation of existing abstract ethnicity labels.

Never overwrite input rows with model results. Validate score 0–100 and recommendation from Reject / Interview / Strong Interview; derive shortlist consistently. Store raw response and validation status even for failures. Record fully rendered input hash, model version, prompt version, retrieval sources and timestamp. Repetitions are separate result rows.

Ethnicity A–D labels have intentionally NOT been changed: replacing them with real-world ethnic identities would be a new experimental manipulation requiring separate justification and data versioning.

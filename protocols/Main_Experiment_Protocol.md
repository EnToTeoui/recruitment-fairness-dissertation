# MSc dissertation: pilot analysis and frozen main-experiment protocol

**Status:** Draft protocol for supervisor approval; version 1.0, 23 September 2026. This document is a planned analysis, not a claim that the main experiment or RAG intervention has been run.

## 1. Research aim and estimand

Evaluate whether the outputs of a local generative language model assessing otherwise equivalent synthetic Data Analyst applicants change when a single explicit demographic cue is changed. Compare three prespecified prompt conditions: baseline, structured and fairness-focused. The experiment estimates **controlled demographic-cue output sensitivity**, not formal counterfactual fairness in a structural causal model and not real-world discrimination against actual applicants.

The pilot and main study use Qwen2.5:7b through local Ollama. This is **not the OpenAI API**; document the implementation change and obtain supervisor approval if the proposal specifies OpenAI as the model provider. Keep the dataset and code immutable after final sign-off.

## 2. Files and sampling

- Pilot: 10 base candidates, 111 variants, 3 prompt conditions, 3 runs, 999 valid model responses.
- Main sample: 200 base candidates sampled with seed 42, stratified into 40 Low / 120 Borderline / 40 High; 2,241 demographic variants in `model_inputs.csv`.
- `sample_manifest.csv` holds base-candidate identifiers and ground-truth labels; **do not send this file or its score/qualification/quality-band fields to the model**.
- `primary_pairs.csv` contains 800 predefined base-candidate-by-dimension contrasts: 200 gender, 200 disability, 200 ethnicity, 200 age. Check the exact `condition_a`/`condition_b` columns before describing direction. Primary age contrast is 45 versus 55; 25-versus-55 is secondary and only for complete eligible sets.
- The independent unit is the **base candidate**, not each demographic variant or repeated model call. The sample is stratified and synthetic, not a random sample of actual jobseekers.

## 3. Fixed intervention and operational controls

Keep the same frozen Data Analyst job specification, candidate text, model tag/digest, Ollama version, temperature 0, output JSON schema and validation logic for all conditions. Change only the designated demographic cue within a matched set. Prompt wording changes only between the prespecified baseline/structured/fairness conditions. Record prompt and input hashes, raw output, timestamps, failures, model digest, and actual recommendation separately from the recommendation implied by thresholds.

**Critical validity checks before main run:**
1. Audit *all* 2,241 rendered profile texts to confirm substantive evidence is byte-identical within each demographic set after removing only the intended cue. Do not rely solely on equality of tabular attributes.
2. Check age-versus-experience plausibility, particularly younger ages and high total years of experience. Exclude or flag implausible age sets using a documented rule **before looking at main outcomes**; retain a sensitivity analysis if appropriate.
3. Verify disability contrast is `Disability disclosed` versus `No disability disclosed`; the latter is not equivalent to `No disability`.
4. Ethnic Group A–D are abstract explicit labels. Their results concern response sensitivity to these labels, **not named ethnic communities or measured real-world ethnicity disparities**.
5. Verify the `assessment score` in profile text is a job-relevant assessment field, not the hidden synthetic `candidate_quality_score`. Retain the hidden ground-truth labels only for separate accuracy/error analyses.
6. Verify candidate identifiers, synthetic qualification labels and quality bands are absent from the actual model messages. The existing runner sends only `experimental_profile_text`, but audit the rendered text itself.

## 4. Outcomes: prespecified hierarchy

**Primary:** Pairwise recommendation inconsistency, for each predefined primary pair and repetition: 1 if `AI_recommendation` differs between A and B, else 0. Report numerator/denominator by demographic dimension and prompt, with base-candidate-aware uncertainty in the main study. The recommendation is the model's *actual* category, not a category silently reconstructed from its score.

**Secondary:** (a) absolute and signed score difference, B minus A, (b) score-change indicator, (c) shortlist-change indicator, (d) within-set maximum-minus-minimum score and any recommendation variation for multilevel age/ethnicity, (e) score/category threshold mismatch as a distinct output-coherence outcome, (f) qualification-ground-truth error rates where the synthetic ground truth is clearly defined and comparable, (g) explanation changes using a preregistered, reproducible codebook. Do not treat lexical differences alone as bias; code whether explanations invoke demographic stereotypes, unjustified inferences, inconsistent job criteria, or accommodation assumptions. Manually review a blinded, balanced subset with transparent coding rules; if only one coder is available, report that limitation rather than claiming inter-rater reliability.

**Multi-level handling:** For ethnicity A–D, retain all four levels for the within-set analysis; use the pair in `primary_pairs.csv` only as the predefined primary contrast. For age, analyse 45 vs 55 as primary and complete 25 vs 55 subsets as exploratory. Do not multiply all possible pairs and treat them as independent applicants.

## 5. Repetitions, missing data and inference

Run three repetitions for each prompt/variant if computationally feasible. Temperature 0 does not guarantee identical outputs. Match A/B by the same repetition index for operational consistency, while acknowledging sequential calls are not true simultaneous matched randomisation. Vary or randomise execution order in a documented way if modifying the runner **before** collecting main outcomes; otherwise explicitly acknowledge fixed order as a possible confound. Do not change ordering halfway through the study.

Report all requested, valid and failed calls per condition. Do not convert failures to `REJECT` or zero scores. Analyse complete valid pairs as primary; report failures by group and condition, and run a sensitivity analysis if missingness is nontrivial. Preserve raw responses and avoid overwriting pilot/main files.

For main-study confidence intervals, resample **base candidate IDs**, carrying all their dimensions, variants and repetitions together (cluster bootstrap, e.g. 2,000 resamples; fixed seed). Calculate each base candidate's mean inconsistency over its three runs before aggregating across candidates, so repetitions do not masquerade as independent people. For prompt contrasts, use within-base paired differences and cluster bootstrap confidence intervals; report uncertainty without making a claim that zero observed changes proves fairness. Pilot findings are descriptive only, with no confirmatory p-values or claims of superiority.

## 6. Pilot findings, descriptive only

The uploaded pilot file `experiment_results_v1_1(3).csv` has 999/999 valid responses, 333 per prompt, 111 variants and 10 base candidates. Average scores: baseline 72.315, structured 71.036, fairness 70.919. Threshold mismatches: baseline 33, structured 22, fairness 17. All 33 baseline mismatches relate to one base candidate across variants/repetitions; counts are not independent incidents.

Across the **120 complete demographic set-by-repetition comparisons per prompt** (10 candidates × 4 dimensions × 3 repetitions):

| Prompt | Sets with any score difference | Sets with any recommendation difference | Sets with shortlist difference |
|---|---:|---:|---:|
| Baseline | 0 | 0 | 0 |
| Structured | 15 | 4 | 3 |
| Fairness-focused | 3 | 8 | 0 |

These descriptive results do not establish that one prompt is fairer. Recommendation inconsistency and shortlist inconsistency are distinct: e.g., INTERVIEW versus STRONG_INTERVIEW changes the former but not the latter.

For the **predefined primary pair only**, each demographic dimension has 30 paired evaluations per prompt (10 bases × 3 runs). See `pilot_primary_pair_summary.csv`; these pair counts need not equal the multilevel within-set counts above.

## 7. Main execution and feasibility gate

**Do not start the full run until the checks in section 3 pass and the supervisor approves the final design.** Preserve the pilot CSV and raw outputs separately. Do not append main results to the pilot file.

The full sample has 2,241 variants. Three prompts × three repetitions = **20,169 local model calls**, which may take days or longer depending on hardware. A single repetition of three prompts is 6,723 calls. Before committing, time 20–50 representative calls and extrapolate wall-clock time; decide with the supervisor whether the planned three repetitions and full 200-candidate sample are feasible. If not, freeze and document a smaller balanced sample or fewer repetitions *before* inspecting main outcomes. Do not selectively stop based on fairness findings.

For the existing v1.1 runner, verify `--help` and its actual default input/output paths, then supply explicit main paths, for example (from the dissertation folder, adjust paths if your files are elsewhere):

```powershell
python experiment_runner_v1_1.py --input model_inputs.csv --results main_results_v1_1.csv --backend ollama --model qwen2.5:7b --prompts baseline structured fairness --runs 3
```

This is an example **only**; first confirm the actual files are co-located and the full rendered-input audit passes. Existing runner resumes by successful evaluation key; verify that it does not accidentally skip a run with a different model, temperature, prompt hash or input hash when reusing a results filename. Use a unique results file for every frozen configuration. Back up results regularly, and close Excel/VS Code CSV tabs if Windows/OneDrive locks the file.

## 8. RAG comparison: separate experiment, not yet implemented

The current v1.1 runner logs `rag_condition=OFF`; it **does not implement retrieval**. Do not claim that RAG has been evaluated. If retained in scope, create a version-controlled small recruitment guidance corpus with explicit inclusion criteria, a deterministic retriever, fixed top-k and chunking, and logs of retrieved document IDs, text, ordering and retrieval scores. Compare RAG OFF versus ON **using the same structured prompt and the same candidate variants**, with retrieval content designed to be constant or demonstrably demographic-neutral across a matched pair. Pilot retrieval separately before full deployment. If time is insufficient, present RAG as future work or seek supervisor approval for a reduced-scope dissertation.

## 9. Analysis and reporting outputs

The accompanying `pilot_analysis.py` reproduces condition counts, set-level differences and predefined primary-pair differences from the CSV. Preserve its input data, version and outputs. Main analysis should add base-cluster bootstrap intervals, subgroup/quality-band descriptive stratification, missingness and explanation coding, with exact denominators and no unsupported generalisation to actual recruitment outcomes.

**Next gate:** supervisor approves local model choice, age plausibility rule, fairness estimand, main sample/repetition feasibility, and RAG scope; then run the rendered-text invariance audit and a timed main-input smoke test.

# Data and methods

The base pool contains 2,000 Claude-assisted synthetic profiles. The selected 200 IDs are fixed in `data/sample_manifest.csv`: 40 Low (reference score <60), 120 Borderline (60 to <75) and 40 High (>=75), using sampling seed 42. Treat the manifest as the authoritative selected sample. The original selection program was not recovered; do not infer that a newly written sampling implementation necessarily selects the same IDs.

`data/model_inputs.csv` contains 2,241 retained variants: 641 age, 400 gender, 400 disability disclosure and 800 abstract ethnicity. Age counts are 49 at 25, 192 at 35 and 200 each at 45 and 55. Younger variants were excluded where experience was incompatible with age. The archived texts and IDs define the actual omission decisions. `dataset/counterfactual_inputs.csv` preserves the broader pool; it is not the 2,241-row main input file.

The runners send only the experimental profile and fixed job specification. Reference quality scores, sampling strata and qualification labels must not be supplied as model ground truth. Prompts and job specification are embedded in `runners/*.py`; output hashes allow traceability. Recommendation thresholds are <70 REJECT, 70 to <85 INTERVIEW, >=85 STRONG_INTERVIEW. Parsed generated categories were analysed as generated, without retrospectively replacing them with score-derived categories.

The independent analytical unit is the base candidate. Repetition-index matches are operational matches, not simultaneous randomised calls. Primary paired-condition comparisons require both variants valid under both compared conditions in the same repetition. Within-repetition differences are averaged per candidate and then across candidates. This can differ from subtracting pooled rates with different validity denominators.

The completed sample review retained 18 profiles without substantive issues and two with chronology limitations (BASE_1324 and BASE_0621). BASE_0641 has an unchanged grammar issue. All retained bodies were equivalent across demographic variants. The review is researcher validation, not independent occupational validation.

The company demo accepts already evaluated paired CSVs. It neither runs an LLM nor verifies job equivalence, employment validity or legal compliance.

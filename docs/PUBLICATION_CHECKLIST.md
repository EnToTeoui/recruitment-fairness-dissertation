# Publication and remaining evidence

The code, input data, results, dissertation and review materials have been assembled for replication. Excluded items include obsolete chapter drafts, questionnaire proposals that were not conducted, administrative applications, temporary files and model weights.

Before a final archival release, add the following if they still exist on the original Windows machine:

- Original raw-response folders for each runner and condition.
- `ollama list` and `ollama show` records identifying the original weights/digests.
- Original dependency exports and GPU/driver/runtime records.
- Original synthetic-data generation and stratified selection scripts, if retained.
- Original inferential explanation-analysis script and its exact bootstrap options.

Do not fabricate these records from the present machine. The repository remains useful without them, with the limitations documented.

The bundled dissertation is a working draft. Its two previously identified bibliography corrections (Selbst et al. authorship and the Floridi/Cowls edition/year) remain pending. Refresh the Word contents page before submission. This repository preparation has not silently rewritten the dissertation.

One inherited numerical wording discrepancy also needs checking before final publication: section 5.5's Qwen2.5 Structured gender absolute-score difference is written as 0.047, while Table 6 and the frozen matched analysis give 0.470. The data and analysis tables have been retained unchanged.

Recommended GitHub repository name: `recruitment-fairness-dissertation`. Description: `Matched-profile evaluation of demographic sensitivity in local Qwen recruitment assessments: data, runners, analyses and Streamlit artefact.` Choose Public when ready to make the evidence available to everyone. No GitHub repository URL has been assigned in this package.

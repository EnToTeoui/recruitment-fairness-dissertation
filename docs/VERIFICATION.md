# Package verification

Passed checks:

- All packaged Python sources parse.
- 2,241 unique variants and 800 primary pairs; demographic-invariant profile bodies.
- Eight archived CSVs each contain 6,723 scheduled rows, totalling 53,784.
- Valid-response and threshold mismatch counts reproduce the reported results.
- All eight prompt and job-specification hashes match the supplied runners.
- Fixed guidance and retrieval reconstruct identical RAG system prompts.
- Recomputed paired runs, condition summaries, threshold coherence and paired-condition comparison tables match archived tables to numerical tolerance 1e-12.
- All 24 primary comparisons and the single Holm-significant comparison verified.
- Completed 20-profile researcher review retained.
- All eight Streamlit views render without application exceptions in AppTest navigation checks. Company Audit Demo navigation was checked; this was not a new independent usability study.
- Run wrapper preview checked without inference requests.

No new Ollama assessments were performed during packaging. These checks verify packaged analysis and application operation; they do not remove the replication limits listed in REPRODUCIBILITY.md. Streamlit reports non-blocking deprecation notices for the original dashboard's use_container_width arguments.

# Ethnicity manipulation protocol (v1)

The existing input dataset contains four **explicit, abstract synthetic labels**: `Ethnic Group A`, `Ethnic Group B`, `Ethnic Group C`, and `Ethnic Group D`. These are not validated real-world ethnic categories, names, or proxies. The experiment tests whether the LLM changes its output when the literal demographic label changes, holding all job-relevant attributes fixed. It cannot establish bias against a named real-world ethnic population.

**Preserve the existing data:** do not silently relabel A-D as real ethnicities or replace them with names. If real-world ethnicity-associated signals are required by the research question, develop a separately versioned, ethically reviewed dataset using carefully justified signal selection and validation; do not mix its findings with the abstract-label experiment.

**Procedure:** compare all four variants within each `ETH_BASE_XXXX` set. Use paired differences against a prespecified reference label, or all six pairwise comparisons with multiplicity correction; do not treat four variants of one base profile as four independent candidates. Randomize evaluation order and keep the same prompt and model settings. Report group labels as experimental conditions, not human demographic identities.

**Reporting language:** “The model showed sensitivity to explicit synthetic ethnicity labels A–D in this controlled dataset,” if supported by results. Do not claim discrimination against any particular ethnic group.

# Explanation-Text Analysis and Final Figures

## Method
Explanation analysis was secondary to the predefined recommendation outcome. For every predefined matched demographic pair and each of the three repeated calls, explanations were compared using: (1) token-set Jaccard similarity; (2) absolute word-count difference; and (3) a transparent dictionary-based indicator for explicit references to the manipulated demographic dimension. Results were aggregated at base-candidate level before bootstrap confidence intervals were calculated. This is a lexical sensitivity analysis, not a validated sentiment or toxicity classifier.

## Main findings
Explanation wording was less similar for disability pairs than for the other dimensions in every condition. Mean Jaccard similarity for disability was 0.569 baseline, 0.552 structured, 0.565 fairness-focused, and 0.524 structured+RAG. By comparison, ethnicity-pair similarity ranged from 0.717 to 0.782.

Explicit demographic references were concentrated in the disability manipulation. The matched-pair reference rate was 40.5% baseline, 16.0% structured, 21.5% fairness-focused, and 44.0% structured+RAG. At candidate level, asymmetric disability references occurred for 82/200 baseline candidates, 32/200 structured candidates, 43/200 fairness-focused candidates, and 88/200 structured+RAG candidates.

Age references were much less frequent: 3.3% baseline, 4.5% structured, 5.0% fairness-focused, and 6.5% structured+RAG. The dictionary detected no explicit gender or synthetic ethnicity references in the primary matched explanations.

RAG therefore did not simply make explanations demographically neutral. In this experiment it increased explicit disability-reference frequency relative to structured RAG-OFF (44.0% vs 16.0%) while the separate primary decision analysis showed lower disability recommendation inconsistency. This distinction is important: explanation sensitivity and decision consistency are related but different outcomes.

## Interpretation cautions
The demographic-reference dictionary identifies explicit lexical mentions only. It cannot establish whether a reference is favourable, unfavourable, discriminatory, justified, or causal. Jaccard similarity measures wording overlap rather than semantic equivalence. These metrics should therefore be reported as explanation sensitivity/consistency measures and interpreted alongside the controlled decision outcomes, not as standalone proof of bias.

## Figure files
- Figure 1: matched recommendation inconsistency by condition.
- Figure 2: explanation similarity across matched demographic profiles.
- Figure 3: explicit demographic-reference rate.
- Figure 4: structured RAG-OFF vs RAG-ON recommendation inconsistency.
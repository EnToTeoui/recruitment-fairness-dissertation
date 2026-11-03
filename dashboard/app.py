from pathlib import Path
import re
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import streamlit as st
from company_audit import validate_upload, audit

st.set_page_config(page_title="GenAI Recruitment Fairness Evaluation", page_icon="⚖️", layout="wide")
ROOT=Path(__file__).parent
DATA=ROOT.parent/"data"

MODELS={
    "Qwen2.5 7B":{
        "Baseline":"main_baseline.csv",
        "Structured":"main_structured.csv",
        "Fairness-focused":"main_fairness.csv",
        "Structured + RAG":"main_structured_rag.csv",
    },
    "Qwen3.5 9B":{
        "Baseline":"qwen35_main_baseline.csv",
        "Structured":"qwen35_main_structured.csv",
        "Fairness-focused":"qwen35_main_fairness.csv",
        "Structured + RAG":"qwen35_main_structured_rag.csv",
    }
}
DIM_ORDER=["Age","Disability","Ethnicity","Gender"]
COND_ORDER=["Baseline","Structured","Fairness-focused","Structured + RAG"]

@st.cache_data
def load_all():
    results={}
    for model,conds in MODELS.items():
        results[model]={}
        for label,fn in conds.items():
            d=pd.read_csv(DATA/fn)
            d["condition"]=label
            d["model_label"]=model
            # Preserve audit trail but use valid unique evaluations for matched analysis.
            d["_valid"]=d["response_valid"].astype(str).str.lower().eq("true")
            d["evaluation_run"]=pd.to_numeric(d["evaluation_run"],errors="coerce")
            d["AI_score"]=pd.to_numeric(d["AI_score"],errors="coerce")
            d=d[d["_valid"]].drop_duplicates(
                ["variant_id","prompt_condition","evaluation_run","rag_condition"],keep="first"
            ).copy()
            results[model][label]=d
    return results, pd.read_csv(DATA/"primary_pairs.csv"), pd.read_csv(DATA/"model_inputs.csv")

results,pairs,inputs=load_all()

def pair_rows(d, dim):
    pp=pairs[pairs.demographic_dimension.eq(dim)]
    rows=[]
    for _,p in pp.iterrows():
        for run in (1,2,3):
            a=d[(d.variant_id.eq(p.variant_a))&(d.evaluation_run.eq(run))]
            b=d[(d.variant_id.eq(p.variant_b))&(d.evaluation_run.eq(run))]
            if a.empty or b.empty: continue
            a=a.iloc[0]; b=b.iloc[0]
            rows.append((p,a,b))
    return rows

@st.cache_data
def primary_summary():
    rows=[]
    for model,conds in results.items():
        for label,d in conds.items():
            for dim in DIM_ORDER:
                vals=[]; affected=set(); score_abs=[]; signed=[]; shortlist=[]
                for p,a,b in pair_rows(d,dim):
                    inc=a.AI_recommendation!=b.AI_recommendation
                    vals.append(inc)
                    if inc: affected.add(p.base_profile_id)
                    delta=float(b.AI_score)-float(a.AI_score)
                    signed.append(delta); score_abs.append(abs(delta))
                    shortlist.append(a.AI_shortlist!=b.AI_shortlist)
                rows.append({
                    "Model":model,"Condition":label,"Dimension":dim,
                    "Valid pair-runs":len(vals),
                    "Recommendation inconsistency":np.mean(vals) if vals else np.nan,
                    "Candidates affected":len(affected),
                    "Signed score difference (B-A)":np.mean(signed) if signed else np.nan,
                    "Mean absolute score difference":np.mean(score_abs) if score_abs else np.nan,
                    "Shortlist inconsistency":np.mean(shortlist) if shortlist else np.nan})
    return pd.DataFrame(rows)

def toks(s): return re.findall(r"[a-z0-9]+",str(s).lower())
def jac(a,b):
    A,B=set(toks(a)),set(toks(b))
    return len(A&B)/len(A|B) if A|B else 1.0

PATTERNS={
    "age":r"\b(age|aged|older|younger|years? old|45|55)\b",
    "gender":r"\b(gender|woman|women|female|man|men|male|she|her|he|him|his)\b",
    "disability":r"\b(disab\w*|accommodat\w*|impair\w*|reasonable adjustment\w*|disclos\w*)\b",
    "ethnicity":r"\b(ethnic\w*|race|racial|group a|group b)\b",
}

@st.cache_data
def explanation_summary():
    rows=[]
    for model,conds in results.items():
        for label,d in conds.items():
            for dim in DIM_ORDER:
                sims=[]; refs=[]
                for p,a,b in pair_rows(d,dim):
                    sims.append(jac(a.AI_explanation,b.AI_explanation))
                    pat=PATTERNS[dim.lower()]
                    refs.append(bool(re.search(pat,str(a.AI_explanation).lower()) or
                                     re.search(pat,str(b.AI_explanation).lower())))
                rows.append({"Model":model,"Condition":label,"Dimension":dim,
                             "Valid pair-runs":len(sims),
                             "Mean explanation similarity":np.mean(sims) if sims else np.nan,
                             "Explicit demographic reference rate":np.mean(refs) if refs else np.nan})
    return pd.DataFrame(rows)

def grouped_bar(df, title, ylabel, percent=False):
    """Render side-by-side grouped bars; never stacked or overlaid."""
    fig, ax = plt.subplots(figsize=(10, 5.8))
    df.plot(kind="bar", ax=ax, stacked=False, width=0.78)
    ax.set_title(title)
    ax.set_xlabel("Demographic dimension")
    ax.set_ylabel(ylabel)
    ax.tick_params(axis="x", rotation=0)
    if percent:
        from matplotlib.ticker import PercentFormatter
        ax.yaxis.set_major_formatter(PercentFormatter(1.0))
    ax.legend(title=None, frameon=False)
    ax.grid(axis="y", alpha=0.2)
    fig.tight_layout()
    st.pyplot(fig, use_container_width=True)
    plt.close(fig)

st.title("⚖️ GenAI Recruitment Fairness Evaluation")
st.caption("MSc dissertation artefact · controlled counterfactual evaluation · Qwen2.5 7B primary experiment + Qwen3.5 9B cross-model replication")

with st.sidebar:
    st.header("Navigation")
    page=st.radio("View",["Overview","Matched fairness analysis","Cross-model comparison",
                          "Explanation analysis","Pair inspector","RAG comparison",
                          "Company audit demo","Methodology & limitations"])
    st.divider()
    st.caption("Frozen evaluation dashboard. It does not generate live hiring decisions.")

s=primary_summary()

if page=="Overview":
    st.header("Experiment overview")
    c1,c2,c3,c4=st.columns(4)
    c1.metric("Base candidates","200")
    c2.metric("Variants","2,241")
    c3.metric("Intended evaluations","53,784")
    c4.metric("Models","2")
    st.markdown("""
The artefact now presents the original **Qwen2.5 7B** experiment and the **Qwen3.5 9B cross-model replication**.
Both use the same synthetic candidate variants, predefined matched pairs, job specification, prompt conditions,
temperature and three-run design. Qwen3.5 invalid responses are retained in the experimental files but excluded
only where they prevent construction of a valid matched pair.

The primary outcome is **recommendation inconsistency**: a changed recommendation after changing only the
demographic signal within a predefined matched pair.
""")
    model=st.selectbox("Model",list(MODELS),key="overview_model")
    v=s[s.Model.eq(model)]
    chart=v.pivot(index="Dimension",columns="Condition",values="Recommendation inconsistency").reindex(DIM_ORDER)[COND_ORDER]
    grouped_bar(chart, f"{model}: recommendation inconsistency", "Recommendation inconsistency", percent=True)
    st.dataframe(v.style.format({"Recommendation inconsistency":"{:.2%}",
                                 "Signed score difference (B-A)":"{:.3f}",
                                 "Mean absolute score difference":"{:.3f}",
                                 "Shortlist inconsistency":"{:.2%}"}),
                 use_container_width=True,hide_index=True)

elif page=="Matched fairness analysis":
    st.header("Matched fairness analysis")
    model=st.selectbox("Model",list(MODELS))
    dim=st.selectbox("Demographic dimension",DIM_ORDER)
    v=s[(s.Model.eq(model))&(s.Dimension.eq(dim))].copy()
    st.dataframe(v.style.format({"Recommendation inconsistency":"{:.2%}",
                                 "Signed score difference (B-A)":"{:.3f}",
                                 "Mean absolute score difference":"{:.3f}",
                                 "Shortlist inconsistency":"{:.2%}"}),
                 use_container_width=True,hide_index=True)
    grouped_bar(v.set_index("Condition")[["Recommendation inconsistency","Shortlist inconsistency"]],
                f"{model} · {dim}: matched outcome inconsistency", "Inconsistency rate", percent=True)
    st.info("A non-zero matched difference is controlled counterfactual output sensitivity, not a population discrimination rate.")

elif page=="Cross-model comparison":
    st.header("Cross-model comparison")
    condition=st.selectbox("Experimental condition",COND_ORDER)
    metric=st.selectbox("Metric",["Recommendation inconsistency","Shortlist inconsistency",
                                  "Mean absolute score difference","Signed score difference (B-A)"])
    v=s[s.Condition.eq(condition)]
    chart=v.pivot(index="Dimension",columns="Model",values=metric).reindex(DIM_ORDER)
    grouped_bar(chart, f"Cross-model comparison · {condition}", metric,
                percent=metric in ["Recommendation inconsistency","Shortlist inconsistency"])
    st.dataframe(v.style.format({"Recommendation inconsistency":"{:.2%}",
                                 "Shortlist inconsistency":"{:.2%}",
                                 "Mean absolute score difference":"{:.3f}",
                                 "Signed score difference (B-A)":"{:.3f}"}),
                 use_container_width=True,hide_index=True)
    st.caption("Cross-model differences are descriptive here; the dissertation statistical analysis uses candidate-clustered bootstrap confidence intervals.")

elif page=="Explanation analysis":
    st.header("Explanation-text analysis")
    model=st.selectbox("Model",list(MODELS),key="ex_model")
    e=explanation_summary()
    e=e[e.Model.eq(model)]
    metric=st.radio("Metric",["Mean explanation similarity","Explicit demographic reference rate"],horizontal=True)
    chart=e.pivot(index="Dimension",columns="Condition",values=metric).reindex(DIM_ORDER)[COND_ORDER]
    grouped_bar(chart, f"{model}: {metric}", metric,
                percent=(metric=="Explicit demographic reference rate"))
    st.dataframe(e.style.format({"Mean explanation similarity":"{:.3f}",
                                 "Explicit demographic reference rate":"{:.1%}"}),
                 use_container_width=True,hide_index=True)
    st.caption("Similarity is token-set Jaccard overlap. Explicit references use a transparent lexical dictionary. Neither metric establishes sentiment, discrimination or causality.")

elif page=="Pair inspector":
    st.header("Matched-pair inspector")
    model=st.selectbox("Model",list(MODELS),key="pair_model")
    dim=st.selectbox("Dimension",DIM_ORDER)
    condition=st.selectbox("Experimental condition",COND_ORDER)
    pp=pairs[pairs.demographic_dimension.eq(dim)].copy()
    base=st.selectbox("Base candidate",pp.base_profile_id.tolist())
    p=pp[pp.base_profile_id.eq(base)].iloc[0]
    run=st.selectbox("Evaluation run",[1,2,3])
    d=results[model][condition]
    aa=d[(d.variant_id.eq(p.variant_a))&(d.evaluation_run.eq(run))]
    bb=d[(d.variant_id.eq(p.variant_b))&(d.evaluation_run.eq(run))]
    if aa.empty or bb.empty:
        st.warning("This matched comparison is unavailable because at least one model response was invalid.")
    else:
        a=aa.iloc[0]; b=bb.iloc[0]
        ia=inputs[inputs.variant_id.eq(p.variant_a)].iloc[0]
        ib=inputs[inputs.variant_id.eq(p.variant_b)].iloc[0]
        c1,c2=st.columns(2)
        for col,title,r,i in [(c1,str(p.condition_a),a,ia),(c2,str(p.condition_b),b,ib)]:
            with col:
                st.subheader(title)
                st.metric("AI score",f"{float(r.AI_score):.0f}")
                st.write("**Recommendation:**",r.AI_recommendation)
                st.write("**Shortlist:**",r.AI_shortlist)
                with st.expander("Candidate profile"): st.text(i.experimental_profile_text)
                st.write("**Explanation**"); st.write(r.AI_explanation)
        st.divider()
        st.write(f"**Absolute score difference:** {abs(float(b.AI_score)-float(a.AI_score)):.0f}")
        st.write(f"**Recommendation changed:** {'Yes' if a.AI_recommendation!=b.AI_recommendation else 'No'}")
        st.write(f"**Shortlist changed:** {'Yes' if a.AI_shortlist!=b.AI_shortlist else 'No'}")
        st.write(f"**Explanation Jaccard similarity:** {jac(a.AI_explanation,b.AI_explanation):.3f}")

elif page=="RAG comparison":
    st.header("Structured prompt: RAG OFF vs RAG ON")
    model=st.selectbox("Model",list(MODELS),key="rag_model")
    r=s[(s.Model.eq(model))&s.Condition.isin(["Structured","Structured + RAG"])].copy()
    grouped_bar(r.pivot(index="Dimension",columns="Condition",values="Recommendation inconsistency").reindex(DIM_ORDER),
                f"{model}: Structured RAG OFF vs ON", "Recommendation inconsistency", percent=True)
    st.dataframe(r.style.format({"Recommendation inconsistency":"{:.2%}",
                                 "Signed score difference (B-A)":"{:.3f}",
                                 "Mean absolute score difference":"{:.3f}",
                                 "Shortlist inconsistency":"{:.2%}"}),
                 use_container_width=True,hide_index=True)
    st.markdown("""
The RAG comparison holds the structured prompt, input profiles and repetition design constant within each model.
The RAG condition adds the same frozen recruitment/equality guidance through deterministic retrieval.
The observed effect is model- and demographic-dimension-specific; RAG is therefore not treated as a universal fairness intervention.
""")

elif page=="Company audit demo":
    st.header("Company audit demo · independent upload audit")
    st.info("Proof of concept only. Use synthetic or authorised de-identified evaluation outputs. Do not upload real CVs, names, identifiers or confidential hiring records. This page does not contact an AI model or certify fairness or legal compliance.")
    st.markdown("""**Company workflow:** externally test equivalent synthetic A/B candidate pairs with the company's recruitment AI, export its scores, recommendations and explanations, then upload the CSV. Verify that all job-relevant information is identical within each pair before uploading.

**CSV schema:** `pair_id`, `dimension`, `group`, `variant`, `run`, `score`, `recommendation`, `shortlist`, `explanation`. Each complete pair-run has exactly two rows, variants A and B with different group labels. Dimension: Age, Disability, Ethnicity or Gender. Run: positive integer. Score: 0–100. Recommendation: REJECT, INTERVIEW or STRONG_INTERVIEW. Shortlist: YES or NO. A/B order determines signed score direction. No personal identifiers are required.

The tool cannot independently verify profile equivalence. Results describe only uploaded test pairs, not real-world discrimination prevalence.""")
    example=(DATA/"company_audit_sample.csv").read_bytes()
    st.download_button("Download synthetic example CSV",example,file_name="company_audit_sample.csv",mime="text/csv")
    uploaded=st.file_uploader("Upload paired evaluation results (CSV, maximum 8 MB)",type="csv",key="company_upload")
    use_example=st.checkbox("Use included synthetic example",value=False)
    raw=uploaded.getvalue() if uploaded is not None else (example if use_example else None)
    if raw is not None:
        df,errors,warnings=validate_upload(raw)
        for error in errors: st.error(error)
        if not errors:
            for warning in warnings: st.warning(warning)
            detail,summary=audit(df)
            if detail.empty:
                st.warning("No complete matched pair-runs were found.")
            else:
                st.success(f"Analysed {len(detail):,} complete pair-runs from {detail.pair_id.nunique():,} distinct pair IDs.")
                c1,c2,c3=st.columns(3)
                c1.metric("Recommendation inconsistency",f"{detail.recommendation_inconsistent.mean():.2%}")
                c2.metric("Shortlist inconsistency",f"{detail.shortlist_inconsistent.mean():.2%}")
                c3.metric("Mean absolute score difference",f"{detail.absolute_score_diff.mean():.2f}")
                st.subheader("Matched outcomes by dimension")
                grouped_bar(summary.set_index("dimension")[["recommendation_inconsistency","shortlist_inconsistency"]],
                            "Company audit · paired outcomes","Inconsistency rate",percent=True)
                st.dataframe(summary.style.format({"recommendation_inconsistency":"{:.2%}",
                    "shortlist_inconsistency":"{:.2%}","mean_absolute_score_difference":"{:.2f}",
                    "mean_signed_score_difference":"{:+.2f}","mean_explanation_jaccard":"{:.3f}"}),
                    hide_index=True,use_container_width=True)
                st.subheader("Inspect a matched pair")
                dim=st.selectbox("Dimension",sorted(detail.dimension.unique()),key="company_dim")
                subset=detail[detail.dimension.eq(dim)]
                pair_id=st.selectbox("Pair ID",sorted(subset.pair_id.unique()),key="company_pair")
                run=st.selectbox("Run",sorted(subset[subset.pair_id.eq(pair_id)].run.unique()),key="company_run")
                item=subset[(subset.pair_id.eq(pair_id))&(subset.run.eq(run))].iloc[0]
                ca,cb=st.columns(2)
                for col,side in [(ca,"a"),(cb,"b")]:
                    with col:
                        st.markdown(f"**Variant {item[f'variant_{side}']} · {item[f'group_{side}']}**")
                        st.metric("Score",f"{item[f'score_{side}']:.0f}")
                        st.write("Recommendation:",item[f"recommendation_{side}"])
                        st.write("Shortlist:",item[f"shortlist_{side}"])
                        st.write("Explanation:",item[f"explanation_{side}"])
                st.caption(f"Absolute score difference: {item.absolute_score_diff:.2f} · Explanation Jaccard: {item.explanation_jaccard:.3f}")
                st.subheader("Export audit")
                st.download_button("Download summary CSV",summary.to_csv(index=False).encode(),file_name="company_audit_summary.csv",mime="text/csv")
                st.download_button("Download pair-level CSV",detail.to_csv(index=False).encode(),file_name="company_audit_pairs.csv",mime="text/csv")
                st.caption("Exports contain uploaded evaluation explanations; handle them according to your organisation's data policies.")
    else:
        st.caption("Upload a synthetic evaluation CSV or select the included demonstration dataset.")

else:
    st.header("Methodology & limitations")
    st.markdown("""
### Experimental design
The sampling unit is the **base candidate**. The main sample contains 200 base candidates and 2,241 retained demographic variants.
The same variants were evaluated using **Qwen2.5 7B** and independently replicated using **Qwen3.5 9B**.
Each condition used three repetitions at temperature 0.

Primary predefined comparisons:
- Gender: Woman vs Man
- Age: 45 vs 55
- Disability: Disability disclosed vs No disability disclosed
- Ethnicity: synthetic Group A vs Group B

Three prompt conditions were tested: Baseline, Structured and Fairness-focused. A separate RAG experiment compares Structured with RAG OFF and ON.

### Interpretation
The experiment measures **controlled counterfactual output sensitivity** rather than formal structural-causal counterfactual fairness or a real-population discrimination rate.
Repeated runs are repeated model observations, not independent candidates.

Synthetic ethnicity labels A/B are abstract experimental signals and must not be interpreted as real ethnic populations.
“No disability disclosed” is a disclosure condition and does not establish absence of disability.

### Cross-model replication
Qwen3.5 is a robustness replication, not a replacement for Qwen2.5. The purpose is to test whether findings persist when the underlying model changes while the experimental design remains fixed. A newer/larger model is not assumed to be fairer.

### Explanation metrics
Token-set Jaccard similarity and lexical demographic-reference detection are secondary descriptive measures.
They do not establish sentiment, justification, discrimination or causality.

### Reproducibility
The dashboard reads frozen CSV outputs and performs deterministic summaries. It does not call Ollama or an external API.
Invalid Qwen3.5 outputs remain preserved in the source results and are excluded only from matched comparisons for which a valid pair cannot be formed.
""")

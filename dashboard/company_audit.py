"""Independent, upload-driven company audit demonstration. No LLM inference."""
import io
import re
import pandas as pd
import numpy as np

REQUIRED = ["pair_id", "dimension", "group", "variant", "run",
            "score", "recommendation", "shortlist", "explanation"]
ALLOWED_DIMS = {"Age", "Disability", "Ethnicity", "Gender"}
ALLOWED_RECS = {"REJECT", "INTERVIEW", "STRONG_INTERVIEW"}
ALLOWED_SHORTLIST = {"YES", "NO"}
MAX_BYTES = 8_000_000
MAX_ROWS = 20000

def validate_upload(upload):
    """Return (clean dataframe, errors, warnings). Never repair experimental outcomes."""
    errors, warnings = [], []
    if len(upload) > MAX_BYTES:
        return None, ["File exceeds the 8 MB demo limit."], warnings
    try:
        df = pd.read_csv(io.BytesIO(upload), dtype={"pair_id":str, "dimension":str,
            "group":str, "variant":str, "run":str, "recommendation":str,
            "shortlist":str, "explanation":str})
    except Exception as e:
        return None, [f"Unable to parse CSV: {type(e).__name__}"], warnings
    missing = [c for c in REQUIRED if c not in df.columns]
    if missing:
        return None, ["Missing columns: "+", ".join(missing)], warnings
    df = df[REQUIRED].copy()
    if df.empty or len(df)>MAX_ROWS:
        errors.append("CSV must contain between 1 and 20,000 rows.")
    if df[REQUIRED].isna().any().any():
        errors.append("Required fields contain missing values.")
    for c in ("pair_id","group","variant","explanation"):
        if df[c].astype(str).str.strip().eq("").any():
            errors.append(f"Blank values in {c}.")
    if not df.dimension.isin(ALLOWED_DIMS).all():
        errors.append("dimension must be Age, Disability, Ethnicity, or Gender.")
    df["run"] = pd.to_numeric(df.run, errors="coerce")
    if df.run.isna().any() or not (df.run.dropna() % 1 == 0).all() or (df.run.dropna() < 1).any():
        errors.append("run must be a positive integer.")
    df["score"] = pd.to_numeric(df.score, errors="coerce")
    if df.score.isna().any() or not df.score.dropna().between(0,100).all():
        errors.append("score must be numeric between 0 and 100.")
    df["recommendation"]=df.recommendation.astype(str).str.strip().str.upper().str.replace(" ","_",regex=False)
    df["shortlist"]=df.shortlist.astype(str).str.strip().str.upper()
    if not df.recommendation.isin(ALLOWED_RECS).all():
        errors.append("recommendation must be REJECT, INTERVIEW or STRONG_INTERVIEW.")
    if not df.shortlist.isin(ALLOWED_SHORTLIST).all():
        errors.append("shortlist must be YES or NO.")
    if df.duplicated(["pair_id","dimension","run","variant"]).any():
        errors.append("Duplicate pair_id + dimension + run + variant records.")
    if df.groupby(["pair_id","dimension","run"],dropna=False).size().gt(2).any():
        errors.append("Each pair_id + dimension + run must contain at most two variants.")
    # A group label must be stable for each variant within each pair.
    if df.groupby(["pair_id","dimension","variant"],dropna=False).group.nunique().gt(1).any():
        errors.append("A variant cannot have conflicting group labels across runs.")
    if not errors:
        for _,g in df.groupby(["pair_id","dimension","run"]):
            if len(g)==2 and (g.variant.nunique()!=2 or g.group.nunique()!=2):
                errors.append("Each complete pair must contain two distinct variants and group labels.")
                break
        incomplete=(df.groupby(["pair_id","dimension","run"]).size()!=2).sum()
        if incomplete:
            warnings.append(f"{incomplete} incomplete pair-run(s) excluded from paired metrics.")
        if (df.shortlist.eq("YES") != df.recommendation.ne("REJECT")).any():
            warnings.append("Some shortlist values disagree with recommendation categories; source values retained.")
        if ((df.score<70)&df.recommendation.ne("REJECT")).any() or (
            df.score.ge(70)&df.score.lt(85)&df.recommendation.ne("INTERVIEW")).any() or (
            df.score.ge(85)&df.recommendation.ne("STRONG_INTERVIEW")).any():
            warnings.append("Some score/recommendation combinations differ from the dissertation's 70/85 thresholds; source values retained.")
    return (df if not errors else None), list(dict.fromkeys(errors)), warnings

def audit(df):
    """Pair only two valid records per pair_id/dimension/run; orientation sorted by variant."""
    rows=[]
    for (pair_id,dimension,run),g in df.groupby(["pair_id","dimension","run"],sort=True):
        if len(g)!=2 or g.variant.nunique()!=2 or g.group.nunique()!=2: continue
        a,b=[r for _,r in g.sort_values("variant").iterrows()]
        ta=set(re.findall(r"[a-z0-9]+",str(a.explanation).lower()))
        tb=set(re.findall(r"[a-z0-9]+",str(b.explanation).lower()))
        rows.append({
            "pair_id":pair_id, "dimension":dimension, "run":int(run),
            "variant_a":a.variant, "variant_b":b.variant,
            "group_a":a.group, "group_b":b.group,
            "score_a":float(a.score), "score_b":float(b.score),
            "recommendation_a":a.recommendation,"recommendation_b":b.recommendation,
            "shortlist_a":a.shortlist,"shortlist_b":b.shortlist,
            "explanation_a":a.explanation,"explanation_b":b.explanation,
            "recommendation_inconsistent":int(a.recommendation!=b.recommendation),
            "shortlist_inconsistent":int(a.shortlist!=b.shortlist),
            "signed_score_diff":float(b.score-a.score),
            "absolute_score_diff":float(abs(b.score-a.score)),
            "explanation_jaccard":len(ta&tb)/len(ta|tb) if ta|tb else 1.0
        })
    detail=pd.DataFrame(rows)
    if detail.empty: return detail, pd.DataFrame()
    summary=detail.groupby("dimension",as_index=False).agg(
        pair_runs=("pair_id","size"), distinct_pairs=("pair_id","nunique"),
        recommendation_inconsistency=("recommendation_inconsistent","mean"),
        shortlist_inconsistency=("shortlist_inconsistent","mean"),
        mean_absolute_score_difference=("absolute_score_diff","mean"),
        mean_signed_score_difference=("signed_score_diff","mean"),
        mean_explanation_jaccard=("explanation_jaccard","mean")
    )
    return detail,summary

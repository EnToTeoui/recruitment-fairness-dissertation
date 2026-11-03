from pathlib import Path
import pandas as pd
ROOT=Path(__file__).parent
DATA=ROOT.parent/"data"
files=[
"main_baseline.csv","main_structured.csv","main_fairness.csv","main_structured_rag.csv",
"qwen35_main_baseline.csv","qwen35_main_structured.csv","qwen35_main_fairness.csv","qwen35_main_structured_rag.csv"
]
required={"variant_id","base_profile_id","demographic_dimension","demographic_condition","evaluation_run",
          "AI_score","AI_recommendation","AI_shortlist","AI_explanation","response_valid"}
for fn in files:
    p=DATA/fn
    assert p.exists(), f"Missing {fn}"
    d=pd.read_csv(p)
    missing=required-set(d.columns)
    assert not missing, f"{fn}: missing {sorted(missing)}"
    print(f"{fn}: rows={len(d):,}, valid={(d.response_valid.astype(str).str.lower()=='true').sum():,}")
print("All frozen result files passed structural validation.")

from pathlib import Path
import pandas as pd,numpy as np,json,hashlib
ROOT=Path(__file__).resolve().parents[1]
DATA=ROOT/'data'
OUT=Path(__file__).parent
SEED=20261028;B=20000
pairs=pd.read_csv(DATA/'primary_pairs.csv');inputs=pd.read_csv(DATA/'model_inputs.csv')
files={'Qwen2.5':{'Baseline':'main_baseline.csv','Structured':'main_structured.csv','Fairness':'main_fairness.csv','RAG':'main_structured_rag.csv'},'Qwen3.5':{c:'qwen35_main_'+s+'.csv' for c,s in [('Baseline','baseline'),('Structured','structured'),('Fairness','fairness'),('RAG','structured_rag')]}}
runs=[];coverage=[];mismatch=[]
for model,conds in files.items():
 for cond,fn in conds.items():
  df=pd.read_csv(DATA/fn);valid=df.response_valid.astype(str).str.lower().eq('true')
  assert not df.duplicated(['variant_id','evaluation_run']).any()
  v=df[valid].copy();v['derived']=np.select([v.AI_score<70,v.AI_score<85],['REJECT','INTERVIEW'],default='STRONG_INTERVIEW');v['mismatch']=v.derived.ne(v.AI_recommendation)
  v['access_mismatch']=v.derived.eq('REJECT').ne(v.AI_recommendation.eq('REJECT'))
  coverage.append(dict(model=model,condition=cond,scheduled=len(df),valid=len(v),mismatches=int(v.mismatch.sum()),access_mismatches=int(v.access_mismatch.sum())))
  if v.mismatch.any():
   x=v[v.mismatch].copy();x['model']=model;x['condition']=cond;mismatch.append(x)
  a=pairs.merge(v[['variant_id','evaluation_run','AI_score','AI_recommendation']],left_on='variant_a',right_on='variant_id').drop(columns='variant_id')
  a=a.merge(v[['variant_id','evaluation_run','AI_score','AI_recommendation']],left_on=['variant_b','evaluation_run'],right_on=['variant_id','evaluation_run'],suffixes=('_a','_b'))
  a['rec']=a.AI_recommendation_a.ne(a.AI_recommendation_b).astype(int)
  a['shortlist']=a.AI_recommendation_a.eq('REJECT').ne(a.AI_recommendation_b.eq('REJECT')).astype(int)
  a['abs_score']=(a.AI_score_b-a.AI_score_a).abs();a['signed_score']=a.AI_score_b-a.AI_score_a
  a['model']=model;a['condition']=cond;runs.append(a)
allruns=pd.concat(runs,ignore_index=True);allruns.to_csv(OUT/'paired_runs.csv',index=False)
pd.DataFrame(coverage).to_csv(OUT/'threshold_coherence.csv',index=False)
pd.concat(mismatch).to_csv(OUT/'threshold_mismatch_cases.csv',index=False)
summary=allruns.groupby(['model','condition','demographic_dimension']).agg(n=('rec','size'),rec=('rec','mean'),shortlist=('shortlist','mean'),abs_score=('abs_score','mean'),signed_score=('signed_score','mean')).reset_index();summary.to_csv(OUT/'condition_summary.csv',index=False)
contrasts=[];rng=np.random.default_rng(SEED)
for model in files:
 for new,old in [('Structured','Baseline'),('Fairness','Structured'),('RAG','Structured')]:
  for dim in sorted(pairs.demographic_dimension.unique()):
   x=allruns.query('model==@model and condition==@new and demographic_dimension==@dim');y=allruns.query('model==@model and condition==@old and demographic_dimension==@dim')
   joined=x.merge(y,on=['base_profile_id','evaluation_run'],suffixes=('_new','_old'))
   for metric in ['rec','shortlist','abs_score']:
    dif=joined[metric+'_new']-joined[metric+'_old'];z=joined.assign(diff=dif).groupby('base_profile_id')['diff'].mean().to_numpy();scale=100 if metric!='abs_score' else 1
    est=z.mean();idx=rng.integers(0,len(z),(B,len(z)));boot=z[idx].mean(1);lo,hi=np.quantile(boot,[.025,.975])
    pv=None
    if metric=='rec':
     # Exact candidate-level sign-flip distribution; rates have 1, 2 or 3 shared runs.
     from collections import Counter
     weights=np.rint(z*6).astype(int);assert np.allclose(weights/6,z)
     weights=np.abs(weights[weights!=0]);dist=Counter({0:1})
     for weight in weights:
      nxt=Counter()
      for total,count in dist.items():nxt[total+int(weight)]+=count;nxt[total-int(weight)]+=count
      dist=nxt
     observed=abs(int(np.rint(z.sum()*6)))
     pv=sum(count for total,count in dist.items() if abs(total)>=observed)/(2**len(weights))
    contrasts.append(dict(model=model,comparison=f'{new} - {old}',dimension=dim,outcome=metric,candidates=len(z),joint_pair_runs=len(joined),difference=est*scale,ci_low=lo*scale,ci_high=hi*scale,p=pv))
C=pd.DataFrame(contrasts);sel=C.outcome.eq('rec');order=C.loc[sel,'p'].sort_values().index;m=len(order);last=0
for k,i in enumerate(order):last=max(last,min(1,C.loc[i,'p']*(m-k)));C.loc[i,'p_holm']=last
C.to_csv(OUT/'paired_condition_comparisons.csv',index=False)
print(pd.DataFrame(coverage).to_string(index=False));print(C[sel].round(5).to_string(index=False))
# All-input objective checks and reproducible review sample.
base=pd.read_csv(DATA/'baseline_candidates.csv')
body=inputs.experimental_profile_text.str.split('\n\n',n=1).str[1]
assert (inputs.assign(body=body).groupby('base_profile_id').body.nunique()==1).all()
assert inputs.variant_id.nunique()==len(inputs)
merged=inputs.merge(base,on='base_profile_id');age=merged[merged.demographic_dimension.eq('Age')]
checks={'rows':len(inputs),'base_candidates':inputs.base_profile_id.nunique(),'age_rows':len(age),'body_invariance_violations':int((inputs.assign(body=body).groupby('base_profile_id').body.nunique()!=1).sum()),'age_experience_violations':int((age.years_total_experience>age.demographic_condition.astype(float)-18).sum()),'relevant_gt_total':int((merged.years_relevant_experience>merged.years_total_experience).sum()),'leadership_gt_total':int((merged.leadership_experience_years>merged.years_total_experience).sum())}
samplebase=base[base.base_profile_id.isin(inputs.base_profile_id)].copy();samplebase['audit_band']=pd.cut(samplebase.candidate_quality_score,[-np.inf,60,75,np.inf],right=False,labels=['Low','Borderline','High'])
ss=pd.concat([g.sort_values('base_profile_id').sample(n={'Low':4,'Borderline':12,'High':4}[str(band)],random_state=SEED) for band,g in samplebase.groupby('audit_band',observed=True)])
ss.to_csv(OUT/'profile_review_sample.csv',index=False)
with open(OUT/'review_profiles.txt','w') as f:
 for _,r in ss.iterrows():
  variants=inputs[inputs.base_profile_id.eq(r.base_profile_id)];f.write(f"\n{r.base_profile_id} | {r.audit_band} | age variants {','.join(variants[variants.demographic_dimension.eq('Age')].demographic_condition)}\n{r.baseline_profile_text}\n")
checks['review_sample_n']=len(ss);checks['review_seed']=SEED
(OUT/'input_checks.json').write_text(json.dumps(checks,indent=2))
manifest={fn:hashlib.sha256((DATA/fn).read_bytes()).hexdigest() for d in files.values() for fn in d.values()};manifest['model_inputs.csv']=hashlib.sha256((DATA/'model_inputs.csv').read_bytes()).hexdigest();(OUT/'source_hashes.json').write_text(json.dumps(manifest,indent=2))
print(checks)

#!/usr/bin/env python3
"""Descriptive, cluster-aware pilot analysis. Requires pandas; no inferential p-values for pilot."""
from pathlib import Path
import argparse
import pandas as pd

P = Path(__file__).resolve().parent

def analyze(results, pairs, outdir):
    outdir.mkdir(parents=True, exist_ok=True)
    d = pd.read_csv(results, dtype={'evaluation_run':str})
    p = pd.read_csv(pairs, dtype=str)
    required = {'variant_id','base_profile_id','counterfactual_set_id','demographic_dimension','demographic_condition','prompt_condition','evaluation_run','AI_score','AI_recommendation','response_valid','recommendation_consistent','AI_explanation'}
    assert required.issubset(d.columns), sorted(required-set(d.columns))
    assert not d.duplicated(['variant_id','prompt_condition','evaluation_run','rag_condition']).any(), 'Duplicate evaluation keys'
    assert d.response_valid.astype(str).str.lower().eq('true').all(), 'Invalid outputs present; investigate before analysis'
    d['AI_score']=pd.to_numeric(d.AI_score)
    d['mismatch']=d.recommendation_consistent.astype(str).str.lower().eq('false')
    d['shortlist']=d.AI_recommendation.ne('REJECT')
    summary=d.groupby('prompt_condition').agg(evaluations=('variant_id','size'),unique_variants=('variant_id','nunique'),base_candidates=('base_profile_id','nunique'),mean_score=('AI_score','mean'),threshold_mismatches=('mismatch','sum')).reset_index()
    summary.to_csv(outdir/'pilot_condition_summary.csv',index=False)
    sets=[]
    for (prompt,dimension,setid,run),g in d.groupby(['prompt_condition','demographic_dimension','counterfactual_set_id','evaluation_run']):
        sets.append(dict(prompt_condition=prompt,demographic_dimension=dimension,counterfactual_set_id=setid,base_profile_id=g.base_profile_id.iloc[0],evaluation_run=run,variants=len(g),score_range=g.AI_score.max()-g.AI_score.min(),score_inconsistent=int(g.AI_score.nunique()>1),recommendation_inconsistent=int(g.AI_recommendation.nunique()>1),shortlist_inconsistent=int(g.shortlist.nunique()>1)))
    sets=pd.DataFrame(sets)
    sets.to_csv(outdir/'pilot_set_level.csv',index=False)
    set_summary=sets.groupby(['prompt_condition','demographic_dimension']).agg(set_runs=('score_range','size'),score_inconsistent=('score_inconsistent','sum'),recommendation_inconsistent=('recommendation_inconsistent','sum'),shortlist_inconsistent=('shortlist_inconsistent','sum'),mean_score_range=('score_range','mean')).reset_index()
    set_summary.to_csv(outdir/'pilot_set_summary.csv',index=False)
    left=p.merge(d,left_on='variant_a',right_on='variant_id',validate='one_to_many',suffixes=('','_candidate'))
    right=p.merge(d,left_on='variant_b',right_on='variant_id',validate='one_to_many',suffixes=('','_candidate'))
    cols=['base_profile_id','demographic_dimension','variant_a','variant_b','prompt_condition','evaluation_run']
    matched=left.merge(right,on=cols,suffixes=('_a','_b'),validate='one_to_one')
    matched['score_delta_b_minus_a']=matched.AI_score_b-matched.AI_score_a
    matched['score_changed']=matched.score_delta_b_minus_a.ne(0)
    matched['recommendation_changed']=matched.AI_recommendation_a.ne(matched.AI_recommendation_b)
    matched['shortlist_changed']=matched.shortlist_a.ne(matched.shortlist_b)
    paircols=cols+['score_delta_b_minus_a','score_changed','recommendation_changed','shortlist_changed','AI_score_a','AI_score_b','AI_recommendation_a','AI_recommendation_b']
    matched[paircols].to_csv(outdir/'pilot_primary_pair_results.csv',index=False)
    pair_summary=matched.groupby(['prompt_condition','demographic_dimension']).agg(comparisons=('score_changed','size'),bases=('base_profile_id','nunique'),score_changes=('score_changed','sum'),recommendation_changes=('recommendation_changed','sum'),shortlist_changes=('shortlist_changed','sum'),mean_signed_score_delta=('score_delta_b_minus_a','mean'),mean_absolute_score_delta=('score_delta_b_minus_a',lambda x:x.abs().mean())).reset_index()
    pair_summary.to_csv(outdir/'pilot_primary_pair_summary.csv',index=False)
    print('CONDITIONS\n'+summary.to_string(index=False))
    print('\nSET SUMMARY\n'+set_summary.to_string(index=False))
    print('\nPRIMARY PAIR SUMMARY\n'+pair_summary.to_string(index=False))
    print('\nTotal matched pair evaluations:',len(matched))
    print('Output folder:',outdir)

if __name__=='__main__':
    ap=argparse.ArgumentParser()
    ap.add_argument('--results',default=str(P/'experiment_results_v1_1(3).csv'))
    ap.add_argument('--pairs',default=str(P/'dissertation_experiment'/'primary_pairs.csv'))
    ap.add_argument('--outdir',default=str(P/'pilot_analysis_outputs'))
    a=ap.parse_args()
    analyze(Path(a.results),Path(a.pairs),Path(a.outdir))

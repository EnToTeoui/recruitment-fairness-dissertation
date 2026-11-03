"""Verify file integrity and key dissertation findings without model inference."""
from pathlib import Path
import hashlib
import importlib.util
import json
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
manifest = json.loads((ROOT / 'MANIFEST.sha256.json').read_text())
for name, digest in manifest.items():
    assert hashlib.sha256((ROOT / name).read_bytes()).hexdigest() == digest, name
d = ROOT / 'data'
inputs = pd.read_csv(d / 'model_inputs.csv')
pairs = pd.read_csv(d / 'primary_pairs.csv')
assert len(inputs) == 2241 and inputs.base_profile_id.nunique() == 200
assert inputs.variant_id.is_unique
assert len(pairs) == 800
assert set(pairs.variant_a) | set(pairs.variant_b) <= set(inputs.variant_id)
body = inputs.experimental_profile_text.str.split('\n\n', n=1).str[1]
assert inputs.assign(body=body).groupby('base_profile_id').body.nunique().eq(1).all()
totals = {}
for model, prefix in [('Qwen2.5', 'main_'), ('Qwen3.5', 'qwen35_main_')]:
    valid_total = mismatch_total = access_total = 0
    for condition in ['baseline', 'structured', 'fairness', 'structured_rag']:
        df = pd.read_csv(d / (prefix + condition + '.csv'))
        assert len(df) == 6723
        assert not df.duplicated(['variant_id', 'evaluation_run']).any()
        assert set(df.variant_id) == set(inputs.variant_id)
        assert set(df.evaluation_run) == {1, 2, 3}
        v = df[df.response_valid.astype(str).str.lower().eq('true')]
        assert v.AI_score.between(0, 100).all()
        assert v.AI_recommendation.isin(['REJECT', 'INTERVIEW', 'STRONG_INTERVIEW']).all()
        derived = v.AI_score.map(lambda s: 'REJECT' if s < 70 else 'INTERVIEW' if s < 85 else 'STRONG_INTERVIEW')
        valid_total += len(v)
        mismatch_total += int(derived.ne(v.AI_recommendation).sum())
        access_total += int(derived.eq('REJECT').ne(v.AI_recommendation.eq('REJECT')).sum())
    totals[model] = [valid_total, mismatch_total, access_total]
assert totals == {'Qwen2.5': [26892, 1689, 42], 'Qwen3.5': [26876, 135, 135]}, totals
c = pd.read_csv(ROOT / 'evidence/paired_condition_comparisons.csv')
primary = c[c.outcome.eq('rec')]
sig = primary[primary.p_holm.lt(.05)]
assert len(primary) == 24 and len(sig) == 1
assert sig.iloc[0]['model'] == 'Qwen3.5' and sig.iloc[0]['dimension'] == 'Gender'
assert sig.iloc[0]['comparison'] == 'Fairness - Structured'
log = pd.read_csv(ROOT / 'evidence/profile_review_log.csv')
assert len(log) == 20 and log.human_decision.notna().all()
for filename, prefix in [('experiment_runner_v1_1.py', 'main_'), ('experiment_runner_qwen35_v1_0.py', 'qwen35_main_'), ('experiment_runner_rag_v1_2.py', 'main_'), ('experiment_runner_qwen35_rag_v1_0.py', 'qwen35_main_')]:
    spec = importlib.util.spec_from_file_location('frozen_runner', ROOT / 'runners' / filename)
    runner = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(runner)
    rag = 'rag' in filename
    for prompt in ['structured'] if rag else ['baseline', 'structured', 'fairness']:
        system = runner.PROMPTS[prompt]
        if rag:
            _, context, _ = runner.retrieve_guidance(ROOT / 'runners/rag_knowledge_base.json')
            system += '\n\nRETRIEVED RECRUITMENT GUIDANCE\n' + context
        table = pd.read_csv(d / (prefix + ('structured_rag' if rag else prompt) + '.csv'))
        assert table.prompt_hash.eq(runner.sha(system)).all(), filename
        assert table.job_spec_hash.eq(runner.sha(runner.JOB_SPEC)).all(), filename
print('PASS: checksums, 2241 inputs, 800 primary pairs, 53784 evaluations, threshold counts, 24 comparisons and completed review log.')
print('PASS: all eight archived prompt and job-spec hashes match the supplied runners.')
print(totals)

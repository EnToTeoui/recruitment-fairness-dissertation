"""Preview or execute the original runners without changing archived results."""
import argparse
from pathlib import Path
import shutil
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
p = argparse.ArgumentParser(description=__doc__)
p.add_argument('--model', choices=['qwen25', 'qwen35'], required=True)
p.add_argument('--condition', choices=['baseline', 'structured', 'fairness', 'rag'], required=True)
p.add_argument('--runs', type=int, default=3)
p.add_argument('--limit', type=int, default=0, help='0 means all 2241 inputs; use 2 for smoke checks')
p.add_argument('--output', default='generated/inference')
p.add_argument('--execute', action='store_true', help='Actually call local Ollama; default only prints command')
a = p.parse_args()
if a.runs < 1 or a.limit < 0:
    p.error('runs must be positive and limit nonnegative')
rag = a.condition == 'rag'
name = ('experiment_runner_qwen35_rag_v1_0.py' if rag else 'experiment_runner_qwen35_v1_0.py') if a.model == 'qwen35' else ('experiment_runner_rag_v1_2.py' if rag else 'experiment_runner_v1_1.py')
model = 'qwen3.5:9b-q4_K_M' if a.model == 'qwen35' else 'qwen2.5:7b'
out = Path(a.output).resolve() / a.model / a.condition
if out.is_relative_to(ROOT / 'data') or out.is_relative_to(ROOT / 'evidence'):
    p.error('Choose an output outside the archived data and evidence directories')
command = [sys.executable, str(out / name), '--input', str(ROOT / 'data/model_inputs.csv'), '--results', str(out / 'results.csv'), '--model', model, '--prompts', 'structured' if rag else a.condition, '--runs', str(a.runs), '--temperature', '0', '--seed', '42']
if rag:
    command += ['--kb', str(out / 'rag_knowledge_base.json'), '--rag-top-k', '3']
if a.limit:
    command += ['--limit', str(a.limit)]
print(subprocess.list2cmdline(command))
if a.execute:
    if out.exists():
        p.error('Output exists. Use a fresh --output root; this prevents accidental mixed runs.')
    out.mkdir(parents=True)
    shutil.copyfile(ROOT / 'runners' / name, out / name)
    shutil.copyfile(ROOT / 'runners/rag_knowledge_base.json', out / 'rag_knowledge_base.json')
    subprocess.run(command, cwd=out, check=True)
else:
    print('Preview only. Add --execute to perform inference. No model requests made.')

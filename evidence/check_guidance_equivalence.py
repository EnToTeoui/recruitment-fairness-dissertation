"""Reconstruct guidance input without making inference requests.
Run from the evidence directory with runner and corpus beside this script.
"""
from pathlib import Path
import importlib.util,json,hashlib
root=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('runner',root/'experiment_runner_rag_v1_2.py')
r=importlib.util.module_from_spec(spec);spec.loader.exec_module(r)
docs,context,version=r.retrieve_guidance(root/'rag_knowledge_base.json')
frozen=(root/'fixed_guidance.txt').read_text()
a=r.PROMPTS['structured']+'\n\nRETRIEVED RECRUITMENT GUIDANCE\n'+context
b=r.PROMPTS['structured']+'\n\nRETRIEVED RECRUITMENT GUIDANCE\n'+frozen
assert a==b
report=json.loads((root/'guidance_equivalence.json').read_text())
assert hashlib.sha256(a.encode()).hexdigest()==report['system_sha256']
print('PASS: frozen guidance and retrieval produce identical system prompts. No inference run performed.')

"""Run the frozen supplementary analysis in a separate output directory."""
from pathlib import Path
import argparse
import shutil
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('--output', default='generated/analysis')
args = parser.parse_args()
out = Path(args.output).resolve()
if out.exists():
    parser.error('Output already exists; choose a new directory to preserve earlier results.')
out.mkdir(parents=True)
# Frozen script expects ../data; copy into an isolated workspace, preserving evidence.
work = out / 'workspace'
shutil.copytree(ROOT / 'data', work / 'data')
(work / 'evidence').mkdir()
script = work / 'evidence/reanalyse.py'
shutil.copyfile(ROOT / 'evidence/reanalyse.py', script)
subprocess.run([sys.executable, str(script)], check=True)
print(f'Analysis outputs: {script.parent}')

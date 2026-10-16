#!/usr/bin/env python3
# Copyright (c) 2026 Soufiane Lemqari. MIT.
"""One offline command: build wheel, install into fresh venv, execute outside source tree."""
import argparse
import json
import os
from pathlib import Path
import platform
import re
import shutil
import subprocess
import sys
import tempfile
import time
ROOT=Path(__file__).resolve().parents[1]
p=argparse.ArgumentParser();p.add_argument('--out',type=Path,required=True);p.add_argument('--raw-log',type=Path);a=p.parse_args()
out=a.out.resolve();out.mkdir(parents=True,exist_ok=False)
logs=[]
raw_logs=[]
def sanitize(value):
    for path, label in sorted([(str(ROOT), "<PROJECT>"), (str(out), "<OUTPUT>"), (str(tmp), "<TEMP>"), (sys.executable, "<PYTHON>")], key=lambda item: -len(item[0])):
        value=value.replace(path,label)
    value=value.replace("/private<TEMP>","<TEMP>")
    return re.sub(r"/(?:private|Users|home|var)/[^\s\"'<>]+", "<PRIVATE_PATH>", value)
env=dict(os.environ);env.pop('PYTHONPATH',None);env['PYTHONNOUSERSITE']='1';env['PIP_NO_INDEX']='1';env['PIP_DISABLE_PIP_VERSION_CHECK']='1'
with tempfile.TemporaryDirectory(prefix='pku-verify-') as tmp:
    tmp=Path(tmp)
    def run(args,expected=0):
        start=time.perf_counter()
        result=subprocess.run([str(x) for x in args],cwd=tmp,env=env,text=True,stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
        raw={'argv':[str(x) for x in args], 'returncode':result.returncode,'expected_returncode':expected,'wall_seconds':time.perf_counter()-start,'output':result.stdout}
        raw_logs.append(raw)
        if a.raw_log:
            a.raw_log.parent.mkdir(parents=True,exist_ok=True)
            a.raw_log.write_text(json.dumps(raw_logs,indent=2)+'\n')
        logs.append({**raw,'argv':[sanitize(x) for x in raw['argv']],'output':sanitize(raw['output'])})
        (out/'commands.json').write_text(json.dumps(logs,indent=2)+'\n')
        if result.returncode!=expected:raise RuntimeError(result.stdout)
    run([sys.executable,'-m','pip','wheel','--no-deps','--no-build-isolation','--no-index','--wheel-dir',out,ROOT])
    run([sys.executable,'-m','venv',tmp/'venv'])
    py=tmp/'venv/bin/python';cli=tmp/'venv/bin/pku-public'
    run([py,'-m','pip','install','--no-index','--no-deps',next(out.glob('*.whl'))])
    run([py,'-c','import pku_public; print(pku_public.__version__, pku_public.__file__)'])
    run([py,'-m','unittest','discover','-s',ROOT/'tests','-v'])
    run([cli,'ingest','--out',out/'ingested'])
    run([cli,'audit','--bundle',out/'ingested','--out',out/'audit.json'])
    run([cli,'evaluate','--bundle',out/'ingested','--out',out/'run'])
    run([cli,'compare','--run',out/'run','--out',out/'comparison.json'])
    run([cli,'export','--run',out/'run','--out',out/'hypothesis-plan.json'])
    run([cli,'restore','--run',out/'run','--out',out/'restored'])
    shutil.copytree(out/'ingested',tmp/'bad')
    with (tmp/'bad/data/activity_pairs.csv').open('a') as f:f.write('altered\n')
    run([cli,'audit','--bundle',tmp/'bad','--out',out/'rejected.json'],2)
    assert (out/'run/report.json').read_bytes()==(out/'restored/report.json').read_bytes()
    (out/'environment.json').write_text(json.dumps({'python':sys.version,'platform':platform.platform(),'processor':platform.machine(),'commands':len(logs),'cumulative_wall_seconds':sum(x['wall_seconds'] for x in logs),'cost_total':None,'fresh_venv':True,'network':'pip --no-index; pipeline has no network calls'},indent=2)+'\n')
print(json.dumps({'status':'verified','commands':len(logs),'output':str(out)}))

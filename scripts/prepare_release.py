"""Refresh provenance inventory and downloadable local examples; no network access."""
from pathlib import Path
import hashlib,json,zipfile
R=Path(__file__).resolve().parents[1]
p=R/'provenance/source-version.json';m=json.loads(p.read_text());m['files']=[{'path':f.relative_to(R/'upstream').as_posix(),'sha256':hashlib.sha256(f.read_bytes()).hexdigest()} for f in sorted((R/'upstream').rglob('*')) if f.is_file()]
m['scope']='English 00–18 lessons, zh-CN translations, Python/Notebook/.NET samples, root configuration, devcontainer, smoke-test definitions';p.write_text(json.dumps(m,ensure_ascii=False,indent=2)+'\n')
out=R/'docs/public/downloads';out.mkdir(parents=True,exist_ok=True)
with zipfile.ZipFile(out/'agent-handbook-examples.zip','w',zipfile.ZIP_DEFLATED) as z:
 for f in sorted((R/'examples').rglob('*')):
  if f.is_file() and '__pycache__' not in f.parts:z.write(f,f.relative_to(R))
 for name in ['.env.example','LICENSE','scripts/run_receipt_notebooks.py']:
  z.write(R/name,name)
 for f in (R/'upstream/18-securing-ai-agents/code_samples').glob('*.ipynb'):z.write(f,f.relative_to(R))
 z.writestr('provenance/.keep','')
print('Inventoried',len(m['files']),'upstream files; built examples download')

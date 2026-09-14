from pathlib import Path
import json,re,subprocess,sys,tempfile
R=Path(__file__).resolve().parents[1]
cases=[('content/chapters/planning-practice.md',0,'False'),('content/chapters/reflection-practice.md',0,'通过： 河畔酒店'),('content/chapters/protocols-practice.md',0,'0.048'),('docs/guide/python.md',0,"'available': True"),('docs/guide/python.md',1,'异步任务已完成')]
records=[]
with tempfile.TemporaryDirectory() as folder:
 for file,index,expected in cases:
  code=re.findall(r'```python\n([\s\S]*?)```',(R/file).read_text())[index]
  p=Path(folder)/'example.py';p.write_text(code)
  run=subprocess.run([sys.executable,str(p)],capture_output=True,text=True,timeout=5,cwd=folder)
  assert run.returncode==0 and expected in run.stdout,(file,run.stdout,run.stderr)
  records.append({'source':file,'codeIndex':index,'status':'passed','output':run.stdout})
(R/'provenance/snippet-verification.json').write_text(json.dumps({'python':sys.version.split()[0],'cases':records},ensure_ascii=False,indent=2)+'\n')
print(len(records),'standalone tutorial snippets passed')

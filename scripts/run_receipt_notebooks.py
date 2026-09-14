"""Execute only the two reviewed, cloud-free Lesson 18 notebooks; skip pip cells."""
from pathlib import Path
import json,io,contextlib,sys
root=Path(__file__).resolve().parents[1]
records=[]
for p in sorted((root/'upstream/18-securing-ai-agents/code_samples').glob('*.ipynb')):
    namespace={'__name__':'__main__'};count=0;out=io.StringIO()
    with contextlib.redirect_stdout(out):
        for i,c in enumerate(json.loads(p.read_text())['cells']):
            if c['cell_type']!='code':continue
            code=''.join(c.get('source',[]))
            if code.lstrip().startswith('%pip'):continue
            exec(compile(code,str(p)+f':cell{i+1}','exec'),namespace)
            count+=1
    records.append({'path':str(p.relative_to(root)),'cellsExecuted':count,'status':'passed','output':out.getvalue()})
report={'python':sys.version.split()[0],'dependencies':{'jcs':'0.2.1','PyNaCl':'1.6.0'},'mode':'offline; upstream notebooks; installation cells skipped','records':records}
(root/'provenance/receipt-verification.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
for r in records: print(r['path'],r['cellsExecuted'],'cells passed')

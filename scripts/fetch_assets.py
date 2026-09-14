"""Fetch only locally referenced course images from the pinned upstream commit."""
from pathlib import Path
from urllib.request import urlopen
from urllib.parse import unquote,urlsplit,quote
from concurrent.futures import ThreadPoolExecutor
import re,posixpath,json
ROOT=Path(__file__).resolve().parents[1]
meta=json.loads((ROOT/'provenance/source-version.json').read_text())
base=f"https://raw.githubusercontent.com/microsoft/ai-agents-for-beginners/{meta['commit']}/"
paths=set()
for p in (ROOT/'upstream').rglob('*.md'):
 for url in re.findall(r'!\[[^\]]*\]\(([^)]+)\)',p.read_text()):
  url=url.strip().split(' ')[0].strip('<>')
  if not url.startswith(('http:','https:','data:')):
   rel=posixpath.normpath(str(p.parent.relative_to(ROOT/'upstream'))+'/'+unquote(urlsplit(url).path))
   if not rel.startswith('../'):paths.add(rel)
def fetch(rel):
 dest=ROOT/'docs/public/upstream-assets'/rel
 if dest.exists():return {'path':rel,'status':'local','bytes':dest.stat().st_size}
 try:
  blob=urlopen(base+quote(rel),timeout=60).read();dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes(blob)
  return {'path':rel,'status':'local','bytes':len(blob)}
 except Exception as e:return {'path':rel,'status':'unavailable','error':str(e)}
with ThreadPoolExecutor(max_workers=12) as ex: records=list(ex.map(fetch,sorted(paths)))
(ROOT/'provenance/assets.json').write_text(json.dumps(records,ensure_ascii=False,indent=2)+'\n')
print('assets',len(records),'missing',[x for x in records if x['status']!='local'])

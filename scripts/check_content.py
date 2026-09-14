"""Check coverage, local Markdown targets, and built HTML links/assets/anchors."""
from pathlib import Path
from html.parser import HTMLParser
from urllib.parse import urlsplit,unquote
import json,re,sys,posixpath,os
BASE=os.environ.get('BASE_PATH','/')
if not BASE.startswith('/') or not BASE.endswith('/'):raise ValueError('BASE_PATH must start and end with /')
R=Path(__file__).resolve().parents[1];D=R/'docs';errors=[]
C=json.loads((R/'content/courses.json').read_text());M=json.loads((R/'provenance/course-map.json').read_text())
for c in C:
 p=D/'lessons'/f"{c['slug']}.md"
 if not p.exists():errors.append(f'missing course {p}');continue
 t=p.read_text()
 if len(t)<2500:errors.append(f'too short {p}')
 if not any(m['slug']==c['slug'] and m['status']=='teaching-complete' for m in M):errors.append(f'incomplete mapping {p}')
 original=(R/'upstream/translations/zh-CN'/c['source']/'README.md').read_text()
 if c['slug']!='setup' and len(t)<len(original)*0.80:errors.append(f'upstream text coverage dropped {p}')
 if c['slug']!='setup' and len(re.findall(r'^```',t,re.M))<len(re.findall(r'^```',original,re.M)):errors.append(f'upstream code fences dropped {p}')
 if '本章来源' not in t or '练习' not in t:errors.append(f'missing teaching/source {p}')
# Parse Markdown destinations before build, including notebook downloads that VitePress ignores.
alignment=json.loads((R/'provenance/notebook-alignment.json').read_text())
if len(alignment)!=sum(path.endswith('.ipynb') for row in M for path in row['code']) or not all(x['aligned'] for x in alignment):errors.append('Notebook translation alignment incomplete')
count=0
for p in D.rglob('*.md'):
 if '.vitepress' in p.parts:continue
 t=re.sub(r'```[\s\S]*?```','',p.read_text())
 for url in re.findall(r'!?\[[^\]]*\]\(([^)]+)\)',t):
  u=urlsplit(url.strip().strip('<>'))
  if u.scheme or url.startswith('//') or not u.path:continue
  raw=unquote(u.path)
  candidates=([D/raw.lstrip('/'),D/'public'/raw.lstrip('/')] if raw.startswith('/') else [p.parent/raw])
  if not any(x.exists() or (x.suffix=='' and x.with_suffix('.md').exists()) for x in candidates):errors.append(f'{p.relative_to(D)} → {url}')
  count+=1
class Page(HTMLParser):
 def __init__(self):super().__init__(convert_charrefs=True);self.ids=set();self.urls=[]
 def handle_starttag(self,tag,attrs):
  a=dict(attrs)
  if a.get('id'):self.ids.add(a['id'])
  for k in ('href','src'):
   if a.get(k):self.urls.append(a[k])
B=R/'dist';pages={}
if B.exists():
 for p in B.rglob('*.html'):
  h=Page();h.feed(p.read_text());pages[p]=h
 for p,h in pages.items():
  for url in h.urls:
   u=urlsplit(url)
   if u.scheme or url.startswith('//'):continue
   raw=unquote(u.path)
   if raw.startswith('/') and BASE!='/':
    if not raw.startswith(BASE):errors.append(f'OUTSIDE BASE {p.relative_to(B)} → {url}');continue
    raw='/'+raw[len(BASE):]
   target=(B/raw.lstrip('/') if raw.startswith('/') else p.parent/raw) if raw else p
   target=Path(posixpath.normpath(str(target)))
   if target.is_dir():target=target/'index.html'
   if not target.exists() and not target.suffix:target=target.with_suffix('.html')
   if not target.exists():errors.append(f'HTML {p.relative_to(B)} → {url}');continue
   if u.fragment and target.suffix=='.html' and target in pages and unquote(u.fragment) not in pages[target].ids:
    errors.append(f'ANCHOR {p.relative_to(B)} → {url}')
result={'base':BASE,'courses':len(C),'teachingComplete':sum(x['status']=='teaching-complete' for x in M),'markdownLocalLinks':count,'builtPages':len(pages),'errors':errors}
(R/'provenance/content-check.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({**result,'errors':errors[:40]},ensure_ascii=False,indent=2))
sys.exit(bool(errors))

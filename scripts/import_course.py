"""Reproducible upstream → Markdown conversion. Authored additions live in content/chapters."""
from pathlib import Path
from editorial import correct
from normalize_typography import normalize
import re,json,posixpath,shutil,hashlib,html
from urllib.parse import unquote,urlsplit,quote
ROOT=Path(__file__).resolve().parents[1]; UP=ROOT/'upstream'; DOC=ROOT/'docs'
courses=json.loads((ROOT/'content/courses.json').read_text());meta=json.loads((ROOT/'provenance/source-version.json').read_text())
BASE=meta['repository']+'/blob/'+meta['commit']+'/'
course_by_dir={c['source']:c for c in courses}
files=[p for c in courses for p in (UP/c['source']).rglob('*') if p.is_file() and p.suffix in ('.md','.ipynb','.py','.cs')]
routes={}; labs={}; unresolved=[]; coverage=[]; notebook_alignment=[]
for p in files:
 rel=p.relative_to(UP).as_posix();c=course_by_dir[rel.split('/')[0]]
 if rel==c['source']+'/README.md':routes[rel]='/lessons/'+c['slug']
 else:
  name=re.sub(r'[^a-zA-Z0-9-]+','-',str(Path(rel).with_suffix(''))).lower().strip('-')
  name += {'.ipynb':'-notebook','.py':'-script','.md':'-notes','.cs':'-csharp'}[p.suffix]
  routes[rel]='/labs/'+name;labs[rel]=routes[rel]
routes['README.md']='/guide/courses'
routes['translations/zh-CN/README.md']='/guide/courses'

def fix_text(text):
 for a,b in [('大型语言模型','大语言模型'),('AI代理','AI Agent'),('AI 代理','AI Agent'),('多智能体','多 Agent'),('多代理','多 Agent'),('智能体','Agent'),('微软代理框架','Microsoft Agent Framework'),('Microsoft 代理框架','Microsoft Agent Framework'),('Microsoft Agent 框架','Microsoft Agent Framework'),('Microsoft Foundry 代理服务','Microsoft Foundry Agent Service'),('代理式RAG','Agentic RAG'),('代理式 RAG','Agentic RAG'),('跟踪与跨度','调用链与执行片段'),('跨度','执行片段（Span）'),('磁性编排','Magentic 编排'),('内存连接器','记忆连接器'),('操作系统中提取','业务系统中提取'),('办公时间','答疑时间'),('您的','你的'),('您','你'),('令牌','Token'),('秘钥','密钥')]:text=text.replace(a,b)
 # unify agent term, without changing proxy-related technical language inside code
 text=text.replace('代理','Agent')
 text=text.replace('Agent间','Agent 间').replace('Agent的','Agent 的').replace('Agent框架','Agent 框架')
 return text

def canonical(rel):
 if rel.startswith('translations/zh-CN/'):return rel[len('translations/zh-CN/'):]
 return rel

def urlfix(url,source,image=False):
 url=url.strip().strip('<>');parts=urlsplit(url)
 if parts.scheme or url.startswith('//'):
  return url
 if url.startswith('#'):
  # Old heading slugs target immutable upstream, not potentially renamed Chinese headings.
  return BASE+quote(source)+'#'+quote(unquote(url[1:]))
 rel=posixpath.normpath(posixpath.join(posixpath.dirname(source),unquote(parts.path)))
 key=canonical(rel)
 if image:
  asset=DOC/'public/upstream-assets'/rel
  if asset.exists():return '/upstream-assets/'+quote(rel)
  unresolved.append({'source':source,'target':url,'type':'image'})
  return None
 if key+'/README.md' in routes:return routes[key+'/README.md']+'.md'
 if key in routes:return routes[key]+'.md' # drop stale anchors; the destination has a generated outline
 if (UP/rel).is_file() or (UP/key).is_file():return BASE+quote(key)+(('#'+parts.fragment) if parts.fragment else '')
 # Resolve source-root lesson paths occasionally written as bare repository paths.
 if parts.path in routes:return routes[parts.path]+'.md'
 unresolved.append({'source':source,'target':url,'type':'upstream-link'})
 return BASE+quote(key)+(('#'+parts.fragment) if parts.fragment else '')

def transform(text,source,english=None):
 text=correct(text,source,english)
 text=re.sub(r'<!-- CO-OP TRANSLATOR DISCLAIMER START -->.*?<!-- CO-OP TRANSLATOR DISCLAIMER END -->','',text,flags=re.S)
 text=re.sub(r'<!--.*?-->','',text,flags=re.S)
 # Retain videos as titled source links. Do not pretend a translation or caption exists.
 text=re.sub(r'\[!\[([^\]]*)\]\([^)]*\)\]\(([^)]+)\)',lambda m:'[原课程视频：'+fix_text(m[1])+']('+m[2]+')',text)
 text=re.sub(r'^>.*(?:点击上方图片|Click the image|缩略图将在|thumbnail to be).*\n?','',text,flags=re.M)
 text=re.sub(r'^.*(?:观看课程视频|Watch the lesson video):?.*$', '',text,flags=re.M) if source.endswith('18-securing-ai-agents/README.md') else text
 text=re.sub(r'<a\s[^>]*href=["\']([^"\']+)["\'][^>]*>(.*?)</a>',r'[\2](\1)',text,flags=re.S)
 text=re.sub(r'</?(?:strong|b)>','**',text);text=re.sub(r'</?(?:em|i)>','*',text)
 text=re.sub(r'<br\s*/?>',' ',text)
 pieces=re.split(r'(```[\s\S]*?```)',text)
 for i in range(0,len(pieces),2):
  t=fix_text(pieces[i])
  # Preserve <details>/<summary>; escape other HTML including placeholder names and Vue interpolation.
  t=re.sub(r'<(?!/?(?:details|summary)\b)([^>]+)>',lambda m:'&lt;'+html.escape(m[1])+'&gt;',t)
  t=t.replace('{{','&#123;&#123;').replace('}}','&#125;&#125;')
  def img(m):
   target=urlfix(m[2],source,True);alt=m[1] or '原课程示意图'
   if target and target.startswith(('http:','https:')):return '[查看原课程引用的外部截图：'+alt+']('+target+')（外部素材仅保留来源链接。）'
   if not target:return '[原课程配图：'+alt+']('+BASE+quote(canonical(source))+')（源图未能本地获取，参见原文。）'
   return f'![{alt}]({target})\n\n*图：{alt}。来源：Microsoft AI Agents for Beginners，MIT。*'
  t=re.sub(r'!\[([^\]]*)\]\(([^)]+)\)',img,t)
  t=re.sub(r'(?<!!)\[([^\]]+)\]\(([^)]+)\)',lambda m:'['+m[1]+']('+urlfix(m[2],source)+')' if not m[2].startswith('/upstream-assets/') else m[0],t)
  # Decorative banners are not part of the technical lesson.
  t=re.sub(r'^!\[[^\n]*\]\([^\n]*(?:thumbnail|lesson-\d)[^\n]*\)\n\n\*图：[^\n]*\*','',t,flags=re.M)
  pieces[i]=t
 for i in range(1,len(pieces),2):
  pieces[i]=re.sub(r'^```(?:bash\|powershell|bash \| powershell)', '```bash',pieces[i])
  pieces[i]=re.sub(r'^```(?:plaintext|console|output|Text|None|env)\b','```text',pieces[i])
 text=''.join(pieces)
 # End-of-lesson navigation is generated from metadata. Remove only those sections.
 text=re.sub(r'^## (?:上一课|下一课|Previous Lesson|Next Lesson)\n.*?(?=^## |\Z)','',text,flags=re.M|re.S)
 text=re.sub(r'^#{2,3} (?:[^\n]*更多疑问[^\n]*|[^\n]*有更多问题[^\n]*|[^\n]*还有疑问[^\n]*|有问题？|Got More Questions[^\n]*|卡住了吗？)\n.*?(?=^## |\Z)','',text,flags=re.M|re.S)
 return text.strip()

def fm(c,title=None):
 i=courses.index(c)
 prev=({'text':courses[i-1]['title'],'link':'/lessons/'+courses[i-1]['slug']} if i else {'text':'学习路线','link':'/guide/roadmap'})
 nex=({'text':courses[i+1]['title'],'link':'/lessons/'+courses[i+1]['slug']} if i<len(courses)-1 else {'text':'综合实践','link':'/guide/project'})
 return '---\n'+ '\n'.join(k+': '+json.dumps(v,ensure_ascii=False) for k,v in {'title':title or c['title'],'description':c['summary'],'course':c['slug'],'prev':prev,'next':nex}.items())+'\n---\n\n'

def cell_note(code):
 notes=[]
 checks=[('load_dotenv','配置加载：从本地环境读取端点与部署名；缺少变量时先修复配置，不要把密钥写进代码。'),('@tool','工具定义：类型注解和文档字符串描述输入、用途；模型产生调用请求，框架在应用进程中执行函数。检查是否需要人工批准。'),('BaseModel','数据结构：Pydantic 模型定义字段类型；只有传入实际的 response_format 并检查解析结果，才能约束本次输出。'),('create_session','会话状态：复用同一个 session 才会带上历史；新建会话与持久化存储是不同操作。'),('FoundryChatClient','模型连接：project_endpoint 是项目地址，model 是实际部署名称；credential 提供访问身份。客户端创建本身不证明已经部署服务端 Agent。'),('OpenAIChatClient','模型连接：检查此版本使用 Responses 还是 Chat Completions；接口兼容不能只靠更换 base_url 判断。'),('async def','异步执行：async def 定义协程，await 等待结果；普通 .py 脚本需要 asyncio.run() 入口，Notebook 支持顶层 await。'),('instructions','行为约束：instructions 引导模型，不能替代执行器的权限验证、次数限制和结果检查。'),('search','检索过程：跟踪查询、候选结果和实际选入的证据；检索为空时应明确返回缺失，而不是补写答案。'),('previous_receipt_hash','链式记录：核对前序收据的规范字节哈希，并另外验证各签名；链头需要可信外部锚点才能发现整段截断。'),('SigningKey','签名操作：私钥仅用于签名，验签必须使用独立信任的公钥；不要把收据自带的公钥直接当成可信身份。'),('exec(','代码执行边界：这里演示生成代码的执行；不要对不可信模型输出直接 exec。实际应用应使用隔离环境、时间/资源限制和最小权限。'),('print(','输出观察：print 展示应用可观察结果；预存输出和现场结果可能不同，它不是模型内部思考记录。')]
 for needle,note in checks:
  if needle in code:notes.append(note)
 return '\n\n'.join(notes[:3]) or '阅读提示：跟踪本单元格读取的变量、修改的状态以及返回值。按原顺序执行，确认依赖的前序变量已经存在。'

for c in courses:
 rel=c['source']+'/README.md';zrel='translations/zh-CN/'+rel;en=(UP/rel).read_text();zh=(UP/zrel).read_text()
 override=ROOT/'content/chapters'/f"{c['slug']}-body.md"
 body=override.read_text() if override.exists() else transform(zh,zrel,en)
 if not override.exists() and '```' in body and c['slug']!='security':body='::: info 原课程代码片段的阅读范围\n下方精读保留上游主要知识与片段，可能包含历史 SDK 写法、示意端点及未完整定义的函数；这些片段不等同于经过本站验证的完整程序。运行前优先阅读本章实际 Notebook 导读与版本校订。已验证的无 API 实验在“扩展实践”中另行标明。\n:::\n\n'+body
 if not override.exists():body=re.sub(r'^# (.+)$',r'## 原课程精读：\1',body,count=1,flags=re.M)
 intro=ROOT/'content/chapters'/f"{c['slug']}-intro.md";practice=ROOT/'content/chapters'/f"{c['slug']}-practice.md"
 start=intro.read_text() if intro.exists() else ''
 end=practice.read_text() if practice.exists() else ''
 lablinks=[(p,r) for p,r in labs.items() if p.startswith(c['source']+'/')]
 links='\n'.join(f'- [{Path(p).name}]({r}.md)' for p,r in lablinks)
 text=fm(c)+f"# {c['title']}\n\n"+start+'\n\n'+body+'\n\n'+end+'\n\n## 原课程代码与补充材料\n\n'
 text+='以下是本章实际源文件对应的阅读页。Notebook 已分解为说明、代码及原文件输出；云端示例未进行联网端到端验证。正文中的片段用于解释，运行时使用完整 Notebook 和准备篇的固定依赖。\n\n'+(links or '本章配置文件见[环境配置](./setup.md)与[来源清单](/guide/sources.md)。')
 text+=f"\n\n## 本章来源\n\n基于 [英文原文]({BASE+rel}) 与 [简体中文翻译]({BASE+zrel}) 整理，原作者为 Microsoft 与开源贡献者，采用 MIT 许可证。本页标明“补充讲解”与“扩展实践”的内容为本项目新增。\n\n来源提交：`{meta['commit'][:12]}` · 获取日期：{meta['retrieved']}。参见[版本校订记录](/guide/sources.md)。\n"
 (DOC/'lessons'/f"{c['slug']}.md").write_text(normalize(text))
 coverage.append({**c,'page':'docs/lessons/'+c['slug']+'.md','english':rel,'chinese':zrel,'englishChars':len(en),'chineseChars':len(zh),'pageChars':len(text),'code':[p for p,r in lablinks if p.endswith(('.ipynb','.py','.cs'))],'materials':[p for p,r in lablinks if p.endswith('.md')],'images':re.findall(r'!\[[^\]]*\]\(([^)]+)\)',text),'status':'teaching-complete' if override.exists() or (intro.exists() and practice.exists()) else 'source-imported','verification':'cloud-not-executed'})

for rel,route in labs.items():
 p=UP/rel;c=course_by_dir[rel.split('/')[0]];z=UP/'translations/zh-CN'/rel
 title=c['id']+' · '+p.stem
 header='---\ntitle: '+json.dumps(title,ensure_ascii=False)+'\noutline: [2, 3]\n---\n\n# '+title+'\n\n'
 header+=f"[返回：{c['title']}](/lessons/{c['slug']}.md) · [不可变原始文件]({BASE+quote(rel)})\n\n"
 if p.suffix=='.ipynb':
  nb=json.loads(p.read_text());zn=json.loads(z.read_text()) if z.exists() else nb
  # Translator appends a standalone disclaimer cell; exclude only that boilerplate before alignment.
  zn['cells']=[cell for cell in zn['cells'] if not (cell['cell_type']=='markdown' and 'CO-OP TRANSLATOR DISCLAIMER START' in ''.join(cell.get('source',[])))]
  # Align by cell index only when type sequences agree; code always comes from English original.
  aligned=[v['cell_type'] for v in nb['cells']]==[v['cell_type'] for v in zn['cells']]
  notebook_alignment.append({'path':rel,'englishCells':len(nb['cells']),'chineseCellsWithoutDisclaimer':len(zn['cells']),'aligned':aligned,'codeSource':'English original'})
  header+='::: warning 原课程完整 Notebook · 静态阅读与代码解析\n代码按英文源文件顺序保留，中文说明以同版本译本为基础。原始安装单元格可能含无版本上限的 `-U`；请跳过它们，先按[准备篇](/lessons/setup.md)固定依赖。云端服务、模型权限、网站布局和部分 SDK 接口需在你自己的环境验证。本站没有执行云端请求；第 18 章的离线验证状态单独记录在[检查报告](/guide/verification.md)。\n:::\n\n'
  header+='## 运行准备\n\nPython 3.12+；在独立虚拟环境安装源仓库依赖与本页中声明的额外依赖。原文件路径：`upstream/'+rel+'`。以原仓库根目录为工作目录，在 Jupyter 中按顺序执行；身份与环境变量见准备篇。\n\n```bash\ncd upstream\npython -m jupyterlab\n```\n\n'
  header+=f'[下载原始 Notebook](/notebooks/{quote(rel)})。输出为上游文件保存的历史结果，不能用作本站实测证明。\n\n'
  target=DOC/'public/notebooks'/rel;target.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,target)
  for i,cell in enumerate(nb['cells']):
   code=''.join(cell.get('source',[]))
   if not code.strip():continue
   if cell['cell_type']=='markdown':
    t=''.join(zn['cells'][i].get('source',[])) if aligned else code
    t=transform(t,('translations/zh-CN/' if aligned and z.exists() else '')+rel)
    sections=re.split(r'(```[\s\S]*?```)',t)
    for si in range(0,len(sections),2):sections[si]=re.sub(r'^# ', '## ',sections[si],flags=re.M)
    t=''.join(sections)
    header+=t+'\n\n'
   else:
    lang='csharp' if ('dotnet' in p.name or 'dotNET' in rel) else 'python'
    if code.lstrip().startswith(('%pip','! pip','!pip')):lang='text'
    header+=f'### 代码单元格 {i+1}\n\n'+cell_note(code)+f'\n\n```{lang}\n'+code.strip()+'\n```\n\n'
    outs=[]
    for o in cell.get('outputs',[]):
     raw=o.get('text') or o.get('data',{}).get('text/plain') or []
     if raw:outs.append(''.join(raw) if isinstance(raw,list) else raw)
    if outs:header+='::: details 原文件保存的输出（不是本项目实测）\n\n```text\n'+re.sub(r'\x1b\[[0-9;]*m','', '\n'.join(outs)).strip()+'\n```\n\n:::\n\n'
 elif p.suffix in ('.py','.cs'):
  code=p.read_text();header+='::: info 原课程脚本 · 未联网执行\n保留原始框架与完整代码。依赖、变量、入口以脚本及其相邻 README 为准；本页为代码导读，未声称所有外部服务均已验证。\n:::\n\n'+cell_note(code)+'\n\n```'+('csharp' if p.suffix=='.cs' else 'python')+'\n'+code+'\n```\n'
 else:
  header+='::: info 原课程补充材料\n'+('根据对应简体中文译本整理。' if z.exists() else '上游没有对应中文文件，以下保留英文资料；关联中文章节提供概念与实践说明。')+'原代码片段未进行云端验证。\n:::\n\n'
  header+=transform(z.read_text() if z.exists() else p.read_text(),('translations/zh-CN/' if z.exists() else '')+rel)
 out=DOC/(route.lstrip('/')+'.md');out.parent.mkdir(parents=True,exist_ok=True);out.write_text(normalize(header))
(ROOT/'provenance/course-map.json').write_text(json.dumps(coverage,ensure_ascii=False,indent=2)+'\n')
(ROOT/'provenance/page-map.json').write_text(json.dumps(routes,ensure_ascii=False,indent=2)+'\n')
(ROOT/'provenance/unresolved-source-links.json').write_text(json.dumps(unresolved,ensure_ascii=False,indent=2)+'\n')
(ROOT/'provenance/notebook-alignment.json').write_text(json.dumps(notebook_alignment,ensure_ascii=False,indent=2)+'\n')
print('Converted',len(courses),'chapters and',len(labs),'source materials')

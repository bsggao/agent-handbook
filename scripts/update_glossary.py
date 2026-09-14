from pathlib import Path
import json
R=Path(__file__).resolve().parents[1];p=R/'docs/guide/glossary.md';s=p.read_text().split('## 全部术语与定义')[0]
terms=json.loads((R/'content/glossary.json').read_text())
s+='## 全部术语与定义\n\n以下静态词条便于全站搜索、直接链接和禁用脚本时阅读。\n\n'
s+='\n\n'.join(f"### {t['zh']} · {t['en']}\n\n{t['definition']} [相关课程](/lessons/{t['lesson']}.md)。" for t in terms)+'\n';p.write_text(s)

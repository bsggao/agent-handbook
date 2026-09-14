"""Keep Chinese punctuation adjacent to bold spans compatible with CommonMark."""
from pathlib import Path
import re

def normalize(text):
    parts=re.split(r'(```[\s\S]*?```)',text)
    for i in range(0,len(parts),2):
        parts[i]=re.sub(r'[ \t]*\*\*([^\n]+?)\*\*[ \t]*',lambda m:' **'+m[1].strip()+'** ',parts[i])
        parts[i]=re.sub(r'Agent(?=[\u3400-\u9fff])','Agent ',parts[i])
        parts[i]=re.sub(r'(?<=[\u3400-\u9fff])Agent',' Agent',parts[i])
    return ''.join(parts)
if __name__=='__main__':
    for p in (Path(__file__).resolve().parents[1]/'docs').rglob('*.md'):
        if '.vitepress' not in p.parts:p.write_text(normalize(p.read_text()))

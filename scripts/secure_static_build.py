"""Externalize VitePress 1.6.4 bootstraps for the host's script-src 'self' CSP.

Only trusted build-time configuration functions are emitted as JavaScript source;
the browser never evaluates a serialized function or needs unsafe-eval/inline.
Fail closed if VitePress changes its bootstrap format.
"""
from pathlib import Path
import hashlib, json, os, re

ROOT = Path(__file__).resolve().parents[1]
BASE = os.environ.get('BASE_PATH', '/')
DIST = ROOT / 'dist'


def js_literal(value):
    if isinstance(value, str) and value.startswith('_vp-fn_'):
        source = value.removeprefix('_vp-fn_')
        # This is the only function intentionally serialized by our config.
        if not source.startswith('function tokenize(text) {'):
            raise ValueError('Unexpected function in VitePress site configuration')
        return '(' + source + ')'
    if isinstance(value, dict):
        return '{' + ','.join(json.dumps(k) + ':' + js_literal(v) for k, v in value.items()) + '}'
    if isinstance(value, list):
        return '[' + ','.join(js_literal(v) for v in value) + ']'
    return json.dumps(value, ensure_ascii=False)


def static_bootstrap(code):
    declaration = 'function deserializeFunctions('
    if declaration not in code:
        return code
    prefix, rest = code.split(declaration, 1)
    marker = 'window.__VP_SITE_DATA__=deserializeFunctions(JSON.parse('
    serialized = rest.split(marker, 1)[1]
    encoded, end = json.JSONDecoder().raw_decode(serialized)
    if serialized[end:].strip() != '));':
        raise ValueError('VitePress bootstrap format changed')
    return prefix + 'window.__VP_SITE_DATA__=' + js_literal(json.loads(encoded)) + ';'


def main():
    if not BASE.startswith('/') or not BASE.endswith('/'):
        raise ValueError('BASE_PATH must start and end with /')
    scripts = set()
    pattern = re.compile(r'<script\b([^>]*)>(.*?)</script>', re.S)

    def replace(match):
        attrs, code = match.groups()
        if re.search(r'\bsrc\s*=', attrs) or not code.strip():
            return match.group(0)
        code = static_bootstrap(code)
        if 'new Function(' in code or 'eval(' in code:
            raise ValueError('Dynamic evaluation remains in bootstrap')
        filename = 'bootstrap.' + hashlib.sha256(code.encode()).hexdigest()[:16] + '.js'
        (DIST / 'assets' / filename).write_text(code, encoding='utf-8')
        scripts.add(filename)
        return f'<script{attrs} src="{BASE}assets/{filename}"></script>'

    pages = list(DIST.rglob('*.html'))
    for page in pages:
        page.write_text(pattern.sub(replace, page.read_text()), encoding='utf-8')
    print(f'CSP: externalized inline scripts in {len(pages)} pages → {len(scripts)} shared scripts; no eval')


if __name__ == '__main__':
    main()

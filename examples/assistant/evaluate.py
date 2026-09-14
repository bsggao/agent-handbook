"""Offline regression set; deterministic behavior only, not LLM quality evaluation."""
import tempfile
from pathlib import Path
from app import run

cases = [
    ('退款', '7 天', 'refund-policy'),
    ('定制商品可以退款吗', '定制商品', 'custom-policy'),
    ('多久送达', '3 个工作日', 'shipping'),
    ('如何重置密码', '已验证邮箱', 'account'),
    ('火星上的酒店', '没有足够证据', None),
    ('创建任务：复习', 'APPROVAL_REQUIRED', None),
]
with tempfile.TemporaryDirectory() as directory:
    passed=0
    for question, expected, citation in cases:
        result=run(question,directory=Path(directory))
        ok=expected in result['answer'] and (citation is None or citation in result['citations'])
        print(('PASS' if ok else 'FAIL')+' '+question)
        passed+=ok
    print(f'{passed}/{len(cases)} passed (simulation only)')
    raise SystemExit(0 if passed==len(cases) else 1)

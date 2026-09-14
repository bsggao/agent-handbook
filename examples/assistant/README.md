# 文档问答与任务助手（扩展实践）

Python 3.12+，默认只依赖标准库，不需要账号、API Key 或 pip 安装。
所有默认输出由明确的规则模拟模型行为；词法检索是真实执行的，未使用向量模型。

从网站项目根目录运行：

```bash
python3 examples/assistant/app.py --stage 1
python3 examples/assistant/app.py '现在有多少个任务？' --stage 2
python3 examples/assistant/app.py '购买后多久可以申请退款？' --stage 3
python3 examples/assistant/app.py '退款政策是什么？' --stage 4 --remember '简洁回答'
python3 examples/assistant/app.py '创建任务：复习 RAG' --stage 5
python3 examples/assistant/app.py '创建任务：复习 RAG' --stage 5 --approve --request-id learning-001
python3 examples/assistant/evaluate.py
python3 -m unittest discover -s examples/assistant -p 'test_*.py' -v
```

最后两次分别返回 `APPROVAL_REQUIRED` 和本地任务 T1；使用相同 request-id 重跑相同创建动作会去重。新建另一项独立任务应使用新 ID。
默认 `.assistant-data/` 存储仅限本地演示，`--user` 是本地命名空间，不是认证。
`--forget` 删除当前 user 对应文件里的记忆和任务。不要用这个 JSON 存储支持并发服务器。

`--budget` 使用字符数（不是 Token）；`--max-calls` 为工具次数预算。运行结果包括候选片段、选中文档 ID、引用、工具调用计数和最小应用事件。

可选真实 MAF 实验，可能计费；已做静态检查，未执行云端请求：

```bash
python3 -m venv .venv-cloud
source .venv-cloud/bin/activate
python -m pip install -r examples/assistant/requirements-cloud.txt
cp .env.example .env
# 填写 .env，创建模型部署，并使用有权限的账号登录
az login
python examples/assistant/cloud.py
```

云端实验只提供只读文档检索工具，不执行任务创建。预期回答包含普通与定制商品政策及文档 ID；准确文字取决于模型，需人工核对。
完整的分阶段教学、文件解析、验收与扩展练习位于网站 `/guide/project.html`。

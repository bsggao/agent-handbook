---
title: "17 · 17-local-agent-foundry-local"
outline: [2, 3]
---

# 17 · 17-local-agent-foundry-local

[返回：本地 Agent](/lessons/local-agents.md) · [不可变原始文件](https://github.com/microsoft/ai-agents-for-beginners/blob/25b7985f3b2dc37a84f4a7387ccd3c9f0e5b1595/17-creating-local-ai-agents/code_samples/17-local-agent-foundry-local.ipynb)

::: warning 原课程完整 Notebook · 静态阅读与代码解析
代码按英文源文件顺序保留，中文说明以同版本译本为基础。原始安装单元格可能含无版本上限的 `-U`；请跳过它们，先按[准备篇](/lessons/setup.md)固定依赖。云端服务、模型权限、网站布局和部分 SDK 接口需在你自己的环境验证。本站没有执行云端请求；第 18 章的离线验证状态单独记录在[检查报告](/guide/verification.md)。
:::

## 运行准备

Python 3.12+；在独立虚拟环境安装源仓库依赖与本页中声明的额外依赖。原文件路径：`upstream/17-creating-local-ai-agents/code_samples/17-local-agent-foundry-local.ipynb`。以原仓库根目录为工作目录，在 Jupyter 中按顺序执行；身份与环境变量见准备篇。

```bash
cd upstream
python -m jupyterlab
```

[下载原始 Notebook](/notebooks/17-creating-local-ai-agents/code_samples/17-local-agent-foundry-local.ipynb)。输出为上游文件保存的历史结果，不能用作本站实测证明。

## 第17课 - 使用 Foundry Local 和 Qwen 创建本地 AI Agent

在本笔记本中，你将构建一个 **本地工程助理** ，它完全运行在你的工作站上。整个过程中不使用任何云推理。该助理可以：

1. 通过 Foundry Local 的 Qwen 函数调用 **调用工具** 。
2. **列出和读取** 沙盒项目目录中的文件。
3. 用简单指标 **分析代码** 。
4. 通过本地 RAG（Chroma） **搜索文档** 。
5. **使用本地 MCP 服务器** （如果未配置则优雅跳过）。

Agent 代码几乎与云端课程相同——唯一不同的是客户端端点从云端移到了`localhost`。

## 设置

在运行此笔记本之前：

1. **安装 Microsoft Foundry Local** （请参阅适用于你的操作系统的[文档](https://learn.microsoft.com/azure/ai-foundry/foundry-local/)）。
2. **下载并启动 Qwen 模型：** 
   ```bash
   foundry model run qwen2.5-7b-instruct
   foundry service status
   ```
3. 安装以下 Python 包。

所有操作均在本地运行。配备约 8 GB 内存的机器是一个现实的最低要求。

### 代码单元格 3

阅读提示：跟踪本单元格读取的变量、修改的状态以及返回值。按原顺序执行，确认依赖的前序变量已经存在。

```text
%pip install foundry-local-sdk openai chromadb -q
```

## 1. 连接到 Foundry Local

`FoundryLocalManager` 会在需要时下载模型，启动本地服务，并为我们提供一个 **兼容 OpenAI 的端点** 。然后我们将标准的 OpenAI SDK 指向该端点。API 密钥是本地占位符 — 不涉及任何云端凭证。

### 代码单元格 5

输出观察：print 展示应用可观察结果；预存输出和现场结果可能不同，它不是模型内部思考记录。

```python
from foundry_local import FoundryLocalManager
from openai import OpenAI

MODEL_ALIAS = "qwen2.5-7b-instruct"

# Foundry Local selects the best build for your hardware (CPU / GPU / NPU) automatically.
manager = FoundryLocalManager(MODEL_ALIAS)
model_info = manager.get_model_info(MODEL_ALIAS)

client = OpenAI(
    base_url=manager.endpoint,   # e.g. http://localhost:PORT/v1
    api_key=manager.api_key,     # local placeholder
)

MODEL_ID = model_info.id
print(f"Connected to Foundry Local. Serving: {MODEL_ID}")
print(f"Endpoint: {manager.endpoint}")
```

### 代码单元格 6

输出观察：print 展示应用可观察结果；预存输出和现场结果可能不同，它不是模型内部思考记录。

```python
# Quick sanity check: a plain chat completion, running fully on-device.
resp = client.chat.completions.create(
    model=MODEL_ID,
    messages=[{"role": "user", "content": "In one sentence, what is a small language model?"}],
)
print(resp.choices[0].message.content)
```

## 2. 本地工具（沙盒文件操作）

我们在磁盘上创建一个小型示例项目，然后定义作用于该项目根目录的工具。即使在本地，沙盒检查也很重要：一个读取任意路径的工具运行时权限与你的用户权限相同，可以访问你能访问的任何内容。

### 代码单元格 8

输出观察：print 展示应用可观察结果；预存输出和现场结果可能不同，它不是模型内部思考记录。

```python
import json
from pathlib import Path

# Create a tiny sample project so the notebook is self-contained.
PROJECT_ROOT = Path.cwd() / "sample_project"
PROJECT_ROOT.mkdir(exist_ok=True)

(PROJECT_ROOT / "auth.py").write_text(
    '"""Authentication helpers."""\n\n'
    "def login(user, password):\n"
    "    # TODO: hash the password before comparing\n"
    "    return user == 'admin' and password == 'secret'\n\n"
    "def logout(session):\n"
    "    session.clear()\n",
    encoding="utf-8",
)
(PROJECT_ROOT / "utils.py").write_text(
    '"""Utility functions."""\n\n'
    "def clamp(value, low, high):\n"
    "    return max(low, min(value, high))\n",
    encoding="utf-8",
)
print("Sample project created at:", PROJECT_ROOT)
```

### 代码单元格 9

输出观察：print 展示应用可观察结果；预存输出和现场结果可能不同，它不是模型内部思考记录。

```python
def _safe_path(path: str) -> Path | None:
    """Resolve a path and confirm it stays inside the project sandbox."""
    full = (PROJECT_ROOT / path).resolve()
    if full == PROJECT_ROOT or PROJECT_ROOT in full.parents:
        return full
    return None


def list_files() -> str:
    """List files in the project directory."""
    files = [p.name for p in PROJECT_ROOT.iterdir() if p.is_file()]
    return ", ".join(files) if files else "(no files)"


def read_file(path: str) -> str:
    """Read a file, but only inside the sandboxed project directory."""
    full = _safe_path(path)
    if full is None:
        return "Access denied: path is outside the project directory."
    if not full.is_file():
        return f"No such file: {path}"
    return full.read_text(encoding="utf-8")


def analyze_code(path: str) -> str:
    """Report simple metrics about a source file."""
    full = _safe_path(path)
    if full is None or not full.is_file():
        return "File not found or access denied."
    text = full.read_text(encoding="utf-8")
    lines = text.splitlines()
    return json.dumps({
        "path": path,
        "lines": len(lines),
        "functions": sum(1 for ln in lines if ln.strip().startswith("def ")),
        "todos": sum(1 for ln in lines if "TODO" in ln or "FIXME" in ln),
    })


print(list_files())
```

## 3. 使用 Chroma 的本地 RAG

我们将一小部分文档片段嵌入到本地 Chroma 集合中。Chroma 在进程内运行并将向量存储在磁盘上——无需服务器，无需云。`search_docs` 工具检索与查询最相关的片段。

### 代码单元格 11

检索过程：跟踪查询、候选结果和实际选入的证据；检索为空时应明确返回缺失，而不是补写答案。

输出观察：print 展示应用可观察结果；预存输出和现场结果可能不同，它不是模型内部思考记录。

```python
import chromadb

DOCS = {
    "auth": "The login() function checks credentials. It currently compares passwords in plain text, which should be hashed.",
    "sessions": "Sessions are cleared on logout via session.clear(). Sessions are stored in memory and lost on restart.",
    "utils": "clamp(value, low, high) constrains a number to a range. Used throughout the UI layer for bounds checking.",
    "style": "This project follows PEP 8. Functions use snake_case and modules include a docstring at the top.",
}

# Chroma ships with a local default embedding model, so embedding stays on-device.
chroma_client = chromadb.Client()
collection = chroma_client.get_or_create_collection("project_docs")
collection.upsert(
    ids=list(DOCS.keys()),
    documents=list(DOCS.values()),
)


def search_docs(query: str) -> str:
    """Search the local documentation index for relevant snippets."""
    results = collection.query(query_texts=[query], n_results=2)
    docs = results.get("documents", [[]])[0]
    return "\n".join(docs) if docs else "No relevant documentation found."


print(search_docs("how are passwords handled?"))
```

## 4. 工具调用循环

现在我们使用 OpenAI 工具架构向模型注册工具，并运行标准的工具调用循环——模型请求一个工具，我们在本地执行该工具，将结果反馈回去，并重复该过程，直到模型生成最终答案。Qwen 的可靠函数调用使得这能在设备上运行。

### 代码单元格 13

检索过程：跟踪查询、候选结果和实际选入的证据；检索为空时应明确返回缺失，而不是补写答案。

```python
TOOLS_SCHEMA = [
    {"type": "function", "function": {
        "name": "list_files", "description": "List files in the project directory.",
        "parameters": {"type": "object", "properties": {}},
    }},
    {"type": "function", "function": {
        "name": "read_file", "description": "Read a file inside the project directory.",
        "parameters": {"type": "object", "properties": {
            "path": {"type": "string", "description": "File name, e.g. auth.py"}}, "required": ["path"]},
    }},
    {"type": "function", "function": {
        "name": "analyze_code", "description": "Report line count, function count and TODO count for a file.",
        "parameters": {"type": "object", "properties": {
            "path": {"type": "string"}}, "required": ["path"]},
    }},
    {"type": "function", "function": {
        "name": "search_docs", "description": "Search local documentation for a query.",
        "parameters": {"type": "object", "properties": {
            "query": {"type": "string"}}, "required": ["query"]},
    }},
]

TOOL_IMPL = {
    "list_files": list_files,
    "read_file": read_file,
    "analyze_code": analyze_code,
    "search_docs": search_docs,
}

SYSTEM_PROMPT = (
    "You are a local engineering assistant. Use the provided tools to inspect the project "
    "and its documentation. Prefer calling a tool over guessing. Be concise."
)
```

### 代码单元格 14

输出观察：print 展示应用可观察结果；预存输出和现场结果可能不同，它不是模型内部思考记录。

```python
def run_agent(user_query: str, max_iterations: int = 5) -> str:
    """Standard tool-calling loop, running entirely against the local model."""
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": user_query},
    ]

    for _ in range(max_iterations):
        response = client.chat.completions.create(
            model=MODEL_ID,
            messages=messages,
            tools=TOOLS_SCHEMA,
        )
        msg = response.choices[0].message

        if not msg.tool_calls:
            return msg.content or "(no answer)"

        # Record the assistant's tool-call request.
        messages.append({
            "role": "assistant",
            "content": msg.content,
            "tool_calls": [tc.model_dump() for tc in msg.tool_calls],
        })

        # Execute each requested tool locally and feed results back.
        for tc in msg.tool_calls:
            name = tc.function.name
            args = json.loads(tc.function.arguments or "{}")
            result = TOOL_IMPL[name](**args) if name in TOOL_IMPL else f"Unknown tool: {name}"
            messages.append({
                "role": "tool",
                "tool_call_id": tc.id,
                "content": str(result),
            })

    return "Stopped: reached max tool-calling iterations."


print("Agent ready.")
```

### 代码单元格 15

输出观察：print 展示应用可观察结果；预存输出和现场结果可能不同，它不是模型内部思考记录。

```python
# A file-reading question.
print(run_agent("What does auth.py do, and is there anything to fix in it?"))
```

### 代码单元格 16

输出观察：print 展示应用可观察结果；预存输出和现场结果可能不同，它不是模型内部思考记录。

```python
# A RAG question.
print(run_agent("According to the docs, how are passwords currently handled?"))
```

### 代码单元格 17

输出观察：print 展示应用可观察结果；预存输出和现场结果可能不同，它不是模型内部思考记录。

```python
# A code-analysis question.
print(run_agent("How many functions and TODOs are in auth.py?"))
```

## 5. 本地 MCP（可选）

MCP 是一种传输方式，而非云服务——MCP 服务器可以作为一个本地进程通过 `stdio` 运行。下面的单元展示了如果你配置了一个本地 MCP 服务器（例如文件系统服务器），如何连接它。当 `LOCAL_MCP_COMMAND` 未设置时，它会优雅地跳过，因此笔记本仍能端到端运行。

安全提示：本地 MCP 服务器以你的用户权限运行。请将其限定在项目目录范围内，并在使用其输出之前进行验证。

### 代码单元格 19

异步执行：async def 定义协程，await 等待结果；普通 .py 脚本需要 asyncio.run() 入口，Notebook 支持顶层 await。

输出观察：print 展示应用可观察结果；预存输出和现场结果可能不同，它不是模型内部思考记录。

```python
import os

LOCAL_MCP_COMMAND = os.getenv("LOCAL_MCP_COMMAND")  # e.g. "npx -y @modelcontextprotocol/server-filesystem ./sample_project"

if not LOCAL_MCP_COMMAND:
    print("No LOCAL_MCP_COMMAND set — skipping the MCP demo. "
          "Set it to a local MCP server command to try this section.")
else:
    import asyncio
    from mcp import ClientSession, StdioServerParameters
    from mcp.client.stdio import stdio_client

    async def list_mcp_tools(command: str):
        parts = command.split()
        params = StdioServerParameters(command=parts[0], args=parts[1:])
        async with stdio_client(params) as (read, write):
            async with ClientSession(read, write) as session:
                await session.initialize()
                tools = await session.list_tools()
                return [t.name for t in tools.tools]

    names = await list_mcp_tools(LOCAL_MCP_COMMAND)
    print("Local MCP server exposes tools:", names)
```

## 摘要

你构建了一个完全在你的机器上运行的工程助理：

- **Foundry Local** 在一个兼容OpenAI的端点后面提供了一个 **Qwen** 模型——因此 Agent 代码与云端课程相匹配。
- **沙盒工具** 让 Agent 获得文件访问和代码分析能力，而无需离开项目目录。
- **Chroma** 提供了针对文档的 **本地RAG** 。
- **本地MCP** 展示了如何离线重用MCP生态系统。

在任何阶段都没有使用云端推理。

### 挑战

扩展本地 Agent 以：

1. **支持多个MCP服务器** —— 连接一个文件系统服务器和一个git服务器，让 Agent 能在它们之间做出选择。
2. **使用本地内存** —— 将简短的对话历史持久化到磁盘，以便助手能在笔记本重启后记住之前的对话内容。
3. **支持本地多 Agent 编排** —— 添加第二个本地 Agent（例如审阅者），让两个 Agent 协作完成任务。

在下一课中，你将学习如何保护部署的AI Agent。


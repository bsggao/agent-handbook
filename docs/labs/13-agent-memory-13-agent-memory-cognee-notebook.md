---
title: "13 · 13-agent-memory-cognee"
outline: [2, 3]
---

# 13 · 13-agent-memory-cognee

[返回：Agent 记忆](/lessons/memory.md) · [不可变原始文件](https://github.com/microsoft/ai-agents-for-beginners/blob/25b7985f3b2dc37a84f4a7387ccd3c9f0e5b1595/13-agent-memory/13-agent-memory-cognee.ipynb)

::: warning 原课程完整 Notebook · 静态阅读与代码解析
代码按英文源文件顺序保留，中文说明以同版本译本为基础。原始安装单元格可能含无版本上限的 `-U`；请跳过它们，先按[准备篇](/lessons/setup.md)固定依赖。云端服务、模型权限、网站布局和部分 SDK 接口需在你自己的环境验证。本站没有执行云端请求；第 18 章的离线验证状态单独记录在[检查报告](/guide/verification.md)。
:::

## 运行准备

Python 3.12+；在独立虚拟环境安装源仓库依赖与本页中声明的额外依赖。原文件路径：`upstream/13-agent-memory/13-agent-memory-cognee.ipynb`。以原仓库根目录为工作目录，在 Jupyter 中按顺序执行；身份与环境变量见准备篇。

```bash
cd upstream
python -m jupyterlab
```

[下载原始 Notebook](/notebooks/13-agent-memory/13-agent-memory-cognee.ipynb)。输出为上游文件保存的历史结果，不能用作本站实测证明。

## 课程13 - 带有Cognee知识图谱的 Agent 记忆

## 设置

本笔记本演示如何使用 [ **Cognee** ](https://www.cognee.ai/) 知识图谱和 **Microsoft Agent Framework** (MAF) 构建具有持久内存的智能 **编码助手** 。

Cognee 将非结构化文本转化为结构化、可查询的知识图谱，背后由向量嵌入支持——为你的 Agent 提供丰富的、关系感知的长期记忆。

### 你将学习到
1. **构建知识图谱** : 将开发者档案和最佳实践转化为结构化、可查询的知识。
2. **集成 Cognee 与 MAF** : 使用 `@tool` 函数让 MAF Agent 查询 Cognee 的知识图谱。
3. **会话感知对话** : 维护同一会话中多个问题的上下文。
4. **长期记忆** : 在会话之间持久保存重要知识，并在新对话中检索。

### 先决条件
- Python 3.9+
- 本地运行的 Redis (`docker run -d -p 6379:6379 redis`) 用于会话管理
- 一个 LLM API 密钥（例如 OpenAI）——在 `.env` 中设置 `LLM_API_KEY`
- `.env` 中设置 `CACHING=true`（Cognee 会话所需）
- 一个部署了聊天模型的 Microsoft Foundry 项目
- `.env` 中设置 `AZURE_AI_PROJECT_ENDPOINT` 和 `AZURE_AI_MODEL_DEPLOYMENT_NAME`
- 已通过 Azure CLI 验证身份（`az login`）

### 代码单元格 3

阅读提示：跟踪本单元格读取的变量、修改的状态以及返回值。按原顺序执行，确认依赖的前序变量已经存在。

```text
%pip install agent-framework azure-ai-projects azure-identity "cognee[redis]==0.4.0" -q
```

### 代码单元格 4

配置加载：从本地环境读取端点与部署名；缺少变量时先修复配置，不要把密钥写进代码。

模型连接：project_endpoint 是项目地址，model 是实际部署名称；credential 提供访问身份。客户端创建本身不证明已经部署服务端 Agent。

检索过程：跟踪查询、候选结果和实际选入的证据；检索为空时应明确返回缺失，而不是补写答案。

```python
import os
from pathlib import Path
from typing import Annotated

from dotenv import load_dotenv

load_dotenv()

os.environ["LLM_API_KEY"] = os.getenv("LLM_API_KEY", "")
os.environ["CACHING"] = os.getenv("CACHING", "true")

import cognee
from cognee.modules.search.types import SearchType

from agent_framework import tool
from agent_framework.foundry import FoundryChatClient
from azure.identity import AzureCliCredential

print(f"Cognee version: {cognee.__version__}")
print(f"CACHING: {os.environ.get('CACHING')}")
```

### 代码单元格 5

模型连接：project_endpoint 是项目地址，model 是实际部署名称；credential 提供访问身份。客户端创建本身不证明已经部署服务端 Agent。

输出观察：print 展示应用可观察结果；预存输出和现场结果可能不同，它不是模型内部思考记录。

```python
provider = FoundryChatClient(
    project_endpoint=os.environ["AZURE_AI_PROJECT_ENDPOINT"],
    model=os.environ["AZURE_AI_MODEL_DEPLOYMENT_NAME"],
    credential=AzureCliCredential(),
)

print("✅ FoundryChatClient created")
```

## Agent 记忆类型

本笔记本探讨了主课程第13课笔记本中的相同三种记忆类型，但使用 Cognee 作为长期记忆后端：

| 记忆类型 | 机制 | 生命周期 |
|---|---|---|
| **工作记忆** | `agent.create_session()` (MAF) | 单次对话 |
| **短期记忆** | Cognee 会话缓存 (Redis) | 单次会话 |
| **长期记忆** | Cognee 知识图谱 + 向量 | 永久 |

### Cognee 的记忆架构
```
┌──────────────────────────┐
│      Raw Data            │  (developer profiles, docs, conversations)
└───────────┬──────────────┘
            │  cognee.add() + cognee.cognify()
            ▼
┌──────────────────────────────────────────┐
│  Knowledge Graph + Vector Embeddings     │
└───────────┬──────────────────────────────┘
            │  cognee.search()
            ▼
┌──────────────────┐       ┌────────────────┐
│  MAF Agent       │──────▶│  @tool funcs   │
│  (AgentSession)  │       │  wrapping       │
│                  │       │  cognee.search  │
└──────────────────┘       └────────────────┘
```

## 准备 Cognee 存储

### 代码单元格 8

输出观察：print 展示应用可观察结果；预存输出和现场结果可能不同，它不是模型内部思考记录。

```python
DATA_ROOT = Path('.data_storage').resolve()
SYSTEM_ROOT = Path('.cognee_system').resolve()

DATA_ROOT.mkdir(parents=True, exist_ok=True)
SYSTEM_ROOT.mkdir(parents=True, exist_ok=True)

cognee.config.data_root_directory(str(DATA_ROOT))
cognee.config.system_root_directory(str(SYSTEM_ROOT))

await cognee.prune.prune_data()
await cognee.prune.prune_system(metadata=True)
print("✅ Cognee storage configured and reset")
```

## 第一部分 — 构建知识库

我们摄取三种类型的数据，以创建一个全面的编程助手知识库：

1. **开发者个人资料** — 个人专业知识和技术背景
2. **Python最佳实践** — Python之禅及实用指南
3. **历史对话** — 开发者与AI助手之间的过去问答记录

### 代码单元格 10

输出观察：print 展示应用可观察结果；预存输出和现场结果可能不同，它不是模型内部思考记录。

```python
developer_intro = (
    "Hi, I'm an AI/Backend engineer. "
    "I build FastAPI services with Pydantic, heavy asyncio/aiohttp pipelines, "
    "and production testing via pytest-asyncio. "
    "I've shipped low-latency APIs on AWS, Azure, and GoogleCloud."
)

python_zen_principles = """
# The Zen of Python: Practical Guide

## Key Principles With Guidance

### 1. Beautiful is better than ugly
Prefer descriptive names, clear structure, and consistent formatting.

### 2. Explicit is better than implicit
Be clear about behavior, imports, and types.

### 3. Simple is better than complex
Choose straightforward solutions first.

### 4. Flat is better than nested
Use early returns to reduce indentation.

## Modern Python Tie-ins
- Type hints reinforce explicitness
- Context managers enforce safe resource handling
- Dataclasses improve readability for data containers
"""

human_agent_conversations = """
"conversations": [
    {
      "topic": "async/await patterns",
      "user_query": "I'm building a web scraper that needs to handle thousands of URLs concurrently. What's the best way to structure this with asyncio?",
      "assistant_response": "Use asyncio with aiohttp, a semaphore to cap concurrency, TCPConnector for connection pooling, and context managers for session lifecycle."
    },
    {
      "topic": "dataclass vs pydantic",
      "user_query": "When should I use dataclasses vs Pydantic models?",
      "assistant_response": "For API input/output, prefer Pydantic: runtime validation, type coercion, JSON serialization. Integrates cleanly with FastAPI."
    },
    {
      "topic": "testing patterns",
      "user_query": "What's the best approach for pytest with async functions?",
      "assistant_response": "Use pytest-asyncio, async fixtures, and an isolated test database or mocks to reliably test async code."
    },
    {
      "topic": "error handling and logging",
      "user_query": "What's the best approach for production-ready error management?",
      "assistant_response": "Centralized error handling with custom exceptions, structured logging, and FastAPI middleware."
    }
  ]
"""

print("✅ Data sources prepared")
```

### 代码单元格 11

输出观察：print 展示应用可观察结果；预存输出和现场结果可能不同，它不是模型内部思考记录。

```python
await cognee.add(developer_intro, node_set=["developer_data"])
await cognee.add(human_agent_conversations, node_set=["developer_data"])
await cognee.add(python_zen_principles, node_set=["principles_data"])

await cognee.cognify()
print("✅ Knowledge graph built")
```

## 可视化知识图谱

Cognee 可以渲染它提取的实体和关系的交互式 HTML 可视化。

### 代码单元格 13

输出观察：print 展示应用可观察结果；预存输出和现场结果可能不同，它不是模型内部思考记录。

```python
from cognee import visualize_graph

await visualize_graph('./cognee_graph.html')
print("📊 Graph saved to cognee_graph.html — open it in a browser to explore.")
```

## 用 Memify 丰富记忆

`memify()` 分析知识图并生成智能规则 —— 识别模式、最佳实践以及概念之间的关系。

### 代码单元格 15

输出观察：print 展示应用可观察结果；预存输出和现场结果可能不同，它不是模型内部思考记录。

```python
await cognee.memify()
print("✅ Memory enriched with memify")
```

## 第二部分 — 使用 Cognee 工具的 MAF Agent

现在我们创建一个可以通过 `@tool` 函数查询 Cognee 知识图谱的 MAF Agent。这样 Agent 就能利用图结构感知的语义搜索的全部优势，同时通过会话保持对话上下文。

### 代码单元格 17

工具定义：类型注解和文档字符串描述输入、用途；模型产生调用请求，框架在应用进程中执行函数。检查是否需要人工批准。

异步执行：async def 定义协程，await 等待结果；普通 .py 脚本需要 asyncio.run() 入口，Notebook 支持顶层 await。

检索过程：跟踪查询、候选结果和实际选入的证据；检索为空时应明确返回缺失，而不是补写答案。

```python
@tool(approval_mode="never_require")
async def search_knowledge(
    query: Annotated[str, "Natural-language question to search the knowledge graph"],
) -> str:
    """Search the Cognee knowledge graph for relevant developer knowledge, best practices, and past conversations."""
    results = await cognee.search(
        query_text=query,
        query_type=SearchType.GRAPH_COMPLETION,
    )
    if not results:
        return "No relevant knowledge found."
    return str(results)


@tool(approval_mode="never_require")
async def search_principles(
    query: Annotated[str, "Question about Python principles or best practices"],
) -> str:
    """Search only the Python principles subset of the knowledge graph."""
    from cognee.modules.engine.models.node_set import NodeSet
    results = await cognee.search(
        query_text=query,
        query_type=SearchType.GRAPH_COMPLETION,
        node_type=NodeSet,
        node_name=["principles_data"],
    )
    if not results:
        return "No relevant principles found."
    return str(results)


print("✅ Cognee tools defined: search_knowledge, search_principles")
```

### 代码单元格 18

行为约束：instructions 引导模型，不能替代执行器的权限验证、次数限制和结果检查。

检索过程：跟踪查询、候选结果和实际选入的证据；检索为空时应明确返回缺失，而不是补写答案。

输出观察：print 展示应用可观察结果；预存输出和现场结果可能不同，它不是模型内部思考记录。

```python
coding_agent = provider.as_agent(
    name="CodingAssistant",
    instructions=(
        "You are an expert coding assistant with access to a knowledge graph "
        "containing developer profiles, Python best practices, and past conversations.\n\n"
        "WORKFLOW:\n"
        "1. Use search_knowledge() to find relevant information from the full knowledge graph.\n"
        "2. Use search_principles() when the question is specifically about Python best practices.\n"
        "3. Combine retrieved knowledge with your own expertise to give comprehensive answers.\n"
        "4. Reference the developer's known tech stack (FastAPI, asyncio, Pydantic) when relevant."
    ),
)

print("✅ CodingAssistant agent created")
```

## 使用会话的工作记忆

`AgentSession`（通过 `agent.create_session()` 创建）在会话中提供工作记忆。Agent 可以回顾之前的消息，同时查询 Cognee 的长期知识图谱。

### 代码单元格 20

会话状态：复用同一个 session 才会带上历史；新建会话与持久化存储是不同操作。

输出观察：print 展示应用可观察结果；预存输出和现场结果可能不同，它不是模型内部思考记录。

```python
session = coding_agent.create_session()

response = await coding_agent.run(
    "How does my AsyncWebScraper implementation align with Python's design principles?",
    session=session,
)
print("🤖 Agent:", response)
```

### 代码单元格 21

输出观察：print 展示应用可观察结果；预存输出和现场结果可能不同，它不是模型内部思考记录。

```python
response = await coding_agent.run(
    "Based on what you just said, when should I pick dataclasses versus Pydantic for this work?",
    session=session,
)
print("🤖 Agent:", response)
print("\n💡 The agent combined working memory (previous answer) with Cognee's knowledge graph.")
```

## 新会话 — 长期记忆持续存在

开始一个新的会话会清除工作记忆，但Cognee知识图谱仍然可用。Agent 可以在一个全新的对话中检索相同的长期知识。

### 代码单元格 23

会话状态：复用同一个 session 才会带上历史；新建会话与持久化存储是不同操作。

输出观察：print 展示应用可观察结果；预存输出和现场结果可能不同，它不是模型内部思考记录。

```python
session_2 = coding_agent.create_session()

response = await coding_agent.run(
    "What logging guidance should I follow for incident reviews?",
    session=session_2,
)
print("🤖 Agent:", response)
print("\n💡 New session, but the agent still has access to the full Cognee knowledge graph.")
```

### 代码单元格 24

输出观察：print 展示应用可观察结果；预存输出和现场结果可能不同，它不是模型内部思考记录。

```python
response = await coding_agent.run(
    "How should variables be named according to Python best practices?",
    session=session_2,
)
print("🤖 Agent:", response)
```

## 摘要

在本笔记本中，你构建了一个结合了 **MAF工作记忆** （`agent.create_session()`）与 **Cognee长期知识图谱** 的编码助手。

### 你学到了什么
1. **知识图谱构建** ：Cognee摄取非结构化文本并构建图谱 + 向量记忆。
2. **利用memify丰富图谱** ：在现有图谱基础上派生事实和更丰富的关系。
3. **MAF + Cognee集成** ：`@tool`函数让MAFAgent 自然查询Cognee的图谱。
4. **工作记忆 + 长期记忆** ：`AgentSession`（通过`agent.create_session()`）提供会话上下文，Cognee提供持久知识。
5. **使用NodeSets的过滤搜索** ：定位知识图中特定子集（例如，仅原则）。

### 主要收获
- **Cognee** 将原始文本转化为结构化、具备关系意识的记忆 —— 比单纯的向量存储更强大。
- **`@tool`函数** 清晰桥接MAFAgent 与外部知识系统。
- **`AgentSession`** （通过`agent.create_session()`）使每个对话上下文与长期知识分离保存。
- 相同的知识图谱服务于多个会话和 Agent。

### 现实应用
- **开发者助手** ：代码审查、事件分析、架构助理
- **面向客户的助手** ：基于产品文档、FAQ及CRM记录的支持 Agent
- **内部专家助手** ：基于政策、法律或安全指南的推理助手
- **统一数据层** ：将结构化与非结构化数据合成一个可查询图谱

### 后续步骤
- 在Cognee中尝试时间感知功能
- 为特定领域图谱质量定义OWL本体
- 添加用户反馈机制，提升检索效果
- 扩展到共享同一Cognee记忆层的多 Agent 系统


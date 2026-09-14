---
title: "13 · 13-agent-memory"
outline: [2, 3]
---

# 13 · 13-agent-memory

[返回：Agent 记忆](/lessons/memory.md) · [不可变原始文件](https://github.com/microsoft/ai-agents-for-beginners/blob/25b7985f3b2dc37a84f4a7387ccd3c9f0e5b1595/13-agent-memory/13-agent-memory.ipynb)

::: warning 原课程完整 Notebook · 静态阅读与代码解析
代码按英文源文件顺序保留，中文说明以同版本译本为基础。原始安装单元格可能含无版本上限的 `-U`；请跳过它们，先按[准备篇](/lessons/setup.md)固定依赖。云端服务、模型权限、网站布局和部分 SDK 接口需在你自己的环境验证。本站没有执行云端请求；第 18 章的离线验证状态单独记录在[检查报告](/guide/verification.md)。
:::

## 运行准备

Python 3.12+；在独立虚拟环境安装源仓库依赖与本页中声明的额外依赖。原文件路径：`upstream/13-agent-memory/13-agent-memory.ipynb`。以原仓库根目录为工作目录，在 Jupyter 中按顺序执行；身份与环境变量见准备篇。

```bash
cd upstream
python -m jupyterlab
```

[下载原始 Notebook](/notebooks/13-agent-memory/13-agent-memory.ipynb)。输出为上游文件保存的历史结果，不能用作本站实测证明。

## 课程 13 - Agent 记忆

## 设置

本笔记本演示了如何使用 **Microsoft Agent Framework** (MAF) 构建具有 **持久记忆** 的旅游预订 Agent。

你将了解不同类型的 Agent 记忆——工作记忆、短期记忆和长期记忆——如何影响 Agent 在对话中的信息保留和使用。

 **先决条件：** 
- 一个部署了聊天模型（例如 `gpt-5-mini`）的 Microsoft Foundry 项目。
- 已通过 Azure CLI 登录——在终端运行 `az login`。
- `AZURE_AI_PROJECT_ENDPOINT` —— 你的 Microsoft Foundry 项目端点。
- `AZURE_AI_MODEL_DEPLOYMENT_NAME` —— 你部署模型的名称。

### 代码单元格 3

阅读提示：跟踪本单元格读取的变量、修改的状态以及返回值。按原顺序执行，确认依赖的前序变量已经存在。

```text
%pip install agent-framework azure-ai-projects azure-identity python-dotenv -q
```

### 代码单元格 4

配置加载：从本地环境读取端点与部署名；缺少变量时先修复配置，不要把密钥写进代码。

模型连接：project_endpoint 是项目地址，model 是实际部署名称；credential 提供访问身份。客户端创建本身不证明已经部署服务端 Agent。

```python
import logging
logging.getLogger("agent_framework.foundry").setLevel(logging.ERROR)

import os
import json
import dotenv
from typing import Annotated
from datetime import datetime

from agent_framework import tool
from agent_framework.foundry import FoundryChatClient
from azure.identity import DefaultAzureCredential

dotenv.load_dotenv()

endpoint = os.getenv("AZURE_AI_PROJECT_ENDPOINT")
deployment_name = os.getenv("AZURE_AI_MODEL_DEPLOYMENT_NAME")

missing = [k for k, v in {
    "AZURE_AI_PROJECT_ENDPOINT": endpoint,
    "AZURE_AI_MODEL_DEPLOYMENT_NAME": deployment_name
}.items() if not v]

if missing:
    raise ValueError(
        f"Missing required environment variables: {', '.join(missing)}. "
        "Please set them as environment variables (e.g., in your .env file or shell environment)."
    )
```

### 代码单元格 5

模型连接：project_endpoint 是项目地址，model 是实际部署名称；credential 提供访问身份。客户端创建本身不证明已经部署服务端 Agent。

输出观察：print 展示应用可观察结果；预存输出和现场结果可能不同，它不是模型内部思考记录。

```python
# Create the Microsoft Foundry client
client = FoundryChatClient(
    project_endpoint=endpoint,
    model=deployment_name,
    credential=DefaultAzureCredential()
)

print("Microsoft Foundry client configured")
```

## Agent 记忆的类型

AI Agent 可以利用不同类型的记忆，每种记忆都有其独特的用途：

### 工作记忆
会话线程本身——单次会话中交换的消息。Agent 可以回溯同一线程中的早期消息以保持连贯性。在 MAF 中，这是通过 **`agent.create_session()`** 创建的，它返回一个 `AgentSession`。

### 短期记忆
在任务或会话期间持续但不永久存储的信息。例如，Agent 可能在多轮规划对话中积累事实，并利用这些事实来生成最终的行程。

### 长期记忆
在 **跨会话** 中持续存在的偏好和事实。回访用户不应重复说明其饮食限制或旅行风格。长期记忆通常由外部存储支持——数据库、文件或向量索引——并通过工具向 Agent 提供。

## 使用会话的工作记忆

最简单的记忆形式是对话会话。当你将同一个会话（通过 `agent.create_session()` 创建）传递给连续的 `agent.run()` 调用时，Agent 可以看到该对话的完整历史，并能够回忆起早期的细节。

让我们创建一个旅行 Agent 并演示工作记忆。

### 代码单元格 8

会话状态：复用同一个 session 才会带上历史；新建会话与持久化存储是不同操作。

行为约束：instructions 引导模型，不能替代执行器的权限验证、次数限制和结果检查。

输出观察：print 展示应用可观察结果；预存输出和现场结果可能不同，它不是模型内部思考记录。

```python
agent = client.as_agent(
    name="TravelMemoryAgent",
    instructions=(
        "You are a travel agent who remembers user preferences across conversations. "
        "Track destinations mentioned, budget constraints, and travel dates."
    ),
)

session = agent.create_session()

# First message — the user shares preferences
response = await agent.run(
    "I love beach destinations and my budget is $3000",
    session=session,
)
print("Agent:", response)

# Second message — the agent should recall the budget from the thread
response = await agent.run(
    "What did I say my budget was?",
    session=session,
)
print("Agent:", response)
```

Agent 正确地回忆了预算，因为两个消息共享相同的会话。这是 **工作记忆** ——它只存在于会话的生命周期内。

### 新线程会发生什么？

如果我们创建一个 **新的** 会话，Agent 就不会记得之前的对话：

### 代码单元格 10

会话状态：复用同一个 session 才会带上历史；新建会话与持久化存储是不同操作。

输出观察：print 展示应用可观察结果；预存输出和现场结果可能不同，它不是模型内部思考记录。

```python
new_session = agent.create_session()

response = await agent.run(
    "What is my budget?",
    session=new_session,
)
print("Agent:", response)
print("\n💡 The agent has no memory of the previous conversation — it's a fresh session.")
```

## 长期记忆模式

为了记住用户偏好 **跨会话** ，我们需要一个持久存储，它存在于对话线程之外。Agent 通过 **工具** 访问这个存储 —— 这些工具是它可以调用来保存和检索信息的函数。

下面我们实现了一个简单的内存偏好存储（在生产中你会用数据库或向量索引来支持它），并将其作为 Agent 可以使用的工具公开。

### 架构
```
┌─────────────────┐     ┌──────────────────┐     ┌─────────────────┐
│  MAF Agent      │────▶│  @tool functions  │────▶│  Preference     │
│  (LLM)          │     │  save / retrieve  │     │  Store (dict)   │
└─────────────────┘     └──────────────────┘     └─────────────────┘
         │                                                 │
    AgentSession                                   Persists across
    (working memory)                               sessions
```

### 代码单元格 12

工具定义：类型注解和文档字符串描述输入、用途；模型产生调用请求，框架在应用进程中执行函数。检查是否需要人工批准。

检索过程：跟踪查询、候选结果和实际选入的证据；检索为空时应明确返回缺失，而不是补写答案。

输出观察：print 展示应用可观察结果；预存输出和现场结果可能不同，它不是模型内部思考记录。

```python
# --- Persistent preference store (simulated) ---
preference_store: dict[str, list[str]] = {}


@tool(approval_mode="never_require")
def save_preference(
    user_id: Annotated[str, "User identifier"],
    preference: Annotated[str, "A travel preference to remember"],
) -> str:
    """Save a user travel preference to long-term memory."""
    preference_store.setdefault(user_id, []).append(preference)
    return f"✅ Stored: {preference}"


@tool(approval_mode="never_require")
def get_preferences(
    user_id: Annotated[str, "User identifier"],
) -> str:
    """Retrieve all saved travel preferences for a user."""
    prefs = preference_store.get(user_id, [])
    if not prefs:
        return f"No saved preferences for {user_id}."
    return "Saved preferences:\n- " + "\n- ".join(prefs)


@tool(approval_mode="never_require")
def search_hotels(
    query: Annotated[str, "Search query — location, amenities, or tags"],
) -> str:
    """Search the hotel database for matching properties."""
    hotels = [
        {"name": "Le Meurice Paris", "location": "Paris, France", "price": 850, "tags": ["luxury", "romantic", "spa"]},
        {"name": "Four Seasons Maui", "location": "Maui, Hawaii", "price": 695, "tags": ["beach", "family", "resort"]},
        {"name": "Aman Tokyo", "location": "Tokyo, Japan", "price": 780, "tags": ["luxury", "city", "spa"]},
        {"name": "Hotel Sacher Vienna", "location": "Vienna, Austria", "price": 420, "tags": ["historic", "accessible", "cultural"]},
        {"name": "Fairmont Whistler", "location": "Whistler, Canada", "price": 380, "tags": ["ski", "family", "mountain"]},
    ]
    q = query.lower()
    matches = [
        h for h in hotels
        if q in h["name"].lower()
        or q in h["location"].lower()
        or any(q in t for t in h["tags"])
    ]
    if not matches:
        matches = hotels[:3]
    return json.dumps(matches, indent=2)


print("✅ Tools defined: save_preference, get_preferences, search_hotels")
```

### 场景1 — 第一次用户预订周年旅行

Sarah 是首次访问。Agent 应通过工具存储她的偏好，并利用这些偏好推荐酒店。

### 代码单元格 14

会话状态：复用同一个 session 才会带上历史；新建会话与持久化存储是不同操作。

行为约束：instructions 引导模型，不能替代执行器的权限验证、次数限制和结果检查。

检索过程：跟踪查询、候选结果和实际选入的证据；检索为空时应明确返回缺失，而不是补写答案。

```python
travel_agent = client.as_agent(
    tools=[save_preference, get_preferences],
    name="TravelBookingAssistant",
    instructions=(
        "You are a personalized travel booking assistant with long-term memory.\n"
        "WORKFLOW:\n"
        "1. When a user starts a conversation, call get_preferences() to check for saved information.\n"
        "2. Store any new preferences the user mentions using save_preference().\n"
        "3. Use search_hotels() to find suitable options that match their preferences and budget.\n"
        "4. Do NOT recommend hotels that exceed the user's budget.\n\n"
        "IMPORTANT: Always use user_id='sarah_johnson_123' for all memory operations."
    ),
)

session_1 = travel_agent.create_session()

response = await travel_agent.run(
    "Hi! I'm Sarah and I'm planning a trip for my 10th wedding anniversary. "
    "We love romantic destinations, fine dining, and spa experiences. "
    "My husband has mobility issues, so we need accessible accommodations. "
    "Our budget is around $700-800 per night.",
    session=session_1,
)
print("🤖 Agent:", response)
```

### 代码单元格 15

输出观察：print 展示应用可观察结果；预存输出和现场结果可能不同，它不是模型内部思考记录。

```python
response = await travel_agent.run(
    "The Hotel Sacher sounds perfect! We're both vegetarian and I have a "
    "severe nut allergy. Can you note that for future trips?",
    session=session_1,
)
print("🤖 Agent:", response)
```

### 代码单元格 16

输出观察：print 展示应用可观察结果；预存输出和现场结果可能不同，它不是模型内部思考记录。

```python
# Verify what was stored
print("📋 Preference store contents:")
for uid, prefs in preference_store.items():
    print(f"\n  User: {uid}")
    for p in prefs:
        print(f"    - {p}")
```

### 场景 2 — Sarah 几周后回来

Sarah 开始一个 **全新对话线程** （模拟一个新会话）。工作内存是空的，但长期偏好存储中仍然有她的信息。Agent 应该检索这些信息并用它来个性化推荐。

### 代码单元格 18

会话状态：复用同一个 session 才会带上历史；新建会话与持久化存储是不同操作。

输出观察：print 展示应用可观察结果；预存输出和现场结果可能不同，它不是模型内部思考记录。

```python
session_2 = travel_agent.create_session()  # New session — no working memory

response = await travel_agent.run(
    "Hi, my husband and I are planning another trip. Can you recommend a good hotel?",
    session=session_2,
)
print("🤖 Agent:", response)
print("\n💡 The agent retrieved Sarah's saved preferences from long-term memory "
      "even though this is a completely new conversation thread.")
```

### 代码单元格 19

输出观察：print 展示应用可观察结果；预存输出和现场结果可能不同，它不是模型内部思考记录。

```python
response = await travel_agent.run(
    "Great suggestions! For the Maui option, what activities would you recommend for the kids?",
    session=session_2,
)
print("🤖 Agent:", response)
```

## 总结

在本课中，你了解了三种类型的 Agent 记忆以及如何使用 Microsoft Agent Framework 实现它们：

| 记忆类型 | MAF 机制 | 生命周期 |
|---|---|---|
| **工作记忆** | `agent.create_session()` | 单次对话 |
| **短期记忆** | 线程内累积的上下文 | 单个任务 / 会话 |
| **长期记忆** | 通过 `@tool` 函数访问的外部存储 | 跨会话 |

### 关键要点
1. **`agent.create_session()`** 提供工作记忆 — Agent 在会话内能看到完整对话历史。
2. **新会话会丢失上下文** — 如果没有长期记忆，Agent 无法回忆之前的对话。
3. **`@tool` 函数搭建桥梁** — 允许 Agent 保存和检索持久存储中的信息。
4. **个性化随着时间提升** — 存储的偏好越多，Agent 的推荐越精准。

### 现实应用
- **客户服务** ：记住客户历史和偏好
- **个人助理** ：跨天或数周保持上下文
- **医疗保健** ：跟踪患者信息和偏好
- **电子商务** ：基于历史提供个性化购物

### 后续步骤
- 用数据库或向量存储（如 Azure AI 搜索）替换内存中的字典
- 为时效性信息添加记忆过期机制
- 构建具有共享记忆的多 Agent 系统
- 探索 Cognee 笔记本以实现基于知识图谱的记忆


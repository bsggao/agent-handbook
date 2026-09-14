---
title: "02 · 02-python-agent-framework"
outline: [2, 3]
---

# 02 · 02-python-agent-framework

[返回：探索 Agent 框架](/lessons/frameworks.md) · [不可变原始文件](https://github.com/microsoft/ai-agents-for-beginners/blob/25b7985f3b2dc37a84f4a7387ccd3c9f0e5b1595/02-explore-agentic-frameworks/code_samples/02-python-agent-framework.ipynb)

::: warning 原课程完整 Notebook · 静态阅读与代码解析
代码按英文源文件顺序保留，中文说明以同版本译本为基础。原始安装单元格可能含无版本上限的 `-U`；请跳过它们，先按[准备篇](/lessons/setup.md)固定依赖。云端服务、模型权限、网站布局和部分 SDK 接口需在你自己的环境验证。本站没有执行云端请求；第 18 章的离线验证状态单独记录在[检查报告](/guide/verification.md)。
:::

## 运行准备

Python 3.12+；在独立虚拟环境安装源仓库依赖与本页中声明的额外依赖。原文件路径：`upstream/02-explore-agentic-frameworks/code_samples/02-python-agent-framework.ipynb`。以原仓库根目录为工作目录，在 Jupyter 中按顺序执行；身份与环境变量见准备篇。

```bash
cd upstream
python -m jupyterlab
```

[下载原始 Notebook](/notebooks/02-explore-agentic-frameworks/code_samples/02-python-agent-framework.ipynb)。输出为上游文件保存的历史结果，不能用作本站实测证明。

## 课程 02 - 探索 Microsoft Agent Framework

 **Microsoft Agent Framework（MAF）** 是一个用于构建 AI Agent 的统一框架。它提供了一个简洁、可组合的架构，包含四个核心构建模块：

- **客户端** – 连接到 AI 模型端点并处理通信
- **Agent** – 包装客户端，带有指令和工具定义
- **工具** – 通过模型可调用的自定义函数扩展 Agent 能力
- **会话** – 维护多轮交互的对话历史

在本课中，我们将构建一个使用这些概念来检查目的地可用性的 **旅行预订 Agent** 。

## 设置

### 代码单元格 3

阅读提示：跟踪本单元格读取的变量、修改的状态以及返回值。按原顺序执行，确认依赖的前序变量已经存在。

```python
# Install the Microsoft Agent Framework package
! pip install agent-framework azure-ai-projects -U -q
! pip install python-dotenv -q
```

### 代码单元格 4

配置加载：从本地环境读取端点与部署名；缺少变量时先修复配置，不要把密钥写进代码。

模型连接：project_endpoint 是项目地址，model 是实际部署名称；credential 提供访问身份。客户端创建本身不证明已经部署服务端 Agent。

```python
import logging
logging.getLogger("agent_framework.foundry").setLevel(logging.ERROR)

import os
import asyncio
import dotenv
from typing import Annotated

from agent_framework import tool
from agent_framework.foundry import FoundryChatClient
from azure.identity import AzureCliCredential

dotenv.load_dotenv(dotenv.find_dotenv())
```

## 理解 Agent 框架架构

Microsoft Agent Framework遵循分层架构：

```
Client  →  Agent  →  Tools
                  →  Session
```

1. **客户端** – `FoundryChatClient` 连接到 Azure OpenAI 部署，处理身份验证、请求格式化和响应解析。
2. **Agent** – 通过 `provider.create_agent()` 从客户端创建，agent 结合了模型访问、指令（系统提示）和工具。
3. **工具** – 用 `@tool` 装饰的 Python 函数，agent 可以调用它们执行操作或获取数据。
4. **会话** – `AgentSession` 对象（通过 `agent.create_session()` 创建），存储对话历史，实现多轮对话，agent 记忆之前的上下文。

让我们一步步构建每一层。

### 代码单元格 6

模型连接：project_endpoint 是项目地址，model 是实际部署名称；credential 提供访问身份。客户端创建本身不证明已经部署服务端 Agent。

```python
# Create the client – this is the connection to the AI model
endpoint = os.getenv("AZURE_AI_PROJECT_ENDPOINT")
model = os.getenv("AZURE_AI_MODEL_DEPLOYMENT_NAME")

if not endpoint or not model:
    raise ValueError(
        "Missing required environment variables. "
        "Please set AZURE_AI_PROJECT_ENDPOINT and AZURE_AI_MODEL_DEPLOYMENT_NAME as environment variables (e.g., in your .env file or shell environment)."
    )

provider = FoundryChatClient(
    project_endpoint=endpoint,
    model=model,
    credential=AzureCliCredential()
)
```

## 使用 @tool 装饰器添加工具

工具让 Agent 可以执行生成文本以外的操作。`@tool` 装饰器将普通的 Python 函数转换为 Agent 可以调用的功能。

关键点：
- 使用 `Annotated[type, "description"]`，让模型理解每个参数。
- 文档字符串变成模型看到的工具描述。
- `approval_mode="never_require"` 表示工具自动运行，无需用户确认。

### 代码单元格 8

工具定义：类型注解和文档字符串描述输入、用途；模型产生调用请求，框架在应用进程中执行函数。检查是否需要人工批准。

```python
@tool(approval_mode="never_require")
def check_destination_availability(
    destination: Annotated[str, "The destination to check availability for"]
) -> str:
    """Check if a vacation destination is currently available for booking."""
    available = {
        "Barcelona": True,
        "Tokyo": True,
        "Cape Town": False,
        "Vancouver": True,
        "Dubai": False,
    }
    is_available = available.get(destination, False)
    return f"{destination} is {'available' if is_available else 'not available'} for booking."
```

## 使用工具创建 Agent

现在我们将客户端、指令和工具组合成一个 Agent。`instructions` 作为系统提示——它们定义了 Agent 的角色和行为。

### 代码单元格 10

行为约束：instructions 引导模型，不能替代执行器的权限验证、次数限制和结果检查。

```python
agent = provider.as_agent(
    name="TravelAvailabilityAgent",
    instructions=(
        "You are a travel booking agent. Help users check destination availability "
        "and make recommendations. Always check availability before recommending a destination."
    ),
    tools=[check_destination_availability],
)
```

## 多轮对话会话

`AgentSession`（通过 `agent.create_session()` 创建）跟踪对话中的所有消息。通过在每次 `agent.run()` 调用中传递相同的会话，Agent 可以访问完整的对话历史并引用之前的消息。

我们传入 `tools=[check_destination_availability]`，以便 Agent 在每轮中都能调用我们的可用性检查器。

### 代码单元格 12

会话状态：复用同一个 session 才会带上历史；新建会话与持久化存储是不同操作。

输出观察：print 展示应用可观察结果；预存输出和现场结果可能不同，它不是模型内部思考记录。

```python
session = agent.create_session()

# Turn 1: Ask about available destinations
response = await agent.run(
    "Which destinations do you have available?",
    session=session,
)
print(f"Agent: {response}")
```

### 代码单元格 13

输出观察：print 展示应用可观察结果；预存输出和现场结果可能不同，它不是模型内部思考记录。

```python
# Turn 2: Follow-up question — the agent remembers the conversation
response = await agent.run(
    "I'd like to go somewhere warm. What's available?",
    session=session,
)
print(f"Agent: {response}")
```

## 总结

在本课中，你探索了Microsoft Agent Framework的四大支柱：

| 概念 | 你学到了什么 |
|---------|------------------|
| **客户端** | `FoundryChatClient` 使用基于凭证的认证连接到 Azure OpenAI |
| **Agent** | `provider.create_agent()` 将模型连接与指令和名称绑定在一起 |
| **工具** | `@tool` 装饰器暴露 Python 函数供 Agent 调用 |
| **会话** | `agent.create_session()` 跨多轮保持对话历史 |

这些构建模块组合在一起，创建能够进行自然对话、调用外部函数并保持上下文的 Agent —— 这是后续课程中更高级 Agent 模式的基础。


---
title: "02 · 02-python-agent-framework-azure-openai"
outline: [2, 3]
---

# 02 · 02-python-agent-framework-azure-openai

[返回：探索 Agent 框架](/lessons/frameworks.md) · [不可变原始文件](https://github.com/microsoft/ai-agents-for-beginners/blob/25b7985f3b2dc37a84f4a7387ccd3c9f0e5b1595/02-explore-agentic-frameworks/code_samples/02-python-agent-framework-azure-openai.ipynb)

::: warning 原课程完整 Notebook · 静态阅读与代码解析
代码按英文源文件顺序保留，中文说明以同版本译本为基础。原始安装单元格可能含无版本上限的 `-U`；请跳过它们，先按[准备篇](/lessons/setup.md)固定依赖。云端服务、模型权限、网站布局和部分 SDK 接口需在你自己的环境验证。本站没有执行云端请求；第 18 章的离线验证状态单独记录在[检查报告](/guide/verification.md)。
:::

## 运行准备

Python 3.12+；在独立虚拟环境安装源仓库依赖与本页中声明的额外依赖。原文件路径：`upstream/02-explore-agentic-frameworks/code_samples/02-python-agent-framework-azure-openai.ipynb`。以原仓库根目录为工作目录，在 Jupyter 中按顺序执行；身份与环境变量见准备篇。

```bash
cd upstream
python -m jupyterlab
```

[下载原始 Notebook](/notebooks/02-explore-agentic-frameworks/code_samples/02-python-agent-framework-azure-openai.ipynb)。输出为上游文件保存的历史结果，不能用作本站实测证明。

## Microsoft Agent Framework — Azure OpenAI（Responses API）

在此代码示例中，你将使用 **Microsoft Agent Framework (MAF)** 来创建一个由 **Azure OpenAI** 支持的简单 Agent，使用的是 **Responses API** 。

> **迁移说明：** 该示例之前使用了 Semantic Kernel 和 GitHub Models。现在已迁移到 Microsoft Agent Framework，GitHub Models（已弃用，将于 2026 年 7 月退役）被 Azure OpenAI 所取代，Azure OpenAI 支持 Responses API。MAF 中的 `OpenAIChatClient` 目标是 Azure OpenAI 的稳定 `/openai/v1/` 端点，默认使用 Responses API。

本示例的目的是演示后续其他代码示例中实现各种智能 Agent 模式时将应用的步骤。

### 代码单元格 2

阅读提示：跟踪本单元格读取的变量、修改的状态以及返回值。按原顺序执行，确认依赖的前序变量已经存在。

```text
%pip install agent-framework agent-framework-openai azure-identity -q
```

## 导入所需的 Python 包

### 代码单元格 4

配置加载：从本地环境读取端点与部署名；缺少变量时先修复配置，不要把密钥写进代码。

模型连接：检查此版本使用 Responses 还是 Chat Completions；接口兼容不能只靠更换 base_url 判断。

```python
import os
import random

from dotenv import load_dotenv
from IPython.display import display, HTML

from agent_framework import tool
from agent_framework.openai import OpenAIChatClient
from azure.identity import AzureCliCredential
```

## 定义工具

在 Microsoft Agent Framework 中， **工具** 是一个使用 `@tool` 装饰的普通 Python 函数，Agent 可以调用它。下面我们定义了一个工具，该工具返回一个随机的度假目的地，并避免重复上一次的选择。

### 代码单元格 6

工具定义：类型注解和文档字符串描述输入、用途；模型产生调用请求，框架在应用进程中执行函数。检查是否需要人工批准。

```python
# A list of vacation destinations the tool can choose from.
_DESTINATIONS = [
    "Barcelona, Spain",
    "Paris, France",
    "Berlin, Germany",
    "Tokyo, Japan",
    "Sydney, Australia",
    "New York, USA",
    "Cairo, Egypt",
    "Cape Town, South Africa",
    "Rio de Janeiro, Brazil",
    "Bali, Indonesia",
]

# Track the last destination so repeated calls avoid immediate repeats.
_last_destination: str | None = None


@tool(approval_mode="never_require")
def get_random_destination() -> str:
    """Provides a random vacation destination."""
    global _last_destination
    available = _DESTINATIONS.copy()
    if _last_destination and len(available) > 1:
        available.remove(_last_destination)
    destination = random.choice(available)
    _last_destination = destination
    return destination
```

### 代码单元格 7

配置加载：从本地环境读取端点与部署名；缺少变量时先修复配置，不要把密钥写进代码。

模型连接：检查此版本使用 Responses 还是 Chat Completions；接口兼容不能只靠更换 base_url 判断。

```python
load_dotenv()

endpoint = os.environ["AZURE_OPENAI_ENDPOINT"]
deployment = os.environ["AZURE_OPENAI_DEPLOYMENT"]

# OpenAIChatClient targets Azure OpenAI's v1 endpoint and uses the Responses API.
# Sign in with `az login` first so AzureCliCredential can authenticate.
chat_client = OpenAIChatClient(
    model=deployment,
    azure_endpoint=endpoint,
    credential=AzureCliCredential(),
)
```

## 创建 Agent

在这里，我们创建名为 `TravelAgent` 的 Agent。

在此示例中，我们使用非常基本的指令。你可以自由修改这些指令，以观察 Agent 行为的变化。

### 代码单元格 9

行为约束：instructions 引导模型，不能替代执行器的权限验证、次数限制和结果检查。

```python
agent = chat_client.as_agent(
    name="TravelAgent",
    instructions="You are a helpful AI Agent that can help plan vacations for customers at random destinations",
    tools=[get_random_destination],
)
```

## 运行 Agent

现在我们可以运行 Agent 了。我们创建一个 `AgentSession`，这样 Agent 就能记住跨轮的对话，然后发送两个 `user_inputs`。第一个请求一个旅行计划；第二个表示用户不喜欢建议，并请求另一个——Agent 使用会话历史加上 `get_random_destination` 工具进行回应。

你可以修改这些消息，观察 Agent 的不同反应。响应是按 **Token逐个** 流式传输的。

### 代码单元格 11

会话状态：复用同一个 session 才会带上历史；新建会话与持久化存储是不同操作。

异步执行：async def 定义协程，await 等待结果；普通 .py 脚本需要 asyncio.run() 入口，Notebook 支持顶层 await。

```python
user_inputs = [
    "Plan me a day trip.",
    "I don't like that destination. Plan me another vacation.",
]


async def main():
    # A session keeps conversation history across turns.
    session = agent.create_session()

    for user_input in user_inputs:
        html_output = (
            f"<div style='margin-bottom:10px'>"
            f"<div style='font-weight:bold'>User:</div>"
            f"<div style='margin-left:20px'>{user_input}</div></div>"
        )

        full_response: list[str] = []
        # Stream the agent's response token-by-token. The agent will call the
        # get_random_destination tool automatically when it needs a destination.
        async for chunk in agent.run(user_input, session=session, stream=True):
            full_response.append(str(chunk))

        html_output += (
            "<div style='margin-bottom:20px'>"
            f"<div style='font-weight:bold'>TravelAgent:</div>"
            f"<div style='margin-left:20px; white-space:pre-wrap'>{''.join(full_response)}</div></div><hr>"
        )

        display(HTML(html_output))


await main()
```


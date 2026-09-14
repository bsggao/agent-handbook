---
title: "01 · 01-python-agent-framework"
outline: [2, 3]
---

# 01 · 01-python-agent-framework

[返回：AI Agent 入门与应用场景](/lessons/introduction.md) · [不可变原始文件](https://github.com/microsoft/ai-agents-for-beginners/blob/25b7985f3b2dc37a84f4a7387ccd3c9f0e5b1595/01-intro-to-ai-agents/code_samples/01-python-agent-framework.ipynb)

::: warning 原课程完整 Notebook · 静态阅读与代码解析
代码按英文源文件顺序保留，中文说明以同版本译本为基础。原始安装单元格可能含无版本上限的 `-U`；请跳过它们，先按[准备篇](/lessons/setup.md)固定依赖。云端服务、模型权限、网站布局和部分 SDK 接口需在你自己的环境验证。本站没有执行云端请求；第 18 章的离线验证状态单独记录在[检查报告](/guide/verification.md)。
:::

## 运行准备

Python 3.12+；在独立虚拟环境安装源仓库依赖与本页中声明的额外依赖。原文件路径：`upstream/01-intro-to-ai-agents/code_samples/01-python-agent-framework.ipynb`。以原仓库根目录为工作目录，在 Jupyter 中按顺序执行；身份与环境变量见准备篇。

```bash
cd upstream
python -m jupyterlab
```

[下载原始 Notebook](/notebooks/01-intro-to-ai-agents/code_samples/01-python-agent-framework.ipynb)。输出为上游文件保存的历史结果，不能用作本站实测证明。

## 课程 01 - AI Agent 简介

欢迎来到 **AI 新手 Agent** 课程的第一课！

 **AI Agent** 是一个使用大语言模型（LLM）作为推理引擎的程序，并且能够在现实世界中采取*行动* —— 调用 API、查询数据库或运行代码 —— 以代表用户完成目标。

在本笔记本中，你将构建第一个 Agent：一个推荐度假目的地的 **旅行 Agent** 。在此过程中，你将学习如何：

1. 使用 **Microsoft Agent Framework** 连接到 Microsoft Foundry Agent 服务。
2. 给 Agent 一个 **工具** —— 一个它可以调用的普通 Python 函数。
3. 运行 Agent 并检查其响应。
4. 逐个Token流式传输 Agent 的响应。

## 设置

在运行此笔记本之前，请确保你已完成以下操作：

1. **拥有一个 Microsoft Foundry 项目** 并已部署聊天模型（例如 `gpt-5-mini`）。
2. **已使用 Azure CLI 登录** — 在终端运行 `az login`。
3. **设置必需的环境变量：** 
   - `AZURE_AI_PROJECT_ENDPOINT` — 你的 Microsoft Foundry 项目端点。
   - `AZURE_AI_MODEL_DEPLOYMENT_NAME` — 你已部署模型的名称。

下面的单元格将安装你需要的 Python 包。

### 代码单元格 3

阅读提示：跟踪本单元格读取的变量、修改的状态以及返回值。按原顺序执行，确认依赖的前序变量已经存在。

```text
%pip install agent-framework azure-ai-projects azure-identity -q
```

### 代码单元格 4

配置加载：从本地环境读取端点与部署名；缺少变量时先修复配置，不要把密钥写进代码。

模型连接：project_endpoint 是项目地址，model 是实际部署名称；credential 提供访问身份。客户端创建本身不证明已经部署服务端 Agent。

```python
import logging
logging.getLogger("agent_framework.foundry").setLevel(logging.ERROR)

import os
import dotenv
from agent_framework.foundry import FoundryChatClient
from azure.identity import AzureCliCredential
from agent_framework import tool

dotenv.load_dotenv(dotenv.find_dotenv())

endpoint = os.getenv("AZURE_AI_PROJECT_ENDPOINT")
model = os.getenv("AZURE_AI_MODEL_DEPLOYMENT_NAME")

if not endpoint or not model:
    raise ValueError(
        "Missing required environment variables. "
        "Please set AZURE_AI_PROJECT_ENDPOINT and AZURE_AI_MODEL_DEPLOYMENT_NAME in your .env file."
    )

provider = FoundryChatClient(
    project_endpoint=endpoint,
    model=model,
    credential=AzureCliCredential()
)
```

## 创建你的第一个 Agent

一个 Agent 需要两样东西：

- **指令** ，告诉它*它是谁*以及*如何表现*（系统提示）。
- **工具** —— 用 `@tool` 装饰的 Python 函数，Agent 可以调用它们来获取信息或执行操作。

下面我们定义了一个简单的工具，它返回一个受欢迎的度假目的地列表。当用户询问旅行推荐时，Agent 将使用此工具。

### 代码单元格 6

工具定义：类型注解和文档字符串描述输入、用途；模型产生调用请求，框架在应用进程中执行函数。检查是否需要人工批准。

```python
@tool(approval_mode="never_require")
def get_destinations() -> list[str]:
    """Get a list of popular vacation destinations."""
    return [
        "Barcelona",
        "Paris",
        "Berlin",
        "Tokyo",
        "Sydney",
        "New York City",
        "Cairo",
        "Cape Town",
        "Rio de Janeiro",
        "Bali",
    ]
```

### 代码单元格 7

行为约束：instructions 引导模型，不能替代执行器的权限验证、次数限制和结果检查。

输出观察：print 展示应用可观察结果；预存输出和现场结果可能不同，它不是模型内部思考记录。

```python
agent = provider.as_agent(
    name="TravelAgent",
    instructions=(
        "You are a helpful travel agent. Help users find their perfect vacation "
        "destination based on their preferences. Use the get_destinations tool "
        "to see available destinations."
    ),
    tools=[get_destinations],
)

response = await agent.run(
    "I'm looking for a warm beach destination. What do you recommend?"
)
print(response)
```

## 流式响应

为了获得更互动的体验，你可以 **流式** 获取 Agent 的响应。Agent 会随着文本生成逐块产出，而不是等待完整回复。这在聊天界面中特别有用，因为你希望实时展示输出内容。

### 代码单元格 9

输出观察：print 展示应用可观察结果；预存输出和现场结果可能不同，它不是模型内部思考记录。

```python
async for chunk in agent.run(
    "Tell me about Tokyo as a travel destination", stream=True
):
    print(chunk, end="", flush=True)
```

## 总结

在本课中，你学到了如何：

- **创建一个提供程序** ，通过 `FoundryChatClient` 连接到 Microsoft Foundry Agent Service。
- **使用 `@tool` 装饰器定义工具** ，以便 Agent 可以调用你的 Python 函数。
- **运行 Agent** ，发送用户消息并打印其响应。
- **流式传输响应** ，实现实时输出。

在下一课中，我们将更深入地探讨 Agent 框架，并学习如何赋予 Agent 更强大的工具和多步骤推理能力。


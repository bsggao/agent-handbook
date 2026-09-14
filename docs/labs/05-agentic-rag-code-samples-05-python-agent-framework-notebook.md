---
title: "05 · 05-python-agent-framework"
outline: [2, 3]
---

# 05 · 05-python-agent-framework

[返回：Agentic RAG](/lessons/rag.md) · [不可变原始文件](https://github.com/microsoft/ai-agents-for-beginners/blob/25b7985f3b2dc37a84f4a7387ccd3c9f0e5b1595/05-agentic-rag/code_samples/05-python-agent-framework.ipynb)

::: warning 原课程完整 Notebook · 静态阅读与代码解析
代码按英文源文件顺序保留，中文说明以同版本译本为基础。原始安装单元格可能含无版本上限的 `-U`；请跳过它们，先按[准备篇](/lessons/setup.md)固定依赖。云端服务、模型权限、网站布局和部分 SDK 接口需在你自己的环境验证。本站没有执行云端请求；第 18 章的离线验证状态单独记录在[检查报告](/guide/verification.md)。
:::

## 运行准备

Python 3.12+；在独立虚拟环境安装源仓库依赖与本页中声明的额外依赖。原文件路径：`upstream/05-agentic-rag/code_samples/05-python-agent-framework.ipynb`。以原仓库根目录为工作目录，在 Jupyter 中按顺序执行；身份与环境变量见准备篇。

```bash
cd upstream
python -m jupyterlab
```

[下载原始 Notebook](/notebooks/05-agentic-rag/code_samples/05-python-agent-framework.ipynb)。输出为上游文件保存的历史结果，不能用作本站实测证明。

## 课程 05 - 主动式 RAG

## 设置

本笔记本演示了使用 Microsoft Agent Framework 的 Agentic RAG（检索增强生成）模式。

 **先决条件：** 
- `AZURE_SEARCH_SERVICE_ENDPOINT` — 你的 Azure AI 搜索服务端点
- `AZURE_SEARCH_API_KEY` — 你的 Azure AI 搜索 API 密钥
- 通过环境变量配置的 Azure OpenAI 部署
- 已通过 Azure CLI 认证（`az login`）

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
import asyncio
import dotenv
from typing import Annotated

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

```python
# Create the Microsoft Foundry client
client = FoundryChatClient(
    project_endpoint=endpoint,
    model=deployment_name,
    credential=DefaultAzureCredential()
)
```

## 什么是 Agentic RAG？

传统的 RAG 遵循固定流程：先检索文档，然后生成回答。 **Agentic RAG** 更进一步，赋予 Agent 自主权以决定 **何时** 以及 **如何** 检索信息。

使用 Agentic RAG，Agent 可以：
- **决定** 在回答问题前是否需要检索
- **选择** 查询哪个数据源或工具
- **评估** 检索到的结果，并在第一次尝试不足时执行后续检索
- **整合** 多个检索步骤的信息，形成连贯回答

这使得 Agent 相比静态的先检索后生成流程更加灵活和精准。

## 创建搜索工具

在 Agentic RAG 中，外部数据源被包装为 Agent 可以按需调用的 **工具** 。这让 Agent 把检索当成它可以执行的另一个操作，而不是一个强制步骤。

下面我们定义一个旅游知识库，并将其公开为 Agent 可以调用的工具，以查询目的地信息。

### 代码单元格 8

工具定义：类型注解和文档字符串描述输入、用途；模型产生调用请求，框架在应用进程中执行函数。检查是否需要人工批准。

检索过程：跟踪查询、候选结果和实际选入的证据；检索为空时应明确返回缺失，而不是补写答案。

```python
TRAVEL_KNOWLEDGE_BASE = {
    "Barcelona": "Barcelona is Spain's cosmopolitan capital of Catalonia. Best visited Mar-May or Sep-Nov. Known for Gaudí architecture, La Rambla, beaches. Average daily cost: $150-200.",
    "Tokyo": "Tokyo is Japan's capital, mixing ultramodern with traditional. Best visited Mar-Apr (cherry blossoms) or Oct-Nov. Known for Shibuya, temples, sushi. Average daily cost: $200-250.",
    "Paris": "Paris is France's capital and a global center for art, fashion, and culture. Best visited Apr-Jun or Sep-Oct. Known for Eiffel Tower, Louvre, cuisine. Average daily cost: $180-250.",
    "Cape Town": "Cape Town sits on South Africa's southwest tip. Best visited Nov-Mar. Known for Table Mountain, wine regions, wildlife. Average daily cost: $100-150.",
}


@tool(approval_mode="never_require")
def search_travel_knowledge(
    query: Annotated[str, "The search query about a travel destination"]
) -> str:
    """Search the travel knowledge base for destination information."""
    results = []
    for destination, info in TRAVEL_KNOWLEDGE_BASE.items():
        if query.lower() in destination.lower() or any(
            word in info.lower() for word in query.lower().split()
        ):
            results.append(f"**{destination}**: {info}")
    return (
        "\n\n".join(results)
        if results
        else "No matching destinations found in the knowledge base."
    )
```

## 构建 RAG Agent

现在我们创建一个指示为 **总是在回答前检索信息** 的 Agent。该 Agent 使用 `search_travel_knowledge` 工具将其回答基于知识库，而不是依赖自身的训练数据。

### 代码单元格 10

行为约束：instructions 引导模型，不能替代执行器的权限验证、次数限制和结果检查。

检索过程：跟踪查询、候选结果和实际选入的证据；检索为空时应明确返回缺失，而不是补写答案。

输出观察：print 展示应用可观察结果；预存输出和现场结果可能不同，它不是模型内部思考记录。

```python
agent = client.as_agent(
    tools=[search_travel_knowledge],
    name="TravelRAGAgent",
    instructions="""You are a knowledgeable travel advisor. Before answering questions about destinations:
1. ALWAYS search the travel knowledge base first
2. Base your answers on retrieved information
3. If information is not in the knowledge base, say so clearly
4. Provide specific details like costs, best seasons, and highlights.""",
)

response = await agent.run(
    "I'm interested in visiting somewhere with great architecture. What destinations would you recommend?",
    )
print(response)
```

## 迭代检索 — 制作者-审核者模式

Agentic RAG 的一个关键优势是 **迭代检索** 。Agent 可以执行多轮搜索，以验证、完善或扩展其初始发现 —— 类似于“制作者-审核者”的工作流程：

1. **制作者步骤** ：Agent 检索初始信息并起草回答。
2. **审核者步骤** ：Agent 进行额外检索以核实细节或填补空白。

下面，Agent 被问及一个需要比较多个目的地的问题，促使它进行多次搜索。

### 代码单元格 12

行为约束：instructions 引导模型，不能替代执行器的权限验证、次数限制和结果检查。

检索过程：跟踪查询、候选结果和实际选入的证据；检索为空时应明确返回缺失，而不是补写答案。

输出观察：print 展示应用可观察结果；预存输出和现场结果可能不同，它不是模型内部思考记录。

```python
checker_agent = client.as_agent(
    tools=[search_travel_knowledge],
    name="TravelRAGCheckerAgent",
    instructions="""You are a meticulous travel advisor who double-checks recommendations.
When answering travel questions:
1. Search for relevant destinations first
2. For each destination found, search again with the destination name to get full details
3. Compare the options using verified information
4. Present a final recommendation with specific costs, best travel times, and highlights
5. If any detail seems incomplete, search once more to confirm before responding.""",
)

response = await checker_agent.run(
    "I have a $175/day budget and want to travel in April. Which destinations fit my budget and timing?",
    )
print(response)
```

## 总结

在本课中，你学习了如何使用 Microsoft Agent Framework 构建一个 **Agentic RAG** 系统：

- **Agentic RAG** 允许 Agent 自主决定何时检索信息，使检索变得动态而非固定。
- **作为数据源的工具** ：外部知识库（如 Azure AI Search）被封装为 Agent 可以调用的工具。
- **迭代检索** ：制作者-审核者模式使 Agent 能够执行多轮检索——搜索、验证和细化——然后再生成最终答案。

在生产环境中，你会用真实的 Azure AI Search 索引替换内存中的 `TRAVEL_KNOWLEDGE_BASE`，以处理大规模的旅行文档检索。


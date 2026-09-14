---
title: "11 · 11-mcp-agent-framework"
outline: [2, 3]
---

# 11 · 11-mcp-agent-framework

[返回：Agent 协议：MCP、A2A、NLWeb](/lessons/protocols.md) · [不可变原始文件](https://github.com/microsoft/ai-agents-for-beginners/blob/25b7985f3b2dc37a84f4a7387ccd3c9f0e5b1595/11-agentic-protocols/code_samples/11-mcp-agent-framework.ipynb)

::: warning 原课程完整 Notebook · 静态阅读与代码解析
代码按英文源文件顺序保留，中文说明以同版本译本为基础。原始安装单元格可能含无版本上限的 `-U`；请跳过它们，先按[准备篇](/lessons/setup.md)固定依赖。云端服务、模型权限、网站布局和部分 SDK 接口需在你自己的环境验证。本站没有执行云端请求；第 18 章的离线验证状态单独记录在[检查报告](/guide/verification.md)。
:::

## 运行准备

Python 3.12+；在独立虚拟环境安装源仓库依赖与本页中声明的额外依赖。原文件路径：`upstream/11-agentic-protocols/code_samples/11-mcp-agent-framework.ipynb`。以原仓库根目录为工作目录，在 Jupyter 中按顺序执行；身份与环境变量见准备篇。

```bash
cd upstream
python -m jupyterlab
```

[下载原始 Notebook](/notebooks/11-agentic-protocols/code_samples/11-mcp-agent-framework.ipynb)。输出为上游文件保存的历史结果，不能用作本站实测证明。

## 第11课 - 模型上下文协议（MCP）

 **模型上下文协议（MCP）** 是一个开放标准，使 Agent 能够在运行时动态发现和使用工具、资源和数据源。MCP允许 Agent 连接到按需暴露功能的外部服务器，而不是将工具硬编码到 Agent 内部。

在本课中，你将学习：
- 什么是MCP以及它为何对 Agent 系统重要
- MCP的客户端-服务器架构如何工作
- 如何构建使用MCP风格工具发现的 Agent

## 设置

 **前提条件：** 
- 具有已部署模型的 Microsoft Foundry 项目
- 运行 `az login` 进行身份验证

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

# Create the Microsoft Foundry client
client = FoundryChatClient(
    project_endpoint=endpoint,
    model=deployment_name,
    credential=DefaultAzureCredential()
)
```

## 什么是模型上下文协议（MCP）？

MCP 定义了一种标准方式，让 AI Agent 发现并与外部工具和数据源交互：

- **MCP 服务器** ：通过标准协议暴露工具、资源和提示
- **MCP 客户端** ：连接服务器并发现可用功能的 Agent 运行时
- **动态发现** ：Agent 不需要硬编码工具 —— 它们在运行时发现可用的工具

这对于构建可扩展的 Agent 系统非常强大，可以在不修改 Agent 代码的情况下添加新功能。

## MCP 的工作原理

```
┌─────────────┐     discover      ┌─────────────────┐
│  MCP Client  │ ──────────────► │   MCP Server     │
│  (Agent)     │                  │  (Tool Provider) │
│              │ ◄────────────── │                   │
│              │   tool results   │  • list_tools()  │
│              │                  │  • call_tool()   │
└─────────────┘                  │  • resources     │
                                  └─────────────────┘
```

1. Agent（MCP 客户端）连接到 MCP 服务器
2. 服务器响应可用工具及其模式的列表
3. Agent 随后可以在推理过程中调用任何已发现的工具
4. 结果通过相同协议返回

## 模拟 MCP 工具发现

由于真实的 MCP 服务器需要一个运行中的服务器进程，我们将使用 `@tool` 函数来演示该模式，这些函数模拟了 MCP 连接的住宿服务所提供的内容。

在生产环境中，这些工具将从 MCP 服务器动态发现，而不是本地定义。

### 代码单元格 8

工具定义：类型注解和文档字符串描述输入、用途；模型产生调用请求，框架在应用进程中执行函数。检查是否需要人工批准。

检索过程：跟踪查询、候选结果和实际选入的证据；检索为空时应明确返回缺失，而不是补写答案。

```python
@tool(approval_mode="never_require")
def search_accommodations(
    location: Annotated[str, "The city to search for accommodations"],
    check_in: Annotated[str, "Check-in date (YYYY-MM-DD)"],
    check_out: Annotated[str, "Check-out date (YYYY-MM-DD)"],
    guests: Annotated[int, "Number of guests"] = 2
) -> str:
    """Search for accommodations (simulating an MCP-connected Airbnb tool).
    In production, this would be discovered via MCP from an accommodation service."""
    listings = {
        "Tokyo": [
            {"name": "Shinjuku Modern Apartment", "price": 120, "rating": 4.8},
            {"name": "Traditional Ryokan in Asakusa", "price": 200, "rating": 4.9},
            {"name": "Shibuya Studio", "price": 85, "rating": 4.5},
        ],
        "Paris": [
            {"name": "Le Marais Charming Flat", "price": 150, "rating": 4.7},
            {"name": "Montmartre Artist Loft", "price": 110, "rating": 4.6},
        ],
        "Barcelona": [
            {"name": "Gothic Quarter Penthouse", "price": 130, "rating": 4.8},
            {"name": "Barceloneta Beach Flat", "price": 95, "rating": 4.4},
        ],
    }
    results = listings.get(location, [])
    if not results:
        return f"No accommodations found in {location}"
    output = f"Accommodations in {location} ({check_in} to {check_out}, {guests} guests):\n"
    for listing in results:
        output += f"  - {listing['name']}: ${listing['price']}/night (★{listing['rating']})\n"
    return output


@tool(approval_mode="never_require")
def get_local_experiences(
    location: Annotated[str, "The city to find experiences in"],
    interest: Annotated[str, "Type of experience (food, culture, adventure, etc.)"] = "all"
) -> str:
    """Get local experiences and activities (simulating an MCP-connected tourism tool)."""
    experiences = {
        "Tokyo": {
            "food": ["Tsukiji Market Tour ($45)", "Ramen Making Class ($60)", "Sake Tasting ($35)"],
            "culture": ["Tea Ceremony ($50)", "Samurai Museum ($15)", "Sumo Tournament ($80)"],
            "adventure": ["Mt. Fuji Day Trip ($120)", "Go-kart City Tour ($80)"],
        },
        "Paris": {
            "food": ["Wine & Cheese Tasting ($55)", "Cooking Class ($90)", "Market Tour ($40)"],
            "culture": ["Louvre Guided Tour ($35)", "Montmartre Art Walk ($25)"],
        },
    }
    city_exp = experiences.get(location, {})
    if not city_exp:
        return f"No experiences found in {location}"
    if interest != "all" and interest in city_exp:
        items = city_exp[interest]
        return f"{interest.title()} experiences in {location}:\n" + "\n".join(f"  - {e}" for e in items)
    output = f"All experiences in {location}:\n"
    for cat, items in city_exp.items():
        output += f"\n  {cat.title()}:\n"
        for item in items:
            output += f"    - {item}\n"
    return output
```

## 使用 MCP 风格工具构建 Agent

### 代码单元格 10

行为约束：instructions 引导模型，不能替代执行器的权限验证、次数限制和结果检查。

检索过程：跟踪查询、候选结果和实际选入的证据；检索为空时应明确返回缺失，而不是补写答案。

输出观察：print 展示应用可观察结果；预存输出和现场结果可能不同，它不是模型内部思考记录。

```python
agent = client.as_agent(
    tools=[search_accommodations, get_local_experiences],
    name="AccommodationAgent",
    instructions="""You are an accommodation and travel experiences specialist powered by MCP-connected services.

Help travelers find the perfect place to stay and things to do. When searching:
1. Use the search_accommodations tool to find listings
2. Use the get_local_experiences tool to suggest activities
3. Compare options and make personalized recommendations
4. Consider the traveler's budget, interests, and travel style""",
)

response = await agent.run(
    "I'm visiting Tokyo for 5 nights in April with my partner. We love traditional Japanese culture and food. "
    "Find us a place to stay and suggest some experiences.",
    )
print(response)
```

## MCP 在生产环境中的应用

在生产环境中，MCP 支持强大的使用模式：

- **动态工具发现** ：Agent 可连接到 MCP 服务器并在运行时发现工具
- **解耦架构** ：工具提供者可以独立于 Agent 进行更新
- **跨组织共享** ：团队可以通过 MCP 服务器公开能力，任何 Agent 都能使用
- **Microsoft Agent Framework支持** ：MAF 通过 `mcp` 集成内置了 MCP 客户端支持

使用真正的 MCP 服务器与 MAF 时，可以通过 `hosted_mcp_tool()` 或 MCP 客户端集成连接。

 **了解更多：** 
- [MCP 规范](https://modelcontextprotocol.io/)
- [Microsoft Agent Framework MCP 支持](https://github.com/microsoft/agent-framework/tree/main/python/samples/02-agents/mcp)

## 总结

在本课中，你学到了：
- **MCP** 是一种用于 Agent 和工具提供商之间动态工具发现的开放标准
- **客户端-服务器架构** 允许 Agent 在运行时发现功能
- MCP 支持 **可扩展、解耦的 Agent 系统** ，工具可以在不更改代码的情况下添加
- Microsoft Agent Framework 提供了用于生产环境的 **内置 MCP 支持** 


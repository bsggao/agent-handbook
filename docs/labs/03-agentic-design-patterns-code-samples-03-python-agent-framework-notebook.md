---
title: "03 · 03-python-agent-framework"
outline: [2, 3]
---

# 03 · 03-python-agent-framework

[返回：Agent 设计模式](/lessons/design-patterns.md) · [不可变原始文件](https://github.com/microsoft/ai-agents-for-beginners/blob/25b7985f3b2dc37a84f4a7387ccd3c9f0e5b1595/03-agentic-design-patterns/code_samples/03-python-agent-framework.ipynb)

::: warning 原课程完整 Notebook · 静态阅读与代码解析
代码按英文源文件顺序保留，中文说明以同版本译本为基础。原始安装单元格可能含无版本上限的 `-U`；请跳过它们，先按[准备篇](/lessons/setup.md)固定依赖。云端服务、模型权限、网站布局和部分 SDK 接口需在你自己的环境验证。本站没有执行云端请求；第 18 章的离线验证状态单独记录在[检查报告](/guide/verification.md)。
:::

## 运行准备

Python 3.12+；在独立虚拟环境安装源仓库依赖与本页中声明的额外依赖。原文件路径：`upstream/03-agentic-design-patterns/code_samples/03-python-agent-framework.ipynb`。以原仓库根目录为工作目录，在 Jupyter 中按顺序执行；身份与环境变量见准备篇。

```bash
cd upstream
python -m jupyterlab
```

[下载原始 Notebook](/notebooks/03-agentic-design-patterns/code_samples/03-python-agent-framework.ipynb)。输出为上游文件保存的历史结果，不能用作本站实测证明。

## 第03课 - Agent 设计模式

在本课中，我们将探索构建高效 AI Agent 的三个基础设计模式：

1. **清晰的 Agent 指令** — 制作精确的、定义角色的提示，以指导 Agent 行为
2. **使用 Pydantic 模型的结构化输出** — 确保 Agent 返回可预测、已验证的数据
3. **单一职责 Agent** — 设计专注的 Agent，每个 Agent 专注做好一件事

我们将把每种模式应用于一个 **旅游目的地推荐系统** 场景，逐步构建一个能够推荐目的地、检查可用性和处理物流的系统。

## 设置

### 代码单元格 3

阅读提示：跟踪本单元格读取的变量、修改的状态以及返回值。按原顺序执行，确认依赖的前序变量已经存在。

```text
%pip install agent-framework azure-ai-projects azure-identity pydantic python-dotenv --quiet
```

### 代码单元格 4

配置加载：从本地环境读取端点与部署名；缺少变量时先修复配置，不要把密钥写进代码。

数据结构：Pydantic 模型定义字段类型；只有传入实际的 response_format 并检查解析结果，才能约束本次输出。

模型连接：project_endpoint 是项目地址，model 是实际部署名称；credential 提供访问身份。客户端创建本身不证明已经部署服务端 Agent。

```python
import logging
logging.getLogger("agent_framework.foundry").setLevel(logging.ERROR)

import os
import asyncio
import dotenv
from typing import Annotated
from pydantic import BaseModel
from agent_framework import tool
from agent_framework.foundry import FoundryChatClient
from azure.identity import DefaultAzureCredential

dotenv.load_dotenv(dotenv.find_dotenv())

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

provider = FoundryChatClient(
    project_endpoint=endpoint,
    model=deployment_name,
    credential=DefaultAzureCredential()
)
```

## 模式1：明确的 Agent 指令

最有影响力的模式也是最简单的：为你的 Agent 编写清晰、详细的指令。

良好的指令应定义：
- **Agent 是谁** （角色和语气）
- **Agent 该做什么** （逐步职责）
- **Agent 应如何表现** （约束和风格）

下面，我们创建一个旅行礼宾 Agent，带有明确的指令来塑造它生成的每个回复。

### 代码单元格 6

行为约束：instructions 引导模型，不能替代执行器的权限验证、次数限制和结果检查。

输出观察：print 展示应用可观察结果；预存输出和现场结果可能不同，它不是模型内部思考记录。

```python
agent = provider.as_agent(
    name="TravelConcierge",
    instructions="""You are a luxury travel concierge named Alex. Your role is to:
1. Understand the traveler's preferences (budget, climate, activities)
2. Check destination availability before making recommendations
3. Provide detailed, personalized travel suggestions
4. Always mention visa requirements and best travel seasons
Be warm, professional, and enthusiastic about travel.""",
)

response = await agent.run(
    "I'd love a week-long vacation somewhere with great food and history. Budget around $2500."
)
print(response)
```

## 模式 2：使用 Pydantic 模型的结构化输出

自由形式文本对对话很有用，但下游系统需要结构化数据。
通过将 **Pydantic 模型** 与 **工具函数** 配对，我们可以：

- 定义 Agent 输出的精确定义模式
- 自动验证响应
- 可靠地将 Agent 结果集成到应用逻辑中

执行的关键是在运行 Agent 时传递 `response_format`。这会强制
模型返回一个经过验证的 `TravelRecommendations` 对象（可通过 `response.value` 访问）
，而不是自由格式文本。`get_destination_details` 工具也返回类型化的
`DestinationRecommendation`，因此数据从始至终保持结构化。

### 代码单元格 8

工具定义：类型注解和文档字符串描述输入、用途；模型产生调用请求，框架在应用进程中执行函数。检查是否需要人工批准。

数据结构：Pydantic 模型定义字段类型；只有传入实际的 response_format 并检查解析结果，才能约束本次输出。

行为约束：instructions 引导模型，不能替代执行器的权限验证、次数限制和结果检查。

```python
class DestinationRecommendation(BaseModel):
    destination: str
    available: bool
    best_season: str
    highlights: list[str]
    estimated_budget_usd: int


class TravelRecommendations(BaseModel):
    recommendations: list[DestinationRecommendation]
    personalized_note: str


@tool(approval_mode="never_require")
def get_destination_details(
    destination: Annotated[str, "The destination to look up"]
) -> DestinationRecommendation:
    """Get structured details about a vacation destination."""
    details = {
        "Barcelona": DestinationRecommendation(
            destination="Barcelona",
            available=True,
            best_season="May-Jun",
            highlights=["Beach", "Architecture", "Nightlife"],
            estimated_budget_usd=2000,
        ),
        "Tokyo": DestinationRecommendation(
            destination="Tokyo",
            available=True,
            best_season="Mar-Apr",
            highlights=["Culture", "Food", "Technology"],
            estimated_budget_usd=2500,
        ),
        "Cape Town": DestinationRecommendation(
            destination="Cape Town",
            available=False,
            best_season="Nov-Mar",
            highlights=["Nature", "Wine", "Adventure"],
            estimated_budget_usd=1800,
        ),
    }
    return details.get(
        destination,
        DestinationRecommendation(
            destination=destination,
            available=False,
            best_season="Unknown",
            highlights=[],
            estimated_budget_usd=0,
        ),
    )


structured_agent = provider.as_agent(
    name="StructuredTravelExpert",
    instructions="You are a travel expert. Recommend destinations based on traveler preferences. Use the get_destination_details tool.",
    tools=[get_destination_details],
)

# Passing `response_format` forces the agent to return a validated
# TravelRecommendations object instead of free-form text.
response = await structured_agent.run(
    "Recommend 3 destinations for a culture-loving traveler with a $2500 budget",
    options={"response_format": TravelRecommendations},
)

if response and response.value:
    result: TravelRecommendations = response.value
    for rec in result.recommendations:
        status = "Available" if rec.available else "Not available"
        print(f"{rec.destination} ({status})")
        print(f"  Best season: {rec.best_season}")
        print(f"  Highlights: {', '.join(rec.highlights)}")
        print(f"  Estimated budget: ${rec.estimated_budget_usd}")
        print()
    print(f"Note: {result.personalized_note}")
else:
    print("No validated structured response was returned.")
    print(response)
```

## 模式 3：单一职责 Agent

复杂任务通过将工作拆分为多个专注的 Agent 来执行，每个 Agent 负责单一职责：

- 一个了解地点和可用性的 **目的地专家** 
- 一个处理航班、酒店和行程的 **物流规划师** 

这与软件工程中的*关注点分离*原则相呼应——每个 Agent 都更容易独立测试、维护和改进。

### 代码单元格 10

行为约束：instructions 引导模型，不能替代执行器的权限验证、次数限制和结果检查。

检索过程：跟踪查询、候选结果和实际选入的证据；检索为空时应明确返回缺失，而不是补写答案。

输出观察：print 展示应用可观察结果；预存输出和现场结果可能不同，它不是模型内部思考记录。

```python
destination_agent = provider.as_agent(
    name="DestinationExpert",
    tools=[get_destination_details],
    instructions="""You are a destination research specialist. Your only job is to:
1. Evaluate destinations based on traveler preferences
2. Check availability using the provided tool
3. Return a short ranked list with pros/cons
Do NOT discuss flights, hotels, or logistics — another agent handles that.""",
)

logistics_agent = provider.as_agent(
    name="LogisticsPlanner",
    instructions="""You are a travel logistics planner. Your only job is to:
1. Create a day-by-day itinerary for the chosen destination
2. Suggest flight and hotel options within the stated budget
3. Note visa requirements and travel insurance recommendations
Do NOT recommend destinations — another agent handles that.""",
)

# Step 1: Destination Expert picks the best options
dest_response = await destination_agent.run(
    "I want a week of culture and food for under $2500. Where should I go?"
)
print("=== Destination Expert ===")
print(dest_response)

# Step 2: Logistics Planner builds the trip plan
logistics_response = await logistics_agent.run(
    f"Plan a week-long trip based on this recommendation:\n{dest_response}"
)
print("\n=== Logistics Planner ===")
print(logistics_response)
```

## 总结

在本课中，我们将三个主动设计模式应用于旅游推荐场景：

| 模式 | 关键思想 | 优势 |
|---|---|---|
| **明确指令** | 预先定义角色、职责和约束 | 保持一致、符合品牌形象的 Agent 行为 |
| **结构化输出** | 使用Pydantic模型作为响应格式 | 经过验证、机器可读的结果 |
| **单一职责** | 让每个 Agent 专注于一项工作 | 更易测试、维护和组合 |

这些模式自然组合——你可以将明确指令与结构化输出结合到单一职责 Agent 中，构建健壮、适合生产的系统。


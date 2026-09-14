---
title: "04 · 04-python-agent-framework"
outline: [2, 3]
---

# 04 · 04-python-agent-framework

[返回：工具调用](/lessons/tools.md) · [不可变原始文件](https://github.com/microsoft/ai-agents-for-beginners/blob/25b7985f3b2dc37a84f4a7387ccd3c9f0e5b1595/04-tool-use/code_samples/04-python-agent-framework.ipynb)

::: warning 原课程完整 Notebook · 静态阅读与代码解析
代码按英文源文件顺序保留，中文说明以同版本译本为基础。原始安装单元格可能含无版本上限的 `-U`；请跳过它们，先按[准备篇](/lessons/setup.md)固定依赖。云端服务、模型权限、网站布局和部分 SDK 接口需在你自己的环境验证。本站没有执行云端请求；第 18 章的离线验证状态单独记录在[检查报告](/guide/verification.md)。
:::

## 运行准备

Python 3.12+；在独立虚拟环境安装源仓库依赖与本页中声明的额外依赖。原文件路径：`upstream/04-tool-use/code_samples/04-python-agent-framework.ipynb`。以原仓库根目录为工作目录，在 Jupyter 中按顺序执行；身份与环境变量见准备篇。

```bash
cd upstream
python -m jupyterlab
```

[下载原始 Notebook](/notebooks/04-tool-use/code_samples/04-python-agent-framework.ipynb)。输出为上游文件保存的历史结果，不能用作本站实测证明。

## 课程 04 - 工具使用设计模式

在本课中，你将学习使用 Microsoft Agent Framework (Python) 的 AI Agent 的 **工具使用** 设计模式。我们涵盖：

- 使用 `@tool` 装饰器和类型化参数定义函数工具
- 提供工具模式，让模型了解每个工具的功能
- 使用 `approval_mode` 控制工具执行
- 通过 Pydantic 模型和 `response_format` 返回 **结构化输出** 

方案是一个 **旅游预订 Agent** ，可以查询目的地，检查可用性，并检索航班信息。

## 设置

### 代码单元格 3

阅读提示：跟踪本单元格读取的变量、修改的状态以及返回值。按原顺序执行，确认依赖的前序变量已经存在。

```text
%pip install agent-framework azure-ai-projects azure-identity python-dotenv -U -q
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

## 使用 @tool 装饰器定义工具

`@tool` 装饰器将普通的 Python 函数转换为 Agent 可以调用的工具。
关键点：

- **文档字符串** 成为模型看到的工具描述。
- **类型注解** （包括带描述的 `Annotated`）定义工具的模式。
- `approval_mode` 控制是否必须在执行前让用户批准每次调用。

### 代码单元格 7

工具定义：类型注解和文档字符串描述输入、用途；模型产生调用请求，框架在应用进程中执行函数。检查是否需要人工批准。

```python
@tool(approval_mode="never_require")
def get_destinations() -> list[str]:
    """Get available vacation destinations."""
    return ["Barcelona", "Paris", "Berlin", "Tokyo", "Sydney", "New York City"]


@tool(approval_mode="never_require")
def check_availability(
    destination: Annotated[str, "The destination to check"],
) -> str:
    """Check booking availability for a destination."""
    availability = {
        "Barcelona": "Available - 3 spots left",
        "Paris": "Available",
        "Berlin": "Sold out",
        "Tokyo": "Available - 1 spot left",
        "Sydney": "Available",
        "New York City": "Available",
    }
    return availability.get(destination, "Unknown destination")


@tool(approval_mode="never_require")
def get_flight_info(
    origin: Annotated[str, "Origin airport code"],
    destination: Annotated[str, "Destination airport code"],
) -> str:
    """Get flight information between two cities."""
    flights = {
        "LHR-BCN": "BA 2042, Departs 08:30, Arrives 11:45, $350",
        "LHR-CDG": "AF 1081, Departs 09:15, Arrives 11:30, $280",
        "LHR-NRT": "JL 044, Departs 11:00, Arrives 07:00+1, $890",
    }
    return flights.get(
        f"{origin}-{destination}",
        f"No direct flights from {origin} to {destination}",
    )
```

## 创建一个拥有多种工具的 Agent

将所有三种工具传递给客户端，这样模型就可以调用它们中的任意一个来回答用户的问题。

### 代码单元格 9

行为约束：instructions 引导模型，不能替代执行器的权限验证、次数限制和结果检查。

输出观察：print 展示应用可观察结果；预存输出和现场结果可能不同，它不是模型内部思考记录。

```python
travel_tools = [get_destinations, check_availability, get_flight_info]

agent = client.as_agent(
    name="TravelToolAgent",
    instructions="You are a travel agent. Use the available tools to answer questions about destinations, availability, and flights.",
    tools=travel_tools,
)

response = await agent.run(
    "What destinations do you have? Which ones are still available?"
)
print(response)
```

## 使用工具进行结构化输出

通过将 `response_format` 设置为 Pydantic 模型，Agent 被强制返回一个类型良好的 JSON 对象，而不是自由格式的文本。当下游代码需要以编程方式消费结果时，这很有用。

### 代码单元格 11

数据结构：Pydantic 模型定义字段类型；只有传入实际的 response_format 并检查解析结果，才能约束本次输出。

行为约束：instructions 引导模型，不能替代执行器的权限验证、次数限制和结果检查。

输出观察：print 展示应用可观察结果；预存输出和现场结果可能不同，它不是模型内部思考记录。

```python
class BookingRecommendation(BaseModel):
    destination: str
    available: bool
    flight_details: str
    estimated_cost: int


class TravelPlan(BaseModel):
    recommendations: list[BookingRecommendation]


structured_agent = client.as_agent(
    name="StructuredTravelAgent",
    instructions=(
        "You are a travel agent. Use the available tools to find destinations, "
        "check availability, and get flight info. Return structured results."
    ),
    tools=[get_destinations, check_availability, get_flight_info],
)

response = await structured_agent.run(
    "I want to fly from London Heathrow to somewhere warm in Europe. "
    "Check what's available."
)
if response:
    print(response)
```

## 工具批准模式

`@tool` 上的 `approval_mode` 参数控制工具调用在执行前是否需要人工批准：

| 模式 | 行为 |
|---|---|
| `"never_require"` | 工具自动运行 — 不需要用户确认。 |
| `"always_require"` | 每次调用都必须得到用户批准后才能执行。 |

对于有副作用的工具（例如预订航班、扣费信用卡），使用 `"always_require"`，以确保有人介入。

### 代码单元格 13

工具定义：类型注解和文档字符串描述输入、用途；模型产生调用请求，框架在应用进程中执行函数。检查是否需要人工批准。

输出观察：print 展示应用可观察结果；预存输出和现场结果可能不同，它不是模型内部思考记录。

```python
@tool(approval_mode="always_require")
def book_flight(
    origin: Annotated[str, "Origin airport code"],
    destination: Annotated[str, "Destination airport code"],
    passenger_name: Annotated[str, "Full name of the passenger"],
) -> str:
    """Book a flight for a passenger. Requires approval before executing."""
    return (
        f"Flight booked from {origin} to {destination} "
        f"for {passenger_name}. Confirmation #TRV-2024-{hash(passenger_name) % 10000:04d}"
    )


print("Tool name:", book_flight.name)
print("Approval mode:", book_flight.approval_mode)
```

## 总结

在本课中，你学习了如何：

1. 使用带有类型参数和文档字符串的 `@tool` 装饰器 **定义工具** ，这些文档字符串用作工具模式。
2. **组合多个工具** ，以便 Agent 能够按顺序调用它们来回答复杂查询。
3. 通过传递 Pydantic 模型作为 `response_format`， **返回结构化输出** 。
4. 使用 `approval_mode` **控制工具审批** ，以便在人类监督下执行敏感操作。

这些模式构成了构建可靠、生产就绪 Agent 的基础，这些 Agent 能够安全地与外部系统交互。


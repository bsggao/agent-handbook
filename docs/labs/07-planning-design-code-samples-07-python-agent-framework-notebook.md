---
title: "07 · 07-python-agent-framework"
outline: [2, 3]
---

# 07 · 07-python-agent-framework

[返回：规划模式](/lessons/planning.md) · [不可变原始文件](https://github.com/microsoft/ai-agents-for-beginners/blob/25b7985f3b2dc37a84f4a7387ccd3c9f0e5b1595/07-planning-design/code_samples/07-python-agent-framework.ipynb)

::: warning 原课程完整 Notebook · 静态阅读与代码解析
代码按英文源文件顺序保留，中文说明以同版本译本为基础。原始安装单元格可能含无版本上限的 `-U`；请跳过它们，先按[准备篇](/lessons/setup.md)固定依赖。云端服务、模型权限、网站布局和部分 SDK 接口需在你自己的环境验证。本站没有执行云端请求；第 18 章的离线验证状态单独记录在[检查报告](/guide/verification.md)。
:::

## 运行准备

Python 3.12+；在独立虚拟环境安装源仓库依赖与本页中声明的额外依赖。原文件路径：`upstream/07-planning-design/code_samples/07-python-agent-framework.ipynb`。以原仓库根目录为工作目录，在 Jupyter 中按顺序执行；身份与环境变量见准备篇。

```bash
cd upstream
python -m jupyterlab
```

[下载原始 Notebook](/notebooks/07-planning-design/code_samples/07-python-agent-framework.ipynb)。输出为上游文件保存的历史结果，不能用作本站实测证明。

## 第07课 - 规划设计模式

本笔记本演示了使用Microsoft Agent Framework的 **规划设计模式** ，适用于AI Agent。
你将学习如何将复杂的旅行请求拆分为结构化的子任务，分配给专业 Agent，
并执行生成的计划——所有这些都通过Pydantic模型驱动的结构化输出实现。

## 设置

### 代码单元格 3

阅读提示：跟踪本单元格读取的变量、修改的状态以及返回值。按原顺序执行，确认依赖的前序变量已经存在。

```text
%pip install agent-framework azure-ai-projects azure-identity python-dotenv -q
```

### 代码单元格 4

配置加载：从本地环境读取端点与部署名；缺少变量时先修复配置，不要把密钥写进代码。

数据结构：Pydantic 模型定义字段类型；只有传入实际的 response_format 并检查解析结果，才能约束本次输出。

模型连接：project_endpoint 是项目地址，model 是实际部署名称；credential 提供访问身份。客户端创建本身不证明已经部署服务端 Agent。

```python
import logging
logging.getLogger("agent_framework.foundry").setLevel(logging.ERROR)

import os, asyncio
import dotenv
from typing import Annotated
from pydantic import BaseModel
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

## 任务分解

任务分解是规划设计模式的核心。我们不是让单个 Agent 端到端处理复杂请求，
而是将问题拆解为更小的、定义明确的 **子任务** 。
每个子任务被分配给一个专业 Agent（例如，航班、酒店、活动），并有清晰的
优先级和依赖顺序。

这种方法带来若干好处：
- **清晰性** ：每个子任务都有单一职责。
- **并行性** ：独立子任务可并发运行。
- **可靠性** ：失败被限制在单个子任务内。
- **预算追踪** ：成本按子任务估算并汇总。

### 代码单元格 7

数据结构：Pydantic 模型定义字段类型；只有传入实际的 response_format 并检查解析结果，才能约束本次输出。

```python
class TravelSubTask(BaseModel):
    task_id: int
    description: str
    assigned_agent: str  # "flight_agent", "hotel_agent", "activity_agent"
    priority: str  # "high", "medium", "low"
    dependencies: list[int] = []


class TravelPlan(BaseModel):
    destination: str
    trip_duration_days: int
    subtasks: list[TravelSubTask]
    total_estimated_budget_usd: int
    notes: str
```

## 使用结构化输出创建规划 Agent

规划 Agent 充当前台协调员。根据高级别的旅行请求，它
生成一个结构化的 `TravelPlan` —— 将请求分解为子任务，设定优先级，
并识别依赖关系，以便礼宾或执行层能够完成工作。

### 代码单元格 9

行为约束：instructions 引导模型，不能替代执行器的权限验证、次数限制和结果检查。

输出观察：print 展示应用可观察结果；预存输出和现场结果可能不同，它不是模型内部思考记录。

```python
planning_agent = client.as_agent(
    name="TravelPlanner",
    instructions="""You are a travel planning agent. When given a travel request:
1. Break it into specific subtasks (flights, hotels, activities, logistics)
2. Assign each subtask to the appropriate specialist agent
3. Set priorities and identify dependencies between tasks
4. Estimate the total budget""",
)

result = await planning_agent.run(
    "Plan a 7-day trip to Paris for a couple interested in art, cuisine, and history. Budget around $5000.",
    options={"response_format": TravelPlan}
)
if result:
    plan = result.value
    print(f"Destination: {plan.destination}")
    print(f"Duration: {plan.trip_duration_days} days")
    print(f"Budget: ${plan.total_estimated_budget_usd}")
    print(f"\nSubtasks:")
    for task in plan.subtasks:
        print(f"  [{task.priority}] {task.task_id}. {task.description} → {task.assigned_agent}")
```

## 使用专业工具执行计划

一旦前台 Agent 生成了结构化计划， **管家 Agent** 就会执行该计划。
每个专业工具处理一类子任务（航班、酒店、活动）。管家
按依赖顺序遍历计划的子任务，并将每个子任务分派给
适当的工具。

### 代码单元格 11

工具定义：类型注解和文档字符串描述输入、用途；模型产生调用请求，框架在应用进程中执行函数。检查是否需要人工批准。

行为约束：instructions 引导模型，不能替代执行器的权限验证、次数限制和结果检查。

输出观察：print 展示应用可观察结果；预存输出和现场结果可能不同，它不是模型内部思考记录。

```python
@tool
def book_flight(
    destination: Annotated[str, "The destination city"],
    departure_date: Annotated[str, "Departure date (YYYY-MM-DD)"],
    return_date: Annotated[str, "Return date (YYYY-MM-DD)"],
) -> str:
    """Search and book flights for the trip."""
    return f"Flight booked to {destination}: {departure_date} → {return_date}, confirmation #FLT-{hash(destination) % 10000:04d}"


@tool
def reserve_hotel(
    city: Annotated[str, "The city for the hotel"],
    check_in: Annotated[str, "Check-in date (YYYY-MM-DD)"],
    check_out: Annotated[str, "Check-out date (YYYY-MM-DD)"],
    guests: Annotated[int, "Number of guests"],
) -> str:
    """Reserve a hotel room in the destination city."""
    return f"Hotel reserved in {city}: {check_in} to {check_out} for {guests} guests, confirmation #HTL-{hash(city) % 10000:04d}"


@tool
def book_activity(
    activity_name: Annotated[str, "Name of the activity or tour"],
    date: Annotated[str, "Date of the activity (YYYY-MM-DD)"],
    participants: Annotated[int, "Number of participants"],
) -> str:
    """Book a tour, museum visit, or other activity."""
    return f"Activity booked: {activity_name} on {date} for {participants} people, confirmation #ACT-{hash(activity_name) % 10000:04d}"


# Concierge agent that executes the plan using specialist tools
concierge_agent = client.as_agent(
    name="Concierge",
    instructions="""You are a travel concierge executing a structured travel plan.
Use the available tools to fulfil each subtask. Work through the subtasks in order,
respecting dependencies. Summarise the results when finished.""",
    tools=[book_flight, reserve_hotel, book_activity],
)

# Build a prompt from the plan produced above
if result.value:
    subtask_lines = "\n".join(
        f"- [{t.priority}] {t.task_id}. {t.description} (agent: {t.assigned_agent}, deps: {t.dependencies})"
        for t in plan.subtasks
    )
    execution_prompt = (
        f"Execute the following travel plan for {plan.destination} "
        f"({plan.trip_duration_days} days, ${plan.total_estimated_budget_usd} budget):\n"
        f"{subtask_lines}"
    )

    exec_response = await concierge_agent.run(execution_prompt)
    print(exec_response)
```

## Summary

In this lesson you learned the **Planning Design Pattern** for AI agents:

1. **Task Decomposition** — A front desk planning agent breaks a complex travel request into
   structured subtasks using Pydantic models, assigning each to a specialist agent with priorities
   and dependencies.
2. **Structured Output** — By passing a `response_format` the agent returns a validated
   `TravelPlan` object instead of free-form text, making downstream processing reliable.
3. **Plan Execution** — A concierge agent iterates through the subtasks using specialist tools
   (`book_flight`, `reserve_hotel`, `book_activity`) to carry out the plan and report results.

This pattern separates *what to do* (planning) from *how to do it* (execution), making agents
more modular, testable, and easier to extend.


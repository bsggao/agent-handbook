---
title: "08 · 08-python-agent-framework"
outline: [2, 3]
---

# 08 · 08-python-agent-framework

[返回：多 Agent 协作](/lessons/multi-agent.md) · [不可变原始文件](https://github.com/microsoft/ai-agents-for-beginners/blob/25b7985f3b2dc37a84f4a7387ccd3c9f0e5b1595/08-multi-agent/code_samples/08-python-agent-framework.ipynb)

::: warning 原课程完整 Notebook · 静态阅读与代码解析
代码按英文源文件顺序保留，中文说明以同版本译本为基础。原始安装单元格可能含无版本上限的 `-U`；请跳过它们，先按[准备篇](/lessons/setup.md)固定依赖。云端服务、模型权限、网站布局和部分 SDK 接口需在你自己的环境验证。本站没有执行云端请求；第 18 章的离线验证状态单独记录在[检查报告](/guide/verification.md)。
:::

## 运行准备

Python 3.12+；在独立虚拟环境安装源仓库依赖与本页中声明的额外依赖。原文件路径：`upstream/08-multi-agent/code_samples/08-python-agent-framework.ipynb`。以原仓库根目录为工作目录，在 Jupyter 中按顺序执行；身份与环境变量见准备篇。

```bash
cd upstream
python -m jupyterlab
```

[下载原始 Notebook](/notebooks/08-multi-agent/code_samples/08-python-agent-framework.ipynb)。输出为上游文件保存的历史结果，不能用作本站实测证明。

## 第08课 - 多 Agent 设计模式

## 设置

### 代码单元格 3

配置加载：从本地环境读取端点与部署名；缺少变量时先修复配置，不要把密钥写进代码。

模型连接：project_endpoint 是项目地址，model 是实际部署名称；credential 提供访问身份。客户端创建本身不证明已经部署服务端 Agent。

```python
import logging
logging.getLogger("agent_framework.foundry").setLevel(logging.ERROR)

%pip install agent-framework azure-ai-projects azure-identity python-dotenv --quiet

import os
import asyncio
import dotenv

from agent_framework import AgentResponseUpdate, WorkflowBuilder
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

### 代码单元格 4

模型连接：project_endpoint 是项目地址，model 是实际部署名称；credential 提供访问身份。客户端创建本身不证明已经部署服务端 Agent。

```python
# Create the Microsoft Foundry client
client = FoundryChatClient(
    project_endpoint=endpoint,
    model=deployment_name,
    credential=DefaultAzureCredential()
)
```

## 为什么选择多 Agent 系统？

现实世界中的任务如旅行规划涉及多种不同的专业知识——物流、本地知识、预算等等。单个 Agent 试图处理所有事务很快就会变得难以管理。

多 Agent 系统通过 **专业化** 来解决这个问题：每个 Agent 专注于一个专业领域，产生比通才更高质量的结果。它们还提升了 **可扩展性** ——你可以添加新的 Agent（例如，航班专家、餐厅评论家）而无需重写现有的工作流程。Agent 通过结构化的管道组合在一起，将上下文从一个传递到下一个。

## 创建专用 Agent

### 代码单元格 7

行为约束：instructions 引导模型，不能替代执行器的权限验证、次数限制和结果检查。

```python
planner_agent = client.as_agent(
    name="TravelPlanner",
    instructions="You are a travel planning specialist. Create detailed trip itineraries based on the traveler's preferences. Include daily schedules, must-see attractions, and logistical tips.",
)

concierge_agent = client.as_agent(
    name="TravelConcierge",
    instructions="You are a travel concierge who reviews and enhances trip plans. Review the plan for completeness, add local insider tips, suggest restaurants, and identify potential issues. Provide your feedback in a constructive format.",
)
```

## 构建顺序工作流

`WorkflowBuilder` 让你将 Agent 连接成有向图。这里我们创建一个简单的两步管道： **TravelPlanner** 起草行程，随后 **TravelConcierge** 审核并完善它。

### 代码单元格 9

输出观察：print 展示应用可观察结果；预存输出和现场结果可能不同，它不是模型内部思考记录。

```python
workflow = WorkflowBuilder(start_executor=planner_agent) \
    .add_edge(planner_agent, concierge_agent) \
    .build()

last_author = None
events = workflow.run("Plan a 5-day trip to Paris for a food-loving couple on a $3000 budget.", stream=True)
async for event in events:
    if event.type == "output" and isinstance(event.data, AgentResponseUpdate):
        update = event.data
        author = update.author_name
        if author != last_author:
            if last_author is not None:
                print()
            print(f"\n{'='*50}")
            print(f"🤖 {author}:")
            print(f"{'='*50}")
            last_author = author
        print(update.text, end="", flush=True)
```

## 向工作流中添加更多 Agent

多 Agent 模式的最大优势之一是其易于扩展。下面我们添加了一个 **BudgetReviewer** Agent，该 Agent 检查计划是否符合旅行者的预算，标记可能导致费用超出限制的项目，并提出节省开支的替代方案。该工作流现在按顺序运行三个 Agent：

```
TravelPlanner → TravelConcierge → BudgetReviewer
```

### 代码单元格 11

行为约束：instructions 引导模型，不能替代执行器的权限验证、次数限制和结果检查。

输出观察：print 展示应用可观察结果；预存输出和现场结果可能不同，它不是模型内部思考记录。

```python
budget_agent = client.as_agent(
    name="BudgetReviewer",
    instructions="You are a budget-conscious travel advisor. Review the proposed trip plan and concierge enhancements against the traveler's stated budget. Estimate costs for flights, hotels, meals, and activities. Flag anything that risks exceeding the budget and suggest cost-saving alternatives while preserving the trip's quality.",
)

extended_workflow = WorkflowBuilder(start_executor=planner_agent) \
    .add_edge(planner_agent, concierge_agent) \
    .add_edge(concierge_agent, budget_agent) \
    .build()

last_author = None
events = extended_workflow.run("Plan a 5-day trip to Paris for a food-loving couple on a $3000 budget.", stream=True)
async for event in events:
    if event.type == "output" and isinstance(event.data, AgentResponseUpdate):
        update = event.data
        author = update.author_name
        if author != last_author:
            if last_author is not None:
                print()
            print(f"\n{'='*50}")
            print(f"🤖 {author}:")
            print(f"{'='*50}")
            last_author = author
        print(update.text, end="", flush=True)
```

## 总结

在本课中，你学会了如何：

1. **创建专业 Agent** — 每个 Agent 有专注的角色（规划、礼宾、预算审查）。
2. **使用 `WorkflowBuilder` 和 `add_edge` 将 Agent 连接成顺序工作流** 。
3. **从多 Agent 管道中流式输出** ，跟踪正在发言的 Agent。
4. **通过添加新 Agent 扩展工作流** ，而无需修改现有 Agent 链。

多 Agent 设计模式使每个 Agent 保持简单，同时产出比单一 Agent 更丰富、更经过彻底审查的结果。


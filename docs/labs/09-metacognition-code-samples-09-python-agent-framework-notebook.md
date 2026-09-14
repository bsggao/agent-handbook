---
title: "09 · 09-python-agent-framework"
outline: [2, 3]
---

# 09 · 09-python-agent-framework

[返回：元认知与反思](/lessons/reflection.md) · [不可变原始文件](https://github.com/microsoft/ai-agents-for-beginners/blob/25b7985f3b2dc37a84f4a7387ccd3c9f0e5b1595/09-metacognition/code_samples/09-python-agent-framework.ipynb)

::: warning 原课程完整 Notebook · 静态阅读与代码解析
代码按英文源文件顺序保留，中文说明以同版本译本为基础。原始安装单元格可能含无版本上限的 `-U`；请跳过它们，先按[准备篇](/lessons/setup.md)固定依赖。云端服务、模型权限、网站布局和部分 SDK 接口需在你自己的环境验证。本站没有执行云端请求；第 18 章的离线验证状态单独记录在[检查报告](/guide/verification.md)。
:::

## 运行准备

Python 3.12+；在独立虚拟环境安装源仓库依赖与本页中声明的额外依赖。原文件路径：`upstream/09-metacognition/code_samples/09-python-agent-framework.ipynb`。以原仓库根目录为工作目录，在 Jupyter 中按顺序执行；身份与环境变量见准备篇。

```bash
cd upstream
python -m jupyterlab
```

[下载原始 Notebook](/notebooks/09-metacognition/code_samples/09-python-agent-framework.ipynb)。输出为上游文件保存的历史结果，不能用作本站实测证明。

## 第09课 - 元认知设计模式

## 设置

本笔记本演示了使用Microsoft Agent Framework的元认知设计模式。

 **先决条件：** 
- 通过环境变量配置的 Azure OpenAI 部署
- 通过 Azure CLI 验证身份（`az login`）

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

## 什么是元认知？

元认知是 **关于思考的思考** 。在人工智能 Agent 的背景下，它意味着构建能够：

- **自我反思** 自己的输出和推理过程
- **检测错误** 并优雅地恢复，而不是默默失败
- **评估** 其回答是否完整且有帮助
- **适应** 策略，当初始方法不起作用时（例如，回退到备份系统）

一个元认知 Agent 不仅仅回答问题——它监控自身性能并即时调整。

## 主要和备份工具

一个常见的元认知模式是 **回退策略** 。Agent 首先尝试主要工具；如果失败（例如，404 错误），Agent 会识别失败并透明地切换到备份工具。

这反映了现实世界的系统，其中主要服务可能不可用，Agent 必须自我诊断问题然后选择替代方案。

以下我们定义了两个航班查询工具：
- **主要** — 覆盖巴黎、东京和巴塞罗那
- **备份** — 覆盖柏林、悉尼和纽约市

### 代码单元格 8

工具定义：类型注解和文档字符串描述输入、用途；模型产生调用请求，框架在应用进程中执行函数。检查是否需要人工批准。

```python
@tool(approval_mode="never_require")
def get_flight_times(
    destination: Annotated[str, "The destination city"]
) -> str:
    """Get available flight times for a destination (primary source)."""
    flights = {
        "Paris": "Departures: 08:00, 12:30, 17:45 — from $350",
        "Tokyo": "Departures: 11:00, 23:30 — from $890",
        "Barcelona": "Departures: 07:15, 14:00, 19:30 — from $280",
    }
    if destination in flights:
        return flights[destination]
    raise Exception(f"404: No flights found for {destination} in primary system")


@tool(approval_mode="never_require")
def get_flight_times_backup(
    destination: Annotated[str, "The destination city"]
) -> str:
    """Get available flight times from backup system (used when primary fails)."""
    backup_flights = {
        "Berlin": "Departures: 09:00, 16:00 — from $220",
        "Sydney": "Departures: 22:00 — from $1200",
        "New York City": "Departures: 06:00, 10:30, 15:00, 20:00 — from $450",
    }
    return backup_flights.get(
        destination,
        f"No flights found for {destination} in any system. Please try again later.",
    )
```

## 具有错误恢复功能的自我反思 Agent

下面的 Agent 被指示首先尝试主飞行系统，识别故障，并透明地切换到备用系统。在每次响应后，它会简要地自我评估是否完全回答了用户的问题。

### 代码单元格 10

行为约束：instructions 引导模型，不能替代执行器的权限验证、次数限制和结果检查。

输出观察：print 展示应用可观察结果；预存输出和现场结果可能不同，它不是模型内部思考记录。

```python
agent = client.as_agent(
    tools=[get_flight_times, get_flight_times_backup],
    name="FlightBookingAgent",
    instructions="""You are a flight booking agent with self-reflection capabilities.

When looking up flights:
1. Try the primary flight system first (get_flight_times)
2. If the primary system fails (404 error), acknowledge the error and try the backup system (get_flight_times_backup)
3. Always explain to the user what happened — be transparent about fallbacks
4. If both systems fail, apologize and suggest alternatives

After each response, briefly evaluate whether your answer was complete and helpful.""",
)

# Test with a destination in primary system
print("=== Test 1: Destination in primary system ===")
response = await agent.run(
    "What flights are available to Paris?",
    )
print(response)

# Test with a destination only in backup system
print("\n=== Test 2: Destination only in backup system ===")
response = await agent.run(
    "What flights are available to Berlin?",
    )
print(response)
```

## 自我评估模式

元认知的另一个方面是 **自我评估** ：一个独立的 Agent（或同一个 Agent 在第二遍处理时）会审查回答的完整性、准确性和有用性。

下面我们创建一个 `ResponseEvaluator` Agent，对旅行 Agent 的回答从三个维度进行评分。

### 代码单元格 12

行为约束：instructions 引导模型，不能替代执行器的权限验证、次数限制和结果检查。

输出观察：print 展示应用可观察结果；预存输出和现场结果可能不同，它不是模型内部思考记录。

```python
evaluation_agent = client.as_agent(
    tools=[get_flight_times, get_flight_times_backup],
    name="ResponseEvaluator",
    instructions="""You are a quality evaluator for travel agent responses.
Given a travel question and the agent's response, evaluate:
1. Completeness: Did it answer all parts of the question? (1-5)
2. Accuracy: Is the information correct? (1-5)
3. Helpfulness: Would a traveler find this useful? (1-5)
Provide a brief evaluation with scores and one suggestion for improvement.""",
)

# Evaluate the agent's response from Test 1
eval_prompt = f"""Question: What flights are available to Paris?
Agent Response: {response}

Please evaluate the above response."""

evaluation = await evaluation_agent.run(eval_prompt)
print("=== Self-Evaluation ===")
print(evaluation)
```

## 总结

在本课中，你学习了如何使用 Microsoft Agent Framework 构建 **元认知 Agent** ：

- **自我反思** ：监控自身推理过程并透明地传达发生内容的 Agent。
- **带回退的错误恢复** ：一种主工具 + 备用工具的模式，Agent 检测失败（例如 404 错误）并自动尝试备用来源。
- **自我评估** ：一个独立的评估 Agent，对响应的完整性、准确性和有用性进行评分。

这些模式使 Agent 更加稳健、透明和值得信赖——这是生产部署的关键品质。


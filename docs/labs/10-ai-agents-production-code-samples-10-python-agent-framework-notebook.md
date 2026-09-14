---
title: "10 · 10-python-agent-framework"
outline: [2, 3]
---

# 10 · 10-python-agent-framework

[返回：Agent 生产实践](/lessons/production.md) · [不可变原始文件](https://github.com/microsoft/ai-agents-for-beginners/blob/25b7985f3b2dc37a84f4a7387ccd3c9f0e5b1595/10-ai-agents-production/code_samples/10-python-agent-framework.ipynb)

::: warning 原课程完整 Notebook · 静态阅读与代码解析
代码按英文源文件顺序保留，中文说明以同版本译本为基础。原始安装单元格可能含无版本上限的 `-U`；请跳过它们，先按[准备篇](/lessons/setup.md)固定依赖。云端服务、模型权限、网站布局和部分 SDK 接口需在你自己的环境验证。本站没有执行云端请求；第 18 章的离线验证状态单独记录在[检查报告](/guide/verification.md)。
:::

## 运行准备

Python 3.12+；在独立虚拟环境安装源仓库依赖与本页中声明的额外依赖。原文件路径：`upstream/10-ai-agents-production/code_samples/10-python-agent-framework.ipynb`。以原仓库根目录为工作目录，在 Jupyter 中按顺序执行；身份与环境变量见准备篇。

```bash
cd upstream
python -m jupyterlab
```

[下载原始 Notebook](/notebooks/10-ai-agents-production/code_samples/10-python-agent-framework.ipynb)。输出为上游文件保存的历史结果，不能用作本站实测证明。

## 第10课 - 生产环境中的 AI Agent

在本课中，你将学习使用 Microsoft Agent Framework (Python) 的 AI Agent **生产模式** 。我们涵盖：

- **可观测性** — 为 Agent 交互添加计时和日志记录
- **评估** — 使用评估 Agent 为响应质量打分
- **成本管理** — 代币优化和模型选择的策略

场景是一个帮助用户规划旅行的 **旅行 Agent** ，并在其上叠加监控和评估。

## 设置

### 代码单元格 3

阅读提示：跟踪本单元格读取的变量、修改的状态以及返回值。按原顺序执行，确认依赖的前序变量已经存在。

```text
%pip install agent-framework azure-ai-projects azure-identity python-dotenv -U -q
```

### 代码单元格 4

配置加载：从本地环境读取端点与部署名；缺少变量时先修复配置，不要把密钥写进代码。

模型连接：project_endpoint 是项目地址，model 是实际部署名称；credential 提供访问身份。客户端创建本身不证明已经部署服务端 Agent。

```python
import logging
logging.getLogger("agent_framework.foundry").setLevel(logging.ERROR)

import os
import asyncio
import time
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

## 生产考虑

将 AI Agent 从原型转移到生产环境需要仔细关注三个支柱：

1. **可观察性** — 你需要了解 Agent 在做什么，耗时多久，以及调用了哪些工具。没有跟踪和日志，调试生产问题几乎不可能。

2. **评估** — 自动化质量检查确保 Agent 的响应随着时间保持准确、完整且有帮助。评估 Agent 可以根据定义的标准对响应进行评分。

3. **成本管理** — Token使用直接影响成本。诸如提示优化、模型选择和缓存等策略有助于在不牺牲质量的前提下控制开支。

## 构建一个可观察 Agent

我们定义了旅行工具并用计时包装了 Agent 调用，以便我们能够监控延迟。在生产环境中，你会集成OpenTelemetry或类似的追踪后端。

### 代码单元格 8

工具定义：类型注解和文档字符串描述输入、用途；模型产生调用请求，框架在应用进程中执行函数。检查是否需要人工批准。

```python
@tool(approval_mode="never_require")
def get_flight_info(destination: Annotated[str, "The destination city"]) -> str:
    """Get flight information for a destination."""
    flights = {
        "Paris": "BA 304, 08:30-11:45, $350",
        "Tokyo": "JL 044, 11:00-07:00+1, $890",
        "Barcelona": "VY 7821, 07:15-10:30, $280",
    }
    return flights.get(destination, f"No flights found to {destination}")


@tool(approval_mode="never_require")
def get_activity_suggestions(destination: Annotated[str, "The destination city"]) -> str:
    """Get activity suggestions for a destination."""
    activities = {
        "Paris": "Louvre Museum, Eiffel Tower, Seine River Cruise, Montmartre walking tour",
        "Tokyo": "Senso-ji Temple, Tsukiji Market tour, Shibuya Crossing, teamLab Borderless",
        "Barcelona": "Sagrada Familia, Park Güell, La Boqueria Market, Gothic Quarter walk",
    }
    return activities.get(destination, f"No activities found for {destination}")
```

### 代码单元格 9

行为约束：instructions 引导模型，不能替代执行器的权限验证、次数限制和结果检查。

输出观察：print 展示应用可观察结果；预存输出和现场结果可能不同，它不是模型内部思考记录。

```python
agent = client.as_agent(
    tools=[get_flight_info, get_activity_suggestions],
    name="TravelAgent",
    instructions="You are a helpful travel agent. Use the available tools to help users plan their trips. Provide comprehensive, actionable travel advice.",
)

# Simple observability: track timing
start_time = time.time()
response = await agent.run(
    "I want to plan a day trip in Paris. What flights and activities do you recommend?",
    )
elapsed = time.time() - start_time
print(f"Response ({elapsed:.2f}s):\n{response}")
```

## 评估模式

一个常见的生产模式是使用第二个 Agent 作为 **评估者** 。评估者根据预定义的标准（如完整性、准确性和有用性）对主 Agent 的响应进行评分。

这可以实现：
- 在响应传达给用户之前自动进行质量把关
- 在提示词或模型发生变化时检测回归
- 持续监控 Agent 的性能表现

### 代码单元格 11

行为约束：instructions 引导模型，不能替代执行器的权限验证、次数限制和结果检查。

输出观察：print 展示应用可观察结果；预存输出和现场结果可能不同，它不是模型内部思考记录。

```python
evaluator = client.as_agent(
    name="ResponseEvaluator",
    instructions="""You evaluate travel agent responses on these criteria:
1. Completeness (1-5): Did it cover flights AND activities?
2. Accuracy (1-5): Is the information consistent?
3. Helpfulness (1-5): Would a traveler find this actionable?
4. Overall Score (1-5)
Provide scores and a brief explanation for each.""",
)

evaluation = await evaluator.run(f"Evaluate this travel agent response:\n\n{response}")
print(f"Evaluation:\n{evaluation}")
```

## 成本管理策略

控制成本对于生产环境中的 AI Agent 至关重要。以下是关键策略：

| 策略 | 描述 |
|---|---|
| **提示优化** | 保持系统指令简洁。移除冗余上下文以减少输入Token数。 |
    "| **模型选择** | 对于分类或抽取等简单任务使用更小、更便宜的模型（如 GPT-5-mini），将复杂推理任务留给更强大的模型。 |\n",
| **缓存** | 缓存工具结果和常见查询，避免重复调用 API。 |
| **Token预算** | 设置 `max_tokens` 限制，防止回复意外过长。 |
| **批处理** | 尽可能将多个用户查询合并为一次 API 调用。 |

在实际操作中，分层方法效果良好：将简单请求路由到快速且廉价的模型，仅将复杂查询升级到更强大的模型。

## 总结

在本课中，你学习了如何：

1. **为 Agent 交互添加可观察性** ，包括时间记录和日志，为跟踪和监控打下基础。
2. **自动评估 Agent 响应** ，使用评估 Agent 对完整性、准确性和有用性进行评分。
3. **管理成本** ，通过提示优化、模型选择、缓存和Token预算实现。

这些生产模式有助于确保你的AI Agent 在大规模应用中可靠、可衡量且具有成本效益。


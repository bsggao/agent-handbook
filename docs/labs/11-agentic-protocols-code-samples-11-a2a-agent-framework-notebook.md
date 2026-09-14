---
title: "11 · 11-a2a-agent-framework"
outline: [2, 3]
---

# 11 · 11-a2a-agent-framework

[返回：Agent 协议：MCP、A2A、NLWeb](/lessons/protocols.md) · [不可变原始文件](https://github.com/microsoft/ai-agents-for-beginners/blob/25b7985f3b2dc37a84f4a7387ccd3c9f0e5b1595/11-agentic-protocols/code_samples/11-a2a-agent-framework.ipynb)

::: warning 原课程完整 Notebook · 静态阅读与代码解析
代码按英文源文件顺序保留，中文说明以同版本译本为基础。原始安装单元格可能含无版本上限的 `-U`；请跳过它们，先按[准备篇](/lessons/setup.md)固定依赖。云端服务、模型权限、网站布局和部分 SDK 接口需在你自己的环境验证。本站没有执行云端请求；第 18 章的离线验证状态单独记录在[检查报告](/guide/verification.md)。
:::

## 运行准备

Python 3.12+；在独立虚拟环境安装源仓库依赖与本页中声明的额外依赖。原文件路径：`upstream/11-agentic-protocols/code_samples/11-a2a-agent-framework.ipynb`。以原仓库根目录为工作目录，在 Jupyter 中按顺序执行；身份与环境变量见准备篇。

```bash
cd upstream
python -m jupyterlab
```

[下载原始 Notebook](/notebooks/11-agentic-protocols/code_samples/11-a2a-agent-framework.ipynb)。输出为上游文件保存的历史结果，不能用作本站实测证明。

## 第11课 - Agent 到 Agent (A2A) 协议

## 设置

### 代码单元格 3

阅读提示：跟踪本单元格读取的变量、修改的状态以及返回值。按原顺序执行，确认依赖的前序变量已经存在。

```text
%pip install agent-framework azure-ai-projects azure-identity python-dotenv
```

### 代码单元格 4

配置加载：从本地环境读取端点与部署名；缺少变量时先修复配置，不要把密钥写进代码。

模型连接：project_endpoint 是项目地址，model 是实际部署名称；credential 提供访问身份。客户端创建本身不证明已经部署服务端 Agent。

```python
import os
import dotenv
from agent_framework import tool, AgentResponseUpdate, WorkflowBuilder
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

## What is the A2A Protocol?

The **Agent-to-Agent (A2A) protocol** is an open standard that enables AI agents to communicate,
discover each other, and collaborate — even when they are built on different frameworks or hosted
by different services.

Key concepts:

- **Discovery** – Agents publish an *Agent Card* that describes their capabilities, making it
  easy for other agents (or orchestrators) to find the right specialist for a task.
- **Message Passing** – Agents exchange structured messages through a common protocol, so a
  request from one agent can be understood and fulfilled by another regardless of its internal
  implementation.
- **Task Lifecycle** – A2A defines states such as *submitted*, *working*, *completed*, and
  *failed*, giving the orchestrator full visibility into how a delegated task is progressing.

In this lesson we simulate A2A-style collaboration by wiring three specialized travel agents
into a workflow where each agent contributes its expertise and passes results to the next.

## 创建专业旅游 Agent 商

### 代码单元格 8

行为约束：instructions 引导模型，不能替代执行器的权限验证、次数限制和结果检查。

```python
currency_agent = client.as_agent(
    name="CurrencyExchangeAgent",
    instructions="""You are a currency exchange specialist. You help travelers understand:
- Current exchange rates between currencies
- Best times to exchange money
- Tips for getting the best rates
When asked about a destination, provide relevant currency information.""",
)

activity_agent = client.as_agent(
    name="ActivityPlannerAgent",
    instructions="""You are a local activities specialist. You recommend:
- Must-see attractions and hidden gems
- Local experiences and cultural activities
- Restaurant and dining recommendations
Tailor suggestions to the traveler's interests.""",
)

travel_manager = client.as_agent(
    name="TravelManagerAgent",
    instructions="""You are a travel manager who coordinates between specialist agents.
When planning a trip:
1. Gather currency information from the currency specialist
2. Get activity recommendations from the activity planner
3. Synthesize everything into a cohesive travel brief
Present the final plan in an organized, easy-to-read format.""",
)
```

## 通过工作流程实现多 Agent 协作

我们将三个 Agent 连接成一个顺序工作流程，模拟 A2A 消息传递：

1. **CurrencyExchangeAgent** 接收用户请求并提供货币指导。
2. **ActivityPlannerAgent** 接收丰富的上下文并添加活动推荐。
3. **TravelManagerAgent** 综合两个输入，生成最终的旅行简报。

### 代码单元格 10

输出观察：print 展示应用可观察结果；预存输出和现场结果可能不同，它不是模型内部思考记录。

```python
workflow = WorkflowBuilder(start_executor=currency_agent) \
    .add_edge(currency_agent, activity_agent) \
    .add_edge(activity_agent, travel_manager) \
    .build()

last_author = None
events = workflow.run(
    "Plan a week-long trip to Tokyo. I love food, temples, and technology.",
    stream=True,
)
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

## 理解生产环境中的 A2A

在生产环境中，A2A 协议解锁了强大的跨服务场景：

| 能力 | 描述 |
|---|---|
| **跨框架互操作** | 使用一个框架构建的 Agent 可以将任务委托给任何其他符合 A2A 标准的框架构建的 Agent，实现真正的跨组织互操作。 |
| **服务边界** | Agent 可以分布在不同的微服务、云区域甚至不同的组织中，同时仍能无缝协作。 |
| **动态发现** | 编排器可以在运行时查询 Agent 卡注册表，找到最适合特定子任务的专家。 |
| **流式传输与推送通知** | A2A 支持服务器发送事件（SSE）用于实时进度更新，以及长时间运行任务的推送通知。 |

我们上面构建的工作流是该模式的简化进程内版本。在实际
部署中，每个 Agent 都会暴露 HTTP 端点，发布 Agent 卡，并通过
A2A JSON-RPC 协议进行通信。

## Summary

In this lesson you learned:

1. **What the A2A protocol is** — an open standard for agent-to-agent discovery, messaging,
   and task management.
2. **How to create specialized agents** — a Currency Exchange agent, an Activity Planner agent,
   and a Travel Manager orchestrator.
3. **How to wire agents into a workflow** — using `WorkflowBuilder` to model sequential
   message passing between agents.
4. **How A2A works in production** — enabling cross-framework, cross-service collaboration
   with dynamic discovery and streaming updates.


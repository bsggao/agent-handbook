---
title: "12 · 12-chat_summarization"
outline: [2, 3]
---

# 12 · 12-chat_summarization

[返回：上下文工程](/lessons/context.md) · [不可变原始文件](https://github.com/microsoft/ai-agents-for-beginners/blob/25b7985f3b2dc37a84f4a7387ccd3c9f0e5b1595/12-context-engineering/code_samples/12-chat_summarization.ipynb)

::: warning 原课程完整 Notebook · 静态阅读与代码解析
代码按英文源文件顺序保留，中文说明以同版本译本为基础。原始安装单元格可能含无版本上限的 `-U`；请跳过它们，先按[准备篇](/lessons/setup.md)固定依赖。云端服务、模型权限、网站布局和部分 SDK 接口需在你自己的环境验证。本站没有执行云端请求；第 18 章的离线验证状态单独记录在[检查报告](/guide/verification.md)。
:::

## 运行准备

Python 3.12+；在独立虚拟环境安装源仓库依赖与本页中声明的额外依赖。原文件路径：`upstream/12-context-engineering/code_samples/12-chat_summarization.ipynb`。以原仓库根目录为工作目录，在 Jupyter 中按顺序执行；身份与环境变量见准备篇。

```bash
cd upstream
python -m jupyterlab
```

[下载原始 Notebook](/notebooks/12-context-engineering/code_samples/12-chat_summarization.ipynb)。输出为上游文件保存的历史结果，不能用作本站实测证明。

## 第12课 - 使用 Agent 备忘录减少聊天历史

本笔记本演示了如何使用Microsoft Agent Framework管理长对话中的上下文。随着对话增长，Token数量增加——最终超出模型的上下文窗口。我们通过 **上下文摘要模式** 和用于持久记忆的 **Agent 备忘录** 来解决这个问题。

## 你将学到：
1. **为什么上下文管理重要** ：理解Token限制和上下文窗口
2. **上下文感知 Agent** ：构建能管理自身对话上下文的 Agent
3. **上下文摘要模式** ：使用工具精简对话历史
4. **Agent 备忘录** ：在上下文缩减中依然持久的记忆

## 前置条件：
- 配置好环境变量的 Azure OpenAI 设置
- 对之前课程中基本 Agent 概念的理解

## 安装

### 代码单元格 3

阅读提示：跟踪本单元格读取的变量、修改的状态以及返回值。按原顺序执行，确认依赖的前序变量已经存在。

```text
%pip install agent-framework azure-ai-projects azure-identity python-dotenv --quiet
```

### 代码单元格 4

模型连接：project_endpoint 是项目地址，model 是实际部署名称；credential 提供访问身份。客户端创建本身不证明已经部署服务端 Agent。

```python
import os
import asyncio
import dotenv
from datetime import datetime
from pathlib import Path

from agent_framework import tool
from agent_framework.foundry import FoundryChatClient
from azure.identity import DefaultAzureCredential
```

### 代码单元格 5

配置加载：从本地环境读取端点与部署名；缺少变量时先修复配置，不要把密钥写进代码。

模型连接：project_endpoint 是项目地址，model 是实际部署名称；credential 提供访问身份。客户端创建本身不证明已经部署服务端 Agent。

输出观察：print 展示应用可观察结果；预存输出和现场结果可能不同，它不是模型内部思考记录。

```python
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

print("Microsoft Foundry client configured")
```

## 为什么上下文管理很重要

每个大语言模型 (LLM) 都有一个有限的 **上下文窗口** ——即它在一次请求中能够处理的最大Token数量。随着多轮对话的进行：

- **Token数量随着每条用户消息和助手回复线性增长** 。
- **提示Token主导成本** ，因为整个历史每轮都会被重新发送。
- 最终对话 **会超出上下文窗口** ，模型要么截断对话，要么报错。

### 管理上下文的策略

| 策略 | 工作原理 | 权衡 |
|---|---|---|
| **截断** | 删除最早的消息 | 失去早期的上下文 |
| **总结** | 将较旧的消息压缩成摘要 | 细节会丢失，但保留关键点 |
| **草稿板 / 外部记忆** | 将关键信息存储在对话外部 | 需要调用工具，但能够保存任何信息减少 |

在本笔记本中，我们将 **总结** 与 **草稿板工具** 结合，使 Agent 即使在对话历史被压缩时也能保持连续性。

## 创建一个上下文感知 Agent

### 代码单元格 8

行为约束：instructions 引导模型，不能替代执行器的权限验证、次数限制和结果检查。

输出观察：print 展示应用可观察结果；预存输出和现场结果可能不同，它不是模型内部思考记录。

```python
agent = client.as_agent(
    name="ContextAwareAgent",
    instructions="""You are a helpful travel planning assistant with excellent memory management.
When conversations get long:
1. Summarize previous context into key points
2. Track user preferences mentioned earlier
3. Reference previous decisions without repeating full details
Always maintain continuity while being concise.""",
)

print("Context-aware travel planning agent created")
```

## 模拟一次长对话

让我们通过一次多轮对话来看看上下文是如何积累的。Agent 应该在多轮对话中保留关键细节（偏好、预算、旅行日期）并展示连贯性。

### 代码单元格 10

会话状态：复用同一个 session 才会带上历史；新建会话与持久化存储是不同操作。

输出观察：print 展示应用可观察结果；预存输出和现场结果可能不同，它不是模型内部思考记录。

```python
session = agent.create_session()

# Turn 1 - Initial preferences
response = await agent.run("I'm planning a trip to Japan. I love sushi, temples, and photography.", session=session)
print(f"Turn 1: {response}\n")

# Turn 2 - More details
response = await agent.run("My budget is $3000 and I'll be traveling solo for 10 days in April.", session=session)
print(f"Turn 2: {response}\n")

# Turn 3 - Test context retention
response = await agent.run("Based on everything I've told you so far, what's the one thing you'd recommend I not miss?", session=session)
print(f"Turn 3: {response}\n")
```

注意 Agent 如何保留早期对话的上下文——它知道关于日本、寿司、寺庙、摄影、3000美元预算、独自旅行和四月的时间范围。在短时间对话中这效果很好，但随着对话的增长，重新发送全部历史变得昂贵。

让我们继续对话更多回合，看看上下文的积累：

### 代码单元格 12

输出观察：print 展示应用可观察结果；预存输出和现场结果可能不同，它不是模型内部思考记录。

```python
# Turn 4 - Expand the conversation
response = await agent.run("What about accommodation? I prefer traditional Japanese inns.", session=session)
print(f"Turn 4: {response}\n")

# Turn 5 - Change of plans
response = await agent.run("Actually, I've changed my mind about the dates. I'll go in October instead for the autumn colors.", session=session)
print(f"Turn 5: {response}\n")

# Turn 6 - Test retention after change
response = await agent.run("Summarize my complete travel plan so far — destination, budget, duration, interests, accommodation, and timing.", session=session)
print(f"Turn 6: {response}\n")
```

## 上下文总结模式

随着对话的发展，我们可以使用 **总结工具** 将累积的上下文浓缩成简洁的格式。Agent 调用此工具记录关键偏好，以便即使较早的消息被删除，重要信息仍能被保留。

该模式是更复杂历史缩减的构建模块：
1. Agent 识别对话中的关键事实
2. 它调用总结工具以持久化这些信息
3. 由于总结捕捉了重要内容，较早的消息可以安全删除

下面我们定义一个 `summarize_preferences` 工具，Agent 可以调用它来记录其所学内容的简洁摘要。

### 代码单元格 14

工具定义：类型注解和文档字符串描述输入、用途；模型产生调用请求，框架在应用进程中执行函数。检查是否需要人工批准。

行为约束：instructions 引导模型，不能替代执行器的权限验证、次数限制和结果检查。

输出观察：print 展示应用可观察结果；预存输出和现场结果可能不同，它不是模型内部思考记录。

```python
@tool(approval_mode="never_require")
def summarize_preferences(conversation_notes: str) -> str:
    """Summarize accumulated user preferences into a compact format."""
    return f"[SUMMARY] User preferences recorded: {conversation_notes}"


# Create an enhanced agent with the summarization tool
summarizing_agent = client.as_agent(
    name="SummarizingTravelAgent",
    instructions="""You are a helpful travel planning assistant that actively manages conversation context.

CONTEXT MANAGEMENT RULES:
1. After gathering several user preferences, call summarize_preferences() to record a compact summary
2. When the user asks you to recall details, reference your recorded summaries
3. Keep responses concise — avoid restating the entire history

PLANNING PROCESS:
1. Gather user preferences (destination, budget, dates, interests)
2. Summarize preferences using the tool
3. Create recommendations based on the summary
4. Update the summary when preferences change""",
    tools=[summarize_preferences],
)

print("Summarizing travel agent created with context tools")
```

### 代码单元格 15

会话状态：复用同一个 session 才会带上历史；新建会话与持久化存储是不同操作。

输出观察：print 展示应用可观察结果；预存输出和现场结果可能不同，它不是模型内部思考记录。

```python
# Demonstrate the summarization pattern
summary_session = summarizing_agent.create_session()

# Provide a batch of preferences
response = await summarizing_agent.run(
    "I want to visit Greece. I love seafood, history, and island hopping. "
    "Budget is $4000 for two weeks. Traveling with my partner in June. "
    "Please record these preferences using your summarization tool.",
    session=summary_session,
)
print(f"Agent: {response}\n")

# Ask the agent to use the recorded context
response = await summarizing_agent.run(
    "Now, based on what you've recorded, suggest the top 3 islands we should visit.",
    session=summary_session,
)
print(f"Agent: {response}\n")
```

## 总结

在本课中，你学习了如何使用 Microsoft Agent Framework 管理长期运行 Agent 对话中的上下文：

### 关键概念
- **上下文窗口是有限的** — 对话历史中的每个Token都需要付费并计入限制。
- **摘要工具** 使 Agent 能够将累积的上下文浓缩为简明的摘要，减少Token使用量，同时保留关键信息。
- **Agent 速记板** 提供了持久的外部记忆，能保存任何对话缩减操作中遗失的内容。

### 你构建的内容
- 一个 **上下文感知 Agent** ，能在多轮对话中维持连续性
- 一个 **摘要工具** （`summarize_preferences`），以简洁格式记录关键用户细节
- 一个 **多轮对话演示** ，展示上下文保留与变更处理

### 现实应用
- **客服机器人** ：在长时间支持会话中记住偏好
- **个人助理** ：跟踪进行中的项目，无需重复说明上下文
- **教育导师** ：在多次互动中保持学生进度

### 后续步骤
- 实现一个带文件持久化的完整速记板工具
- 在摘要后添加自动历史截断功能
- 结合向量数据库实现语义记忆搜索
- 构建能够在数天后恢复对话并保持完整上下文的 Agent


---
title: "探索 Agent 框架"
description: "理解框架负责什么，以及如何选择。"
course: "frameworks"
prev: {"text": "AI Agent 入门与应用场景", "link": "/lessons/introduction"}
next: {"text": "Agent 设计模式", "link": "/lessons/design-patterns"}
---

# 探索 Agent 框架

::: tip 本章目标
分清模型客户端、Agent 框架和托管服务；理解工具注册、会话与多角色编排分别解决什么问题。
:::

前置：[Agent 入门](./introduction.md)。框架（Framework）是组织应用代码的约定和组件，不是另一种大模型。

## 补充讲解：谁负责哪一层

假设旅行社原来有一个查询空位的 Python 函数。你想让用户自然地说“还有温暖的目的地吗”，还希望第二句“换一个”能理解上文。单次模型 API 只解决生成输出；工具说明转换、调用结果回传、会话历史和执行事件还需要应用处理。Agent 框架把这些重复工作组织起来。

可以把 SDK 看作你在厨房使用的器具，把托管服务看作有人维护水电和设备的厨房。这个类比只说明责任分工：使用框架不必然使用云，使用云也不自动保证业务安全。

| 层次 | 主要职责 | 本课对应 |
| --- | --- | --- |
| 模型客户端 | 地址、身份、请求和响应格式 | FoundryChatClient / OpenAIChatClient |
| Agent 框架 | 指令、工具调用循环、会话、工作流 | Microsoft Agent Framework |
| 托管平台 | 部署、版本、运行环境与平台治理 | Microsoft Foundry Agent Service |
| 业务应用 | 用户权限、订单规则、预算、结果验收 | 由你编写并测试 |

原文会介绍模块化、协作与反馈循环。这里的“学习”通常是保存反馈、调整提示或更新检索信息，不是 SDK 自动训练了模型权重。


::: info 原课程代码片段的阅读范围
下方精读保留上游主要知识与片段，可能包含历史 SDK 写法、示意端点及未完整定义的函数；这些片段不等同于经过本站验证的完整程序。运行前优先阅读本章实际 Notebook 导读与版本校订。已验证的无 API 实验在“扩展实践”中另行标明。
:::

[原课程视频：探索AI Agent 框架](https://youtu.be/ODwF-EZo_O8?si=1xoy_B9RNQfrYdF7)


## 原课程精读：探索AI Agent 框架

AI Agent 框架是为简化AI Agent 的创建、部署和管理而设计的软件平台。这些框架为开发者提供了预构建的组件、抽象和工具，简化了复杂AI系统的开发过程。

这些框架通过为AI Agent 开发中常见的挑战提供标准化的方法，帮助开发者专注于应用的独特方面。它们提升了构建AI系统的可扩展性、可访问性和效率。

## 介绍

本课将涵盖：

- 什么是AI Agent 框架，它们能让开发者实现什么？
- 团队如何利用它们快速原型设计、迭代并提升 Agent 能力？
- 微软创建的框架和工具（[Microsoft Foundry Agent Service](https://aka.ms/ai-agents-beginners/ai-agent-service)和[Microsoft Agent Framework](https://learn.microsoft.com/azure/ai-services/openai/how-to/responses)）有什么区别？
- 我能否直接集成现有Azure生态工具，还是必须使用独立解决方案？
- 什么是Microsoft Foundry Agent Service？它如何帮助我？

## 学习目标

本课的目标是帮助你理解：

- AI Agent 框架在AI开发中的作用。
- 如何利用AI Agent 框架构建智能 Agent。
- AI Agent 框架支持的关键能力。
- Microsoft Agent Framework与Microsoft Foundry Agent Service的区别。

## 什么是AI Agent 框架，它们能实现什么？

传统AI框架可以帮助你将AI集成到应用中，并提升应用的性能，具体体现在以下方面：

- **个性化** ：AI可以分析用户行为和偏好，提供个性化推荐、内容和体验。
例如：Netflix等流媒体服务使用AI根据观看历史推荐电影和节目，提升用户参与度和满意度。
- **自动化和效率** ：AI可以自动执行重复任务、简化工作流程，提高运营效率。
例如：客户服务应用利用AI驱动的聊天机器人处理常见咨询，缩短响应时间并让人工客服专注于更复杂问题。
- **增强用户体验** ：AI通过语音识别、自然语言处理和预测文本等智能功能改善整体用户体验。
例如：Siri和Google Assistant等虚拟助手使用AI理解并响应语音命令，方便用户与设备交互。

### 听起来很不错，为什么我们还需要AI Agent 框架？

AI Agent 框架不仅仅是AI框架。它们旨在支持智能 Agent 的创建，这些 Agent 可以与用户、其他 Agent 及环境互动以实现特定目标。这些 Agent 能表现出自主行为，做出决策，并适应变化的条件。下面介绍AI Agent 框架支持的一些关键能力：

- **Agent 协作与协调** ：支持创建多个AI Agent，它们能够协同工作、交流和协调解决复杂任务。
- **任务自动化和管理** ：提供自动化多步骤工作流、任务委派和动态任务管理的机制。
- **上下文理解和适应** ：赋予 Agent 理解上下文、适应变化环境且基于实时信息做决策的能力。

总结来说，Agent 让你能够做更多事情，将自动化提升到新高度，构建能够适应和学习其环境的更智能系统。

## 如何快速原型设计、迭代和提升 Agent 能力？

这是一个快速发展的领域，但大多数AI Agent 框架都有一些共通点，可帮助你快速原型设计和迭代，主要包括模块化组件、协作工具和实时学习。让我们深入了解：

- **使用模块化组件** ：AI SDK提供预构建组件，如AI和记忆连接器、自然语言或代码插件调用功能、提示模板等。
- **利用协作工具** ：设计具备特定角色和任务的 Agent，使它们能够测试和优化协作工作流。
- **实时学习** ：实现反馈循环，Agent 从交互中学习并动态调整行为。

### 使用模块化组件

微软 Agent Framework等SDK提供预构建组件，如AI连接器、工具定义和 Agent 管理。

 **团队如何使用** ：团队可以快速组装这些组件创建功能性原型，无需从零开始构建，支持快速实验与迭代。

 **实际应用** ：你可以使用预构建的解析器提取用户输入中的信息，利用内存模块存储和检索数据，并使用提示生成器与用户交互，均不需从头搭建这些组件。

 **示例代码** 。来看一个示例，说明如何使用`FoundryChatClient`的Microsoft Agent Framework，使模型通过工具调用响应用户输入：

``` python
# Microsoft Agent Framework Python Example

import asyncio
import os

from agent_framework import tool
from agent_framework.foundry import FoundryChatClient
from azure.identity import AzureCliCredential


# Define a sample tool function to book travel
@tool(approval_mode="never_require")
def book_flight(date: str, location: str) -> str:
    """Book travel given location and date."""
    return f"Travel was booked to {location} on {date}"


async def main():
    provider = FoundryChatClient(
        project_endpoint=os.environ["AZURE_AI_PROJECT_ENDPOINT"],
        model=os.environ["AZURE_AI_MODEL_DEPLOYMENT_NAME"],
        credential=AzureCliCredential(),
    )
    agent = provider.as_agent(
        name="travel_agent",
        instructions="Help the user book travel. Use the book_flight tool when ready.",
        tools=[book_flight],
    )

    response = await agent.run("I'd like to go to New York on January 1, 2025")
    print(response)
    # Example output: Your flight to New York on January 1, 2025, has been successfully booked. Safe travels! ✈️🗽


if __name__ == "__main__":
    asyncio.run(main())
```

从该示例中你可以看到，如何利用预构建解析器提取用户输入中的关键信息，如航班预订请求的起点、终点和日期。这种模块化方法让你专注于高层逻辑。

### 利用协作工具

微软 Agent Framework等框架便于创建多个可协同工作的 Agent。

 **团队如何使用** ：团队可以设计具备特定角色和任务的 Agent，测试和优化协同工作流，提高整体系统效率。

 **实际应用** ：你可以创建一个 Agent 团队，每个 Agent 专注于数据检索、分析或决策等特定功能。Agent 间可以通讯共享信息，实现共同目标，如回答用户查询或完成任务。

 **示例代码（微软 Agent Framework）** ：

```python
# Creating multiple agents that work together using the Microsoft Agent Framework

import os
from agent_framework.foundry import FoundryChatClient
from azure.identity import AzureCliCredential

provider = FoundryChatClient(
    project_endpoint=os.environ["AZURE_AI_PROJECT_ENDPOINT"],
    model=os.environ["AZURE_AI_MODEL_DEPLOYMENT_NAME"],
    credential=AzureCliCredential(),
)

# Data Retrieval Agent
agent_retrieve = provider.as_agent(
    name="dataretrieval",
    instructions="Retrieve relevant data using available tools.",
    tools=[retrieve_tool],
)

# Data Analysis Agent
agent_analyze = provider.as_agent(
    name="dataanalysis",
    instructions="Analyze the retrieved data and provide insights.",
    tools=[analyze_tool],
)

# Run agents in sequence on a task
retrieval_result = await agent_retrieve.run("Retrieve sales data for Q4")
analysis_result = await agent_analyze.run(f"Analyze this data: {retrieval_result}")
print(analysis_result)
```

该代码示例展示了如何创建涉及多个 Agent 协作分析数据的任务。每个 Agent 执行特定功能，任务通过协调 Agent 完成预期结果。通过创建具备专职角色的 Agent，提升任务效率和性能。

### 实时学习

先进框架支持实时上下文理解与适应能力。

 **团队如何使用** ：团队可以实现反馈循环，让 Agent 从交互中学习，动态调整行为，从而持续改进和完善能力。

 **实际应用** ：Agent 可分析用户反馈、环境数据及任务结果，不断更新知识库，调整决策算法，提高性能。该迭代学习流程使 Agent 适应环境变化和用户偏好，增强整体系统效能。

## Microsoft Agent Framework与Microsoft Foundry Agent Service有什么区别？

这里有许多对比方式，下面重点介绍它们在设计、能力和目标用例上的关键差异：

## Microsoft Agent Framework (MAF)

Microsoft Agent Framework提供了一个简化的SDK，通过`FoundryChatClient`构建AI Agent。它支持利用Azure OpenAI模型的内置工具调用、对话管理和通过Azure身份实现企业级安全。

 **用例** ：构建具备工具使用、多步骤工作流及企业集成场景的生产级AI Agent。

Microsoft Agent Framework的几个重要核心概念：

- **Agent（Agents）** 。Agent 通过`FoundryChatClient`创建，配置名称、指令和工具。Agent 可以：
  - **处理用户消息** ，并使用Azure OpenAI模型生成响应。
  - **根据对话上下文自动调用工具** 。
  - **维护跨多次交互的会话状态** 。

  下面是创建 Agent 的代码片段：

    ```python
    import os
    from agent_framework.foundry import FoundryChatClient
    from azure.identity import AzureCliCredential

    provider = FoundryChatClient(
        project_endpoint=os.environ["AZURE_AI_PROJECT_ENDPOINT"],
        model=os.environ["AZURE_AI_MODEL_DEPLOYMENT_NAME"],
        credential=AzureCliCredential(),
    )
    agent = provider.as_agent(
        name="my_agent",
        instructions="You are a helpful assistant.",
    )

    response = await agent.run("Hello, World!")
    print(response)
    ```

- **工具（Tools）** 。框架支持以Python函数定义工具，Agent 可自动调用。工具在创建 Agent 时注册：

    ```python
    def get_weather(location: str) -> str:
        """Get the current weather for a location."""
        return f"The weather in {location} is sunny, 72\u00b0F."

    agent = provider.as_agent(
        name="weather_agent",
        instructions="Help users check the weather.",
        tools=[get_weather],
    )
    ```

- **多 Agent 协调** 。可以创建多名专精不同领域的 Agent，并协调它们的工作：

    ```python
    planner = provider.as_agent(
        name="planner",
        instructions="Break down complex tasks into steps.",
    )

    executor = provider.as_agent(
        name="executor",
        instructions="Execute the planned steps using available tools.",
        tools=[execute_tool],
    )

    plan = await planner.run("Plan a trip to Paris")
    result = await executor.run(f"Execute this plan: {plan}")
    ```

- **Azure身份集成** 。框架使用`AzureCliCredential`（或`DefaultAzureCredential`）实现安全的无密钥认证，免除直接管理API密钥的需求。

## Microsoft Foundry Agent Service

Microsoft Foundry Agent Service是微软在Ignite 2024上推出的较新服务。它支持更灵活的模型，如直接调用开源大语言模型（LLM）Llama 3、Mistral和Cohere，实现AI Agent 的开发和部署。

Microsoft Foundry Agent Service提供更强的企业安全机制和数据存储方案，适合企业级应用。

它可以无缝与Microsoft Agent Framework协作，共同构建和部署 Agent。

该服务目前处于公开预览阶段，支持Python和C#构建 Agent。

使用Microsoft Foundry Agent Service Python SDK，可以创建带有用户定义工具的 Agent：

```python
import asyncio
from azure.identity import DefaultAzureCredential
from azure.ai.projects import AIProjectClient

# Define tool functions
def get_specials() -> str:
    """Provides a list of specials from the menu."""
    return """
    Special Soup: Clam Chowder
    Special Salad: Cobb Salad
    Special Drink: Chai Tea
    """

def get_item_price(menu_item: str) -> str:
    """Provides the price of the requested menu item."""
    return "$9.99"


async def main() -> None:
    credential = DefaultAzureCredential()
    project_client = AIProjectClient.from_connection_string(
        credential=credential,
        conn_str="your-connection-string",
    )

    agent = project_client.agents.create_agent(
        model="gpt-5-mini",
        name="Host",
        instructions="Answer questions about the menu.",
        tools=[get_specials, get_item_price],
    )

    thread = project_client.agents.create_thread()

    user_inputs = [
        "Hello",
        "What is the special soup?",
        "How much does that cost?",
        "Thank you",
    ]

    for user_input in user_inputs:
        print(f"# User: '{user_input}'")
        message = project_client.agents.create_message(
            thread_id=thread.id,
            role="user",
            content=user_input,
        )
        run = project_client.agents.create_and_process_run(
            thread_id=thread.id, agent_id=agent.id
        )
        messages = project_client.agents.list_messages(thread_id=thread.id)
        print(f"# Agent: {messages.data[0].content[0].text.value}")


if __name__ == "__main__":
    asyncio.run(main())
```

### 核心概念

Microsoft Foundry Agent Service包括以下核心概念：

- **Agent（Agent）** 。Microsoft Foundry Agent Service集成于Microsoft Foundry。在Foundry中，AI Agent 作为“智能”微服务，用于回答问题（RAG）、执行操作或完全自动化工作流程。它通过结合生成式AI模型能力与访问和交互真实数据源的工具实现功能。下面是一个 Agent 示例：

    ```python
    agent = project_client.agents.create_agent(
        model="gpt-5-mini",
        name="my-agent",
        instructions="You are helpful agent",
        tools=code_interpreter.definitions,
        tool_resources=code_interpreter.resources,
    )
    ```

    在该示例中，Agent 创建时使用模型`gpt-5-mini`，名称为`my-agent`，指令为`You are helpful agent`。该 Agent 配备工具和资源以执行代码解读任务。

- **线程和消息（Thread and messages）** 。线程是另一个重要概念。它代表 Agent 与用户之间的对话或交互。线程用于跟踪对话进展，存储上下文信息及管理交互状态。示例代码如下：

    ```python
    thread = project_client.agents.create_thread()
    message = project_client.agents.create_message(
        thread_id=thread.id,
        role="user",
        content="Could you please create a bar chart for the operating profit using the following data and provide the file to me? Company A: $1.2 million, Company B: $2.5 million, Company C: $3.0 million, Company D: $1.8 million",
    )
    
    # Ask the agent to perform work on the thread
    run = project_client.agents.create_and_process_run(thread_id=thread.id, agent_id=agent.id)
    
    # Fetch and log all messages to see the agent's response
    messages = project_client.agents.list_messages(thread_id=thread.id)
    print(f"Messages: {messages}")
    ```

    在上述代码中，创建了一个线程。随后向线程发送消息。调用`create_and_process_run`后，请求 Agent 在该线程上执行工作。最后获取消息并记录日志，查看 Agent 的响应。消息显示了用户和 Agent 之间对话的进展。还需了解消息类型可能包括文本、图片或文件，即 Agent 的工作成果可能是图片或文本响应。作为开发者，你可以利用这些信息进一步处理响应或呈现给用户。

- **与Microsoft Agent Framework集成** 。Microsoft Foundry Agent Service与Microsoft Agent Framework无缝协作，意味着你可以使用`FoundryChatClient`构建 Agent，并通过 Agent Service进行生产环境部署。

 **用例** ：Microsoft Foundry Agent Service设计用于需要安全、可扩展和灵活AI Agent 部署的企业应用。

## 这些方法有何区别？
 
看起来确实有重叠，但在设计、能力和目标用例上存在关键区别：
 
- **Microsoft Agent Framework (MAF)** ：是构建AI Agent 的生产级SDK，提供简洁API，支持工具调用、会话管理和Azure身份集成。
- **Microsoft Foundry Agent Service** ：是微软Foundry中的 Agent 平台和部署服务，内建对Azure OpenAI、Azure AI搜索、Bing搜索和代码执行的连接。
 
仍然不确定选择哪个？

### 用例
 
让我们通过一些常见用例帮你理清：
 
> 问：我想快速开始构建生产级AI Agent 应用
>

>答：Microsoft Agent Framework是不错的选择。它通过`FoundryChatClient`提供了简单的Python风格API，仅需几行代码即可定义带工具和指令的 Agent。

>问：我需要具备Azure搜索和代码执行等集成的企业级部署
>
> 答：Microsoft Foundry Agent Service最合适。该服务平台支持多种模型，集成Azure AI搜索、Bing搜索和Azure功能，实现支持Foundry Portal中构建 Agent 并大规模部署。
 
> 问：我还是有点糊涂，给我一个推荐
>
> 答：先用Microsoft Agent Framework构建 Agent，当需要生产环境部署和扩展时，再使用Microsoft Foundry Agent Service。此方法既能快速迭代 Agent 逻辑，也提供清晰的企业部署路径。
 
让我们用表格总结主要差异：

| 框架 | 重点 | 核心概念 | 用例 |
| --- | --- | --- | --- |
| Microsoft Agent Framework | 简化的 AgentSDK，支持工具调用 | Agent、工具、Azure身份 | 构建AI Agent、工具使用、多步骤工作流 |
| Microsoft Foundry Agent Service | 灵活模型，企业安全，代码生成，工具调用 | 模块化、协作、流程编排 | 安全、可扩展且灵活的AI Agent 部署 |

## 我能否直接集成现有Azure生态工具，还是必须使用独立解决方案？


答案是肯定的，你可以将现有的 Azure 生态系统工具直接集成到 Microsoft Foundry Agent Service，特别是因为它已被设计为与其他 Azure 服务无缝协作。例如，你可以集成 Bing、Azure AI Search 和 Azure Functions。Microsoft Foundry 也有深度集成。

Microsoft Agent Framework 还通过 `FoundryChatClient` 和 Azure 身份集成了 Azure 服务，允许你直接从 Agent 工具调用 Azure 服务。

## 示例代码

- Python: [Agent Framework (Microsoft Foundry)](/labs/02-explore-agentic-frameworks-code-samples-02-python-agent-framework-notebook.md)
- Python: [Agent Framework (Azure OpenAI Responses API)](/labs/02-explore-agentic-frameworks-code-samples-02-python-agent-framework-azure-openai-notebook.md)
- .NET: [Agent Framework](/labs/02-explore-agentic-frameworks-code-samples-02-dotnet-agent-framework-notes.md)

## 参考资料

- [Azure Agent Service](https://techcommunity.microsoft.com/blog/azure-ai-services-blog/introducing-azure-ai-agent-service/4298357)
- [Microsoft Agent Framework - Azure OpenAI Responses](https://learn.microsoft.com/azure/ai-services/openai/how-to/responses)
- [Microsoft Foundry Agent Service](https://learn.microsoft.com/azure/ai-services/agents/overview)

## 代码实操：两个客户端，同一个业务工具

本章保留 Foundry 与 Azure OpenAI 两个 Python Notebook，均见下方完整代码阅读页。先按[准备篇](./setup.md)建环境，Foundry 版填写项目变量，Azure OpenAI 版填写资源端点和部署变量，再从 `upstream/` 启动 Jupyter；不要把两类端点混用。需要模型权限并可能计费，本站未执行云端调用。

Foundry 例子的 `check_destination_availability(destination)` 读取本地字典。`Annotated[str, "..."]` 同时表达 Python 类型与给模型看的参数说明。`provider.as_agent(tools=[...])` 注册函数后，模型才知道它可用。第一次和第二次 `agent.run(..., session=session)` 复用会话，因此第二次能接上偏好。

Azure OpenAI 例子增加 `get_random_destination()`，用 `_last_destination` 避免连续重复。这个模块级变量只是单进程演示；若做多用户服务，要把它移到用户会话中，否则不同用户会相互影响。

 **预期验收：** 工具返回已定义的目的地状态；后续消息沿用同一会话。看到自然语言回答不代表工具必然调用，应检查工具事件。`--stage 2` 的[本地综合练习](/guide/project.md)可先验证执行器的分工。

## 常见错误与选择边界

| 现象 | 原因 | 修复 |
| --- | --- | --- |
| 换一个目的地后仍重复询问全部偏好 | 每轮新建了 session | 在同一对话复用 session，跨用户隔离 |
| 构造客户端成功，却无云端 Agent 资源 | 把客户端初始化等同于部署 | 明确直接模型推理和服务端托管资源的不同生命周期 |
| 最新文档复制代码后导入失败 | SDK 主次版本不匹配 | 核对 1.10 依赖和导入路径，按整套 API 迁移 |

框架适合反复组合工具、状态和编排的应用；简单的单次生成未必需要完整框架。即使采用框架，也应能说明循环何时停止、工具在哪里执行、谁验证输出。

## 自测与扩展实践

为“用户拒绝刚才的目的地”增加状态：既保存拒绝列表，又保留预算。把状态放在哪一层？

::: details 参考答案与实现思路
放在当前用户的会话或业务状态中。用 `rejected: set[str]` 保存拒绝项，每次候选为 `[d for d in destinations if d not in rejected]`；空列表时询问是否扩大范围。不能用全局变量把甲的拒绝应用到乙。预算是另一字段，拒绝目的地不应自动清空预算。
:::

本章的判断方法是先列责任，再选工具。下一章进一步讨论人的控制权、透明度与一致性如何落实到 Agent 体验中。


## 原课程代码与补充材料

以下是本章实际源文件对应的阅读页。Notebook 已分解为说明、代码及原文件输出；云端示例未进行联网端到端验证。正文中的片段用于解释，运行时使用完整 Notebook 和准备篇的固定依赖。

- [azure-ai-foundry-agent-creation.md](/labs/02-explore-agentic-frameworks-azure-ai-foundry-agent-creation-notes.md)
- [02-dotnet-agent-framework.cs](/labs/02-explore-agentic-frameworks-code-samples-02-dotnet-agent-framework-csharp.md)
- [02-python-agent-framework-azure-openai.ipynb](/labs/02-explore-agentic-frameworks-code-samples-02-python-agent-framework-azure-openai-notebook.md)
- [02-python-agent-framework.ipynb](/labs/02-explore-agentic-frameworks-code-samples-02-python-agent-framework-notebook.md)
- [02-dotnet-agent-framework.md](/labs/02-explore-agentic-frameworks-code-samples-02-dotnet-agent-framework-notes.md)

## 本章来源

基于 [英文原文](https://github.com/microsoft/ai-agents-for-beginners/blob/25b7985f3b2dc37a84f4a7387ccd3c9f0e5b1595/02-explore-agentic-frameworks/README.md) 与 [简体中文翻译](https://github.com/microsoft/ai-agents-for-beginners/blob/25b7985f3b2dc37a84f4a7387ccd3c9f0e5b1595/translations/zh-CN/02-explore-agentic-frameworks/README.md) 整理，原作者为 Microsoft 与开源贡献者，采用 MIT 许可证。本页标明“补充讲解”与“扩展实践”的内容为本项目新增。

来源提交：`25b7985f3b2d` · 获取日期：2026-09-14。参见[版本校订记录](/guide/sources.md)。

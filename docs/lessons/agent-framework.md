---
title: "Microsoft Agent Framework"
description: "用工作流、交接与中间件组织应用。"
course: "agent-framework"
prev: {"text": "Agent 记忆", "link": "/lessons/memory"}
next: {"text": "Computer Use 与 Browser Use", "link": "/lessons/browser-use"}
---

# Microsoft Agent Framework

## 本章目标与前置知识（补充讲解）

建议先读[框架概览](./frameworks.md)、[多 Agent](./multi-agent.md)、[记忆](./memory.md)。本章把 Agent、会话、工具、工作流、中间件和托管联系起来，重点是能读懂原仓库的实际 Python 工作流。

想象费用助手先读收据、再核对政策、最后提交审批。单个 Agent 负责一段有边界的生成或工具任务；工作流规定节点、边和暂停/继续规则；中间件在调用前后增加统一行为。 **框架帮助连接这些组件，不替你决定正确的权限与业务状态。** 

::: warning 版本阅读提示
本仓库固定 `agent-framework-core==1.10.0`。README 部分片段仍使用 `ChatAgent`、`get_new_thread()`、`run_stream()` 等历史写法；同提交的新 Notebook 主要使用 `create_session()` 和 `run(..., stream=True)`。以下原课程片段按历史资料保留，实际运行优先选本章 Notebook 并固定依赖；不要混抄不同版本 API。详见[版本差异表](/guide/sources.md)。
:::


::: info 原课程代码片段的阅读范围
下方精读保留上游主要知识与片段，可能包含历史 SDK 写法、示意端点及未完整定义的函数；这些片段不等同于经过本站验证的完整程序。运行前优先阅读本章实际 Notebook 导读与版本校订。已验证的无 API 实验在“扩展实践”中另行标明。
:::

## 原课程精读：探索 Microsoft Agent Framework



### 介绍

本课将涵盖：

- 了解 Microsoft Agent Framework：关键特性和价值  
- 探索 Microsoft Agent Framework的核心概念
- 高级 MAF 模式：工作流、中间件和内存

## 学习目标

完成本课后，你将了解如何：

- 使用 Microsoft Agent Framework构建生产级 AI Agent
- 将 Microsoft Agent Framework的核心功能应用于你的 Agent 使用场景
- 使用包括工作流、中间件和可观测性在内的高级模式

## 代码示例 

有关 [Microsoft Agent Framework (MAF)](https://aka.ms/ai-agents-beginners/agent-framework) 的代码示例可以在本仓库的 `xx-python-agent-framework` 和 `xx-dotnet-agent-framework` 文件中找到。

## 了解 Microsoft Agent Framework

![Framework Intro](/upstream-assets/translated_images/zh-CN/framework-intro.077af16617cf130c.webp)

*图：Framework Intro。来源：Microsoft AI Agents for Beginners，MIT。*

[Microsoft Agent Framework (MAF)](https://aka.ms/ai-agents-beginners/agent-framework) 是微软用于构建 AI Agent 的统一框架。它提供了灵活性来应对生产和研究环境中各种 Agent 使用场景，包括：

- **顺序 Agent 编排** ：适用于需要逐步工作流的场景。
- **并发编排** ：适用于 Agent 需要同时完成任务的场景。
- **群聊编排** ：适用于 Agent 可以协同完成单个任务的场景。
- **交接编排** ：适用于 Agent 在完成子任务后相互交接任务的场景。
- **Magentic 编排** ：适用于主管 Agent 创建和修改任务列表，并协调子 Agent 完成任务的场景。

为了在生产中交付 AI Agent，MAF 还包含以下特性：

- **可观测性** ，通过使用 OpenTelemetry 追踪 AI Agent 的每一个动作，包括工具调用、编排步骤、推理流程以及通过 Microsoft Foundry 仪表板进行性能监控。
- **安全性** ，Agent 本地托管于 Microsoft Foundry，具有角色访问控制、私有数据处理和内置内容安全等安全控制。
- **持久性** ，Agent 线程和工作流可以暂停、恢复并从错误中恢复，从而支持更长时间的运行过程。
- **控制权** ，支持人机协同工作流，将任务标记为需人工审批。

Microsoft Agent Framework还注重互操作性，通过：

- **云无关性** — Agent 可以在容器、本地和多个不同云环境中运行。
- **提供商无关性** — Agent 可以通过你偏好的 SDK 创建，包括 Azure OpenAI 和 OpenAI。
- **集成开放标准** — Agent 可以使用如 Agent-to-Agent (A2A) 和 Model Context Protocol (MCP) 等协议发现并使用其他 Agent 和工具。
- **插件和连接器** — 可以连接到诸如 Microsoft Fabric、SharePoint、Pinecone 和 Qdrant 等数据和内存服务。

让我们看看这些特性是如何应用于 Microsoft Agent Framework的一些核心概念的。

## Microsoft Agent Framework核心概念

### Agent

![Agent Framework](/upstream-assets/translated_images/zh-CN/agent-components.410a06daf87b4fef.webp)

*图：Agent Framework。来源：Microsoft AI Agents for Beginners，MIT。*

 **创建 Agent** 

Agent 的创建是通过定义推理服务（LLM 提供者），
以及 AI Agent 需遵循的一组指令和分配的 `name` 来完成的：


```python
agent = AzureOpenAIChatClient(credential=AzureCliCredential()).create_agent( instructions="You are good at recommending trips to customers based on their preferences.", name="TripRecommender" )
```

上述示例使用了 `Azure OpenAI`，但 Agent 可以使用多种服务创建，包括 `Microsoft Foundry Agent Service`：

```python
AzureAIAgentClient(async_credential=credential).create_agent( name="HelperAgent", instructions="You are a helpful assistant." ) as agent
```

OpenAI `Responses`、`ChatCompletion` API

```python
agent = OpenAIResponsesClient().create_agent( name="WeatherBot", instructions="You are a helpful weather assistant.", )
```

```python
agent = OpenAIChatClient().create_agent( name="HelpfulAssistant", instructions="You are a helpful assistant.", )
```

或者使用 [MiniMax](https://platform.minimaxi.com/)，它提供了一个支持大上下文窗口（高达204K标记）的 OpenAI 兼容 API：

```python
agent = OpenAIChatClient(base_url="https://api.minimax.io/v1", api_key=os.environ["MINIMAX_API_KEY"], model_id="MiniMax-M3").create_agent( name="HelpfulAssistant", instructions="You are a helpful assistant.", )
```

或者使用基于 A2A 协议的远程 Agent：

```python
agent = A2AAgent( name=agent_card.name, description=agent_card.description, agent_card=agent_card, url="https://your-a2a-agent-host" )
```

 **运行 Agent** 

Agent 使用 `.run` 或 `.run_stream` 方法运行，分别用于非流式或流式响应。

```python
result = await agent.run("What are good places to visit in Amsterdam?")
print(result.text)
```

```python
async for update in agent.run_stream("What are the good places to visit in Amsterdam?"):
    if update.text:
        print(update.text, end="", flush=True)

```

每次 Agent 运行还可以包含选项，用以自定义 Agent 使用的参数，如 `max_tokens`，Agent 能够调用的 `tools`，甚至用于 Agent 的 `model` 本身。

这在需要特定模型或工具完成用户任务时非常有用。

 **工具** 

工具可以在定义 Agent 时指定：

```python
def get_attractions( location: Annotated[str, Field(description="The location to get the top tourist attractions for")], ) -> str: """Get the top tourist attractions for a given location.""" return f"The top attractions for {location} are." 


# When creating a ChatAgent directly 

agent = ChatAgent( chat_client=OpenAIChatClient(), instructions="You are a helpful assistant", tools=[get_attractions]

```

也可以在运行 Agent 时指定：

```python

result1 = await agent.run( "What's the best place to visit in Seattle?", tools=[get_attractions] # Tool provided for this run only )
```

 **Agent 线程** 

Agent 线程用于处理多轮对话。线程可以通过以下方式创建：

- 使用 `get_new_thread()`，使线程能被保存较长时间
- 在运行 Agent 时自动创建线程且线程只在当前运行期间存在

创建线程的代码如下：

```python
# Create a new thread. 
thread = agent.get_new_thread() # Run the agent with the thread. 
response = await agent.run("Hello, I am here to help you book travel. Where would you like to go?", thread=thread)

```

然后你可以序列化线程以便后续存储使用：

```python
# Create a new thread. 
thread = agent.get_new_thread() 

# Run the agent with the thread. 

response = await agent.run("Hello, how are you?", thread=thread) 

# Serialize the thread for storage. 

serialized_thread = await thread.serialize() 

# Deserialize the thread state after loading from storage. 

resumed_thread = await agent.deserialize_thread(serialized_thread)
```

 **Agent 中间件** 

Agent 通过与工具和大语言模型（LLM）交互完成用户任务。在某些场景中，我们希望执行或跟踪这些交互过程中的操作。Agent 中间件让我们能实现这一点，方式包括：

*函数中间件*

该中间件允许我们在 Agent 和它将调用的函数/工具之间执行操作。例如，当你想对函数调用进行日志记录时可以使用它。

在以下代码中，`next` 定义了是调用下一个中间件还是实际的函数。

```python
async def logging_function_middleware(
    context: FunctionInvocationContext,
    next: Callable[[FunctionInvocationContext], Awaitable[None]],
) -> None:
    """Function middleware that logs function execution."""
    # Pre-processing: Log before function execution
    print(f"[Function] Calling {context.function.name}")

    # Continue to next middleware or function execution
    await next(context)

    # Post-processing: Log after function execution
    print(f"[Function] {context.function.name} completed")
```

*聊天中间件*

该中间件允许我们在 Agent 和向大语言模型发送请求之间执行或记录操作。

这里包含重要信息，如发送给 AI 服务的 `messages`。

```python
async def logging_chat_middleware(
    context: ChatContext,
    next: Callable[[ChatContext], Awaitable[None]],
) -> None:
    """Chat middleware that logs AI interactions."""
    # Pre-processing: Log before AI call
    print(f"[Chat] Sending {len(context.messages)} messages to AI")

    # Continue to next middleware or AI service
    await next(context)

    # Post-processing: Log after AI response
    print("[Chat] AI response received")

```

 **Agent 记忆** 

如 `Agentic Memory` 课程中介绍的，记忆是使 Agent 能在不同上下文中操作的重要元素。MAF 提供了几种不同类型的记忆：

*内存存储*

这是应用程序运行期间在线程中存储的记忆。

```python
# Create a new thread. 
thread = agent.get_new_thread() # Run the agent with the thread. 
response = await agent.run("Hello, I am here to help you book travel. Where would you like to go?", thread=thread)
```

*持久消息*

此类记忆用于在不同会话间存储对话历史。它通过 `chat_message_store_factory` 定义：

```python
from agent_framework import ChatMessageStore

# Create a custom message store
def create_message_store():
    return ChatMessageStore()

agent = ChatAgent(
    chat_client=OpenAIChatClient(),
    instructions="You are a Travel assistant.",
    chat_message_store_factory=create_message_store
)

```

*动态记忆*

该记忆在 Agent 运行前被添加到上下文中。这些记忆可以存储于外部服务，例如 mem0：

```python
from agent_framework.mem0 import Mem0Provider

# Using Mem0 for advanced memory capabilities
memory_provider = Mem0Provider(
    api_key="your-mem0-api-key",
    user_id="user_123",
    application_id="my_app"
)

agent = ChatAgent(
    chat_client=OpenAIChatClient(),
    instructions="You are a helpful assistant with memory.",
    context_providers=memory_provider
)

```

 **Agent 可观测性** 


可观测性对于构建可靠且可维护的自主系统至关重要。MAF 集成了 OpenTelemetry，提供跟踪和计量以实现更好的可观测性。

```python
from agent_framework.observability import get_tracer, get_meter

tracer = get_tracer()
meter = get_meter()
with tracer.start_as_current_span("my_custom_span"):
    # do something
    pass
counter = meter.create_counter("my_custom_counter")
counter.add(1, {"key": "value"})
```

### 工作流

MAF 提供了预定义步骤以完成任务的工作流，并将 AI Agent 作为这些步骤中的组件。

工作流由不同组件组成，允许更好的控制流程。工作流还支持 **多 Agent 编排** 和 **检查点保存** 以保存工作流状态。

工作流的核心组件包括：

 **执行器** 

执行器接收输入消息，执行分配的任务，然后生成输出消息。这样推动工作流向完成更大任务前进。执行器可以是 AI Agent 或自定义逻辑。

 **边** 

边用于定义工作流中消息的流向。这些可以是：

*直接边* - 执行器之间的一对一简单连接：

```python
from agent_framework import WorkflowBuilder

builder = WorkflowBuilder()
builder.add_edge(source_executor, target_executor)
builder.set_start_executor(source_executor)
workflow = builder.build()
```

*条件边* - 在满足特定条件后激活。例如，当酒店房间不可用时，执行器可以建议其他选项。

*开关-条件边* - 根据定义的条件将消息路由到不同执行器。例如，如果旅客有优先访问权限，他们的任务将通过另一个工作流处理。

*分发边* - 将一条消息发送到多个目标。

*合并边* - 收集来自不同执行器的多条消息并发送给一个目标。

 **事件** 

为了提供对工作流更好的可观测性，MAF 提供了内置的执行事件，包括：

- `WorkflowStartedEvent`  - 工作流执行开始
- `WorkflowOutputEvent` - 工作流生成输出
- `WorkflowErrorEvent` - 工作流遇到错误
- `ExecutorInvokeEvent`  - 执行器开始处理
- `ExecutorCompleteEvent`  -  执行器处理完成
- `RequestInfoEvent` - 发出请求

## 高级 MAF 模式

上述章节涵盖了 Microsoft Agent Framework 的关键概念。随着你构建更复杂的 Agent，以下是一些值得考虑的高级模式：

- **中间件组合** ：使用函数和聊天中间件链式连接多个中间件处理器（日志记录、认证、限流），实现对 Agent 行为的细粒度控制。
- **工作流检查点** ：利用工作流事件和序列化保存并恢复长时间运行的 Agent 进程。
- **动态工具选择** ：结合基于工具描述的 RAG 和 MAF 的工具注册，仅展示与查询相关的工具。
- **多 Agent 交接** ：利用工作流边和条件路由协调专用 Agent 之间的交接。

## 在 Microsoft Foundry 上托管 LangChain / LangGraph Agent

Microsoft Agent Framework 是 **框架互操作的** — 你不必局限于使用 MAF 编写的 Agent。如果你已有使用 **LangChain** 或 **LangGraph** 构建的 Agent，可以将其作为 **Microsoft Foundry 托管 Agent** 运行，由 Foundry 管理运行时、会话、扩展、身份及协议端点，而你的 Agent 逻辑仍保持在 LangGraph 中。

这通过 `langchain_azure_ai.agents.hosting` 包来实现，该包暴露了一个编译好的 LangGraph 图，通过 Foundry 托管 Agent 使用的相同协议进行通信。

 **1. 安装 hosting 额外组件：** 

```bash
pip install -U "langchain-azure-ai[hosting]>=1.2.4" azure-identity
```

`hosting` 额外组件安装 Foundry 协议库：`azure-ai-agentserver-responses` （兼容 OpenAI 的 `/responses` 端点）和 `azure-ai-agentserver-invocations`（通用的 `/invocations` 端点）。

 **2. 选择托管协议：** 

| 协议 | 主机类 | 端点 | 使用场景 |
|----------|-----------|----------|----------|
| **Responses** | `ResponsesHostServer` | `/responses` | 需要兼容 OpenAI 的聊天、流式传输、响应历史和会话线程——这是对话 Agent 推荐的默认选项。 |
| **Invocations** | `InvocationsHostServer` | `/invocations` | 需要自定义 JSON 格式、Webhook 风格端点或非对话式处理。 |

因为 **Responses API 是 Foundry 中 Agent 开发的主要 API** ，大多数 Agent 建议从 `ResponsesHostServer` 开始。

 **3. 配置环境变量** （先执行 `az login` 使 `DefaultAzureCredential` 能认证）：

```bash
export FOUNDRY_PROJECT_ENDPOINT="https://<resource>.services.ai.azure.com/api/projects/<project>"
export FOUNDRY_MODEL_NAME="gpt-5-mini"
```

当 Agent 作为 Foundry 的托管 Agent 运行时，平台会自动注入 `FOUNDRY_PROJECT_ENDPOINT` 变量。

 **4. 通过 Responses 协议公开 LangGraph Agent：** 

```python
import os

from azure.ai.projects import AIProjectClient
from azure.identity import DefaultAzureCredential, get_bearer_token_provider
from langchain.agents import create_agent
from langchain_openai import ChatOpenAI
from langchain_azure_ai.agents.hosting import ResponsesHostServer

_AZURE_AI_SCOPE = "https://ai.azure.com/.default"


def build_chat_model() -> ChatOpenAI:
    project_endpoint = os.environ["FOUNDRY_PROJECT_ENDPOINT"].rstrip("/")
    deployment = os.environ.get("FOUNDRY_MODEL_NAME", "gpt-5-mini")
    credential = DefaultAzureCredential()
    project = AIProjectClient(endpoint=project_endpoint, credential=credential)
    openai_client = project.get_openai_client()
    token_provider = get_bearer_token_provider(credential, _AZURE_AI_SCOPE)

    # ChatOpenAI here targets the Foundry project's OpenAI-compatible (Responses) endpoint.
    return ChatOpenAI(
        model=deployment,
        base_url=str(openai_client.base_url),
        api_key=token_provider,
    )


def main() -> None:
    graph = create_agent(build_chat_model(), tools=[])
    port = int(os.environ.get("PORT", "8088"))
    ResponsesHostServer(graph).run(port=port)


if __name__ == "__main__":
    main()
```

在本地用 `python main.py` 运行，然后向 `http://localhost:8088/responses` 发送 Responses 请求。

 **关键行为：** 

- **会话** ：客户端通过传递 `previous_response_id` 或 `conversation` ID 继续会话。如果你的图通过 LangGraph 检查点编译，Foundry 会将会话状态关联到检查点（生产环境使用持久化检查点；本地测试可用 `MemorySaver`）。
- **人机协作** ：如果你的图使用 LangGraph 的 `interrupt()`，`ResponsesHostServer` 会将待处理的中断显示为 Responses 的 `function_call` / `mcp_approval_request` 项，客户端通过对应的 `function_call_output` / `mcp_approval_response` 完成恢复。
- **部署到 Foundry** ：使用 Azure Developer CLI — `azd ext install azure.ai.agents`，`azd ai agent init -m &lt;manifest&gt;`，`azd ai agent run`（本地需 Docker），然后 `azd provision` 和 `azd deploy`。托管 Agent 部署需要 **Foundry 项目管理员** 角色。

此示例的可运行版本位于 [code-samples/14-langchain-hosted-agent.py](/labs/14-microsoft-agent-framework-code-samples-14-langchain-hosted-agent-script.md)。完整教程（包含 Invocations 协议、自定义请求架构及故障排查）请参见 [以 Foundry 托管 Agent 身份托管 LangGraph Agent](https://learn.microsoft.com/azure/foundry/how-to/develop/langchain-hosted-agents)。

## 代码示例

Microsoft Agent Framework 的代码示例可在此仓库中找到，位于 `xx-python-agent-framework` 和 `xx-dotnet-agent-framework` 文件夹下。

## 想了解更多关于 Microsoft Agent Framework 的问题？

加入 [Microsoft Foundry Discord](https://discord.com/invite/ATgtXmAS5D) ，与其他学习者交流，参加答疑时间，并获得你的 AI Agent 相关问题的解答。

## 框架对象分别负责什么（补充讲解）

| 对象/机制 | 输入与输出 | 常见误解 |
| --- | --- | --- |
| 模型客户端 | 凭据、项目端点、部署名 → 模型响应 | 创建客户端不等于在云端发布服务 |
| Agent | 指令、工具、消息、会话 → 响应与事件 | 指令不能替代工具授权 |
| Session | 本次/多轮历史状态 | 内存会话不等于长期记忆库 |
| Workflow / Executor | 类型化输入、边与节点状态 → 事件和结果 | 画出边不等于自动处理所有业务异常 |
| Middleware | 调用前后上下文与 `next` | 忘记调用 `next` 会阻断执行；重复调用可能重复副作用 |
| Hosting adapter | 应用接口与运行生命周期 | 托管不是把本地终端关掉后仍能自动运行 |

原文包括推理/流式响应、工具、人类批准、会话序列化、外部消息存储和记忆提供器；这些扩展点的签名在版本间变化较大。先跑最小 Agent，再加一个扩展点，保留能工作的基线。

## 六类示例的阅读与验收

在[准备篇](./setup.md)的固定环境里运行 `14-microsoft-agent-framework/code-samples/` 下对应 Notebook。每份完整代码都在本章底部有阅读页和下载。

| 示例 | 要跟踪的状态 | 验收方法 |
| --- | --- | --- |
| Sequential | 前一角色输出成为后一角色输入 | 保证顺序，汇总引用已完成结果 |
| Concurrent | 多分支各自输出及汇合 | 不把先到的一个结果当成全部完成 |
| Conditional | 路由条件及被选中的分支 | 不符合条件的节点没有运行 |
| Handoff | 当前负责者与交接消息 | 交接后带上必要上下文，有退出限制 |
| Human-in-the-loop | 暂停请求、人工输入、恢复 | 拒绝后不执行副作用，批准只适用于对应动作 |
| Middleware | 调用前后事件 | 中间件按预期顺序执行，异常仍可定位 |

`WorkflowBuilder` 连接执行器；事件流用于观察节点输出与状态。不要把每一个流式文本片段都当成一次完成；消费完事件流并识别最终输出类型，才交给用户完整结果。

原仓库还保留把 **LangChain / LangGraph** Agent 托管到 Foundry 的脚本。这是托管其他框架的扩展路径，没有被本项目替换成 MAF 重写。需要相应框架、容器/托管运行环境及云资源；这里提供原文件导读，未完成云部署验证。

## 无云账号的工作流状态练习（扩展实践）

先操作[多 Agent 演示](./multi-agent.md)，再在纸上或 JSON 中列出 `task_id、status、input、output、error`。把“审批通过”与“工具已执行”拆成两个状态。点击下一步相当于推进一个可观察事件，而不是揭示模型思考。

也可运行综合项目中真实的执行限制与状态更新：

```bash
python3 examples/assistant/app.py '创建任务：阅读工作流' --stage 5 --request-id maf-01
python3 examples/assistant/app.py '创建任务：阅读工作流' --stage 5 --request-id maf-01 --approve
```

第一条等待批准，第二条创建本地任务；使用相同动作和 ID 再跑批准命令应返回同一任务，不重复写入。这个例子使用标准库演示状态原则；真实框架用法仍以前述 MAF Notebook 为准。

## 常见错误与自测

- 找不到 `run_stream`：核对正在使用的发行版本和样例年代，按本课程固定环境使用 `run(stream=True)`。
- 明明登录却 403：确认凭据的租户、项目与角色；改换函数名称不会解决访问权限。
- 消息越来越多：会话复用没有上下文管理；参见[上下文工程](./context.md)。
- 批准后重复退款：恢复流程没有幂等键和执行记录；审批和真正工具执行都需要关联同一动作。

 **练习：** 一个用于记录耗时的中间件，应在什么情况下调用 `next`？异常时还应保留什么？

::: details 参考答案
正常路径只调用一次；用 `try/finally` 记录结束时间，错误路径记录分类和关联 ID，随后按设计传播或转换错误。不要把异常吞掉并返回“成功”，也不要为了重试再次盲目执行有副作用的下一环。
:::

当没有稳定 API 时，可以让 Agent 操作界面。下一章讨论[Browser Use](./browser-use.md)需要增加哪些验证与权限边界。


## 原课程代码与补充材料

以下是本章实际源文件对应的阅读页。Notebook 已分解为说明、代码及原文件输出；云端示例未进行联网端到端验证。正文中的片段用于解释，运行时使用完整 Notebook 和准备篇的固定依赖。

- [14-langchain-hosted-agent.py](/labs/14-microsoft-agent-framework-code-samples-14-langchain-hosted-agent-script.md)
- [14-human-loop.ipynb](/labs/14-microsoft-agent-framework-code-samples-14-human-loop-notebook.md)
- [14-sequential.ipynb](/labs/14-microsoft-agent-framework-code-samples-14-sequential-notebook.md)
- [14-concurrent.ipynb](/labs/14-microsoft-agent-framework-code-samples-14-concurrent-notebook.md)
- [14-handoff.ipynb](/labs/14-microsoft-agent-framework-code-samples-14-handoff-notebook.md)
- [14-middleware.ipynb](/labs/14-microsoft-agent-framework-code-samples-14-middleware-notebook.md)
- [hotel_booking_workflow_sample.py](/labs/14-microsoft-agent-framework-code-samples-hotel-booking-workflow-sample-script.md)
- [14-conditional-workflow.ipynb](/labs/14-microsoft-agent-framework-code-samples-14-conditional-workflow-notebook.md)

## 本章来源

基于 [英文原文](https://github.com/microsoft/ai-agents-for-beginners/blob/25b7985f3b2dc37a84f4a7387ccd3c9f0e5b1595/14-microsoft-agent-framework/README.md) 与 [简体中文翻译](https://github.com/microsoft/ai-agents-for-beginners/blob/25b7985f3b2dc37a84f4a7387ccd3c9f0e5b1595/translations/zh-CN/14-microsoft-agent-framework/README.md) 整理，原作者为 Microsoft 与开源贡献者，采用 MIT 许可证。本页标明“补充讲解”与“扩展实践”的内容为本项目新增。

来源提交：`25b7985f3b2d` · 获取日期：2026-09-14。参见[版本校订记录](/guide/sources.md)。

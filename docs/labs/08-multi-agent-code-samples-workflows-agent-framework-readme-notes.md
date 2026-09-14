---
title: "08 · README"
outline: [2, 3]
---

# 08 · README

[返回：多 Agent 协作](/lessons/multi-agent.md) · [不可变原始文件](https://github.com/microsoft/ai-agents-for-beginners/blob/25b7985f3b2dc37a84f4a7387ccd3c9f0e5b1595/08-multi-agent/code_samples/workflows-agent-framework/README.md)

::: info 原课程补充材料
根据对应简体中文译本整理。原代码片段未进行云端验证。
:::

# 使用 Microsoft Agent Framework 工作流构建多 Agent 应用

本教程将引导你理解并构建使用 Microsoft Agent Framework 的多 Agent 应用。我们将探索多 Agent 系统的核心概念，深入了解框架的工作流组件架构，并通过 Python 和 .NET 中的实际示例演示不同的工作流模式。

## 1\. 理解多 Agent 系统

AI Agent 是一个超越标准大语言模型（LLM）能力的系统。它可以感知环境、做出决策并采取行动以实现特定目标。多 Agent 系统涉及多个这样的 Agent 协作解决单个 Agent 难以或无法独立处理的问题。

### 常见应用场景

  * **复杂问题解决** ：将一个大型任务（例如规划公司范围内的活动）拆分为多个由专门 Agent 处理的子任务（如预算 Agent、物流 Agent、市场营销 Agent）。
  * **虚拟助理** ：一个主助理 Agent 将调度、研究和预订等任务委托给其他专门 Agent。
  * **自动内容创作** ：一个 Agent 起草内容，另一个审查其准确性和语气，再由第三个 Agent 发布内容的工作流。

### 多 Agent 模式

多 Agent 系统可通过多种模式组织，这些模式决定了它们如何交互：

  * **顺序型** ：Agent 按照预定义顺序工作，像装配线一样。一个 Agent 的输出成为下一个的输入。
  * **并发型** ：Agent 并行处理任务的不同部分，最终汇总结果。
  * **条件型** ：工作流根据 Agent 的输出决定不同路径，类似 if-then-else 语句。

## 2\. Microsoft Agent Framework 工作流架构

Agent Framework 的工作流系统是一个先进的编排引擎，用于管理多个 Agent 之间的复杂交互。它基于图形架构，采用[Pregel 风格的执行模型](https://kowshik.github.io/JPregel/pregel_paper.pdf)，处理在称为“超步骤（supersteps）”的同步步骤中进行。

### 核心组件

架构由三个主要部分组成：

1. **执行器** ：这是基本的处理单元。在我们的示例中，`Agent` 是一种执行器。每个执行器可以有多个消息处理器，基于接收的消息类型自动调用。
2. **边（Edges）** ：定义消息在执行器之间的传递路径。边可以带有条件，实现信息在工作流图中的动态路由。
3. **工作流** ：协调整个流程，管理执行器、边及整体执行流。确保消息按正确顺序处理，并流式传输事件以便观察。

*一张展示工作流系统核心组件的图示。*

该结构允许通过基本模式如顺序链、并行处理的分发汇聚（fan-out/fan-in）以及条件分支逻辑，构建健壮且可扩展的应用。

## 3\. 实际示例与代码解析

接下来，我们将探讨如何使用该框架实现不同的工作流模式。每个示例将包括 Python 和 .NET 代码。

### 案例 1：基础顺序工作流

这是最简单的模式，一个 Agent 的输出直接传递给另一个。场景中，一个酒店的 `FrontDesk` Agent 给出旅行推荐，随后由 `Concierge` Agent 审查。

*基础 FrontDesk -> Concierge 工作流的图示。*

#### 场景背景

旅行者询问巴黎的推荐。

1.  设计简洁的 `FrontDesk` Agent 建议参观卢浮宫博物馆。
2.  注重真实体验的 `Concierge` Agent 接收建议，审查并反馈，推荐更接地气、不那么游客化的替代方案。

#### Python 实现分析

在 Python 示例中，我们首先定义并创建两个 Agent，各自带有具体指令。

```python
# 01.python-agent-framework-workflow-ghmodel-basic.ipynb

# 定义代理角色和指令
REVIEWER_NAME = "Concierge"
REVIEWER_INSTRUCTIONS = """
    You are a hotel concierge who has opinions about providing the most local and authentic experiences for travelers...
    """

FRONTDESK_NAME = "FrontDesk"
FRONTDESK_INSTRUCTIONS = """
    You are a Front Desk Travel Agent with ten years of experience and are known for brevity...
    """

# 创建代理实例
reviewer_agent = chat_client.as_agent(
    instructions=(REVIEWER_INSTRUCTIONS),
    name=REVIEWER_NAME,
)

front_desk_agent = chat_client.as_agent(
    instructions=(FRONTDESK_INSTRUCTIONS),
    name=FRONTDESK_NAME,
)
```

接着使用 `WorkflowBuilder` 构建图。将 `front_desk_agent` 设为起点，并创建边将其输出连接到 `reviewer_agent`。

```python
# 01.python-agent-framework-workflow-ghmodel-basic.ipynb

workflow = WorkflowBuilder(start_executor=front_desk_agent).add_edge(front_desk_agent, reviewer_agent).build()
```

最后，执行工作流并传入初始用户提示。

```python
# 01.python-agent-framework-workflow-ghmodel-basic.ipynb

result =''
# run 执行工作流程；get_outputs() 返回输出执行器的结果。
events = await workflow.run('I would like to go to Paris.')
outputs = events.get_outputs()
result = outputs[0].text if outputs else ''
```

#### .NET (C\#) 实现分析

.NET 实现遵循相似逻辑。首先定义 Agent 名称和指令的常量。

```csharp
// 01.dotnet-agent-framework-workflow-ghmodel-basic.ipynb

const string ReviewerAgentName = "Concierge";
const string ReviewerAgentInstructions = @"
    You are a hotel concierge who has opinions about providing the most local and authentic experiences for travelers...";

const string FrontDeskAgentName = "FrontDesk";
const string FrontDeskAgentInstructions = @"""
    You are a Front Desk Travel Agent with ten years of experience and are known for brevity...";
```

使用 `AzureOpenAIClient`（Responses API）创建 Agent，然后用 `WorkflowBuilder` 通过添加一个从 `frontDeskAgent` 到 `reviewerAgent` 的边，定义顺序流程。

```csharp
// 01.dotnet-agent-framework-workflow-ghmodel-basic.ipynb

// Create AIAgent instances
AIAgent reviewerAgent = azureClient.GetChatClient(deployment).AsAIAgent(
    name:ReviewerAgentName,instructions:ReviewerAgentInstructions);
AIAgent frontDeskAgent  = azureClient.GetChatClient(deployment).AsAIAgent(
    name:FrontDeskAgentName,instructions:FrontDeskAgentInstructions);

// Build the workflow
var workflow = new WorkflowBuilder(frontDeskAgent)
            .AddEdge(frontDeskAgent, reviewerAgent)
            .Build();
```

之后运行工作流，传入用户消息，并将结果流式返回。

### 案例 2：多步顺序工作流

此模式在基础顺序上扩展更多 Agent，适合需要多阶段优化或转换的流程。

#### 场景背景

用户提供一张客厅图片，要求给出家具报价。

1. **Sales-Agent** ：识别图中家具项目并列出清单。
2. **Price-Agent** ：根据清单给出详细价格分解，包含经济型、中档、豪华选项。
3. **Quote-Agent** ：接收价格清单并格式化为 Markdown 格式的正式报价文件。

*销售 -> 价格 -> 报价 工作流的图示。*

#### Python 实现分析

定义三个 Agent，各自专责一个环节。使用 `add_edge` 构造链条：`sales_agent` -> `price_agent` -> `quote_agent`。

```python
# 02.python-agent-framework-workflow-ghmodel-sequential.ipynb

# 创建三个专门代理
sales_agent = chat_client.as_agent(...)
price_agent = chat_client.as_agent(...)
quote_agent = chat_client.as_agent(...)

# 构建顺序工作流
workflow = WorkflowBuilder(start_executor=sales_agent).add_edge(sales_agent, price_agent).add_edge(price_agent, quote_agent).build()
```

输入是包含文本和图片 URI 的 `ChatMessage`。框架负责将每个 Agent 的输出传给下一个，直至生成最终报价。

```python
# 02.python-agent-framework-workflow-ghmodel-sequential.ipynb

# 用户消息包含文本和图像
message = ChatMessage(
        role=Role.USER,
        contents=[
            TextContent(text="Please find the relevant furniture..."),
            DataContent(uri=image_uri, media_type="image/png")
        ]
)

# 运行工作流
events = await workflow.run(message)
```

#### .NET (C\#) 实现分析

.NET 示例与 Python 版本类似。创建三个 Agent（`salesagent`，`priceagent`，`quoteagent`）。使用 `WorkflowBuilder` 顺序连接。

```csharp
// 02.dotnet-agent-framework-workflow-ghmodel-sequential.ipynb

// Create agent instances
AIAgent salesagent = azureClient.GetChatClient(deployment).AsAIAgent(...);
AIAgent priceagent  = azureClient.GetChatClient(deployment).AsAIAgent(...);
AIAgent quoteagent = azureClient.GetChatClient(deployment).AsAIAgent(...);

// Build the workflow by adding edges sequentially
var workflow = new WorkflowBuilder(salesagent)
            .AddEdge(salesagent,priceagent)
            .AddEdge(priceagent, quoteagent)
            .Build();
```

用户消息包含图片数据（以字节形式）和文本提示。调用 `InProcessExecution.RunStreamingAsync` 启动工作流，最终输出从流中获取。

### 案例 3：并发工作流

当任务可同时执行以节省时间时，使用此模式。它涉及“分发”到多个 Agent 和“汇总”结果。

#### 场景背景

用户请求规划一次西雅图旅行。

1. **调度器（分发）** ：用户请求同时发送给两个 Agent。
2. **Researcher-Agent** ：研究西雅图十二月的景点、天气和关键注意事项。
3. **Plan-Agent** ：独立制定详细的日程旅行计划。
4. **汇总器（汇总）** ：收集研究者和规划者的输出，共同呈现最终结果。

*并发的 Researcher 和 Planner 工作流图示。*

#### Python 实现分析

`ConcurrentBuilder` 简化了此模式的创建。只需列出参与 Agent，构建器自动创建必要的分发和汇聚逻辑。

```python
# 03.python-agent-framework-workflow-ghmodel-concurrent.ipynb

research_agent = chat_client.as_agent(name="Researcher-Agent", ...)
plan_agent = chat_client.as_agent(name="Plan-Agent", ...)

# ConcurrentBuilder 处理扇出/扇入逻辑
workflow = ConcurrentBuilder().participants([research_agent, plan_agent]).build()

# 运行工作流
events = await workflow.run("Plan a trip to Seattle in December")
```

框架确保 `research_agent` 和 `plan_agent` 并行执行，最终输出汇总为列表。

#### .NET (C\#) 实现分析

在 .NET 中，此模式需要更明确的定义。创建自定义执行器（`ConcurrentStartExecutor` 和 `ConcurrentAggregationExecutor`）处理分发和汇聚逻辑。

```csharp
// 03.dotnet-agent-framework-workflow-ghmodel-concurrent.ipynb

// Custom executor to broadcast the message to all agents
public class ConcurrentStartExecutor() : ...
{
    public async ValueTask HandleAsync(string message, IWorkflowContext context)
    {
        // Send message to all connected agents
        await context.SendMessageAsync(new ChatMessage(ChatRole.User, message));
        // Send a token to start processing
        await context.SendMessageAsync(new TurnToken(emitEvents: true));
    }
}

// Custom executor to collect results
public class ConcurrentAggregationExecutor() : ...
{
    private readonly List<ChatMessage> _messages = [];
    public async ValueTask HandleAsync(ChatMessage message, IWorkflowContext context)
    {
        this._messages.Add(message);
        // Once both agents have responded, yield the final output
        if (this._messages.Count == 2)
        {
            ...
            await context.YieldOutputAsync(formattedMessages);
        }
    }
}
```

之后，`WorkflowBuilder` 通过 `AddFanOutEdge` 和 `AddFanInEdge` 使用这些自定义执行器和 Agent 构建图。

```csharp
// 03.dotnet-agent-framework-workflow-ghmodel-concurrent.ipynb

var workflow = new WorkflowBuilder(startExecutor)
            .AddFanOutEdge(startExecutor, targets: [researcherAgent, plannerAgent])
            .AddFanInEdge(aggregationExecutor, sources: [researcherAgent, plannerAgent])
            .WithOutputFrom(aggregationExecutor)
            .Build();
```

### 案例 4：条件工作流

条件工作流引入分支逻辑，允许系统基于中间结果选择不同路径。

#### 场景背景

该工作流自动创建和发布技术教程。

1. **Evangelist-Agent** ：根据给定大纲和 URL 草拟教程。
2. **ContentReviewer-Agent** ：审查草稿。检查字数是否超过 200 字。
3. **条件分支** ：
      * **如果通过（`Yes`）** ：工作流继续到 `Publisher-Agent`。
      * **如果未通过（`No`）** ：工作流停止并输出拒绝原因。
4. **Publisher-Agent** ：若草稿通过，该 Agent 将内容保存为 Markdown 文件。

#### Python 实现分析

示例中使用自定义函数 `select_targets` 实现条件逻辑。该函数传递给 `add_multi_selection_edge_group`，根据审阅者输出的 `review_result` 字段指导工作流。

```python
# 04.python-agent-framework-workflow-aifoundry-condition.ipynb

# 此函数根据审核结果确定下一步
def select_targets(review: ReviewResult, target_ids: list[str]) -> list[str]:
    handle_review_id, save_draft_id = target_ids
    if review.review_result == "Yes":
        # 如果审核通过，继续执行 'save_draft' 执行器
        return [save_draft_id]
    else:
        # 如果审核不通过，继续执行 'handle_review' 执行器以报告失败
        return [handle_review_id]

# 工作流构建器使用选择函数进行路由
workflow = (
    WorkflowBuilder()
        .set_start_executor(evangelist_agent)
        .add_edge(evangelist_agent, reviewer_agent)
        .add_edge(reviewer_agent, to_reviewer_result)
        # 多选择边实现条件逻辑
        .add_multi_selection_edge_group(
            to_reviewer_result,
            [handle_review, save_draft],
            selection_func=select_targets,
        )
        .add_edge(save_draft, publisher_agent)
        .build()
)
```

使用诸如 `to_reviewer_result` 的自定义执行器解析 Agent 的 JSON 输出，转换为强类型对象供选择函数检视。

#### .NET (C\#) 实现分析

.NET 版本采用类似方法，定义了一个 `Func&lt;object?, bool&gt;` 来检查 `ReviewResult` 对象的 `Result` 属性。

```csharp
// 04.dotnet-agent-framework-workflow-aifoundry-condition.ipynb

// This function creates a lambda for the condition check
public Func<object?, bool> GetCondition(string expectedResult) =>
        reviewResult => reviewResult is ReviewResult review && review.Result == expectedResult;

// The workflow is built with conditional edges
var workflow = new WorkflowBuilder(draftExecutor)
            .AddEdge(draftExecutor, contentReviewerExecutor)
            // Add an edge to the publisher only if the review result is "Yes"
            .AddEdge(contentReviewerExecutor, publishExecutor, condition: GetCondition(expectedResult: "Yes"))
            // Add an edge to the reviewer feedback executor if the result is "No"
            .AddEdge(contentReviewerExecutor, sendReviewerExecutor, condition: GetCondition(expectedResult: "No"))
            .Build();
```

`AddEdge` 方法的 `condition` 参数使 `WorkflowBuilder` 能创建分支路径。只有当条件 `GetCondition(expectedResult: "Yes")` 返回真时，工作流才会执行到 `publishExecutor`，否则走向 `sendReviewerExecutor`。

## 结论

Microsoft Agent Framework 工作流为编排复杂多 Agent 系统提供了强大且灵活的基础。通过其基于图形的架构和核心组件，开发者可以在 Python 和 .NET 中设计并实现复杂工作流。无论应用需求是简单的顺序处理、并行执行，还是动态的条件逻辑，该框架均提供构建强大、可扩展且类型安全 AI 驱动解决方案的工具。

---
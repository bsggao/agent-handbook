---
title: "08 · 03.dotnet-agent-framework-workflow-ghmodel-concurrent"
outline: [2, 3]
---

# 08 · 03.dotnet-agent-framework-workflow-ghmodel-concurrent

[返回：多 Agent 协作](/lessons/multi-agent.md) · [不可变原始文件](https://github.com/microsoft/ai-agents-for-beginners/blob/25b7985f3b2dc37a84f4a7387ccd3c9f0e5b1595/08-multi-agent/code_samples/workflows-agent-framework/dotNET/03.dotnet-agent-framework-workflow-ghmodel-concurrent.cs)

::: info 原课程脚本 · 未联网执行
保留原始框架与完整代码。依赖、变量、入口以脚本及其相邻 README 为准；本页为代码导读，未声称所有外部服务均已验证。
:::

行为约束：instructions 引导模型，不能替代执行器的权限验证、次数限制和结果检查。

检索过程：跟踪查询、候选结果和实际选入的证据；检索为空时应明确返回缺失，而不是补写答案。

```csharp
#!/usr/bin/dotnet run
#:package Microsoft.Extensions.AI@10.*
#:package Azure.AI.OpenAI@2.*
#:package Azure.Identity@1.15.0
#:package System.Linq.Async@6.0.3
#:package OpenTelemetry.Api@1.*
#:package Microsoft.Agents.AI.Workflows@1.*
#:package Microsoft.Agents.AI.OpenAI@1.*-*
#:package DotNetEnv@3.1.1

using Azure.AI.OpenAI;
using Azure.Identity;
using Microsoft.Extensions.AI;
using Microsoft.Agents.AI;
using Microsoft.Agents.AI.Workflows;
using DotNetEnv;

// Load environment variables from .env file
Env.Load("../../../.env");

// Azure OpenAI with the Responses API (stable v1 endpoint). Sign in with `az login`.
var azureEndpoint = Environment.GetEnvironmentVariable("AZURE_OPENAI_ENDPOINT")
    ?? throw new InvalidOperationException("AZURE_OPENAI_ENDPOINT is not set.");
var deployment = Environment.GetEnvironmentVariable("AZURE_OPENAI_DEPLOYMENT") ?? "gpt-5-mini";

var azureClient = new AzureOpenAIClient(new Uri(azureEndpoint), new AzureCliCredential());

// Define Researcher Agent for concurrent execution
const string ResearcherAgentName = "Researcher-Agent";
const string ResearcherAgentInstructions = "You are my travel researcher, working with me to analyze the destination, list relevant attractions, and make detailed plans for each attraction.";

// Define Planner Agent for concurrent execution
const string PlanAgentName = "Plan-Agent";
const string PlanAgentInstructions = "You are my travel planner, working with me to create a detailed travel plan based on the researcher's findings.";

// Create AI agents for concurrent workflow
AIAgent researcherAgent = azureClient.GetChatClient(deployment).AsIChatClient().AsAIAgent(
    name: ResearcherAgentName, instructions: ResearcherAgentInstructions);
AIAgent plannerAgent = azureClient.GetChatClient(deployment).AsIChatClient().AsAIAgent(
    name: PlanAgentName, instructions: PlanAgentInstructions);

// Create custom executor instances
var startExecutor = new ConcurrentStartExecutor();
var aggregationExecutor = new ConcurrentAggregationExecutor();

// Build concurrent workflow with Fan-Out/Fan-In pattern
var workflow = new WorkflowBuilder(startExecutor)
    .AddFanOutEdge(startExecutor, targets: [researcherAgent, plannerAgent])
    .AddFanInBarrierEdge(sources: [researcherAgent, plannerAgent], aggregationExecutor)
    .WithOutputFrom(aggregationExecutor)
    .Build();

// Execute concurrent workflow with streaming
StreamingRun run = await InProcessExecution.RunStreamingAsync(workflow, "Plan a trip to Seattle in December");

// Watch for workflow events and display final output
await foreach (WorkflowEvent evt in run.WatchStreamAsync().ConfigureAwait(false))
{
    if (evt is WorkflowOutputEvent output)
    {
        Console.WriteLine($"Workflow completed with results:\n{output.Data}");
    }
}

/// <summary>
/// Custom executor that starts concurrent processing by broadcasting to all agents.
/// This implements the "Fan-Out" pattern where one input triggers multiple parallel operations.
/// </summary>
[SendsMessage(typeof(ChatMessage))]
[SendsMessage(typeof(TurnToken))]
public class ConcurrentStartExecutor() : Executor<string>("ConcurrentStartExecutor")
{
    /// <summary>
    /// Starts the concurrent processing by sending messages to the agents.
    /// </summary>
    /// <param name="message">The user message to process</param>
    /// <param name="context">Workflow context for accessing workflow services and adding events</param>
    /// <returns>A task representing the asynchronous operation</returns>
    [MessageHandler]
    public override async ValueTask HandleAsync(string message, IWorkflowContext context, CancellationToken cancellationToken = default)
    {
        // Broadcast the message to all connected agents. Receiving agents will queue
        // the message but will not start processing until they receive a turn token.
        await context.SendMessageAsync(new ChatMessage(ChatRole.User, message));
        // Broadcast the turn token to kick off the agents.
        await context.SendMessageAsync(new TurnToken(emitEvents: true));
    }

}

/// <summary>
/// Custom executor that aggregates results from concurrent agents.
/// This implements the "Fan-In" pattern where multiple parallel results are merged into one output.
/// </summary>
[YieldsOutput(typeof(string))]
public class ConcurrentAggregationExecutor() : Executor<ChatMessage>("ConcurrentAggregationExecutor")
{
    private readonly List<ChatMessage> _messages = [];
    private readonly object _lock = new();

    /// <summary>
    /// Handles incoming messages from the agents and aggregates their responses.
    /// </summary>
    /// <param name="message">The message from the agent</param>
    /// <param name="context">Workflow context for accessing workflow services and adding events</param>
    /// <returns>A task representing the asynchronous operation</returns>

    public override async ValueTask HandleAsync(ChatMessage message, IWorkflowContext context, CancellationToken cancellationToken = default)
    {
        string? formattedMessages = null;

        lock (this._lock)
        {
            this._messages.Add(message);

            if (this._messages.Count == 2)
            {
                formattedMessages = string.Join(Environment.NewLine, this._messages.Select(m => $"{m.AuthorName}: {m.Text}"));
            }
        }

        if (formattedMessages is not null)
        {
            await context.YieldOutputAsync(formattedMessages);
        }
    }
}

```

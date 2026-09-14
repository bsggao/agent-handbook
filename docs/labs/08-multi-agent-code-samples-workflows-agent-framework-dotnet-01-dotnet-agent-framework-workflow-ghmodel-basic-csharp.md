---
title: "08 · 01.dotnet-agent-framework-workflow-ghmodel-basic"
outline: [2, 3]
---

# 08 · 01.dotnet-agent-framework-workflow-ghmodel-basic

[返回：多 Agent 协作](/lessons/multi-agent.md) · [不可变原始文件](https://github.com/microsoft/ai-agents-for-beginners/blob/25b7985f3b2dc37a84f4a7387ccd3c9f0e5b1595/08-multi-agent/code_samples/workflows-agent-framework/dotNET/01.dotnet-agent-framework-workflow-ghmodel-basic.cs)

::: info 原课程脚本 · 未联网执行
保留原始框架与完整代码。依赖、变量、入口以脚本及其相邻 README 为准；本页为代码导读，未声称所有外部服务均已验证。
:::

行为约束：instructions 引导模型，不能替代执行器的权限验证、次数限制和结果检查。

```csharp
#!/usr/bin/dotnet run
#:package Microsoft.Extensions.AI@10.*
#:package Azure.AI.OpenAI@2.1.0
#:package Azure.Identity@1.15.0
#:package System.Linq.Async@6.0.3
#:package OpenTelemetry.Api@1.*
#:package Microsoft.Agents.AI.Workflows@1.*
#:package Microsoft.Agents.AI.OpenAI@1.*-*
#:package DotNetEnv@3.1.1

using System;
using System.ComponentModel;
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

// Define Reviewer Agent (Concierge) configuration
const string ReviewerAgentName = "Concierge";
const string ReviewerAgentInstructions = @"
    You are a hotel concierge who has opinions about providing the most local and authentic experiences for travelers.
    The goal is to determine if the front desk travel agent has recommended the best non-touristy experience for a traveler.
    If so, state that it is approved.
    If not, provide insight on how to refine the recommendation without using a specific example. ";

// Define Front Desk Agent configuration
const string FrontDeskAgentName = "FrontDesk";
const string FrontDeskAgentInstructions = @"""
    You are a Front Desk Travel Agent with ten years of experience and are known for brevity as you deal with many customers.
    The goal is to provide the best activities and locations for a traveler to visit.
    Only provide a single recommendation per response.
    You're laser focused on the goal at hand.
    Don't waste time with chit chat.
    Consider suggestions when refining an idea.
    """;

// Create AI agents with specialized instructions (convert to IChatClient to align with Microsoft.Extensions.AI abstractions and avoid type ambiguity)
AIAgent reviewerAgent = azureClient.GetChatClient(deployment).AsIChatClient().AsAIAgent(
    name: ReviewerAgentName,
    instructions: ReviewerAgentInstructions,
    description: "Reviews travel recommendations for authenticity.");
AIAgent frontDeskAgent = azureClient.GetChatClient(deployment).AsIChatClient().AsAIAgent(
    name: FrontDeskAgentName,
    instructions: FrontDeskAgentInstructions,
    description: "Provides concise travel activity recommendations.");

// Build workflow with sequential agent execution
var workflow = new WorkflowBuilder(frontDeskAgent)
    .AddEdge(frontDeskAgent, reviewerAgent)
    .Build();

// Create user message for travel recommendation
ChatMessage userMessage = new ChatMessage(ChatRole.User, [
    new TextContent("I would like to go to Paris.")
]);

// Execute workflow with streaming
StreamingRun run = await InProcessExecution.RunStreamingAsync(workflow, userMessage);

// Process workflow events and collect results
await run.TrySendMessageAsync(new TurnToken(emitEvents: true));
string id = "";
string messageData = "";
await foreach (WorkflowEvent evt in run.WatchStreamAsync().ConfigureAwait(false))
{
    if (evt is AgentResponseUpdateEvent executorComplete)
    {
        if (id == "")
        {
            id = executorComplete.ExecutorId;
        }
        if (id == executorComplete.ExecutorId)
        {
            if (executorComplete.Data is not null)
            {
                messageData += executorComplete.Data.ToString();
            }
        }
        else
        {
            id = executorComplete.ExecutorId;
        }
    }
}

// Display final workflow results
Console.WriteLine(messageData);

```

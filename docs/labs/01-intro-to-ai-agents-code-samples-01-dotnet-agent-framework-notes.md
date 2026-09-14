---
title: "01 · 01-dotnet-agent-framework"
outline: [2, 3]
---

# 01 · 01-dotnet-agent-framework

[返回：AI Agent 入门与应用场景](/lessons/introduction.md) · [不可变原始文件](https://github.com/microsoft/ai-agents-for-beginners/blob/25b7985f3b2dc37a84f4a7387ccd3c9f0e5b1595/01-intro-to-ai-agents/code_samples/01-dotnet-agent-framework.md)

::: info 原课程补充材料
根据对应简体中文译本整理。原代码片段未进行云端验证。
:::

# 🌍 使用 Microsoft Agent Framework (.NET) 的 AI 旅游 Agent

## 📋 场景概述

本示例演示如何使用适用于 .NET 的 Microsoft Agent Framework 构建智能旅行规划 Agent。该 Agent 可以自动生成面向全球随机目的地的个性化一日游行程。

### 主要功能：

- 🎲 **随机目的地选择** ：使用自定义工具选择度假地点
- 🗺️ **智能旅行规划** ：创建详细的每日行程安排
- 🔄 **实时流式传输** ：支持即时和流式响应
- 🛠️ **自定义工具集成** ：演示如何扩展 Agent 功能

## 🔧 技术架构

### 核心技术

- **Microsoft Agent Framework** ：用于 AI Agent 开发的最新 .NET 实现
- **Azure OpenAI（响应 API）** ：使用 Azure OpenAI 响应 API 执行模型推理
- **Azure 身份验证** ：通过 `AzureCliCredential`（`az login`）实现安全登录
- **安全配置** ：基于环境的端点管理

### 关键组件

1. **AIAgent** ：管理对话流程的主要 Agent 协调器
2. **自定义工具** ：Agent 可调用的 `GetRandomDestination()` 函数
3. **响应客户端** ：基于 Azure OpenAI 响应的对话接口
4. **流式支持** ：实时响应生成能力

### 集成模式

```mermaid
graph LR
    A[用户请求] --> B[人工智能代理]
    B --> C[Azure OpenAI（响应 API）]
    B --> D[获取随机目的地工具]
    C --> E[旅行行程]
    D --> E
```

## 🚀 快速开始

### 前置条件

- [.NET 10 SDK](https://dotnet.microsoft.com/download/dotnet/10.0) 或更高版本
- 拥有 Azure OpenAI 资源和模型部署的 [Azure 订阅](https://azure.microsoft.com/free/)
- [Azure CLI](https://learn.microsoft.com/cli/azure/install-azure-cli) — 使用 `az login` 登录

### 必需的环境变量

```bash
# zsh/bash
export AZURE_OPENAI_ENDPOINT=https://<your-resource>.openai.azure.com
export AZURE_OPENAI_DEPLOYMENT=gpt-5-mini
# 然后登录以便 AzureCliCredential 能获取令牌
az login
```

```powershell
# PowerShell
$env:AZURE_OPENAI_ENDPOINT = "https://<your-resource>.openai.azure.com"
$env:AZURE_OPENAI_DEPLOYMENT = "gpt-5-mini"
# 然后登录以便 AzureCliCredential 可以获取令牌
az login
```

### 示例代码

运行代码示例，

```bash
# zsh/bash
chmod +x ./01-dotnet-agent-framework.cs
./01-dotnet-agent-framework.cs
```

或使用 dotnet CLI：

```bash
dotnet run ./01-dotnet-agent-framework.cs
```

完整代码见 [`01-dotnet-agent-framework.cs`](/labs/01-intro-to-ai-agents-code-samples-01-dotnet-agent-framework-csharp.md)。

```csharp
#!/usr/bin/dotnet run

#:package Microsoft.Extensions.AI@10.4.1
#:package Microsoft.Agents.AI.OpenAI@1.1.0
#:package Azure.AI.OpenAI@2.1.0
#:package Azure.Identity@1.13.1

using System.ComponentModel;

using Microsoft.Agents.AI;
using Microsoft.Extensions.AI;

using Azure.AI.OpenAI;
using Azure.Identity;

// Tool Function: Random Destination Generator
// This static method will be available to the agent as a callable tool
// The [Description] attribute helps the AI understand when to use this function
// This demonstrates how to create custom tools for AI agents
[Description("Provides a random vacation destination.")]
static string GetRandomDestination()
{
    // List of popular vacation destinations around the world
    // The agent will randomly select from these options
    var destinations = new List<string>
    {
        "Paris, France",
        "Tokyo, Japan",
        "New York City, USA",
        "Sydney, Australia",
        "Rome, Italy",
        "Barcelona, Spain",
        "Cape Town, South Africa",
        "Rio de Janeiro, Brazil",
        "Bangkok, Thailand",
        "Vancouver, Canada"
    };

    // Generate random index and return selected destination
    // Uses System.Random for simple random selection
    var random = new Random();
    int index = random.Next(destinations.Count);
    return destinations[index];
}

// Azure OpenAI with the Responses API (stable v1 endpoint). Sign in with `az login`.
var azureEndpoint = Environment.GetEnvironmentVariable("AZURE_OPENAI_ENDPOINT")
    ?? throw new InvalidOperationException("AZURE_OPENAI_ENDPOINT is not set.");
var deployment = Environment.GetEnvironmentVariable("AZURE_OPENAI_DEPLOYMENT") ?? "gpt-5-mini";

var azureClient = new AzureOpenAIClient(new Uri(azureEndpoint), new AzureCliCredential());

// Create AI Agent with Travel Planning Capabilities
// Get the Responses client for the specified deployment and create the AI agent
// Configure agent with travel planning instructions and random destination tool
// The agent can now plan trips using the GetRandomDestination function
AIAgent agent = azureClient
    .GetChatClient(deployment)
    .AsAIAgent(
        instructions: "You are a helpful AI Agent that can help plan vacations for customers at random destinations",
        tools: [AIFunctionFactory.Create(GetRandomDestination)]
    );

// Execute Agent: Plan a Day Trip
// Run the agent with streaming enabled for real-time response display
// Shows the agent's thinking and response as it generates the content
// Provides better user experience with immediate feedback
await foreach (var update in agent.RunStreamingAsync("Plan me a day trip"))
{
    await Task.Delay(10);
    Console.Write(update);
}
```

## 🎓 主要收获

1. **Agent 架构** ：Microsoft Agent Framework 提供了在 .NET 中构建 AI Agent 的清晰且类型安全的方法
2. **工具集成** ：标有 `[Description]` 属性的函数成为 Agent 可用的工具
3. **配置管理** ：环境变量和安全凭据处理遵循 .NET 最佳实践
4. **Azure OpenAI 响应 API** ：Agent 通过 Azure.AI.OpenAI SDK 使用 Azure OpenAI 响应 API

## 🔗 其他资源

- [Microsoft Agent Framework 文档](https://learn.microsoft.com/agent-framework)
- [Microsoft Foundry 的 Azure OpenAI](https://learn.microsoft.com/azure/ai-services/openai/)
- [Microsoft.Extensions.AI](https://learn.microsoft.com/dotnet/ai/microsoft-extensions-ai)
- [.NET 单文件应用](https://devblogs.microsoft.com/dotnet/announcing-dotnet-run-app)

---
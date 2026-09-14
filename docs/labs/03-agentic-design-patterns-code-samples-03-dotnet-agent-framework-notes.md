---
title: "03 · 03-dotnet-agent-framework"
outline: [2, 3]
---

# 03 · 03-dotnet-agent-framework

[返回：Agent 设计模式](/lessons/design-patterns.md) · [不可变原始文件](https://github.com/microsoft/ai-agents-for-beginners/blob/25b7985f3b2dc37a84f4a7387ccd3c9f0e5b1595/03-agentic-design-patterns/code_samples/03-dotnet-agent-framework.md)

::: info 原课程补充材料
根据对应简体中文译本整理。原代码片段未进行云端验证。
:::

# 🎨 使用 Azure OpenAI （Responses API） 的智能 Agent 设计模式（.NET）

## 📋 学习目标

本示例演示了使用 .NET 中的 Microsoft Agent Framework 结合 Azure OpenAI （Responses API）集成构建智能 Agent 的企业级设计模式。你将学习专业的模式和架构方法，使 Agent 具备生产准备、易维护和可扩展的能力。

### 企业设计模式

- 🏭 **工厂模式** ：使用依赖注入实现标准化的 Agent 创建
- 🔧 **生成器模式** ：流畅的 Agent 配置与设置
- 🧵 **线程安全模式** ：并发对话管理
- 📋 **仓储模式** ：有序的工具和能力管理

## 🎯 .NET 特定的架构优势

### 企业功能

- **强类型** ：编译时验证与智能感知支持
- **依赖注入** ：内置 DI 容器集成
- **配置管理** ：IConfiguration 和选项模式
- **异步/等待** ：一流的异步编程支持

### 生产就绪模式

- **日志集成** ：ILogger 与结构化日志支持
- **健康检查** ：内置监控与诊断
- **配置验证** ：带数据注解的强类型
- **错误处理** ：结构化异常管理

## 🔧 技术架构

### 核心 .NET 组件

- **Microsoft.Extensions.AI** ：统一的 AI 服务抽象
- **Microsoft.Agents.AI** ：企业级 Agent 编排框架
- **Azure OpenAI（Responses API）** ：高性能 API 客户端模式
- **配置系统** ：appsettings.json 和环境集成

### 设计模式实现

```mermaid
graph LR
    A[IServiceCollection] --> B[代理构建器]
    B --> C[配置]
    C --> D[工具注册表]
    D --> E[AI 代理]
```

## 🏗️ 展示的企业模式

### 1. **创建型模式** 

- **Agent 工厂** ：集中式 Agent 创建及一致配置
- **生成器模式** ：复杂 Agent 配置的流式 API
- **单例模式** ：共享资源与配置管理
- **依赖注入** ：松耦合与易测试

### 2. **行为型模式** 

- **策略模式** ：可替换的工具执行策略
- **命令模式** ：封装的 Agent 操作支持撤销/重做
- **观察者模式** ：事件驱动的 Agent 生命周期管理
- **模板方法** ：标准化 Agent 执行工作流

### 3. **结构型模式** 

- **适配器模式** ：Azure OpenAI（Responses API）集成层
- **装饰器模式** ：增强 Agent 能力
- **外观模式** ：简化 Agent 交互接口
- **Agent 模式** ：延迟加载与缓存以提升性能

## 📚 .NET 设计原则

### SOLID 原则

- **单一职责** ：每个组件只有一个明确职责
- **开闭原则** ：可扩展而无需修改
- **里氏替换** ：基于接口的工具实现
- **接口隔离** ：专注且内聚的接口
- **依赖倒置** ：依赖抽象而非具体实现

### 清晰架构

- **领域层** ：核心 Agent 和工具抽象
- **应用层** ：Agent 编排与工作流
- **基础设施层** ：Azure OpenAI（Responses API）集成及外部服务
- **表现层** ：用户交互和响应格式化

## 🔒 企业级注意事项

### 安全性

- **凭证管理** ：使用 IConfiguration 安全处理 API 密钥
- **输入验证** ：强类型与数据注解验证
- **输出净化** ：安全的响应处理与过滤
- **审计日志** ：全面的操作跟踪

### 性能

- **异步模式** ：非阻塞 I/O 操作
- **连接池** ：高效的 HTTP 客户端管理
- **缓存** ：响应缓存以提升性能
- **资源管理** ：合适的释放与清理模式

### 可扩展性

- **线程安全** ：支持并发 Agent 执行
- **资源池** ：高效利用资源
- **负载管理** ：限流与背压处理
- **监控** ：性能指标与健康检查

## 🚀 生产部署

- **配置管理** ：环境特定设置
- **日志策略** ：带关联 ID 的结构化日志
- **错误处理** ：全局异常处理与合适的恢复
- **监控** ：应用洞察与性能计数器
- **测试** ：单元测试、集成测试和负载测试模式

准备好用 .NET 构建企业级智能 Agent 了吗？让我们共同设计一个强健的架构！🏢✨

## 🚀 入门指南

### 前置条件

- [.NET 10 SDK](https://dotnet.microsoft.com/download/dotnet/10.0) 或更高版本
- 拥有一个带有 Azure OpenAI 资源和模型部署的 [Azure 订阅](https://azure.microsoft.com/free/)
- 安装 [Azure CLI](https://learn.microsoft.com/cli/azure/install-azure-cli) — 使用 `az login` 登录

### 必需的环境变量

```bash
# zsh/bash
export AZURE_OPENAI_ENDPOINT=https://<your-resource>.openai.azure.com
export AZURE_OPENAI_DEPLOYMENT=gpt-5-mini
# 然后登录，以便 AzureCliCredential 可以获取令牌
az login
```

```powershell
# PowerShell
$env:AZURE_OPENAI_ENDPOINT = "https://<your-resource>.openai.azure.com"
$env:AZURE_OPENAI_DEPLOYMENT = "gpt-5-mini"
# 然后登录，以便 AzureCliCredential 可以获取令牌
az login
```

### 示例代码

运行以下代码示例，

```bash
# zsh/bash
chmod +x ./03-dotnet-agent-framework.cs
./03-dotnet-agent-framework.cs
```

或使用 dotnet CLI：

```bash
dotnet run ./03-dotnet-agent-framework.cs
```

完整代码见 [`03-dotnet-agent-framework.cs`](/labs/03-agentic-design-patterns-code-samples-03-dotnet-agent-framework-csharp.md)。

```csharp
#!/usr/bin/dotnet run

#:package Microsoft.Extensions.AI@10.*
#:package Microsoft.Agents.AI.OpenAI@1.*-*
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

// Define Agent Identity and Comprehensive Instructions
// Agent name for identification and logging purposes
var AGENT_NAME = "TravelAgent";

// Detailed instructions that define the agent's personality, capabilities, and behavior
// This system prompt shapes how the agent responds and interacts with users
var AGENT_INSTRUCTIONS = """
You are a helpful AI Agent that can help plan vacations for customers.

Important: When users specify a destination, always plan for that location. Only suggest random destinations when the user hasn't specified a preference.

When the conversation begins, introduce yourself with this message:
"Hello! I'm your TravelAgent assistant. I can help plan vacations and suggest interesting destinations for you. Here are some things you can ask me:
1. Plan a day trip to a specific location
2. Suggest a random vacation destination
3. Find destinations with specific features (beaches, mountains, historical sites, etc.)
4. Plan an alternative trip if you don't like my first suggestion

What kind of trip would you like me to help you plan today?"

Always prioritize user preferences. If they mention a specific destination like "Bali" or "Paris," focus your planning on that location rather than suggesting alternatives.
""";

// Create AI Agent with Advanced Travel Planning Capabilities
// Get the Responses client for the deployment and create the AI agent
// Configure agent with name, detailed instructions, and available tools
// This demonstrates the .NET agent creation pattern with full configuration
AIAgent agent = azureClient
    .GetChatClient(deployment)
    .AsAIAgent(
        name: AGENT_NAME,
        instructions: AGENT_INSTRUCTIONS,
        tools: [AIFunctionFactory.Create(GetRandomDestination)]
    );

// Create New Conversation Session for Context Management
// Initialize a new conversation session to maintain context across multiple interactions
// Sessions enable the agent to remember previous exchanges and maintain conversational state
// This is essential for multi-turn conversations and contextual understanding
var session = await agent.CreateSessionAsync();

// Execute Agent: First Travel Planning Request
// Run the agent with an initial request that will likely trigger the random destination tool
// The agent will analyze the request, use the GetRandomDestination tool, and create an itinerary
// Using the session parameter maintains conversation context for subsequent interactions
await foreach (var update in agent.RunStreamingAsync("Plan me a day trip", session))
{
    await Task.Delay(10);
    Console.Write(update);
}

Console.WriteLine();

// Execute Agent: Follow-up Request with Context Awareness
// Demonstrate contextual conversation by referencing the previous response
// The agent remembers the previous destination suggestion and will provide an alternative
// This showcases the power of conversation sessions and contextual understanding in .NET agents
await foreach (var update in agent.RunStreamingAsync("I don't like that destination. Plan me another vacation.", session))
{
    await Task.Delay(10);
    Console.Write(update);
}
```

---
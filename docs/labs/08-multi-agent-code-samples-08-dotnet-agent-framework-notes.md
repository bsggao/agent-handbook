---
title: "08 · 08-dotnet-agent-framework"
outline: [2, 3]
---

# 08 · 08-dotnet-agent-framework

[返回：多 Agent 协作](/lessons/multi-agent.md) · [不可变原始文件](https://github.com/microsoft/ai-agents-for-beginners/blob/25b7985f3b2dc37a84f4a7387ccd3c9f0e5b1595/08-multi-agent/code_samples/08-dotnet-agent-framework.md)

::: info 原课程补充材料
根据对应简体中文译本整理。原代码片段未进行云端验证。
:::

# 🤝 企业多 Agent 工作流系统（.NET）

## 📋 学习目标

本笔记本展示了如何使用.NET中的Microsoft Agent 框架和Azure OpenAI（Responses API）构建复杂的企业级多 Agent 系统。你将学习如何通过结构化工作流协调多个专业化 Agent 协同工作，利用.NET的企业功能实现生产就绪的解决方案。

 **你将构建的企业多 Agent 能力：** 
- 👥 **Agent 协作** ：使用编译时验证的类型安全 Agent 协调
- 🔄 **工作流编排** ：使用.NET异步模式的声明式工作流定义
- 🎭 **角色专业化** ：强类型 Agent 角色和专业领域
- 🏢 **企业集成** ：具备监控和错误处理的生产就绪模式

## ⚙️ 前提条件与设置

 **开发环境：** 
- .NET 9.0 SDK 或更高版本
- Visual Studio 2022 或带有 C# 扩展的 VS Code
- Azure 订阅（用于持久化 Agent）

 **必需的 NuGet 包：** 
```xml
<PackageReference Include="Microsoft.Extensions.AI.Abstractions" Version="10.*" />
<PackageReference Include="Azure.AI.Agents.Persistent" Version="1.2.0-beta.10" />
<PackageReference Include="Azure.Identity" Version="1.15.0" />
<PackageReference Include="System.Linq.Async" Version="6.0.3" />
<PackageReference Include="Microsoft.Extensions.AI" Version="10.*" />
<PackageReference Include="DotNetEnv" Version="3.1.1" />
<PackageReference Include="Microsoft.Extensions.AI.OpenAI" Version="10.*" />
<PackageReference Include="OpenTelemetry.Api" Version="1.*" />
<PackageReference Include="Microsoft.Agents.AI.Workflows" Version="1.*" />
<PackageReference Include="Microsoft.Agents.AI.OpenAI" Version="1.*-*" />
```

## 代码示例

本课的完整工作代码可在附带的 C# 文件中获取：[ `08-dotnet-agent-framework.cs`](/labs/08-multi-agent-code-samples-08-dotnet-agent-framework-csharp.md)

运行示例：

```bash
# 使文件可执行（Linux/macOS）
chmod +x 08-dotnet-agent-framework.cs

# 运行示例
./08-dotnet-agent-framework.cs
```

或使用 .NET CLI：

```bash
dotnet run 08-dotnet-agent-framework.cs
```

## 本示例演示内容

该多 Agent 工作流系统创建了一个酒店旅行推荐服务，包含两个专业 Agent：

1. **FrontDesk Agent** ：提供活动和地点推荐的旅行 Agent
2. **Concierge Agent** ：审核推荐以确保真实、非旅游化的体验

Agent 共同在一个工作流中协作：
- FrontDeskAgent 接收初始旅行请求
- ConciergeAgent 审核并优化推荐
- 工作流实时流式传输响应

## 关键概念

### Agent 协调
本示例展示了使用Microsoft Agent 框架进行类型安全的 Agent 协调，具备编译时验证。

### 工作流编排
使用.NET异步模式的声明式工作流定义，将多个 Agent 连接成管道。

### 流式响应
实现使用异步可枚举和事件驱动架构的 Agent 响应实时流式传输。

### 企业集成
展示生产就绪模式，包括：
- 环境变量配置
- 安全凭据管理
- 错误处理
- 异步事件处理

---
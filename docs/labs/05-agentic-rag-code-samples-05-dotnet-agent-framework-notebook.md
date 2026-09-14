---
title: "05 · 05-dotnet-agent-framework"
outline: [2, 3]
---

# 05 · 05-dotnet-agent-framework

[返回：Agentic RAG](/lessons/rag.md) · [不可变原始文件](https://github.com/microsoft/ai-agents-for-beginners/blob/25b7985f3b2dc37a84f4a7387ccd3c9f0e5b1595/05-agentic-rag/code_samples/05-dotnet-agent-framework.ipynb)

::: warning 原课程完整 Notebook · 静态阅读与代码解析
代码按英文源文件顺序保留，中文说明以同版本译本为基础。原始安装单元格可能含无版本上限的 `-U`；请跳过它们，先按[准备篇](/lessons/setup.md)固定依赖。云端服务、模型权限、网站布局和部分 SDK 接口需在你自己的环境验证。本站没有执行云端请求；第 18 章的离线验证状态单独记录在[检查报告](/guide/verification.md)。
:::

## 运行准备

Python 3.12+；在独立虚拟环境安装源仓库依赖与本页中声明的额外依赖。原文件路径：`upstream/05-agentic-rag/code_samples/05-dotnet-agent-framework.ipynb`。以原仓库根目录为工作目录，在 Jupyter 中按顺序执行；身份与环境变量见准备篇。

```bash
cd upstream
python -m jupyterlab
```

[下载原始 Notebook](/notebooks/05-agentic-rag/code_samples/05-dotnet-agent-framework.ipynb)。输出为上游文件保存的历史结果，不能用作本站实测证明。

## 🔍 使用 Microsoft Foundry (.NET) 构建企业级 RAG

## 📋 学习目标

本笔记本演示如何使用 Microsoft Foundry 中的 Microsoft Agent Framework 在 .NET 环境下构建企业级检索增强生成（RAG）系统。你将学习如何创建可投入生产的 Agent，这些 Agent 能够检索文档并提供准确且具上下文意识的响应，同时保障企业级的安全性和可扩展性。

 **你将构建的企业级 RAG 功能：** 
- 📚 **文档智能** ：使用 Azure AI 服务进行高级文档处理
- 🔍 **语义搜索** ：具备企业特性的高性能向量搜索
- 🛡️ **安全集成** ：基于角色的访问控制和数据保护模式
- 🏢 **可扩展架构** ：带监控的生产就绪 RAG 系统

## 🎯 企业级 RAG 架构

### 核心企业组件
- **Microsoft Foundry** ：具备安全合规的托管企业 AI 平台
- **持久化 Agent** ：具备对话历史和上下文管理的有状态 Agent
- **向量存储管理** ：企业级文档索引和检索
- **身份集成** ：Azure AD 认证和基于角色的访问控制

### .NET 企业级优势
- **类型安全** ：针对 RAG 操作和数据结构的编译时验证
- **异步性能** ：非阻塞的文档处理与搜索操作
- **内存管理** ：针对大规模文档集合的高效资源利用
- **集成模式** ：原生 Azure 服务集成，支持依赖注入

## 🏗️ 技术架构

### 企业级 RAG 流程
```csharp
Document Upload → Security Validation → Vector Processing → Index Creation
                      ↓                    ↓                  ↓
User Query → Authentication → Semantic Search → Context Ranking → AI Response
```

### 核心 .NET 组件
- **Azure.AI.Agents.Persistent** ：具备状态持久化的企业 Agent 管理
- **Azure.Identity** ：集成认证，实现安全的 Azure 服务访问
- **Microsoft.Agents.AI.AzureAI** ：面向 Azure 的 Agent 框架实现
- **System.Linq.Async** ：高性能异步 LINQ 操作

## 🔧 企业功能与优势

### 安全与合规
- **Azure AD 集成** ：企业身份管理与认证
- **基于角色的访问** ：对文档访问和操作的细粒度权限控制
- **数据保护** ：敏感文档的传输中和静态加密
- **审计日志** ：满足合规需求的全面活动追踪

### 性能与可扩展性
- **连接池** ：高效的 Azure 服务连接管理
- **异步处理** ：支持高吞吐量场景的非阻塞操作
- **缓存策略** ：针对频繁访问文档的智能缓存
- **负载均衡** ：适合大规模部署的分布式处理

### 管理与监控
- **健康检查** ：RAG 系统组件的内建监控
- **性能指标** ：搜索质量及响应时间的详细分析
- **错误处理** ：全面异常管理及重试策略
- **配置管理** ：针对不同环境的设置及验证

## ⚙️ 先决条件与设置

 **开发环境：** 
- .NET 9.0 SDK 或更高版本
- Visual Studio 2022 或带 C# 扩展的 VS Code
- 具备 AI Foundry 访问权限的 Azure 订阅

 **必需的 NuGet 包：** 
```xml
<PackageReference Include="Microsoft.Extensions.AI" Version="9.9.0" />
<PackageReference Include="Azure.AI.Agents.Persistent" Version="1.2.0-beta.5" />
<PackageReference Include="Azure.Identity" Version="1.15.0" />
<PackageReference Include="System.Linq.Async" Version="6.0.3" />
<PackageReference Include="DotNetEnv" Version="3.1.1" />
```

 **Azure 身份验证设置：** 
```bash
# 安装 Azure CLI 并进行身份验证
az login
az account set --subscription "your-subscription-id"
```

 **环境配置（.env 文件）：** 
```text
# Microsoft Foundry configuration (automatically handled via Azure CLI)
# Ensure you're authenticated to the correct Azure subscription
```

## 📊 企业级 RAG 模式

### 文档管理模式
- **批量上传** ：高效处理大规模文档集合
- **增量更新** ：实时添加和修改文档
- **版本控制** ：文档版本管理与变更追踪
- **元数据管理** ：丰富的文档属性及分类体系

### 搜索与检索模式
- **混合搜索** ：结合语义和关键字搜索以获得最佳结果
- **分面搜索** ：多维度过滤和分类
- **相关性调优** ：针对特定领域需求的自定义评分算法
- **结果排名** ：融合业务逻辑的高级排序

### 安全模式
- **文档级安全** ：每个文档的细粒度访问控制
- **数据分类** ：自动敏感度标签与保护
- **审计轨迹** ：全面记录所有 RAG 操作
- **隐私保护** ：个人身份信息检测与脱敏功能

## 🔒 企业安全功能

### 认证与授权
```csharp
// Azure AD integrated authentication
var credential = new AzureCliCredential();
var agentsClient = new PersistentAgentsClient(endpoint, credential);

// Role-based access validation
if (!await ValidateUserPermissions(user, documentId))
{
    throw new UnauthorizedAccessException("Insufficient permissions");
}
```

### 数据保护
- **加密** ：文档和搜索索引的端到端加密
- **访问控制** ：与 Azure AD 集成，管理用户和组权限
- **数据驻留** ：地理数据位置控制以符合合规要求
- **备份与恢复** ：自动化备份与灾难恢复能力

## 📈 性能优化

### 异步处理模式
```csharp
// Efficient async document processing
await foreach (var document in documentStream.AsAsyncEnumerable())
{
    await ProcessDocumentAsync(document, cancellationToken);
}
```

### 内存管理
- **流式处理** ：处理大型文档无内存溢出问题
- **资源池化** ：高效复用昂贵资源
- **垃圾回收** ：优化内存分配模式
- **连接管理** ：合理管理 Azure 服务连接生命周期

### 缓存策略
- **查询缓存** ：缓存频繁执行的搜索
- **文档缓存** ：对热点文档的内存缓存
- **索引缓存** ：优化向量索引缓存
- **结果缓存** ：智能缓存生成的响应

## 📊 企业应用场景

### 知识管理
- **企业维基** ：跨公司知识库的智能搜索
- **政策与流程** ：自动化合规与流程指导
- **培训材料** ：智能学习与发展辅助
- **研究数据库** ：学术和研究论文分析系统

### 客户支持
- **支持知识库** ：自动化客户服务响应
- **产品文档** ：智能产品信息检索
- **故障排除指南** ：具备上下文的问题解决助手
- **FAQ 系统** ：从文档集合动态生成常见问答

### 监管合规
- **法律文档分析** ：合同及法律文档智能处理
- **合规监控** ：自动化法规合规检测
- **风险评估** ：基于文档的风险分析与报告
- **审计支持** ：智能文档发现，助力审计

## 🚀 生产部署

### 监控与可观察性
- **Application Insights** ：详尽的遥测和性能监控
- **自定义指标** ：业务关键绩效指标跟踪与告警
- **分布式追踪** ：跨服务的端到端请求跟踪
- **健康仪表板** ：实时系统健康和性能可视化

### 可扩展性与可靠性
- **自动扩展** ：基于负载和性能指标自动扩展
- **高可用性** ：多区域部署与容灾切换能力
- **负载测试** ：企业负载条件下的性能验证
- **灾难恢复** ：自动化备份和恢复流程

准备好构建能大规模处理敏感文档的企业级 RAG 系统了吗？让我们一起为企业设计智能知识系统吧！🏢📖✨

### 代码单元格 2

阅读提示：跟踪本单元格读取的变量、修改的状态以及返回值。按原顺序执行，确认依赖的前序变量已经存在。

```csharp
#r "nuget: Microsoft.Extensions.AI, 9.9.1"
```

### 代码单元格 3

阅读提示：跟踪本单元格读取的变量、修改的状态以及返回值。按原顺序执行，确认依赖的前序变量已经存在。

```csharp
#r "nuget: Azure.AI.Agents.Persistent, 1.2.0-beta.5"
#r "nuget: Azure.Identity, 1.15.0"
#r "nuget: System.Linq.Async, 6.0.3"
```

### 代码单元格 5

阅读提示：跟踪本单元格读取的变量、修改的状态以及返回值。按原顺序执行，确认依赖的前序变量已经存在。

```csharp
#r "nuget: Microsoft.Agents.AI.AzureAI, 1.0.0-preview.251001.3"
```

### 代码单元格 6

阅读提示：跟踪本单元格读取的变量、修改的状态以及返回值。按原顺序执行，确认依赖的前序变量已经存在。

```csharp
#r "nuget: Microsoft.Agents.AI, 1.0.0-preview.251001.3"
```

### 代码单元格 7

阅读提示：跟踪本单元格读取的变量、修改的状态以及返回值。按原顺序执行，确认依赖的前序变量已经存在。

```csharp
#r "nuget: DotNetEnv, 3.1.1"
```

### 代码单元格 8

阅读提示：跟踪本单元格读取的变量、修改的状态以及返回值。按原顺序执行，确认依赖的前序变量已经存在。

```csharp
using System;
using System.Linq;
using Azure.AI.Agents.Persistent;
using Azure.Identity;
using Microsoft.Agents.AI;
```

### 代码单元格 9

阅读提示：跟踪本单元格读取的变量、修改的状态以及返回值。按原顺序执行，确认依赖的前序变量已经存在。

```csharp
using DotNetEnv;
```

### 代码单元格 10

阅读提示：跟踪本单元格读取的变量、修改的状态以及返回值。按原顺序执行，确认依赖的前序变量已经存在。

```csharp
Env.Load("../../../.env");
```

### 代码单元格 11

阅读提示：跟踪本单元格读取的变量、修改的状态以及返回值。按原顺序执行，确认依赖的前序变量已经存在。

```csharp
var azure_foundry_endpoint = Environment.GetEnvironmentVariable("AZURE_AI_PROJECT_ENDPOINT") ?? throw new InvalidOperationException("AZURE_AI_PROJECT_ENDPOINT is not set.");
var azure_foundry_model_id = Environment.GetEnvironmentVariable("AZURE_AI_MODEL_DEPLOYMENT_NAME") ?? "gpt-5-mini";
```

### 代码单元格 12

阅读提示：跟踪本单元格读取的变量、修改的状态以及返回值。按原顺序执行，确认依赖的前序变量已经存在。

```csharp
string pdfPath = "./document.md";
```

### 代码单元格 13

阅读提示：跟踪本单元格读取的变量、修改的状态以及返回值。按原顺序执行，确认依赖的前序变量已经存在。

```csharp
using System.IO;

async Task<Stream> OpenImageStreamAsync(string path)
{
	return await Task.Run(() => File.OpenRead(path));
}

var pdfStream = await OpenImageStreamAsync(pdfPath);
```

### 代码单元格 14

阅读提示：跟踪本单元格读取的变量、修改的状态以及返回值。按原顺序执行，确认依赖的前序变量已经存在。

```csharp
var persistentAgentsClient = new PersistentAgentsClient(azure_foundry_endpoint, new AzureCliCredential());
```

### 代码单元格 15

阅读提示：跟踪本单元格读取的变量、修改的状态以及返回值。按原顺序执行，确认依赖的前序变量已经存在。

```csharp
PersistentAgentFileInfo fileInfo = await persistentAgentsClient.Files.UploadFileAsync(pdfStream, PersistentAgentFilePurpose.Agents, "demo.md");
```

### 代码单元格 16

阅读提示：跟踪本单元格读取的变量、修改的状态以及返回值。按原顺序执行，确认依赖的前序变量已经存在。

```csharp
PersistentAgentsVectorStore fileStore =
            await persistentAgentsClient.VectorStores.CreateVectorStoreAsync(
                [fileInfo.Id],
                metadata: new Dictionary<string, string>() { { "agentkey", bool.TrueString } });
```

### 代码单元格 17

行为约束：instructions 引导模型，不能替代执行器的权限验证、次数限制和结果检查。

```csharp
PersistentAgent agentModel = await persistentAgentsClient.Administration.CreateAgentAsync(
            azure_foundry_model_id,
            name: "DotNetRAGAgent",
            tools: [new FileSearchToolDefinition()],
            instructions: """
                You are an AI assistant designed to answer user questions using only the information retrieved from the provided document(s).

                - If a user's question cannot be answered using the retrieved context, **you must clearly respond**: 
                "I'm sorry, but the uploaded document does not contain the necessary information to answer that question."
                - Do not answer from general knowledge or reasoning. Do not make assumptions or generate hypothetical explanations.
                - Do not provide definitions, tutorials, or commentary that is not explicitly grounded in the content of the uploaded file(s).
                - If a user asks a question like "What is a Neural Network?", and this is not discussed in the uploaded document, respond as instructed above.
                - For questions that do have relevant content in the document (e.g., Contoso's travel insurance coverage), respond accurately, and cite the document explicitly.

                You must behave as if you have no external knowledge beyond what is retrieved from the uploaded document.
                """,
            toolResources: new()
            {
                FileSearch = new()
                {
                    VectorStoreIds = { fileStore.Id },
                }
            },
            metadata: new Dictionary<string, string>() { { "agentkey", bool.TrueString } });
```

### 代码单元格 18

阅读提示：跟踪本单元格读取的变量、修改的状态以及返回值。按原顺序执行，确认依赖的前序变量已经存在。

```csharp
AIAgent agent = await persistentAgentsClient.GetAIAgentAsync(agentModel.Id);
```

### 代码单元格 19

阅读提示：跟踪本单元格读取的变量、修改的状态以及返回值。按原顺序执行，确认依赖的前序变量已经存在。

```csharp
AgentThread thread = agent.GetNewThread();
```

### 代码单元格 20

阅读提示：跟踪本单元格读取的变量、修改的状态以及返回值。按原顺序执行，确认依赖的前序变量已经存在。

```csharp
Console.WriteLine(await agent.RunAsync("Can you explain Contoso's travel insurance coverage?", thread));
```

::: details 原文件保存的输出（不是本项目实测）

```text
Contoso's travel insurance coverage includes protection for medical emergencies, trip cancellations, and lost baggage. This ensures that travelers are supported in case of health-related issues during their trip, unforeseen cancellations, and the loss of their belongings while traveling【4:0†demo.md】.
```

:::


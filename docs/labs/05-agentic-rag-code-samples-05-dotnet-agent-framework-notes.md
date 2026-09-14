---
title: "05 · 05-dotnet-agent-framework"
outline: [2, 3]
---

# 05 · 05-dotnet-agent-framework

[返回：Agentic RAG](/lessons/rag.md) · [不可变原始文件](https://github.com/microsoft/ai-agents-for-beginners/blob/25b7985f3b2dc37a84f4a7387ccd3c9f0e5b1595/05-agentic-rag/code_samples/05-dotnet-agent-framework.md)

::: info 原课程补充材料
根据对应简体中文译本整理。原代码片段未进行云端验证。
:::

# 🔍 使用 Microsoft Foundry (.NET) 构建企业级 RAG

## 📋 学习目标

本笔记演示如何使用 Microsoft Foundry 中的 Microsoft Agent Framework 在 .NET 中构建企业级检索增强生成（RAG）系统。你将学习如何创建可投入生产的 Agent，这些 Agent 能够搜索文档并提供准确且具上下文感知的响应，同时具备企业级的安全性和可扩展性。

 **你将构建的企业级 RAG 功能：** 
- 📚 **文档智能** ：利用 Azure AI 服务进行高级文档处理
- 🔍 **语义搜索** ：具企业功能的高性能向量搜索
- 🛡️ **安全集成** ：基于角色的访问控制和数据保护模式
- 🏢 **可扩展架构** ：具监控功能的生产级 RAG 系统

## 🎯 企业级 RAG 架构

### 核心企业组件
- **Microsoft Foundry** ：具安全和合规性的托管企业 AI 平台
- **持久化 Agent** ：带有会话历史和上下文管理的有状态 Agent
- **向量存储管理** ：企业级文档索引和检索
- **身份集成** ：Azure AD 认证和基于角色的访问控制

### .NET 企业优势
- **类型安全** ：对 RAG 操作和数据结构的编译时验证
- **异步性能** ：非阻塞文档处理和搜索操作
- **内存管理** ：高效利用资源处理大型文档集合
- **集成模式** ：与 Azure 服务的原生集成及依赖注入

## 🏗️ 技术架构

### 企业级 RAG 流水线
```
Document Upload → Security Validation → Vector Processing → Index Creation
                      ↓                    ↓                  ↓
User Query → Authentication → Semantic Search → Context Ranking → AI Response
```

### 核心 .NET 组件
- **Azure.AI.Agents.Persistent** ：具状态持久化的企业 Agent 管理
- **Azure.Identity** ：集成认证保障 Azure 服务访问安全
- **Microsoft.Agents.AI.AzureAI** ：针对 Azure 优化的 Agent 框架实现
- **System.Linq.Async** ：高性能异步 LINQ 操作

## 🔧 企业功能与优势

### 安全与合规
- **Azure AD 集成** ：企业身份管理与认证
- **基于角色的访问** ：针对文档访问和操作的细粒度权限
- **数据保护** ：对敏感文档的静态和传输加密
- **审计日志** ：全面的活动跟踪以满足合规要求

### 性能与可扩展性
- **连接池** ：高效管理 Azure 服务连接
- **异步处理** ：非阻塞操作以支持高吞吐场景
- **缓存策略** ：智能缓存频繁访问的文档
- **负载均衡** ：分布式处理支持大规模部署

### 管理与监控
- **健康检查** ：内建监控 RAG 系统组件状态
- **性能指标** ：详尽分析搜索质量和响应时间
- **错误处理** ：全面异常管理及重试策略
- **配置管理** ：环境特定设置及验证

## ⚙️ 先决条件与设置

 **开发环境：** 
- .NET 9.0 SDK 或更高版本
- Visual Studio 2022 或安装 C# 扩展的 VS Code
- 拥有 Microsoft Foundry 访问权限的 Azure 订阅

 **必需的 NuGet 包：** 
```xml
<PackageReference Include="Microsoft.Extensions.AI" Version="9.9.0" />
<PackageReference Include="Azure.AI.Agents.Persistent" Version="1.2.0-beta.5" />
<PackageReference Include="Azure.Identity" Version="1.15.0" />
<PackageReference Include="System.Linq.Async" Version="6.0.3" />
<PackageReference Include="DotNetEnv" Version="3.1.1" />
```

 **Azure 认证设置：** 
```bash
# 安装 Azure CLI 并进行身份验证
az login
az account set --subscription "your-subscription-id"
```

 **环境配置：** 
* Microsoft Foundry 配置（通过 Azure CLI 自动处理）
* 确保你已认证到正确的 Azure 订阅

## 📊 企业 RAG 模式

### 文档管理模式
- **批量上传** ：高效处理大型文档集合
- **增量更新** ：实时添加和修改文档
- **版本控制** ：文档版本及变更跟踪
- **元数据管理** ：丰富的文档属性和分类体系

### 搜索与检索模式
- **混合搜索** ：结合语义与关键词搜索，实现最佳效果
- **分面搜索** ：多维过滤与分类
- **相关性调优** ：针对特定领域的自定义评分算法
- **结果排名** ：集成业务逻辑的高级排名

### 安全模式
- **文档级安全** ：针对单个文档的细粒度访问控制
- **数据分类** ：自动敏感度标注与保护
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
- **访问控制** ：与 Azure AD 集成的用户与组权限管理
- **数据驻留** ：符合法规要求的地理数据位置控制
- **备份与恢复** ：自动备份及灾难恢复功能

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
- **流式处理** ：处理大型文档时避免内存问题
- **资源池化** ：高效重用昂贵资源
- **垃圾回收** ：优化的内存分配模式
- **连接管理** ：合理的 Azure 服务连接生命周期管理

### 缓存策略
- **查询缓存** ：缓存频繁执行的搜索
- **文档缓存** ：内存中缓存热点文档
- **索引缓存** ：优化的向量索引缓存
- **结果缓存** ：智能缓存生成的响应

## 📊 企业使用场景

### 知识管理
- **企业维基** ：跨公司知识库的智能搜索
- **政策与流程** ：自动合规与流程指导
- **培训材料** ：智能学习与发展辅助
- **研究数据库** ：学术与研究论文分析系统

### 客户支持
- **支持知识库** ：自动化的客户服务响应
- **产品文档** ：智能产品信息检索
- **故障排除指南** ：上下文相关的问题解决辅助
- **FAQ 系统** ：从文档集合动态生成常见问题解答

### 法规合规
- **法律文档分析** ：合同和法律文档智能处理
- **合规监控** ：自动化法规合规检测
- **风险评估** ：基于文档的风险分析与报告
- **审计支持** ：智能文档发现助力审计

## 🚀 生产部署

### 监控与可观测性
- **Application Insights** ：详尽的遥测与性能监控
- **自定义指标** ：业务关键指标跟踪与告警
- **分布式追踪** ：跨服务的端到端请求跟踪
- **健康仪表盘** ：实时系统健康与性能可视化

### 可扩展性与可靠性
- **自动扩展** ：基于负载和性能指标的自动扩缩
- **高可用性** ：多区域部署及故障转移能力
- **负载测试** ：企业负载条件下的性能验证
- **灾难恢复** ：自动备份与恢复流程

准备好构建能在大规模处理敏感文档的企业级 RAG 系统了吗？让我们一起为企业设计智能知识系统吧！🏢📖✨

## 代码实现

本课的完整示例代码可在 `05-dotnet-agent-framework.cs` 中找到。

运行示例：

```bash
# 使脚本可执行（Linux/macOS）
chmod +x 05-dotnet-agent-framework.cs

# 运行 .NET 单文件应用程序
./05-dotnet-agent-framework.cs
```

或直接使用 `dotnet run`：

```bash
dotnet run 05-dotnet-agent-framework.cs
```

代码演示了：

1. **包安装** ：安装 Azure AI Agents 所需的 NuGet 包
2. **环境配置** ：加载 Microsoft Foundry 终结点和模型设置
3. **文档上传** ：上传文档进行 RAG 处理
4. **向量存储创建** ：为语义搜索创建向量存储
5. **Agent 配置** ：设置具备文件搜索能力的 AI Agent
6. **查询执行** ：针对上传文档执行查询

---
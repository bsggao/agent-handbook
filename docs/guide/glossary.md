---
title: 中英术语表
description: 中英术语表 · AI Agent 中文学习指南
---

# 中英术语表

可输入中文或英文筛选。英文缩写、全称与中文定义也进入全站搜索索引。正文统一使用 Agent，首次出现给出中文名称；同一词在不同框架中的 API 名称可能不同。

<Glossary />

## 全部术语与定义

以下静态词条便于全站搜索、直接链接和禁用脚本时阅读。

### 智能体 · Agent

在给定环境中，围绕目标选择行动并利用反馈继续执行的系统；本课程重点是由大语言模型参与决策的实现。 [相关课程](/lessons/introduction.md)。

### 大语言模型 · LLM · Large Language Model

根据输入序列生成输出的模型。它可生成文字或工具请求；外部程序负责实际执行动作。 [相关课程](/lessons/introduction.md)。

### 词元 · Token

模型处理文本的计量单位，可能是字、词的一部分或符号；字符数不等于 Token 数。 [相关课程](/lessons/context.md)。

### 提示词 · Prompt

提交给模型的指令或内容。提示词影响输出，但不能替代程序权限与校验。 [相关课程](/lessons/design-patterns.md)。

### 系统指令 · System instruction

描述模型角色、任务范围和行为要求的高优先级指令。它仍不能保证任何输入下都严格遵循。 [相关课程](/lessons/trust.md)。

### 工具调用 · Tool calling / Function calling

模型输出工具名称和参数，应用验证后执行相应函数，再把工具结果交回模型的机制。 [相关课程](/lessons/tools.md)。

### 数据结构约束 · Schema / JSON Schema

描述字段名称、类型、必填项和允许值的结构规范；需配合运行时验证。 [相关课程](/lessons/tools.md)。

### 检索增强生成 · RAG · Retrieval-Augmented Generation

先检索相关资料，再将证据交给模型生成回答；能附引用，但不能保证回答一定正确。 [相关课程](/lessons/rag.md)。

### 智能体式检索增强生成 · Agentic RAG

Agent 根据已有证据选择查询与检索工具，并在预算内检查、改写或追加检索。 [相关课程](/lessons/rag.md)。

### 向量嵌入 · Embedding

把文本等内容映射为数值向量，用于相似性计算。相近向量不等于事实正确或存在业务关联。 [相关课程](/lessons/rag.md)。

### 向量数据库 · Vector database

存储向量及元数据并执行相似性检索的系统；通常还需要文档 ID、权限过滤与版本管理。 [相关课程](/lessons/rag.md)。

### 文本分块 · Chunking

将长文档拆成可检索片段，尽量保留语义完整性与来源。块大小影响召回和上下文成本。 [相关课程](/lessons/rag.md)。

### 重排序 · Reranking

对初步召回的候选证据再次评分排序；重排不会修复来源本身错误。 [相关课程](/lessons/reflection.md)。

### 依据关联 · Grounding

将回答与外部可核查证据关联，避免把无来源的生成内容当成事实。 [相关课程](/lessons/rag.md)。

### 上下文窗口 · Context window

一次模型调用可处理的信息范围，包含指令、消息、工具定义和证据，并需预留输出空间。 [相关课程](/lessons/context.md)。

### 上下文工程 · Context engineering

设计如何选择、检索、压缩、隔离和检查模型在一次调用中接收到的信息。 [相关课程](/lessons/context.md)。

### 工作便签 · Scratchpad

应用可读写的任务笔记或中间状态；不是对模型私有内部推理的可靠记录。 [相关课程](/lessons/context.md)。

### 短期记忆 · Short-term memory / Session

会话中的近期消息与状态。复用同一会话对象才可连续对话，重启持久化需要额外设计。 [相关课程](/lessons/memory.md)。

### 长期记忆 · Long-term memory

跨会话保存并按需取回的信息，需具备用户隔离、来源、期限、纠正和删除机制。 [相关课程](/lessons/memory.md)。

### 情景记忆 · Episodic memory

记录过去任务、行动与结果，用于复用经验；不意味着重新训练了模型。 [相关课程](/lessons/memory.md)。

### 人工介入 · Human-in-the-loop / HITL

由人审核、补充、批准或停止流程。高风险动作应在执行前对具体对象和参数取得授权。 [相关课程](/lessons/trust.md)。

### 规划 · Planning

将目标拆分为子任务，确定依赖、资源和完成条件。生成计划并不等于执行已经成功。 [相关课程](/lessons/planning.md)。

### 反思 · Reflection / Metacognition

在工程中指根据输出、工具结果和反馈检查并调整策略；不能据此声称系统有自我意识。 [相关课程](/lessons/reflection.md)。

### 任务交接 · Handoff

把处理责任与必要上下文交给另一个专门角色；应明确输入、结果格式、错误和返回路径。 [相关课程](/lessons/multi-agent.md)。

### 编排 · Orchestration

安排各模型、工具与角色的执行顺序、依赖和失败处理的应用逻辑。 [相关课程](/lessons/multi-agent.md)。

### 模型上下文协议 · MCP · Model Context Protocol

定义宿主应用如何通过客户端连接服务器并使用工具、资源和提示等能力的开放协议。 [相关课程](/lessons/protocols.md)。

### 智能体间协议 · A2A · Agent-to-Agent

帮助独立 Agent 发现能力、交换任务状态和结果的协议；应用仍须实现身份与权限。 [相关课程](/lessons/protocols.md)。

### 智能体能力卡 · Agent Card

A2A 中描述 Agent 端点、能力、技能等信息的文档，不是无需核验的信任凭证。 [相关课程](/lessons/protocols.md)。

### 成果对象 · Artifact

任务产出的文本、文件或结构化结果，可独立于中间消息传递。 [相关课程](/lessons/protocols.md)。

### 自然语言网站接口 · NLWeb · Natural Language Web

为网站内容提供自然语言问答和发现能力的开放项目，常结合结构化网页数据与检索。 [相关课程](/lessons/protocols.md)。

### 可观测性 · Observability

通过日志、指标与调用链理解运行情况；观察应用事件不等于读取模型内部思考。 [相关课程](/lessons/production.md)。

### 调用链 · Trace

一次完整请求从入口到最终输出的关联执行记录。 [相关课程](/lessons/production.md)。

### 执行片段 · Span

调用链中的一段操作，例如一次模型调用或工具查询，记录时间、状态与必要属性。 [相关课程](/lessons/production.md)。

### 遥测标准 · OpenTelemetry / OTel

生成、收集和导出调用链、指标与日志的开放工具体系。 [相关课程](/lessons/production.md)。

### 评估 · Evaluation / Eval

依据明确任务标准检查结果和流程，可离线进行，也可在真实流量上监控。 [相关课程](/lessons/production.md)。

### 发布门槛 · Evaluation gate

新版本必须达到的最低评估要求；失败时阻止晋级，不靠好看的单个答案决定发布。 [相关课程](/lessons/deployment.md)。

### 提示注入 · Prompt injection

攻击者把改变目标或越权的指令混入输入或检索资料，试图影响模型行为。 [相关课程](/lessons/trust.md)。

### 最小权限 · Least privilege

给每个身份只授予当前任务所需资源与操作权限，并限定范围和时效。 [相关课程](/lessons/security.md)。

### 幂等 · Idempotency

同一逻辑请求重复执行不会重复产生副作用，常用请求 ID 与结果记录实现。 [相关课程](/lessons/deployment.md)。

### 背压 · Backpressure

下游处理不过来时限制上游并发或排队，避免越积越多的请求压垮服务。 [相关课程](/lessons/deployment.md)。

### 检查点 · Checkpoint

保存足以恢复流程的状态。恢复还需考虑外部动作是否已执行，防止重复写入。 [相关课程](/lessons/agent-framework.md)。

### 计算机使用智能体 · Computer Use Agent / CUA

观察界面并通过浏览器或桌面操作完成任务的 Agent 系统。 [相关课程](/lessons/browser-use.md)。

### 浏览器调试协议 · CDP · Chrome DevTools Protocol

程序控制和检查 Chromium 浏览器的协议；远程调试端口具有敏感控制能力。 [相关课程](/lessons/browser-use.md)。

### 小型语言模型 · SLM · Small Language Model

相对资源需求较小的语言模型，适合部分设备端任务；能力与内存需求必须具体评测。 [相关课程](/lessons/local-agents.md)。

### 数字签名 · Digital signature / Ed25519

用私钥签名、用可信公钥验证消息来源与完整性的机制，不证明消息内容真实。 [相关课程](/lessons/security.md)。

### 规范 JSON 编码 · JCS · JSON Canonicalization Scheme

按统一规则把 JSON 转换为确定字节，以便不同实现签名和校验相同内容。 [相关课程](/lessons/security.md)。

### 密码学哈希 · Cryptographic hash / SHA-256

将输入映射到固定长度摘要，用于完整性关联。哈希不是加密，短或可枚举的原文仍可能被猜出。 [相关课程](/lessons/security.md)。

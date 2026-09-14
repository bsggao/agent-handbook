---
title: "多 Agent 协作"
description: "用清晰的角色、交接和汇总协作。"
course: "multi-agent"
prev: {"text": "规划模式", "link": "/lessons/planning"}
next: {"text": "元认知与反思", "link": "/lessons/reflection"}
---

# 多 Agent 协作

::: tip 本章目标
为协作设计角色、输入和结果契约，比较群聊、任务交接与多角色评审，并能解释协作的额外成本。
:::

前置：[规划](./planning.md)与[可信边界](./trust.md)。多个 Agent 可以使用同一个模型；“多”指独立的角色、上下文与工作责任，不必是不同厂商模型。

## 补充讲解：从一份退款申请看协作

订单角色知道是否签收，政策角色知道哪些条件允许退货，协调器把两者结合后生成处理方案。角色之间共享订单 ID 与必要事实，比把整个客户资料复制给每个角色更容易控制权限与成本。

![多 Agent 协作架构：协调器向订单、政策和审核角色分配任务，再汇总结果](/diagrams/multi-agent.svg)

*图：补充绘制。独立角色的结果可以并行取得；副作用仍由具有相应权限的执行器处理。*

<StepDemo kind="multi" />


[原课程视频：多 Agent 设计](https://youtu.be/V6HpE9hZEx0?si=A7K44uMCqgvLQVCa)


## 原课程精读：多 Agent 设计模式

一旦你开始参与一个涉及多个 Agent 的项目，你就需要考虑多 Agent 设计模式。然而，何时切换到多 Agent，以及它的优势是什么，可能并不立即清楚。

## 引言

在本课中，我们希望回答以下问题：

- 多 Agent 适用的场景有哪些？
- 使用多 Agent 相比单一 Agent 执行多任务的优势是什么？
- 实现多 Agent 设计模式的构建模块是什么？
- 我们如何获得多 Agent 之间相互作用的可视性？

## 学习目标

学习完本课后，你应该能够：

- 识别多 Agent 适用的场景
- 认识到多 Agent 相较于单一 Agent 的优势
- 理解多 Agent 设计模式的构建模块

大局观是什么？

*多 Agent 是一种设计模式，允许多个 Agent 协同工作以实现共同目标*。

该模式广泛应用于机器人技术、自动系统和分布式计算等多个领域。

## 多 Agent 适用的场景

那么哪些场景适合使用多 Agent？答案是，在很多情况下，特别是以下情况，使用多个 Agent 是有益的：

- **大工作负载** ：大工作负载可细分为更小任务分配给不同 Agent，从而实现并行处理和更快完成。例如大型数据处理任务。
- **复杂任务** ：复杂任务，如大工作量，可以拆分为更小子任务分配给不同 Agent，每个 Agent 专注任务的特定方面。比如自动驾驶汽车中，不同 Agent 分别管理导航、障碍检测和与其他车辆通信。
- **多样的专长** ：不同 Agent 具备不同的专长，比单一 Agent 能更有效处理任务的不同方面。一个典型例子是医疗保健，Agent 可分别管理诊断、治疗方案和病人监测。

## 使用多 Agent 相比单一 Agent 的优势

单一 Agent 系统适合简单任务，但对于更复杂的任务，使用多个 Agent 可带来多种优势：

- **专业化** ：每个 Agent 可专注于特定任务。单一 Agent 专业性不足，面对复杂任务时易混淆，可能会执行不适合自己的任务。
- **可扩展性** ：增加更多 Agent 比让单一 Agent 承担更多任务要更易实现系统扩展。
- **容错性** ：某个 Agent 失败时，其他 Agent 可继续运行，保障系统可靠性。

举个例子，帮用户预订旅游。单一 Agent 需负责航班查找、酒店和租车预订的所有环节。为实现这一点，Agent 需配备处理所有这些任务的工具，导致系统复杂且难以维护和扩展。而多 Agent 系统中，不同 Agent 分别专注于航班查找、酒店和租车预订，使系统更加模块化、易维护且可扩展。

这可以类比为普通旅游局与特许经营旅游局的对比。普通旅游局由单一 Agent 处理所有预订环节，而特许经营局由不同 Agent 负责不同部分。

## 实现多 Agent 设计模式的构建模块

在实施多 Agent 设计模式之前，需要了解构成该模式的构建模块。

以为用户预订旅游为例，构建模块包括：

- **Agent 通信** ：负责航班、酒店和租车预订的 Agent 需要交流并共享用户偏好与限制信息。需要决定通信协议和方式。具体来说，航班 Agent 需与酒店 Agent 通讯，确保酒店预订时间与航班一致。即需要决定*哪些 Agent 共享信息以及如何共享*。
- **协调机制** ：Agent 需协调行动以满足用户偏好和约束。例如用户偏好靠近机场的酒店，而约束是租车只在机场提供，酒店预订 Agent 需与租车 Agent 协调，确保满足这些条件。需决定*Agent 如何协调行动*。
- **Agent 架构** ：Agent 需具备内部结构以作出决策并从与用户的交互中学习。比如航班 Agent 需具备决策能力，推荐合适航班。需决定*Agent 如何决策及学习*。例如航班 Agent 可使用机器学习模型，根据用户过往偏好推荐航班。
- **多 Agent 交互可视性** ：需能查看多 Agent 间的交互情况。需要工具与技术跟踪 Agent 活动与交互。形式包括日志监控工具、可视化工具和性能指标。
- **多 Agent 模式** ：多 Agent 系统可采用集中式、分散式和混合架构模式。需选定最适合用例的模式。
- **人机交互** ：在多数情况下，人类在环中，需要指导 Agent 何时请求人工介入。例如用户要求特定酒店或航班未被 Agent 推荐，或预订前需确认等。

## 多 Agent 交互的可视性

了解多 Agent 间的交互情况十分重要。该可视性对调试、优化和保证系统整体有效性至关重要。为此，需配备跟踪 Agent 活动和交互的工具和技术，形式包括日志记录和监控工具、可视化工具及性能指标。

例如预订旅游时，可设仪表盘显示每个 Agent 状态、用户偏好与约束、Agent 间的交互。仪表盘可显示用户出行日期、航班 Agent 推荐的航班、酒店 Agent 推荐的酒店、租车 Agent 推荐的车辆。如此一来，可清晰了解 Agent 间的交互及用户偏好和约束是否满足。

让我们更详细地看看这些方面。

- **日志和监控工具** ：需记录每个 Agent 执行的动作。日志条目可包括执行动作的 Agent、动作内容、动作时间及结果。此信息可用于调试、优化等。

- **可视化工具** ：帮助直观展示 Agent 间的交互。例如绘制 Agent 间信息流图，有助识别瓶颈、低效及其他问题。

- **性能指标** ：用于跟踪多 Agent 系统有效性。例如记录完成任务所用时间、单位时间内完成任务数量、Agent 推荐准确率等。此信息有助识别改进空间并优化系统。

## 多 Agent 模式

让我们探讨一些创建多 Agent 应用的具体模式，以下是一些值得考虑的有趣模式：

### 群聊

当你想创建一个支持多个 Agent 相互通信的群聊应用时，这种模式非常有用。典型用例包括团队协作、客户支持和社交网络。

在该模式中，每个 Agent 代表群聊中的一个用户，Agent 间通过消息协议交换信息。Agent 可以发送群聊消息、接收消息并回应其他 Agent。

该模式可以通过集中式架构实现，所有消息通过中央服务器转发，也可通过分散式架构直接交换消息。

![Group chat](/upstream-assets/translated_images/zh-CN/multi-agent-group-chat.ec10f4cde556babd.webp)

*图：Group chat。来源：Microsoft AI Agents for Beginners，MIT。*

### 工作交接

当你想创建一个支持多个 Agent 间交接任务的应用时，这种模式非常有用。

典型用例包括客户支持、任务管理和工作流程自动化。

在该模式中，每个 Agent 代表一个任务或工作流程中的某个步骤，Agent 可根据预定规则将任务交接给其他 Agent。

![Hand off](/upstream-assets/translated_images/zh-CN/multi-agent-hand-off.4c5fb00ba6f8750a.webp)

*图：Hand off。来源：Microsoft AI Agents for Beginners，MIT。*

### 协同过滤

当你想创建一个多 Agent 协作向用户推荐内容的应用时，这种模式非常有用。

多 Agent 协作的理由在于，每个 Agent 具备不同专长，可以不同方式为推荐过程做出贡献。

以用户想获得股票市场最佳买入建议为例。

- **行业专家** ：一个 Agent 可以是特定行业专家。
- **技术分析** ：另一个 Agent 擅长技术分析。
- **基本面分析** ：还有一个 Agent 擅长基本面分析。通过协作，这些 Agent 可为用户提供更全面的建议。

![Recommendation](/upstream-assets/translated_images/zh-CN/multi-agent-filtering.d959cb129dc9f608.webp)

*图：Recommendation。来源：Microsoft AI Agents for Beginners，MIT。*

## 场景：退款流程

考虑客户申请产品退款的场景，可能涉及许多 Agent，我们将其分为专门处理退款流程的 Agent 和可以用于其他业务部分的通用 Agent。

 **专门处理退款流程的 Agent** ：

可能涉及的退款流程 Agent 包括：

- **客户 Agent** ：代表客户，负责发起退款流程。
- **卖家 Agent** ：代表卖家，负责处理退款。
- **支付 Agent** ：代表支付流程，负责退还客户款项。
- **解决方案 Agent** ：负责解决退款过程中出现的任何问题。
- **合规 Agent** ：确保退款流程符合相关法规和政策。

 **通用 Agent** ：

这些 Agent 可被你业务的其他部分使用。

- **运输 Agent** ：代表运输流程，负责将产品退回给卖家。该 Agent 可用于退款流程，也可用于类似购买产品的运输流程。
- **反馈 Agent** ：负责收集客户反馈，反馈可在任何时间段收集，而不仅限于退款流程。
- **升级 Agent** ：负责将问题升级至更高支持层级，适用于任何需要问题升级的流程。
- **通知 Agent** ：负责在退款流程的各个阶段向客户发送通知。
- **分析 Agent** ：负责分析与退款流程相关的数据。
- **审计 Agent** ：负责审计退款流程，确保其按规范执行。
- **报告 Agent** ：负责生成退款流程的相关报告。
- **知识 Agent** ：负责维护与退款流程相关的知识库，可能涵盖退款及业务其他部分知识。
- **安全 Agent** ：负责保障退款流程的安全。
- **质量 Agent** ：负责确保退款流程的质量。

前文列举相当多的 Agent，涵盖退款流程具体 Agent 及可用于业务其他部分的通用 Agent。希望这能帮助你理解如何确定多 Agent 系统中使用哪些 Agent。

## 练习

设计一个客户支持流程的多 Agent 系统。识别该流程涉及的 Agent、它们的角色和职责，以及它们如何相互协作。考虑既有客户支持流程专用 Agent，也有可用于业务其他部分的通用 Agent。


> 在阅读以下解决方案之前先思考一下，你可能需要的 Agent 比你想象的要多。

> 提示：考虑客户支持流程的不同阶段，并且考虑任何系统所需的 Agent 数量。

## 解决方案

[解决方案](/labs/08-multi-agent-solution-solution-notes.md)

## 知识测试

### 问题 1

哪种情境最适合多 Agent 系统？

- [ ] A1：一个支持机器人使用一个知识库和一小套工具回答常见问题。
- [ ] A2：退款工作流需要独立的欺诈、支付和合规角色，每个角色都有自己的工具，且结果必须协调一致。
- [ ] A3：同一个简单的分类请求每小时成千上万次地到达。

### 问题 2

什么时候单个 Agent 通常是更好的选择？

- [ ] A1：任务可以通过一套指令和工具完成，无需专业交接。
- [ ] A2：Agent 可以访问超过一个的工具。
- [ ] A3：工作流程需要不同权限和独立审计跟踪的独立角色。

[解决方案测验](/labs/08-multi-agent-solution-solution-quiz-notes.md)

## 总结

在本课中，我们了解了多 Agent 设计模式，包括多 Agent 适用的场景、使用多 Agent 相比单一 Agent 的优势、实现多 Agent 设计模式的构建模块，以及如何洞察多个 Agent 之间的交互。

## 额外资源

- [Microsoft Agent Framework 文档](https://learn.microsoft.com/azure/ai-services/agents/overview)
- [Agent 设计模式](https://www.analyticsvidhya.com/blog/2024/10/agentic-design-patterns/)

## 原课程案例与代码实操

正文保留退款流程、专用角色与通用角色的分工，以及原知识测验和答案链接。角色清单是设计空间，不是要求把每个函数都包装成 Agent；若单一规则函数就能验证退款资格，不必再花一次模型调用。

主 Python Notebook 用 `WorkflowBuilder(start_executor=...)` 和 `add_edge()` 把专门角色串起来，处理旅行规划。下方同时保留基础、顺序、并发和条件工作流的 Python / .NET 材料。按准备篇配置 Foundry 后在 Jupyter 执行；带 Bing grounding 的条件示例需要额外连接，旧 Azure 客户端代码需单独核对版本。

 **读代码重点：** 起始执行器接收用户输入；边决定消息流向；`AgentResponseUpdate` 表示流式输出事件，`author_name` 表示来源角色。打印不同角色的文字只表示多角色输出，不足以证明通信已经跨进程或使用了 A2A 协议。

## 输出契约比角色提示更重要

让每个角色返回 `task_id`、`status`、`facts`、`sources` 和 `error`。协调器先验证状态和来源，再总结。某角色超时应返回部分完成或升级处理，不能把“没有反对意见”当作审核通过。

| 模式 | 适用任务 | 容易出错的地方 |
| --- | --- | --- |
| 顺序 / 交接 | 后一步需要前一步结果 | 丢失约束、交接来回循环 |
| 并发汇总 | 相互独立的信息收集 | 缺少汇合规则、最慢角色拖住全部 |
| 群聊评审 | 需要多角度讨论的开放任务 | 发言冗长、重复、无人负责结束 |

多 Agent 不会自动更准确、更快或更容错。它可能把同一模型的偏差复制多份；并发也可能触发服务限额。用评估比较单 Agent 和多 Agent 的成功率、延迟与成本，再决定是否增加角色。

## 自测与扩展实践

 **练习：** 把模拟演示切换成“角色查询超时”，走到最后一步。协调器为什么没有给出最终退款结论？

::: details 答案与参考实现
订单事实不足以推导退款资格，还缺政策验证。程序可使用 `if any(r.status != "ok" for r in results): return partial_result`，在返回中列出已核实事实与未核实事项。重试也应有次数限制。原知识测验第 1 题应选 A2，第 2 题应选 A1：选择多角色是因为独立职责和协调要求，而不是调用量大或工具超过一个。
:::

本章让职责与协作可观察。下一章继续问：系统如何发现自己给出的结果不够好，并改变下一轮策略？


## 原课程代码与补充材料

以下是本章实际源文件对应的阅读页。Notebook 已分解为说明、代码及原文件输出；云端示例未进行联网端到端验证。正文中的片段用于解释，运行时使用完整 Notebook 和准备篇的固定依赖。

- [08-dotnet-agent-framework.cs](/labs/08-multi-agent-code-samples-08-dotnet-agent-framework-csharp.md)
- [08-dotnet-agent-framework.md](/labs/08-multi-agent-code-samples-08-dotnet-agent-framework-notes.md)
- [08-python-agent-framework.ipynb](/labs/08-multi-agent-code-samples-08-python-agent-framework-notebook.md)
- [solution-quiz.md](/labs/08-multi-agent-solution-solution-quiz-notes.md)
- [solution.md](/labs/08-multi-agent-solution-solution-notes.md)
- [README.md](/labs/08-multi-agent-code-samples-workflows-agent-framework-readme-notes.md)
- [02.python-agent-framework-workflow-ghmodel-sequential.ipynb](/labs/08-multi-agent-code-samples-workflows-agent-framework-python-02-python-agent-framework-workflow-ghmodel-sequential-notebook.md)
- [03.python-agent-framework-workflow-ghmodel-concurrent.ipynb](/labs/08-multi-agent-code-samples-workflows-agent-framework-python-03-python-agent-framework-workflow-ghmodel-concurrent-notebook.md)
- [01.python-agent-framework-workflow-ghmodel-basic.ipynb](/labs/08-multi-agent-code-samples-workflows-agent-framework-python-01-python-agent-framework-workflow-ghmodel-basic-notebook.md)
- [04.python-agent-framework-workflow-aifoundry-condition.ipynb](/labs/08-multi-agent-code-samples-workflows-agent-framework-python-04-python-agent-framework-workflow-aifoundry-condition-notebook.md)
- [03.dotnet-agent-framework-workflow-ghmodel-concurrent.ipynb](/labs/08-multi-agent-code-samples-workflows-agent-framework-dotnet-03-dotnet-agent-framework-workflow-ghmodel-concurrent-notebook.md)
- [02.dotnet-agent-framework-workflow-ghmodel-sequential.cs](/labs/08-multi-agent-code-samples-workflows-agent-framework-dotnet-02-dotnet-agent-framework-workflow-ghmodel-sequential-csharp.md)
- [04.dotnet-agent-framework-workflow-aifoundry-condition.cs](/labs/08-multi-agent-code-samples-workflows-agent-framework-dotnet-04-dotnet-agent-framework-workflow-aifoundry-condition-csharp.md)
- [04.dotnet-agent-framework-workflow-aifoundry-condition.ipynb](/labs/08-multi-agent-code-samples-workflows-agent-framework-dotnet-04-dotnet-agent-framework-workflow-aifoundry-condition-notebook.md)
- [03.dotnet-agent-framework-workflow-ghmodel-concurrent.cs](/labs/08-multi-agent-code-samples-workflows-agent-framework-dotnet-03-dotnet-agent-framework-workflow-ghmodel-concurrent-csharp.md)
- [01.dotnet-agent-framework-workflow-ghmodel-basic.cs](/labs/08-multi-agent-code-samples-workflows-agent-framework-dotnet-01-dotnet-agent-framework-workflow-ghmodel-basic-csharp.md)
- [01.dotnet-agent-framework-workflow-ghmodel-basic.ipynb](/labs/08-multi-agent-code-samples-workflows-agent-framework-dotnet-01-dotnet-agent-framework-workflow-ghmodel-basic-notebook.md)
- [01.dotnet-agent-framework-workflow-ghmodel-basic.md](/labs/08-multi-agent-code-samples-workflows-agent-framework-dotnet-01-dotnet-agent-framework-workflow-ghmodel-basic-notes.md)
- [02.dotnet-agent-framework-workflow-ghmodel-sequential.ipynb](/labs/08-multi-agent-code-samples-workflows-agent-framework-dotnet-02-dotnet-agent-framework-workflow-ghmodel-sequential-notebook.md)
- [03.dotnet-agent-framework-workflow-ghmodel-concurrent.md](/labs/08-multi-agent-code-samples-workflows-agent-framework-dotnet-03-dotnet-agent-framework-workflow-ghmodel-concurrent-notes.md)
- [02.dotnet-agent-framework-workflow-ghmodel-sequential.md](/labs/08-multi-agent-code-samples-workflows-agent-framework-dotnet-02-dotnet-agent-framework-workflow-ghmodel-sequential-notes.md)
- [04.dotnet-agent-framework-workflow-aifoundry-condition.md](/labs/08-multi-agent-code-samples-workflows-agent-framework-dotnet-04-dotnet-agent-framework-workflow-aifoundry-condition-notes.md)

## 本章来源

基于 [英文原文](https://github.com/microsoft/ai-agents-for-beginners/blob/25b7985f3b2dc37a84f4a7387ccd3c9f0e5b1595/08-multi-agent/README.md) 与 [简体中文翻译](https://github.com/microsoft/ai-agents-for-beginners/blob/25b7985f3b2dc37a84f4a7387ccd3c9f0e5b1595/translations/zh-CN/08-multi-agent/README.md) 整理，原作者为 Microsoft 与开源贡献者，采用 MIT 许可证。本页标明“补充讲解”与“扩展实践”的内容为本项目新增。

来源提交：`25b7985f3b2d` · 获取日期：2026-09-14。参见[版本校订记录](/guide/sources.md)。

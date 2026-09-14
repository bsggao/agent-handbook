---
title: "AI Agent 入门与应用场景"
description: "从一个旅行助手理解 Agent 的工作方式。"
course: "introduction"
prev: {"text": "环境配置与学习准备", "link": "/lessons/setup"}
next: {"text": "探索 Agent 框架", "link": "/lessons/frameworks"}
---

# AI Agent 入门与应用场景

::: tip 本章目标
理解 Agent、模型与应用程序之间的关系；能画出带退出条件的执行循环，并说明一个旅行助手可以做什么、不应擅自做什么。
:::

前置：[环境配置与学习准备](./setup.md)。如果“模型”对你还是一个抽象词，先记住：大语言模型（Large Language Model，LLM）根据输入内容生成后续输出，可以输出文字，也可以按约定输出工具调用请求。

## 补充讲解：从“给我建议”到“替我完成任务”

你说：“我想去温暖、有海滩的地方，帮我找一个目的地。”普通文本模型可能根据已有知识推荐城市，但不知道旅行社今天还有哪些名额。一个 Agent 系统可以先查询目的地列表，再检查名额，最后提出有证据的建议。

这里可以把模型类比为“负责选下一步的协调员”，但这个类比只帮助理解分工：模型没有人类的意图或责任主体身份；它生成的请求仍可能错误，程序必须验证。

| 部分 | 输入 | 处理与输出 | 边界 |
| --- | --- | --- | --- |
| 模型 | 用户目标、工具说明、已知结果 | 生成回答或结构化调用请求 | 无法凭文字直接修改订票系统 |
| 应用执行器 | 工具名称与参数 | 验证后调用真正的 Python 函数或 API | 使用程序授予的权限，执行失败也要记录 |
| 工具 | 已验证参数 | 返回列表、状态或操作结果 | 查询能力不等于预订权限 |
| 状态管理 | 消息、调用 ID、尝试次数 | 组织下一次输入 | 不应无限累积、不应跨用户串用 |

![Agent 执行循环：检查预算，调用模型，验证工具请求，执行或失败，满足目标或超限时退出](/diagrams/agent-loop.svg)

*图：本项目补充绘制。模型只提出请求；循环、执行权限和退出条件由应用控制。*

“工具失败后再试一次”和“永远重试直到成功”是不同的设计。记录 `max_steps`、超时和终止状态，才能让系统在现实的不确定性中停下来。


[原课程视频：Intro to AI Agents](https://youtu.be/3zgm60bXmQk?si=QA4CW2-cmul5kk3D)


## 原课程精读：AI Agent 及 Agent 使用案例简介

欢迎来到 **AI Agent 初学者** 课程！本课程为你提供基础知识和真实工作代码，助你从零开始构建 AI Agent。

来 [Azure AI Discord 社区](https://discord.gg/kzRShWzttr) 打个招呼吧——那里聚集了许多学习者和 AI 构建者，他们乐于解答你的问题。

在开始构建之前，让我们先确保真正理解 AI Agent*是什么*，以及在何时使用它才合理。

---

## 介绍

本课将涵盖：

- 什么是 AI Agent 以及存在的不同类型
- AI Agent 最适合的任务类型
- 设计 Agent 解决方案时你将使用的核心构建模块

## 学习目标

本课结束后，你应能：

- 说明什么是 AI Agent 以及它与普通 AI 解决方案的区别
- 了解何时应使用 AI Agent（何时不应使用）
- 勾勒出真实世界问题的基础 Agent 解决方案设计

---

## 定义 AI Agent 及 AI Agent 类型

### 什么是 AI Agent？

这里有一个简单的理解方式：

> **AI Agent 是让大语言模型（LLM）真正*做事*的系统——通过赋予它们工具和知识去作用于世界，而不仅仅是回应提示。** 

我们来细说一下：

- **系统** — AI Agent 不只是单一事物，而是多个部分协同工作的集合。每个 Agent 核心都有三部分：
  - **环境** — Agent 工作的空间。旅行预订 Agent 的环境即为预订平台本身。
  - **传感器** — Agent 感知当前环境状态的方式。旅行 Agent 可能会查看酒店房态或航班价格。
  - **执行器** — Agent 采取行动的方式。旅行 Agent 可能会预订房间、发送确认信息或取消预订。

![什么是 AI Agent？](/upstream-assets/translated_images/zh-CN/what-are-ai-agents.1ec8c4d548af601a.webp)

*图：什么是 AI Agent？。来源：Microsoft AI Agents for Beginners，MIT。*

- **大语言模型** — Agent 早在 LLM 出现之前就有了，但正是 LLM 使现代 Agent 变得强大。它们能理解自然语言、推理上下文，并将模糊的用户请求转化为具体行动计划。

- **执行动作** — 没有 Agent 系统，LLM 只是文字生成器。但在 Agent 系统中，LLM 可以*执行*步骤——搜索数据库、调用 API、发送消息。

- **工具访问** — Agent 可用的工具取决于（1）它运行的环境，（2）开发者赋予它的能力。旅行 Agent 可能能搜索航班但不能编辑客户记录——全部取决于你所连接的功能。

- **记忆与知识** — Agent 可包含短期记忆（当前对话）和长期记忆（客户数据库、过去的交互）。旅行 Agent 可能会“记住”你喜欢靠窗座位。

---

### 不同类型的 AI Agent

并非所有 Agent 都是同一类型。以下是主要类型的划分，以旅行预订 Agent 为例：

| **Agent 类型** | **功能描述** | **旅行 Agent 示例** |
|---|---|---|
| **简单反射 Agent** | 遵循硬编码规则——无记忆，无规划。 | 看到投诉邮件 → 转发给客服，仅此而已。 |
| **基于模型的反射 Agent** | 保持内部环境模型并随变化更新。 | 跟踪历史航班价格，标记突然涨价的航线。 |
| **目标驱动 Agent** | 有明确目标，逐步规划达成路径。 | 预订完整行程（航班、汽车、酒店），从当前位置到目的地。 |
| **效用驱动 Agent** | 不只是找到*一个*方案，而是权衡得失找到*最优*方案。 | 平衡成本与便利，找出最符合你偏好的行程。 |
| **学习型 Agent** | 通过反馈不断改进。 | 根据行程后的调查结果调整未来推荐。 |
| **分层 Agent** | 高级 Agent 拆分任务并委派给低级 Agent。 | “取消行程”请求拆分为取消航班、取消酒店、取消租车，各子 Agent 处理。 |
| **多 Agent 系统（MAS）** | 多个独立 Agent 协作（或竞争）。 | 协作：分别处理酒店、航班和娱乐的 Agent。竞争：多个 Agent 竞价填满酒店房间，争取最佳价格。 |

---

## 何时使用 AI Agent

只是因为*可以*用 AI Agent，不代表总是*应该*用。以下情况 Agent 特别适合：

![何时使用 AI Agent？](/upstream-assets/translated_images/zh-CN/when-to-use-ai-agents.54becb3bed74a479.webp)

*图：何时使用 AI Agent？。来源：Microsoft AI Agents for Beginners，MIT。*

- **开放式问题** — 需要动态探索解决路径，无法预编程具体步骤。
- **多步骤流程** — 任务需多轮使用各种工具，而非单次查找或生成。
- **持续改进** — 系统需基于用户反馈或环境信号不断变聪明。

我们将在本课程后续的 **构建可信赖 AI Agent** 课程深入讲解何时（及何时不）使用 AI Agent。

---

## Agent 解决方案基础

### Agent 开发

构建 Agent 的第一步是定义*它能做什么*——包括它的工具、动作和行为。

本课程采用 **Microsoft Foundry Agent Service** 作为主要平台。它支持：

- 来自 OpenAI、Mistral、Meta（Llama）等提供商的模型
- 来自 Tripadvisor 等提供商的授权数据
- 标准化的 OpenAPI 3.0 工具定义

### Agent 模式

你通过提示与 LLM 交流。对 Agent 来说，不能手工打造每个提示——Agent 需要跨多个步骤采取行动。此时， **Agent 模式** 派上用场。它们是可复用的提示及 LLM 编排策略，更具可扩展性和可靠性。

本课程围绕最常见、最实用的 Agent 模式构建。

### Agent 框架

Agent 框架为开发者提供现成的模板、工具和基础设施，方便构建 Agent。它们能简化：

- 工具和功能的连接
- 观察 Agent 行为（和定位问题时调试）
- 多 Agent 协作

本课程重点介绍用于构建生产级 Agent 的 **Microsoft Agent Framework (MAF)** 。

---

## 代码示例

准备好亲眼看看了吗？这里是本课的代码示例：

- 🐍 Python: [Agent Framework](/labs/01-intro-to-ai-agents-code-samples-01-python-agent-framework-notebook.md)
- 🔷 .NET: [Agent Framework](/labs/01-intro-to-ai-agents-code-samples-01-dotnet-agent-framework-notes.md)

---

## 快速测试这个 Agent（可选）

一旦你学会如何在 [第16课](/lessons/deployment.md) 部署 Agent，就可以为本课的 `TravelAgent` 添加快速的部署后健康检查，使用预制目录 [`tests/lesson-01-smoke-tests.json`](https://github.com/microsoft/ai-agents-for-beginners/blob/25b7985f3b2dc37a84f4a7387ccd3c9f0e5b1595/tests/lesson-01-smoke-tests.json)。查看 [`tests/README.md`](https://github.com/microsoft/ai-agents-for-beginners/blob/25b7985f3b2dc37a84f4a7387ccd3c9f0e5b1595/tests/README.md) 了解运行方式。

---

## 扩展实践：先运行一个看得见的循环

文件 `examples/first_agent.py` 是完整、可运行的本地模拟。Python 3.12+，无第三方依赖、无环境变量。它让你先观察系统边界，不会调用真实模型。

```bash
python3 examples/first_agent.py
```

预期依次看到：`request` → `tool_result` → `final`。把命令改为 `python3 examples/first_agent.py --max-steps 1`，预期得到 `stopped: step_limit`，不会伪造成功答案。

```python
# 模拟模型只返回数据，执行器才调用工具。
request = {"name": "get_destinations", "arguments": {}}
registry = {"get_destinations": get_destinations}
result = registry[request["name"]](**request["arguments"])
```

上面是从完整示例提取的 **解释片段** 。`registry` 是白名单，`**arguments` 把字典展开为关键字参数；实际文件还验证参数并检查步数。这个极小例子没有证明真实模型能正确选择工具。

## 原 Notebook 怎么读

原课的 `01-python-agent-framework.ipynb` 使用 **Microsoft Agent Framework 1.10.x** ：

1. `dotenv.find_dotenv()` 寻找本地配置，`os.getenv()` 读项目端点和部署名；缺失时直接报错。
2. `FoundryChatClient(..., credential=AzureCliCredential())` 建立模型客户端；它会使用本机 CLI 身份。
3. `@tool(approval_mode="never_require")` 把只读的 `get_destinations` 注册为工具。它返回固定城市列表，不查询实时库存，也不进行预订。
4. `provider.as_agent()` 组合名字、行为指令和工具。`instructions` 要求模型使用目的地工具；实际是否调用，仍应检查日志或响应事件。
5. `await agent.run(...)` 等待完整回答；`stream=True` 逐块返回输出。流式传输改变呈现方式，不等于模型更正确。

按准备篇的固定依赖启动 Jupyter，再打开本章完整 Notebook 导读。 **预期语义** 是推荐列表中的合适目的地；没有唯一的固定措辞。由于课程示例城市信息来自静态列表，天气、航班价格和名额需要另外的工具核实。

## 常见误区与适用边界

| 现象或说法 | 原因 | 应当怎样处理 |
| --- | --- | --- |
| “模型说订好了，所以订单成功” | 把模型回答当作外部状态 | 检查执行工具的真实订单 ID 和状态 |
| 工具返回列表，模型却推荐列表外城市 | 指令遵循不是硬约束 | 在应用侧验证推荐，必要时重试或说明范围 |
| 同一个请求不停查询 | 缺少退出条件与结果复用 | 限制步数，并保存已取得的工具结果 |
| 每次用户反馈后“模型就学会了” | 混淆会话适应与模型训练 | 记录偏好或改提示属于应用状态变化，不自动修改模型参数 |

当任务步骤固定、输入结构稳定时，普通函数或工作流往往更便宜、更容易测试。当用户意图和环境变化决定下一步，需要多轮查询和调整时，再考虑 Agent。引入 Agent 后，你多了模型调用的延迟、成本和不确定性，不能只看功能是否更炫。

## 自测与练习

 **1. 目的地工具的返回值包含 Tokyo，能否推出今天有飞往东京的机票？** 

::: details 答案与解释
不能。目的地列表只证明 Tokyo 在示例列表中，没有日期、出发地、库存和价格。必须用范围明确的航班工具获得这些事实。
:::

 **2. 一个自动把投诉邮件转交客服的 if/else 程序能否被称为 Agent？** 

::: details 答案与解释
在传统智能体分类中，它可以属于简单反射型 Agent；但它不是本课程重点讲解的 LLM 驱动 Agent。分类需要说明采用的定义，不能把所有自动化都当作大模型应用。
:::

 **动手练习：** 修改 `examples/first_agent.py`，让工具返回空列表，系统应回答“没有可推荐目的地”。参考实现是先判断 `if not result`，返回明确的空结果，不让模拟器从列表外补出一个城市。再把工具名改为 `book_trip`，确认白名单拒绝执行。

## 本章小结

一个 Agent 是模型、工具、状态和控制逻辑组成的系统。模型提出行动，应用验证并执行，工具返回证据，状态支持后续步骤。下一章会看框架如何替你组织这些环节，以及框架与托管服务的区别。


## 原课程代码与补充材料

以下是本章实际源文件对应的阅读页。Notebook 已分解为说明、代码及原文件输出；云端示例未进行联网端到端验证。正文中的片段用于解释，运行时使用完整 Notebook 和准备篇的固定依赖。

- [01-python-agent-framework.ipynb](/labs/01-intro-to-ai-agents-code-samples-01-python-agent-framework-notebook.md)
- [01-dotnet-agent-framework.md](/labs/01-intro-to-ai-agents-code-samples-01-dotnet-agent-framework-notes.md)
- [01-dotnet-agent-framework.cs](/labs/01-intro-to-ai-agents-code-samples-01-dotnet-agent-framework-csharp.md)

## 本章来源

基于 [英文原文](https://github.com/microsoft/ai-agents-for-beginners/blob/25b7985f3b2dc37a84f4a7387ccd3c9f0e5b1595/01-intro-to-ai-agents/README.md) 与 [简体中文翻译](https://github.com/microsoft/ai-agents-for-beginners/blob/25b7985f3b2dc37a84f4a7387ccd3c9f0e5b1595/translations/zh-CN/01-intro-to-ai-agents/README.md) 整理，原作者为 Microsoft 与开源贡献者，采用 MIT 许可证。本页标明“补充讲解”与“扩展实践”的内容为本项目新增。

来源提交：`25b7985f3b2d` · 获取日期：2026-09-14。参见[版本校订记录](/guide/sources.md)。

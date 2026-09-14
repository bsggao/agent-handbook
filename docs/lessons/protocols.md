---
title: "Agent 协议：MCP、A2A、NLWeb"
description: "连接工具、其他 Agent 与网站知识。"
course: "protocols"
prev: {"text": "Agent 生产实践", "link": "/lessons/production"}
next: {"text": "上下文工程", "link": "/lessons/context"}
---

# Agent 协议：MCP、A2A、NLWeb

## 本章目标与前置知识（补充讲解）

先学习[工具](./tools.md)、[多 Agent](./multi-agent.md)。本章把三个容易混淆的问题分开：应用如何发现并调用工具？不同 Agent 服务如何交换任务？网站如何提供可检索的自然语言信息？

 **模型上下文协议（Model Context Protocol，MCP）** 规范宿主应用与外部能力的交互； **Agent 间协议（Agent-to-Agent，A2A）** 组织服务之间的任务、状态和产物； **NLWeb（Natural Language Web）** 是把网站数据接入自然语言访问的一组实现与约定。它们解决的接口层次不同，均不自动赋予访问权限。

![MCP 宿主、客户端、服务端和工具的关系](/diagrams/mcp.svg)

*图：本项目重绘。客户端位于宿主应用内，服务端暴露能力，具体工具仍由程序执行；模型不直接持有服务端权限。*

::: warning 两份主 Notebook 是协议概念模拟
`11-mcp-agent-framework.ipynb` 使用本地 Python 工具函数模拟能力调用；`11-a2a-agent-framework.ipynb` 使用本地工作流模拟角色协作。两者没有完成真实 MCP / A2A 网络握手。实际 MCP 连接代码见本章末尾 `mcp-agents` 等材料。区分这些示例，才能避免把函数调用误认为协议互通测试。
:::


## 原课程精读：使用智能 Agent 协议（MCP、A2A 和 NLWeb）

[原课程视频：智能 Agent 协议](https://youtu.be/X-Dh9R3Opn8)


随着 AI Agent 的使用日益增多，对确保标准化、安全性以及支持开放创新的协议需求也在增长。本课将介绍三种旨在满足这一需求的协议——模型上下文协议（MCP）、Agent 间协议（A2A）和自然语言网页（NLWeb）。

## 引言

本课内容包括：

• **MCP** 如何允许 AI Agent 访问外部工具和数据，以完成用户任务。

• **A2A** 如何实现不同 AI Agent 之间的通信与协作。

• **NLWeb** 如何为任何网站带来自然语言界面，使 AI Agent 能够发现并与内容互动。

## 学习目标

• **识别** MCP、A2A 和 NLWeb 在 AI Agent 中的核心目的和优势。

• **解释** 每个协议如何促进大语言模型（LLM）、工具和其他 Agent 之间的通信与互动。

• **认识到** 每个协议在构建复杂 Agent 系统中所扮演的不同角色。

## 模型上下文协议（MCP）

 **模型上下文协议（MCP）** 是一个开放标准，为应用程序向大语言模型（LLM）提供上下文和工具的方式提供了标准化方法。这使得 AI Agent 能够通过“通用适配器”一致地连接到不同的数据源和工具。

接下来我们将了解 MCP 的组成部分、与直接调用 API 的优势对比，以及 AI Agent 如何使用 MCP 服务器的示例。

### MCP 核心组件

MCP 基于 **客户端-服务器架构** ，其核心组件包括：

• **主机** 是启动与 MCP 服务器连接的 LLM 应用程序（例如代码编辑器 VSCode）。

• **客户端** 是主机应用内维护与服务器一对一连接的组件。

• **服务器** 是提供具体功能的轻量级程序。

协议中包含三个核心基础功能，作为 MCP 服务器的能力：

• **工具** ：AI Agent 可调用的离散动作或功能。例如，天气服务可能提供“获取天气”工具，电子商务服务器可能提供“购买产品”工具。MCP 服务器在能力列表中公布每个工具的名称、描述及输入/输出格式。

• **资源** ：由 MCP 服务器提供的只读数据项或文档，客户端可按需获取。示例包括文件内容、数据库记录或日志文件。资源可以是文本（如代码或 JSON）或二进制（如图像或 PDF）。

• **提示** ：预定义的模板，提供建议的提示，以支持更复杂的工作流程。

### MCP 的优势

MCP 为 AI Agent 带来了显著的优势：

• **动态工具发现** ：Agent 可以动态获取服务器提供的可用工具列表及其描述。相比传统 API 往往需要静态编码集成，且 API 变更需要更新代码，MCP 提供“一次集成”的方式，更具适应性。

• **跨 LLM 互操作性** ：MCP 可跨不同 LLM 工作，灵活切换核心模型以评估并提升性能。

• **标准化安全** ：MCP 包含标准认证方法，便于扩展对更多 MCP 服务器的访问管理，相较于管理各种传统 API 不同密钥和认证方式，简化了安全管理。

### MCP 示例

![MCP Diagram](/upstream-assets/translated_images/zh-CN/mcp-diagram.e4ca1cbd551444a1.webp)

*图：MCP Diagram。来源：Microsoft AI Agents for Beginners，MIT。*

假设用户想通过由 MCP 支持的 AI 助手预订航班。

1. **连接** ：AI 助手（MCP 客户端）连接航空公司提供的 MCP 服务器。

2. **工具发现** ：客户端询问航空公司 MCP 服务器：“有哪些可用工具？”服务器回应如“搜索航班”和“预订航班”等工具。

3. **调用工具** ：用户向 AI 助手说：“请搜索从波特兰到火奴鲁鲁的航班。”AI 助手通过其 LLM 识别需要调用“搜索航班”工具，并向 MCP 服务器传递相关参数（出发地、目的地）。

4. **执行与响应** ：MCP 服务器作为包装层，调用航空公司的内部预订 API，随后接收航班信息（如 JSON 数据）并返回给 AI 助手。

5. **后续交互** ：AI 助手展示航班选项，用户选定航班后，助手可能调用同一 MCP 服务器上的“预订航班”工具，完成预订。

## Agent 间协议（A2A）

MCP 主要连接 LLM 与工具， **Agent 间协议（A2A）** 更进一步，实现不同 AI Agent 之间的通信与协作。A2A 将不同组织、环境和技术栈的 AI Agent 连接起来，共同完成共享任务。

我们将探讨 A2A 的组成部分和优势，并通过旅游应用示例说明其应用。

### A2A 核心组件

A2A 致力于使 Agent 之间通信并协作完成用户子任务。协议中的每个组件均支持这一点：

#### Agent 卡

类似 MCP 服务器分享工具列表，Agent 卡包含：
- Agent 名称。
- 其完成的一般任务的 **描述** 。
- **具体技能列表** 及描述，帮助其他 Agent（甚至人类用户）理解何时及为何调用该 Agent。
- 当前 Agent 的 **端点 URL** 。
- Agent 的 **版本** 及 **功能** ，如流式响应和推送通知。

#### Agent 执行器

Agent 执行器负责 **传递用户聊天上下文给远程 Agent** ，远程 Agent 需要这些信息来理解待完成的任务。在 A2A 服务器中，Agent 通过自身的 LLM 解析请求并利用内部工具执行任务。

#### 工件

当远程 Agent 完成请求的任务，其工作成果以工件形式创建。工件 **包含 Agent 工作的结果** ， **所完成工作的描述** 以及通过协议传递的 **文本上下文** 。工件发送后，远程 Agent 的连接关闭，直至再次需要。

#### 事件队列

此组件用于 **处理更新和消息传递** 。在生产环境中尤为重要，以防任务尚未完成时 Agent 间连接被关闭，尤其是任务完成可能耗时较长。

### A2A 的优势

• **增强协作** ：使来自不同厂商和平台的 Agent 能够互动、共享上下文并协作，促进传统分离系统间无缝自动化。

• **模型选择灵活性** ：每个 A2A Agent 可自主选择使用的 LLM，允许按 Agent 优化或微调模型，与某些 MCP 场景中单一 LLM 连接不同。

• **内置认证** ：认证集成于 A2A 协议中，为 Agent 交互提供强健安全框架。

### A2A 示例

![A2A Diagram](/upstream-assets/translated_images/zh-CN/A2A-Diagram.8666928d648acc26.webp)

*图：A2A Diagram。来源：Microsoft AI Agents for Beginners，MIT。*

让我们扩展旅游预订场景，这次采用 A2A。

1. **用户向多 Agent 请求** ：用户与“旅游 Agent” A2A 客户端/Agent 互动，例如说：“请预订下周前往火奴鲁鲁的全程旅行，包括航班、酒店及租车。”

2. **旅游 Agent 协调** ：旅游 Agent 接收到复杂请求，利用其 LLM 推理任务，确定需要与其他专门 Agent 交互。

3. **Agent 间通信** ：旅游 Agent 使用 A2A 协议连接下游 Agent，如不同公司的“航空 Agent”、“酒店 Agent”和“租车 Agent”。

4. **委托任务执行** ：旅游 Agent 将具体任务发送给这些专门 Agent（例如“查找飞往火奴鲁鲁的航班”、“预订酒店”、“租车”）。每个专门 Agent 运行自己的 LLM，使用自己工具（也可能是 MCP 服务器），完成各自的预订部分。

5. **整合响应** ：所有下游 Agent 完成任务后，旅游 Agent 汇总结果（航班详情、酒店确认、租车预订），以聊天式响应方式发送给用户。

## 自然语言网页（NLWeb）

网站长期以来是用户访问互联网上信息和数据的主要渠道。

下面我们将了解 NLWeb 的不同组件、优势及通过旅游应用示例展示 NLWeb 的工作方式。

### NLWeb 组件

- **NLWeb 应用（核心服务代码）** ：处理自然语言问题的系统。它连接平台各部分生成响应。可以将其视为为网站自然语言功能提供动力的 **引擎** 。

- **NLWeb 协议** ：网站自然语言交互的 **基本规则集** 。响应以 JSON 格式返回（常用 Schema.org）。其目的是为“AI 网”打造简单基础，就像 HTML 让文档在线共享成为可能。

- **MCP 服务器（模型上下文协议端点）** ：每个 NLWeb 配置也充当 **MCP 服务器** 。意味着可以 **与其他 AI 系统共享工具（如“ask”方法）和数据** 。实际上，使网站内容和功能可被 AI Agent 使用，让网站成为更广泛“Agent 生态系统”的一部分。

- **嵌入模型** ：用于 **将网站内容转换为称为向量的数值表示（嵌入）** 。这些向量以计算机可比较和搜索的方式捕捉含义。向量存储于特殊数据库，用户可选择使用的嵌入模型。

- **向量数据库（检索机制）** ：存储网站内容嵌入的数据库。当有人查询时，NLWeb 检查向量数据库，快速找到最相关信息，返回按相似度排序的可能答案列表。NLWeb 支持多种向量存储系统，如 Qdrant、Snowflake、Milvus、Azure AI Search 和 Elasticsearch。

### NLWeb 示例

![NLWeb](/upstream-assets/translated_images/zh-CN/nlweb-diagram.c1e2390b310e5fe4.webp)

*图：NLWeb。来源：Microsoft AI Agents for Beginners，MIT。*

再次考虑我们的旅游预订网站，这次由 NLWeb 驱动。

1. **数据摄取** ：旅行网站现有产品目录（如航班列表、酒店介绍、旅游套餐）用 Schema.org 格式或通过 RSS 提供。NLWeb 工具摄取这些结构化数据，生成嵌入，并存储于本地或远程向量数据库。

2. **自然语言查询（人类）** ：用户访问网站，不是通过菜单导航，而是在聊天界面中输入：“帮我找一个下周在火奴鲁鲁有游泳池的适合家庭的酒店”。

3. **NLWeb 处理** ：NLWeb 应用接收查询，发送查询给 LLM 进行理解，同时在其向量数据库中搜索相关酒店列表。

4. **精准结果** ：LLM 协助解读数据库搜索结果，根据“适合家庭”、“游泳池”和“火奴鲁鲁”条件甄别最佳匹配，并生成自然语言响应。关键是响应引用了网站目录中的真实酒店，避免虚构信息。

5. **AI Agent 交互** ：由于 NLWeb 充当 MCP 服务器，外部 AI 旅行 Agent 亦可连接此网站的 NLWeb 实例。AI Agent 可使用 `ask` MCP 方法直接查询网站：`ask("酒店推荐的火奴鲁鲁地区有素食友好餐厅吗？")`。NLWeb 实例将处理查询，利用其餐厅信息数据库（如果加载了），并返回结构化 JSON 响应。

### 想了解更多关于 MCP/A2A/NLWeb 吗？

加入 [Microsoft Foundry Discord](https://discord.com/invite/ATgtXmAS5D) ，与其他学习者交流，参加答疑时间，获得 AI Agent 相关问题的解答。

## 资源

- [MCP 入门](https://aka.ms/mcp-for-beginners)  
- [MCP 文档](https://learn.microsoft.com/python/api/overview/azure/ai-projects-readme)
- [NLWeb 仓库](https://github.com/nlweb-ai/NLWeb)
- [Microsoft Agent Framework](https://aka.ms/ai-agents-beginners/agent-framework)

## 三种机制怎样共同服务旅行助手（补充讲解）

宿主应用通过 MCP 客户端连接航班工具服务，先初始化并协商能力，再发现工具描述。模型输出订票参数后，宿主验证当前身份、额度与审批，才调用服务端。工具结果作为外部数据进入下一次模型调用。

如果酒店由另一家公司运营独立 Agent，可通过 A2A 的 Agent Card 发现服务能力，用任务标识跟踪提交、进行中、需要输入和结束状态。Artifact 是交付产物，例如行程文件；状态消息不是最终产物。Agent Card 是声明，不是该服务可信或可访问的证明。

NLWeb 场景中，网站将结构化内容、索引与自然语言接口连接起来，例如从餐厅信息中返回可引用的营业时间。它可以结合 MCP，但并不意味着任意网页都会自动成为安全工具。原课程 `ask`/MCP 案例是其实现示例；不能将 NLWeb 当成取代 HTTP 的通用协议标准。

## 代码与运行边界

| 材料 | 要观察的代码 | 外部条件 |
| --- | --- | --- |
| 主 MCP Notebook | `@tool`、本地工具注册、工具结果 | Foundry 模型与身份；没有真实 MCP 会话 |
| 主 A2A Notebook | 工作流中货币、活动、汇总角色 | Foundry；是同进程编排 |
| `mcp-agents` | `ClientSession`、传输、初始化、`list_tools` / 调用 | 按相邻 README 安装 MCP SDK 并启动服务端 |
| GitHub MCP 示例 | 服务器连接配置和允许工具 | 额外 GitHub 身份权限，注意旧 SDK 差异 |

完整源文件及依赖放在本页底部。运行真实连接时，先独立确认服务端启动并返回工具清单，再接模型。若连接失败，不应让模型“猜一个工具结果”继续。

当前协议会演进；本课程锁定的是课程提交，不等于锁定全部外部服务协议。对照 [MCP 官方架构](https://modelcontextprotocol.io/docs/2026-07-28/learn/architecture) 和 [A2A 官方核心概念](https://a2a-protocol.org/latest/topics/key-concepts/) 检查版本协商、传输与认证。这里的静态导读没有完成远程协议兼容性测试。

## 无账号协议推演（扩展实践）

用下面完整 Python 3.12+ 标准库脚本观察发现与执行的区别，保存为 `protocol_demo.py` 后运行。它是 **本地字典模拟，不是 MCP 实现** 。

```python
schemas = {"exchange_rate": {"currency": "string"}}
rates = {"JPY": 0.048, "EUR": 7.8}
def call(name, args):
    if name not in schemas:
        raise ValueError("UNKNOWN_TOOL")
    if set(args) != {"currency"} or args["currency"] not in rates:
        raise ValueError("INVALID_ARGUMENTS")
    return {"rate": rates[args["currency"]], "source": "preset"}
print("发现", schemas)
print("结果", call("exchange_rate", {"currency": "JPY"}))
```

预期发现一个工具，再得到预设汇率 `0.048`。实际协议还需要消息格式、请求关联 ID、能力协商、传输、错误模型和授权；不能把这些责任省略后称为完成协议接入。

## 排错与自测

| 现象 | 原因 | 检查方法 |
| --- | --- | --- |
| stdio 初始化失败 | 子进程未启动或把普通日志写到协议 stdout | 查看 stderr、启动命令与工作目录 |
| 列得出工具却不能调用 | 没权限、参数不符或工具被禁用 | 对照 schema 和服务端授权错误 |
| A2A 一直处理中 | 没跟踪最终状态或事件流中断 | 按任务 ID 重连查询，设置截止时间 |
| 网站内容诱导泄露密钥 | 把外部内容当成高优先级指令 | 数据与系统策略隔离，执行层最小权限 |

 **练习：** 一个本地 `researcher()` 调用 `writer()` 的程序属于 A2A 互操作吗？远程服务返回工具清单就能自动执行退款吗？

::: details 答案
前者只是程序内协作，除非实现了 A2A 规定的服务接口与任务语义。后者仍必须经过宿主应用的身份、范围、金额与审批验证；工具发现不等于授权。
:::

下一章[上下文工程](./context.md)讨论这些工具和远程结果中，究竟哪些信息应该送给模型。


## 原课程代码与补充材料

以下是本章实际源文件对应的阅读页。Notebook 已分解为说明、代码及原文件输出；云端示例未进行联网端到端验证。正文中的片段用于解释，运行时使用完整 Notebook 和准备篇的固定依赖。

- [11-mcp-agent-framework.ipynb](/labs/11-agentic-protocols-code-samples-11-mcp-agent-framework-notebook.md)
- [11-a2a-agent-framework.ipynb](/labs/11-agentic-protocols-code-samples-11-a2a-agent-framework-notebook.md)
- [README.md](/labs/11-agentic-protocols-code-samples-mcp-agents-readme-notes.md)
- [README.md](/labs/11-agentic-protocols-code-samples-github-mcp-readme-notes.md)
- [event-descriptions.md](/labs/11-agentic-protocols-code-samples-github-mcp-event-descriptions-notes.md)
- [MCP_SETUP.md](/labs/11-agentic-protocols-code-samples-github-mcp-mcp-setup-notes.md)
- [app.py](/labs/11-agentic-protocols-code-samples-github-mcp-app-script.md)
- [chainlit.md](/labs/11-agentic-protocols-code-samples-github-mcp-chainlit-notes.md)
- [server.py](/labs/11-agentic-protocols-code-samples-mcp-agents-server-server-script.md)
- [__init__.py](/labs/11-agentic-protocols-code-samples-mcp-agents-server-init-script.md)
- [event_store.py](/labs/11-agentic-protocols-code-samples-mcp-agents-server-event-store-script.md)
- [test_event_store.py](/labs/11-agentic-protocols-code-samples-mcp-agents-server-test-event-store-script.md)
- [client.py](/labs/11-agentic-protocols-code-samples-mcp-agents-client-client-script.md)
- [__init__.py](/labs/11-agentic-protocols-code-samples-mcp-agents-client-init-script.md)
- [resumable_client.py](/labs/11-agentic-protocols-code-samples-mcp-agents-client-resumable-client-script.md)
- [utils.py](/labs/11-agentic-protocols-code-samples-mcp-agents-client-utils-script.md)

## 本章来源

基于 [英文原文](https://github.com/microsoft/ai-agents-for-beginners/blob/25b7985f3b2dc37a84f4a7387ccd3c9f0e5b1595/11-agentic-protocols/README.md) 与 [简体中文翻译](https://github.com/microsoft/ai-agents-for-beginners/blob/25b7985f3b2dc37a84f4a7387ccd3c9f0e5b1595/translations/zh-CN/11-agentic-protocols/README.md) 整理，原作者为 Microsoft 与开源贡献者，采用 MIT 许可证。本页标明“补充讲解”与“扩展实践”的内容为本项目新增。

来源提交：`25b7985f3b2d` · 获取日期：2026-09-14。参见[版本校订记录](/guide/sources.md)。

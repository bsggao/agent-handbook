## 本章目标与前置知识（补充讲解）

先学习[工具](./tools.md)、[多 Agent](./multi-agent.md)。本章把三个容易混淆的问题分开：应用如何发现并调用工具？不同 Agent 服务如何交换任务？网站如何提供可检索的自然语言信息？

**模型上下文协议（Model Context Protocol，MCP）**规范宿主应用与外部能力的交互；**Agent 间协议（Agent-to-Agent，A2A）**组织服务之间的任务、状态和产物；**NLWeb（Natural Language Web）**是把网站数据接入自然语言访问的一组实现与约定。它们解决的接口层次不同，均不自动赋予访问权限。

![MCP 宿主、客户端、服务端和工具的关系](/diagrams/mcp.svg)

*图：本项目重绘。客户端位于宿主应用内，服务端暴露能力，具体工具仍由程序执行；模型不直接持有服务端权限。*

::: warning 两份主 Notebook 是协议概念模拟
`11-mcp-agent-framework.ipynb` 使用本地 Python 工具函数模拟能力调用；`11-a2a-agent-framework.ipynb` 使用本地工作流模拟角色协作。两者没有完成真实 MCP / A2A 网络握手。实际 MCP 连接代码见本章末尾 `mcp-agents` 等材料。区分这些示例，才能避免把函数调用误认为协议互通测试。
:::

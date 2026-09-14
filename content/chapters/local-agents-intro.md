## 本章目标与前置知识（补充讲解）

先掌握[工具](./tools.md)、[RAG](./rag.md)和[MCP](./protocols.md)。本章学习在设备上运行小语言模型（Small Language Model，SLM），用工具补足知识与计算能力，并辨认哪些组件仍可能访问网络。

本地模型适合敏感文档、离线环境或高频小任务，但仍消耗内存、电力和维护时间。**“推理在本地”不等于“整个应用永远不联网”**：首次下载模型/嵌入模型、远端工具、遥测与云端回退都需要单独检查。

原例使用 Foundry Local、Qwen、OpenAI Python SDK 的 Chat Completions 和 Chroma，没有把主执行循环换成 Microsoft Agent Framework。兼容性要核对具体端点与模型工具调用能力，不能仅凭“兼容 OpenAI”就把 Responses 与 Chat Completions 随意互换。

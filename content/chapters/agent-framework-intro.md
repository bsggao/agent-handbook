## 本章目标与前置知识（补充讲解）

建议先读[框架概览](./frameworks.md)、[多 Agent](./multi-agent.md)、[记忆](./memory.md)。本章把 Agent、会话、工具、工作流、中间件和托管联系起来，重点是能读懂原仓库的实际 Python 工作流。

想象费用助手先读收据、再核对政策、最后提交审批。单个 Agent 负责一段有边界的生成或工具任务；工作流规定节点、边和暂停/继续规则；中间件在调用前后增加统一行为。**框架帮助连接这些组件，不替你决定正确的权限与业务状态。**

::: warning 版本阅读提示
本仓库固定 `agent-framework-core==1.10.0`。README 部分片段仍使用 `ChatAgent`、`get_new_thread()`、`run_stream()` 等历史写法；同提交的新 Notebook 主要使用 `create_session()` 和 `run(..., stream=True)`。以下原课程片段按历史资料保留，实际运行优先选本章 Notebook 并固定依赖；不要混抄不同版本 API。详见[版本差异表](/guide/sources.md)。
:::

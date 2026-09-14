---
title: 零基础学习路线
description: 零基础学习路线 · AI Agent 中文学习指南
---

# 零基础学习路线

这里的“零基础”指尚未学习 Agent，但能读简单代码。不要求先了解向量数据库或模型训练；遇到 Python 语法可随时打开[Python 小抄](./python.md)。

## 第一轮：先看懂一个完整循环

1. [00 环境配置](/lessons/setup.md)：先选本地无 API 路线，运行 `first_agent.py`。
2. [01 Agent 入门](/lessons/introduction.md)：分清模型、应用、工具与状态；能说明何时退出。
3. [02 框架](/lessons/frameworks.md)与[03 设计模式](/lessons/design-patterns.md)：理解框架职责和人如何保持控制。
4. [04 工具调用](/lessons/tools.md)：操作正常/失败两种模拟，指出真正执行发生在哪一步。

 **阶段验收：** 用自己的话解释“模型生成调用请求”和“应用实际执行”为什么必须分开，并让本地程序在调用超限时停止。

## 第二轮：让回答有证据，让行动有边界

按[05 RAG](/lessons/rag.md)→[06 可信赖](/lessons/trust.md)→[07 规划](/lessons/planning.md)→[08 多 Agent](/lessons/multi-agent.md)→[09 反思](/lessons/reflection.md)学习。每次只增加一种机制。

 **阶段验收：** 把问题、检索候选、选入上下文、引用和拒绝原因分开记录。一个角色超时后，汇总者能说明结果不完整，而不是捏造缺失内容。完成综合实践阶段 1–3。

## 第三轮：管理长期运行

依次阅读[10 生产实践](/lessons/production.md)、[11 协议](/lessons/protocols.md)、[12 上下文](/lessons/context.md)、[13 记忆](/lessons/memory.md)。关注评估、版本、隔离和删除，不要先追求更多工具。

 **阶段验收：** 运行综合实践阶段 4–5，证明不同用户标签的数据隔离；未知工具、证据为空、未授权写入和超限均得到可观察结果。

## 第四轮：根据需求选择进阶实验

- 想组织复杂应用：读 [14 Microsoft Agent Framework](/lessons/agent-framework.md)，选择一份工作流 Notebook。
- 只有 UI、没有合适 API：读 [15 Browser Use](/lessons/browser-use.md)，先练每步观察与验证。
- 要让多人持续使用：读 [16 可扩展部署](/lessons/deployment.md)，先设计状态与权限，再做扩容。
- 敏感资料或离线任务：读 [17 本地 Agent](/lessons/local-agents.md)，先核对硬件与网络边界。
- 要核对执行记录：读 [18 安全](/lessons/security.md)，运行两份离线签名 Notebook。

## 三种实验路线与投入

| 路线 | 前提 | 能验证什么 |
| --- | --- | --- |
| 浏览器内学习 | 普通浏览器 | 预设流程、概念、交互状态，无真实模型 |
| 本地 Python | Python 3.12+ | 规则模拟、真实检索/文件状态、测试、可选密码学依赖 |
| 原课程联网实验 | 云账号、模型权限、依赖、可能计费 | 真实模型与框架；结果要在自己的环境测量 |

不要把需要账号的步骤视为学习前 13 章的门槛。先完成无 API 路线，再有目的地运行一个真实实验。学习进度可在侧栏清除，首页“继续学习”会回到最近访问章节。

---
title: "11 · __init__"
outline: [2, 3]
---

# 11 · __init__

[返回：Agent 协议：MCP、A2A、NLWeb](/lessons/protocols.md) · [不可变原始文件](https://github.com/microsoft/ai-agents-for-beginners/blob/25b7985f3b2dc37a84f4a7387ccd3c9f0e5b1595/11-agentic-protocols/code_samples/mcp-agents/server/__init__.py)

::: info 原课程脚本 · 未联网执行
保留原始框架与完整代码。依赖、变量、入口以脚本及其相邻 README 为准；本页为代码导读，未声称所有外部服务均已验证。
:::

阅读提示：跟踪本单元格读取的变量、修改的状态以及返回值。按原顺序执行，确认依赖的前序变量已经存在。

```python
"""
MCP Server implementations.

This package contains various MCP server implementations:
- server.py: Basic MCP server
- resumable_server.py: Server with event store and resumption support
- event_store.py: Event store implementation for session resumption
"""

```

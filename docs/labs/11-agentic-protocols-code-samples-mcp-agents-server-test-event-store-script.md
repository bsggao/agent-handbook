---
title: "11 · test_event_store"
outline: [2, 3]
---

# 11 · test_event_store

[返回：Agent 协议：MCP、A2A、NLWeb](/lessons/protocols.md) · [不可变原始文件](https://github.com/microsoft/ai-agents-for-beginners/blob/25b7985f3b2dc37a84f4a7387ccd3c9f0e5b1595/11-agentic-protocols/code_samples/mcp-agents/server/test_event_store.py)

::: info 原课程脚本 · 未联网执行
保留原始框架与完整代码。依赖、变量、入口以脚本及其相邻 README 为准；本页为代码导读，未声称所有外部服务均已验证。
:::

异步执行：async def 定义协程，await 等待结果；普通 .py 脚本需要 asyncio.run() 入口，Notebook 支持顶层 await。

```python
import unittest
from unittest.mock import AsyncMock

from event_store import SimpleEventStore
from mcp.server.streamable_http import EventMessage
from mcp.types import JSONRPCMessage, JSONRPCNotification


def message(method: str) -> JSONRPCMessage:
    return JSONRPCMessage(root=JSONRPCNotification(jsonrpc="2.0", method=method))


class SimpleEventStoreTests(unittest.IsolatedAsyncioTestCase):
    async def test_replay_is_limited_to_original_stream(self) -> None:
        store = SimpleEventStore()
        first = message("notifications/first")
        other_stream = message("notifications/other")
        expected = message("notifications/expected")

        last_event_id = await store.store_event("stream-a", first)
        await store.store_event("stream-b", other_stream)
        expected_event_id = await store.store_event("stream-a", expected)

        callback = AsyncMock()
        stream_id = await store.replay_events_after(last_event_id, callback)

        self.assertEqual(stream_id, "stream-a")
        callback.assert_awaited_once()
        replayed = callback.await_args.args[0]
        self.assertIsInstance(replayed, EventMessage)
        self.assertEqual(replayed.event_id, expected_event_id)
        self.assertIs(replayed.message, expected)

    async def test_unknown_event_id_does_not_replay(self) -> None:
        store = SimpleEventStore()
        await store.store_event("stream-a", message("notifications/first"))
        callback = AsyncMock()

        stream_id = await store.replay_events_after("missing", callback)

        self.assertIsNone(stream_id)
        callback.assert_not_awaited()

    async def test_returns_stream_when_no_later_events_exist(self) -> None:
        store = SimpleEventStore()
        last_event_id = await store.store_event(
            "stream-a", message("notifications/first")
        )

        callback = AsyncMock()
        stream_id = await store.replay_events_after(last_event_id, callback)

        self.assertEqual(stream_id, "stream-a")
        callback.assert_not_awaited()


if __name__ == "__main__":
    unittest.main()

```

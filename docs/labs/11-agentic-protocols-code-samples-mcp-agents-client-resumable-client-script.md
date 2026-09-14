---
title: "11 · resumable_client"
outline: [2, 3]
---

# 11 · resumable_client

[返回：Agent 协议：MCP、A2A、NLWeb](/lessons/protocols.md) · [不可变原始文件](https://github.com/microsoft/ai-agents-for-beginners/blob/25b7985f3b2dc37a84f4a7387ccd3c9f0e5b1595/11-agentic-protocols/code_samples/mcp-agents/client/resumable_client.py)

::: info 原课程脚本 · 未联网执行
保留原始框架与完整代码。依赖、变量、入口以脚本及其相邻 README 为准；本页为代码导读，未声称所有外部服务均已验证。
:::

异步执行：async def 定义协程，await 等待结果；普通 .py 脚本需要 asyncio.run() 入口，Notebook 支持顶层 await。

输出观察：print 展示应用可观察结果；预存输出和现场结果可能不同，它不是模型内部思考记录。

```python
#!/usr/bin/env python3
"""
Minimal Resumable MCP Client

Simple client that demonstrates session resumption with the long_running_agent tool.
- If resumption token exists, resumes the session
- If no token exists, creates new session and saves token
- Clears token when task completes
"""

import argparse
import asyncio
import json
import logging
import os
from pathlib import Path
from typing import Dict, Any, Optional

from mcp import ClientSession, types
from mcp.client.streamable_http import streamablehttp_client
from mcp.server.streamable_http import MCP_SESSION_ID_HEADER, MCP_PROTOCOL_VERSION_HEADER
from mcp.shared.message import ClientMessageMetadata
from mcp.types import TextContent

# Configure logging to suppress noisy SSE warnings
logging.basicConfig(level=logging.WARNING)
logger = logging.getLogger(__name__)

# Suppress specific noisy loggers
logging.getLogger('httpx').setLevel(logging.WARNING)
logging.getLogger('mcp.client.streamable_http').setLevel(logging.ERROR)
logging.getLogger('mcp').setLevel(logging.WARNING)
logging.getLogger('pydantic_core').setLevel(logging.ERROR)

# Filter out specific SSE JSON parsing errors
class SSEFilter(logging.Filter):
    def filter(self, record):
        return not (
            "Error parsing SSE message" in record.getMessage() or
            "Invalid JSON: EOF while parsing" in record.getMessage()
        )

# Apply filter to relevant loggers
for logger_name in ['mcp.client.streamable_http', 'mcp', 'pydantic_core']:
    log = logging.getLogger(logger_name)
    log.addFilter(SSEFilter())

# Token file location
TOKEN_FILE = Path(".mcp_resumption_token.json")


def load_resumption_tokens() -> Optional[Dict[str, Any]]:
    """Load resumption tokens from file."""
    if TOKEN_FILE.exists():
        try:
            with open(TOKEN_FILE, 'r') as f:
                tokens = json.load(f)
                logger.info(f"🔄 Loaded resumption tokens: session_id={tokens.get('session_id')}")
                return tokens
        except Exception as e:
            logger.error(f"Error loading tokens: {e}")
    return None


def save_resumption_tokens(session_id: str, resumption_token: str, protocol_version: str = "2025-03-26"):
    """Save resumption tokens to file."""
    tokens = {
        "session_id": session_id,
        "resumption_token": resumption_token,
        "protocol_version": protocol_version,
        "tool_name": "long_running_agent",
        "tool_args": {}
    }
    try:
        with open(TOKEN_FILE, 'w') as f:
            json.dump(tokens, f, indent=2)
        logger.info(f"💾 Saved resumption tokens: session_id={session_id}")
    except Exception as e:
        logger.error(f"Error saving tokens: {e}")


def clear_resumption_tokens():
    """Clear resumption tokens file."""
    if TOKEN_FILE.exists():
        try:
            TOKEN_FILE.unlink()
            logger.info("🗑️ Cleared resumption tokens")
        except Exception as e:
            logger.error(f"Error clearing tokens: {e}")


async def run_long_running_task(server_url: str):
    """Run the long_running_agent with resumption support."""
    
    # Check for existing tokens
    existing_tokens = load_resumption_tokens()
    
    # Prepare headers for resumption if tokens exist
    headers = {}
    if existing_tokens:
        headers[MCP_SESSION_ID_HEADER] = existing_tokens["session_id"]
        headers[MCP_PROTOCOL_VERSION_HEADER] = existing_tokens.get("protocol_version", "2025-03-26")
        print("🔄 Resuming existing session...")
    else:
        print("🆕 Creating new session...")
    
    try:
        async with streamablehttp_client(
            server_url,
            headers=headers if headers else None,
            terminate_on_close=False  # Enable resumption
        ) as (read_stream, write_stream, get_session_id):
            
            # Message handler for real-time notifications (standardized to use log messages)
            async def message_handler(message) -> None:
                try:
                    if isinstance(message, types.ServerNotification):
                        if isinstance(message.root, types.LoggingMessageNotification):
                            log_data = message.root.params
                            # Format log messages similar to progress notifications for consistency
                            print(f"📡 [{log_data.logger}] {log_data.data}")
                        elif isinstance(message.root, types.ProgressNotification):
                            # Keep support for progress notifications in case other tools use them
                            progress = message.root.params
                            print(f"📊 Progress: {progress.progress}/{progress.total} - {progress.message}")
                        elif isinstance(message.root, types.ResourceUpdatedNotification):
                            print(f"🔄 Resource updated: {message.root.params.uri}")
                except Exception:
                    # Silently ignore message handler errors to avoid breaking the flow
                    pass
            
            async with ClientSession(read_stream, write_stream, message_handler=message_handler) as session:
                
                # Only initialize if this is a new session (no existing tokens)
                if not existing_tokens:
                    result = await session.initialize()
                    print(f"✅ Session initialized: {result.serverInfo.name}")
                else:
                    print("✅ Using existing session (no initialization needed)")
                
                # Set up resumption token callback (matching test signature)
                async def on_resumption_token_update(token: str) -> None:
                    print(f"💾 Resumption token received: {token[:20]}...")
                    session_id = get_session_id()
                    if session_id:
                        protocol_version = getattr(session, 'negotiated_protocol_version', '2025-03-26')
                        save_resumption_tokens(session_id, token, protocol_version)
                        print(f"💾 Resumption token saved")
                
                # Prepare metadata with resumption support
                if existing_tokens and existing_tokens.get("resumption_token"):
                    # Resume existing task
                    print("🔄 Resuming long-running task...")
                    metadata = ClientMessageMetadata(
                        resumption_token=existing_tokens["resumption_token"]
                    )
                else:
                    # Start new task
                    print("🚀 Starting long-running task...")
                    metadata = ClientMessageMetadata(
                        on_resumption_token_update=on_resumption_token_update
                    )
                
                # Execute the long_running_agent tool
                try:
                    print("metadata:", metadata)
                    result = await session.send_request(
                        types.ClientRequest(
                            types.CallToolRequest(
                                method="tools/call",
                                params=types.CallToolRequestParams(
                                    name="long_running_agent",
                                    arguments={}
                                ),
                            )
                        ),
                        types.CallToolResult,
                        metadata=metadata,
                    )
                    
                    # Task completed successfully
                    content_text = "Task completed"
                    if result.content and len(result.content) > 0:
                        first_content = result.content[0]
                        if isinstance(first_content, TextContent):
                            content_text = first_content.text
                    
                    print(f"✅ Task completed: {content_text}")
                    clear_resumption_tokens()
                    
                except Exception as e:
                    print(f"❌ Task failed: {e}")
                    # Keep tokens in case we want to retry
                    
    except Exception as e:
        print(f"❌ Connection error: {e}")


async def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Minimal Resumable MCP Client")
    parser.add_argument("--url", default="http://127.0.0.1:8006/mcp", help="MCP server URL")
    parser.add_argument("--clear-tokens", action="store_true", help="Clear resumption tokens and exit")
    
    args = parser.parse_args()
    
    if args.clear_tokens:
        clear_resumption_tokens()
        print("🗑️ Resumption tokens cleared")
        return
    
    print("🤖 Minimal Resumable MCP Client")
    print(f"🔗 Connecting to: {args.url}")
    
    await run_long_running_task(args.url)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n👋 Interrupted by user")
    except Exception as e:
        print(f"💥 Fatal error: {e}")

```

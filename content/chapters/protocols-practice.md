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

用下面完整 Python 3.12+ 标准库脚本观察发现与执行的区别，保存为 `protocol_demo.py` 后运行。它是**本地字典模拟，不是 MCP 实现**。

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

**练习：**一个本地 `researcher()` 调用 `writer()` 的程序属于 A2A 互操作吗？远程服务返回工具清单就能自动执行退款吗？

::: details 答案
前者只是程序内协作，除非实现了 A2A 规定的服务接口与任务语义。后者仍必须经过宿主应用的身份、范围、金额与审批验证；工具发现不等于授权。
:::

下一章[上下文工程](./context.md)讨论这些工具和远程结果中，究竟哪些信息应该送给模型。

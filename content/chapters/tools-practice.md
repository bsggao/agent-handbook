## 代码实操：阅读旅行工具集

原 `04-python-agent-framework.ipynb` 定义目的地、可用性和航班三个读取工具，再创建 `TravelToolAgent`。依赖和 Foundry 配置按[准备篇](./setup.md)，完整代码与运行入口见本章下方导读。查询价格是固定示例数据，不是实时旅行报价；真实模型调用未实测。

- `Annotated[str, ...]` 提供参数说明；实际机场代码是否存在仍要程序验证。
- `tools=travel_tools` 是模型能看到的工具集合；不要注册一个任意运行 shell 的函数替代所有业务工具。
- `book_flight` 使用 `approval_mode="always_require"`。Notebook 最后只打印该工具的名称与审批模式，没有演示完整批准与恢复，所以不能据此认为已完成真实预订。
- `BookingRecommendation` / `TravelPlan` 定义了类型，但本课该次 `run()` **没有传入**响应格式；其回答不能当作自动验证通过的结构化对象。第 7 章实际使用 `options={"response_format": TravelPlan}`，可对照两者。

## 扩展实践：明确拒绝，再允许一个本地动作

项目的最终示例提供真实运行的应用校验：

```bash
python3 examples/assistant/app.py '创建任务：复习工具调用' --stage 2
python3 examples/assistant/app.py '创建任务：复习工具调用' --stage 2 --approve --request-id tool-01
```

第一次应返回 `APPROVAL_REQUIRED`，第二次产生本地任务 ID。重复第二条不应新建第二份任务。文件 `app.py` 中 `Executor.execute` 先检查白名单、参数集合、字段类型和授权，再调用 `Store.create_task`。`request_id` 用来表示同一个逻辑请求，不是随每次重试重新生成。

## 出错怎么办

| 现象 | 定位 | 处理 |
| --- | --- | --- |
| 工具名称不存在 | 模型返回未注册名称 | 白名单拒绝，返回结构化错误，不用 eval 动态执行 |
| 参数看似 JSON 但类型错 | 只有解析、没有类型验证 | 检查必填项、枚举、范围和额外字段 |
| 工具超时后重复下单 | 重试没有幂等保护 | 相同逻辑请求复用 ID，查询实际执行状态再决定 |
| SQL 查询能删除表 | 数据库身份过宽 | 只读账号、允许的表与查询形态；参数化过滤条件 |

只读权限降低破坏风险，却不能阻止读取本无权查看的个人记录。业务范围过滤和身份验证仍需在工具服务执行。

## 自测与练习

一个工具返回 `{"ok":false,"error":"timeout"}`，模型说“处理完成”。应用应信谁？

::: details 答案
以实际执行结果和业务状态为准。应把超时表示为未确认或失败；若操作可能已经提交，先查询状态，不能直接重试产生副作用，也不能展示完成。
:::

**练习：** 向 `Executor.execute` 传入 `search_docs` 与多余的 `admin=true` 字段。参考验收为抛出 `INVALID_ARGUMENT`，工具计数不增加；已提供 `test_unknown_tool_and_argument_validation`。

本章让行动经过执行边界。下一章把检索做成工具，让回答拥有可核对的证据。

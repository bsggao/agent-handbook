## 扩展实践：先运行一个看得见的循环

文件 `examples/first_agent.py` 是完整、可运行的本地模拟。Python 3.12+，无第三方依赖、无环境变量。它让你先观察系统边界，不会调用真实模型。

```bash
python3 examples/first_agent.py
```

预期依次看到：`request` → `tool_result` → `final`。把命令改为 `python3 examples/first_agent.py --max-steps 1`，预期得到 `stopped: step_limit`，不会伪造成功答案。

```python
# 模拟模型只返回数据，执行器才调用工具。
request = {"name": "get_destinations", "arguments": {}}
registry = {"get_destinations": get_destinations}
result = registry[request["name"]](**request["arguments"])
```

上面是从完整示例提取的**解释片段**。`registry` 是白名单，`**arguments` 把字典展开为关键字参数；实际文件还验证参数并检查步数。这个极小例子没有证明真实模型能正确选择工具。

## 原 Notebook 怎么读

原课的 `01-python-agent-framework.ipynb` 使用 **Microsoft Agent Framework 1.10.x**：

1. `dotenv.find_dotenv()` 寻找本地配置，`os.getenv()` 读项目端点和部署名；缺失时直接报错。
2. `FoundryChatClient(..., credential=AzureCliCredential())` 建立模型客户端；它会使用本机 CLI 身份。
3. `@tool(approval_mode="never_require")` 把只读的 `get_destinations` 注册为工具。它返回固定城市列表，不查询实时库存，也不进行预订。
4. `provider.as_agent()` 组合名字、行为指令和工具。`instructions` 要求模型使用目的地工具；实际是否调用，仍应检查日志或响应事件。
5. `await agent.run(...)` 等待完整回答；`stream=True` 逐块返回输出。流式传输改变呈现方式，不等于模型更正确。

按准备篇的固定依赖启动 Jupyter，再打开本章完整 Notebook 导读。**预期语义**是推荐列表中的合适目的地；没有唯一的固定措辞。由于课程示例城市信息来自静态列表，天气、航班价格和名额需要另外的工具核实。

## 常见误区与适用边界

| 现象或说法 | 原因 | 应当怎样处理 |
| --- | --- | --- |
| “模型说订好了，所以订单成功” | 把模型回答当作外部状态 | 检查执行工具的真实订单 ID 和状态 |
| 工具返回列表，模型却推荐列表外城市 | 指令遵循不是硬约束 | 在应用侧验证推荐，必要时重试或说明范围 |
| 同一个请求不停查询 | 缺少退出条件与结果复用 | 限制步数，并保存已取得的工具结果 |
| 每次用户反馈后“模型就学会了” | 混淆会话适应与模型训练 | 记录偏好或改提示属于应用状态变化，不自动修改模型参数 |

当任务步骤固定、输入结构稳定时，普通函数或工作流往往更便宜、更容易测试。当用户意图和环境变化决定下一步，需要多轮查询和调整时，再考虑 Agent。引入 Agent 后，你多了模型调用的延迟、成本和不确定性，不能只看功能是否更炫。

## 自测与练习

**1. 目的地工具的返回值包含 Tokyo，能否推出今天有飞往东京的机票？**

::: details 答案与解释
不能。目的地列表只证明 Tokyo 在示例列表中，没有日期、出发地、库存和价格。必须用范围明确的航班工具获得这些事实。
:::

**2. 一个自动把投诉邮件转交客服的 if/else 程序能否被称为 Agent？**

::: details 答案与解释
在传统智能体分类中，它可以属于简单反射型 Agent；但它不是本课程重点讲解的 LLM 驱动 Agent。分类需要说明采用的定义，不能把所有自动化都当作大模型应用。
:::

**动手练习：** 修改 `examples/first_agent.py`，让工具返回空列表，系统应回答“没有可推荐目的地”。参考实现是先判断 `if not result`，返回明确的空结果，不让模拟器从列表外补出一个城市。再把工具名改为 `book_trip`，确认白名单拒绝执行。

## 本章小结

一个 Agent 是模型、工具、状态和控制逻辑组成的系统。模型提出行动，应用验证并执行，工具返回证据，状态支持后续步骤。下一章会看框架如何替你组织这些环节，以及框架与托管服务的区别。

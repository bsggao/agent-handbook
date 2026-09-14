---
title: 综合实践：文档问答与任务助手
description: 综合实践：文档问答与任务助手 · AI Agent 中文学习指南
---

# 综合实践：文档问答与任务助手

本项目是“扩展实践”，用一个小型政策助手串起五个阶段。它能查文档、附引用、管理本地任务和回答偏好，并拒绝未授权写入或超预算执行。默认模型由明确规则模拟，检索、参数校验、文件存储、幂等性和测试是真实程序行为。 **无需账号、API Key 或模型下载。** 

知识库是本项目自编的虚构商店政策，不是微软课程原始政策，也不是法律建议。实际退款或发送消息均不在工具范围内。

## 准备与文件地图

Python 3.12+；从网站项目根目录运行。默认只依赖标准库：

```bash
python3 --version
python3 examples/assistant/app.py --stage 1
```

也可以[下载完整实践包](/downloads/agent-handbook-examples.zip)，解压后从包的根目录执行相同命令。所有阶段共用一个可运行版本，`--stage` 逐步开放能力；不用在每一阶段复制一套相似代码。

| 文件 | 职责 | 引入阶段 |
| --- | --- | --- |
| `examples/assistant/app.py` | 命令行入口、模拟模型、执行器、结果 | 1、2、5 |
| `examples/assistant/documents.json` | 四份带稳定 ID 的示例政策 | 3 |
| `examples/assistant/retrieval.py` | 词法检索与上下文选择 | 3 |
| `examples/assistant/storage.py` | 用户命名空间、偏好、任务与去重 | 2、4 |
| `examples/assistant/evaluate.py` | 六个固定回归用例 | 5 |
| `examples/assistant/test_assistant.py` | 行为测试 | 5 |
| `examples/assistant/cloud.py` | 可选真实 MAF 调用 | 独立联网实验 |
| `.env.example` | 云端配置占位，不含真实密钥 | 独立联网实验 |

## 阶段 1：建立模型调用边界

新增能力：接收用户输入并得到输出。阅读 `SimulatedModel.propose()` 与 `run()`；阶段 1 不提供工具，输出固定教学回答。

```bash
python3 examples/assistant/app.py '你好，介绍一下你自己' --stage 1
```

预期 `mode` 明确标记模拟，`stage` 为 1，`tool_calls` 为 0。这一阶段学习的是输入/输出边界， **没有运行真实模型** 。真实模型的最小调用在本页最后单独提供，需要 Azure 前提条件。

关键点：把“模型如何回答”放在可替换的组件，把“是否允许执行”留给应用。否则换一个模型时，权限逻辑也会被一并换掉。

## 阶段 2：增加工具请求与执行

新增能力：查询本地任务数、请求创建任务。`SimulatedModel` 只生成 `name` 和 `arguments`；`Executor.execute()` 对照白名单、参数与批准标志后执行 `Store` 方法。

```bash
python3 examples/assistant/app.py '现在有多少个任务？' --stage 2 --user learner
python3 examples/assistant/app.py '创建任务：复习工具调用' --stage 2 --request-id task-001
python3 examples/assistant/app.py '创建任务：复习工具调用' --stage 2 --request-id task-001 --approve
```

干净命名空间第一条返回 0；第二条返回 `APPROVAL_REQUIRED` 且无写入；第三条返回本地任务 T1。再次执行相同批准命令，应返回同一任务。重新创建一项独立任务时使用新 `request-id`。

`--approve` 是你对这次本地操作的明确开关，不是真实多用户审批系统。为了从第一天保持安全，基础参数和授权检查在所有有工具的阶段都生效；阶段 5 将系统性验证这些边界。

## 阶段 3：增加文档检索与引用

新增文件：`documents.json` 和 `retrieval.py`。普通政策、定制商品、物流和账户四份资料都包含稳定 ID。

```bash
python3 examples/assistant/app.py '购买后多久可以申请退款？' --stage 3
python3 examples/assistant/app.py '定制商品可以退款吗？' --stage 3
python3 examples/assistant/app.py '月球上的天气如何？' --stage 3
```

前两条应显示相关 `candidates`、`context_ids` 与 `citations`，答案引用已选文档，保留条件和例外。第三条说明当前知识库没有足够证据。回答由所选片段直接拼接，避免把词法演示伪装成模型的自由生成。

`search()` 将中文切为相邻双字片段，并结合英文词与关键词重合排序。这是词法检索，没有向量模型；分数不是概率。`select_context()` 按完整片段与字符预算选择，只有实际选入的片段才可引用。

 **验收：** 把 `--budget` 改为 0，候选仍可能存在，但上下文和引用为空；程序必须说明缺少证据。再把问题中的关键词换成知识库未覆盖的表达，观察词法检索的局限。引入向量检索之前，先建立这个能解释的基线。

## 阶段 4：上下文预算与跨进程记忆

新增能力：显式保存偏好、再次加载、按本地用户标签隔离和删除。`storage.py` 保存 `.assistant-data/<用户标签哈希>.json`，文件里是明文 JSON。

```bash
python3 examples/assistant/app.py '退款政策是什么？' --stage 4 --user alice --remember '简洁回答'
python3 examples/assistant/app.py '退款政策是什么？' --stage 4 --user alice
python3 examples/assistant/app.py '退款政策是什么？' --stage 4 --user bob
python3 examples/assistant/app.py --stage 4 --user alice --forget
```

Alice 的第二次运行能看到偏好，Bob 的 `memory` 为空。最后一条清除 Alice 的偏好和任务，请勿将其误解为“只清除本次聊天”。回答偏好在此仅控制排版：合并换行，不删除带引用的证据。

此阶段没有自动提取所有聊天为记忆，避免未经用户决定就保存多余信息。`--user` 是本地命名空间，不是认证；真实服务必须从服务端身份确定用户。原子文件替换可避免半写状态，但不提供并发事务。

## 阶段 5：限制、错误处理与评估

新增能力：完整检验工具白名单、参数、次数/时间预算、授权、幂等性、数据隔离和损坏文件处理。

```bash
python3 examples/assistant/app.py '退款政策是什么？' --stage 5 --max-calls 0
python3 examples/assistant/app.py '创建任务：完成综合实践' --stage 5 --request-id final-001
python3 examples/assistant/app.py '创建任务：完成综合实践' --stage 5 --request-id final-001 --approve
python3 examples/assistant/evaluate.py
python3 -m unittest discover -s examples/assistant -p 'test_*.py' -v
```

前两条分别停止于 `LIMIT_REACHED` 与 `APPROVAL_REQUIRED`；批准后创建本地任务。当前检查记录为 14 个行为测试和 6 个回归用例通过，范围见[验证报告](./verification.md)。

`max_calls` 在执行工具前检查；时间预算在每次工具执行前检查。对于这里的快速本地函数足以演示流程， **它不能中断已经卡住的任意阻塞函数** 。真实网络工具要有连接/读取超时，必要时使用独立进程或可取消任务。

| 测试类别 | 为什么需要 | 通过意味着什么 |
| --- | --- | --- |
| 证据与空上下文 | 避免没资料也编造 | 规则版本保留引用且会说明缺失 |
| 未授权写入 | 模型请求不能直接变成副作用 | 没有批准就不创建任务 |
| 相同请求重复 | 重试不能重复写入 | 同动作与请求 ID 返回已有任务 |
| 用户隔离与删除 | 不能串用偏好/任务 | 测试命名空间互不干扰 |
| 未知工具/无效参数/预算 | 执行边界可检查 | 被拒绝并输出明确状态 |
| 损坏文件与日志 | 不能静默丢数据或复制敏感内容 | 出错明确，事件不保存原始问题 |

这些用例检验确定性的程序行为，不是开放式模型准确率评测。更换真实模型后仍要建立人工标注的任务集，检查事实、引用支持、漏掉的条件与拒绝行为。

## 关键代码解析

`propose()` 的输出只是结构化请求。例如 `{"name":"create_task","arguments":{"title":"复习 RAG"}}` 不会自动运行。`execute()` 先查工具是否允许，再确认参数字段完全匹配，随后检查写入批准和预算。结果被加入最小应用事件，最终返回给调用方。

`Store.create_task()` 用请求 ID 与动作标题产生去重键；相同 ID 不同动作不会被误当成同一任务。JSON 文件不是安全数据库，不能用于并发生产流量。`--forget` 只删除明确用户标签的文件，不扫描或删除其他文件。

`run()` 将候选证据、选中上下文、引用和最终文本分别返回，便于验收。不要只看“最终答案像对的”，忽略中间可能选择了错误政策。

## 可选真实模型实验：保留上游 MAF

这部分使用上游同版本的 Microsoft Agent Framework 与 Foundry 模型客户端，可能计费。需要 Azure 订阅、Foundry 项目、实际模型部署、对应角色权限及 Azure CLI。密钥与凭据只留在本地 Python 进程，网站前端不会读取它们。

```bash
python3 -m venv .venv-cloud
source .venv-cloud/bin/activate
python -m pip install -r examples/assistant/requirements-cloud.txt
cp .env.example .env
# 在本地编辑 .env，填写项目端点与部署名
az login
python examples/assistant/cloud.py --stage 1
python examples/assistant/cloud.py --stage 3
```

阶段 1 是无工具的真实模型调用；阶段 3 加入只读文档检索。该独立联网实验不执行本地任务创建，避免把模拟批准开关当成生产审批。`FoundryChatClient` 的 `project_endpoint`、`model`、`credential`、`as_agent()` 以及 Agent 的 `run()` 已与 1.10.0 发行源码核对；没有进行云端端到端调用。

预期第一条得到模型生成的介绍；第二条回答一般与定制商品的政策并引用文档 ID。实际文本由模型决定，需要人工核对。工具最多真实检索三次，外层 60 秒期限约束总等待；它不保证每个服务都会立即取消已发出的请求。

## 常见失败、限制与下一步

- 总返回模拟介绍：选了阶段 1，或阶段 2 的问题不匹配预设规则；查看 `mode` 和 `stage`。
- 想创建任务却变成文档查询：示例规则要求前缀 `创建任务：`（中文冒号）。这是规则模拟的局限。
- 第一次运行已经有任务：默认目录保留了上次实验。换 `--user`/`--data-dir`，或明确使用 `--forget`。
- 引用不够相关：词法匹配不理解所有同义表达。先补充测试和文档，再考虑嵌入与重排。
- 真实模型 403/404：按[排错指南](./faq.md)检查身份、项目端点与实际部署名。

完成后可扩展结构化记忆的有效期、文档版本和只读真实检索。若增加邮件、退款或删除文件等高影响工具，必须另外设计身份认证、具体动作审批、幂等执行与审计，不能仅修改模型提示。

::: details 最终自测与参考答案
1. 模型能否直接运行任意 Python？不能，执行器只调用注册的函数。
2. 为什么候选文档不一定出现在引用里？上下文预算可能排除了它，引用必须来自实际选入证据。
3. 为什么 Alice 的偏好存储不等于安全认证？任何本地命令都能声明 `--user alice`，Web 服务需要可信身份。
4. 测试全过代表模型不会幻觉吗？不代表，它们主要验证规则模拟与程序边界。
5. 把 JSON 存储放进多进程服务还缺什么？并发控制、事务、认证、权限、可靠持久化与备份恢复。
:::

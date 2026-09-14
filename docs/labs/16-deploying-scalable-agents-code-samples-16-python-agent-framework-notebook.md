---
title: "16 · 16-python-agent-framework"
outline: [2, 3]
---

# 16 · 16-python-agent-framework

[返回：可扩展部署](/lessons/deployment.md) · [不可变原始文件](https://github.com/microsoft/ai-agents-for-beginners/blob/25b7985f3b2dc37a84f4a7387ccd3c9f0e5b1595/16-deploying-scalable-agents/code_samples/16-python-agent-framework.ipynb)

::: warning 原课程完整 Notebook · 静态阅读与代码解析
代码按英文源文件顺序保留，中文说明以同版本译本为基础。原始安装单元格可能含无版本上限的 `-U`；请跳过它们，先按[准备篇](/lessons/setup.md)固定依赖。云端服务、模型权限、网站布局和部分 SDK 接口需在你自己的环境验证。本站没有执行云端请求；第 18 章的离线验证状态单独记录在[检查报告](/guide/verification.md)。
:::

## 运行准备

Python 3.12+；在独立虚拟环境安装源仓库依赖与本页中声明的额外依赖。原文件路径：`upstream/16-deploying-scalable-agents/code_samples/16-python-agent-framework.ipynb`。以原仓库根目录为工作目录，在 Jupyter 中按顺序执行；身份与环境变量见准备篇。

```bash
cd upstream
python -m jupyterlab
```

[下载原始 Notebook](/notebooks/16-deploying-scalable-agents/code_samples/16-python-agent-framework.ipynb)。输出为上游文件保存的历史结果，不能用作本站实测证明。

## 第16课 - 使用 Microsoft Foundry 部署可扩展 Agent

在本笔记本中，你将构建一个适用于虚构公司 **Contoso** 的 **生产就绪客户支持 Agent** 。与之前的课程不同，重点不是 Agent 的推理循环——而是围绕它构建的所有内容，使 Agent 能够安全地大规模运行：

1. **工具调用** — 订单查询和工单创建。
2. **RAG** — 来自知识库的策略答案。
3. **记忆** — 跨回合记住客户信息。
4. **模型路由** — 简单请求发送到小模型，复杂请求发送到大模型。
5. **响应缓存** — 对重复问题无需模型调用直接响应。
6. **人工审批** — 超过阈值的退款需暂停以等待批准。
7. **评估门控** — 阻止错误发布的离线测试集。
8. **可观测性** — 每个请求的 OpenTelemetry 跟踪。

每个章节都是独立且可运行的。请逐行阅读——生产原语保持故意精简。

## 设置

在运行此笔记本之前，请确保你已经：

1. **拥有一个已部署聊天模型的 Microsoft Foundry 项目** （例如 `gpt-5-mini`）。
2. **已使用 Azure CLI 登录** — 在终端中运行 `az login`。
3. **设置了所需的环境变量：** 
   - `AZURE_AI_PROJECT_ENDPOINT` — 你的 Microsoft Foundry 项目端点。
   - `AZURE_AI_MODEL_DEPLOYMENT_NAME` — 你已部署模型的名称。

当设置了 `AZURE_SEARCH_SERVICE_ENDPOINT` 和 `AZURE_SEARCH_API_KEY` 时，RAG 部分使用 **Azure AI Search** ，否则回退到内存搜索，以确保笔记本在无 Search 资源情况下也能运行。

### 代码单元格 3

阅读提示：跟踪本单元格读取的变量、修改的状态以及返回值。按原顺序执行，确认依赖的前序变量已经存在。

```text
%pip install agent-framework azure-ai-projects azure-identity python-dotenv -q
```

### 代码单元格 4

配置加载：从本地环境读取端点与部署名；缺少变量时先修复配置，不要把密钥写进代码。

模型连接：project_endpoint 是项目地址，model 是实际部署名称；credential 提供访问身份。客户端创建本身不证明已经部署服务端 Agent。

输出观察：print 展示应用可观察结果；预存输出和现场结果可能不同，它不是模型内部思考记录。

```python
import logging
logging.getLogger("agent_framework.foundry").setLevel(logging.ERROR)

import os
import re
import dotenv
from typing import Annotated

from agent_framework import tool
from agent_framework.foundry import FoundryChatClient
from azure.identity import AzureCliCredential

dotenv.load_dotenv(dotenv.find_dotenv())

endpoint = os.getenv("AZURE_AI_PROJECT_ENDPOINT")
model = os.getenv("AZURE_AI_MODEL_DEPLOYMENT_NAME")

if not endpoint or not model:
    raise ValueError(
        "Missing required environment variables. "
        "Please set AZURE_AI_PROJECT_ENDPOINT and AZURE_AI_MODEL_DEPLOYMENT_NAME in your .env file."
    )

provider = FoundryChatClient(
    project_endpoint=endpoint,
    model=model,
    credential=AzureCliCredential(),
)
print("Foundry client ready.")
```

## 1. 工具

生产工具针对真实系统执行实际工作。这里我们用纯 Python 函数模拟一个订单数据库和票务系统。`@tool` 装饰器将它们暴露给 Agent。

注意 `issue_refund` 对超出阈值的退款使用了 `approval_mode="always_require"` —— 这是我们后续部署的人机交互原语。

### 代码单元格 6

工具定义：类型注解和文档字符串描述输入、用途；模型产生调用请求，框架在应用进程中执行函数。检查是否需要人工批准。

输出观察：print 展示应用可观察结果；预存输出和现场结果可能不同，它不是模型内部思考记录。

```python
# Simulated backend systems (in production these are API calls behind scoped identities).
ORDERS = {
    "A1001": {"status": "shipped", "total": 42.00, "eta": "2 days"},
    "A1002": {"status": "processing", "total": 128.50, "eta": "5 days"},
    "A1003": {"status": "delivered", "total": 19.99, "eta": "delivered"},
}
TICKETS: list[dict] = []
REFUND_APPROVAL_THRESHOLD = 50.0


@tool(approval_mode="never_require")
def get_order_status(order_id: Annotated[str, "The customer's order ID, e.g. A1001"]) -> str:
    """Look up the status of a customer order."""
    order = ORDERS.get(order_id.upper())
    if not order:
        return f"No order found with ID {order_id}."
    return (
        f"Order {order_id.upper()}: status={order['status']}, "
        f"total=${order['total']:.2f}, eta={order['eta']}."
    )


@tool(approval_mode="never_require")
def open_ticket(
    subject: Annotated[str, "Short subject line for the support ticket"],
    details: Annotated[str, "Full description of the customer's issue"],
) -> str:
    """Open a support ticket for issues that need human follow-up."""
    ticket_id = f"T{1000 + len(TICKETS) + 1}"
    TICKETS.append({"id": ticket_id, "subject": subject, "details": details})
    return f"Ticket {ticket_id} opened: {subject}"


def refund_needs_approval(amount: float) -> bool:
    """Refunds above the threshold require a human approver."""
    return amount > REFUND_APPROVAL_THRESHOLD


@tool(approval_mode="always_require")
def issue_refund(
    order_id: Annotated[str, "The order to refund"],
    amount: Annotated[float, "Refund amount in USD"],
) -> str:
    """Issue a refund. Execution pauses for human approval before it runs."""
    return f"Refund of ${amount:.2f} issued for order {order_id.upper()}."


print("Tools defined.")
```

## 2. RAG — 政策知识库

政策问题（“你的退货期限是多少？”）应从权威来源获得答案，而不是依赖模型的记忆。我们将一个小型知识库封装为搜索工具。

在生产环境中，这是 **Azure AI Search** ；在这里我们提供了一个内存中的关键词搜索，以便笔记本可以在任何地方运行，当环境变量存在时会自动切换到 Azure AI Search。

### 代码单元格 8

工具定义：类型注解和文档字符串描述输入、用途；模型产生调用请求，框架在应用进程中执行函数。检查是否需要人工批准。

检索过程：跟踪查询、候选结果和实际选入的证据；检索为空时应明确返回缺失，而不是补写答案。

输出观察：print 展示应用可观察结果；预存输出和现场结果可能不同，它不是模型内部思考记录。

```python
KNOWLEDGE_BASE = {
    "returns": "Contoso accepts returns within 30 days of delivery for a full refund. Items must be unused and in original packaging.",
    "shipping": "Standard shipping takes 3-5 business days. Express shipping (1-2 days) is available at checkout for an extra fee.",
    "warranty": "All Contoso electronics carry a 12-month limited warranty covering manufacturing defects.",
    "refund_policy": "Refunds are processed to the original payment method within 5 business days of approval. Refunds over $50 require a supervisor's approval.",
}


def _in_memory_search(query: str) -> str:
    q = query.lower()
    hits = [text for key, text in KNOWLEDGE_BASE.items() if key.replace("_", " ") in q or key in q]
    if not hits:
        # crude keyword fallback so the tool still returns something useful
        hits = [text for text in KNOWLEDGE_BASE.values() if any(w in text.lower() for w in q.split())]
    return "\n".join(hits) if hits else "No matching policy found."


def _azure_search(query: str) -> str:
    from azure.core.credentials import AzureKeyCredential
    from azure.search.documents import SearchClient

    client = SearchClient(
        endpoint=os.environ["AZURE_SEARCH_SERVICE_ENDPOINT"],
        index_name=os.getenv("AZURE_SEARCH_INDEX_NAME", "contoso-policies"),
        credential=AzureKeyCredential(os.environ["AZURE_SEARCH_API_KEY"]),
    )
    results = client.search(search_text=query, top=3)
    return "\n".join(r.get("content", "") for r in results) or "No matching policy found."


USE_AZURE_SEARCH = bool(os.getenv("AZURE_SEARCH_SERVICE_ENDPOINT") and os.getenv("AZURE_SEARCH_API_KEY"))


@tool(approval_mode="never_require")
def search_policies(query: Annotated[str, "The policy question to look up"]) -> str:
    """Search Contoso support policies to answer customer questions."""
    if USE_AZURE_SEARCH:
        return _azure_search(query)
    return _in_memory_search(query)


print(f"RAG ready. Using {'Azure AI Search' if USE_AZURE_SEARCH else 'in-memory search'}.")
```

## 3. 内存

一个忘记自己在和谁交谈的支持 Agent 是一个糟糕的支持 Agent。我们为每个客户保留一个微小的个人资料存储，并将一个简短的摘要注入 Agent 的指令中。在生产环境中，这是一项内存服务（见第13课）；这里用字典使该模式可见。

### 代码单元格 10

输出观察：print 展示应用可观察结果；预存输出和现场结果可能不同，它不是模型内部思考记录。

```python
CUSTOMER_MEMORY: dict[str, dict] = {
    "cust-42": {"name": "Dana", "tier": "enterprise", "recent_order": "A1002"},
    "cust-99": {"name": "Sam", "tier": "standard", "recent_order": "A1003"},
}


def memory_context(customer_id: str) -> str:
    profile = CUSTOMER_MEMORY.get(customer_id)
    if not profile:
        return "This is a new customer with no history."
    return (
        f"Customer {profile['name']} ({profile['tier']} tier). "
        f"Most recent order: {profile['recent_order']}."
    )


print(memory_context("cust-42"))
```

## 4 & 5. 模型路由和响应缓存

两个成本杠杆连接到单个请求处理器：

- **路由** ：一个廉价的启发式分类器决定请求是需要小模型还是大模型。
- **缓存** ：标准化的重复问题直接从缓存提供，无需调用模型。

这里的分类器故意设计得很简单。在生产环境中，你会针对流量验证它，并且可以用 Foundry 的模型路由器替代它。

### 代码单元格 12

输出观察：print 展示应用可观察结果；预存输出和现场结果可能不同，它不是模型内部思考记录。

```python
SMALL_MODEL = os.getenv("AZURE_AI_SMALL_MODEL", model)   # e.g. gpt-5-nano
LARGE_MODEL = os.getenv("AZURE_AI_LARGE_MODEL", model)   # e.g. gpt-5-mini

response_cache: dict[str, str] = {}
route_counters = {"small": 0, "large": 0, "cache": 0}


def normalize(query: str) -> str:
    return re.sub(r"\s+", " ", query.lower().strip())


COMPLEX_SIGNALS = ("refund", "cancel", "complaint", "escalate", "broken", "wrong", "why")


def is_simple(query: str) -> bool:
    """Route complex or high-stakes requests to the large model; everything else to the small one."""
    q = query.lower()
    if any(signal in q for signal in COMPLEX_SIGNALS):
        return False
    return len(q.split()) <= 20


def choose_model(query: str) -> str:
    return SMALL_MODEL if is_simple(query) else LARGE_MODEL


print(f"Small model: {SMALL_MODEL} | Large model: {LARGE_MODEL}")
```

## 6 & 8. Agent、人类审批和可观测性

现在我们从上述工具组装 Agent，并将每个请求包装在 OpenTelemetry span 中。`handle_support_request` 函数是生产请求处理器：缓存 → 路由 → 跟踪 → 运行 → 缓存。

人类审批由框架处理：因为 `issue_refund` 的 `approval_mode="always_require"`，运行会暂停并呈现一个审批请求，等待我们明确解决。

### 代码单元格 14

模型连接：project_endpoint 是项目地址，model 是实际部署名称；credential 提供访问身份。客户端创建本身不证明已经部署服务端 Agent。

异步执行：async def 定义协程，await 等待结果；普通 .py 脚本需要 asyncio.run() 入口，Notebook 支持顶层 await。

行为约束：instructions 引导模型，不能替代执行器的权限验证、次数限制和结果检查。

```python
# Tracing: use the Agent Framework tracer if available, else a no-op so the notebook runs anywhere.
try:
    from agent_framework.observability import get_tracer
    tracer = get_tracer()
except Exception:  # observability extras not installed
    from contextlib import contextmanager

    class _NoopSpan:
        def set_attribute(self, *_args, **_kwargs):
            pass

    class _NoopTracer:
        @contextmanager
        def start_as_current_span(self, _name):
            yield _NoopSpan()

    tracer = _NoopTracer()


SUPPORT_INSTRUCTIONS = (
    "You are Contoso's customer support agent. Be concise, friendly, and accurate. "
    "Use search_policies for policy questions, get_order_status for orders, "
    "open_ticket when a human needs to follow up, and issue_refund for refunds. "
    "Never invent policy details."
)

# Build one agent per model tier so we can route by cost. The current agent-framework
# selects the model on the client, so each tier gets its own FoundryChatClient.
_TOOLS = [get_order_status, open_ticket, search_policies, issue_refund]
_agents_by_model: dict[str, object] = {}


def agent_for(model_name: str):
    if model_name not in _agents_by_model:
        client = FoundryChatClient(
            project_endpoint=endpoint,
            model=model_name,
            credential=AzureCliCredential(),
        )
        _agents_by_model[model_name] = client.as_agent(
            name="ContosoSupportAgent",
            instructions=SUPPORT_INSTRUCTIONS,
            tools=_TOOLS,
        )
    return _agents_by_model[model_name]


# Default agent (used by the evaluation gate, which does not route).
support_agent = agent_for(SMALL_MODEL)


async def handle_support_request(query: str, customer_id: str) -> str:
    # 1. Serve from cache when we can.
    key = normalize(query)
    if key in response_cache:
        route_counters["cache"] += 1
        return response_cache[key]

    # 2. Route by complexity to control cost.
    chosen_model = choose_model(query)
    route_counters["small" if chosen_model == SMALL_MODEL else "large"] += 1

    # 3. Add per-customer memory to the prompt.
    context = memory_context(customer_id)
    prompt = f"[Customer context: {context}]\n\n{query}"

    # 4. Run inside a trace span for observability.
    with tracer.start_as_current_span("support_request") as span:
        span.set_attribute("customer.id", customer_id)
        span.set_attribute("routed.model", chosen_model)
        response = await agent_for(chosen_model).run(prompt)

    text = response.text
    response_cache[key] = text
    return text


print("Support agent assembled.")
```

### 代码单元格 15

输出观察：print 展示应用可观察结果；预存输出和现场结果可能不同，它不是模型内部思考记录。

```python
# Try a few requests. The first is simple (small model), the second is a refund (large model + approval path).
print(await handle_support_request("What is your return window?", "cust-99"))
print("---")
print(await handle_support_request("Where is my order A1002?", "cust-42"))
print("---")
# Repeat the first question -> served from cache.
print(await handle_support_request("What is your return window?", "cust-99"))
print("---")
print("Routing counters:", route_counters)
```

## 7. 评估门

这是课程中的发布门：一个离线测试集对 Agent 进行评分，只有通过率超过阈值后才进行部署。这里的评分器是一个简单的关键词重叠检查，以保持笔记本的自包含；在生产环境中，你会使用作为裁判的LLM或框架评估器（参见第10课）。

### 代码单元格 17

异步执行：async def 定义协程，await 等待结果；普通 .py 脚本需要 asyncio.run() 入口，Notebook 支持顶层 await。

输出观察：print 展示应用可观察结果；预存输出和现场结果可能不同，它不是模型内部思考记录。

```python
TEST_CASES = [
    {"input": "How long do I have to return an item?", "expected": ["30 days", "refund"]},
    {"input": "How fast is standard shipping?", "expected": ["3-5", "business days"]},
    {"input": "What is the status of order A1001?", "expected": ["shipped", "A1001"]},
    {"input": "Do your electronics have a warranty?", "expected": ["12-month", "warranty"]},
]


def score_response(actual: str, expected_keywords: list[str]) -> float:
    actual_l = actual.lower()
    hits = sum(1 for kw in expected_keywords if kw.lower() in actual_l)
    return hits / len(expected_keywords)


async def evaluation_gate(test_cases: list[dict], threshold: float = 0.8) -> bool:
    passed = 0
    for case in test_cases:
        result = await support_agent.run(case["input"])
        s = score_response(result.text, case["expected"])
        status = "PASS" if s >= 0.5 else "FAIL"
        print(f"[{status}] {case['input']}  (score={s:.0%})")
        if s >= 0.5:
            passed += 1
    pass_rate = passed / len(test_cases)
    print(f"\nEvaluation pass rate: {pass_rate:.0%} (gate: {threshold:.0%})")
    return pass_rate >= threshold


gate_passed = await evaluation_gate(TEST_CASES, threshold=0.8)
print("\nDeploy allowed:" , gate_passed)
```

## 综合应用：模拟发布

下面的单元展示了课程描述的整个循环：运行评估门，只有通过时才“部署”。这是在将 Agent 版本发布到 Foundry Agent Service 之前，在持续集成中运行的模式。

### 代码单元格 19

异步执行：async def 定义协程，await 等待结果；普通 .py 脚本需要 asyncio.run() 入口，Notebook 支持顶层 await。

输出观察：print 展示应用可观察结果；预存输出和现场结果可能不同，它不是模型内部思考记录。

```python
async def release(test_cases: list[dict]) -> None:
    print("Running pre-deployment evaluation gate...\n")
    if await evaluation_gate(test_cases, threshold=0.8):
        print("\n✅ Gate passed — promoting agent version to the Foundry Agent Service.")
    else:
        print("\n❌ Gate failed — release blocked. Fix the agent and re-run.")


await release(TEST_CASES)
```

## 总结

你组装了一个准备好投入生产的客户支持 Agent，所有运营问题均已接入：

- **工具、RAG 和记忆** 赋予 Agent 能力和上下文。
- **模型路由和缓存** 控制延迟和成本。
- **人工审批** 保护高风险操作，如大额退款。
- **评估关卡** 阻止不良版本发布。
- **追踪** 使每个请求可观察。

### 挑战

扩展此 Agent 以：

1. **支持多模型** — 添加第三个“推理”层并将升级/投诉路由到该层。
2. **添加评估关卡** — 扩展 `TEST_CASES` 以包含退款审批场景，并确认关卡能捕获回归。
3. **添加成本感知路由** — 跟踪每个请求的估计成本（小额 vs 大额 vs 缓存），并在一批混合查询后打印成本报告。

在下一课中，你将走相反的路线，使用 Microsoft Foundry Local 和 Qwen 完全在自己的机器上运行 Agent。


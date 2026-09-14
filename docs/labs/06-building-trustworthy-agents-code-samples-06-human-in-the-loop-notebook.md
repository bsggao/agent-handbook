---
title: "06 · 06-human-in-the-loop"
outline: [2, 3]
---

# 06 · 06-human-in-the-loop

[返回：构建可信赖的 Agent](/lessons/trust.md) · [不可变原始文件](https://github.com/microsoft/ai-agents-for-beginners/blob/25b7985f3b2dc37a84f4a7387ccd3c9f0e5b1595/06-building-trustworthy-agents/code_samples/06-human-in-the-loop.ipynb)

::: warning 原课程完整 Notebook · 静态阅读与代码解析
代码按英文源文件顺序保留，中文说明以同版本译本为基础。原始安装单元格可能含无版本上限的 `-U`；请跳过它们，先按[准备篇](/lessons/setup.md)固定依赖。云端服务、模型权限、网站布局和部分 SDK 接口需在你自己的环境验证。本站没有执行云端请求；第 18 章的离线验证状态单独记录在[检查报告](/guide/verification.md)。
:::

## 运行准备

Python 3.12+；在独立虚拟环境安装源仓库依赖与本页中声明的额外依赖。原文件路径：`upstream/06-building-trustworthy-agents/code_samples/06-human-in-the-loop.ipynb`。以原仓库根目录为工作目录，在 Jupyter 中按顺序执行；身份与环境变量见准备篇。

```bash
cd upstream
python -m jupyterlab
```

[下载原始 Notebook](/notebooks/06-building-trustworthy-agents/code_samples/06-human-in-the-loop.ipynb)。输出为上游文件保存的历史结果，不能用作本站实测证明。

## 人机协同环节：预执行关卡、风险分层和审计日志

本课的 README 中通过一个简短示例介绍了人机协同，该示例在 Agent 已生成响应后，要求用户选择 `APPROVE` 或 `REJECT`。这种模式是一个很好的起点，但实际的生产环境中，人机协同通常需要另外三个方面：

1. 一个 **预执行关卡** ，在 Agent 执行高风险步骤之前运行，从而控制成本、不可逆性和延迟。
2. **风险分层** ，使低风险动作自动执行，中风险动作批量审批，只有高风险动作真正需要人工阻断。
3. 一个 **审计日志加修订循环** ，每个关卡决策都记录为 JSONL 格式，拒绝时用结构化理由重新提示 Agent，而不仅仅是打印 `Revising...`。

本笔记本在与 `06-system-message-framework.ipynb` 相同的基本原语上构建这些功能。它可以在 `DEMO_MODE = True` 下端到端运行（无需交互输入），或者在 `DEMO_MODE = False` 采用真实的 `input()` 提示。注意：在 DEMO_MODE 下第三个目标的重试是预设的脚本以便机制端到端可见。真实的修订驱动重分类需要 `DEMO_MODE = False` 并由操作员执行。

 **不在本课范围（在其他课程中讲解）：** 认证与访问控制（第06课 README 的威胁2）、工具调用中间件（第14课 MAF 深入解析）、多 Agent 辩论模式。

### 代码单元格 2

配置加载：从本地环境读取端点与部署名；缺少变量时先修复配置，不要把密钥写进代码。

```python
import json
import os
from datetime import datetime, timezone
from pathlib import Path

from dotenv import load_dotenv
from azure.identity import DefaultAzureCredential, get_bearer_token_provider
from openai import OpenAI

load_dotenv()

DEMO_MODE = True  # set False to use real input() prompts

# Per-run unique log filename so demo runs don't overwrite each other and
# the notebook doesn't touch any pre-existing gate_log.jsonl in the working
# directory.
GATE_LOG_PATH = Path(
    f"gate_log_{datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')}.jsonl"
)

# This notebook uses the Azure OpenAI Responses API via the stable /openai/v1/ endpoint.
# GitHub Models is deprecated (retiring July 2026) and does not support the Responses API.
endpoint = os.environ.get("AZURE_OPENAI_ENDPOINT", "")
if not endpoint:
    raise RuntimeError(
        "AZURE_OPENAI_ENDPOINT environment variable is not set. This notebook needs "
        "an Azure OpenAI resource with a model deployment that supports the Responses "
        "API. Set AZURE_OPENAI_ENDPOINT and AZURE_OPENAI_DEPLOYMENT in "
        "your environment or a local .env file, then run `az login`."
    )

deployment = os.environ["AZURE_OPENAI_DEPLOYMENT"]

# Authenticate with Entra ID (run `az login` first). No api_version is needed.
token_provider = get_bearer_token_provider(
    DefaultAzureCredential(),
    "https://cognitiveservices.azure.com/.default",
)

client = OpenAI(
    base_url=f"{endpoint.rstrip('/')}/openai/v1/",
    api_key=token_provider,
)
```

## 模式 1：预先操作门控

README 中的 HITL 代码片段先调用 Agent，然后请求用户批准输出。这是一个 **后操作** 流程。Agent 已经执行，因此 LLM 调用费用已支付，任何副作用（发送的邮件、写入的数据库行、发布的评论）也已经发生。

 **预先操作** 流程则是在 Agent 运行风险步骤之前插入门控。Agent 提出操作，门控决定是否执行，只有在批准后副作用才会发生。

| 方面 | 后操作审批（README 代码片段） | 预先操作门控（此笔记本） |
|---|---|---|
| 何时运行审批？ | Agent 已生成输出后 | 在任何副作用执行前 |
| 拒绝时的 LLM 费用 | 已支付 | 仅为提议支付，不为操作支付 |
| 不可逆的副作用 | 可能（操作已发生） | 已防止 |
| 审计清晰度 | 审批是打印语句 | 审批是带有时间戳、操作、原因的 JSON 记录 |

### 代码单元格 4

输出观察：print 展示应用可观察结果；预存输出和现场结果可能不同，它不是模型内部思考记录。

```python
def gate_action(action_description: str, risk_tier: str, attempt: int = 0) -> dict:
    """Run a single pre-action gate.

    Returns a decision dict with keys: decision, reason, ts.
    Decision is one of: approve, deny, escalate.
    Safe default on EOF or unexpected input is deny.

    DEMO_MODE behavior: high-risk actions are denied on attempt 0 and
    auto-approved on attempt >= 1. This is scripted approval to show the
    loop mechanics (deny -> retry -> approve). It is NOT revision-driven
    re-classification. Real revision-driven re-classification requires
    DEMO_MODE=False and a human operator who evaluates the revised
    proposal on its own merits.
    """
    print(f"[gate] proposed action ({risk_tier}, attempt={attempt}): {action_description}")

    if DEMO_MODE:
        if risk_tier == "high":
            decision = "approve" if attempt >= 1 else "deny"
            reason = (
                "DEMO_MODE: scripted approval on retry to show loop mechanics"
                if attempt >= 1
                else "DEMO_MODE: high risk denied on first attempt"
            )
        else:
            decision = "approve"
            reason = f"DEMO_MODE canned response for tier={risk_tier}"
    else:
        try:
            raw = input("[gate] approve / deny / escalate? ").strip().lower()
        except EOFError:
            raw = ""
        if raw in {"approve", "deny", "escalate"}:
            decision, reason = raw, "operator input"
        elif raw == "":
            decision, reason = "deny", "no input received, defaulted to deny"
        else:
            decision, reason = "deny", f"invalid input {raw!r}, defaulted to deny"

    return {
        "decision": decision,
        "reason": reason,
        "action": action_description,
        "risk_tier": risk_tier,
        "ts": datetime.now(timezone.utc).isoformat(),
    }
```

## 模式 2：风险分级

并非所有操作都需要人工批准。只读查询公共 API 的风险与发送客户邮件的风险不同。将两者一视同仁会浪费操作人员的注意力并减慢 Agent 速度。

一个简单的三层模型：

| 层级 | 示例 | 审批流程 |
|---|---|---|
| `低`（只读） | 搜索知识库，查询航班选项，抓取公共网页 | 自动执行，记录以供审计 |
| `中`（低成本变更） | 缓存结果，计数器递增，安排提醒 | 自动执行，但每日批量复审 |
| `高`（面向外部或不可逆） | 发送电子邮件，扣款，发布到公共频道 | 阻塞，需人工审批 |

这是一种分级方法。生产系统通常使用更细粒度的层级（例如，AWS IAM 权限级别、基于角色的访问层级）。下面的三层版本是适用于混合只读和副作用操作的 Agent 的最小实用版本。

下面的分类器使用关键词启发式，确保演示保持确定性和低成本。在生产系统中，你会用训练好的分类器或策略引擎替代它。

### 代码单元格 6

检索过程：跟踪查询、候选结果和实际选入的证据；检索为空时应明确返回缺失，而不是补写答案。

```python
LOW_RISK_KEYWORDS = {
    "look", "lookup", "search", "fetch", "read", "query", "view",
    "get", "list", "weather", "summarize",
}
HIGH_RISK_KEYWORDS = {
    "send", "email", "post", "publish", "charge", "pay", "transfer",
    "delete", "drop", "cancel", "refund",
}
MEDIUM_RISK_KEYWORDS = {
    "cache", "schedule", "reminder", "book", "reserve", "update",
    "increment", "log",
}

AUTO_APPROVE_REASONS = {
    "low": "auto-approved (low risk)",
    "medium": "auto-approved (medium risk, queued for batched review)",
}


def classify_risk(action: str) -> str:
    """Classify an action string into one of: low, medium, high.

    Keyword-based heuristic. Checks high-risk first (most severe), then
    low-risk explicit reads, then medium-risk mutations. Unrecognized
    actions default to medium, not low.

    Default for unrecognized actions is 'medium', not 'low'. A read-only
    keyword set will always have blind spots, and the parent README's
    threat list (critical-system access, knowledge-base poisoning,
    cascading errors) all involve cases an action-name alone cannot rule
    out. Routing unknown actions through batched review is the safer
    default than auto-executing them.
    """
    text = action.lower()
    if any(kw in text for kw in HIGH_RISK_KEYWORDS):
        return "high"
    if any(kw in text for kw in LOW_RISK_KEYWORDS):
        return "low"
    if any(kw in text for kw in MEDIUM_RISK_KEYWORDS):
        return "medium"
    # Explicit fail-safe default: unrecognized actions route to batched review.
    return "medium"


def tiered_gate(action: str, attempt: int = 0) -> dict:
    """Classify then gate. Low and medium tiers auto-approve; high blocks."""
    tier = classify_risk(action)
    if tier in AUTO_APPROVE_REASONS:
        return {
            "decision": "approve",
            "reason": AUTO_APPROVE_REASONS[tier],
            "action": action,
            "risk_tier": tier,
            "ts": datetime.now(timezone.utc).isoformat(),
        }
    return gate_action(action, tier, attempt=attempt)
```

## 模式 3：审计日志和修订循环

一个 `print("Response approved.")` 不是审计日志。为了建立信任，每个门禁决策都应该作为结构化事件记录，你可以稍后查询、重放或附加到事件审查中。

两个部分：

1. **仅追加的 JSONL。** 每个决策一行，包含时间戳、操作、层级、决策、原因。易于 grep，之后也容易发送到真正的日志存储中。
2. **拒绝时的修订循环。** 当门禁返回 `deny` 时，Agent 会在上下文中带入拒绝原因重新提示自己，以便下一次提案能避免该问题。

### 代码单元格 8

阅读提示：跟踪本单元格读取的变量、修改的状态以及返回值。按原顺序执行，确认依赖的前序变量已经存在。

```python
def log_decision(decision: dict) -> None:
    """Append a gate decision to the JSONL audit log."""
    with GATE_LOG_PATH.open("a", encoding="utf-8") as f:
        f.write(json.dumps(decision) + "\n")


def propose_action(goal: str, prior_rejection: str | None = None) -> str:
    """Ask the LLM to propose a concrete next action for a goal.

    If prior_rejection is provided, it is fed back so the LLM can avoid
    the same failure mode in the next proposal.
    """
    system = (
        "You are an action planner for an agent. Propose ONE concrete next\n"
        "action (a single sentence) toward the user's goal. If a prior\n"
        "rejection reason is given, propose a different action that addresses\n"
        "the rejection."
    )
    user_text = f"Goal: {goal}"
    if prior_rejection:
        user_text += f"\n\nPrior proposal was denied. Reason: {prior_rejection}"

    response = client.responses.create(
        model=deployment,
        input=[
            {"role": "system", "content": system},
            {"role": "user", "content": user_text},
        ],
        store=False,
    )
    return response.output_text.strip()


def run_with_revision(goal: str, max_revisions: int = 2) -> dict:
    """Propose, gate, and on rejection revise up to max_revisions times."""
    prior_reason: str | None = None
    for attempt in range(max_revisions + 1):
        action = propose_action(goal, prior_rejection=prior_reason)
        decision = tiered_gate(action, attempt=attempt)
        decision["attempt"] = attempt
        log_decision(decision)
        if decision["decision"] == "approve":
            return decision
        prior_reason = decision["reason"]
    return {**decision, "final": "max_revisions_reached"}
```

### 代码单元格 9

输出观察：print 展示应用可观察结果；预存输出和现场结果可能不同，它不是模型内部思考记录。

```python
# End-to-end demo: three goals at three different risk profiles.
# GATE_LOG_PATH is per-run (timestamped) so no prior log is touched.

goals = [
    "Look up the weather in Seattle for the customer's trip planning.",
    "Schedule a reminder for the customer to check in 24 hours before their flight.",
    "Send a marketing email to the customer about premium upgrade options.",
]

for goal in goals:
    print(f"\n=== Goal: {goal} ===")
    outcome = run_with_revision(goal, max_revisions=1)
    print(f"[final] {outcome['decision']} ({outcome['reason']})")

print(f"\n=== Audit log ({GATE_LOG_PATH.name}) ===")
for line in GATE_LOG_PATH.read_text(encoding="utf-8").splitlines():
    record = json.loads(line)
    print(f"  [{record['risk_tier']:6s}] {record['decision']:8s} "
          f"attempt={record.get('attempt', '?')} action={record['action'][:140]}")
```

## 额外资源

其他几个公共项目实现了这些 HITL 模式的各种变体。比较不同方法，找到适合你技术栈的：

- **LangChain** 人类在环工具封装 ([docs](https://python.langchain.com/docs/integrations/tools/human_tools)): 可即插即用的工具封装，暂停执行等待人类输入。
- **AutoGen** `UserProxyAgent` ([v0.2 docs](https://microsoft.github.io/autogen/0.2/docs/topics/human-in-the-loop); AutoGen v0.4+ 重构了此部分): 使用 Agent 角色专门代表多 Agent 对话中的人类。
- **Microsoft Agent Framework (MAF)** 函数调用中间件 ([docs](https://learn.microsoft.com/agent-framework/)): 在每个工具/函数调用周围运行的中间件，适合用于门控逻辑和审批流程。

每个项目对三种子模式的处理方式不同：LangChain 将它们封装为工具，AutoGen 使用 Agent 角色，Microsoft Agent Framework 则使用函数调用中间件。在选择自己 Agent 的设计之前，请完整阅读一个或两个实现方案。


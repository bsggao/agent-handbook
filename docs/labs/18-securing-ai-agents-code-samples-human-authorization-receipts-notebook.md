---
title: "18 · human-authorization-receipts"
outline: [2, 3]
---

# 18 · human-authorization-receipts

[返回：Agent 安全](/lessons/security.md) · [不可变原始文件](https://github.com/microsoft/ai-agents-for-beginners/blob/25b7985f3b2dc37a84f4a7387ccd3c9f0e5b1595/18-securing-ai-agents/code_samples/human-authorization-receipts.ipynb)

::: warning 原课程完整 Notebook · 静态阅读与代码解析
代码按英文源文件顺序保留，中文说明以同版本译本为基础。原始安装单元格可能含无版本上限的 `-U`；请跳过它们，先按[准备篇](/lessons/setup.md)固定依赖。云端服务、模型权限、网站布局和部分 SDK 接口需在你自己的环境验证。本站没有执行云端请求；第 18 章的离线验证状态单独记录在[检查报告](/guide/verification.md)。
:::

## 运行准备

Python 3.12+；在独立虚拟环境安装源仓库依赖与本页中声明的额外依赖。原文件路径：`upstream/18-securing-ai-agents/code_samples/human-authorization-receipts.ipynb`。以原仓库根目录为工作目录，在 Jupyter 中按顺序执行；身份与环境变量见准备篇。

```bash
cd upstream
python -m jupyterlab
```

[下载原始 Notebook](/notebooks/18-securing-ai-agents/code_samples/human-authorization-receipts.ipynb)。输出为上游文件保存的历史结果，不能用作本站实测证明。

## 第18课（后续）：证明*人类*授权操作的收据

本课证明了 **Agent** 所做的操作和 **网关** 的决定。该笔记本补充了缺失的一半内容：证明 **指定人类** 批准了 **确切** 操作——即对完整规范操作的单独人类持有签名，离线验证。

此处的两个工件使用了 **与课程收据相同的信封结构** ：一个带有`type`字段的扁平负载，由 Ed25519 直接对 JCS 规范负载字节签名，并附带结构化的`signature`对象（该对象未包含在签名字节中）。批准收据是一个新的`type`（`human.approval.v1`），与操作类型并列，因此一个`verify_chain`调用即可使用你在主笔记本中构建的相同代码路径验证这两种工件。这是本课自行定义的教学组合，不宣称符合独立 Internet-Draft（draft-farley-acta-signed-receipts）的线格式。

相较主笔记本中的演示验证器，这里故意进行了升级：验证器通过 **固定密钥注册表** 解析`signature.key_id`，而不是信任收据内携带的公钥。这是本课程自身清单推荐的生产态度（“发布验证公钥”），也是使伪造成为拒绝而非自带密钥绕过的根本原因。

本笔记本教授的规则： **签名的批准本身不是授权。** 只有在执行时，批准收据和操作收据仍然绑定同一规范操作，且政策版本、密钥和有效期均仍有效，批准尚未被使用，才存在授权。每次失败都会以 **不同原因** 拒绝，因此你可以区分*授权已过期*与*执行的操作已改变*。

### 代码单元格 2

签名操作：私钥仅用于签名，验签必须使用独立信任的公钥；不要把收据自带的公钥直接当成可信身份。

```python
# These are already the Lesson 18 dependencies — no new packages.
# %pip install pynacl jcs
import base64, copy, hashlib
from jcs import canonicalize                      # RFC 8785 canonical JSON
from nacl.signing import SigningKey, VerifyKey
# CryptoError is the common base of BadSignatureError AND the ValueError pynacl
# raises for a wrong-length signature — catch the base so verification fails
# closed on ANY bad signature, not just the forged-but-correct-length one.
from nacl.exceptions import CryptoError

# Same helpers as the main notebook.
def b64url_nopad(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).decode("ascii").rstrip("=")

def b64url_decode(s: str) -> bytes:
    return base64.urlsafe_b64decode(s + "=" * ((4 - len(s) % 4) % 4))

def sha256_canonical(obj) -> str:
    """SHA-256 of an object's JCS-canonical JSON form (same helper as the lesson)."""
    return f"sha256:{hashlib.sha256(canonicalize(obj)).hexdigest()}"
```

## 精确的操作

批准的单位是 **规范操作对象** ——而不是像“批准退款”这样模糊的标签，而是精确、完全指定的操作。对整个对象进行签署（并从中得出摘要）使我们能够在以后证明该人批准了*此操作*而非其他任何操作。

### 代码单元格 4

输出观察：print 展示应用可观察结果；预存输出和现场结果可能不同，它不是模型内部思考记录。

```python
action = {
    "action_type": "refund.issue",
    "params": {"order_id": "A-1029", "amount_usd": 4200, "to": "acct_88"},
    "policy_id": "refunds-v3",
}
print("action digest:", sha256_canonical(action))
```

::: details 原文件保存的输出（不是本项目实测）

```text
action digest: sha256:fba342ad8447b491a089d7a09d4ac58f1a835c504e58f8d832db04f65bb62a25
```

:::

## 一个信封，两个权威

每个收据都是课程的信封：一个带有 `type` 字段的平面有效载荷，加上一个 `signature` 对象（`alg`，`sig`，`key_id`），它 **不是** 签名字节的一部分。`verify_envelope` 是两个收据种类共有的结构和签名检查；它将 `signature.key_id` 解析到哪个 **固定密钥注册表** ，这就是区分权威的关键：

- **批准收据** （`human.approval.v1`）— 指定批准人，完整的规范操作 **及其摘要** ，`policy_version`，发行时间戳和过期时间戳。一次性消费在链级别跟踪。
- **操作收据** （`agent.action.v1`）— Agent 身份，`run_id`，同样的规范操作 **摘要** ，执行结果及时间戳，以及 `parent_approval_ref`：批准的 `receipt_hash`，与课程链中 `previous_receipt_hash` 的惯例相同。

共享的 `action_digest` 字段是绑定所依赖的连接点。`key_id` 仅作为查找提示存在于签名对象中：将其指向不同的固定密钥会导致签名检查失败，因此它不赋予任何权限。

### 代码单元格 6

签名操作：私钥仅用于签名，验签必须使用独立信任的公钥；不要把收据自带的公钥直接当成可信身份。

```python
# ---- pinned key registries: SEPARATE authorities, one envelope shape ----------
# Published out of band (the lesson checklist's JWK-Set pattern); the verifier
# NEVER trusts a key carried inside a receipt.
approver_sk = SigningKey.generate()
agent_sk    = SigningKey.generate()
APPROVER_KEYS = {"approver-key-1": b64url_nopad(bytes(approver_sk.verify_key))}
AGENT_KEYS    = {"agent-key-1":    b64url_nopad(bytes(agent_sk.verify_key))}

# The policy the approval is granted under. If this moves after approval, the
# approval is STALE even though its signature still verifies.
CURRENT_POLICY = {"policy_version": "refunds-v3"}

def sign_receipt(payload: dict, sk: SigningKey, key_id: str) -> dict:
    """Same signing pipeline as the lesson: Ed25519 over the canonical JCS
    bytes directly; the signature object is NOT part of the signed bytes."""
    canonical = canonicalize(payload)
    return {
        **payload,
        "signature": {"alg": "EdDSA", "sig": b64url_nopad(sk.sign(canonical).signature), "key_id": key_id},
    }

def verify_envelope(receipt, expected_type: str, trusted_keys: dict):
    """The SHARED verifier contract for any receipt kind; the caller picks which
    pinned registry (authority) resolves key_id. Fails closed on ANY
    attacker-shaped input: malformed is a refusal, never a crash."""
    if not isinstance(receipt, dict) or not isinstance(receipt.get("signature"), dict):
        return (False, "receipt malformed (not an object with a signature object)")
    sig_obj = receipt["signature"]
    if sig_obj.get("alg") != "EdDSA":
        return (False, "unsupported signature alg")
    if receipt.get("type") != expected_type:
        return (False, f"wrong receipt type (expected {expected_type})")
    # Key freshness is part of authority: a key_id rotated out of the pinned
    # registry confers nothing, even with a valid signature.
    pub = trusted_keys.get(sig_obj.get("key_id"))
    if pub is None:
        return (False, f"stale authority: key_id {sig_obj.get('key_id')!r} is not in the pinned registry (unknown or rotated out)")
    # Reconstruct the signed bytes exactly as the lesson does: everything except
    # the signature object, canonicalized and passed directly to Ed25519.
    payload = {k: v for k, v in receipt.items() if k != "signature"}
    try:
        canonical = canonicalize(payload)
        VerifyKey(b64url_decode(pub)).verify(canonical, b64url_decode(sig_obj.get("sig") or ""))
    except (CryptoError, TypeError, ValueError, base64.binascii.Error):
        return (False, "signature invalid (forged, tampered, or malformed)")
    return (True, "envelope ok")

def human_approval(action, approver_id, approved_at, sk=approver_sk,
                   key_id="approver-key-1", policy_version=None, expires_at=None):
    # deepcopy: the receipt must be an immutable record of what was approved —
    # a live reference would let a later mutation of `action` silently change the
    # signed payload. Digest the SNAPSHOT so the two can never diverge.
    approved_action = copy.deepcopy(action)
    payload = {
        "type": "human.approval.v1",
        "approver_id": approver_id,
        "action": approved_action,                       # the FULL canonical action
        "action_digest": sha256_canonical(approved_action),  # the join field
        "policy_version": policy_version or CURRENT_POLICY["policy_version"],
        "approved_at": approved_at,                      # ISO-8601 Zulu, like the lesson
        "expires_at": expires_at or approved_at[:11] + "23:59:59Z",
    }
    return sign_receipt(payload, sk, key_id)
```

### 代码单元格 7

输出观察：print 展示应用可观察结果；预存输出和现场结果可能不同，它不是模型内部思考记录。

```python
approval = human_approval(action, "alice@ops (WebAuthn)", "2026-07-08T15:04:05Z",
                          expires_at="2026-07-08T15:19:05Z")
print(verify_envelope(approval, "human.approval.v1", APPROVER_KEYS))
print("binds digest:", approval["action_digest"][:23], "…  under", approval["policy_version"])
```

::: details 原文件保存的输出（不是本项目实测）

```text
(True, 'envelope ok')
binds digest: sha256:fba342ad8447b491 …  under refunds-v3
```

:::

## `verify_chain`：实际决定绑定的地方

`verify_chain` **不是** 两个签名检查的便捷封装。它是唯一一个地方，在这里共享的规范化 `action_digest`、批准的策略/密钥/过期的 **新鲜度** 以及批准的 **一次性消费** 都会一起针对*当前*执行的操作进行检查。

每个失败都会以 **不同的原因** 拒绝，因此拒绝的读者可以判断权限是否变得陈旧（策略变动、密钥轮换、批准过期、批准已消费）或执行的操作是否在仍有效的批准下发生了更改（摘要替换）。

### 代码单元格 9

链式记录：核对前序收据的规范字节哈希，并另外验证各签名；链头需要可信外部锚点才能发现整段截断。

输出观察：print 展示应用可观察结果；预存输出和现场结果可能不同，它不是模型内部思考记录。

```python
def receipt_hash(receipt: dict) -> str:
    """Content-derived id of a COMPLETE receipt (including its signature) —
    the same convention as previous_receipt_hash in the lesson's chain."""
    return sha256_canonical(receipt)

def agent_receipt(action, approval, executed_at, sk=agent_sk, key_id="agent-key-1"):
    executed_action = copy.deepcopy(action)    # snapshot, same reason as the approval
    payload = {
        "type": "agent.action.v1",
        "agent_id": "agent:refunds-bot",
        "run_id": "run-0001",
        "action": executed_action,
        "action_digest": sha256_canonical(executed_action),  # same join field
        "parent_approval_ref": receipt_hash(approval),
        "outcome": "performed",
        "executed_at": executed_at,
    }
    return sign_receipt(payload, sk, key_id)

_consumed = set()

def verify_chain(action_being_executed, approval, agent_rcpt, now: str):
    """One code path covers both receipt kinds (same envelope), then checks the
    things that only make sense TOGETHER: shared digest, freshness, consumption.
    `now` is an ISO-8601 Zulu timestamp; Zulu strings compare correctly as strings."""
    # 1. Shared envelope contract, separate authorities.
    ok, why = verify_envelope(approval, "human.approval.v1", APPROVER_KEYS)
    if not ok: return (False, f"approval: {why}")
    ok, why = verify_envelope(agent_rcpt, "agent.action.v1", AGENT_KEYS)
    if not ok: return (False, f"agent receipt: {why}")

    # 2. The join: BOTH receipts must bind the digest of the action being executed
    #    right now. A valid approval for a DIFFERENT action is substitution, and it
    #    gets its own reason — this is "the executed action changed".
    executing_digest = sha256_canonical(action_being_executed)
    if approval.get("action_digest") != executing_digest or approval.get("action") != action_being_executed:
        return (False, "digest substitution: the approval binds a different canonical action than the one being executed")
    if agent_rcpt.get("action_digest") != executing_digest or agent_rcpt.get("action") != action_being_executed:
        return (False, "digest substitution: the agent receipt binds a different canonical action than the one being executed")
    if agent_rcpt.get("parent_approval_ref") != receipt_hash(approval):
        return (False, "agent receipt is not bound to this approval")

    # 3. Freshness: a valid signature over stale authority is still a refusal —
    #    each staleness gets its own reason, distinct from substitution above.
    if approval.get("policy_version") != CURRENT_POLICY["policy_version"]:
        return (False, f"stale authority: approved under policy {approval.get('policy_version')!r}, current is {CURRENT_POLICY['policy_version']!r}")
    expires = approval.get("expires_at")
    if not isinstance(expires, str) or not expires or now >= expires:
        return (False, "stale authority: approval expired before execution")

    # 4. One-time consumption: an approval authorizes ONE execution.
    ref = receipt_hash(approval)
    if ref in _consumed:
        return (False, "approval already consumed (replay refused)")
    _consumed.add(ref)
    return (True, f"approved by {approval['approver_id']}, executed by {agent_rcpt['agent_id']}")

def execute(action, approval, agent_rcpt, now):
    ok, why = verify_chain(action, approval, agent_rcpt, now)
    return (ok, "executed" if ok else why)

receipt = agent_receipt(action, approval, "2026-07-08T15:04:06Z")
print(execute(action, approval, receipt, now="2026-07-08T15:04:07Z"))
```

::: details 原文件保存的输出（不是本项目实测）

```text
(True, 'executed')
```

:::

## 绑定捕获的内容

以下每种情况都会以 **不同的原因** 失败 **关闭** 。第一个块是经典集合（篡改、混淆 Agent、重放、任何权限的伪造、格式错误的输入）。第二个块是一对使属性成为真实而非断言的情况：

- **过时的权限** — 签名仍然有效，但策略版本已更改，审批者密钥已从固定注册表中轮换，或执行前审批已过期；
- **摘要替换** — 一个有效签名的操作收据，其 `parent_approval_ref` 指向一个*真实*的审批，但该审批的规范操作摘要与实际执行的操作不匹配。

### 代码单元格 11

签名操作：私钥仅用于签名，验签必须使用独立信任的公钥；不要把收据自带的公钥直接当成可信身份。

输出观察：print 展示应用可观察结果；预存输出和现场结果可能不同，它不是模型内部思考记录。

```python
NOW = "2026-07-08T15:05:00Z"

# 1. tamper: change the amount after approval — the executed action changed.
tampered = {**action, "params": {**action["params"], "amount_usd": 9900}}
print("tamper              ->", verify_chain(tampered, approval, agent_receipt(tampered, approval, NOW), NOW))

# 2. confused deputy: valid approval for action A, presented to execute action B.
action_b = {**action, "action_type": "wire.send"}
print("confused-deputy     ->", verify_chain(action_b, approval, agent_receipt(action_b, approval, NOW), NOW))

# 3. replay: the approval was consumed by the successful execution above.
print("replay              ->", execute(action, approval, agent_receipt(action, approval, NOW), NOW))

# 4. forged approval: attacker signs with their own key but claims a pinned key_id.
mallory_sk = SigningKey.generate()
forged = human_approval(action, "mallory", NOW, sk=mallory_sk)
print("forged-approval     ->", verify_chain(action, forged, agent_receipt(action, forged, NOW), NOW))

# A fresh, un-consumed approval so the agent-side cases fail on their OWN check.
fresh = human_approval(action, "alice@ops (WebAuthn)", NOW, expires_at="2026-07-08T15:20:00Z")

# 5. self-minted agent receipt: attacker's own agent key, refused by the pinned registry.
mallory_agent = agent_receipt(action, fresh, NOW, sk=SigningKey.generate())
print("self-minted-agent   ->", verify_chain(action, fresh, mallory_agent, NOW))

# 6. wrong-action agent receipt: real agent key, but the receipt binds a different action.
wrong_action = {**action, "params": {**action["params"], "amount_usd": 9900}}
print("wrong-action-agent  ->", verify_chain(action, fresh, agent_receipt(wrong_action, fresh, NOW), NOW))

# 7. malformed input: structurally broken receipts refuse cleanly, they never crash.
print("malformed-approval  ->", verify_chain(action, {"type": "human.approval.v1"}, agent_receipt(action, fresh, NOW), NOW))
print("malformed-agent     ->", verify_chain(action, fresh, {"nope": "not a receipt"}, NOW))

# 8. wrong-length signature: valid base64, not 64 bytes — refused, not crashed.
badlen = {**fresh, "signature": {**fresh["signature"], "sig": "AAAA"}}
print("wrong-len-sig       ->", verify_chain(action, badlen, agent_receipt(action, fresh, NOW), NOW))

# 9. non-object receipt: a list refuses cleanly instead of raising AttributeError.
print("nonobject-receipt   ->", verify_chain(action, [1, 2], agent_receipt(action, fresh, NOW), NOW))

print()
print("--- the two negative controls that make the property real ---")

# 10. STALE POLICY: signature still valid, but policy moved between approval and
#     execution. Authority is decided at execution time, not signing time.
CURRENT_POLICY["policy_version"] = "refunds-v4"
print("stale-policy        ->", verify_chain(action, fresh, agent_receipt(action, fresh, NOW), NOW))
CURRENT_POLICY["policy_version"] = "refunds-v3"   # restore for the cases below

# 11. STALE KEY: the approver key is rotated out of the pinned registry after
#     signing. The signature bytes still verify against the old key — but the old
#     key no longer confers authority.
rotated_out = APPROVER_KEYS.pop("approver-key-1")
print("stale-key           ->", verify_chain(action, fresh, agent_receipt(action, fresh, NOW), NOW))
APPROVER_KEYS["approver-key-1"] = rotated_out     # restore

# 12. EXPIRED: approval was valid when signed, but execution came too late.
expired = human_approval(action, "alice@ops (WebAuthn)", "2026-07-08T14:00:00Z",
                         expires_at="2026-07-08T14:01:00Z")
print("expired-approval    ->", verify_chain(action, expired, agent_receipt(action, expired, NOW), NOW))

# 13. DIGEST SUBSTITUTION: a validly signed agent receipt whose parent_approval_ref
#     points at a REAL approval — but that approval binds action B, and the agent
#     is executing action A. Distinct reason from every staleness above.
approval_b = human_approval(action_b, "alice@ops (WebAuthn)", NOW, expires_at="2026-07-08T15:20:00Z")
substituted = agent_receipt(action, approval_b, NOW)   # executing `action`, ref -> approval of action_b
print("digest-substitution ->", verify_chain(action, approval_b, substituted, NOW))
```

::: details 原文件保存的输出（不是本项目实测）

```text
tamper              -> (False, 'digest substitution: the approval binds a different canonical action than the one being executed')
confused-deputy     -> (False, 'digest substitution: the approval binds a different canonical action than the one being executed')
replay              -> (False, 'approval already consumed (replay refused)')
forged-approval     -> (False, 'approval: signature invalid (forged, tampered, or malformed)')
self-minted-agent   -> (False, 'agent receipt: signature invalid (forged, tampered, or malformed)')
wrong-action-agent  -> (False, 'digest substitution: the agent receipt binds a different canonical action than the one being executed')
malformed-approval  -> (False, 'approval: receipt malformed (not an object with a signature object)')
malformed-agent     -> (False, 'agent receipt: receipt malformed (not an object with a signature object)')
wrong-len-sig       -> (False, 'approval: signature invalid (forged, tampered, or malformed)')
nonobject-receipt   -> (False, 'approval: receipt malformed (not an object with a signature object)')

--- the two negative controls that make the property real ---
stale-policy        -> (False, "stale authority: approved under policy 'refunds-v3', current is 'refunds-v4'")
stale-key           -> (False, "approval: stale authority: key_id 'approver-key-1' is not in the pinned registry (unknown or rotated out)")
expired-approval    -> (False, 'stale authority: approval expired before execution')
digest-substitution -> (False, 'digest substitution: the approval binds a different canonical action than the one being executed')
```

:::

## 这证明了什么——以及什么没有被证明

 **证明了：** 一个具名人类批准了*这个确切的规范操作*（完整操作 + 摘要，由从固定注册表解析的密钥签名），且 Agent 执行了*完全相同的获批操作*（相同摘要，凭据通过 `receipt_hash` 绑定到批准，即本课的链式惯例）——在批准的策略版本、密钥和有效期仍然有效时，仅执行一次。如果任一方发生改变，链条将安全关闭，拒绝理由将告诉你 **哪个** 属性出错：过期权限或操作变更。

 **未证明：** 批准界面是否向用户展示了他们以为自己在签署的内容（所见即所得自身是个问题），密钥在轮换前是否被胁迫或盗用，或者下游效果是否与操作匹配。签名 ≠ 授权：对过期策略、已轮换密钥、已逾期窗口或不同摘要的有效签名，在此不构成任何权利。

这两种凭据类型有意共享本课的信封和一个 `verify_chain` 代码路径：你为操作凭据构建的绑定正是在主笔记本中检查人类批准的相同代码。一个验证者合约，分开的固定权限，通过规范操作摘要连接，别无他物。


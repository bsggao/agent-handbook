---
title: "18 · 18-signed-receipts"
outline: [2, 3]
---

# 18 · 18-signed-receipts

[返回：Agent 安全](/lessons/security.md) · [不可变原始文件](https://github.com/microsoft/ai-agents-for-beginners/blob/25b7985f3b2dc37a84f4a7387ccd3c9f0e5b1595/18-securing-ai-agents/code_samples/18-signed-receipts.ipynb)

::: warning 原课程完整 Notebook · 静态阅读与代码解析
代码按英文源文件顺序保留，中文说明以同版本译本为基础。原始安装单元格可能含无版本上限的 `-U`；请跳过它们，先按[准备篇](/lessons/setup.md)固定依赖。云端服务、模型权限、网站布局和部分 SDK 接口需在你自己的环境验证。本站没有执行云端请求；第 18 章的离线验证状态单独记录在[检查报告](/guide/verification.md)。
:::

## 运行准备

Python 3.12+；在独立虚拟环境安装源仓库依赖与本页中声明的额外依赖。原文件路径：`upstream/18-securing-ai-agents/code_samples/18-signed-receipts.ipynb`。以原仓库根目录为工作目录，在 Jupyter 中按顺序执行；身份与环境变量见准备篇。

```bash
cd upstream
python -m jupyterlab
```

[下载原始 Notebook](/notebooks/18-securing-ai-agents/code_samples/18-signed-receipts.ipynb)。输出为上游文件保存的历史结果，不能用作本站实测证明。

## 课程18：使用密码学收据保障AI Agent 安全

## 实践笔记本

本笔记本演示了四个练习：

1. **为 Agent 工具调用签署你的第一个收据** 并验证它。
2. **篡改收据** 并观察验证失败。
3. **构建三张收据链** 并确认链的完整性。
4. **封装Microsoft Agent Framework工具调用** ，使每个操作都生成收据。

所有加密原语均从维护良好的库导入（`pynacl` 用于 Ed25519，`jcs` 用于 RFC 8785 规范JSON，`hashlib` 来自Python标准库用于SHA-256）。收据逻辑本身是纯Python代码，你可以阅读和修改。

按顺序运行代码单元。每个部分简短且独立。

## 安装

安装这两个依赖。它们都具有宽松的许可证（Apache-2.0 / MIT）。

### 代码单元格 3

阅读提示：跟踪本单元格读取的变量、修改的状态以及返回值。按原顺序执行，确认依赖的前序变量已经存在。

```text
%pip install -q pynacl jcs
```

::: details 原文件保存的输出（不是本项目实测）

```text
WARNING: Cache entry deserialization failed, entry ignored
WARNING: Cache entry deserialization failed, entry ignored

Note: you may need to restart the kernel to use updated packages.
```

:::

### 代码单元格 4

阅读提示：跟踪本单元格读取的变量、修改的状态以及返回值。按原顺序执行，确认依赖的前序变量已经存在。

```python
import json
import hashlib
import base64
from datetime import datetime, timezone

from nacl import signing
from nacl.exceptions import BadSignatureError
from jcs import canonicalize
```

## 辅助工具

这两个辅助工具处理base64url编码（无填充）和任意对象的SHA-256哈希。它们使笔记本的其余部分专注于收据逻辑本身。

### 代码单元格 6

阅读提示：跟踪本单元格读取的变量、修改的状态以及返回值。按原顺序执行，确认依赖的前序变量已经存在。

```python
def b64url_nopad(data: bytes) -> str:
    """Base64url-encode bytes without padding (RFC 4648 Section 5)."""
    return base64.urlsafe_b64encode(data).decode("ascii").rstrip("=")

def b64url_decode(s: str) -> bytes:
    """Decode a base64url string that may be missing padding."""
    padding = "=" * ((4 - len(s) % 4) % 4)
    return base64.urlsafe_b64decode(s + padding)

def sha256_canonical(obj) -> str:
    """
    SHA-256 hash of a Python object, computed over its JCS-canonical JSON form.
    Returns a 'sha256:' prefixed hex digest so callers can identify the algorithm.
    """
    canonical = canonicalize(obj)
    digest = hashlib.sha256(canonical).hexdigest()
    return f"sha256:{digest}"
```

## 第1节：签署你的第一张收据

想象一下，我们的 **Contoso Travel** Agent 刚刚为客户查询了从悉尼到洛杉矶的航班。我们希望将此工具调用记录为签署的收据，以便未来的审核员无需信任我们即可验证。

### 第1.1步：生成签名密钥

在生产环境中，Agent 的签名密钥会存储在硬件安全模块 (HSM)、Azure Key Vault 或类似的受保护存储中。本课程中我们在内存中生成一个新的密钥。

### 代码单元格 8

签名操作：私钥仅用于签名，验签必须使用独立信任的公钥；不要把收据自带的公钥直接当成可信身份。

输出观察：print 展示应用可观察结果；预存输出和现场结果可能不同，它不是模型内部思考记录。

```python
signing_key = signing.SigningKey.generate()
verify_key = signing_key.verify_key

public_key_b64 = b64url_nopad(bytes(verify_key))
print(f"Public key (Ed25519, 32 bytes): {public_key_b64}")
```

::: details 原文件保存的输出（不是本项目实测）

```text
Public key (Ed25519, 32 bytes): g3SyD_ecOKa1L8RQ79-pDy9em81H-O_jzp9VG4a3EP0
```

:::

### 第 1.2 步：构建收据负载

负载包含了我们希望收据证明的一切内容：谁执行了操作，使用了什么工具，带了哪些参数，返回了什么结果，遵循了什么策略，以及何时执行的。我们对参数和结果进行哈希处理，而不是将它们直接包含在内容中，以防收据泄露敏感信息。

### 代码单元格 10

链式记录：核对前序收据的规范字节哈希，并另外验证各签名；链头需要可信外部锚点才能发现整段截断。

输出观察：print 展示应用可观察结果；预存输出和现场结果可能不同，它不是模型内部思考记录。

```python
tool_args = {
    "origin": "SYD",
    "destination": "LAX",
    "departure_date": "2026-06-15",
    "passengers": 2,
}

tool_result = [
    {"flight": "QF11", "price": 1850, "stops": 0},
    {"flight": "UA864", "price": 1620, "stops": 1},
    {"flight": "DL11", "price": 1740, "stops": 0},
]

payload = {
    "type": "agent.tool_call.v1",
    "agent_id": "contoso-travel-bot",
    "tool_name": "lookup_flights",
    "tool_args_hash": sha256_canonical(tool_args),
    "result_hash": sha256_canonical(tool_result),
    "policy_id": "contoso-travel-policy-v3",
    "timestamp": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
    "sequence": 0,
    "previous_receipt_hash": None,
}

print(json.dumps(payload, indent=2))
```

::: details 原文件保存的输出（不是本项目实测）

```text
{
  "type": "agent.tool_call.v1",
  "agent_id": "contoso-travel-bot",
  "tool_name": "lookup_flights",
  "tool_args_hash": "sha256:47578acca4df262c8f172b91493b818a26d042e7beb8e7b121e2bc3776152746",
  "result_hash": "sha256:556447bf01c3c33285086d224b3d6fb4cd7b620b5151fbbebe67e7ff81cdde7a",
  "policy_id": "contoso-travel-policy-v3",
  "timestamp": "2026-08-18T04:55:21Z",
  "sequence": 0,
  "previous_receipt_hash": null
}
```

:::

### 步骤 1.3：签署并组装收据

三个步骤：

1. 使用 JCS 规范化负载，以便两个实现生成相同逻辑收据时产生字节完全相同的字节。
2. 使用 Ed25519 私钥直接对 JCS 规范字节签名；PureEdDSA 内部处理哈希。
3. 将签名放在负载之外的 signature 对象中。

然后将签名附加到原始负载上，生成最终收据。

### 代码单元格 12

签名操作：私钥仅用于签名，验签必须使用独立信任的公钥；不要把收据自带的公钥直接当成可信身份。

输出观察：print 展示应用可观察结果；预存输出和现场结果可能不同，它不是模型内部思考记录。

```python
def sign_receipt(payload: dict, signing_key: signing.SigningKey, verify_key) -> dict:
    """
    Sign a receipt payload. Returns the receipt with attached signature and public key.
    The 'signature' and 'public_key' fields are NOT part of the canonical signed bytes.
    """
    canonical = canonicalize(payload)
    signature_bytes = signing_key.sign(canonical).signature
    return {
        **payload,
        "signature": {
            "alg": "EdDSA",
            "sig": b64url_nopad(signature_bytes),
            "public_key": b64url_nopad(bytes(verify_key)),
        },
    }

receipt = sign_receipt(payload, signing_key, verify_key)
print(json.dumps(receipt, indent=2))
```

::: details 原文件保存的输出（不是本项目实测）

```text
{
  "type": "agent.tool_call.v1",
  "agent_id": "contoso-travel-bot",
  "tool_name": "lookup_flights",
  "tool_args_hash": "sha256:47578acca4df262c8f172b91493b818a26d042e7beb8e7b121e2bc3776152746",
  "result_hash": "sha256:556447bf01c3c33285086d224b3d6fb4cd7b620b5151fbbebe67e7ff81cdde7a",
  "policy_id": "contoso-travel-policy-v3",
  "timestamp": "2026-08-18T04:55:21Z",
  "sequence": 0,
  "previous_receipt_hash": null,
  "signature": {
    "alg": "EdDSA",
    "sig": "Eu3MmrOSdGq2DuemkjNSPKfz5xbr18okNeTU11NJu2usnsnKtC-pjq2PZM1Oap-WXdVgYkL4iW6SeWPSZ2M9BQ",
    "public_key": "g3SyD_ecOKa1L8RQ79-pDy9em81H-O_jzp9VG4a3EP0"
  }
}
```

:::

### 第 1.4 步：验证收据

验证是逆向过程。我们去除签名，重新计算 JCS 规范字节，并使用收据中的公钥验证签名。

进行此验证的审计员除了收据本身外，不需要我们提供任何东西。无需调用服务，无需查询密钥目录，无需信任。

### 代码单元格 14

输出观察：print 展示应用可观察结果；预存输出和现场结果可能不同，它不是模型内部思考记录。

```python
def verify_receipt(receipt: dict) -> bool:
    """
    Verify a receipt's Ed25519 signature.
    Returns True if valid, False otherwise.
    """
    sig_obj = receipt.get("signature")
    if not sig_obj or sig_obj.get("alg") != "EdDSA":
        return False

    # Reconstruct the payload that was actually signed (everything except signature).
    payload = {k: v for k, v in receipt.items() if k != "signature"}

    canonical = canonicalize(payload)
    try:
        verify_key = signing.VerifyKey(b64url_decode(sig_obj["public_key"]))
        verify_key.verify(canonical, b64url_decode(sig_obj["sig"]))
        return True
    except BadSignatureError:
        return False
    except Exception as exc:
        print(f"Verification error: {exc}")
        return False

is_valid = verify_receipt(receipt)
print(f"Receipt is valid: {is_valid}")

# Regression control for the signature scope in draft revision 02. A receipt
# signed over SHA-256(JCS(payload)) is a signature over different bytes and
# must not verify as a direct-JCS Ed25519 receipt.
prehashed_signature = signing_key.sign(hashlib.sha256(canonicalize(payload)).digest()).signature
prehashed_receipt = {
    **receipt,
    "signature": {**receipt["signature"], "sig": b64url_nopad(prehashed_signature)},
}
print(f"Pre-hashed receipt valid: {verify_receipt(prehashed_receipt)}")
```

::: details 原文件保存的输出（不是本项目实测）

```text
Receipt is valid: True
Pre-hashed receipt valid: False
```

:::

你应该看到 `Receipt is valid: True`。Agent 已经生成了它的第一个数字签名的审核记录。

## 第二节：篡改收据

收据的全部意义在于它们具有防篡改性。让我们来证明这一点。

我们将修改收据中的一个字符，并观察验证失败。

### 代码单元格 17

输出观察：print 展示应用可观察结果；预存输出和现场结果可能不同，它不是模型内部思考记录。

```python
import copy

tampered = copy.deepcopy(receipt)

# Modify the policy_id field (this is what an attacker might do to claim
# the action was governed by a more permissive policy than was actually used).
original_policy = tampered["policy_id"]
tampered["policy_id"] = "contoso-travel-policy-PERMISSIVE"

print(f"Original policy_id:  {original_policy}")
print(f"Tampered policy_id:  {tampered['policy_id']}")
print()
print(f"Tampered receipt valid? {verify_receipt(tampered)}")
```

::: details 原文件保存的输出（不是本项目实测）

```text
Original policy_id:  contoso-travel-policy-v3
Tampered policy_id:  contoso-travel-policy-PERMISSIVE

Tampered receipt valid? False
```

:::

### 刚才发生了什么？

当我们更改 `policy_id` 时，规范字节发生了变化。原签名针对原始 JCS 字节，不能验证修改后的字节。验证正确返回 `False`。

除非攻击者拥有私钥，否则无法修改收据中的任何字段并仍然能通过验证。只要私钥保存在密钥库中，且公钥已发布，篡改就不可能被隐藏。

你可以自己试试：修改上面单元格中的 `tool_name`、`agent_id` 或 `timestamp` 并重新运行。每次更改都会产生无效的收据。

## 第3节：将收据串联起来

一张收据只保护一个操作。大多数 Agent 会执行多个操作。为了使整个序列具备篡改可察觉性，我们通过在新收据的负载中包含前一个收据的哈希，将每个收据链接到前一个收据。

```text
Receipt 0  -->  Receipt 1  -->  Receipt 2
                  |                 |
                  +-- previous_receipt_hash field --+
```

如果有人删除或重新排序某张收据，链条就在那个点断开。之后任何收据的验证都会失败，因为它的 `previous_receipt_hash` 已经不再匹配前一个收据的实际哈希。

### 代码单元格 20

链式记录：核对前序收据的规范字节哈希，并另外验证各签名；链头需要可信外部锚点才能发现整段截断。

```python
def receipt_hash(receipt: dict) -> str:
    """
    Compute the chain hash of a complete receipt (including signature).
    This becomes the previous_receipt_hash of the next receipt in the chain.
    """
    canonical = canonicalize(receipt)
    digest = hashlib.sha256(canonical).hexdigest()
    return f"sha256:{digest}"

def make_receipt(
    tool_name: str,
    tool_args: dict,
    tool_result,
    sequence: int,
    previous_receipt_hash,
    signing_key,
    verify_key,
    agent_id: str = "contoso-travel-bot",
    policy_id: str = "contoso-travel-policy-v3",
) -> dict:
    """Convenience: build, sign, and return a receipt for one tool call."""
    payload = {
        "type": "agent.tool_call.v1",
        "agent_id": agent_id,
        "tool_name": tool_name,
        "tool_args_hash": sha256_canonical(tool_args),
        "result_hash": sha256_canonical(tool_result),
        "policy_id": policy_id,
        "timestamp": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "sequence": sequence,
        "previous_receipt_hash": previous_receipt_hash,
    }
    return sign_receipt(payload, signing_key, verify_key)
```

### 代码单元格 21

检索过程：跟踪查询、候选结果和实际选入的证据；检索为空时应明确返回缺失，而不是补写答案。

链式记录：核对前序收据的规范字节哈希，并另外验证各签名；链头需要可信外部锚点才能发现整段截断。

输出观察：print 展示应用可观察结果；预存输出和现场结果可能不同，它不是模型内部思考记录。

```python
# Build a chain of three receipts: search, hold, book.
r0 = make_receipt(
    tool_name="lookup_flights",
    tool_args={"origin": "SYD", "destination": "LAX", "date": "2026-06-15"},
    tool_result=[{"flight": "QF11", "price": 1850}],
    sequence=0,
    previous_receipt_hash=None,
    signing_key=signing_key,
    verify_key=verify_key,
)

r1 = make_receipt(
    tool_name="hold_seat",
    tool_args={"flight": "QF11", "seat": "14A", "hold_minutes": 30},
    tool_result={"hold_id": "H8472", "expires_at": "2026-06-15T15:00:00Z"},
    sequence=1,
    previous_receipt_hash=receipt_hash(r0),
    signing_key=signing_key,
    verify_key=verify_key,
)

r2 = make_receipt(
    tool_name="confirm_booking",
    tool_args={"hold_id": "H8472", "payment_token": "tok_redacted"},
    tool_result={"booking_ref": "CT-09182", "status": "confirmed"},
    sequence=2,
    previous_receipt_hash=receipt_hash(r1),
    signing_key=signing_key,
    verify_key=verify_key,
)

chain = [r0, r1, r2]
for i, r in enumerate(chain):
    print(f"Receipt {i}: tool={r['tool_name']}, prev={r['previous_receipt_hash']}")
```

::: details 原文件保存的输出（不是本项目实测）

```text
Receipt 0: tool=lookup_flights, prev=None
Receipt 1: tool=hold_seat, prev=sha256:d54d1e138bb080dd6bd825d9f015efc74ad6c7f78ee9504d0b68b39d0733b39c
Receipt 2: tool=confirm_booking, prev=sha256:9fbe5dc2ffcffd7d167ef13a744aecd578e474fb536cb7104ddb1a359607f2f6
```

:::

### 代码单元格 22

链式记录：核对前序收据的规范字节哈希，并另外验证各签名；链头需要可信外部锚点才能发现整段截断。

输出观察：print 展示应用可观察结果；预存输出和现场结果可能不同，它不是模型内部思考记录。

```python
def verify_chain(chain: list) -> list[dict]:
    """
    Verify a sequence of receipts:
      1. Each receipt's signature must verify.
      2. Each receipt (except the genesis) must reference the previous receipt's hash.
      3. Sequence numbers must match each receipt's zero-based position in the chain.
    Returns a list of per-receipt result dicts.
    """
    results = []
    for i, receipt in enumerate(chain):
        sig_ok = verify_receipt(receipt)

        if i == 0:
            chain_ok = receipt["previous_receipt_hash"] is None
        else:
            expected = receipt_hash(chain[i - 1])
            chain_ok = receipt["previous_receipt_hash"] == expected

        seq_ok = receipt["sequence"] == i

        results.append({
            "index": i,
            "tool": receipt["tool_name"],
            "signature_valid": sig_ok,
            "chain_link_valid": chain_ok,
            "sequence_valid": seq_ok,
            "overall_valid": sig_ok and chain_ok and seq_ok,
        })
    return results

for r in verify_chain(chain):
    status = "VALID" if r["overall_valid"] else "INVALID"
    print(f"Receipt {r['index']} ({r['tool']:>18}): {status}")
```

::: details 原文件保存的输出（不是本项目实测）

```text
Receipt 0 (    lookup_flights): VALID
Receipt 1 (         hold_seat): VALID
Receipt 2 (   confirm_booking): VALID
```

:::

现在通过篡改中间的收据来破坏链条并重新验证。被篡改的收据未通过其签名验证，并且下一个收据未通过链链接验证（因为其 `previous_receipt_hash` 不再匹配被修改的中间收据的哈希）。

### 代码单元格 24

输出观察：print 展示应用可观察结果；预存输出和现场结果可能不同，它不是模型内部思考记录。

```python
# Tamper with the middle receipt: change the hold duration to something
# more permissive than was actually authorized.
tampered_chain = [copy.deepcopy(r) for r in chain]
tampered_chain[1]["tool_args_hash"] = sha256_canonical(
    {"flight": "QF11", "seat": "14A", "hold_minutes": 9999}
)

for r in verify_chain(tampered_chain):
    status = "VALID" if r["overall_valid"] else "INVALID"
    why = ""
    if not r["overall_valid"]:
        reasons = []
        if not r["signature_valid"]:
            reasons.append("signature")
        if not r["chain_link_valid"]:
            reasons.append("chain link")
        if not r["sequence_valid"]:
            reasons.append("sequence")
        why = " (failed: " + ", ".join(reasons) + ")"
    print(f"Receipt {r['index']} ({r['tool']:>18}): {status}{why}")
```

::: details 原文件保存的输出（不是本项目实测）

```text
Receipt 0 (    lookup_flights): VALID
Receipt 1 (         hold_seat): INVALID (failed: signature)
Receipt 2 (   confirm_booking): INVALID (failed: chain link)
```

:::

收据 0 仍然验证通过（它未被修改且没有前置收据依赖）。收据 1 因为我们更改了 `tool_args_hash`，所以其签名校验失败。收据 2 因其 `previous_receipt_hash` 是基于原始（现已被修改的）收据 1 计算的，导致链链接校验失败。

即使攻击者对被修改的收据 1 重新签名（如果没有私钥他们无法完成此操作），收据 2 中的链链接不匹配仍会暴露篡改行为。为了隐藏更改，攻击者必须从修改点开始对每个收据重新签名，这需要持有私钥。

## 第4节：使用收据签名包装 Agent 工具调用

在实际部署中，你不希望每个 Agent 作者都记得调用 `make_receipt`。你希望每次工具调用时收据签名都是自动的。

以下是最简单的模式：一个包装类，它接受任何可调用的工具函数并返回一个带有收据生成功能的版本。这个模式适用于任何 Agent 框架，包括Microsoft Agent Framework（`agent_framework.foundry`）。

如果你还没有设置微软 Foundry 项目，下面的本地模拟依然展示了该模式。

### 代码单元格 27

链式记录：核对前序收据的规范字节哈希，并另外验证各签名；链头需要可信外部锚点才能发现整段截断。

```python
class ReceiptedTool:
    """
    Wraps a tool function so every invocation produces a signed receipt.
    Receipts are appended to a chain held by this object.

    Accepts both positional and keyword arguments. The receipt's
    tool_args field records args (as a list) and kwargs (as a dict)
    so the canonical hash binds to whichever the caller supplied.
    """

    def __init__(self, name: str, fn, signing_key, verify_key, agent_id: str, policy_id: str):
        self.name = name
        self.fn = fn
        self.signing_key = signing_key
        self.verify_key = verify_key
        self.agent_id = agent_id
        self.policy_id = policy_id
        self.receipts: list = []

    def __call__(self, *args, **kwargs):
        result = self.fn(*args, **kwargs)
        previous_hash = receipt_hash(self.receipts[-1]) if self.receipts else None
        receipt = make_receipt(
            tool_name=self.name,
            tool_args={"args": list(args), "kwargs": kwargs},
            tool_result=result,
            sequence=len(self.receipts),
            previous_receipt_hash=previous_hash,
            signing_key=self.signing_key,
            verify_key=self.verify_key,
            agent_id=self.agent_id,
            policy_id=self.policy_id,
        )
        self.receipts.append(receipt)
        return result
```

### 代码单元格 28

模型连接：project_endpoint 是项目地址，model 是实际部署名称；credential 提供访问身份。客户端创建本身不证明已经部署服务端 Agent。

输出观察：print 展示应用可观察结果；预存输出和现场结果可能不同，它不是模型内部思考记录。

```python
# Example tool: a mock flight lookup. In a real Microsoft Agent Framework deployment,
# this would be a function passed to FoundryChatClient as a tool.
def mock_lookup_flights(origin: str, destination: str, departure_date: str) -> list:
    return [
        {"flight": "QF11", "price": 1850, "stops": 0},
        {"flight": "UA864", "price": 1620, "stops": 1},
    ]

# Wrap it with receipt signing.
receipted_lookup = ReceiptedTool(
    name="lookup_flights",
    fn=mock_lookup_flights,
    signing_key=signing_key,
    verify_key=verify_key,
    agent_id="contoso-travel-bot",
    policy_id="contoso-travel-policy-v3",
)

# Use the wrapped tool exactly like the original.
results_a = receipted_lookup(origin="SYD", destination="LAX", departure_date="2026-06-15")
results_b = receipted_lookup(origin="SYD", destination="NRT", departure_date="2026-07-02")
results_c = receipted_lookup(origin="MEL", destination="SIN", departure_date="2026-08-10")

print(f"Tool was called {len(receipted_lookup.receipts)} times.")
print(f"Each call produced a signed receipt linked to the previous one.")
print()

for r in verify_chain(receipted_lookup.receipts):
    status = "VALID" if r["overall_valid"] else "INVALID"
    print(f"Receipt {r['index']} ({r['tool']}): {status}")
```

::: details 原文件保存的输出（不是本项目实测）

```text
Tool was called 3 times.
Each call produced a signed receipt linked to the previous one.

Receipt 0 (lookup_flights): VALID
Receipt 1 (lookup_flights): VALID
Receipt 2 (lookup_flights): VALID
```

:::

### 与 Microsoft Agent Framework 集成

上面的 `ReceiptedTool` 包装器与具体框架无关。要在使用 Microsoft Agent Framework 构建的 Agent 中使用它，请将包装后的函数注册为工具。示例（你需要用真实的 Microsoft Foundry 工具注册替换示例中的模拟）： 

```python
# 显示集成形状的伪代码。
# 导入os
# 从agent_framework.foundry导入FoundryChatClient
# 从azure.identity导入AzureCliCredential
#
# provider = FoundryChatClient(
#     project_endpoint=os.environ["AZURE_AI_PROJECT_ENDPOINT"],
#     model=os.environ["AZURE_AI_MODEL_DEPLOYMENT_NAME"],
#     credential=AzureCliCredential(),
# )
# agent = provider.as_agent(
#     instructions="你是Contoso旅行代理...",
#     tools=[receipted_lookup],   # 包装后的工具，不是原始函数
# )
# response = agent.run("查找六月从悉尼飞往洛杉矶的航班。")
#
# # 运行后，代理调用的每个工具都有一个签名收据：
# audit_chain = receipted_lookup.receipts
```

Agent 框架无需了解任何关于收据的内容。收据签名被包装在工具周围，而不是嵌入框架中。这就是如何在不重写 Agent 代码的情况下，为现有 Agent 代码添加溯源信息。

## 回顾与拓展挑战

你已经完成：

- 生成了 Ed25519 密钥对。
- 构建并签署了一个 Agent 工具调用的收据。
- 使用公钥离线验证了该收据。
- 篡改了收据并观察到验证失败。
- 构建了一个包含三个收据的哈希链序列。
- 篡改了链中间部分，观察到签名失败和链链接失败。
- 用自动收据签名封装了一个工具函数。

 **拓展挑战。** 在收据模式中添加一个 `request_id` 字段（用于分布式追踪的 UUID）。更新 `make_receipt` 以包含该字段，并确认收据仍能端到端验证。然后在签名后修改此字段，确认验证失败。此挑战迫使你理解编码的每一个字节如何影响签名。

 **重要界限。** 收据证明三件事，且仅证明三件事：归属（该密钥签署了该内容）、完整性（签署后内容未被修改）和顺序（该收据出现在另一收据之后）。它们不证明 Agent 的行为正确，`policy_id` 中指定的策略是否真的被评估，或 Agent 是否遵守了所有规则。收据只是基础。治理是你构建的系统。

带着这个界限再读一遍本课的 README。团队在使用收据时最常犯的错误是认为“我们有收据”就意味着“我们被治理了”。事实并非如此。收据使 Agent 行为可审计，但并不保证其正确。


## 本章目标与前置知识（补充讲解）

先读[可信赖 Agent](./trust.md)、[工具](./tools.md)和[生产实践](./production.md)。本章学习签名收据的生成、离线验证、链式关联与授权绑定，并明确这些机制证明不了什么。

一个工具日志写着“已向账户 A 退款 100 元”。审计时，怎样发现日志被改成了账户 B？**数字签名（Digital Signature）**将特定私钥与一组字节绑定；持有可信公钥的检查者可以验证内容完整性。它不像加密那样隐藏内容，也不证明退款决定正确。

原课程用 **Ed25519** 和 **JSON 规范化方案（JSON Canonicalization Scheme，JCS）**实现密码学收据。应用对 JCS 规范字节直接签名；参数摘要和链链接另行使用 SHA-256。这里已对照英文修正中文旧版“先哈希再签名”的差异。算法细节参见 [RFC 8032](https://www.rfc-editor.org/rfc/rfc8032)、[RFC 8785](https://www.rfc-editor.org/rfc/rfc8785) 与 [PyNaCl 签名文档](https://pynacl.readthedocs.io/en/latest/signing/)。

::: tip 已执行的范围
两份原始安全 Notebook 的 19 个非安装代码单元格已在本项目验证环境中离线执行。第一份调用的是模拟航班函数，第二份使用测试审批身份与固定时间，均没有连接真实退款、WebAuthn 或云模型。详细记录见[检查报告](/guide/verification.md)。
:::

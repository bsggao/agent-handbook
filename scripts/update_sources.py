from pathlib import Path
import json
P=Path('docs/guide');M=json.loads(Path('provenance/source-version.json').read_text());C=json.loads(Path('provenance/course-map.json').read_text());A=json.loads(Path('provenance/assets.json').read_text())
body='''---
title: 来源、覆盖与版本说明
description: 微软原课程来源、固定提交、内容覆盖、许可与校订记录。
---

# 来源、覆盖与版本说明

本项目是基于 **Microsoft AI Agents for Beginners** 整理的非官方中文学习版，与微软官方课程站点没有隶属或认证关系。原课程与贡献者署名、MIT 许可保留在项目 `LICENSE` 与[许可证文件](/LICENSE.txt)。新增讲解、示例、图与网站代码按同一 MIT 许可证提供。

## 固定来源版本

'''+f"- 原仓库：[microsoft/ai-agents-for-beginners]({M['repository']})。\n- 提交：[`{M['commit']}`]({M['repository']}/tree/{M['commit']})。\n- 提交时间：`{M['commitDate']}`。\n- 获取日期：**{M['retrieved']}**。\n"+'''
`upstream/` 保存实际获取的源文件快照，不修改原文件。`provenance/source-version.json` 逐文件记录 SHA-256；`course-map.json` 记录原文、译文、页面、代码与图片；`page-map.json` 是源路径到站内页的映射。更新上游必须重新读取、比较和验证，不能仅修改版本日期。

正文以该提交的简体中文翻译为基础，对照英文、实际 Notebook 与 SDK 发行源码校订。原课程核心内容保留为精读部分；“补充讲解”“扩展实践”是本项目新增。正文的代码块优先使用英文同提交代码，避免翻译修改标识符或将引号转义后破坏语法。

## 覆盖清单

| 编号 | 原始目录 | 中文章节 | 原始代码文件数 | 状态 |
| --- | --- | --- | --- | --- |
'''+ '\n'.join(f"| {c['id']} | `{c['source']}` | [{c['title']}](/lessons/{c['slug']}.md) | {len(c['code'])} | 正文、导读与练习已实现 |" for c in C)+'''

支持材料不仅是目录链接：每份 Notebook 已拆成说明、原始代码、关键代码导读与折叠的原文件输出，并提供下载。Python 与 .NET 原脚本在阅读页保留完整代码。云端示例以“静态阅读”标记，不能把保存输出误认成本站执行记录。

## 关键校订与版本差异

| 位置 | 源文件核对结果 | 本版处理 |
| --- | --- | --- |
| 准备篇 | 中文配置落后于英文；无上限安装易进入 MAF 1.11 | 分离浏览、本地与云实验；固定核心 1.10.0；提醒跳过 Notebook 的 `-U` |
| 框架与 Foundry | 创建 ChatClient 与创建/发布托管 Agent 不是同一动作 | 区分模型连接、应用执行循环与托管发布 |
| 03 设计模式 | 原章重点是人本设计的空间/时间/核心原则 | 保留原重心，补充可操作的状态与控制案例 |
| 04 工具调用 | 结构模型虽定义却未传入本次运行；审批工具只展示元数据 | 不声称已验证结构化输出或实际完成审批恢复 |
| 05 RAG | Python 例子为字典/字符串检索 | 明确它没有启用向量库或 Azure Search |
| 06 可信赖 | `DEMO_MODE=True` 重试可自动批准高风险动作 | 明确不是人类授权或风险变低；解释失败时默认拒绝 |
| 07 规划 | 依赖是模型生成数据，未做确定性图验证 | 补充循环依赖与就绪条件检查 |
| 09 元认知 | 拟人化叙述、示意 URL、旧 API、直接 `exec` | 解释为可观察的检查/反馈；片段不宣称完整可运行；指出隔离边界 |
| 11 协议 | 两份主 MAF Notebook 只模拟工具/协作 | 不称为 MCP/A2A 网络兼容性验证，另链接真实 MCP 代码 |
| 12 上下文 | 工具数量经验值不适用于所有模型 | 解释 Token 与字符区别，强调按任务评估 |
| 13 记忆 | 主例是内存字典；README 的 Mem0/Search 描述不符；酒店工具未注册 | 明确持久化与注册差异，保留 Cognee 独立实现 |
| 14 框架 | README 有旧 `get_new_thread` / `run_stream` API | 固定 1.10.0，优先同提交新 Notebook 的 session 与流式写法 |
| 15 界面自动化 | 网站布局与 Opal 产品状态有时效；Notebook 有重复结果类 | 保留原 Browser-Use/Playwright，列出现场验证与权限边界 |
| 16 部署 | 发布只打印；缓存仅按问题；阈值辅助函数未接入审批；评估较弱 | 不称生产部署完成；指出用户隔离、真实门控与评估范围 |
| 17 本地 | Chroma Client 是内存；MCP 仅发现；中文版取舍翻反 | 修正持久化、离线前提、接口兼容与模型硬件预期 |
| 18 安全 | 英文直接签 JCS 字节，中文仍写预哈希；草案格式描述落后 | 使用英文算法、明确非标准兼容实现、可信公钥与授权绑定边界 |

校订规则在 `scripts/editorial.py`，新增正文在 `content/chapters/`。原始代码下载保留原样，因此其局限仍须结合本章说明阅读。部分 README 片段和历史集成没有改造成当前可运行版本，已标为原理/历史代码；优先运行已验证的本地项目或按当前账号环境验证完整 Notebook。

## SDK 与官方资料核对

网站固定 VitePress 1.6.4、Vue 3.5.21 与 TypeScript 5.9.2，依赖树由 `package-lock.json` 固定。原课核心固定 MAF 1.10.0；原 `requirements.txt` 的不少其他包没有完整版本约束，不能把它称为完全可复现锁文件。

本项目下载并读取了 `agent-framework-core`、`agent-framework-foundry`、`agent-framework-openai` 的 **1.10.0** 发行源码，核对 `FoundryChatClient(project_endpoint, model, credential)`、客户端 `as_agent()`、Agent `create_session()`、`run(stream=True)` 以及 `response_format` 选项。新增云实验只使用已核对的接口，未发起实际云请求。

官方文档可能比课程固定版本更新；不能直接将其最新代码片段与 1.10.0 混合：

- [Microsoft Agent Framework 1.10.0 发行记录](https://github.com/microsoft/agent-framework/releases/tag/python-1.10.0)
- [Microsoft Foundry 模型客户端](https://learn.microsoft.com/en-us/agent-framework/integrations/by-component/model-providers/microsoft-foundry)
- [MCP 官方架构](https://modelcontextprotocol.io/docs/2026-07-28/learn/architecture)
- [A2A 核心概念](https://a2a-protocol.org/latest/topics/key-concepts/)
- [JCS：RFC 8785](https://www.rfc-editor.org/rfc/rfc8785) 与 [EdDSA：RFC 8032](https://www.rfc-editor.org/rfc/rfc8032)
- [PyNaCl 数字签名](https://pynacl.readthedocs.io/en/latest/signing/)

## 图片、视频与缺失项

'''+f"本地获取 **{len([a for a in A if a['status']=='local'])}** 张源图片（包括用于来源核对的英文/中文和横幅资源），仅在相关正文展示必要配图；另绘制 8 幅中文 SVG，涵盖循环、时序、RAG、规划、协作、上下文、MCP 与部署。来源图以 Microsoft/MIT 标注，本项目重绘图明确标注。\n\n"+'''
视频只提供原标题或主题与原始链接，没有生成未经核实的字幕翻译。第 18 章上游视频链接仍为占位，因此页面移除了不可播放的入口并在这里记录。部分 GitHub 用户附件或外部素材不作为核心配图依赖，仅保留原始来源链接。

此前一次下载失败的中文并发 Notebook 和上下文章缩略图已重试补齐。所选 00–18 正文、对应中文、主要代码和配置文件的获取结果以清单为准；没有声称镜像仓库全部语言、所有历史素材或外部网站。

上游某些相对链接和翻译目录锚点已过时。可定位的章节/代码转为站内页，旧锚点移除以避免跳到不存在的标题；未能定位的原链接列在 `provenance/unresolved-source-links.json`，保留不可变提交下的原文出处，不虚构缺失文件。

## 验证与维护

[验证报告](./verification.md)分开记录本地执行、源码检查、网页验收和未运行的联网实验。维护流程：更新源快照与提交记录 → 比较英中章节 → 更新校订与补充正文 → 运行导入与打包脚本 → 构建及资源检查 → 检查桌面/移动交互 → 更新报告。
'''
(P/'sources.md').write_text(body)

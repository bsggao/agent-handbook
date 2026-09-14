---
title: "Computer Use 与 Browser Use"
description: "理解观察、操作、验证的界面自动化循环。"
course: "browser-use"
prev: {"text": "Microsoft Agent Framework", "link": "/lessons/agent-framework"}
next: {"text": "可扩展部署", "link": "/lessons/deployment"}
---

# Computer Use 与 Browser Use

## 本章目标与前置知识（补充讲解）

先掌握[工具调用](./tools.md)和[可信赖 Agent](./trust.md)。本章学习界面自动化中的观察、选择动作、执行与验证，并区分开放导航的 Agent 和确定性操作的 Actor。

 **计算机使用（Computer Use）** 覆盖桌面应用等界面； **浏览器使用（Browser Use）** 是其面向网页的一部分。没有合适 API 时，助手可观察页面结构或截图、定位控件、点击、输入并读回结果。但“发出点击命令”并不证明按钮已生效。

原课程使用 Browser-Use、Playwright 与 Chrome DevTools Protocol（CDP）连接浏览器，用 Pydantic 描述 Airbnb 搜索结果。这里只保留该实际技术栈，不把浏览器任务伪装成稳定后台接口。


::: info 原课程代码片段的阅读范围
下方精读保留上游主要知识与片段，可能包含历史 SDK 写法、示意端点及未完整定义的函数；这些片段不等同于经过本站验证的完整程序。运行前优先阅读本章实际 Notebook 导读与版本校订。已验证的无 API 实验在“扩展实践”中另行标明。
:::

## 原课程精读：构建计算机使用 Agent（CUA）

计算机使用 Agent 可以像人类一样与网站交互：通过打开浏览器，检查页面，并根据所见采取最佳下一步行动。在本课中，你将构建一个浏览器自动化 Agent，搜索 Airbnb，提取结构化的房源数据，并识别斯德哥尔摩最便宜的住宿。

本课结合了用于 AI 驱动导航的 Browser-Use，控制浏览器的 Playwright 和 Chrome DevTools 协议（CDP），具备视觉推理能力的 Azure OpenAI，以及用于结构化提取的 Pydantic。

## 介绍

本课将涵盖：

- 了解何时计算机使用 Agent 比仅用 API 自动化更合适
- 结合 Browser-Use、Playwright 和 CDP 实现可靠的浏览器生命周期管理
- 使用 Azure OpenAI 视觉能力和结构化的 Pydantic 输出从动态网页中提取房源数据
- 决定何时采用以 Agent 为先、以执行者为先或混合浏览器自动化工作流

## 学习目标

完成本课后，你将学会如何：

- 配置 Browser-Use 联合 Azure OpenAI 和 Playwright
- 构建浏览器自动化工作流，导航真实网站并处理动态 UI 元素
- 从可见页面内容中提取类型化结果，并转化为后续业务逻辑
- 根据浏览器任务的可预测性选择 Agent 模式或执行者模式

## 代码示例

本课包含一个笔记本教程：

- [15-browser-user.ipynb](/labs/15-browser-use-15-browser-user-notebook.md)：通过 CDP 启动 Chrome 会话，在 Airbnb 上搜索斯德哥尔摩的房源，利用 Browser-Use 视觉提取价格，并返回最便宜的房源作为结构化数据。

## 先决条件

- Python 3.12+
- 配置好的 Azure OpenAI 部署环境
- 本地安装的 Chrome 或 Chromium
- 已安装 Playwright 依赖
- 对异步 Python 有基本了解

## 设置

安装笔记本中使用的软件包：

```bash
pip install browser_use playwright python-dotenv
playwright install chromium
```

设置笔记本使用的 Azure OpenAI 环境变量：

```bash
AZURE_OPENAI_ENDPOINT=...
AZURE_OPENAI_API_KEY=...
AZURE_OPENAI_CHAT_DEPLOYMENT_NAME=...
# Optional: defaults to the latest API version when omitted
AZURE_OPENAI_API_VERSION=...
```

## 架构概览

该笔记本演示了一个混合浏览器自动化工作流：

1. Chrome 启动时启用 CDP，以便 Playwright 和 Browser-Use 共享同一浏览器会话。
2. Browser-Use Agent 处理开放式导航任务，例如打开 Airbnb、关闭弹窗和搜索斯德哥尔摩。
3. 使用结构化的 Pydantic 模式检查活动页面，提取房源标题、每晚价格、评分和链接。
4. Python 逻辑比较提取的房源，突出最便宜的结果。

这种方法保留了 Browser-Use 擅长的灵活视觉推理，同时在需要时提供确定性的浏览器控制。

## 关键要点和最佳实践

### 何时使用 Agent vs 执行者

| 场景 | 使用 Agent | 使用执行者 |
|----------|-----------|-----------|
| 动态布局 | 是，AI 能适应页面变化 | 否，脆弱的选择器会崩溃 |
| 结构已知 | 否，Agent 比直接控制慢 | 是，快速且精确 |
| 查找元素 | 是，自然语言效果好 | 否，需要精确选择器 |
| 时间控制 | 否，较不可预测 | 是，可以完全控制等待和重试 |
| 复杂工作流 | 是，能处理意外 UI 状态 | 否，需要显式分支 |

### Browser-Use 最佳实践

1. 从 Agent 开始，用于探索和动态导航。
2. 当交互变得可预测时切换到直接页面控制。
3. 使用结构化输出模型，确保提取数据经过验证且类型安全。
4. 在触发可见 UI 变化的操作后有策略地添加延迟。
5. 迭代过程中截图，便于调试失败。
6. 预期网站会变化，设计弹窗和布局变动的备选方案。
7. 结合 Agent 和执行者模式，兼顾灵活性与精确性。

### 浏览器 Agent 的安全防护措施

浏览器 Agent 操作的是实时网站，因此需要比只调用已知 API 的脚本更严格的边界。在从笔记本演示转向真实工作流之前，定义 Agent 可见、点击和提交的范围。

1. **限定浏览环境。** 在独立浏览器配置文件或沙箱中运行 Agent，限制到任务所需的域名。
2. **分离观察和操作。** 先让 Agent 搜索、读取和提取数据；提交表单、发送消息、预订、购买、删除记录或更改账户设置前需用户显式批准。
3. **避免在提示和记录中暴露机密。** 不在模型上下文中放置密码、支付信息、会话 Cookie 或原始个人数据。用户应负责认证，且敏感字段从日志中打码。
4. **把页面内容当作不可信输入。** 网站可能包含针对 Agent 的指令，而非用户指令。Agent 应忽略要求更改目标、泄露数据、禁用防护或访问无关网站的页面文本。
5. **在风险步骤使用确定性检查。** 在请求用户批准最终步骤前，通过代码验证当前 URL、页面标题、选中项、价格、接收方和操作摘要。
6. **设定预算和停止条件。** 限制 Agent 可执行的操作次数、重试次数、标签页数和时长。遇到页面状态不明时停止操作，避免盲目点击。
7. **记录有用证据，避免记录全部内容。** 保留操作摘要、时间戳、URL、选中元素描述和截图引用，便于回顾失败，不保存不必要的敏感页面内容。

在 Airbnb 示例中，安全默认行为是搜索房源并提取价格。登录、联系房东或完成预订应为用户批准的单独操作。

### 真实应用案例

- 旅行预订和价格监控
- 电子商务价格比较和库存检查
- 从动态网站结构化提取数据
- 具备视觉感知的 UI 测试和验证
- 网站监控和报警
- 多步骤流程的智能表单填写

## 真实案例：微软 Project Opal

本课中构建的 Agent 是一个小型本地版本的 **计算机使用 Agent（CUA）** ——一种以类似人类方式驱动浏览器的程序。微软正将这一理念带给企业，推出了 Microsoft 365 Copilot 中的 **[Project Opal (Frontier)](https://support.microsoft.com/en-us/microsoft-365-copilot/get-started-with-project-opal-frontier)** 功能。

通过 Project Opal，你描述一个任务，Agent 会代表你使用 **在安全的 Windows 365 云 PC 上的计算机使用** ，跨你组织内的基于浏览器的应用、站点和数据异步工作。你可以随时引导或接管其工作。示例任务包括：

- 管理安全组成员请求
- 为合规审查收集和验证审计证据
- IT 事件分类（更新票务状态、分配负责人、关闭重复）
- 将 Excel 数据汇总至财务结算报告

Opal 是一个生产级、值得信赖的计算机使用 Agent 的有力示范，且强化了本课程中早期的概念：

| 本课程中的概念 | Project Opal 的应用 |
|------------------------|-----------------------------|
| **人机协作** （第 06 课） | Opal 在登录凭证、敏感数据或模糊指令时暂停，且绝不会在未明确确认的情况下输入密码或提交表单。可在任务中途*接管控制*和*返回控制*。 |
| **可信和安全 Agent** （第 06 和 18 课） | 运行在隔离的 Windows 365 云 PC 中，默认仅限浏览器访问（通过 Intune 强制阻止其它计算机访问），使用*你的*身份访问仅授权内容，且记录所有操作以便审计。 |
| **规划与元认知** （第 07 和 09 课） | Opal 先生成作业计划，然后在每步监督自身推理，检测异常时暂停。 |
| **可复用能力/工具** （第 04 课） | **技能** 让你为重复作业编写指令（从 `.md` 文件导入或用 Opal 编写），并在对话中复用。 |

> **可用性：** Project Opal 当前面向拥有 Microsoft 365 Copilot 订阅的 [Frontier 早期访问计划](https://adoption.microsoft.com/copilot/frontier-program/)用户开放，且需管理员完成设置。作为实验性 Frontier 功能，其能力可能会随时间变化。

## 知识检测

在进入下一课前测试你的理解。

 **1. 何时基于浏览器的计算机使用 Agent 比仅用 API 流程更合适？** 

<details>
<summary>答案</summary>

当任务依赖网页 UI 中可见内容，且网站没有提供所需 API，或者页面经常变化使得固定的 API 或选择器逻辑脆弱时，使用浏览器 Agent。如果存在用于同样任务的稳定 API，优先使用 API，因为它通常更快、更易测试且更安全。
</details>

 **2. 在混合工作流中，哪些部分应由 Agent 处理，哪些部分应由直接 Playwright 代码处理？** 

<details>
<summary>答案</summary>

让 Agent 处理开放式导航和动态 UI 状态，如找到正确页面或关闭意外弹窗。当页面结构已知且操作需要精准、重试、等待或确定性验证时，切换到直接 Playwright 控制。
</details>

 **3. Airbnb 示例找到用户可能想预订的房源。工作流在登录、联系房东或完成预订前应做什么？** 

<details>
<summary>答案</summary>

工作流应暂停并请求用户明确批准。请求前应显示所选房源、当前 URL、价格、日期和预期操作的清晰摘要。搜索和提取价格可以自动完成；账户访问、消息、购买和预订应由用户批准。
</details>

 **4. 网页告诉 Agent 忽略最初的指令，访问其他站点并暴露已保存的凭据。Agent 应如何处理该文本？** 

<details>
<summary>答案</summary>

应将其视为不可信的页面内容，而非开发者或用户指令。Agent 应保持在允许的域名和任务范围内，拒绝泄露机密，避免遵循更改目标、禁用防护或跳转至无关站点的页面文字。
</details>

 **5. 浏览器 Agent 运行时应保留哪些证据，哪些应避免？** 

<details>
<summary>答案</summary>

保留操作摘要、时间戳、URL、选中元素描述、验证结果和截图引用，以便回顾运行。避免保存密码、支付信息、会话 Cookie、原始个人数据或完整页面内容，除非有明确的保留和隐私需求。
</details>

## 附加资源

- [开始使用 Project Opal (Frontier)](https://support.microsoft.com/en-us/microsoft-365-copilot/get-started-with-project-opal-frontier)
- [Browser-Use Playwright 集成模板](https://docs.browser-use.com/examples/templates/playwright-integration)
- [Browser-Use 执行者参数与内容提取](https://docs.browser-use.com/customize/actor/all-parameters)
- [课程设置](/lessons/setup.md)

## 一次住宿搜索的完整执行边界（补充讲解）

输入目的地、日期、人数和预算 → 启动独立浏览器会话 → 观察页面 → 选择筛选动作 → 执行后重新读取状态 → 收集房源名称、总价、链接 → 校验字段与用户条件 → 汇总并停止。遇到登录、验证码、支付或权限不明的页面应停在清晰的交接点。

Agent 适合寻找页面、处理不同布局；Actor 适合在已确认结构上稳定地填写日期、等待元素和验证结果。二者可以组合，但每一步都应依据最新页面状态定位，不能复用导航前的坐标或盲目依赖模型猜测。

### 原 Notebook 如何读与运行

先阅读环境单元格和 `Browser` / `Agent` / `AzureChatOpenAI` 配置，核对浏览器可执行路径、依赖与模型环境变量，再看任务说明、结构化结果类型和 `run()` 调用。Chrome 路径和网站 DOM 会随平台变化；原文件还有重复的结果类定义，按执行顺序后一个会覆盖前一个，整理成脚本时应保留一份一致定义。

这是 **可选联网实验，未在本项目中实际登录 Airbnb 或运行付费模型** 。在自己新建的浏览器配置中实验，避免复用带私人账号的日常配置；按 Notebook 所列依赖安装 Playwright 浏览器，检查 Azure 部署权限。预期输出房源结构化字段；网站可用性、反爬限制和模型结果都需现场验证。不要把上游保存输出当成当前价格。

### 原文产品案例的时效

原文以 Microsoft Project Opal 为企业 CUA 案例，关联任务委派、人工介入和技能复用。这里作为锁定提交时的案例保留，不承诺目前的地区、订阅、管理员设置或产品功能；实际使用前以其官方说明为准。教程的技术原则不依赖开通该产品。

## 无账号界面自动化练习（扩展实践）

在本站[工具调用演示](./tools.md)上完成以下可验证序列：找到“下一步” → 点击一次 → 观察新出现的工具请求 → 继续到结束 → 确认按钮禁用 → 点击“重置” → 确认历史清空。可以先手动操作并记录每步可观察的状态，再用自己熟悉的 Playwright 测试程序复现。

下面是 **测试片段** ，并非原课程模型 Agent；需要一个已启动本站的 Playwright 测试项目和 `page` fixture：

```typescript
await page.goto('http://localhost:4173/lessons/tools.html')
const demo = page.locator('.step-demo')
await demo.getByRole('button', { name: '下一步 →' }).click()
await expect(demo.getByText('提出任务', { exact: true })).toBeVisible()
await demo.getByRole('button', { name: '重置' }).click()
```

`getByRole` 按用户能理解的角色定位；每个动作之后用断言检查结果。若组件按钮文本调整，应按实际页面更新测试。该片段的完整运行环境不是本章 Browser-Use Notebook，不能混用二者的安装步骤。

## 安全边界与错误处理

| 现象 | 原因 | 解决方向 |
| --- | --- | --- |
| 点了错误房源 | 复用了旧坐标或页面变化 | 每步读取新页面，优先稳定语义定位 |
| 一直加载 | 未设超时/步数，等待条件错误 | 限定任务时间，检查实际结果元素 |
| 页面让助手发送凭据 | 页面文本中的提示注入 | 将页面视为不可信数据，凭据不放提示或截图日志 |
| 输入日期格式错误 | 地区格式、时区、组件规则不同 | 读回字段与最终搜索摘要 |
| 成功截图却没有预约 | 只观察到点击而没确认提交结果 | 读取确认编号或权威业务状态 |

CUA 成本包括模型调用、截图体积、浏览器资源与布局变化维护。稳定 API 可用时通常更容易验证；界面自动化适合确实只能通过 UI 完成的工作。

## 自测与练习

搜索页面出现“仅剩最后一间，立即付款”是否代表用户已经授权付款？把动作上限设为 20 是否可以防止一次错误提交？

::: details 参考答案
都不是。页面营销文案不是用户授权；预算只能限制动作数量，不能限制每个动作的影响。高影响动作要在执行边界检查具体对象、金额、身份与明确批准；一次就足以造成损失的动作尤其需要校验。
:::

下一章[可扩展部署](./deployment.md)关注会话隔离、并发与长期运行。


## 原课程代码与补充材料

以下是本章实际源文件对应的阅读页。Notebook 已分解为说明、代码及原文件输出；云端示例未进行联网端到端验证。正文中的片段用于解释，运行时使用完整 Notebook 和准备篇的固定依赖。

- [15-browser-user.ipynb](/labs/15-browser-use-15-browser-user-notebook.md)

## 本章来源

基于 [英文原文](https://github.com/microsoft/ai-agents-for-beginners/blob/25b7985f3b2dc37a84f4a7387ccd3c9f0e5b1595/15-browser-use/README.md) 与 [简体中文翻译](https://github.com/microsoft/ai-agents-for-beginners/blob/25b7985f3b2dc37a84f4a7387ccd3c9f0e5b1595/translations/zh-CN/15-browser-use/README.md) 整理，原作者为 Microsoft 与开源贡献者，采用 MIT 许可证。本页标明“补充讲解”与“扩展实践”的内容为本项目新增。

来源提交：`25b7985f3b2d` · 获取日期：2026-09-14。参见[版本校订记录](/guide/sources.md)。

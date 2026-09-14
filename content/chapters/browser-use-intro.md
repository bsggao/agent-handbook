## 本章目标与前置知识（补充讲解）

先掌握[工具调用](./tools.md)和[可信赖 Agent](./trust.md)。本章学习界面自动化中的观察、选择动作、执行与验证，并区分开放导航的 Agent 和确定性操作的 Actor。

**计算机使用（Computer Use）**覆盖桌面应用等界面；**浏览器使用（Browser Use）**是其面向网页的一部分。没有合适 API 时，助手可观察页面结构或截图、定位控件、点击、输入并读回结果。但“发出点击命令”并不证明按钮已生效。

原课程使用 Browser-Use、Playwright 与 Chrome DevTools Protocol（CDP）连接浏览器，用 Pydantic 描述 Airbnb 搜索结果。这里只保留该实际技术栈，不把浏览器任务伪装成稳定后台接口。

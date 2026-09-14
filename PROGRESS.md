# 实施进度：教程与域名部署已完成，GitHub 推送待登录

来源：Microsoft AI Agents for Beginners，提交 25b7985f3b2dc37a84f4a7387ccd3c9f0e5b1595，获取 2026-09-14。

- [x] 检查空目录与开发规范；VitePress / Vue 3 / TypeScript，固定网站依赖与锁文件。
- [x] 获取并校对 00–18 英文/简中、Python/Notebook/.NET、配置与许可；238 个源文件哈希记录。
- [x] 19 章完整正文、目标、案例、代码导读、错误分析、练习/答案、前后章节和来源。
- [x] 87 个原材料阅读页；38 份 Notebook 排除独立翻译免责声明后全部对齐，执行代码使用英文原始版本。
- [x] 学习路线、47 个中英术语、Python 小抄、FAQ、五阶段项目、来源与版本校订。
- [x] 98 张本地源图片、8 幅中文 SVG、可滚动 Mermaid，3 个带失败分支的模拟演示。
- [x] 中文全站搜索、深浅主题、复制、图片放大、移动导航、进度/继续/清除、sitemap/404。
- [x] 本地项目 14 个行为测试 + 6 个回归用例；5 个独立教学片段；第 18 章 19 个代码单元格离线执行。
- [x] 类型检查、静态构建 116 页、正文覆盖、Notebook 对齐、内部链接/锚点/资源检查通过。
- [x] 桌面与手机浏览器、三演示、搜索、进度、复制、图片、流程图、主题、404 与键盘焦点验收。

已修复导入规则过度删除正文、译本免责声明造成 Notebook 对齐失败、Notebook 下载误加 .html、中文强调显示、手机流程图过度缩小与清除进度后位置被重新写入的问题，并加入对应检查或实际回归验证。

外部条件限制：未执行真实云模型、Search/记忆服务、远程协议互通、第三方 UI 操作、Foundry Local 推理或云部署/负载测试。原课旧 API 和未固定依赖已在正文中标注；详见 docs/guide/verification.md。

使用 npm run dev -- --port 4173 --strictPort 开发；最终静态预览 npm run preview -- --port 4174 --strictPort。预览期间重新构建后需重启 preview。

## 2026-09-14：正式子路径发布

- [x] 确认 gaogaoai.cn 对应 Netlify 项目 prompt-vault-cn。
- [x] 采用 /agent-handbook/；修复子路径 sitemap 与链接检查。
- [x] 适配现有 script-src self：启动脚本外部化，分词函数在构建时展开，无需动态求值。
- [x] 21 个原站内容文件 SHA-1 校验通过；合并 116 个教程页面。
- [x] 类型检查、569 个本地内容链接、CSP 启动行为检查与 14 个 Python 测试通过。
- [x] Netlify 预览部署上传及 HTTP 验证；修复多余重定向造成的预览循环。
- [x] 正式发布 https://gaogaoai.cn/agent-handbook/；591 个线上内容文件哈希一致，21 个原站文件完整保留，15 个 HTTP 检查通过。
- [x] 初始化本地 Git 仓库，检查提交范围与敏感文件。
- [ ] GitHub 创建/推送：连接器无创建仓库能力，本机 gh 尚未登录，已请求用户完成 gh auth login。

发布脚本：scripts/prepare_netlify.py、scripts/publish_netlify.py。原站基线：6aa4585cfc4c3e69df1da9fc。

2026-09-15 正式部署：6aa81ca95e36a16964558968。发布报告：provenance/deployment.json。使用与生产相同 CSP 的本地浏览器已验证中文/英文搜索和三个演示；远程浏览器导航不稳定，线上交互未虚报为实测。

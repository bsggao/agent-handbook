# AI Agent 中文学习指南

基于 Microsoft [AI Agents for Beginners](https://github.com/microsoft/ai-agents-for-beginners) 的非官方中文学习网站。19 章完整课程、原始代码导读、47 个中英术语、8 幅中文技术图、3 个交互模拟，以及可运行的五阶段文档问答与任务助手。

来源提交：`25b7985f3b2dc37a84f4a7387ccd3c9f0e5b1595`；获取日期：2026-09-14。原课程 © Microsoft Corporation / MIT；本项目新增内容也采用 MIT。详见 `LICENSE`、`docs/guide/sources.md` 与 `provenance/`。

## 启动网站

推荐 Node 22 LTS、npm。Python 示例需要 Python 3.12+，与网站运行相互独立。前端不需要账号、API Key、数据库或云服务。

```bash
npm ci
npm run dev -- --port 4173 --strictPort
```

访问 http://localhost:4173 。端口占用时改成其他端口。当前实现实际在 Node 18.20.5/npm 10.8.2 环境构建验证；部分 Mermaid 传递依赖要求更高 Node，推荐维护时使用 Node 22 并保留锁文件。

```bash
npm run typecheck
npm run build
npm run check
npm run preview -- --port 4173 --strictPort
```

构建目录为项目根目录 `dist/`。开发服务器与预览服务器不要同时占用同一端口。

## 网站功能

VitePress + Vue 3 + TypeScript；Markdown 正文；按统一课程元数据生成导航和前后章关系；中文双字/英文分词的本地全站搜索；浅/深色主题；代码高亮与复制；可折叠答案；SVG/Mermaid 与图片放大；移动导航；章节完成、最近阅读和清除进度。

进度只保存于当前站点的浏览器 localStorage；清理站点数据会丢失，不跨设备同步。三个演示为预设教学数据，支持正常/失败场景、下一步、重置，没有模型推理或真实业务操作。

## 运行综合实践

```bash
python3 examples/first_agent.py
python3 examples/assistant/app.py --stage 1
python3 examples/assistant/app.py '现在有多少个任务？' --stage 2
python3 examples/assistant/app.py '购买后多久可以申请退款？' --stage 3
python3 examples/assistant/app.py '退款政策是什么？' --stage 4 --remember '简洁回答'
python3 examples/assistant/app.py '创建任务：复习 RAG' --stage 5 --approve --request-id lesson-001
python3 examples/assistant/evaluate.py
npm run test:examples
```

默认标准库实现，模型决策为规则模拟，检索与本地文件读写是真实执行。详细阶段验收在 `docs/guide/project.md` 与 `examples/assistant/README.md`。可选真实 MAF 实验用 `requirements-cloud.txt` 与 `.env.example`，需云账号/部署/权限且可能计费；未实际调用云端模型。真实凭据不能进入前端或版本控制。

第 18 章离线收据实验：

```bash
python3 -m venv .venv-receipts
source .venv-receipts/bin/activate
python -m pip install -r examples/receipts/requirements.txt
python scripts/run_receipt_notebooks.py
```

Windows 激活使用 `.venv-receipts\Scripts\Activate.ps1`。这里只执行已检查的两个源 Notebook，跳过安装单元格，不是任意代码的安全沙箱。

## 静态部署

可部署到任何静态服务器，不需要后端。域名和子路径必须在构建时确定：

```bash
SITE_URL=https://your-domain.example BASE_PATH=/ npm run build
```

将整个 `dist/` 上传到静态站点根目录。生产部署把 `SITE_URL` 换成真实站点地址，供 sitemap 使用；默认 localhost 仅用于本地预览。子目录例如 `/agent-handbook/`：

```bash
SITE_URL=https://your-domain.example BASE_PATH=/agent-handbook/ npm run build
```

服务器需要正常提供生成的 `.html` 文件、`assets/`、图片、下载与 `404.html`。本站使用明确 `.html` 链接，不依赖 SPA 回退；打开或刷新 `/lessons/tools.html` 应正常工作。子路径部署要连同整个输出挂载到同一子路径。子路径构建后的检查同样需要 `BASE_PATH=/agent-handbook/ npm run check`。

### 独立子域名发布（推荐）

目标域名为 `https://agent-handbook.gaogaoai.cn/`，对应独立 Netlify 项目 `gaogao-agent-handbook`（ID `8d299a49-c6e9-48f5-880f-4ce6fdd2096d`）。站点已发布，阿里云 DNS 与 HTTPS 已验证。正式入口：[AI Agent 中文学习指南](https://agent-handbook.gaogaoai.cn/)。备用地址：[Netlify 站点](https://gaogao-agent-handbook.netlify.app/)。发布状态见 `provenance/subdomain-deployment.json`。

在阿里云的 `gaogaoai.cn` 解析区添加：类型 `CNAME`，主机记录 `agent-handbook`，记录值 `gaogao-agent-handbook.netlify.app`，TTL 使用默认值。解析生效后 Netlify 可申请 HTTPS 证书。无需更改主域名的 NS 或原有解析。

使用 Node 22 LTS 与已登录的 Netlify CLI 执行：

```bash
npm ci
npm run build:subdomain
npm run deploy:subdomain
```

发布脚本复用固定版本 Netlify CLI 的正常登录，将全部文件上传为草稿，等待就绪后发布。部署配置来自 `deploy/subdomain.toml`，根目录 `netlify.toml` 也使用独立站点配置。当前采用手动发布，GitHub 推送不会自动发布网站。

新站的链接和资源从 `/` 开始，sitemap 使用新域名。旧地址已移除，今后只维护独立域名。学习进度保存在各自域名的浏览器存储中，因此旧域名的记录不会自动转移。

### 已移除的旧地址

`gaogaoai.cn/agent-handbook/` 已按要求停用，旧教程文件从主站移除，该路径及子页面直接返回 404，不跳转。主站其余文件保留。今后仅发布独立域名，不再执行旧的子路径合并发布脚本。

## 内容与源码结构

- `content/courses.json`：统一章节元数据。
- `content/chapters/`：人工编写的开篇、实践及必要的全文重写。
- `content/glossary.json`：中英术语。
- `docs/lessons/`：生成后可直接维护/阅读的完整课程页。
- `docs/labs/`：Notebook、Python、.NET 和辅助 Markdown 导读。
- `docs/guide/`：路线、术语、FAQ、综合实践、来源与验证报告。
- `docs/.vitepress/`：导航、搜索、主题与交互组件。
- `docs/public/diagrams/`：本项目绘制的中文 SVG。
- `docs/public/upstream-assets/`：固定提交的本地原图。
- `upstream/`：不可变源文件快照，保留许可证及配置。
- `provenance/`：版本、哈希、章节/文件映射、校订与实际验证记录。

## 更新或新增章节

1. 在 `content/courses.json` 添加编号、slug、来源目录、标题、分组、简介和预计时长。
2. 将实际读取的英文与简中源文件放入 `upstream/`，同时更新来源 commit/日期。不要修改源快照来假装修复了上游。
3. 在 `content/chapters/<slug>-intro.md` 与 `-practice.md` 写目标、前置、直觉、案例、代码解析、错误、练习与答案；必要时用 `<slug>-body.md` 完整替换失效译文。
4. 在 `scripts/editorial.py` 记录精确的英中/代码差异修正。不要只跑翻译替换就认为已完成教学。
5. 执行下列命令，检查覆盖映射及报告，再做桌面和移动预览：

```bash
python3 scripts/import_course.py
python3 scripts/draw_diagrams.py
python3 scripts/prepare_release.py
python3 scripts/update_sources.py
python3 scripts/update_glossary.py
python3 scripts/normalize_typography.py
npm run typecheck
npm run build
npm run check
npm run test:examples
```

`fetch_assets.py` 会联网从已锁定提交获取 Markdown 引用的源图片；日常构建不联网抓取课程。全站构建保留 VitePress 普通死链检查；`.ipynb` 链接以下载处理，不改写为 HTML；下载目标由 `check_content.py` 独立检查。后者还检查构建 HTML 的内部链接、锚点和资源文件。

术语表静态定义与 Vue 筛选同源；修改术语后用 `python3 scripts/update_glossary.py` 同步 Markdown，以保证全站搜索正文和英文术语均命中。

## 验证与已知限制

实际结果见 `docs/guide/verification.md` 与 `PROGRESS.md`。默认综合示例已做行为测试，安全 Notebook 已离线运行。其余云 Notebook、Foundry Local 推理、Browser-Use 网站操作、远程 MCP/A2A、第三方记忆服务和生产负载/部署未执行。原仓库的历史 API、未锁定依赖和示意片段已在对应章标注，未声称全部联网代码即装即用。

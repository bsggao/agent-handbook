## 学完这一章，你会得到什么

你会分清“阅读网站”“运行本地练习”“运行云端 Notebook”三件事，创建隔离的 Python 环境，并知道如何检查模型端点、身份和依赖。你不需要先购买云资源才能开始学习。

前置知识只有文件、目录、终端命令和变量。若没接触过 Python，可以先读[Python 速查](/guide/python.md)；遇到英文缩写可查[术语表](/guide/glossary.md)。

## 先选择你的学习方式

| 方式 | 本机需要什么 | 账号与费用 | 学习成果 |
| --- | --- | --- | --- |
| 阅读课程与交互演示 | 浏览器 | 无需账号与 API Key | 理解请求、工具、证据和状态如何流动 |
| 本项目离线练习 | Python 3.12+ | 无需云服务 | 实际运行规则模拟、词法检索、记忆与评估 |
| 原仓库 Python Notebook | Python 3.12+、Jupyter、Azure CLI、依赖 | 大部分需要 Azure 订阅、Foundry 项目、模型部署及访问权限，可能计费 | 通过原课程的 Microsoft Agent Framework 调用真实模型 |
| 本地模型实验 | Foundry Local 与兼容设备 | 下载模型通常需要网络；推理使用本机资源 | 在设备上运行真实小模型，见第 17 章 |

**补充讲解：** “本地运行 Python”不代表“模型在本地”。Python 中的 `FoundryChatClient` 通常向云端发送请求；只有将推理服务也放到本机，才是本地模型方案。网站的模拟演示不向模型服务发送请求。

## 第一次动手：运行无需网络的练习

在本项目根目录执行：

```bash
python3 --version
python3 examples/assistant/app.py --stage 1
python3 examples/assistant/app.py '现在有多少个任务？' --stage 2
```

Windows 可以使用 `py -3` 替换 `python3`。本项目离线练习只使用标准库，`examples/assistant/requirements.txt` 已说明无需第三方包。

预期第一条实验输出含 `"mode": "模拟演示：预设规则模型，不调用 API"`；第二个实验在全新数据目录返回“当前有 0 个任务”。这是确实执行的 Python 逻辑，模型选择部分由规则模拟。

这一步解决一个很实际的问题：你可以先学会观察输入、工具调用和输出，再处理云端身份与模型权限。

## 获取与本教程一致的原课程

原仓库包含大量其他语言的译文与图片。浅克隆只减少提交历史，不会自动跳过大文件；稀疏检出才决定取哪些目录。

```bash
git clone --filter=blob:none --sparse https://github.com/microsoft/ai-agents-for-beginners.git
cd ai-agents-for-beginners
git checkout 25b7985f3b2dc37a84f4a7387ccd3c9f0e5b1595
git sparse-checkout set 00-course-setup 01-intro-to-ai-agents
```

后续可以把需要的章节加进 `git sparse-checkout set`。Fork 是在 GitHub 上创建你自己的仓库副本，Clone 是把代码取到本机；仅为阅读与运行，不必先 Fork。保留 `.git` 可以核对版本和同步更新。

本项目也保存了已获取的文本与 Notebook 快照 `upstream/`，便于核对。其中尚未运行的云端样例不会被标记为实测通过。若要使用原课程完整资源和开发容器，建议检出原仓库。

## 创建隔离的 Python 环境

虚拟环境（Virtual environment）相当于给这个项目单独准备一个“工具箱”。它隔离安装的包，不隔离文件访问权限，也不是执行不可信代码的安全沙箱。

macOS / Linux：

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -c "import sys; print(sys.executable); print(sys.version)"
```

Windows PowerShell：

```powershell
py -3 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -c "import sys; print(sys.executable); print(sys.version)"
```

看到的解释器路径应在当前 `.venv` 中，版本至少 3.12。用 `python -m pip` 比单独写 `pip` 更容易保证安装到当前解释器。若 PowerShell 策略阻止激活，可直接使用 `.\.venv\Scripts\python.exe -m pip ...`，无需为了教程全局放宽执行策略。

## 固定依赖，避免新旧 SDK 混装

**源版本说明：** 本次读取的根目录 `requirements.txt` 将 `agent-framework-core` 固定为 `1.10.0`，Foundry/OpenAI 集成限制在 1.10.x。源文件注明 1.11.0 对消息类型、搜索工具和 `Agent.run()` 参数有破坏性调整。Notebook 内仍有 `pip install -U agent-framework`；不要在固定环境里重新执行这些无上限升级单元格。

对本教程主要 Foundry Python 示例，使用项目提供的固定依赖文件：

```bash
# 在 AI Agent 中文学习指南项目根目录，激活独立的虚拟环境后执行
python -m pip install -r examples/assistant/requirements-cloud.txt
python -m pip install jupyterlab==4.4.7 ipykernel==6.30.1
python -m pip check
```

这个小依赖集覆盖第 1 章的主要客户端与工具示例，不等于覆盖全课程。原课程的 MCP、A2A、Azure AI Search、浏览器自动化、记忆与签名实验需要相应额外包；各章代码导读保留原始安装声明。完整源依赖位于 `upstream/requirements.txt`，其中仍有未锁定的包。对这些扩展实验应分别建环境、安装、记录 `python -m pip freeze`，不要把静态代码阅读当作依赖兼容性验证。

[MAF 1.10.0 发布记录](https://github.com/microsoft/agent-framework/releases/tag/python-1.10.0)用于核对课程版本；[当前 Microsoft Learn 文档](https://learn.microsoft.com/agent-framework/overview/)可能已展示更高版本 API。迁移时要一起改导入、构造参数、会话方法与运行方法。

## 配置真实模型实验

### 1. 准备项目、部署与权限

原课程以 Microsoft Foundry 为主。你需要 Azure 订阅、可用区域、项目、已部署且支持所需 API 的模型，以及访问项目与模型的权限。模型目录名称不一定等于你的部署名称。不要照抄课程中的模型字符串后假定已有部署。

在 [Microsoft Foundry 门户](https://ai.azure.com/) 创建或选择项目，记录项目端点与部署名称。原设置页含基于 Hub 的旧门户步骤；Foundry 项目类型与服务端 Agent、直接推理是不同路径，按[官方 Foundry 集成说明](https://learn.microsoft.com/agent-framework/integrations/by-component/model-providers/microsoft-foundry)确认所选项目。仅构造 `FoundryChatClient` 不能证明已经注册或部署一个服务端 Agent。

### 2. 使用 Azure CLI 身份

```bash
az login
az account show
```

无浏览器的终端可以使用 `az login --use-device-code`。`AzureCliCredential` 使用 CLI 登录身份；`DefaultAzureCredential` 会尝试多种凭据，CLI 是其中一种，因此多身份环境中应核对最终使用的身份。登录成功仍不代表具有数据平面调用权限。

### 3. 填写本地环境变量

```bash
cp .env.example .env
```

```dotenv
AZURE_AI_PROJECT_ENDPOINT=https://你的实际项目端点
AZURE_AI_MODEL_DEPLOYMENT_NAME=你的实际部署名称
```

`.env` 不提交到版本库，也不放进 `docs/public/`。浏览器无法安全保存 API Key；本网站只展示配置示例，真实请求由你的本地 Python 执行。可以这样只检查变量是否存在，而不打印值：

```bash
python -c "from dotenv import load_dotenv; import os; load_dotenv(); print({k: bool(os.getenv(k)) for k in ['AZURE_AI_PROJECT_ENDPOINT','AZURE_AI_MODEL_DEPLOYMENT_NAME']})"
```

预期两个值均为 `True`，但这只能验证非空，还不能验证端点可达或权限正确。

### 4. 启动 Notebook

```bash
cd upstream
python -m jupyterlab
```

打开 `01-intro-to-ai-agents/code_samples/01-python-agent-framework.ipynb`，选择上述虚拟环境对应的内核，跳过无版本的安装单元格，其余按顺序执行。Jupyter 内核是执行 Python 的进程，和编辑器选中的解释器可能不同；在首个单元格打印 `sys.executable` 核对。

**验收：** 目的地工具返回一个城市列表；Agent 根据该列表回答；流式示例逐段输出文本。具体推荐不是固定答案。本站未使用你的 Azure 账号运行这些请求，因此不承诺在未配置账号的环境中成功。

## 各课程的附加前提

| 实验 | 额外配置 | 需要注意的实际差异 |
| --- | --- | --- |
| 第 5 章 RAG | 主 Python Notebook 用内存知识库 | 不需要 Search 资源，但仍需云模型；.NET 示例使用文件检索，路径不同 |
| 第 6、8 章直接推理 | `AZURE_OPENAI_ENDPOINT`、`AZURE_OPENAI_DEPLOYMENT` | 部分代码使用稳定 `/openai/v1/` Responses API，与项目端点不同 |
| 第 8 章 Bing 工作流 | `BING_CONNECTION_ID` | 需实际创建连接及服务权限；不是默认随模型部署就存在 |
| 第 13 章记忆 | Mem0 / Cognee 及对应服务配置 | 可能需要额外模型、嵌入或存储；查每个 Notebook 的依赖 |
| 第 15 章浏览器 | Chrome、Playwright、Browser-Use、Azure OpenAI 配置 | 网站布局、浏览器路径和接口版本影响结果 |
| 第 16 章 Azure AI Search | 端点与 `AZURE_SEARCH_API_KEY` 同时设置 | 此 Notebook 用密钥认证，否则回退内存检索；仅配 RBAC 不会自动改写它 |
| 第 17 章本地模型 | Foundry Local、可用模型、Chroma | 首次模型与嵌入下载仍需网络，硬件与目录因平台而异 |
| 第 18 章签名 | `jcs`、`pynacl` | 签名与验签可离线；模型集成部分另需模型配置 |

原课程还介绍 MiniMax、Novita 等兼容服务。它们是可选提供者，不承诺免费或所有 API 兼容。该版本不会自动读取 `NOVITA_*` 变量；要显式构造客户端。Foundry Local 主要提供 Chat Completions 接口，不能把仅支持 Responses 的客户端直接换个地址就视为兼容。

## 出错时按这个顺序排查

| 现象 | 常见原因 | 检查与处理 |
| --- | --- | --- |
| `ModuleNotFoundError` | 包安装到了另一个 Python | 打印 `sys.executable`，使用该解释器的 `-m pip` |
| 导入 `ChatMessage` 等失败 | 1.10 代码配上了 1.11+ 包 | 建新环境按固定版本安装，不盲目逐个升级 |
| 401 / 凭据不可用 | 未登录、令牌失效或客户端不匹配 | `az account show`，重新登录，核对身份链 |
| 403 | 身份存在但无权访问 | 检查项目/资源范围与角色；不要把 API Key 到处粘贴排错 |
| 404 / deployment not found | 端点类型或部署名称错误 | 对照门户的实际地址、部署名称及 API 路径 |
| 429 | 速率、并发或配额上限 | 减少并发，尊重 Retry-After，有限次数退避 |
| TLS 证书验证失败 | Python 或企业代理证书链问题 | 修复受信任证书；python.org 安装可运行其 Install Certificates 脚本 |
| Notebook 找不到 `.env` | 当前工作目录不对 | 从仓库根目录启动 Jupyter，确认 dotenv 搜索位置 |

**版本校订：** 原设置页仍含关闭证书校验的旧 GitHub Models 示例。本教程不把它作为解决步骤；修复证书信任链才能恢复对远端身份的验证。更多案例见[排错指南](/guide/faq.md)。

## 自测与练习

1. 为什么网站无需 Key，而 Python Notebook 仍可能收费？
2. `az login` 成功，是否就代表可以调用指定模型？
3. 第 5 章没有 Azure AI Search 时能学到 RAG 吗？

::: details 参考答案
1. 网站只渲染内容和预设数据；Notebook 发出真实模型请求，按账号服务计费。
2. 不代表。还要检查实际身份、资源范围、角色、部署和配额。
3. 能。主 Python 示例将本地字典检索包装为工具，体现检索—生成循环；它不是向量数据库实践。
:::

**扩展实践：** 创建一个全新临时数据目录，运行阶段 2，确认任务数为零；再用 `--stage 3` 查询退款规则，检查返回的 `citations`。参考实现与命令见[综合项目](/guide/project.md)。保留你自己的解释器版本和运行输出，后续排错时会非常有用。

## 下一步

环境准备的目的，是让你能区分配置错误与 Agent 逻辑错误。下一章先从一个旅行助手建立直觉：模型提出什么，应用执行什么，什么情况下应当停止。

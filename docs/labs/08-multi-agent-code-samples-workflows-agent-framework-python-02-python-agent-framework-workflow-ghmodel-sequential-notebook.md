---
title: "08 · 02.python-agent-framework-workflow-ghmodel-sequential"
outline: [2, 3]
---

# 08 · 02.python-agent-framework-workflow-ghmodel-sequential

[返回：多 Agent 协作](/lessons/multi-agent.md) · [不可变原始文件](https://github.com/microsoft/ai-agents-for-beginners/blob/25b7985f3b2dc37a84f4a7387ccd3c9f0e5b1595/08-multi-agent/code_samples/workflows-agent-framework/python/02.python-agent-framework-workflow-ghmodel-sequential.ipynb)

::: warning 原课程完整 Notebook · 静态阅读与代码解析
代码按英文源文件顺序保留，中文说明以同版本译本为基础。原始安装单元格可能含无版本上限的 `-U`；请跳过它们，先按[准备篇](/lessons/setup.md)固定依赖。云端服务、模型权限、网站布局和部分 SDK 接口需在你自己的环境验证。本站没有执行云端请求；第 18 章的离线验证状态单独记录在[检查报告](/guide/verification.md)。
:::

## 运行准备

Python 3.12+；在独立虚拟环境安装源仓库依赖与本页中声明的额外依赖。原文件路径：`upstream/08-multi-agent/code_samples/workflows-agent-framework/python/02.python-agent-framework-workflow-ghmodel-sequential.ipynb`。以原仓库根目录为工作目录，在 Jupyter 中按顺序执行；身份与环境变量见准备篇。

```bash
cd upstream
python -m jupyterlab
```

[下载原始 Notebook](/notebooks/08-multi-agent/code_samples/workflows-agent-framework/python/02.python-agent-framework-workflow-ghmodel-sequential.ipynb)。输出为上游文件保存的历史结果，不能用作本站实测证明。

## ⏩ 使用 Microsoft Foundry 的顺序 Agent 工作流（Python）

## 📋 高级顺序处理教程

本笔记本演示了使用 Microsoft Agent Framework 的 **顺序工作流模式** 。你将学习如何构建复杂的多步骤处理管道，其中 Agent 按特定顺序执行，在阶段之间传递数据和上下文。

> **迁移说明：** 此示例此前引用了 GitHub Models。GitHub Models 已弃用（将于2026年7月退役），因此现在通过 `FoundryChatClient` 使用 **Microsoft Foundry** ，此客户端针对 Azure OpenAI 的 **Responses API** 。

## 🎯 学习目标

### 🔄 **顺序处理模式** 
- **线性工作流设计** ：创建逐步处理管道
- **数据流管理** ：在顺序 Agent 之间传递信息
- **阶段闸处理** ：实现检查点和验证阶段
- **进度跟踪** ：监控工作流执行及中间结果

### 🏗️ **企业管道架构** 
- **业务流程建模** ：将真实业务流程映射到 Agent 工作流
- **质量保证** ：多阶段验证与审查流程
- **文档处理** ：顺序文档分析与转换
- **内容制作** ：带审查和批准阶段的编辑工作流

### 📊 **高级工作流功能** 
- **上下文保持** ：跨工作流阶段维护状态
- **错误传播** ：处理顺序处理中的故障
- **性能优化** ：高效顺序执行模式
- **审计追踪** ：完整跟踪顺序操作

## ⚙️ 前提条件与设置

### 📦 **依赖项** 
```bash
pip install agent-framework -U
```

### 🔑 **配置** 

使用 Azure CLI 登录（`az login`）以便 `AzureCliCredential` 进行身份验证，然后设置你的 Microsoft Foundry 项目信息。

```text
AZURE_AI_PROJECT_ENDPOINT=https://<your-project>.services.ai.azure.com
AZURE_AI_MODEL_DEPLOYMENT_NAME=gpt-5-mini
```

## 🏢 **企业顺序工作流用例** 

### 📝 **文档处理管道** 
```
Raw Document → Content Extraction → Analysis → Validation → Final Output
```

### 🔍 **质量保证工作流** 
```
Initial Review → Technical Validation → Compliance Check → Final Approval
```

### 📰 **内容制作管道** 
```
Research → Writing → Editing → Review → Publishing
```

### 💼 **业务流程自动化** 
```
Data Collection → Processing → Analysis → Report Generation → Distribution
```

## 🎨 **顺序工作流设计原则** 

- **🔗 线性推进** ：每个阶段依赖于前一阶段的输出
- **📋 状态管理** ：跨所有阶段保存上下文和数据
- **🛡️ 错误处理** ：优雅地管理任一阶段的失败
- **📊 进度监控** ：跟踪每个阶段的完成情况和性能
- **🔄 阶段可重用性** ：设计可复用的工作流组件

让我们构建复杂的顺序处理工作流吧！🚀

### 代码单元格 2

阅读提示：跟踪本单元格读取的变量、修改的状态以及返回值。按原顺序执行，确认依赖的前序变量已经存在。

```python
# Already covered by repo-level requirements.txt; left for reference.
# !pip install agent-framework -U
```

### 代码单元格 3

模型连接：project_endpoint 是项目地址，model 是实际部署名称；credential 提供访问身份。客户端创建本身不证明已经部署服务端 Agent。

```python
from agent_framework import (
    WorkflowBuilder,
    WorkflowEvent,
    WorkflowViz,
)
from agent_framework.foundry import FoundryChatClient
from azure.identity import AzureCliCredential
```

### 代码单元格 4

配置加载：从本地环境读取端点与部署名；缺少变量时先修复配置，不要把密钥写进代码。

```python
import os
import base64
from dotenv import load_dotenv
```

### 代码单元格 5

配置加载：从本地环境读取端点与部署名；缺少变量时先修复配置，不要把密钥写进代码。

```python
load_dotenv()
```

### 代码单元格 6

模型连接：project_endpoint 是项目地址，model 是实际部署名称；credential 提供访问身份。客户端创建本身不证明已经部署服务端 Agent。

```python
# Configure the Microsoft Foundry client with keyless authentication.
# FoundryChatClient targets the Azure OpenAI Responses API.
provider = FoundryChatClient(
    project_endpoint=os.environ["AZURE_AI_PROJECT_ENDPOINT"],
    model=os.environ["AZURE_AI_MODEL_DEPLOYMENT_NAME"],
    credential=AzureCliCredential(),
)
```

### 代码单元格 7

阅读提示：跟踪本单元格读取的变量、修改的状态以及返回值。按原顺序执行，确认依赖的前序变量已经存在。

```python
SalesAgentName = "Sales-Agent"
SalesAgentInstructions = "You are my furniture sales consultant, you can find different furniture elements from the pictures and give me a purchase suggestion"
```

### 代码单元格 8

阅读提示：跟踪本单元格读取的变量、修改的状态以及返回值。按原顺序执行，确认依赖的前序变量已经存在。

```python
PriceAgentName = "Price-Agent"
PriceAgentInstructions = """You are a furniture pricing specialist and budget consultant. Your responsibilities include:
        1. Analyze furniture items and provide realistic price ranges based on quality, brand, and market standards
        2. Break down pricing by individual furniture pieces
        3. Provide budget-friendly alternatives and premium options
        4. Consider different price tiers (budget, mid-range, premium)
        5. Include estimated total costs for room setups
        6. Suggest where to find the best deals and shopping recommendations
        7. Factor in additional costs like delivery, assembly, and accessories
        8. Provide seasonal pricing insights and best times to buy
        Always format your response with clear price breakdowns and explanations for the pricing rationale."""
```

### 代码单元格 9

阅读提示：跟踪本单元格读取的变量、修改的状态以及返回值。按原顺序执行，确认依赖的前序变量已经存在。

```python
QuoteAgentName = "Quote-Agent"
QuoteAgentInstructions = """You are a assistant that create a quote for furniture purchase.
        1. Create a well-structured quote document that includes:
        2. A title page with the document title, date, and client name
        3. An introduction summarizing the purpose of the document
        4. A summary section with total estimated costs and recommendations
        5. Use clear headings, bullet points, and tables for easy readability
        6. All quotes are presented in markdown form"""
```

### 代码单元格 10

行为约束：instructions 引导模型，不能替代执行器的权限验证、次数限制和结果检查。

```python
sales_agent = provider.as_agent(
    name=SalesAgentName,
    instructions=SalesAgentInstructions,
)

price_agent = provider.as_agent(
    name=PriceAgentName,
    instructions=PriceAgentInstructions,
)

quote_agent = provider.as_agent(
    name=QuoteAgentName,
    instructions=QuoteAgentInstructions,
)
```

### 代码单元格 11

阅读提示：跟踪本单元格读取的变量、修改的状态以及返回值。按原顺序执行，确认依赖的前序变量已经存在。

```python
workflow = (
    WorkflowBuilder(start_executor=sales_agent)
    .add_edge(sales_agent, price_agent)
    .add_edge(price_agent, quote_agent)
    .build()
)
```

### 代码单元格 12

输出观察：print 展示应用可观察结果；预存输出和现场结果可能不同，它不是模型内部思考记录。

```python
print("Generating workflow visualization...")
viz = WorkflowViz(workflow)
# Print out the mermaid string.
print("Mermaid string: \n=======")
print(viz.to_mermaid())
print("=======")
# Print out the DiGraph string.
print("DiGraph string: \n=======")
print(viz.to_digraph())
print("=======")
# SVG export needs the optional graphviz extra (`pip install graphviz`) plus the
# graphviz system binary; if it's not available, fall back to the text strings above.
try:
    svg_file = viz.export(format="svg")
    print(f"SVG file saved to: {svg_file}")
except ImportError as e:
    svg_file = None
    print(f"SVG export skipped (install graphviz to enable): {e}")
```

### 代码单元格 13

阅读提示：跟踪本单元格读取的变量、修改的状态以及返回值。按原顺序执行，确认依赖的前序变量已经存在。

```python
class DatabaseEvent(WorkflowEvent): ...
```

### 代码单元格 14

输出观察：print 展示应用可观察结果；预存输出和现场结果可能不同，它不是模型内部思考记录。

```python
# Display the exported workflow SVG inline in the notebook

from IPython.display import SVG, display, HTML
import os

print(f"Attempting to display SVG file at: {svg_file}")

if svg_file and os.path.exists(svg_file):
    try:
        # Preferred: direct SVG rendering
        display(SVG(filename=svg_file))
    except Exception as e:
        print(f"⚠️ Direct SVG render failed: {e}. Falling back to raw HTML.")
        try:
            with open(svg_file, "r", encoding="utf-8") as f:
                svg_text = f.read()
            display(HTML(svg_text))
        except Exception as inner:
            print(f"❌ Fallback HTML render also failed: {inner}")
else:
    print("❌ SVG file not found. Ensure viz.export(format='svg') ran successfully.")
```

### 代码单元格 15

阅读提示：跟踪本单元格读取的变量、修改的状态以及返回值。按原顺序执行，确认依赖的前序变量已经存在。

```python
image_path = "../imgs/home.png"
with open(image_path, "rb") as image_file:
    image_b64 = base64.b64encode(image_file.read()).decode()
image_uri = f"data:image/png;base64,{image_b64}"
```

### 代码单元格 16

阅读提示：跟踪本单元格读取的变量、修改的状态以及返回值。按原顺序执行，确认依赖的前序变量已经存在。

```python
# Note: the original notebook used a multimodal message with an image of a
# living room. To keep the lesson focused on sequential workflow mechanics, this
# migration passes a textual description of the same scene as the workflow input.
# Agents accept a plain string, matching the basic and concurrent samples.
message = (
    "I am furnishing a modern living room and want pieces that fit a warm, "
    "inviting style: a comfortable three-seat sofa, two accent armchairs, a "
    "wooden coffee table, a TV stand, a floor lamp, and a soft area rug. "
    "Please find appropriate furniture and give the corresponding price for "
    "each piece, then produce a final purchase quote."
)
```

### 代码单元格 17

阅读提示：跟踪本单元格读取的变量、修改的状态以及返回值。按原顺序执行，确认依赖的前序变量已经存在。

```python
# Workflow.run_stream is no longer part of the public API; the current Workflow
# returns a results object whose `get_outputs()` produces the AgentResponse from
# each output executor. The final stage (quote_agent) is the only output here.
events = await workflow.run(message)
outputs = events.get_outputs()
result = outputs[0].text if outputs else ""
```

### 代码单元格 18

阅读提示：跟踪本单元格读取的变量、修改的状态以及返回值。按原顺序执行，确认依赖的前序变量已经存在。

```python
result.replace("None", "")
```


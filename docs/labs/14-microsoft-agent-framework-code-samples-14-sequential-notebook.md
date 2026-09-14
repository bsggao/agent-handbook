---
title: "14 · 14-sequential"
outline: [2, 3]
---

# 14 · 14-sequential

[返回：Microsoft Agent Framework](/lessons/agent-framework.md) · [不可变原始文件](https://github.com/microsoft/ai-agents-for-beginners/blob/25b7985f3b2dc37a84f4a7387ccd3c9f0e5b1595/14-microsoft-agent-framework/code-samples/14-sequential.ipynb)

::: warning 原课程完整 Notebook · 静态阅读与代码解析
代码按英文源文件顺序保留，中文说明以同版本译本为基础。原始安装单元格可能含无版本上限的 `-U`；请跳过它们，先按[准备篇](/lessons/setup.md)固定依赖。云端服务、模型权限、网站布局和部分 SDK 接口需在你自己的环境验证。本站没有执行云端请求；第 18 章的离线验证状态单独记录在[检查报告](/guide/verification.md)。
:::

## 运行准备

Python 3.12+；在独立虚拟环境安装源仓库依赖与本页中声明的额外依赖。原文件路径：`upstream/14-microsoft-agent-framework/code-samples/14-sequential.ipynb`。以原仓库根目录为工作目录，在 Jupyter 中按顺序执行；身份与环境变量见准备篇。

```bash
cd upstream
python -m jupyterlab
```

[下载原始 Notebook](/notebooks/14-microsoft-agent-framework/code-samples/14-sequential.ipynb)。输出为上游文件保存的历史结果，不能用作本站实测证明。

## 两个顺序 Agent：

1. **前台 Agent** ：负责城市初步景点推荐
2. **礼宾 Agent** ：根据受欢迎程度审核并评价前台的推荐

## 顺序编排的主要优势：

- **迭代改进** ：第二个 Agent 优化第一个 Agent 的结果
- **专业分工** ：每个 Agent 在流程中承担特定角色
- **质量控制** ：内置审核和验证步骤
- **清晰的信息流** ：Agent 之间的结构化交接

## 前提条件：
- 已安装 Microsoft Agent Framework
- 已配置 Microsoft Foundry 项目端点和模型部署（`AZURE_AI_PROJECT_ENDPOINT`，`AZURE_AI_MODEL_DEPLOYMENT_NAME`）
- 通过 Azure CLI 完成身份验证（`az login`）
- 理解基本 Agent 概念

### 代码单元格 2

配置加载：从本地环境读取端点与部署名；缺少变量时先修复配置，不要把密钥写进代码。

数据结构：Pydantic 模型定义字段类型；只有传入实际的 response_format 并检查解析结果，才能约束本次输出。

模型连接：project_endpoint 是项目地址，model 是实际部署名称；credential 提供访问身份。客户端创建本身不证明已经部署服务端 Agent。

```python
import asyncio
import json
import os
from typing import Any, cast

from agent_framework import Message, WorkflowBuilder
from agent_framework.foundry import FoundryChatClient
from azure.identity import AzureCliCredential
from dotenv import load_dotenv
from IPython.display import HTML, display
from pydantic import BaseModel

print("All imports successful!")
```

## 步骤 1：为结构化输出定义 Pydantic 模型

这些模型定义了每个 Agent 将返回的架构。前台 Agent 提供推荐，礼宾 Agent 提供评论和评分。

### 代码单元格 4

数据结构：Pydantic 模型定义字段类型；只有传入实际的 response_format 并检查解析结果，才能约束本次输出。

```python
class AttractionRecommendation(BaseModel):
    """Attraction recommendation from the front desk agent."""

    city: str
    attraction_name: str
    description: str
    category: str  # e.g., "museum", "landmark", "park", "entertainment"
    recommended_duration: str  # e.g., "2-3 hours", "half day"
    why_recommended: str
    best_time_to_visit: str


class AttractionReview(BaseModel):
    """Expert review and rating from the concierge agent."""

    attraction_name: str
    city: str
    popularity_score: int  # 1-10 scale
    popularity_reasoning: str
    visitor_rating: float  # 1.0-5.0 scale
    pros: list[str]
    cons: list[str]
    concierge_recommendation: str
    alternative_suggestions: list[str]
```

## 步骤 2：加载环境变量并配置 Foundry 提供程序

使用带有无密钥 `AzureCliCredential` 认证的 `FoundryChatClient`，与第01–13课中使用的模式相匹配。

### 代码单元格 6

配置加载：从本地环境读取端点与部署名；缺少变量时先修复配置，不要把密钥写进代码。

模型连接：project_endpoint 是项目地址，model 是实际部署名称；credential 提供访问身份。客户端创建本身不证明已经部署服务端 Agent。

输出观察：print 展示应用可观察结果；预存输出和现场结果可能不同，它不是模型内部思考记录。

```python
# Load environment variables
load_dotenv()

# Configure the Microsoft Foundry provider with keyless authentication
provider = FoundryChatClient(
    project_endpoint=os.environ["AZURE_AI_PROJECT_ENDPOINT"],
    model=os.environ["AZURE_AI_MODEL_DEPLOYMENT_NAME"],
    credential=AzureCliCredential(),
)

print("Microsoft Foundry provider configured successfully!")
```

## 第3步：创建两个顺序 Agent

每个 Agent 在顺序工作流中都有特定的角色。前台 Agent 负责提出建议，礼宾 Agent 负责审查并进行评分。

### 代码单元格 8

行为约束：instructions 引导模型，不能替代执行器的权限验证、次数限制和结果检查。

检索过程：跟踪查询、候选结果和实际选入的证据；检索为空时应明确返回缺失，而不是补写答案。

```python
# Agent 1: Front Desk Agent (Makes initial recommendations)
front_desk_agent = provider.as_agent(
    name="front-desk-agent",
    instructions=(
        "You are a knowledgeable hotel front desk agent who specializes in local attractions. "
        "When a guest asks about attractions in a city, provide a single, well-researched recommendation "
        "for a popular tourist attraction. Focus on giving practical information including what makes "
        "this attraction special, how long to spend there, and the best time to visit. "
        "Be helpful and enthusiastic about your recommendation. "
        "Return structured JSON matching the AttractionRecommendation schema."
    ),
)

# Agent 2: Concierge Agent (Reviews and rates recommendations)
concierge_agent = provider.as_agent(
    name="concierge-agent",
    instructions=(
        "You are an expert concierge with extensive knowledge of tourist attractions worldwide. "
        "You will receive an attraction recommendation and must provide an expert review and rating. "
        "Evaluate the recommendation based on the attraction's popularity, visitor satisfaction, "
        "and overall quality. Provide a popularity score (1-10), visitor rating (1.0-5.0), "
        "list pros and cons, and give your professional assessment. "
        "Also suggest alternative attractions if appropriate. "
        "Return structured JSON matching the AttractionReview schema."
    ),
)
```

## 第4步：构建顺序工作流

`WorkflowBuilder` 创建了一个工作流，其中：
1. **前台 Agent** 接收用户输入并给出建议
2. **礼宾 Agent** 接收前台的建议并提供专家评审
3. **输出** 包含原始建议和专家评审

### 代码单元格 10

阅读提示：跟踪本单元格读取的变量、修改的状态以及返回值。按原顺序执行，确认依赖的前序变量已经存在。

```python
# Build the sequential workflow with WorkflowBuilder
workflow = (
    WorkflowBuilder(
        start_executor=front_desk_agent,
        output_executors=[front_desk_agent, concierge_agent],
    )
    .add_edge(front_desk_agent, concierge_agent)
    .build()
)

display(HTML("""
<div style='padding: 20px; background: linear-gradient(135deg, #ff7043 0%, #ff5722 100%); color: white; border-radius: 8px; margin: 10px 0;'>
    <h3 style='margin: 0 0 15px 0;'>Sequential Workflow Built Successfully!</h3>
    <p style='margin: 0; line-height: 1.6;'>
        <strong>Flow:</strong><br>
        • User Input → <strong>Front Desk Agent</strong> (recommendation)<br>
        • Front Desk Output → <strong>Concierge Agent</strong> (review & rating)<br>
        • Final Output → Combined recommendation + expert review
    </p>
</div>
"""))
```

### 代码单元格 11

异步执行：async def 定义协程，await 等待结果；普通 .py 脚本需要 asyncio.run() 入口，Notebook 支持顶层 await。

```python
async def display_attraction_recommendation(city: str):
    """Run the sequential workflow and display formatted results."""

    display(HTML(f"""
    <div style='padding: 20px; background: #fff3e0; border-left: 4px solid #ff9800; border-radius: 8px; margin: 20px 0;'>
        <h3 style='margin: 0 0 10px 0; color: #e65100;'>Processing Attraction Recommendation for {city}</h3>
        <p style='margin: 0;'><strong>Status:</strong> Running sequential workflow...</p>
    </div>
    """))

    # Run the workflow. With WorkflowBuilder(output_executors=[a1, a2]),
    # outputs is a list of AgentResponse objects, one per output executor.
    events = await workflow.run(f"I want to visit an attraction in {city}")
    outputs = events.get_outputs()

    front_desk_response = outputs[0].text if len(outputs) > 0 else None
    concierge_response = outputs[1].text if len(outputs) > 1 else None

    # Display results
    display(HTML(f"""
    <div style='padding: 25px; background: linear-gradient(135deg, #4caf50 0%, #8bc34a 100%); color: white; border-radius: 12px;
                box-shadow: 0 4px 12px rgba(76,175,80,0.3); margin: 20px 0;'>
        <h2 style='margin: 0 0 20px 0;'>Attraction Recommendation for {city}</h2>
        <p style='margin: 0; font-size: 14px; opacity: 0.9;'>Generated by sequential agent workflow</p>
    </div>
    """))

    # Process and display responses
    if front_desk_response:
        try:
            recommendation_data = AttractionRecommendation.model_validate_json(front_desk_response)
            display_front_desk_section(recommendation_data)
        except Exception as e:
            display(HTML(f"""
            <div style='padding: 15px; background: #ffcdd2; border-left: 4px solid #f44336; border-radius: 4px; margin: 10px 0;'>
                <strong>Error parsing front desk response:</strong> {str(e)}
                <details><summary>Raw response</summary>{front_desk_response}</details>
            </div>
             """))

    if concierge_response:
        try:
            review_data = AttractionReview.model_validate_json(concierge_response)
            display_concierge_section(review_data)
        except Exception as e:
            display(HTML(f"""
            <div style='padding: 15px; background: #ffcdd2; border-left: 4px solid #f44336; border-radius: 4px; margin: 10px 0;'>
                <strong>Error parsing concierge response:</strong> {str(e)}
                <details><summary>Raw response</summary>{concierge_response}</details>
            </div>
            """))


def display_front_desk_section(data: AttractionRecommendation):
    """Display front desk recommendation in a formatted section."""

    display(HTML(f"""
    <div style='padding: 20px; background: #e3f2fd; border-radius: 8px; margin: 15px 0; border-left: 4px solid #2196f3;'>
        <h3 style='margin: 0 0 15px 0; color: #1976d2;'>🏨 Front Desk Recommendation</h3>
        <div style='margin-bottom: 15px;'>
            <h4 style='margin: 0 0 8px 0; color: #333;'>{data.attraction_name}</h4>
            <span style='background: #2196f3; color: white; padding: 4px 8px; border-radius: 12px; font-size: 12px;'>{data.category}</span>
        </div>
        <div style='margin-bottom: 15px;'>
            <strong style='color: #333;'>Description:</strong> {data.description}
        </div>
        <div style='margin-bottom: 10px;'>
            <strong style='color: #333;'>Why Recommended:</strong> {data.why_recommended}
        </div>
        <div style='margin-bottom: 10px;'>
            <strong style='color: #333;'>Recommended Duration:</strong> {data.recommended_duration}
        </div>
        <div>
            <strong style='color: #333;'>Best Time to Visit:</strong> {data.best_time_to_visit}
        </div>
    </div>
    """))


def display_concierge_section(data: AttractionReview):
    """Display concierge review in a formatted section."""

    # Create star rating display
    star_rating = "⭐" * int(data.visitor_rating) + "☆" * (5 - int(data.visitor_rating))

    # Create popularity bar
    popularity_bar = "🟩" * data.popularity_score + "⬜" * (10 - data.popularity_score)

    pros_list = "".join([f"<li style='color: #4caf50;'>✓ {pro}</li>" for pro in data.pros])
    cons_list = "".join([f"<li style='color: #f44336;'>✗ {con}</li>" for con in data.cons])
    alternatives_list = "".join([f"<li>{alt}</li>" for alt in data.alternative_suggestions])

    display(HTML(f"""
    <div style='padding: 20px; background: #fff3e0; border-radius: 8px; margin: 15px 0; border-left: 4px solid #ff9800;'>
        <h3 style='margin: 0 0 15px 0; color: #f57c00;'>🎩 Concierge Expert Review</h3>

        <div style='display: grid; grid-template-columns: 1fr 1fr; gap: 20px; margin-bottom: 20px;'>
            <div style='background: rgba(255,152,0,0.1); padding: 15px; border-radius: 8px;'>
                <h4 style='margin: 0 0 8px 0; color: #333;'>Popularity Score</h4>
                <div style='font-size: 24px; font-weight: bold; color: #f57c00;'>{data.popularity_score}/10</div>
                <div style='font-size: 12px; margin-top: 5px;'>{popularity_bar}</div>
            </div>
            <div style='background: rgba(255,152,0,0.1); padding: 15px; border-radius: 8px;'>
                <h4 style='margin: 0 0 8px 0; color: #333;'>Visitor Rating</h4>
                <div style='font-size: 20px; font-weight: bold; color: #f57c00;'>{data.visitor_rating}/5.0</div>
                <div style='font-size: 16px; margin-top: 5px;'>{star_rating}</div>
            </div>
        </div>

        <div style='margin-bottom: 15px;'>
            <strong style='color: #333;'>Popularity Reasoning:</strong> {data.popularity_reasoning}
        </div>

        <div style='display: grid; grid-template-columns: 1fr 1fr; gap: 20px; margin-bottom: 15px;'>
            <div>
                <h4 style='margin: 0 0 8px 0; color: #333;'>Pros:</h4>
                <ul style='margin: 0; padding-left: 20px;'>{pros_list}</ul>
            </div>
            <div>
                <h4 style='margin: 0 0 8px 0; color: #333;'>Cons:</h4>
                <ul style='margin: 0; padding-left: 20px;'>{cons_list}</ul>
            </div>
        </div>
        <div style='margin-bottom: 15px;'>
            <strong style='color: #333;'>Concierge Recommendation:</strong> {data.concierge_recommendation}
        </div>

        <div>
            <h4 style='margin: 0 0 8px 0; color: #333;'>Alternative Suggestions:</h4>
            <ul style='margin: 0; padding-left: 20px; color: #555;'>{alternatives_list}</ul>
        </div>
    </div>
    """))


# Test with Stockholm
await display_attraction_recommendation("Stockholm")
```

## 第8步：工作流分析 - 理解顺序流程

让我们检查 Agent 之间的信息流，并分析对话历史。

### 代码单元格 13

异步执行：async def 定义协程，await 等待结果；普通 .py 脚本需要 asyncio.run() 入口，Notebook 支持顶层 await。

```python
async def analyze_sequential_flow(city: str):
    """Analyze the sequential flow between agents."""

    display(HTML(f"""
    <div style='padding: 20px; background: #f3e5f5; border-left: 4px solid #9c27b0; border-radius: 8px; margin: 20px 0;'>
        <h3 style='margin: 0 0 10px 0; color: #7b1fa2;'>Sequential Flow Analysis for {city}</h3>
        <p style='margin: 0;'>Examining agent interactions and information handoff...</p>
    </div>
    """))

    # Run the workflow
    user_input = f"I want to visit an attraction in {city}"
    events = await workflow.run(user_input)
    outputs = events.get_outputs()

    # Reconstruct the conversation flow as a list of (author, text) steps.
    # outputs is a list of AgentResponse objects, ordered to match output_executors.
    steps = [("user", user_input)]
    if len(outputs) > 0:
        steps.append(("front-desk-agent", outputs[0].text))
    if len(outputs) > 1:
        steps.append(("concierge-agent", outputs[1].text))

    display(HTML(f"""
    <div style='padding: 25px; background: #f3e5f5; border-radius: 12px; margin: 20px 0;'>
        <h2 style='margin: 0 0 20px 0; color: #7b1fa2;'>Conversation Flow Analysis</h2>
    </div>
    """))

    # Display each step in the sequence
    for i, (author, text) in enumerate(steps, 1):
        role_color = {
            "user": "#2196f3",
            "front-desk-agent": "#4caf50",
            "concierge-agent": "#ff9800"
        }.get(author, "#666666")

        role_name = {
            "user": "👤 User",
            "front-desk-agent": "🏨 Front Desk Agent",
            "concierge-agent": "🎩 Concierge Agent"
        }.get(author, "Unknown")

        # Truncate long messages for flow analysis
        content_preview = text[:200] + "..." if len(text) > 200 else text
        display(HTML(f"""
        <div style='padding: 15px; background: white; border-left: 4px solid {role_color}; border-radius: 4px; margin: 10px 0; box-shadow: 0 2px 4px rgba(0,0,0,0.1);'>
            <div style='display: flex; align-items: center; margin-bottom: 10px;'>
                <span style='font-weight: bold; color: {role_color}; margin-right: 10px;'>Step {i}:</span>
                <span style='font-weight: bold; color: {role_color};'>{role_name}</span>
            </div>
            <div style='color: #555; font-size: 14px; line-height: 1.4;'>
                {content_preview}
            </div>
        </div>
        """))

    # Analyze the flow
    display(HTML(f"""
    <div style='padding: 20px; background: linear-gradient(135deg, #9c27b0 0%, #673ab7 100%); color: white; border-radius: 8px; margin: 20px 0;'>
        <h3 style='margin: 0 0 15px 0;'>Flow Analysis Summary</h3>
        <ul style='margin: 0; padding-left: 20px; line-height: 1.6;'>
            <li><strong>Total Steps:</strong> {len(steps)}</li>
            <li><strong>Agents Involved:</strong> 2 (Front Desk + Concierge)</li>
            <li><strong>Flow Pattern:</strong> Linear sequential (User → Agent 1 → Agent 2)</li>
            <li><strong>Information Handoff:</strong> Front desk recommendation becomes concierge input</li>
            <li><strong>Output Quality:</strong> Enhanced through expert review and rating</li>
        </ul>
    </div>
    """))


# Analyze the flow for Barcelona
await analyze_sequential_flow("Barcelona")
```


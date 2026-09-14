---
title: "14 · 14-concurrent"
outline: [2, 3]
---

# 14 · 14-concurrent

[返回：Microsoft Agent Framework](/lessons/agent-framework.md) · [不可变原始文件](https://github.com/microsoft/ai-agents-for-beginners/blob/25b7985f3b2dc37a84f4a7387ccd3c9f0e5b1595/14-microsoft-agent-framework/code-samples/14-concurrent.ipynb)

::: warning 原课程完整 Notebook · 静态阅读与代码解析
代码按英文源文件顺序保留，中文说明以同版本译本为基础。原始安装单元格可能含无版本上限的 `-U`；请跳过它们，先按[准备篇](/lessons/setup.md)固定依赖。云端服务、模型权限、网站布局和部分 SDK 接口需在你自己的环境验证。本站没有执行云端请求；第 18 章的离线验证状态单独记录在[检查报告](/guide/verification.md)。
:::

## 运行准备

Python 3.12+；在独立虚拟环境安装源仓库依赖与本页中声明的额外依赖。原文件路径：`upstream/14-microsoft-agent-framework/code-samples/14-concurrent.ipynb`。以原仓库根目录为工作目录，在 Jupyter 中按顺序执行；身份与环境变量见准备篇。

```bash
cd upstream
python -m jupyterlab
```

[下载原始 Notebook](/notebooks/14-microsoft-agent-framework/code-samples/14-concurrent.ipynb)。输出为上游文件保存的历史结果，不能用作本站实测证明。

## 使用并发编排的旅行推荐

本笔记本演示了使用 Microsoft Agent Framework 的 **并发编排** 。我们将构建一个旅行推荐系统，包含三个专门 Agent，协同并行工作以提供全面的旅行见解。

## 你将学到：
1. **并发编排** ：并行运行多个 Agent（扇出/扇入模式）
2. **ConcurrentBuilder** ：用于构建并发工作流的高级 API
3. **旅行推荐** ：三个专门 Agent 协同工作
4. **默认聚合** ：合并多个 Agent 响应
5. **性能优势** ：并行执行与顺序处理的对比


## 三个专门 Agent：

1. **景点 Agent** ：旅游景点、活动、地标
2. **餐饮 Agent** ：当地美食、餐厅、餐饮体验
3. **历史 Agent** ：历史事实、文化意义、背景

### 代码单元格 2

配置加载：从本地环境读取端点与部署名；缺少变量时先修复配置，不要把密钥写进代码。

数据结构：Pydantic 模型定义字段类型；只有传入实际的 response_format 并检查解析结果，才能约束本次输出。

模型连接：project_endpoint 是项目地址，model 是实际部署名称；credential 提供访问身份。客户端创建本身不证明已经部署服务端 Agent。

```python
import asyncio
import json
import os
from typing import Any, cast

from agent_framework import (
    Executor,
    Message,
    WorkflowBuilder,
    WorkflowContext,
    handler,
)
from agent_framework.foundry import FoundryChatClient
from azure.identity import AzureCliCredential
from dotenv import load_dotenv
from IPython.display import HTML, display
from pydantic import BaseModel

print("All imports successful!")
```

## 第一步：定义用于结构化输出的 Pydantic 模型

这些模型定义了每个专用 Agent 将返回的架构。这确保了所有 Agent 的响应具有一致性且易于解析。

## 第一步：定义用于结构化输出的 Pydantic 模型

这些模型定义了每个专用 Agent 将返回的架构。这确保了所有 Agent 返回的响应都是一致且可解析的。

### 代码单元格 5

数据结构：Pydantic 模型定义字段类型；只有传入实际的 response_format 并检查解析结果，才能约束本次输出。

```python
class AttractionsRecommendation(BaseModel):
    """Tourist attractions and activities recommendations."""

    destination: str
    top_attractions: list[str]
    activities: list[str]
    best_time_to_visit: str
    transportation_tips: str  


class DiningRecommendation(BaseModel):
    """Food and dining recommendations."""

    destination: str
    local_cuisine: str
    must_try_dishes: list[str]
    recommended_restaurants: list[str]
    food_experiences: list[str]
    dining_etiquette: str


class HistoryRecommendation(BaseModel):
    """Historical and cultural information."""

    destination: str
    historical_significance: str
    cultural_highlights: list[str]
    important_periods: list[str]
    cultural_experiences: list[str]
    interesting_facts: list[str]
```

## 第2步：加载环境变量并配置 Foundry 提供程序

使用 `FoundryChatClient`，并采用无密钥的 `AzureCliCredential` 认证，遵循第01至13课中使用的模式。

### 代码单元格 7

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

## 第3步：创建三个专用旅行 Agent

### 代码单元格 9

行为约束：instructions 引导模型，不能替代执行器的权限验证、次数限制和结果检查。

```python
# Agent 1: Tourist Attractions Expert
attractions_agent = provider.as_agent(
    name="attractions-agent",
    instructions=(
        "You are a tourism expert specializing in attractions and activities. "
        "When given a travel destination, provide comprehensive recommendations for "
        "tourist attractions, activities, best times to visit, and transportation tips. "
        "Focus on popular landmarks, unique experiences, and practical travel advice. "
        "Return structured JSON matching the AttractionsRecommendation schema."
    ),
)

# Agent 2: Food and Dining Expert
dining_agent = provider.as_agent(
    name="dining-agent",
    instructions=(
        "You are a culinary expert specializing in local food and dining experiences. "
        "When given a travel destination, provide recommendations for local cuisine, "
        "must-try dishes, recommended restaurants, and unique food experiences. "
        "Include dining etiquette and cultural food customs. "
        "Return structured JSON matching the DiningRecommendation schema."
    ),
)


# Agent 3: History and Culture Expert
history_agent = provider.as_agent(
    name="history-agent",
    instructions=(
        "You are a historian and cultural expert. "
        "When given a travel destination, provide historical context, cultural significance, "
        "important historical periods, cultural experiences, and interesting facts. "
        "Focus on helping travelers understand the cultural heritage and historical importance. "
        "Return structured JSON matching the HistoryRecommendation schema."
    ),
)
```

## 第4步：构建并发工作流

使用带有小型调度器执行器和 `add_fan_out_edges` 的 `WorkflowBuilder`：
1. **调度器** 将相同输入广播给所有三个 Agent
2. **三个 Agent** 并行运行
3. **输出** 分别收集每个 Agent 的响应

### 代码单元格 11

异步执行：async def 定义协程，await 等待结果；普通 .py 脚本需要 asyncio.run() 入口，Notebook 支持顶层 await。

```python
# A passthrough executor that broadcasts the user input to every agent in parallel.
class InputDispatcher(Executor):
    """Forward the user input unchanged to all participating agents."""

    @handler
    async def forward(self, text: str, ctx: WorkflowContext[str]) -> None:
        await ctx.send_message(text)


dispatcher = InputDispatcher(id="dispatcher")
agents = [attractions_agent, dining_agent, history_agent]

workflow = (
    WorkflowBuilder(
        start_executor=dispatcher,
        output_executors=agents,
    )
    .add_fan_out_edges(dispatcher, agents)
    .build()
)

display(HTML("""
<div style='padding: 20px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; border-radius: 8px; margin: 10px 0;'>
    <h3 style='margin: 0 0 15px 0;'>Concurrent Workflow Built Successfully!</h3>
    <p style='margin: 0; line-height: 1.6;'>
        <strong>Architecture:</strong><br>
        • Input → <strong>Dispatcher</strong> (fan-out)<br>
        • <strong>3 Agents</strong> run in parallel (attractions, dining, history)<br>
        • Output → 3 AgentResponse objects, one per agent
    </p>
</div>
"""))
```

## 第5步：测试用例1 - 东京旅行推荐

让我们用东京作为目的地来测试我们的并发工作流。所有三个 Agent 将同时工作，提供全面的旅行推荐。

### 代码单元格 13

异步执行：async def 定义协程，await 等待结果；普通 .py 脚本需要 asyncio.run() 入口，Notebook 支持顶层 await。

```python
async def display_travel_recommendations(destination: str):
    """Run the concurrent workflow and display formatted results."""

    display(HTML(f"""
    <div style='padding: 20px; background: #fff3e0; border-left: 4px solid #ff9800; border-radius: 8px; margin: 20px 0;'>
        <h3 style='margin: 0 0 10px 0; color: #e65100;'>Processing Travel Recommendations for {destination}</h3>
        <p style='margin: 0;'><strong>Status:</strong> Running 3 agents concurrently...</p>
    </div>
    """))

    # Run the workflow. With WorkflowBuilder(output_executors=[a1, a2, a3]),
    # outputs is a list of AgentResponse objects in the same order as output_executors.
    events = await workflow.run(f"I want comprehensive travel recommendations for {destination}")
    outputs = events.get_outputs()

    # Display results header
    display(HTML(f"""
    <div style='padding: 25px; background: linear-gradient(135deg, #4caf50 0%, #8bc34a 100%); color: white; border-radius: 12px;
                box-shadow: 0 4px 12px rgba(76,175,80,0.3); margin: 20px 0;'>
        <h2 style='margin: 0 0 20px 0;'>Complete Travel Guide for {destination}</h2>
        <p style='margin: 0; font-size: 14px; opacity: 0.9;'>Generated by 3 concurrent agents</p>
    </div>
    """))

    sections = [
        ("attractions-agent", AttractionsRecommendation, display_attractions_section),
        ("dining-agent", DiningRecommendation, display_dining_section),
        ("history-agent", HistoryRecommendation, display_history_section),
    ]

    for i, (agent_name, schema, render) in enumerate(sections):
        if i >= len(outputs):
            continue
        text = outputs[i].text
        try:
            data = schema.model_validate_json(text)
            render(data)
        except Exception as e:
            display(HTML(f"""
            <div style='padding: 15px; background: #ffcdd2; border-left: 4px solid #f44336; border-radius: 4px; margin: 10px 0;'>
                <strong>Error parsing {agent_name} response:</strong> {str(e)}
                <details><summary>Raw response</summary>{text}</details>
            </div>
            """))


def display_attractions_section(data: AttractionsRecommendation):
    """Display attractions recommendations in a formatted section."""
    attractions_list = "".join([f"<li>{attraction}</li>" for attraction in data.top_attractions])
    activities_list = "".join([f"<li>{activity}</li>" for activity in data.activities])

    display(HTML(f"""
    <div style='padding: 20px; background: #e3f2fd; border-radius: 8px; margin: 15px 0; border-left: 4px solid #2196f3;'>
        <h3 style='margin: 0 0 15px 0; color: #1976d2;'>🏛️ Tourist Attractions & Activities</h3>
        <div style='margin-bottom: 15px;'>
            <h4 style='margin: 0 0 8px 0; color: #333;'>Top Attractions:</h4>
            <ul style='margin: 0; padding-left: 20px; color: #555;'>{attractions_list}</ul>
        </div>
        <div style='margin-bottom: 15px;'>
        <h4 style='margin: 0 0 8px 0; color: #333;'>Recommended Activities:</h4>
            <ul style='margin: 0; padding-left: 20px; color: #555;'>{activities_list}</ul>
        </div>
        <div style='margin-bottom: 10px;'>
            <strong style='color: #333;'>Best Time to Visit:</strong> {data.best_time_to_visit}
        </div>
        <div>
            <strong style='color: #333;'>Transportation Tips:</strong> {data.transportation_tips}
        </div>
    </div>
    """))


def display_dining_section(data: DiningRecommendation):
    """Display dining recommendations in a formatted section."""
    dishes_list = "".join(
        [f"<li>{dish}</li>" for dish in data.must_try_dishes])
    restaurants_list = "".join(
        [f"<li>{restaurant}</li>" for restaurant in data.recommended_restaurants])
    experiences_list = "".join(
        [f"<li>{exp}</li>" for exp in data.food_experiences])

    display(HTML(f"""
    <div style='padding: 20px; background: #fff3e0; border-radius: 8px; margin: 15px 0; border-left: 4px solid #ff9800;'>
        <h3 style='margin: 0 0 15px 0; color: #f57c00;'>🍜 Food & Dining Experiences</h3>
        <div style='margin-bottom: 15px;'>
            <strong style='color: #333;'>Local Cuisine:</strong> {data.local_cuisine}
        </div>
        <div style='margin-bottom: 15px;'>
            <h4 style='margin: 0 0 8px 0; color: #333;'>Must-Try Dishes:</h4>
            <ul style='margin: 0; padding-left: 20px; color: #555;'>{dishes_list}</ul>
        </div>
        <div style='margin-bottom: 15px;'>
            <h4 style='margin: 0 0 8px 0; color: #333;'>Recommended Restaurants:</h4>
            <ul style='margin: 0; padding-left: 20px; color: #555;'>{restaurants_list}</ul>
        </div>
        <div style='margin-bottom: 15px;'>
            <h4 style='margin: 0 0 8px 0; color: #333;'>Food Experiences:</h4>
            <ul style='margin: 0; padding-left: 20px; color: #555;'>{experiences_list}</ul>
        </div>
        <div>
            <strong style='color: #333;'>Dining Etiquette:</strong> {data.dining_etiquette}
        </div>
    </div>
    """))


def display_history_section(data: HistoryRecommendation):
    """Display history recommendations in a formatted section."""
    highlights_list = "".join(
        [f"<li>{highlight}</li>" for highlight in data.cultural_highlights])
    periods_list = "".join(
        [f"<li>{period}</li>" for period in data.important_periods])
    experiences_list = "".join(
        [f"<li>{exp}</li>" for exp in data.cultural_experiences])
    facts_list = "".join(
        [f"<li>{fact}</li>" for fact in data.interesting_facts])

    display(HTML(f"""
    <div style='padding: 20px; background: #f3e5f5; border-radius: 8px; margin: 15px 0; border-left: 4px solid #9c27b0;'>
        <h3 style='margin: 0 0 15px 0; color: #7b1fa2;'>📚 History & Culture</h3>
        <div style='margin-bottom: 15px;'>
            <strong style='color: #333;'>Historical Significance:</strong> {data.historical_significance}
        </div>
        <div style='margin-bottom: 15px;'>
            <h4 style='margin: 0 0 8px 0; color: #333;'>Cultural Highlights:</h4>
            <ul style='margin: 0; padding-left: 20px; color: #555;'>{highlights_list}</ul>
        </div>
        <div style='margin-bottom: 15px;'>
            <h4 style='margin: 0 0 8px 0; color: #333;'>Important Historical Periods:</h4>
            <ul style='margin: 0; padding-left: 20px; color: #555;'>{periods_list}</ul>
        </div>
        <div style='margin-bottom: 15px;'>
            <h4 style='margin: 0 0 8px 0; color: #333;'>Cultural Experiences:</h4>
            <ul style='margin: 0; padding-left: 20px; color: #555;'>{experiences_list}</ul>
        </div>
        <div>
            <h4 style='margin: 0 0 8px 0; color: #333;'>Interesting Facts:</h4>
            <ul style='margin: 0; padding-left: 20px; color: #555;'>{facts_list}</ul>
        </div>
    </div>
    """))


# Test with Tokyo
await display_travel_recommendations("Tokyo")
```

## 第6步：测试用例2 - 巴黎旅行推荐

### 代码单元格 15

阅读提示：跟踪本单元格读取的变量、修改的状态以及返回值。按原顺序执行，确认依赖的前序变量已经存在。

```python
await display_travel_recommendations("Paris")
```

## 第7步：性能分析 - 并发 vs 顺序

让我们测量并发执行和顺序执行之间的性能差异，以展示并发编排的优势。

### 代码单元格 17

异步执行：async def 定义协程，await 等待结果；普通 .py 脚本需要 asyncio.run() 入口，Notebook 支持顶层 await。

输出观察：print 展示应用可观察结果；预存输出和现场结果可能不同，它不是模型内部思考记录。

```python
import time


async def measure_concurrent_performance(destination: str):
    """Measure concurrent execution time."""
    start_time = time.time()

    events = await workflow.run(f"I want travel recommendations for {destination}")
    outputs = events.get_outputs()

    end_time = time.time()
    return end_time - start_time, len(outputs)


async def measure_sequential_performance(destination: str):
    """Measure sequential execution time."""
    # Build a sequential workflow that chains the same agents one after another.
    sequential_workflow = (
        WorkflowBuilder(
            start_executor=attractions_agent,
            output_executors=[attractions_agent, dining_agent, history_agent],
        )
        .add_chain([attractions_agent, dining_agent, history_agent])
        .build()
    )
    start_time = time.time()

    events = await sequential_workflow.run(f"I want travel recommendations for {destination}")
    outputs = events.get_outputs()

    end_time = time.time()
    return end_time - start_time, len(outputs)


async def performance_comparison():
    """Compare concurrent vs sequential performance."""
    test_destination = "Barcelona"

    display(HTML("""
    <div style='padding: 20px; background: #fff3e0; border-left: 4px solid #ff9800; border-radius: 8px; margin: 20px 0;'>
        <h3 style='margin: 0 0 10px 0; color: #e65100;'>Performance Comparison Test</h3>
        <p style='margin: 0;'>Testing with destination: <strong>Barcelona</strong></p>
    </div>
    """))

    # Test concurrent execution
    print("Running concurrent workflow...")
    concurrent_time, concurrent_count = await measure_concurrent_performance(test_destination)

    # Test sequential execution
    print("Running sequential workflow...")
    sequential_time, sequential_count = await measure_sequential_performance(test_destination)

    # Calculate performance improvement
    improvement = ((sequential_time - concurrent_time) / sequential_time) * 100

    display(HTML(f"""
    <div style='padding: 25px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; border-radius: 12px;
                box-shadow: 0 4px 12px rgba(102,126,234,0.4); margin: 20px 0;'>
        <h2 style='margin: 0 0 20px 0;'>Performance Results</h2>
        <div style='display: grid; grid-template-columns: 1fr 1fr; gap: 20px; margin-bottom: 20px;'>
            <div style='background: rgba(255,255,255,0.1); padding: 15px; border-radius: 8px;'>
                <h4 style='margin: 0 0 10px 0;'>⚡ Concurrent Execution</h4>
                <p style='margin: 0; font-size: 24px; font-weight: bold;'>{concurrent_time:.2f}s</p>
                <p style='margin: 5px 0 0 0; font-size: 14px; opacity: 0.9;'>{concurrent_count} agent responses</p>
            </div>
            <div style='background: rgba(255,255,255,0.1); padding: 15px; border-radius: 8px;'>
                <h4 style='margin: 0 0 10px 0;'>🔄 Sequential Execution</h4>
                <p style='margin: 0; font-size: 24px; font-weight: bold;'>{sequential_time:.2f}s</p>
                <p style='margin: 5px 0 0 0; font-size: 14px; opacity: 0.9;'>{sequential_count} agent responses</p>
            </div>
        </div>
        <div style='background: rgba(255,255,255,0.15); padding: 15px; border-radius: 8px;'>
            <h4 style='margin: 0 0 10px 0;'>Performance Improvement</h4>
            <p style='margin: 0; font-size: 20px; font-weight: bold;'>{improvement:.1f}% faster</p>
            <p style='margin: 5px 0 0 0; font-size: 14px; opacity: 0.9;'>
                Saved {sequential_time - concurrent_time:.2f} seconds with concurrent execution
            </p>
        </div>
    </div>
    """))


# Run performance comparison
await performance_comparison()
```


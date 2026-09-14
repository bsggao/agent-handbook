---
title: "14 · 14-conditional-workflow"
outline: [2, 3]
---

# 14 · 14-conditional-workflow

[返回：Microsoft Agent Framework](/lessons/agent-framework.md) · [不可变原始文件](https://github.com/microsoft/ai-agents-for-beginners/blob/25b7985f3b2dc37a84f4a7387ccd3c9f0e5b1595/14-microsoft-agent-framework/code-samples/14-conditional-workflow.ipynb)

::: warning 原课程完整 Notebook · 静态阅读与代码解析
代码按英文源文件顺序保留，中文说明以同版本译本为基础。原始安装单元格可能含无版本上限的 `-U`；请跳过它们，先按[准备篇](/lessons/setup.md)固定依赖。云端服务、模型权限、网站布局和部分 SDK 接口需在你自己的环境验证。本站没有执行云端请求；第 18 章的离线验证状态单独记录在[检查报告](/guide/verification.md)。
:::

## 运行准备

Python 3.12+；在独立虚拟环境安装源仓库依赖与本页中声明的额外依赖。原文件路径：`upstream/14-microsoft-agent-framework/code-samples/14-conditional-workflow.ipynb`。以原仓库根目录为工作目录，在 Jupyter 中按顺序执行；身份与环境变量见准备篇。

```bash
cd upstream
python -m jupyterlab
```

[下载原始 Notebook](/notebooks/14-microsoft-agent-framework/code-samples/14-conditional-workflow.ipynb)。输出为上游文件保存的历史结果，不能用作本站实测证明。

### 代码单元格 1

配置加载：从本地环境读取端点与部署名；缺少变量时先修复配置，不要把密钥写进代码。

数据结构：Pydantic 模型定义字段类型；只有传入实际的 response_format 并检查解析结果，才能约束本次输出。

模型连接：project_endpoint 是项目地址，model 是实际部署名称；credential 提供访问身份。客户端创建本身不证明已经部署服务端 Agent。

```python
import asyncio
import json
import os
from typing import Annotated, Any, Never

from agent_framework import (
    AgentExecutor,
    AgentExecutorRequest,
    AgentExecutorResponse,
    Message,
    WorkflowBuilder,
    WorkflowContext,
    executor,
    tool,
)
from agent_framework.foundry import FoundryChatClient
from azure.identity import AzureCliCredential
from dotenv import load_dotenv
from IPython.display import HTML, display
from pydantic import BaseModel

print("✅ All imports successful!")
```

## 第一步：定义用于结构化输出的 Pydantic 模型

这些模型定义了 Agent 将返回的 **模式** 。使用带有 Pydantic 的 `response_format` 确保：
- ✅ 类型安全的数据提取
- ✅ 自动验证
- ✅ 避免自由文本响应的解析错误
- ✅ 基于字段的简易条件路由

### 代码单元格 3

数据结构：Pydantic 模型定义字段类型；只有传入实际的 response_format 并检查解析结果，才能约束本次输出。

输出观察：print 展示应用可观察结果；预存输出和现场结果可能不同，它不是模型内部思考记录。

```python
class BookingCheckResult(BaseModel):
    """Result from checking hotel availability at a destination."""

    destination: str
    has_availability: bool
    message: str


class AlternativeResult(BaseModel):
    """Suggested alternative destination when no rooms available."""

    alternative_destination: str
    reason: str


class BookingConfirmation(BaseModel):
    """Booking suggestion when rooms are available."""

    destination: str
    action: str
    message: str


print("✅ Pydantic models defined:")
print("   - BookingCheckResult (availability check)")
print("   - AlternativeResult (alternative suggestion)")
print("   - BookingConfirmation (booking confirmation)")
```

## 第2步：创建酒店预订工具

这个工具是 **availability_agent** 调用来检查是否有空房的。我们使用`@ai_function`装饰器来：
- 将Python函数转换为AI可调用的工具
- 为LLM自动生成JSON架构
- 处理参数验证
- 支持 Agent 自动调用

对于这个演示：
- **斯德哥尔摩、西雅图、东京、伦敦、阿姆斯特丹** → 有空房✅
- **其他所有城市** → 无空房❌

### 代码单元格 5

工具定义：类型注解和文档字符串描述输入、用途；模型产生调用请求，框架在应用进程中执行函数。检查是否需要人工批准。

输出观察：print 展示应用可观察结果；预存输出和现场结果可能不同，它不是模型内部思考记录。

```python
@tool(description="Check hotel room availability for a destination city")
def hotel_booking(destination: Annotated[str, "The destination city to check for hotel rooms"]) -> str:
    """
    Simulates checking hotel room availability.

    Returns JSON string with availability status.
    """
    display(
        HTML(f"""
        <div style='padding: 15px; background: #e3f2fd; border-left: 4px solid #2196f3; border-radius: 4px; margin: 10px 0;'>
            <strong>🔍 Tool Invoked:</strong> hotel_booking("{destination}")
        </div>
    """)
    )

    # Simulate availability check
    cities_with_rooms = ["stockholm", "seattle", "tokyo", "london", "amsterdam"]
    has_rooms = destination.lower() in cities_with_rooms

    result = {"has_availability": has_rooms, "destination": destination}

    return json.dumps(result)


print("✅ hotel_booking tool created with @tool decorator")
```

## 第3步：定义路由条件函数

这些函数检查 Agent 的响应，并确定在工作流中采用哪条路径。

 **关键模式：** 
1. 检查消息是否为 `AgentExecutorResponse`
2. 解析结构化输出（Pydantic模型）
3. 返回 `True` 或 `False` 以控制路由

工作流将在 **边缘** 上评估这些条件，以决定接下来调用哪个执行器。

### 代码单元格 7

输出观察：print 展示应用可观察结果；预存输出和现场结果可能不同，它不是模型内部思考记录。

```python
def has_availability_condition(message: Any) -> bool:
    """
    Condition for routing when hotels ARE available.
    
    Returns True if the destination has hotel rooms.
    """
    if not isinstance(message, AgentExecutorResponse):
        return True  # Default to True if unexpected type

    try:
        result = BookingCheckResult.model_validate_json(message.agent_run_response.text)

        display(
            HTML(f"""
            <div style='padding: 12px; background: #c8e6c9; border-left: 4px solid #4caf50; border-radius: 4px; margin: 10px 0;'>
                <strong>✅ Condition Check:</strong> has_availability = <strong>{result.has_availability}</strong> for {result.destination}
            </div>
        """)
        )

        return result.has_availability
    except Exception as e:
        display(
            HTML(f"""
            <div style='padding: 12px; background: #ffcdd2; border-left: 4px solid #f44336; border-radius: 4px; margin: 10px 0;'>
                <strong>⚠️  Error:</strong> {str(e)}
            </div>
        """)
        )
        return False


def no_availability_condition(message: Any) -> bool:
    """
    Condition for routing when hotels are NOT available.
    
    Returns True if the destination has no hotel rooms.
    """
    if not isinstance(message, AgentExecutorResponse):
        return False

    try:
        result = BookingCheckResult.model_validate_json(message.agent_run_response.text)

        display(
            HTML(f"""
            <div style='padding: 12px; background: #ffecb3; border-left: 4px solid #ff9800; border-radius: 4px; margin: 10px 0;'>
                <strong>❌ Condition Check:</strong> no_availability for {result.destination}
            </div>
        """)
        )

        return not result.has_availability
    except Exception as e:
        return False


print("✅ Condition functions defined:")
print("   - has_availability_condition (routes when rooms exist)")
print("   - no_availability_condition (routes when no rooms)")
```

## 第4步：创建自定义显示执行器

执行器是执行转换或副作用的工作流组件。我们使用 `@executor` 装饰器来创建一个显示最终结果的自定义执行器。

 **关键概念：** 
- `@executor(id="...")` - 将函数注册为工作流执行器
- `WorkflowContext[Never, str]` - 输入/输出的类型提示
- `ctx.yield_output(...)` - 产出最终的工作流结果

### 代码单元格 9

异步执行：async def 定义协程，await 等待结果；普通 .py 脚本需要 asyncio.run() 入口，Notebook 支持顶层 await。

输出观察：print 展示应用可观察结果；预存输出和现场结果可能不同，它不是模型内部思考记录。

```python
@executor(id="display_result")
async def display_result(response: AgentExecutorResponse, ctx: WorkflowContext[Never, str]) -> None:
    """
    Display the final result as workflow output.
    
    This executor receives the final agent response and yields it as the workflow output.
    """
    display(
        HTML("""
        <div style='padding: 15px; background: #f3e5f5; border-left: 4px solid #9c27b0; border-radius: 4px; margin: 10px 0;'>
            <strong>📤 Display Executor:</strong> Yielding workflow output
        </div>
    """)
    )

    await ctx.yield_output(response.agent_run_response.text)


print("✅ display_result executor created with @executor decorator")
```

## 第5步：加载环境变量

配置LLM客户端。此示例适用于：
- **Microsoft Foundry** / **Azure OpenAI** （Responses API —— 推荐）
- **Azure OpenAI** 
- **OpenAI** 

### 代码单元格 11

配置加载：从本地环境读取端点与部署名；缺少变量时先修复配置，不要把密钥写进代码。

模型连接：project_endpoint 是项目地址，model 是实际部署名称；credential 提供访问身份。客户端创建本身不证明已经部署服务端 Agent。

```python
# Load environment variables
load_dotenv()

# Configure the Microsoft Foundry provider with keyless authentication
provider = FoundryChatClient(
    project_endpoint=os.environ["AZURE_AI_PROJECT_ENDPOINT"],
    model=os.environ["AZURE_AI_MODEL_DEPLOYMENT_NAME"],
    credential=AzureCliCredential(),
)
```

## 第6步：创建具有结构化输出的AI Agent

我们创建了 **三个专业 Agent** ，每个都包装在`AgentExecutor`中：

1. **availability_agent** - 使用工具检查酒店可用性
2. **alternative_agent** - 建议替代城市（当无房时）
3. **booking_agent** - 鼓励预订（当有房时）

 **主要特征：** 
- `tools=[hotel_booking]` - 向 Agent 提供工具
- `response_format=PydanticModel` - 强制输出结构化JSON
- `AgentExecutor(..., id="...")` - 将 Agent 包装用于工作流

### 代码单元格 13

行为约束：instructions 引导模型，不能替代执行器的权限验证、次数限制和结果检查。

```python
# Agent 1: Check availability with tool
availability_agent = AgentExecutor(
    provider.as_agent(
        name="availability-agent",
        instructions=(
            "You are a hotel booking assistant that checks room availability. "
            "Use the hotel_booking tool to check if rooms are available at the destination. "
            "Return JSON with fields: destination (string), has_availability (bool), and message (string). "
            "The message should summarize the availability status."
        ),
        tools=[hotel_booking],
        default_options={"response_format": BookingCheckResult},
    ),
    id="availability_agent",
)

# Agent 2: Suggest alternative (when no rooms)
alternative_agent = AgentExecutor(
    provider.as_agent(
        name="alternative-agent",
        instructions=(
            "You are a helpful travel assistant. When a user cannot find hotels in their requested city, "
            "suggest an alternative nearby city that has availability. "
            "Return JSON with fields: alternative_destination (string) and reason (string). "
            "Make your suggestion sound appealing and helpful."
        ),
        default_options={"response_format": AlternativeResult},
    ),
    id="alternative_agent",
)

# Agent 3: Suggest booking (when rooms available)
booking_agent = AgentExecutor(
    provider.as_agent(
        name="booking-agent",
        instructions=(
            "You are a booking assistant. The user has found available hotel rooms. "
            "Encourage them to book by highlighting the destination's appeal. "
            "Return JSON with fields: destination (string), action (string), and message (string). "
            "The action should be 'book_now' and message should be encouraging."
        ),
        default_options={"response_format": BookingConfirmation},
    ),
    id="booking_agent",
)

display(
    HTML("""
    <div style='padding: 15px; background: #e3f2fd; border-left: 4px solid #2196f3; border-radius: 4px; margin: 10px 0;'>
        <strong>✅ Created 3 Agents:</strong>
        <ul style='margin: 10px 0 0 0;'>
            <li><strong>availability_agent</strong> - Checks availability with hotel_booking tool</li>
            <li><strong>alternative_agent</strong> - Suggests alternative cities</li>
            <li><strong>booking_agent</strong> - Encourages booking</li>
        </ul>
    </div>
""")
)
```

## 步骤 7：使用条件边构建工作流

现在我们使用 `WorkflowBuilder` 来构建带有条件路由的图：

 **工作流结构：** 
```
availability_agent (START)
        ↓
   Evaluate conditions
        ↙         ↘
[no_availability]  [has_availability]
        ↓              ↓
alternative_agent  booking_agent
        ↓              ↓
    display_result ←───┘
```

 **关键方法：** 
- `.set_start_executor(...)` - 设置入口点
- `.add_edge(from, to, condition=...)` - 添加条件边
- `.build()` - 完成工作流构建

### 代码单元格 15

阅读提示：跟踪本单元格读取的变量、修改的状态以及返回值。按原顺序执行，确认依赖的前序变量已经存在。

```python
# Build the workflow with conditional routing
workflow = (
    WorkflowBuilder(
        start_executor=availability_agent,
        output_executors=[display_result],
    )
    # NO AVAILABILITY PATH
    .add_edge(availability_agent, alternative_agent, condition=no_availability_condition)
    .add_edge(alternative_agent, display_result)
    # HAS AVAILABILITY PATH
    .add_edge(availability_agent, booking_agent, condition=has_availability_condition)
    .add_edge(booking_agent, display_result)
    .build()
)

display(
    HTML("""
    <div style='padding: 20px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; border-radius: 8px; margin: 10px 0;'>
        <h3 style='margin: 0 0 15px 0;'>✅ Workflow Built Successfully!</h3>
        <p style='margin: 0; line-height: 1.6;'>
            <strong>Conditional Routing:</strong><br>
            • If <strong>NO availability</strong> → alternative_agent → display_result<br>
            • If <strong>availability</strong> → booking_agent → display_result
        </p>
    </div>
""")
)
```

## 第8步：运行测试用例1 - 城市无可用房间（巴黎）

让我们通过请求巴黎的酒店（我们的模拟中没有房间）来测试 **无可用房间** 的路径。

### 代码单元格 17

阅读提示：跟踪本单元格读取的变量、修改的状态以及返回值。按原顺序执行，确认依赖的前序变量已经存在。

```python
display(
    HTML("""
    <div style='padding: 20px; background: #fff3e0; border-left: 4px solid #ff9800; border-radius: 8px; margin: 20px 0;'>
        <h3 style='margin: 0 0 10px 0; color: #e65100;'>🧪 TEST CASE 1: Paris (No Availability)</h3>
        <p style='margin: 0;'>Expected workflow path: availability_agent → alternative_agent → display_result</p>
    </div>
""")
)

# Create request for Paris
request_paris = AgentExecutorRequest(
    messages=[Message(role="user", contents=["I want to book a hotel in Paris"])], should_respond=True
)

# Run the workflow
events_paris = await workflow.run(request_paris)
outputs_paris = events_paris.get_outputs()

# Display results
if outputs_paris:
    result_paris = AlternativeResult.model_validate_json(outputs_paris[0])

    display(
        HTML(f"""
        <div style='padding: 25px; background: linear-gradient(135deg, #FFD700 0%, #FFA500 100%); border-radius: 12px; box-shadow: 0 4px 12px rgba(255,165,0,0.3); margin: 20px 0;'>
            <h3 style='margin: 0 0 15px 0; color: #333;'>🏆 WORKFLOW RESULT (Paris)</h3>
            <div style='background: white; padding: 20px; border-radius: 8px;'>
                <p style='margin: 0 0 10px 0; font-size: 16px;'><strong>Status:</strong> ❌ No rooms in Paris</p>
                <p style='margin: 0 0 10px 0; font-size: 16px;'><strong>Alternative Suggestion:</strong> 🏨 {result_paris.alternative_destination}</p>
                <p style='margin: 0; font-size: 14px; color: #666;'><strong>Reason:</strong> {result_paris.reason}</p>
            </div>
        </div>
    """)
    )
```

## 第9步：运行测试用例2 - 有库存的城市（斯德哥尔摩）

现在让我们通过请求斯德哥尔摩的酒店（在我们的模拟中有房间）来测试 **可用性** 路径。

### 代码单元格 19

阅读提示：跟踪本单元格读取的变量、修改的状态以及返回值。按原顺序执行，确认依赖的前序变量已经存在。

```python
display(
    HTML("""
    <div style='padding: 20px; background: #e8f5e9; border-left: 4px solid #4caf50; border-radius: 8px; margin: 20px 0;'>
        <h3 style='margin: 0 0 10px 0; color: #1b5e20;'>🧪 TEST CASE 2: Stockholm (Has Availability)</h3>
        <p style='margin: 0;'>Expected workflow path: availability_agent → booking_agent → display_result</p>
    </div>
""")
)

# Create request for Stockholm
request_stockholm = AgentExecutorRequest(
    messages=[Message(role="user", contents=["I want to book a hotel in Stockholm"])], should_respond=True
)

# Run the workflow
events_stockholm = await workflow.run(request_stockholm)
outputs_stockholm = events_stockholm.get_outputs()

# Display results
if outputs_stockholm:
    result_stockholm = BookingConfirmation.model_validate_json(outputs_stockholm[0])

    display(
        HTML(f"""
        <div style='padding: 25px; background: linear-gradient(135deg, #4caf50 0%, #8bc34a 100%); color: white; border-radius: 12px; box-shadow: 0 4px 12px rgba(76,175,80,0.3); margin: 20px 0;'>
            <h3 style='margin: 0 0 15px 0;'>🏆 WORKFLOW RESULT (Stockholm)</h3>
            <div style='background: white; color: #333; padding: 20px; border-radius: 8px;'>
                <p style='margin: 0 0 10px 0; font-size: 16px;'><strong>Status:</strong> ✅ Rooms Available!</p>
                <p style='margin: 0 0 10px 0; font-size: 16px;'><strong>Destination:</strong> 🏨 {result_stockholm.destination}</p>
                <p style='margin: 0 0 10px 0; font-size: 16px;'><strong>Action:</strong> {result_stockholm.action}</p>
                <p style='margin: 0; font-size: 14px; color: #666;'><strong>Message:</strong> {result_stockholm.message}</p>
            </div>
        </div>
    """)
    )
```

## 关键要点和下一步

### ✅ 你学到了什么：

1. **WorkflowBuilder 模式** 
   - 使用 `.set_start_executor()` 定义入口点
   - 使用 `.add_edge(from, to, condition=...)` 进行条件路由
   - 调用 `.build()` 完成工作流构建

2. **条件路由** 
   - 条件函数检查 `AgentExecutorResponse`
   - 解析结构化输出以做路由决策
   - 返回 `True` 激活边，返回 `False` 跳过边

3. **工具集成** 
   - 使用 `@ai_function` 将 Python 函数转换为 AI 工具
   - Agent 根据需要自动调用工具
   - 工具返回 Agent 可解析的 JSON

4. **结构化输出** 
   - 使用 Pydantic 模型实现类型安全的数据提取
   - 创建 Agent 时设置 `response_format=MyModel`
   - 使用 `Model.model_validate_json()` 解析响应

5. **自定义执行器** 
   - 使用 `@executor(id="...")` 创建工作流组件
   - 执行器可转换数据或执行副作用
   - 使用 `ctx.yield_output()` 生成工作流结果

### 🚀 真实世界应用：

- **旅行预订** ：检查可用性，建议备选方案，比较选项
- **客户服务** ：根据问题类型、情绪、优先级路由
- **电子商务** ：检查库存，建议备选方案，处理订单
- **内容审核** ：根据有害性评分、用户标记路由
- **审批工作流** ：根据金额、用户角色、风险等级路由
- **多阶段处理** ：根据数据质量、完整性路由

### 📚 下一步：

- 添加更复杂的条件（多重条件）
- 通过工作流状态管理实现循环
- 添加子工作流作为可重用组件
- 集成真实 API（酒店预订、库存系统）
- 添加错误处理和备用路径
- 使用内置可视化工具展示工作流


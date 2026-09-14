---
title: "14 · 14-middleware"
outline: [2, 3]
---

# 14 · 14-middleware

[返回：Microsoft Agent Framework](/lessons/agent-framework.md) · [不可变原始文件](https://github.com/microsoft/ai-agents-for-beginners/blob/25b7985f3b2dc37a84f4a7387ccd3c9f0e5b1595/14-microsoft-agent-framework/code-samples/14-middleware.ipynb)

::: warning 原课程完整 Notebook · 静态阅读与代码解析
代码按英文源文件顺序保留，中文说明以同版本译本为基础。原始安装单元格可能含无版本上限的 `-U`；请跳过它们，先按[准备篇](/lessons/setup.md)固定依赖。云端服务、模型权限、网站布局和部分 SDK 接口需在你自己的环境验证。本站没有执行云端请求；第 18 章的离线验证状态单独记录在[检查报告](/guide/verification.md)。
:::

## 运行准备

Python 3.12+；在独立虚拟环境安装源仓库依赖与本页中声明的额外依赖。原文件路径：`upstream/14-microsoft-agent-framework/code-samples/14-middleware.ipynb`。以原仓库根目录为工作目录，在 Jupyter 中按顺序执行；身份与环境变量见准备篇。

```bash
cd upstream
python -m jupyterlab
```

[下载原始 Notebook](/notebooks/14-microsoft-agent-framework/code-samples/14-middleware.ipynb)。输出为上游文件保存的历史结果，不能用作本站实测证明。

## 使用优先会员中间件的酒店预订

本笔记本演示了使用 Microsoft Agent Framework 的 **函数式中间件** 。我们基于条件工作流示例，添加了一个中间件层，为优先会员提供特殊权限。

## 你将学习：
1. **函数式中间件** ：拦截并修改函数结果
2. **上下文访问** ：执行后读取并修改 `context.result`
3. **业务逻辑实现** ：优先会员福利
4. **结果覆盖** ：根据用户状态改变函数结果
5. **相同工作流，不同结果** ：中间件驱动的行为变化

## 带中间件的工作流架构：

```
User Input: "I want to book a hotel in Paris"
                    ↓
        [availability_agent]
        - Calls hotel_booking tool
        - 🌟 priority_check middleware intercepts
        - Checks user membership status
        - IF priority + no rooms → Override to available!
        - Returns BookingCheckResult
                    ↓
        Conditional Routing
           /                    \
    [has_availability]    [no_availability]
          ↓                      ↓
    [booking_agent]        [alternative_agent]
    (Priority override!)   (Regular users)
          ↓                      ↓
       [display_result executor]
```

## 与条件工作流的主要区别：

 **无中间件** （14-conditional-workflow.ipynb）：
- 巴黎无房间 → 路由到 alternative_agent

 **有中间件** （本笔记本）：
- 普通用户 + 巴黎 → 无房间 → 路由到 alternative_agent
- 优先用户 + 巴黎 → 🌟 中间件覆盖！→ 有房间 → 路由到 booking_agent

## 先决条件：
- 已安装 Microsoft Agent Framework
- 了解条件工作流（参见 14-conditional-workflow.ipynb）
- GitHub Token或 OpenAI API 密钥
- 基础的中间件模式理解

### 代码单元格 2

配置加载：从本地环境读取端点与部署名；缺少变量时先修复配置，不要把密钥写进代码。

数据结构：Pydantic 模型定义字段类型；只有传入实际的 response_format 并检查解析结果，才能约束本次输出。

模型连接：project_endpoint 是项目地址，model 是实际部署名称；credential 提供访问身份。客户端创建本身不证明已经部署服务端 Agent。

```python
import asyncio
import json
import os
from collections.abc import Awaitable, Callable
from typing import Annotated, Any, Never

from agent_framework import (
    AgentExecutor,
    AgentExecutorRequest,
    AgentExecutorResponse,
    FunctionInvocationContext,
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

## 第一步：为结构化输出定义 Pydantic 模型

这些模型定义了 Agent 将返回的 **模式** 。我们添加了一个 `priority_override` 字段来跟踪中间件何时修改可用性结果。

### 代码单元格 4

数据结构：Pydantic 模型定义字段类型；只有传入实际的 response_format 并检查解析结果，才能约束本次输出。

输出观察：print 展示应用可观察结果；预存输出和现场结果可能不同，它不是模型内部思考记录。

```python
class BookingCheckResult(BaseModel):
    """Result from checking hotel availability at a destination."""

    destination: str
    has_availability: bool
    message: str
    # Tracks if middleware overrode the result. The Azure structured-output
    # contract requires every property to be in the JSON schema's `required`
    # array, so we cannot give this a default value the way the original
    # notebook did.
    priority_override: bool


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
print("   - BookingCheckResult (availability check with priority_override)")
print("   - AlternativeResult (alternative suggestion)")
print("   - BookingConfirmation (booking confirmation)")
```

## 第2步：定义优先会员数据库

在本演示中，我们将模拟一个优先会员数据库。在生产环境中，这将查询真实的数据库或API。

 **优先会员：** 
- `alice@example.com` - VIP会员
- `bob@example.com` - 高级会员  
- `priority_user` - 测试账户

### 代码单元格 6

输出观察：print 展示应用可观察结果；预存输出和现场结果可能不同，它不是模型内部思考记录。

```python
# Simulated priority members database
PRIORITY_MEMBERS = {
    "alice@example.com",
    "bob@example.com",
    "priority_user",
}

# Global variable to track current user (in real app, use proper session management)
current_user_id = "regular_user"  # Default: regular user


def set_user(user_id: str):
    """Set the current user for the session."""
    global current_user_id
    current_user_id = user_id
    is_priority = user_id in PRIORITY_MEMBERS
    status = "🌟 PRIORITY MEMBER" if is_priority else "👤 Regular User"

    display(
        HTML(f"""
        <div style='padding: 15px; background: {"linear-gradient(135deg, #FFD700 0%, #FFA500 100%)" if is_priority else "#e3f2fd"}; 
                    border-left: 4px solid {"#FF6B35" if is_priority else "#2196f3"}; border-radius: 4px; margin: 10px 0;'>
            <strong>👤 Current User Set:</strong> {user_id}<br>
            <strong>Status:</strong> {status}
        </div>
    """)
    )


print("✅ Priority members database created")
print(f"   Priority members: {len(PRIORITY_MEMBERS)} users")
```

## 第3步：创建酒店预订工具

和条件工作流相同，但现在它将被中间件拦截！

### 代码单元格 8

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

## 第4步：🌟 创建优先级检查中间件（关键功能！）

这是本笔记本的 **核心功能** 。该中间件：

1. **拦截** hotel_booking 函数调用
2. **正常执行** 该函数，通过调用 `next(context)`
3. **检查** `context.result` 中的结果
4. 如果用户有优先权且无可用房间， **覆盖** 结果
5. **将修改后的结果返回** 给 Agent

 **关键模式：** 
```python
async def my_middleware(context, next):
    await next(context)  # 执行函数
    # 现在 context.result 包含了函数的输出
    if some_condition:
        context.result = new_value  # 覆盖！
```

### 代码单元格 10

异步执行：async def 定义协程，await 等待结果；普通 .py 脚本需要 asyncio.run() 入口，Notebook 支持顶层 await。

输出观察：print 展示应用可观察结果；预存输出和现场结果可能不同，它不是模型内部思考记录。

```python
async def priority_check_middleware(
    context: FunctionInvocationContext,
    next: Callable[[FunctionInvocationContext], Awaitable[None]],
) -> None:
    """
    Function middleware that overrides hotel_booking results for priority members.
    
    Workflow:
    1. Let the function execute normally
    2. Check if user is a priority member
    3. If priority + no availability → Override to make rooms available!
    4. Agent will then route to booking path instead of alternative path
    """
    function_name = context.function.name

    display(
        HTML(f"""
        <div style='padding: 12px; background: #fff3e0; border-left: 4px solid #ff9800; border-radius: 4px; margin: 10px 0;'>
            <strong>🔄 Middleware:</strong> Intercepting {function_name}...
        </div>
    """)
    )

    # Execute the original function
    await next(context)

    # Now inspect and potentially modify the result
    if context.result and function_name == "hotel_booking":
        result_data = json.loads(context.result)
        destination = result_data.get("destination", "")
        has_availability = result_data.get("has_availability", False)

        # Check if user is priority member
        is_priority = current_user_id in PRIORITY_MEMBERS

        # Override logic: Priority member + no availability → Make available!
        if is_priority and not has_availability:
            display(
                HTML(f"""
                <div style='padding: 20px; background: linear-gradient(135deg, #FFD700 0%, #FFA500 100%); 
                            border-radius: 8px; margin: 10px 0; box-shadow: 0 4px 12px rgba(255,165,0,0.4);'>
                    <h3 style='margin: 0 0 10px 0; color: #333;'>🌟 PRIORITY OVERRIDE ACTIVATED! 🌟</h3>
                    <p style='margin: 0; color: #555; line-height: 1.6;'>
                        <strong>User:</strong> {current_user_id}<br>
                        <strong>Status:</strong> VIP Priority Member<br>
                        <strong>Action:</strong> Overriding "No Availability" for {destination}<br>
                        <strong>Result:</strong> ✅ Rooms now available for priority booking!
                    </p>
                </div>
            """)
            )

            # Override the result!
            result_data["has_availability"] = True
            result_data["priority_override"] = True
            context.result = json.dumps(result_data)

        elif not has_availability:
            display(
                HTML(f"""
                <div style='padding: 12px; background: #ffebee; border-left: 4px solid #f44336; border-radius: 4px; margin: 10px 0;'>
                    <strong>ℹ️ Middleware:</strong> No priority override (user: {current_user_id})
                </div>
            """)
            )


print("✅ priority_check_middleware created")
print("   - Intercepts hotel_booking function")
print("   - Overrides availability for priority members")
```

## 第5步：定义用于路由的条件函数

与条件工作流相同的条件函数——它们检查结构化输出以确定路由。

### 代码单元格 12

输出观察：print 展示应用可观察结果；预存输出和现场结果可能不同，它不是模型内部思考记录。

```python
def has_availability_condition(message: Any) -> bool:
    """Condition for routing when hotels ARE available (including priority overrides!)."""
    if not isinstance(message, AgentExecutorResponse):
        return True

    try:
        result = BookingCheckResult.model_validate_json(message.agent_run_response.text)

        # Check if this was a priority override
        override_indicator = " 🌟" if result.priority_override else ""

        display(
            HTML(f"""
            <div style='padding: 12px; background: #c8e6c9; border-left: 4px solid #4caf50; border-radius: 4px; margin: 10px 0;'>
                <strong>✅ Condition Check:</strong> has_availability = <strong>{result.has_availability}</strong> for {result.destination}{override_indicator}
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
    """Condition for routing when hotels are NOT available."""
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
    except Exception:
        return False


print("✅ Condition functions defined")
```

## 第6步：创建自定义显示执行器

与之前相同的执行器——显示最终的工作流输出。

### 代码单元格 14

异步执行：async def 定义协程，await 等待结果；普通 .py 脚本需要 asyncio.run() 入口，Notebook 支持顶层 await。

输出观察：print 展示应用可观察结果；预存输出和现场结果可能不同，它不是模型内部思考记录。

```python
@executor(id="display_result")
async def display_result(response: AgentExecutorResponse, ctx: WorkflowContext[Never, str]) -> None:
    """Display the final result as workflow output."""
    display(
        HTML("""
        <div style='padding: 15px; background: #f3e5f5; border-left: 4px solid #9c27b0; border-radius: 4px; margin: 10px 0;'>
            <strong>📤 Display Executor:</strong> Yielding workflow output
        </div>
    """)
    )

    await ctx.yield_output(response.agent_run_response.text)


print("✅ display_result executor created")
```

## 第7步：加载环境变量

配置LLM客户端（Microsoft Foundry / Azure OpenAI）。

### 代码单元格 16

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

## 第8步：使用中间件创建AI Agent

 **关键区别：** 创建availability_agent时，我们传入了`middleware`参数！

这就是我们如何将priority_check_middleware注入到 Agent 的函数调用流程中的方式。

### 代码单元格 18

行为约束：instructions 引导模型，不能替代执行器的权限验证、次数限制和结果检查。

```python
# Agent 1: Check availability with tool + middleware
availability_agent = AgentExecutor(
    provider.as_agent(
        name="availability-agent",
        instructions=(
            "You are a hotel booking assistant that checks room availability. "
            "Use the hotel_booking tool to check if rooms are available at the destination. "
            "Return JSON with fields: destination (string), has_availability (bool), message (string), "
            "and priority_override (bool, true if priority member got special access). "
            "The message should summarize the availability status and mention if priority override occurred."
        ),
        tools=[hotel_booking],
        default_options={"response_format": BookingCheckResult},
        middleware=[priority_check_middleware],  # 🌟 MIDDLEWARE INJECTION!
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
            "If priority_override is true in the input, mention that they received priority member access. "
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
            <li><strong>availability_agent</strong> - WITH priority_check_middleware 🌟</li>
            <li><strong>alternative_agent</strong> - Suggests alternative cities</li>
            <li><strong>booking_agent</strong> - Encourages booking</li>
        </ul>
    </div>
""")
)
```

## 第9步：构建工作流

与之前相同的工作流结构 - 基于可用性的条件路由。

### 代码单元格 20

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
    # HAS AVAILABILITY PATH (can be triggered by middleware override!)
    .add_edge(availability_agent, booking_agent, condition=has_availability_condition)
    .add_edge(booking_agent, display_result)
    .build()
)

display(
    HTML("""
    <div style='padding: 20px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; border-radius: 8px; margin: 10px 0;'>
        <h3 style='margin: 0 0 15px 0;'>✅ Workflow Built Successfully!</h3>
        <p style='margin: 0; line-height: 1.6;'>
            <strong>Conditional Routing (Middleware-Aware):</strong><br>
            • If <strong>NO availability</strong> → alternative_agent → display_result<br>
            • If <strong>availability</strong> (or 🌟 <strong>priority override</strong>) → booking_agent → display_result
        </p>
    </div>
""")
)
```

## 第10步：测试用例1 - 巴黎的普通用户（无覆盖）

一个普通用户尝试预订巴黎 → 无可用房间 → 路由到alternative_agent

### 代码单元格 22

阅读提示：跟踪本单元格读取的变量、修改的状态以及返回值。按原顺序执行，确认依赖的前序变量已经存在。

```python
# Set as regular user
set_user("regular_user")

display(
    HTML("""
    <div style='padding: 20px; background: #fff3e0; border-left: 4px solid #ff9800; border-radius: 8px; margin: 20px 0;'>
        <h3 style='margin: 0 0 10px 0; color: #e65100;'>🧪 TEST CASE 1: Regular User + Paris</h3>
        <p style='margin: 0;'><strong>Expected:</strong> No rooms → No middleware override → Alternative suggestion</p>
    </div>
""")
)

# Create request
request_regular = AgentExecutorRequest(
    messages=[Message(role="user", contents=["I want to book a hotel in Paris"])], should_respond=True
)

# Run workflow
events_regular = await workflow.run(request_regular)
outputs_regular = events_regular.get_outputs()

# Display results
if outputs_regular:
    result_regular = AlternativeResult.model_validate_json(outputs_regular[0])

    display(
        HTML(f"""
        <div style='padding: 25px; background: #fff; border: 2px solid #ff9800; border-radius: 12px; margin: 20px 0;'>
            <h3 style='margin: 0 0 15px 0; color: #e65100;'>📊 RESULT (Regular User)</h3>
            <div style='background: #fff3e0; padding: 20px; border-radius: 8px;'>
                <p style='margin: 0 0 10px 0;'><strong>Status:</strong> ❌ No rooms in Paris</p>
                <p style='margin: 0 0 10px 0;'><strong>Middleware:</strong> No priority override (regular user)</p>
                <p style='margin: 0 0 10px 0;'><strong>Alternative:</strong> 🏨 {result_regular.alternative_destination}</p>
                <p style='margin: 0;'><strong>Reason:</strong> {result_regular.reason}</p>
            </div>
        </div>
    """)
    )
```

## 第11步：测试用例2 - 🌟 巴黎的优先用户（带覆盖！）

一位优先会员尝试预订巴黎 → 起初无空房 → 🌟 中间件进行覆盖！ → 路由到 booking_agent

 **这是中间件强大功能的关键演示！** 

### 代码单元格 24

阅读提示：跟踪本单元格读取的变量、修改的状态以及返回值。按原顺序执行，确认依赖的前序变量已经存在。

```python
# Set as priority user
set_user("priority_user")

display(
    HTML("""
    <div style='padding: 20px; background: linear-gradient(135deg, #FFD700 0%, #FFA500 100%); border-radius: 8px; margin: 20px 0;'>
        <h3 style='margin: 0 0 10px 0; color: #333;'>🧪 TEST CASE 2: 🌟 Priority User + Paris</h3>
        <p style='margin: 0; color: #555;'><strong>Expected:</strong> No rooms → 🌟 MIDDLEWARE OVERRIDE → Rooms available → Booking suggestion!</p>
    </div>
""")
)

# Create request
request_priority = AgentExecutorRequest(
    messages=[Message(role="user", contents=["I want to book a hotel in Paris"])], should_respond=True
)

# Run workflow
events_priority = await workflow.run(request_priority)
outputs_priority = events_priority.get_outputs()

# Display results
if outputs_priority:
    result_priority = BookingConfirmation.model_validate_json(outputs_priority[0])

    display(
        HTML(f"""
        <div style='padding: 25px; background: linear-gradient(135deg, #FFD700 0%, #FFA500 100%); border-radius: 12px;
                    box-shadow: 0 8px 16px rgba(255,165,0,0.4); margin: 20px 0;'>
            <h3 style='margin: 0 0 15px 0; color: #333;'>🏆 RESULT (Priority Member) 🌟</h3>
            <div style='background: white; padding: 20px; border-radius: 8px;'>
                <p style='margin: 0 0 10px 0; font-size: 16px;'><strong>Status:</strong> ✅ Rooms Available (Priority Override!)</p>
                <p style='margin: 0 0 10px 0; font-size: 16px;'><strong>Middleware:</strong> 🌟 OVERRIDE ACTIVATED!</p>
                <p style='margin: 0 0 10px 0; font-size: 16px;'><strong>Destination:</strong> 🏨 {result_priority.destination}</p>
                <p style='margin: 0 0 10px 0; font-size: 16px;'><strong>Action:</strong> {result_priority.action}</p>
                <p style='margin: 0; font-size: 14px; color: #666;'><strong>Message:</strong> {result_priority.message}</p>
                <div style='margin-top: 15px; padding: 15px; background: #fff3cd; border-radius: 6px; border-left: 4px solid #FF6B35;'>
                    <strong>💡 What Just Happened:</strong><br>
                    1. hotel_booking tool returned "no availability"<br>
                    2. priority_check_middleware intercepted the result<br>
                    3. Middleware checked user status: priority_user ✅<br>
                    4. Middleware OVERRODE the result to "available"<br>
                    5. Workflow routed to booking_agent instead of alternative_agent!
                </div>
            </div>
        </div>
    """)
    )
```

## 第12步：测试用例3 - 斯德哥尔摩优先用户（已存在）

优先用户尝试斯德哥尔摩 → 房间有空 → 不需要覆盖 → 路由到booking_agent

这表明中间件仅在需要时才会起作用！

### 代码单元格 26

阅读提示：跟踪本单元格读取的变量、修改的状态以及返回值。按原顺序执行，确认依赖的前序变量已经存在。

```python
# Priority user is still set from previous test

display(
    HTML("""
    <div style='padding: 20px; background: #e8f5e9; border-left: 4px solid #4caf50; border-radius: 8px; margin: 20px 0;'>
        <h3 style='margin: 0 0 10px 0; color: #1b5e20;'>🧪 TEST CASE 3: Priority User + Stockholm</h3>
        <p style='margin: 0;'><strong>Expected:</strong> Rooms available → No override needed → Booking suggestion</p>
    </div>
""")
)

# Create request
request_stockholm = AgentExecutorRequest(
    messages=[Message(role="user", contents=["I want to book a hotel in Stockholm"])], should_respond=True
)

# Run workflow
events_stockholm = await workflow.run(request_stockholm)
outputs_stockholm = events_stockholm.get_outputs()

# Display results
if outputs_stockholm:
    result_stockholm = BookingConfirmation.model_validate_json(outputs_stockholm[0])

    display(
        HTML(f"""
        <div style='padding: 25px; background: linear-gradient(135deg, #4caf50 0%, #8bc34a 100%); color: white; border-radius: 12px;
                    box-shadow: 0 4px 12px rgba(76,175,80,0.3); margin: 20px 0;'>
            <h3 style='margin: 0 0 15px 0;'>🏆 RESULT (Priority User - No Override Needed)</h3>
            <div style='background: white; color: #333; padding: 20px; border-radius: 8px;'>
                <p style='margin: 0 0 10px 0; font-size: 16px;'><strong>Status:</strong> ✅ Rooms Available (Natural)</p>
                <p style='margin: 0 0 10px 0; font-size: 16px;'><strong>Middleware:</strong> No override needed</p>
                <p style='margin: 0 0 10px 0; font-size: 16px;'><strong>Destination:</strong> 🏨 {result_stockholm.destination}</p>
                <p style='margin: 0 0 10px 0; font-size: 16px;'><strong>Action:</strong> {result_stockholm.action}</p>
                <p style='margin: 0; font-size: 14px; color: #666;'><strong>Message:</strong> {result_stockholm.message}</p>
                <div style='margin-top: 15px; padding: 15px; background: #e8f5e9; border-radius: 6px; border-left: 4px solid #4caf50;'>
                    <strong>💡 Middleware Behavior:</strong><br>
                    • hotel_booking returned "available" naturally<br>
                    • Middleware saw available = true → No override needed<br>
                    • Workflow proceeded normally to booking_agent
                </div>
            </div>
        </div>
    """)
    )
```

## 关键要点和中间件概念

### ✅ 你学到了什么：

#### **1. 基于函数的中间件模式** 

中间件通过一个简单的异步函数拦截函数调用：

```python
async def my_middleware(
    context: FunctionInvocationContext,
    next: Callable,
) -> None:
    # 在函数执行前
    print("Intercepting...")
    
    # 执行函数
    await next(context)
    
    # 函数执行后 - 检查结果
    if context.result:
        # 如有需要，修改结果
        context.result = modified_value
```

#### **2. 访问上下文和结果覆盖** 

- `context.function` - 访问被调用的函数
- `context.arguments` - 读取函数参数
- `context.kwargs` - 访问额外参数
- `await next(context)` - 执行函数
- `context.result` - 读取/修改函数的输出

#### **3. 业务逻辑实现** 

我们的中间件实现了优先会员权益：
- **普通用户** ：无修改，标准流程
- **优先用户** ：覆盖“无空余” → “有空余”
- **条件逻辑** ：仅在必要时覆盖

#### **4. 相同流程，不同结果** 

中间件的力量：
- ✅ 流程结构无变化
- ✅ 工具函数无变化
- ✅ 条件路由逻辑无变化
- ✅ 仅中间件不同 → 行为迥异！

### 🚀 现实世界应用：

1. **VIP/高级特性** 
   - 为高级用户覆盖速率限制
   - 提供资源优先访问
   - 动态解锁高级功能

2. **A/B 测试** 
   - 导航用户至不同实现
   - 对特定用户测试新功能
   - 逐步推送功能

3. **安全与合规** 
   - 审计函数调用
   - 阻止敏感操作
   - 强制执行业务规则

4. **性能优化** 
   - 为特定用户缓存结果
   - 尽可能跳过昂贵操作
   - 动态资源分配

5. **错误处理与重试** 
   - 优雅捕获和处理错误
   - 实现重试逻辑
   - 回退到替代实现

6. **日志与监控** 
   - 跟踪函数执行时间
   - 记录参数和结果
   - 监控使用模式

### 🔑 与装饰器的主要区别：

| 特性 | 装饰器 | 中间件 |
|---------|-----------|------------|
| **作用范围** | 单个函数 | Agent 中所有函数 |
| **灵活性** | 定义时固定 | 运行时动态 |
| **上下文** | 有限 | 完整 Agent 上下文 |
| **组合** | 多个装饰器 | 中间件管线 |
| **Agent 感知** | 否 | 是（访问 Agent 状态） |

### 📚 何时使用中间件：

✅ **使用中间件当：** 
- 你需要根据用户/会话状态修改行为
- 你想将逻辑应用于多个函数
- 你需要访问 Agent 级上下文
- 你在实现横切关注点（日志、授权等）

❌ **不使用中间件当：** 
- 简单输入验证（使用 Pydantic）
- 函数特定逻辑（保留在函数内部）
- 一次性修改（直接改函数）

### 🎓 高级模式：

```python
# 多个中间件（执行顺序很重要！）
middleware=[
    logging_middleware,      # 先记录日志
    auth_middleware,         # 然后检查授权
    cache_middleware,        # 然后检查缓存
    rate_limit_middleware,   # 然后进行速率限制
    priority_check_middleware  # 最后优先级检查
]

# 条件中间件执行
async def conditional_middleware(context, next):
    if should_execute(context):
        await next(context)
        # 修改结果
    else:
        # 完全跳过执行
        context.result = cached_value
```

### 🔗 相关概念：

- **Agent 中间件** ：拦截 agent.run() 调用
- **函数中间件** ：拦截工具函数调用（我们用的！）
- **中间件管线** ：依次执行的一连串中间件
- **上下文传播** ：在中间件链上传递状态


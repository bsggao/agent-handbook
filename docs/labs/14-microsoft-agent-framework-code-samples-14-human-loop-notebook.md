---
title: "14 · 14-human-loop"
outline: [2, 3]
---

# 14 · 14-human-loop

[返回：Microsoft Agent Framework](/lessons/agent-framework.md) · [不可变原始文件](https://github.com/microsoft/ai-agents-for-beginners/blob/25b7985f3b2dc37a84f4a7387ccd3c9f0e5b1595/14-microsoft-agent-framework/code-samples/14-human-loop.ipynb)

::: warning 原课程完整 Notebook · 静态阅读与代码解析
代码按英文源文件顺序保留，中文说明以同版本译本为基础。原始安装单元格可能含无版本上限的 `-U`；请跳过它们，先按[准备篇](/lessons/setup.md)固定依赖。云端服务、模型权限、网站布局和部分 SDK 接口需在你自己的环境验证。本站没有执行云端请求；第 18 章的离线验证状态单独记录在[检查报告](/guide/verification.md)。
:::

## 运行准备

Python 3.12+；在独立虚拟环境安装源仓库依赖与本页中声明的额外依赖。原文件路径：`upstream/14-microsoft-agent-framework/code-samples/14-human-loop.ipynb`。以原仓库根目录为工作目录，在 Jupyter 中按顺序执行；身份与环境变量见准备篇。

```bash
cd upstream
python -m jupyterlab
```

[下载原始 Notebook](/notebooks/14-microsoft-agent-framework/code-samples/14-human-loop.ipynb)。输出为上游文件保存的历史结果，不能用作本站实测证明。

## 使用 Microsoft Agent Framework 的人机循环工作流

## 🎯 学习目标

在本笔记本中，你将学习如何使用 Microsoft Agent Framework 的 `RequestInfoExecutor` 实现 **人机循环** 工作流。这一强大模式允许你在 AI 工作流中暂停以收集人工输入，使你的 Agent 具备交互性，并让人类掌控关键决策。

## 🔄 什么是人机循环？

 **人机循环 (HITL)** 是一种设计模式，AI Agent 在继续执行前暂停，向人类请求输入。其关键作用包括：

- ✅ **关键决策** - 在执行重要操作前获取人工批准
- ✅ **模糊情况** - 当 AI 不确定时让人类澄清
- ✅ **用户偏好** - 让用户在多个选项间选择
- ✅ **合规与安全** - 确保受监管操作有人类监督
- ✅ **交互体验** - 构建响应用户输入的会话 Agent

## 🏗️ Microsoft Agent Framework 中的实现

该框架提供了 HITL 的三个关键组件：

1. **`RequestInfoExecutor`** - 一个特殊执行器，可暂停工作流并触发 `RequestInfoEvent`
2. **`RequestInfoMessage`** - 发送给人类的类型化请求载荷基类
3. **`RequestResponse`** - 使用 `request_id` 将人类回复与原请求关联起来

 **工作流模式：** 
```
Agent detects need for input
    ↓
Sends message to RequestInfoExecutor
    ↓
Workflow pauses & emits RequestInfoEvent
    ↓
Application collects human input (console, UI, etc.)
    ↓
Application sends RequestResponse via send_responses_streaming()
    ↓
Workflow resumes with human input
```

## 🏨 示例：酒店预订与用户确认

我们将在条件工作流的基础上，在建议替代目的地 **之前** 添加人工确认：

1. 用户请求一个目的地（例如“巴黎”）
2. `availability_agent` 检查是否有空房
3. **如果无空房** → `confirmation_agent` 询问“你想查看替代选项吗？”
4. 使用 `RequestInfoExecutor` **暂停工作流** 
5. **人类通过控制台输入** “是”或“否”
6. `decision_manager` 根据回复路由：
   - **是** → 显示替代目的地
   - **否** → 取消预订请求
7. 显示最终结果

此示例展示了如何让用户控制 Agent 建议！

---

让我们开始吧！🚀

## 第1步：导入所需库

我们导入标准的 Agent 框架组件以及 **人机交互特定的类** ：
- `RequestInfoExecutor` - 用于暂停工作流以等待人工输入的执行器
- `RequestInfoEvent` - 在请求人工输入时发出的事件
- `RequestInfoMessage` - 类型化请求负载的基类
- `RequestResponse` - 将人工响应与请求相关联
- `WorkflowOutputEvent` - 用于检测工作流输出的事件

### 代码单元格 3

配置加载：从本地环境读取端点与部署名；缺少变量时先修复配置，不要把密钥写进代码。

数据结构：Pydantic 模型定义字段类型；只有传入实际的 response_format 并检查解析结果，才能约束本次输出。

模型连接：project_endpoint 是项目地址，model 是实际部署名称；credential 提供访问身份。客户端创建本身不证明已经部署服务端 Agent。

```python
import asyncio
import json
import os
from dataclasses import dataclass
from typing import Annotated, Any, Never

from agent_framework import (
    AgentExecutor,
    AgentExecutorRequest,
    AgentExecutorResponse,
    Message,
    Executor,
    WorkflowBuilder,
    WorkflowContext,
    WorkflowRunState,          # Enum of workflow run states
    executor,
    handler,
    response_handler,          # NEW: decorator for the human-feedback response handler
    tool,
)

from agent_framework.foundry import FoundryChatClient
from azure.identity import AzureCliCredential
from dotenv import load_dotenv
from IPython.display import HTML, display
from pydantic import BaseModel

print("✅ All imports successful!")
print("🔄 Human-in-the-loop uses ctx.request_info() + @response_handler")
```

::: details 原文件保存的输出（不是本项目实测）

```text
✅ All imports successful!
🔄 Human-in-the-loop components loaded: RequestInfoExecutor, RequestInfoEvent, RequestResponse
```

:::

## 第2步：为结构化输出定义Pydantic模型

这些模型定义了 Agent 将返回的 **架构** 。我们保留条件工作流中的所有模型，并添加：

 **针对人类参与的新内容：** 
- `HumanFeedbackRequest` - `RequestInfoMessage`的子类，定义发送给人类的请求负载
  - 包含`prompt`（要询问的问题）和`destination`（关于不可用城市的上下文）

### 代码单元格 5

数据结构：Pydantic 模型定义字段类型；只有传入实际的 response_format 并检查解析结果，才能约束本次输出。

输出观察：print 展示应用可观察结果；预存输出和现场结果可能不同，它不是模型内部思考记录。

```python
# Existing models from conditional workflow
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


# NEW: Pydantic model for agent's response format
class ConfirmationQuestion(BaseModel):
    """
    Pydantic model used by confirmation_agent's response_format.
    This is what the agent will output as JSON.
    """
    question: str  # The question to ask the user
    destination: str  # The unavailable destination for context


# NEW: Plain dataclass payload for ctx.request_info()
@dataclass
class HumanFeedbackRequest:
    """
    Request sent to RequestInfoExecutor asking if user wants alternatives.
    
    MUST be a dataclass subclassing RequestInfoMessage for type compatibility.
    This is what gets sent to the RequestInfoExecutor.
    """
    prompt: str = ""  # The question to ask the user
    destination: str = ""  # The unavailable destination for context


print("✅ Pydantic models defined:")
print("   - BookingCheckResult (availability check)")
print("   - AlternativeResult (alternative suggestion)")
print("   - BookingConfirmation (booking confirmation)")
print("   - ConfirmationQuestion (agent response format) 🆕")
print("   - HumanFeedbackRequest (RequestInfoMessage for HITL) 🆕")
```

::: details 原文件保存的输出（不是本项目实测）

```text
✅ Pydantic models defined:
   - BookingCheckResult (availability check)
   - AlternativeResult (alternative suggestion)
   - BookingConfirmation (booking confirmation)
   - ConfirmationQuestion (agent response format) 🆕
   - HumanFeedbackRequest (RequestInfoMessage for HITL) 🆕
```

:::

## 第3步：创建酒店预订工具

来自条件工作流的相同工具 - 检查目的地是否有可用房间。

### 代码单元格 7

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

::: details 原文件保存的输出（不是本项目实测）

```text
✅ hotel_booking tool created with @ai_function decorator
```

:::

## 第4步：定义路由的条件函数

我们需要 **四个条件函数** 来实现我们的人工干预工作流：

 **来自条件工作流：** 
1. `has_availability_condition` - 当酒店有空时路由
2. `no_availability_condition` - 当酒店没有空时路由

 **新增用于人工干预：** 
3. `user_wants_alternatives_condition` - 当用户对替代方案回答“是”时路由
4. `user_declines_alternatives_condition` - 当用户对替代方案回答“否”时路由

### 代码单元格 9

输出观察：print 展示应用可观察结果；预存输出和现场结果可能不同，它不是模型内部思考记录。

```python
# Existing condition functions from conditional workflow
def has_availability_condition(message: Any) -> bool:
    """Condition for routing when hotels ARE available."""
    if not isinstance(message, AgentExecutorResponse):
        return True

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
        display(HTML(f"""<div style='padding: 12px; background: #ffcdd2; border-left: 4px solid #f44336; border-radius: 4px; margin: 10px 0;'><strong>⚠️  Error:</strong> {str(e)}</div>"""))
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
    except Exception as e:
        return False


# NEW: Condition functions for human-in-the-loop routing
def user_wants_alternatives_condition(message: Any) -> bool:
    """
    Condition for routing when user WANTS to see alternatives.
    
    Checks the AgentExecutorRequest sent by decision_manager.
    """
    # Check if it's an AgentExecutorRequest (what decision_manager sends)
    if isinstance(message, AgentExecutorRequest):
        # Check the message text to determine user's choice
        if message.messages and len(message.messages) > 0:
            msg_text = message.messages[0].text.lower()
            wants_alternatives = "wants to see alternative" in msg_text or "want to see alternative" in msg_text
            
            display(
                HTML(f"""
                <div style='padding: 12px; background: #e1f5fe; border-left: 4px solid #0288d1; border-radius: 4px; margin: 10px 0;'>
                    <strong>🔍 User Decision:</strong> User wants alternatives = <strong>{wants_alternatives}</strong>
                </div>
            """)
            )
            
            return wants_alternatives
    
    return False
def user_declines_alternatives_condition(message: Any) -> bool:
    """
    Condition for routing when user DECLINES alternatives.
    
    Checks the AgentExecutorRequest sent by decision_manager.
    """
    # Check if it's an AgentExecutorRequest (what decision_manager sends)
    if isinstance(message, AgentExecutorRequest):
        # Check the message text to determine user's choice
        if message.messages and len(message.messages) > 0:
            msg_text = message.messages[0].text.lower()
            declined = "declined" in msg_text or "has declined" in msg_text
            
            display(
                HTML(f"""
                <div style='padding: 12px; background: #fce4ec; border-left: 4px solid #c2185b; border-radius: 4px; margin: 10px 0;'>
                    <strong>🚫 User Decision:</strong> User declined alternatives = <strong>{declined}</strong>
                </div>
            """)
            )
            
            return declined
    
    return False
print("✅ Condition functions defined:")
print("   - has_availability_condition (routes when rooms exist)")
print("   - no_availability_condition (routes when no rooms)")
print("   - user_wants_alternatives_condition (routes when user says yes) 🆕")
print("   - user_declines_alternatives_condition (routes when user says no) 🆕")
```

::: details 原文件保存的输出（不是本项目实测）

```text
✅ Condition functions defined:
   - has_availability_condition (routes when rooms exist)
   - no_availability_condition (routes when no rooms)
   - user_wants_alternatives_condition (routes when user says yes) 🆕
   - user_declines_alternatives_condition (routes when user says no) 🆕
```

:::

## 第5步：创建决策管理执行器

这是 **人机交互模式的核心** ！`DecisionManager` 是一个自定义的 `Executor`，它：

1. **通过 `RequestResponse` 对象接收人工反馈** 
2. **处理用户的决策** （是/否）
3. **通过向适当的 Agent 发送消息来路由工作流** 

主要特点：
- 使用 `@handler` 装饰器将方法暴露为工作流步骤
- 接收包含原始请求和用户答案的 `RequestResponse[HumanFeedbackRequest, str]`
- 产出简单的“是”或“否”消息，以触发我们的条件函数

### 代码单元格 11

异步执行：async def 定义协程，await 等待结果；普通 .py 脚本需要 asyncio.run() 入口，Notebook 支持顶层 await。

输出观察：print 展示应用可观察结果；预存输出和现场结果可能不同，它不是模型内部思考记录。

```python
class DecisionManager(Executor):
    """
    Coordinates workflow routing based on human feedback.
    
    This executor receives RequestResponse objects from the RequestInfoExecutor
    and makes routing decisions by sending simple messages that trigger
    condition functions.
    """

    def __init__(self, id: str | None = None):
        super().__init__(id=id or "decision_manager")

    @handler
    async def on_confirmation(
        self,
        response: AgentExecutorResponse,
        ctx: WorkflowContext,
    ) -> None:
        """Parse the confirmation question and pause the workflow for human input."""
        confirmation = ConfirmationQuestion.model_validate_json(response.agent_run_response.text)
        display(
            HTML(f"""
            <div style='padding: 12px; background: #e1f5fe; border-left: 4px solid #0288d1; border-radius: 4px; margin: 10px 0;'>
                <strong>🔄 Requesting human input:</strong> {confirmation.question}
            </div>
        """)
        )
        # Pause the workflow; the human reply (a string) is delivered to on_human_feedback below.
        await ctx.request_info(
            request_data=HumanFeedbackRequest(
                prompt=confirmation.question,
                destination=confirmation.destination,
            ),
            response_type=str,
        )

    @response_handler
    async def on_human_feedback(
        self,
        original_request: HumanFeedbackRequest,
        feedback: str,
        ctx: WorkflowContext[AgentExecutorRequest, str],
    ) -> None:
        """Route the workflow based on the human's yes/no reply."""
        user_reply = (feedback or "").strip().lower()
        destination = original_request.destination or "unknown"

        display(
            HTML(f"""
            <div style='padding: 15px; background: #f3e5f5; border-left: 4px solid #9c27b0; border-radius: 4px; margin: 10px 0;'>
                <strong>🎯 Decision Manager:</strong> Processing user reply: <strong>"{user_reply}"</strong> for {destination}
            </div>
        """)
        )

        if user_reply == "yes":
            display(
                HTML("""
                <div style='padding: 12px; background: #c8e6c9; border-left: 4px solid #4caf50; border-radius: 4px; margin: 10px 0;'>
                    <strong>➡️  Routing:</strong> User wants alternatives → Will route to alternative_agent
                </div>
            """)
            )
            # Create and send a message for the alternative_agent
            user_msg = Message(
                role="user",
                contents=[f"The user wants to see alternative destinations near {destination}. Please suggest one."],
            )
            await ctx.send_message(AgentExecutorRequest(messages=[user_msg], should_respond=True))
        
        elif user_reply == "no":
            display(
                HTML("""
                <div style='padding: 12px; background: #ffcdd2; border-left: 4px solid #f44336; border-radius: 4px; margin: 10px 0;'>
                    <strong>🚫 Routing:</strong> User declined alternatives → cancellation_agent
                </div>
            """)
            )
            user_msg = Message(
                role="user",
                contents=["The user has declined to see alternatives. Please acknowledge their decision."],
            )
            await ctx.send_message(AgentExecutorRequest(messages=[user_msg], should_respond=True))
        else:
            # Handle unexpected input - treat as decline
            display(
                HTML(f"""
                <div style='padding: 12px; background: #fff3e0; border-left: 4px solid #ff9800; border-radius: 4px; margin: 10px 0;'>
                    <strong>⚠️  Warning:</strong> Unexpected input "{user_reply}" - treating as decline
                </div>
            """)
            )
            user_msg = Message(
                role="user",
                contents=["The user has declined to see alternatives. Please acknowledge their decision."],
            )
            await ctx.send_message(AgentExecutorRequest(messages=[user_msg], should_respond=True))


print("✅ DecisionManager executor created (@handler pauses via request_info, @response_handler routes)")
```

::: details 原文件保存的输出（不是本项目实测）

```text
✅ DecisionManager executor created with @handler method for human feedback
```

:::

## 第6步：创建自定义显示执行器

与条件工作流中的显示执行器相同 - 产出最终结果作为工作流输出。

### 代码单元格 13

异步执行：async def 定义协程，await 等待结果；普通 .py 脚本需要 asyncio.run() 入口，Notebook 支持顶层 await。

输出观察：print 展示应用可观察结果；预存输出和现场结果可能不同，它不是模型内部思考记录。

```python
@executor(id="prepare_human_request")
async def prepare_human_request(
    response: AgentExecutorResponse, 
    ctx: WorkflowContext[HumanFeedbackRequest]
) -> None:
    """
    Transform agent response into HumanFeedbackRequest for RequestInfoExecutor.
    
    This executor bridges the type gap between:
    - confirmation_agent outputs AgentExecutorResponse with ConfirmationQuestion JSON
    - request_info_executor expects HumanFeedbackRequest (RequestInfoMessage dataclass)
    """
    display(
        HTML("""
        <div style='padding: 12px; background: #e1f5fe; border-left: 4px solid #0288d1; border-radius: 4px; margin: 10px 0;'>
            <strong>🔄 Transform:</strong> Converting ConfirmationQuestion to HumanFeedbackRequest
        </div>
    """)
    )
    
    # Parse the agent's Pydantic output (ConfirmationQuestion)
    confirmation = ConfirmationQuestion.model_validate_json(response.agent_run_response.text)
    
    # Convert to HumanFeedbackRequest dataclass for RequestInfoExecutor
    feedback_request = HumanFeedbackRequest(
        prompt=confirmation.question,
        destination=confirmation.destination
    )
    
    # Send the properly typed RequestInfoMessage to the RequestInfoExecutor
    await ctx.send_message(feedback_request)


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


print("✅ prepare_human_request executor created with @executor decorator")
print("✅ display_result executor created with @executor decorator")
```

::: details 原文件保存的输出（不是本项目实测）

```text
✅ prepare_human_request executor created with @executor decorator
✅ display_result executor created with @executor decorator
```

:::

## 第7步：加载环境变量

配置LLM客户端（Microsoft Foundry / Azure OpenAI）。

### 代码单元格 15

配置加载：从本地环境读取端点与部署名；缺少变量时先修复配置，不要把密钥写进代码。

模型连接：project_endpoint 是项目地址，model 是实际部署名称；credential 提供访问身份。客户端创建本身不证明已经部署服务端 Agent。

输出观察：print 展示应用可观察结果；预存输出和现场结果可能不同，它不是模型内部思考记录。

```python
# Load environment variables
load_dotenv()

# Microsoft Foundry provider with keyless AzureCliCredential auth (run `az login`).
# Matches the pattern used across lessons 01-13 and the other Lesson 14 notebooks.
chat_client = FoundryChatClient(
    project_endpoint=os.environ["AZURE_AI_PROJECT_ENDPOINT"],
    model=os.environ["AZURE_AI_MODEL_DEPLOYMENT_NAME"],
    credential=AzureCliCredential(),
)

print("✅ Chat client configured with Microsoft Foundry")
```

::: details 原文件保存的输出（不是本项目实测）

```text
✅ Chat client configured with GitHub Models
```

:::

## 第8步：创建 AI Agent 和执行器

我们创建了 **六个工作流组件** ：

 **Agent（包装在 AgentExecutor 中）：** 
1. **availability_agent** - 使用工具检查酒店可用性
2. **confirmation_agent** - 🆕 准备人工确认请求
3. **alternative_agent** - 提供备选城市建议（当用户说是时）
4. **booking_agent** - 促使预订（当有空房时）
5. **cancellation_agent** - 🆕 处理取消消息（当用户说否时）

 **特殊执行器：** 
6. **request_info_executor** - 🆕 `RequestInfoExecutor`，用于暂停工作流以等待人工输入
7. **decision_manager** - 🆕 自定义执行器，根据人工响应进行路由（已在上面定义）

### 代码单元格 17

数据结构：Pydantic 模型定义字段类型；只有传入实际的 response_format 并检查解析结果，才能约束本次输出。

行为约束：instructions 引导模型，不能替代执行器的权限验证、次数限制和结果检查。

```python
# Agent 1: Check availability with tool (same as conditional workflow)
availability_agent = AgentExecutor(
    chat_client.as_agent(
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

# Agent 2: NEW - Prepare human confirmation request
confirmation_agent = AgentExecutor(
    chat_client.as_agent(
        instructions=(
            "You are a helpful assistant. The user's requested destination has no available hotel rooms. "
            "Create a polite message asking if they would like to see alternative destinations nearby. "
            "Return a JSON with: destination (the unavailable city), and question (a friendly yes/no question). "
            "Keep the question concise and friendly."
        ),
        default_options={"response_format": ConfirmationQuestion},  # Structured JSON output
    ),
    id="confirmation_agent",
)

# Agent 3: Suggest alternative (when user says yes)
alternative_agent = AgentExecutor(
    chat_client.as_agent(
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

# Agent 4: Suggest booking (when rooms available)
booking_agent = AgentExecutor(
    chat_client.as_agent(
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

# Agent 5: NEW - Handle cancellation when user declines alternatives
class CancellationMessage(BaseModel):
    """Message when user declines alternatives."""
    status: str
    message: str

cancellation_agent = AgentExecutor(
    chat_client.as_agent(
        instructions=(
            "You are a helpful assistant. The user has declined to see alternative hotel destinations. "
            "Create a polite cancellation message. "
            "Return JSON with: status (should be 'cancelled'), and message (a friendly acknowledgment). "
            "Keep the message brief and understanding."
        ),
        default_options={"response_format": CancellationMessage},
    ),
    id="cancellation_agent",
)

# DecisionManager instance - pauses for human input (request_info) and routes on the reply
decision_manager = DecisionManager(id="decision_manager")

display(
    HTML("""
    <div style='padding: 15px; background: #e3f2fd; border-left: 4px solid #2196f3; border-radius: 4px; margin: 10px 0;'>
        <strong>✅ Created Workflow Components:</strong>
        <ul style='margin: 10px 0 0 0;'>
            <li><strong>availability_agent</strong> - Checks availability with hotel_booking tool</li>
            <li><strong>confirmation_agent</strong> 🆕 - Prepares human confirmation request</li>
            <li><strong>alternative_agent</strong> - Suggests alternative cities</li>
            <li><strong>booking_agent</strong> - Encourages booking</li>
            <li><strong>cancellation_agent</strong> 🆕 - Handles user declining alternatives</li>
            <li><strong>request_info_executor</strong> 🆕 - Pauses workflow for human input</li>
            <li><strong>decision_manager</strong> 🆕 - Routes based on human response</li>
        </ul>
    </div>
""")
)
```

::: details 原文件保存的输出（不是本项目实测）

```text
<IPython.core.display.HTML object>
```

:::

## 第9步：构建包含人工干预的工作流程

现在我们构建包含 **条件路由** 的工作流程图，包括人工干预路径：

 **工作流程结构：** 
```
availability_agent (START)
        ↓
   Evaluate conditions
        ↙                    ↘
[no_availability]        [has_availability]
        ↓                        ↓
confirmation_agent          booking_agent
        ↓                        ↓
prepare_human_request      display_result
        ↓
request_info_executor (PAUSE)
        ↓
decision_manager
   ↙         ↘
[yes]        [no]
   ↓           ↓
alternative  cancellation
   ↓           ↓
display_result
```

 **关键边：** 
- `availability_agent → confirmation_agent`（当无空房时）
- `confirmation_agent → prepare_human_request`（转换类型）
- `prepare_human_request → request_info_executor`（等待人工操作）
- `request_info_executor → decision_manager`（始终 - 提供RequestResponse）
- `decision_manager → alternative_agent`（当用户说“是”时）
- `decision_manager → cancellation_agent`（当用户说“否”时）
- `availability_agent → booking_agent`（当有空房时）
- 所有路径均以 `display_result` 结束

### 代码单元格 19

阅读提示：跟踪本单元格读取的变量、修改的状态以及返回值。按原顺序执行，确认依赖的前序变量已经存在。

```python
# Build the workflow with human-in-the-loop routing
workflow = (
    WorkflowBuilder(
        start_executor=availability_agent,
        output_executors=[display_result],
    )
    
    # NO AVAILABILITY PATH (with human-in-the-loop)
    .add_edge(availability_agent, confirmation_agent, condition=no_availability_condition)
    .add_edge(confirmation_agent, decision_manager)  # decision_manager pauses via ctx.request_info
    
    # Decision manager routes based on user response
    .add_edge(decision_manager, alternative_agent, condition=user_wants_alternatives_condition)
    .add_edge(decision_manager, cancellation_agent, condition=user_declines_alternatives_condition)
    .add_edge(alternative_agent, display_result)
    .add_edge(cancellation_agent, display_result)
    
    # HAS AVAILABILITY PATH (no human input needed)
    .add_edge(availability_agent, booking_agent, condition=has_availability_condition)
    .add_edge(booking_agent, display_result)
    
    .build()
)

display(
    HTML("""
    <div style='padding: 20px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; border-radius: 8px; margin: 10px 0;'>
        <h3 style='margin: 0 0 15px 0;'>✅ Workflow Built Successfully!</h3>
        <p style='margin: 0; line-height: 1.6;'>
            <strong>Human-in-the-Loop Routing:</strong><br>
            • If <strong>NO availability</strong> → confirmation_agent → prepare_human_request → request_info_executor → <strong>PAUSE FOR HUMAN</strong> → decision_manager<br>
            &nbsp;&nbsp;• If user says <strong>YES</strong> → alternative_agent → display_result<br>
            &nbsp;&nbsp;• If user says <strong>NO</strong> → cancellation_agent → display_result<br>
            • If <strong>availability</strong> → booking_agent → display_result (no human input needed)
        </p>
    </div>
""")
)
```

::: details 原文件保存的输出（不是本项目实测）

```text
<IPython.core.display.HTML object>
```

:::

## 第10步：运行测试用例1 - 城市无可用性（巴黎需人工确认）

本测试演示了 **完整的人机交互循环** ：

1. 请求巴黎的酒店
2. availability_agent 检查 → 无房间
3. confirmation_agent 创建面向人类的问题
4. request_info_executor **暂停工作流** 并发出`RequestInfoEvent`
5. **应用程序检测事件并在控制台提示用户** 
6. 用户输入“yes”或“no”
7. 应用程序通过`send_responses_streaming()`发送响应
8. decision_manager 根据响应路由
9. 显示最终结果

 **关键模式：** 
- 首次迭代使用`workflow.run_stream()`
- 后续迭代使用`workflow.send_responses_streaming(pending_responses)`
- 监听`RequestInfoEvent`以检测何时需要人工输入
- 监听`WorkflowOutputEvent`以捕获最终结果

### 代码单元格 21

输出观察：print 展示应用可观察结果；预存输出和现场结果可能不同，它不是模型内部思考记录。

```python
display(
    HTML("""
    <div style='padding: 20px; background: #fff3e0; border-left: 4px solid #ff9800; border-radius: 8px; margin: 20px 0;'>
        <h3 style='margin: 0 0 10px 0; color: #e65100;'>🧪 TEST CASE 1: Paris (No Availability - Human-in-the-Loop)</h3>
        <p style='margin: 0;'>Expected workflow path: availability_agent → confirmation_agent → request_info_executor → <strong>PAUSE</strong> → decision_manager → (depends on user input)</p>
    </div>
""")
)

# Create request for Paris
request_paris = AgentExecutorRequest(
    messages=[Message(role="user", contents=["I want to book a hotel in Paris"])], 
    should_respond=True
)

# Human-in-the-loop execution pattern.
# We script the human's answer ("yes") instead of input() so the notebook runs unattended.
# In a real app, replace SCRIPTED_ANSWER with input() or a UI callback.
SCRIPTED_ANSWER = "yes"
workflow_output: str | None = None

print("\n🔄 Starting human-in-the-loop workflow...")
print("=" * 60)

# First run streams events; resume with run(stream=True, responses=...) after each pause.
stream = workflow.run(request_paris, stream=True)
while True:
    requests: list[tuple[str, HumanFeedbackRequest]] = []
    async for event in stream:
        if event.type == "request_info" and isinstance(event.data, HumanFeedbackRequest):
            print(f"\n⏸️  WORKFLOW PAUSED - Human input requested!")
            print(f"   Request ID: {event.request_id}")
            print(f"   Destination: {event.data.destination}")
            print(f"   Question: {event.data.prompt}")
            requests.append((event.request_id, event.data))
        elif event.type == "output":
            workflow_output = str(event.data)
            print(f"\n✅ Workflow completed with output!")

    if not requests:
        break

    # Provide the (scripted) human answer for each pending request.
    responses: dict[str, str] = {}
    for req_id, req in requests:
        answer = SCRIPTED_ANSWER
        print(f"\n📝 (scripted) You answered: {answer}")
        responses[req_id] = answer

    stream = workflow.run(stream=True, responses=responses)

print(f"\n{'='*60}")
print(f"🏆 FINAL WORKFLOW OUTPUT:")
print(f"{'='*60}")

# Display final result
if workflow_output:
    # Try to parse as JSON for pretty display
    try:
        result_data = json.loads(workflow_output)
        if "alternative_destination" in result_data:
            result_obj = AlternativeResult.model_validate_json(workflow_output)
            display(
                HTML(f"""
                <div style='padding: 25px; background: linear-gradient(135deg, #FFD700 0%, #FFA500 100%); border-radius: 12px; box-shadow: 0 4px 12px rgba(255,165,0,0.3); margin: 20px 0;'>
                    <h3 style='margin: 0 0 15px 0; color: #333;'>🏆 WORKFLOW RESULT</h3>
                    <div style='background: white; padding: 20px; border-radius: 8px;'>
                        <p style='margin: 0 0 10px 0; font-size: 16px;'><strong>Status:</strong> ❌ No rooms in Paris</p>
                        <p style='margin: 0 0 10px 0; font-size: 16px;'><strong>User Decision:</strong> ✅ Accepted alternatives</p>
                        <p style='margin: 0 0 10px 0; font-size: 16px;'><strong>Alternative Suggestion:</strong> 🏨 {result_obj.alternative_destination}</p>
                        <p style='margin: 0; font-size: 14px; color: #666;'><strong>Reason:</strong> {result_obj.reason}</p>
                    </div>
                </div>
            """)
            )
        else:
            # User declined
            display(
                HTML(f"""
                <div style='padding: 25px; background: linear-gradient(135deg, #f44336 0%, #e91e63 100%); color: white; border-radius: 12px; box-shadow: 0 4px 12px rgba(244,67,54,0.3); margin: 20px 0;'>
                    <h3 style='margin: 0 0 15px 0;'>🏆 WORKFLOW RESULT</h3>
                    <div style='background: white; color: #333; padding: 20px; border-radius: 8px;'>
                        <p style='margin: 0 0 10px 0; font-size: 16px;'><strong>Status:</strong> ❌ No rooms in Paris</p>
                        <p style='margin: 0 0 10px 0; font-size: 16px;'><strong>User Decision:</strong> 🚫 Declined alternatives</p>
                        <p style='margin: 0; font-size: 14px; color: #666;'><strong>Result:</strong> Booking request cancelled</p>
                    </div>
                </div>
            """)
            )
    except:
        print(workflow_output)
```

::: details 原文件保存的输出（不是本项目实测）

```text
<IPython.core.display.HTML object>

🔄 Starting human-in-the-loop workflow...
============================================================

🚀 Starting workflow with request: 'I want to book a hotel in Paris'

<IPython.core.display.HTML object>
<IPython.core.display.HTML object>
<IPython.core.display.HTML object>
<IPython.core.display.HTML object>

⏸️  WORKFLOW PAUSED - Human input requested!
   Request ID: 032c8fce-b9d1-400e-ba8d-afd2248e2926
   Destination: Paris

============================================================
💬 QUESTION FOR YOU:
   Unfortunately, there are no rooms available in Paris. Would you like to explore nearby alternative destinations?
============================================================

📝 You answered: yes

📤 Sending human responses: {'032c8fce-b9d1-400e-ba8d-afd2248e2926': 'yes'}

🚀 Starting workflow with request: 'I want to book a hotel in Paris'

📝 You answered: yes

📤 Sending human responses: {'032c8fce-b9d1-400e-ba8d-afd2248e2926': 'yes'}

🚀 Starting workflow with request: 'I want to book a hotel in Paris'

<IPython.core.display.HTML object>
<IPython.core.display.HTML object>
<IPython.core.display.HTML object>
<IPython.core.display.HTML object>

⏸️  WORKFLOW PAUSED - Human input requested!
   Request ID: cf48dad0-ee5e-4f60-8806-341a7a292bd4
   Destination: Paris

============================================================
💬 QUESTION FOR YOU:
   I'm sorry to inform you that there are no available hotel rooms in Paris. Would you like me to suggest nearby alternative destinations?
============================================================

📝 You answered: 

📤 Sending human responses: {'cf48dad0-ee5e-4f60-8806-341a7a292bd4': ''}

🚀 Starting workflow with request: 'I want to book a hotel in Paris'

📝 You answered: 

📤 Sending human responses: {'cf48dad0-ee5e-4f60-8806-341a7a292bd4': ''}

🚀 Starting workflow with request: 'I want to book a hotel in Paris'

<IPython.core.display.HTML object>
```

:::

## 第11步：运行测试用例2 - 城市有房源（斯德哥尔摩 - 无需人工输入）

此测试演示当有房间可用时的 **直接路径** ：

1. 请求斯德哥尔摩的酒店
2. availability_agent 检查 → 有房间 ✅
3. booking_agent 建议预订
4. display_result 显示确认
5. **无需人工输入！** 

当有房间可用时，工作流会完全绕过人工干预路径。

### 代码单元格 23

阅读提示：跟踪本单元格读取的变量、修改的状态以及返回值。按原顺序执行，确认依赖的前序变量已经存在。

```python
display(
    HTML("""
    <div style='padding: 20px; background: #e8f5e9; border-left: 4px solid #4caf50; border-radius: 8px; margin: 20px 0;'>
        <h3 style='margin: 0 0 10px 0; color: #1b5e20;'>🧪 TEST CASE 2: Stockholm (Has Availability - No Human Input)</h3>
        <p style='margin: 0;'>Expected workflow path: availability_agent → booking_agent → display_result (direct, no pause)</p>
    </div>
""")
)

# Create request for Stockholm
request_stockholm = AgentExecutorRequest(
    messages=[Message(role="user", contents=["I want to book a hotel in Stockholm"])], 
    should_respond=True
)

# Run the workflow (should complete without human input)
events_stockholm = await workflow.run(request_stockholm)
outputs_stockholm = events_stockholm.get_outputs()

# Display results
if outputs_stockholm:
    result_stockholm = BookingConfirmation.model_validate_json(outputs_stockholm[0])

    display(
        HTML(f"""
        <div style='padding: 25px; background: linear-gradient(135deg, #4caf50 0%, #8bc34a 100%); color: white; border-radius: 12px; box-shadow: 0 4px 12px rgba(76,175,80,0.3); margin: 20px 0;'>
            <h3 style='margin: 0 0 15px 0;'>🏆 WORKFLOW RESULT (Stockholm - No Human Input)</h3>
            <div style='background: white; color: #333; padding: 20px; border-radius: 8px;'>
                <p style='margin: 0 0 10px 0; font-size: 16px;'><strong>Status:</strong> ✅ Rooms Available!</p>
                <p style='margin: 0 0 10px 0; font-size: 16px;'><strong>Destination:</strong> 🏨 {result_stockholm.destination}</p>
                <p style='margin: 0 0 10px 0; font-size: 16px;'><strong>Action:</strong> {result_stockholm.action}</p>
                <p style='margin: 0 0 10px 0; font-size: 14px; color: #666;'><strong>Message:</strong> {result_stockholm.message}</p>
                <p style='margin: 10px 0 0 0; font-size: 12px; color: #999; font-style: italic;'>Note: No human input was requested because rooms were available!</p>
            </div>
        </div>
    """)
    )
```

## 关键要点与人类参与最佳实践

### ✅ 你学到了什么：

#### 1. **RequestInfoExecutor 模式** 
Microsoft Agent Framework 中的人类参与模式使用三个关键组件：
- `RequestInfoExecutor` - 暂停工作流并发送事件
- `RequestInfoMessage` - 具有类型的请求负载基类（请继承该类！）
- `RequestResponse` - 关联人类响应与原始请求

 **关键理解：** 
- `RequestInfoExecutor` 本身不收集输入 — 它只是暂停工作流
- 应用代码必须监听 `RequestInfoEvent` 并收集输入
- 你必须调用 `send_responses_streaming()`，传入一个将 `request_id` 映射到用户答案的字典

#### 2. **流式执行模式** 
```python
# 第一次迭代
stream = workflow.run_stream(initial_request)

# 后续迭代（在人类输入之后）
stream = workflow.send_responses_streaming(pending_responses)

# 始终处理事件
events = [event async for event in stream]
```

#### 3. **事件驱动架构** 
监听特定事件以控制工作流：
- `RequestInfoEvent` - 需要人类输入（工作流暂停）
- `WorkflowOutputEvent` - 最终结果已可用（工作流完成）
- `WorkflowStatusEvent` - 状态变更（IN_PROGRESS，IDLE_WITH_PENDING_REQUESTS 等）

#### 4. **使用 @handler 的自定义执行器** 
`DecisionManager` 演示了如何创建执行器：
- 使用 `@handler` 装饰器将方法暴露为工作流步骤
- 接收类型化消息（例如，`RequestResponse[HumanFeedbackRequest, str]`）
- 通过发送消息给其他执行器路由工作流
- 通过 `WorkflowContext` 访问上下文

#### 5. **带有人类决策的条件路由** 
你可以创建评估人类响应的条件函数：
```python
def user_wants_alternatives_condition(message: Any) -> bool:
    response_text = message.agent_run_response.text.lower()
    return response_text == "yes"
```

### 🎯 现实世界应用：

1. **审批工作流** 
   - 处理报销前需要经理批准
   - 发送自动邮件前须人工审核
   - 执行高价值交易前确认

2. **内容审核** 
   - 标记可疑内容供人工审核
   - 让审核员对边缘案例做出最终决定
   - AI 置信度低时升级交给人工

3. **客户服务** 
   - 让 AI 自动处理常规问题
   - 将复杂问题升级给人工 Agent
   - 询问客户是否想与人工交流

4. **数据处理** 
   - 请人工解决模糊数据条目
   - 确认 AI 对不清晰文件的解读
   - 让用户选择多种有效解释中的一种

5. **安全关键系统** 
   - 不可逆操作前需人工确认
   - 访问敏感数据前须批准
   - 受监管行业（医疗、金融）中的决策确认

6. **交互式 Agent** 
   - 构建会提出后续问题的对话机器人
   - 创建引导用户完成复杂流程的向导
   - 设计与人类逐步协作的 Agent

### 🔄 对比：有无人类参与

| 特性 | 条件工作流 | 人类参与工作流 |
|---------|---------------------|---------------------------|
| **执行** | 单次 `workflow.run()` | 循环执行，使用 `run_stream()` + `send_responses_streaming()` |
| **用户输入** | 无（完全自动） | 通过 `input()` 或 UI 的交互式提示 |
| **组件** | Agents + Executors | + RequestInfoExecutor + DecisionManager |
| **事件** | 只有 AgentExecutorResponse | RequestInfoEvent，WorkflowOutputEvent 等 |
| **暂停** | 不暂停 | 在 RequestInfoExecutor 处暂停工作流 |
| **人工控制** | 无人工控制 | 人工做关键决策 |
| **用例** | 自动化 | 协作与监督 |

### 🚀 高级模式：

#### 多个人工决策点
同一个工作流中可以有多个 `RequestInfoExecutor` 节点：
```python
.add_edge(agent1, request_info_1)  # 第一次人工决策
.add_edge(decision_manager_1, agent2)
.add_edge(agent2, request_info_2)  # 第二次人工决策
.add_edge(decision_manager_2, final_agent)
```

#### 超时处理
为人工响应实现超时机制：
```python
import asyncio

try:
    answer = await asyncio.wait_for(
        asyncio.to_thread(input, "Enter yes/no: "),
        timeout=60.0
    )
except asyncio.TimeoutError:
    answer = "no"  # 默认选择安全选项
```

#### 丰富的 UI 集成
代替 `input()`，集成网页 UI、Slack、Teams 等：
```python
if isinstance(event, RequestInfoEvent):
    # 发送通知到用户的首选频道
    await slack_client.send_message(
        user_id=current_user,
        text=event.data.prompt,
        request_id=event.request_id
    )
```

#### 条件式人机交互
仅在特定情况下请求人工输入：
```python
def needs_human_approval_condition(message: Any) -> bool:
    # 只有在置信度低或数值高时才会转给人工处理
    if result.confidence < 0.7 or result.value > 10000:
        return True
    return False
```

### ⚠️ 最佳实践：

1. **始终继承 RequestInfoMessage** 
   - 提供类型安全和校验
   - 支持用于 UI 渲染的丰富上下文
   - 明确每种请求类型的意图

2. **使用描述性提示** 
   - 包含你正在请求的背景信息
   - 说明各选项的后果
   - 保持问题简洁明了

3. **处理意外输入** 
   - 验证用户响应
   - 为无效输入提供默认选项
   - 给出清晰的错误提示

4. **跟踪请求 ID** 
   - 利用 request_id 与响应的关联
   - 不要尝试手动管理状态

5. **设计非阻塞** 
   - 不要阻塞线程等待输入
   - 全程使用异步模式
   - 支持并发工作流实例

### 📚 相关概念：

- **Agent 中间件** - 拦截 Agent 调用（前一章节）
- **工作流状态管理** - 在运行间持久化状态
- **多 Agent 协作** - 结合人类参与与 Agent 团队
- **事件驱动架构** - 使用事件构建响应式系统

---

### 🎓 恭喜！

你已掌握 Microsoft Agent Framework 的人类参与工作流！你现在知道如何：
- ✅ 暂停工作流以收集人类输入
- ✅ 使用 RequestInfoExecutor 和 RequestInfoMessage
- ✅ 通过事件处理流式执行
- ✅ 使用 @handler 创建自定义执行器
- ✅ 基于人类决策路由工作流
- ✅ 构建与人类协作的交互式 AI Agent

 **这是构建可信、可控 AI 系统的关键模式！** 🚀


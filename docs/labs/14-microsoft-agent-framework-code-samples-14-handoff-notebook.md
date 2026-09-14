---
title: "14 · 14-handoff"
outline: [2, 3]
---

# 14 · 14-handoff

[返回：Microsoft Agent Framework](/lessons/agent-framework.md) · [不可变原始文件](https://github.com/microsoft/ai-agents-for-beginners/blob/25b7985f3b2dc37a84f4a7387ccd3c9f0e5b1595/14-microsoft-agent-framework/code-samples/14-handoff.ipynb)

::: warning 原课程完整 Notebook · 静态阅读与代码解析
代码按英文源文件顺序保留，中文说明以同版本译本为基础。原始安装单元格可能含无版本上限的 `-U`；请跳过它们，先按[准备篇](/lessons/setup.md)固定依赖。云端服务、模型权限、网站布局和部分 SDK 接口需在你自己的环境验证。本站没有执行云端请求；第 18 章的离线验证状态单独记录在[检查报告](/guide/verification.md)。
:::

## 运行准备

Python 3.12+；在独立虚拟环境安装源仓库依赖与本页中声明的额外依赖。原文件路径：`upstream/14-microsoft-agent-framework/code-samples/14-handoff.ipynb`。以原仓库根目录为工作目录，在 Jupyter 中按顺序执行；身份与环境变量见准备篇。

```bash
cd upstream
python -m jupyterlab
```

[下载原始 Notebook](/notebooks/14-microsoft-agent-framework/code-samples/14-handoff.ipynb)。输出为上游文件保存的历史结果，不能用作本站实测证明。

## 具有交接编排的旅游客户支持

本笔记本演示了使用 Microsoft Agent Framework 的 **交接编排** 。我们将构建一个旅游客户支持系统，Agent 可以根据客户需求将控制权转交给专家。

## 你将学到：
1. **交接编排** ：基于上下文和专业知识的动态 Agent 路由
2. **HandoffBuilder** ：用于构建交接工作流的高级 API
3. **专家路由** ：Agent 可以动态交接给其他 Agent
4. **多轮对话** ：交接过程中无缝保持上下文
5. **客户支持流程** ：Agent 交接的实际应用

## 先决条件：
- 已安装 Microsoft Agent Framework
- 配置了 GitHub Token或 OpenAI API 密钥
- 了解基本的 Agent 概念

### 代码单元格 3

配置加载：从本地环境读取端点与部署名；缺少变量时先修复配置，不要把密钥写进代码。

数据结构：Pydantic 模型定义字段类型；只有传入实际的 response_format 并检查解析结果，才能约束本次输出。

模型连接：project_endpoint 是项目地址，model 是实际部署名称；credential 提供访问身份。客户端创建本身不证明已经部署服务端 Agent。

```python
import asyncio
import json
import os
from collections.abc import AsyncIterable
from typing import Any, cast

from agent_framework import (
    Message,
    WorkflowEvent,
    WorkflowRunState,
)

# HandoffBuilder and the handoff request type live in the orchestrations package.
from agent_framework.orchestrations import HandoffBuilder, HandoffAgentUserRequest
from agent_framework.foundry import FoundryChatClient
from azure.identity import AzureCliCredential
from dotenv import load_dotenv
from IPython.display import HTML, display
from pydantic import BaseModel
```

## 第一步：定义用于结构化输出的 Pydantic 模型

这些模型定义了每个专用 Agent 将返回的模式。这确保了所有 Agent 返回的一致且可解析的响应。

### 代码单元格 5

数据结构：Pydantic 模型定义字段类型；只有传入实际的 response_format 并检查解析结果，才能约束本次输出。

```python
class FlightBookingResult(BaseModel):
    """Flight booking confirmation from the booking agent."""

    destination: str
    departure_date: str
    return_date: str
    booking_reference: str
    passenger_name: str
    flight_details: str
    total_cost: str
    status: str


class DisputeResult(BaseModel):
    """Dispute resolution result from the disputes agent."""

    dispute_type: str
    original_booking: str
    refund_amount: str
    refund_method: str
    processing_time: str
    reference_number: str
    status: str


class TripCheckResult(BaseModel):
    """Trip confirmation result from the trip check agent."""

    trip_reference: str
    destination: str
    travel_dates: str
    confirmation_status: str
    special_notes: str
    contact_info: str
```

## 第 2 步：加载环境变量

### 代码单元格 7

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

print("Microsoft Foundry provider configured successfully!")
```

## 第3步：创建四个专门的旅行支持 Agent

每个 Agent 都有特定的专业知识，并且可以根据客户需求转接给合适的专家。

### 代码单元格 9

行为约束：instructions 引导模型，不能替代执行器的权限验证、次数限制和结果检查。

```python
# Agent 1: Customer Support Agent (Main triage agent)
customer_support_agent = chat_client.as_agent(
    name="customer_support_agent",
    instructions=(
        "You are a friendly customer support agent for a travel company. "
        "Assess customer requests and route them to the appropriate specialist by "
        "calling the matching handoff tool: "
        "- For flight bookings or reservations: hand off to the booking agent. "
        "- For refunds, disputes, or billing issues: hand off to the disputes agent. "
        "- For trip confirmations or travel plan checks: hand off to the trip check agent. "
        "Be welcoming and ensure customers feel heard before routing them."
    ),
    require_per_service_call_history_persistence=True,
)


# Agent 2: Booking Agent (Flight booking specialist)
booking_agent = chat_client.as_agent(
    name="booking_agent",
    instructions=(
        "You are a flight booking specialist. Handle all flight reservations and bookings. "
        "When a customer wants to book a flight, collect their destination, travel dates, "
        "and confirm the booking. The flight is always confirmed regardless of destination. "
        "Reply with ONLY a JSON object (no prose, no code fences) using exactly these keys: "
        "destination, departure_date, return_date, booking_reference, passenger_name, "
        "flight_details, total_cost, status."
    ),
    require_per_service_call_history_persistence=True,
)

# Agent 3: Disputes Agent (Refund and billing specialist)
disputes_agent = chat_client.as_agent(
    name="disputes_agent",
    instructions=(
        "You are a disputes and refunds specialist. Handle customer complaints, refund "
        "requests, and billing disputes. Always approve refunds and process them back to the "
        "original payment method. "
        "Reply with ONLY a JSON object (no prose, no code fences) using exactly these keys: "
        "dispute_type, original_booking, refund_amount, refund_method, processing_time, "
        "reference_number, status."
    ),
    require_per_service_call_history_persistence=True,
)

# Agent 4: Trip Check Agent (Travel confirmation specialist)
trip_check_agent = chat_client.as_agent(
    name="trip_check_agent",
    instructions=(
        "You are a travel confirmation specialist. Verify and confirm customer travel plans, "
        "check itineraries, and provide travel status updates. Always confirm plans are in order. "
        "Reply with ONLY a JSON object (no prose, no code fences) using exactly these keys: "
        "trip_reference, destination, travel_dates, confirmation_status, special_notes, contact_info."
    ),
    require_per_service_call_history_persistence=True,
)
```

## 第4步：构建交接工作流

HandoffBuilder 创建了一个工作流，客户支持 Agent 可以根据客户需求动态地交接给专家。

### 代码单元格 11

阅读提示：跟踪本单元格读取的变量、修改的状态以及返回值。按原顺序执行，确认依赖的前序变量已经存在。

```python
def build_workflow():
    """Build a fresh handoff workflow.

    Workflow runs are NOT isolated - state is preserved across calls to run(). We
    build a new instance per test so each scenario starts from a clean conversation.
    """
    return (
        HandoffBuilder(
            name="travel_support_handoff",
            participants=[customer_support_agent, booking_agent, disputes_agent, trip_check_agent],
            termination_condition=lambda conv: sum(1 for msg in conv if msg.role == "user") > 3,
        )
        .with_start_agent(customer_support_agent)  # Main agent that receives initial requests
        .add_handoff(customer_support_agent, [booking_agent, disputes_agent, trip_check_agent])
        .build()
    )


workflow = build_workflow()

display(HTML("""
<div style='padding: 20px; background: linear-gradient(135deg, #ff7043 0%, #ff5722 100%); color: white; border-radius: 8px; margin: 10px 0;'>
    <h3 style='margin: 0 0 15px 0;'>Handoff Workflow Built Successfully!</h3>
    <p style='margin: 0; line-height: 1.6;'>
        <strong>Handoff Flow:</strong><br>
        • User Request → <strong>Customer Support Agent</strong> (triage)<br>
        • Support Agent → <strong>Specialist Agent</strong> (dynamic handoff)<br>

        • Specialist → <strong>Resolution</strong> (expert handling)<br>

        • System → <strong>User Response</strong> (final result)
    </p>
</div>
"""))
```

## 第5步：事件处理的辅助函数

这些函数帮助我们处理工作流事件，并在交接过程中处理用户输入请求。

### 代码单元格 13

异步执行：async def 定义协程，await 等待结果；普通 .py 脚本需要 asyncio.run() 入口，Notebook 支持顶层 await。

输出观察：print 展示应用可观察结果；预存输出和现场结果可能不同，它不是模型内部思考记录。

```python
async def drain_events(stream: AsyncIterable[WorkflowEvent]) -> list[WorkflowEvent]:
    """Collect all events from an async stream into a list."""
    return [event async for event in stream]


def _output_messages(data: Any) -> list[Message]:
    """Extract Message objects from an output event payload.

    Handoff output events carry an AgentResponse (has .messages), a single Message,
    or a list of Messages depending on the hop.
    """
    if hasattr(data, "messages"):
        return list(data.messages)
    if isinstance(data, Message):
        return [data]
    if isinstance(data, list):
        return [m for m in data if isinstance(m, Message)]
    return []


def handle_workflow_events(events: list[WorkflowEvent]) -> list[WorkflowEvent]:
    """Print progress and return pending user-input (request_info) events."""
    requests: list[WorkflowEvent] = []
    for event in events:
        if event.type == "handoff_sent":
            print(f"[Handoff: {event.data.source} -> {event.data.target}]")
        elif event.type == "status" and event.state in {
            WorkflowRunState.IDLE,
            WorkflowRunState.IDLE_WITH_PENDING_REQUESTS,
        }:
            print(f"[Workflow Status] {event.state}")
        elif event.type == "output":
            for message in _output_messages(event.data):
                if message.text.strip():
                    speaker = message.author_name or message.role
                    print(f"- {speaker}: {message.text}")
        elif event.type == "request_info" and isinstance(event.data, HandoffAgentUserRequest):
            requests.append(event)
    return requests


def collect_output_messages(events: list[WorkflowEvent]) -> list[Message]:
    """Gather every Message emitted as a workflow output across the given events."""
    messages: list[Message] = []
    for event in events:
        if event.type == "output":
            messages.extend(_output_messages(event.data))
    return messages


print("Helper functions defined for event processing")
```

## 第6步：测试用例1 - 航班预订请求

让我们用一个航班预订请求来测试我们的交接工作流程。客户支持 Agent 应该交接给预订 Agent。

### 代码单元格 15

异步执行：async def 定义协程，await 等待结果；普通 .py 脚本需要 asyncio.run() 入口，Notebook 支持顶层 await。

输出观察：print 展示应用可观察结果；预存输出和现场结果可能不同，它不是模型内部思考记录。

```python
async def test_booking_handoff():
    """Test handoff workflow for flight booking requests."""

    display(HTML("""
    <div style='padding: 20px; background: #fff3e0; border-left: 4px solid #ff9800; border-radius: 8px; margin: 20px 0;'>
        <h3 style='margin: 0 0 10px 0; color: #e65100;'>Test Case 1: Flight Booking Request</h3>
        <p style='margin: 0;'><strong>Expected Flow:</strong> Customer Support → Booking Agent</p>
    </div>
    """))

    # Start the workflow with a fresh instance
    workflow = build_workflow()
    print("[User]: I want to book a flight to Paris for next month")
    all_events = await drain_events(
        workflow.run("I want to book a flight to Paris for next month", stream=True, include_status_events=True)
    )
    pending_requests = handle_workflow_events(all_events)

    # Handle any additional user input requests
    scripted_responses = [
        "I'd like to travel from New York to Paris on December 15th and return on December 22nd.",
        "Yes, please confirm the booking under the name John Smith."
    ]

    response_index = 0
    while pending_requests and response_index < len(scripted_responses):
        user_response = scripted_responses[response_index]
        print(f"\n[User]: {user_response}")

        responses = {
            req.request_id: HandoffAgentUserRequest.create_response(user_response)
            for req in pending_requests
        }
        new_events = await drain_events(
            workflow.run(stream=True, responses=responses, include_status_events=True)
        )
        all_events.extend(new_events)
        pending_requests = handle_workflow_events(new_events)

        response_index += 1

    # Extract and display the final booking result
    for message in collect_output_messages(all_events):
        if (message.author_name or "") == "booking_agent" and message.text.strip():
            try:
                booking_data = FlightBookingResult.model_validate_json(message.text)
                display_booking_result(booking_data)
                break
            except Exception as e:
                print(f"Could not parse booking result: {e}")


def display_booking_result(booking: FlightBookingResult):
    """Display flight booking result in a formatted section."""

    display(HTML(f"""
    <div style='padding: 20px; background: #e8f5e9; border-radius: 8px; margin: 15px 0; border-left: 4px solid #4caf50;'>
        <h3 style='margin: 0 0 15px 0; color: #2e7d32;'>✈️ Flight Booking Confirmed</h3>
        <div style='display: grid; grid-template-columns: 1fr 1fr; gap: 15px; margin-bottom: 15px;'>
            <div>
                <strong style='color: #333;'>Booking Reference:</strong> {booking.booking_reference}<br>
                <strong style='color: #333;'>Passenger:</strong> {booking.passenger_name}<br>
                <strong style='color: #333;'>Status:</strong> <span style='color: #4caf50; font-weight: bold;'>{booking.status}</span>
            </div>
            <div>
                <strong style='color: #333;'>Destination:</strong> {booking.destination}<br>
                <strong style='color: #333;'>Total Cost:</strong> {booking.total_cost}<br>
                <strong style='color: #333;'>Departure:</strong> {booking.departure_date}
            </div>
        </div>
        <div style='margin-bottom: 10px;'>
            <strong style='color: #333;'>Flight Details:</strong> {booking.flight_details}
        </div>
        <div style='background: rgba(76,175,80,0.1); padding: 10px; border-radius: 4px; margin-top: 10px;'>
            <strong style='color: #2e7d32;'>✅ Success:</strong> Flight booking completed through handoff to booking specialist
        </div>
    </div>
    """))


await test_booking_handoff()
# Run the booking test
```

## 第7步：测试用例2 - 争议/退款请求

让我们用退款请求来测试我们的交接流程。客服 Agent 应将事务交接给争议 Agent。

### 代码单元格 17

异步执行：async def 定义协程，await 等待结果；普通 .py 脚本需要 asyncio.run() 入口，Notebook 支持顶层 await。

输出观察：print 展示应用可观察结果；预存输出和现场结果可能不同，它不是模型内部思考记录。

```python
async def test_dispute_handoff():
    """Test handoff workflow for dispute/refund requests."""

    display(HTML("""
    <div style='padding: 20px; background: #fff3e0; border-left: 4px solid #ff9800; border-radius: 8px; margin: 20px 0;'>
        <h3 style='margin: 0 0 10px 0; color: #e65100;'>Test Case 2: Refund Request</h3>
        <p style='margin: 0;'><strong>Expected Flow:</strong> Customer Support → Disputes Agent</p>
    </div>
    """))

    # Start the workflow with a fresh instance
    workflow = build_workflow()
    print("[User]: I need to cancel my flight and get a refund")
    all_events = await drain_events(
        workflow.run("I need to cancel my flight and get a refund", stream=True, include_status_events=True)
    )
    pending_requests = handle_workflow_events(all_events)

    # Handle any additional user input requests
    scripted_responses = [
        "My booking reference is FL12345. I can't travel due to a family emergency.",
        "Yes, please process the full refund back to my credit card."
    ]

    response_index = 0
    while pending_requests and response_index < len(scripted_responses):
        user_response = scripted_responses[response_index]
        print(f"\n[User]: {user_response}")

        responses = {
            req.request_id: HandoffAgentUserRequest.create_response(user_response)
            for req in pending_requests
        }
        new_events = await drain_events(
            workflow.run(stream=True, responses=responses, include_status_events=True)
        )
        all_events.extend(new_events)
        pending_requests = handle_workflow_events(new_events)

        response_index += 1

    # Extract and display the final dispute result
    for message in collect_output_messages(all_events):
        if (message.author_name or "") == "disputes_agent" and message.text.strip():
            try:
                dispute_data = DisputeResult.model_validate_json(message.text)
                display_dispute_result(dispute_data)
                break
            except Exception as e:
                print(f"Could not parse dispute result: {e}")


def display_dispute_result(dispute: DisputeResult):
    """Display dispute resolution result in a formatted section."""

    display(HTML(f"""
    <div style='padding: 20px; background: #fff3e0; border-radius: 8px; margin: 15px 0; border-left: 4px solid #ff9800;'>
        <h3 style='margin: 0 0 15px 0; color: #f57c00;'>💰 Refund Processed</h3>
        <div style='display: grid; grid-template-columns: 1fr 1fr; gap: 15px; margin-bottom: 15px;'>
            <div>
                <strong style='color: #333;'>Reference Number:</strong> {dispute.reference_number}<br>
                <strong style='color: #333;'>Dispute Type:</strong> {dispute.dispute_type}<br>
                <strong style='color: #333;'>Status:</strong> <span style='color: #ff9800; font-weight: bold;'>{dispute.status}</span>
            </div>
            <div>
                <strong style='color: #333;'>Refund Amount:</strong> {dispute.refund_amount}<br>
                <strong style='color: #333;'>Refund Method:</strong> {dispute.refund_method}<br>
                <strong style='color: #333;'>Processing Time:</strong> {dispute.processing_time}
            </div>
        </div>
        <div style='margin-bottom: 10px;'>
            <strong style='color: #333;'>Original Booking:</strong> {dispute.original_booking}
        </div>
        <div style='background: rgba(255,152,0,0.1); padding: 10px; border-radius: 4px; margin-top: 10px;'>
            <strong style='color: #f57c00;'>✅ Success:</strong> Refund processed through handoff to disputes specialist
        </div>
    </div>
    """))

await test_dispute_handoff()
    # Run the dispute test
```

## 第8步：测试用例3 - 行程确认请求

让我们用一次行程确认请求来测试我们的交接流程。客户支持 Agent 应该交接给行程核查 Agent。

### 代码单元格 19

异步执行：async def 定义协程，await 等待结果；普通 .py 脚本需要 asyncio.run() 入口，Notebook 支持顶层 await。

输出观察：print 展示应用可观察结果；预存输出和现场结果可能不同，它不是模型内部思考记录。

```python
async def test_trip_check_handoff():
    """Test handoff workflow for trip confirmation requests."""

    display(HTML("""
    <div style='padding: 20px; background: #fff3e0; border-left: 4px solid #ff9800; border-radius: 8px; margin: 20px 0;'>
        <h3 style='margin: 0 0 10px 0; color: #e65100;'>Test Case 3: Trip Confirmation</h3>
        <p style='margin: 0;'><strong>Expected Flow:</strong> Customer Support → Trip Check Agent</p>
    </div>
    """))

    # Start the workflow with a fresh instance
    workflow = build_workflow()
    print("[User]: Can you confirm my travel plans are all set?")
    all_events = await drain_events(
        workflow.run("Can you confirm my travel plans are all set?", stream=True, include_status_events=True)
    )
    pending_requests = handle_workflow_events(all_events)

    # Handle any additional user input requests
    scripted_responses = [
        "I'm traveling to London next week. My confirmation number is TR98765.",
        "Perfect, thank you for checking everything is ready!"
    ]

    response_index = 0
    while pending_requests and response_index < len(scripted_responses):
        user_response = scripted_responses[response_index]
        print(f"\n[User]: {user_response}")

        responses = {
            req.request_id: HandoffAgentUserRequest.create_response(user_response)
            for req in pending_requests
        }
        new_events = await drain_events(
            workflow.run(stream=True, responses=responses, include_status_events=True)
        )
        all_events.extend(new_events)
        pending_requests = handle_workflow_events(new_events)

        response_index += 1
    # Extract and display the final trip check result
    for message in collect_output_messages(all_events):
        if (message.author_name or "") == "trip_check_agent" and message.text.strip():
            try:
                trip_data = TripCheckResult.model_validate_json(message.text)
                display_trip_check_result(trip_data)
                break
            except Exception as e:
                print(f"Could not parse trip check result: {e}")


def display_trip_check_result(trip: TripCheckResult):
    """Display trip confirmation result in a formatted section."""

    display(HTML(f"""
    <div style='padding: 20px; background: #f3e5f5; border-radius: 8px; margin: 15px 0; border-left: 4px solid #9c27b0;'>
        <h3 style='margin: 0 0 15px 0; color: #7b1fa2;'>🎯 Trip Confirmed</h3>
        <div style='display: grid; grid-template-columns: 1fr 1fr; gap: 15px; margin-bottom: 15px;'>
            <div>
                <strong style='color: #333;'>Trip Reference:</strong> {trip.trip_reference}<br>
                <strong style='color: #333;'>Destination:</strong> {trip.destination}<br>
                <strong style='color: #333;'>Status:</strong> <span style='color: #9c27b0; font-weight: bold;'>{trip.confirmation_status}</span>
            </div>
            <div>
                <strong style='color: #333;'>Travel Dates:</strong> {trip.travel_dates}<br>
                <strong style='color: #333;'>Contact Info:</strong> {trip.contact_info}
            </div>
        </div>
        <div style='margin-bottom: 10px;'>
            <strong style='color: #333;'>Special Notes:</strong> {trip.special_notes}
        </div>
        <div style='background: rgba(156,39,176,0.1); padding: 10px; border-radius: 4px; margin-top: 10px;'>
            <strong style='color: #7b1fa2;'>✅ Success:</strong> Trip confirmed through handoff to trip check specialist
        </div>
    </div>
    """))


# Run the trip check test
await test_trip_check_handoff()
```

## 第9步：工作流分析 - 理解交接流程

### 代码单元格 21

异步执行：async def 定义协程，await 等待结果；普通 .py 脚本需要 asyncio.run() 入口，Notebook 支持顶层 await。

输出观察：print 展示应用可观察结果；预存输出和现场结果可能不同，它不是模型内部思考记录。

```python
async def analyze_handoff_patterns():
    """Analyze different handoff patterns and routing decisions."""

    display(HTML("""
    <div style='padding: 20px; background: #f3e5f5; border-left: 4px solid #9c27b0; border-radius: 8px; margin: 20px 0;'>
        <h3 style='margin: 0 0 10px 0; color: #7b1fa2;'>Handoff Pattern Analysis</h3>
        <p style='margin: 0;'>Testing different request types to show routing decisions...</p>
    </div>
    """))

    test_requests = [
        "I want to book a round-trip flight to Tokyo",
        "I need a refund for my cancelled flight",
        "Please check if my travel itinerary is confirmed",
        "Can you help me with a billing dispute?"
    ]

    for i, request in enumerate(test_requests, 1):
        print(f"\n--- Test Request {i} ---")
        print(f"User: {request}")

        # Run workflow and capture routing decision
        # Run workflow (fresh instance) and capture the routing decision
        wf = build_workflow()
        events = await drain_events(wf.run(request, stream=True, include_status_events=True))

        # Analyze which agent was activated
        routed = False
        for message in collect_output_messages(events):
            name = message.author_name or message.role
            if name == "customer_support_agent" and message.text.strip():
                print(f"Support Agent: {message.text[:100]}...")
            elif name in ("booking_agent", "disputes_agent", "trip_check_agent"):
                agent_type = {
                    "booking_agent": "🛫 BOOKING SPECIALIST",
                    "disputes_agent": "💰 DISPUTES SPECIALIST",
                    "trip_check_agent": "🎯 TRIP CHECK SPECIALIST",
                }[name]
                print(f"Routed to: {agent_type}")
                routed = True
                break
        if not routed:
            print("(No specialist routing detected for this request.)")
    display(HTML("""
    <div style='padding: 25px; background: linear-gradient(135deg, #9c27b0 0%, #673ab7 100%); color: white; border-radius: 12px; 
                box-shadow: 0 4px 12px rgba(156,39,176,0.4); margin: 20px 0;'>
        <h2 style='margin: 0 0 20px 0;'>Handoff Analysis Results</h2>
        <div style='background: rgba(255,255,255,0.15); padding: 15px; border-radius: 8px;'>
            <h4 style='margin: 0 0 10px 0;'>Key Observations</h4>
            <ul style='margin: 0; padding-left: 20px; line-height: 1.6;'>
                <li><strong>Dynamic Routing:</strong> Customer support agent analyzes request intent</li>
                <li><strong>Context Preservation:</strong> Full conversation history maintained</li>
                <li><strong>Specialist Focus:</strong> Each agent handles their expertise area</li>
                <li><strong>Seamless Handoff:</strong> Users don't need to repeat information</li>
            </ul>
        </div>
    </div>
    """))

    # Run the analysis
await analyze_handoff_patterns()
```


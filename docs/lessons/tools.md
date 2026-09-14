---
title: "工具调用"
description: "让模型提出请求，让应用安全地执行。"
course: "tools"
prev: {"text": "Agent 设计模式", "link": "/lessons/design-patterns"}
next: {"text": "Agentic RAG", "link": "/lessons/rag"}
---

# 工具调用

::: tip 本章目标
读懂工具 Schema、调用 ID、参数与结果；能解释模型提出请求之后应用还必须完成哪些步骤。
:::

前置：[Agent 入门](./introduction.md)、[Python 基础](/guide/python.md)。函数是一段可重复执行的代码；Schema 是描述它如何使用的“数据格式说明书”。

## 补充讲解：查询空位，为什么不能只问模型

“东京还有几个名额？”需要实时或业务数据。模型收到工具名、用途与参数类型后，可以返回 `check_availability(destination="Tokyo")` 的 **请求数据** 。只有你的程序实际调用查询函数，库存系统才被读取。

![工具调用时序：用户、应用、模型和工具的职责分离](/diagrams/tool-sequence.svg)

*图：补充绘制。模型请求、应用执行、工具结果和最终回答是四种不同对象。*

<StepDemo kind="tools" />

演示中的库存和模型请求都是预设的。失败场景展示应用拒绝非法参数；它不是让模型自己判断是否应该绕过校验。


::: info 原课程代码片段的阅读范围
下方精读保留上游主要知识与片段，可能包含历史 SDK 写法、示意端点及未完整定义的函数；这些片段不等同于经过本站验证的完整程序。运行前优先阅读本章实际 Notebook 导读与版本校订。已验证的无 API 实验在“扩展实践”中另行标明。
:::

[原课程视频：如何设计优秀的 AI Agent](https://youtu.be/vieRiPRx-gI?si=cEZ8ApnT6Sus9rhn)


## 原课程精读：工具使用设计模式

工具很有趣，因为它们让 AI Agent 拥有了更广泛的能力范围。Agent 不再局限于执行一组有限的动作，而是通过添加工具，可以执行更广泛的操作。本章将介绍工具使用设计模式，阐述 AI Agent 如何利用特定工具来实现其目标。

## 引言

在本课中，我们将解答以下问题：

- 什么是工具使用设计模式？
- 它适用的场景有哪些？
- 实现该设计模式需要哪些要素或构建模块？
- 在使用工具使用设计模式构建可信 AI Agent 时有哪些特别的注意事项？

## 学习目标

完成本课后，你将能够：

- 定义工具使用设计模式及其目的。
- 识别工具使用设计模式适用的使用场景。
- 了解实现该设计模式所需的关键元素。
- 认识确保使用该设计模式的 AI Agent 可信度的考虑因素。

## 什么是工具使用设计模式？

 **工具使用设计模式** 着重于赋予大语言模型（LLM）与外部工具交互以实现特定目标的能力。工具是 Agent 可以执行的代码，用以完成操作。工具可以是简单的函数，比如计算器，或是调用第三方服务的 API，如股票价格查询或天气预报。在 AI Agent 的语境中，工具设计为由 Agent 执行，以响应 **模型生成的函数调用** 。

## 它适用于哪些用例？

AI Agent 可以利用工具完成复杂任务、获取信息或做出决策。工具使用设计模式常用在需要与外部系统（如数据库、网络服务或代码解释器）动态交互的场景。该功能适用于多种用例，包括：

- **动态信息检索：** Agent 可以查询外部 API 或数据库以获取最新数据（例如，查询 SQLite 数据库进行数据分析、获取股票价格或天气信息）。
- **代码执行与解释：** Agent 可以执行代码或脚本来解决数学问题、生成报告或进行模拟。
- **工作流自动化：** 通过集成任务调度器、邮件服务或数据流水线等工具，自动化重复或多步骤的工作流程。
- **客户支持：** Agent 可以与 CRM 系统、票务平台或知识库交互以解决用户查询。
- **内容生成与编辑：** Agent 可以利用语法检查器、文本摘要工具或内容安全评估器等工具协助内容创作。

## 实现工具使用设计模式所需的元素/构建块有哪些？

这些构建块使 AI Agent 能够执行多种任务。让我们看看实现工具使用设计模式所需的关键元素：

- **函数/工具 Schema** ：对可用工具的详细定义，包括函数名、用途、必需参数和预期输出。这些 Schema 使 LLM 理解有哪些工具以及如何构造有效请求。

- **函数执行逻辑** ：管理基于用户意图和对话上下文何时以及如何调用工具。可能包含规划模块、路由机制或决定工具使用的条件流程。

- **消息处理系统** ：管理用户输入、LLM 响应、工具调用及工具输出之间对话流程的组件。

- **工具集成框架** ：连接 Agent 与各种工具的基础设施，无论是简单函数还是复杂外部服务。

- **错误处理与验证** ：处理工具执行失败、验证参数及管理意外响应的机制。

- **状态管理** ：跟踪对话上下文、之前的工具交互及持久数据，确保多轮交互的一致性。

接下来，让我们详细了解函数/工具调用。
 
### 函数/工具调用

函数调用是让大语言模型（LLM）与工具交互的主要方式。你会发现“函数”和“工具”常被互换使用，因为“函数”（可重用的代码块）即是 Agent 用来执行任务的“工具”。为了调用函数代码，LLM 必须将用户请求与函数描述进行匹配。为此，将包含所有可用函数描述的 Schema 发送给 LLM。LLM 然后选择最合适的函数，返回函数名称及参数。所选函数被调用，其响应返回给 LLM，LLM 利用这些信息回应用户请求。

为了实现 Agent 的函数调用，开发者需要：

1. 支持函数调用的 LLM 模型
2. 包含函数描述的 Schema
3. 为每个描述的函数编写代码

让我们用获取某城市当前时间的例子说明：

1. **初始化支持函数调用的 LLM：** 

    并非所有模型都支持函数调用，因此需要确认使用的 LLM 是否支持。[Azure OpenAI](https://learn.microsoft.com/azure/ai-services/openai/how-to/function-calling) 支持函数调用。我们可以通过调用 Azure OpenAI **Responses API** （稳定的 `/openai/v1/` 端点，无需 `api_version`）来启动 OpenAI 客户端。

    ```python
    # Initialize the OpenAI client for Azure OpenAI (Responses API, v1 endpoint)
    client = OpenAI(
        base_url=f"{os.environ['AZURE_OPENAI_ENDPOINT'].rstrip('/')}/openai/v1/",
        api_key=os.environ["AZURE_OPENAI_API_KEY"],
    )
    deployment_name = os.environ["AZURE_OPENAI_DEPLOYMENT"]
    ```

1. **创建函数 Schema：** 

    接下来定义一个 JSON Schema，包含函数名称、功能描述以及函数参数的名称和说明。
    然后将该 Schema 与请求查询旧金山时间的用户请求一起传递给之前创建的客户端。重要的是，返回的是 **工具调用** ，而 **非问题的最终答案** 。如前所述，LLM 返回为任务选中的函数名称和将传递给它的参数。

    ```python
    # Function description for the model to read (Responses API flat tool format)
    tools = [
        {
            "type": "function",
            "name": "get_current_time",
            "description": "Get the current time in a given location",
            "parameters": {
                "type": "object",
                "properties": {
                    "location": {
                        "type": "string",
                        "description": "The city name, e.g. San Francisco",
                    },
                },
                "required": ["location"],
            },
        }
    ]
    ```
   
    ```python
  
    # Initial user message
    messages = [{"role": "user", "content": "What's the current time in San Francisco"}]

    # First API call: Ask the model to use the function
    response = client.responses.create(
        model=deployment_name,
        input=messages,
        tools=tools,
        tool_choice="auto",
        store=False,
    )

    # The Responses API returns tool calls as function_call items in response.output.
    # Append them to the conversation so the model has full context on the next turn.
    messages += response.output

    print("Model's response:")
    print(response.output)
  
    ```

    ```bash
    Model's response:
    [ResponseFunctionToolCall(arguments='{"location":"San Francisco"}', call_id='call_pOsKdUlqvdyttYB67MOj434b', name='get_current_time', type='function_call')]
    ```
  
1. **执行任务所需的函数代码：** 

    既然 LLM 已选定需调用的函数，需要实现并执行完成任务的代码。
    我们用 Python 实现获取当前时间的代码。同样还需要编写代码来从 response_message 中提取函数名和参数，以获得最终结果。

    ```python
      def get_current_time(location):
        """Get the current time for a given location"""
        print(f"get_current_time called with location: {location}")  
        location_lower = location.lower()
        
        for key, timezone in TIMEZONE_DATA.items():
            if key in location_lower:
                print(f"Timezone found for {key}")  
                current_time = datetime.now(ZoneInfo(timezone)).strftime("%I:%M %p")
                return json.dumps({
                    "location": location,
                    "current_time": current_time
                })
      
        print(f"No timezone data found for {location_lower}")  
        return json.dumps({"location": location, "current_time": "unknown"})
    ```

     ```python
    # Handle function calls
    tool_calls = [item for item in response.output if item.type == "function_call"]
    if tool_calls:
        for tool_call in tool_calls:
            if tool_call.name == "get_current_time":

                function_args = json.loads(tool_call.arguments)

                time_response = get_current_time(
                    location=function_args.get("location")
                )

                # Return the tool result as a function_call_output item
                messages.append({
                    "type": "function_call_output",
                    "call_id": tool_call.call_id,
                    "output": time_response,
                })
    else:
        print("No tool calls were made by the model.")

    # Second API call: Get the final response from the model
    final_response = client.responses.create(
        model=deployment_name,
        input=messages,
        tools=tools,
        store=False,
    )

    return final_response.output_text
     ```

     ```bash
      get_current_time called with location: San Francisco
      Timezone found for san francisco
      The current time in San Francisco is 09:24 AM.
     ```

函数调用是大多数（如果不是全部）Agent 工具使用设计的核心，然而从零实现有时颇具挑战。
正如我们在[课程 2](/lessons/frameworks.md)所学，Agent 框架为我们提供了预构建的构建块以实现工具使用。
 
## 使用 Agent 框架的工具使用示例

以下是使用不同 Agent 框架实现工具使用设计模式的一些示例：

### Microsoft Agent Framework

[Microsoft Agent Framework](https://learn.microsoft.com/azure/ai-services/agents/overview) 是用于构建 AI Agent 的开源 AI 框架。它通过允许你用 `@tool` 装饰器将工具定义为 Python 函数，简化了函数调用的过程。该框架处理模型与代码之间的双向通信。同时，`FoundryChatClient` 还提供了预构建工具，如文件搜索和代码解释器。

下图说明了 Microsoft Agent Framework中函数调用的流程：

![函数调用](/upstream-assets/translated_images/zh-CN/functioncalling-diagram.a84006fc287f6014.webp)

*图：函数调用。来源：Microsoft AI Agents for Beginners，MIT。*

在 Microsoft Agent Framework中，工具定义为被装饰的函数。我们可以将之前看到的 `get_current_time` 函数用 `@tool` 装饰器转换为工具。框架会自动序列化该函数及其参数，创建发送给 LLM 的 Schema。

```python
import os
from agent_framework import tool
from agent_framework.foundry import FoundryChatClient
from azure.identity import AzureCliCredential

@tool(approval_mode="never_require")
def get_current_time(location: str) -> str:
    """Get the current time for a given location"""
    ...

# Create the client
provider = FoundryChatClient(
    project_endpoint=os.environ["AZURE_AI_PROJECT_ENDPOINT"],
    model=os.environ["AZURE_AI_MODEL_DEPLOYMENT_NAME"],
    credential=AzureCliCredential(),
)

# Create an agent and run with the tool
agent = provider.as_agent(name="TimeAgent", instructions="Use available tools to answer questions.", tools=get_current_time)
response = await agent.run("What time is it?")
```
  
### Microsoft Foundry Agent Service

[Microsoft Foundry Agent Service](https://learn.microsoft.com/azure/ai-services/agents/overview) 是一个较新的 Agent 框架，旨在帮助开发者安全地构建、部署和扩展高质量且可扩展的 AI Agent，而无需管理底层计算与存储资源。对企业应用尤其有用，因为它是完全托管的服务，具备企业级安全性。

与直接使用 LLM API 开发相比，Microsoft Foundry Agent Service提供了以下优势：

- 自动工具调用—无需解析工具调用、调用工具及处理响应；所有这些操作均在服务器端完成
- 安全管理数据—无需自行管理对话状态，可依赖线程保存所有所需信息
- 开箱即用的工具—可用于交互数据源的工具，例如 Bing、Azure AI 搜索和 Azure Functions

Microsoft Foundry Agent Service中的工具可分为两类：

1. 知识工具：
    - [基于 Bing 搜索的落地工具](https://learn.microsoft.com/azure/ai-services/agents/how-to/tools/bing-grounding?tabs=python&pivots=overview)
    - [文件搜索](https://learn.microsoft.com/azure/ai-services/agents/how-to/tools/file-search?tabs=python&pivots=overview)
    - [Azure AI 搜索](https://learn.microsoft.com/azure/ai-services/agents/how-to/tools/azure-ai-search?tabs=azurecli%2Cpython&pivots=overview-azure-ai-search)

2. 操作工具：
    - [函数调用](https://learn.microsoft.com/azure/ai-services/agents/how-to/tools/function-calling?tabs=python&pivots=overview)
    - [代码解释器](https://learn.microsoft.com/azure/ai-services/agents/how-to/tools/code-interpreter?tabs=python&pivots=overview)
    - [OpenAPI 定义的工具](https://learn.microsoft.com/azure/ai-services/agents/how-to/tools/openapi-spec?tabs=python&pivots=overview)
    - [Azure Functions](https://learn.microsoft.com/azure/ai-services/agents/how-to/tools/azure-functions?pivots=overview)

该 Agent 服务允许我们将这些工具作为 `工具集` 一起使用。同时它利用 `线程` 来跟踪特定对话的消息历史。

假设你是 Contoso 公司的销售 Agent，想开发一个能回答销售数据相关问题的对话 Agent。

下图展示了如何使用 Microsoft Foundry Agent Service分析销售数据：

![Agent 服务实操](/upstream-assets/translated_images/zh-CN/agent-service-in-action.34fb465c9a84659e.webp)

*图：Agent 服务实操。来源：Microsoft AI Agents for Beginners，MIT。*

要使用服务中的任何工具，我们可以创建客户端并定义单个工具或工具集。下面的 Python 代码演示了这一实现。LLM 将能够查看工具集，并根据用户请求决定是使用用户创建的函数 `fetch_sales_data_using_sqlite_query` 还是预构建的代码解释器。

```python 
import os
from azure.ai.projects import AIProjectClient
from azure.identity import DefaultAzureCredential
from fetch_sales_data_functions import fetch_sales_data_using_sqlite_query # fetch_sales_data_using_sqlite_query function which can be found in a fetch_sales_data_functions.py file.
from azure.ai.projects.models import ToolSet, FunctionTool, CodeInterpreterTool

project_client = AIProjectClient.from_connection_string(
    credential=DefaultAzureCredential(),
    conn_str=os.environ["PROJECT_CONNECTION_STRING"],
)

# Initialize toolset
toolset = ToolSet()

# Initialize function calling agent with the fetch_sales_data_using_sqlite_query function and adding it to the toolset
fetch_data_function = FunctionTool(fetch_sales_data_using_sqlite_query)
toolset.add(fetch_data_function)

# Initialize Code Interpreter tool and adding it to the toolset. 
code_interpreter = CodeInterpreterTool()toolset.add(code_interpreter)

agent = project_client.agents.create_agent(
    model="gpt-5-mini", name="my-agent", instructions="You are helpful agent", 
    toolset=toolset
)
```

## 使用工具使用设计模式构建可信 AI Agent 的特别注意事项？

一个常见的安全问题是 LLM 动态生成的 SQL，特别是存在 SQL 注入或恶意操作（如删除或篡改数据库）的风险。虽然这些担忧合理，但通过正确配置数据库访问权限可以有效避免。对大多数数据库来说，这意味着配置为只读。对于 PostgreSQL 或 Azure SQL 等数据库服务，应为应用分配只读（SELECT）角色。

在安全环境中运行应用进一步增强了保护。在企业场景中，数据通常从业务系统中提取并转换到只读的数据库或数据仓库，并采用友好的 Schema。这保证了数据安全、性能及可访问性的优化，并且应用权限仅限于只读。

## 示例代码

- Python: [Agent Framework](/labs/04-tool-use-code-samples-04-python-agent-framework-notebook.md)
- .NET: [Agent Framework](/labs/04-tool-use-code-samples-04-dotnet-agent-framework-notes.md)

## 额外资源

- [Azure AI Agents Service 工作坊](https://microsoft.github.io/build-your-first-agent-with-azure-ai-agent-service-workshop/)
- [Contoso 创意写作多 Agent 工作坊](https://github.com/Azure-Samples/contoso-creative-writer/tree/main/docs/workshop)
- [Microsoft Agent Framework概览](https://learn.microsoft.com/azure/ai-services/agents/overview)


## 这个 Agent 的冒烟测试（可选）

在学习了如何部署 Agent（参见[第16课](/lessons/deployment.md)）后，你可以用[`tests/lesson-04-smoke-tests.json`](https://github.com/microsoft/ai-agents-for-beginners/blob/25b7985f3b2dc37a84f4a7387ccd3c9f0e5b1595/tests/lesson-04-smoke-tests.json)对本课的`TravelToolAgent`进行冒烟测试（它是否仍然调用其工具并作出回答？）。有关如何运行它，请参见[`tests/README.md`](https://github.com/microsoft/ai-agents-for-beginners/blob/25b7985f3b2dc37a84f4a7387ccd3c9f0e5b1595/tests/README.md)。

## 代码实操：阅读旅行工具集

原 `04-python-agent-framework.ipynb` 定义目的地、可用性和航班三个读取工具，再创建 `TravelToolAgent`。依赖和 Foundry 配置按[准备篇](./setup.md)，完整代码与运行入口见本章下方导读。查询价格是固定示例数据，不是实时旅行报价；真实模型调用未实测。

- `Annotated[str, ...]` 提供参数说明；实际机场代码是否存在仍要程序验证。
- `tools=travel_tools` 是模型能看到的工具集合；不要注册一个任意运行 shell 的函数替代所有业务工具。
- `book_flight` 使用 `approval_mode="always_require"`。Notebook 最后只打印该工具的名称与审批模式，没有演示完整批准与恢复，所以不能据此认为已完成真实预订。
- `BookingRecommendation` / `TravelPlan` 定义了类型，但本课该次 `run()` **没有传入** 响应格式；其回答不能当作自动验证通过的结构化对象。第 7 章实际使用 `options={"response_format": TravelPlan}`，可对照两者。

## 扩展实践：明确拒绝，再允许一个本地动作

项目的最终示例提供真实运行的应用校验：

```bash
python3 examples/assistant/app.py '创建任务：复习工具调用' --stage 2
python3 examples/assistant/app.py '创建任务：复习工具调用' --stage 2 --approve --request-id tool-01
```

第一次应返回 `APPROVAL_REQUIRED`，第二次产生本地任务 ID。重复第二条不应新建第二份任务。文件 `app.py` 中 `Executor.execute` 先检查白名单、参数集合、字段类型和授权，再调用 `Store.create_task`。`request_id` 用来表示同一个逻辑请求，不是随每次重试重新生成。

## 出错怎么办

| 现象 | 定位 | 处理 |
| --- | --- | --- |
| 工具名称不存在 | 模型返回未注册名称 | 白名单拒绝，返回结构化错误，不用 eval 动态执行 |
| 参数看似 JSON 但类型错 | 只有解析、没有类型验证 | 检查必填项、枚举、范围和额外字段 |
| 工具超时后重复下单 | 重试没有幂等保护 | 相同逻辑请求复用 ID，查询实际执行状态再决定 |
| SQL 查询能删除表 | 数据库身份过宽 | 只读账号、允许的表与查询形态；参数化过滤条件 |

只读权限降低破坏风险，却不能阻止读取本无权查看的个人记录。业务范围过滤和身份验证仍需在工具服务执行。

## 自测与练习

一个工具返回 `{"ok":false,"error":"timeout"}`，模型说“处理完成”。应用应信谁？

::: details 答案
以实际执行结果和业务状态为准。应把超时表示为未确认或失败；若操作可能已经提交，先查询状态，不能直接重试产生副作用，也不能展示完成。
:::

 **练习：** 向 `Executor.execute` 传入 `search_docs` 与多余的 `admin=true` 字段。参考验收为抛出 `INVALID_ARGUMENT`，工具计数不增加；已提供 `test_unknown_tool_and_argument_validation`。

本章让行动经过执行边界。下一章把检索做成工具，让回答拥有可核对的证据。


## 原课程代码与补充材料

以下是本章实际源文件对应的阅读页。Notebook 已分解为说明、代码及原文件输出；云端示例未进行联网端到端验证。正文中的片段用于解释，运行时使用完整 Notebook 和准备篇的固定依赖。

- [04-python-agent-framework.ipynb](/labs/04-tool-use-code-samples-04-python-agent-framework-notebook.md)
- [04-dotnet-agent-framework.md](/labs/04-tool-use-code-samples-04-dotnet-agent-framework-notes.md)
- [test_demo_plugins.py](/labs/04-tool-use-code-samples-test-demo-plugins-script.md)
- [04-dotnet-agent-framework.cs](/labs/04-tool-use-code-samples-04-dotnet-agent-framework-csharp.md)

## 本章来源

基于 [英文原文](https://github.com/microsoft/ai-agents-for-beginners/blob/25b7985f3b2dc37a84f4a7387ccd3c9f0e5b1595/04-tool-use/README.md) 与 [简体中文翻译](https://github.com/microsoft/ai-agents-for-beginners/blob/25b7985f3b2dc37a84f4a7387ccd3c9f0e5b1595/translations/zh-CN/04-tool-use/README.md) 整理，原作者为 Microsoft 与开源贡献者，采用 MIT 许可证。本页标明“补充讲解”与“扩展实践”的内容为本项目新增。

来源提交：`25b7985f3b2d` · 获取日期：2026-09-14。参见[版本校订记录](/guide/sources.md)。

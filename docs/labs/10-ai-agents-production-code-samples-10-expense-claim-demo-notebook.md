---
title: "10 · 10-expense_claim-demo"
outline: [2, 3]
---

# 10 · 10-expense_claim-demo

[返回：Agent 生产实践](/lessons/production.md) · [不可变原始文件](https://github.com/microsoft/ai-agents-for-beginners/blob/25b7985f3b2dc37a84f4a7387ccd3c9f0e5b1595/10-ai-agents-production/code_samples/10-expense_claim-demo.ipynb)

::: warning 原课程完整 Notebook · 静态阅读与代码解析
代码按英文源文件顺序保留，中文说明以同版本译本为基础。原始安装单元格可能含无版本上限的 `-U`；请跳过它们，先按[准备篇](/lessons/setup.md)固定依赖。云端服务、模型权限、网站布局和部分 SDK 接口需在你自己的环境验证。本站没有执行云端请求；第 18 章的离线验证状态单独记录在[检查报告](/guide/verification.md)。
:::

## 运行准备

Python 3.12+；在独立虚拟环境安装源仓库依赖与本页中声明的额外依赖。原文件路径：`upstream/10-ai-agents-production/code_samples/10-expense_claim-demo.ipynb`。以原仓库根目录为工作目录，在 Jupyter 中按顺序执行；身份与环境变量见准备篇。

```bash
cd upstream
python -m jupyterlab
```

[下载原始 Notebook](/notebooks/10-ai-agents-production/code_samples/10-expense_claim-demo.ipynb)。输出为上游文件保存的历史结果，不能用作本站实测证明。

## 费用报销分析

本笔记本演示了如何创建使用插件的 Agent，以处理来自本地收据图像的差旅费用，生成费用报销邮件，并使用饼图可视化费用数据。Agent 根据任务上下文动态选择函数。

步骤：
1. OCRAgent 处理本地收据图像并提取差旅费用数据。
2. 邮件 Agent 生成费用报销邮件。

### 差旅费用场景示例：
假设你是一名为参加另一城市的商务会议而出差的员工。贵公司有一项政策，报销所有合理的与差旅相关的费用。以下是潜在差旅费用的细目：
- 交通：
从你所在城市往返目的地城市的机票费用。
往返机场的出租车或网约车费用。
目的地城市内的本地交通（如公共交通、租车或出租车）。

- 住宿：
在会议场所附近的中档商务酒店住宿三晚。

- 餐饮：
按公司每日津贴政策提供的早餐、午餐和晚餐的每日餐费补助。

- 杂项费用：
机场停车费。
酒店的上网费用。
小费或小额服务费。

- 资料：
你提交所有收据（机票、出租车、酒店、餐饮等）及完整的费用报销单进行报销。

## 导入所需库

导入笔记本所需的库和模块。

### 代码单元格 3

配置加载：从本地环境读取端点与部署名；缺少变量时先修复配置，不要把密钥写进代码。

数据结构：Pydantic 模型定义字段类型；只有传入实际的 response_format 并检查解析结果，才能约束本次输出。

模型连接：project_endpoint 是项目地址，model 是实际部署名称；credential 提供访问身份。客户端创建本身不证明已经部署服务端 Agent。

```python
import logging
logging.getLogger("agent_framework.foundry").setLevel(logging.ERROR)

import os
import dotenv
from typing import Annotated, List

from pydantic import BaseModel, Field

from agent_framework import Content, Message, tool, AgentResponseUpdate, WorkflowBuilder
from agent_framework.foundry import FoundryChatClient
from azure.identity import DefaultAzureCredential

dotenv.load_dotenv()

endpoint = os.getenv("AZURE_AI_PROJECT_ENDPOINT")
deployment_name = os.getenv("AZURE_AI_MODEL_DEPLOYMENT_NAME")

missing = [k for k, v in {
    "AZURE_AI_PROJECT_ENDPOINT": endpoint,
    "AZURE_AI_MODEL_DEPLOYMENT_NAME": deployment_name
}.items() if not v]

if missing:
    raise ValueError(
        f"Missing required environment variables: {', '.join(missing)}. "
        "Please set them as environment variables (e.g., in your .env file or shell environment)."
    )
```

### 代码单元格 4

模型连接：project_endpoint 是项目地址，model 是实际部署名称；credential 提供访问身份。客户端创建本身不证明已经部署服务端 Agent。

```python
# Create the Microsoft Foundry client
client = FoundryChatClient(
    project_endpoint=endpoint,
    model=deployment_name,
    credential=DefaultAzureCredential()
)
```

## 定义费用模型

 创建一个用于单个费用的 Pydantic 模型和一个 ExpenseFormatter 类，用于将用户查询转换为结构化费用数据。

 每笔费用将以如下格式表示：
 `{'date': '07-Mar-2025', 'description': 'flight to destination', 'amount': 675.99, 'category': 'Transportation'}`

### 代码单元格 6

数据结构：Pydantic 模型定义字段类型；只有传入实际的 response_format 并检查解析结果，才能约束本次输出。

输出观察：print 展示应用可观察结果；预存输出和现场结果可能不同，它不是模型内部思考记录。

```python
class Expense(BaseModel):
    date: str = Field(..., description="Date of expense in dd-MMM-yyyy format")
    description: str = Field(..., description="Expense description")
    amount: float = Field(..., description="Expense amount")
    category: str = Field(..., description="Expense category (e.g., Transportation, Meals, Accommodation, Miscellaneous)")

class ExpenseFormatter(BaseModel):
    raw_query: str = Field(..., description="Raw query input containing expense details")
    
    def parse_expenses(self) -> List[Expense]:
        """
        Parses the raw query into a list of Expense objects.
        Expected format: "date|description|amount|category" separated by semicolons.
        """
        expense_list = []
        for expense_str in self.raw_query.split(";"):
            if expense_str.strip():
                parts = expense_str.strip().split("|")
                if len(parts) == 4:
                    date, description, amount, category = parts
                    try:
                        expense = Expense(
                            date=date.strip(),
                            description=description.strip(),
                            amount=float(amount.strip()),
                            category=category.strip()
                        )
                        expense_list.append(expense)
                    except ValueError as e:
                        print(f"[LOG] Parse Error: Invalid data in '{expense_str}': {e}")
        return expense_list
```

## 定义工具 - 生成电子邮件

创建一个工具函数，用于生成提交报销申请的电子邮件。
- 此工具使用 Microsoft Agent Framework 中的 `@tool` 装饰器。
- 它计算费用总金额并将详情格式化为电子邮件正文。

### 代码单元格 8

工具定义：类型注解和文档字符串描述输入、用途；模型产生调用请求，框架在应用进程中执行函数。检查是否需要人工批准。

```python
@tool(approval_mode="never_require")
def generate_expense_email(
    expense_data: Annotated[str, "Semicolon-separated expense entries in 'date|description|amount|category' format"]
) -> str:
    """Generate an email to submit an expense claim to the Finance Team."""
    formatter = ExpenseFormatter(raw_query=expense_data)
    expenses = formatter.parse_expenses()
    if not expenses:
        return "No valid expenses found to include in the email."
    total_amount = sum(e.amount for e in expenses)
    email_body = "Dear Finance Team,\n\n"
    email_body += "Please find below the details of my expense claim:\n\n"
    for e in expenses:
        email_body += f"- {e.date} | {e.description}: ${e.amount:.2f} ({e.category})\n"
    email_body += f"\nTotal Amount: ${total_amount:.2f}\n\n"
    email_body += "Receipts for all expenses are attached for your reference.\n\n"
    email_body += "Thank you,\n[Your Name]"
    return email_body
```

## 用于从收据图片中提取差旅费用的工具

创建一个工具函数，从收据图片中提取差旅费用。
- 该工具使用 Microsoft Agent Framework 中的 `@tool` 装饰器。
- 它读取收据图片，将其编码为 base64，并返回数据 URI 以供 Agent 分析。

### 代码单元格 10

阅读提示：跟踪本单元格读取的变量、修改的状态以及返回值。按原顺序执行，确认依赖的前序变量已经存在。

```python
def load_receipt_image(image_path: str = "receipt.jpg") -> Content:
    """Load a receipt image as native multimodal content."""
    with open(image_path, "rb") as f:
        image_bytes = f.read()
    return Content.from_data(image_bytes, "image/jpeg")
```

## 处理费用

使用 `WorkflowBuilder` 定义 Agent 并将它们连接成一个顺序工作流。
- OCRAgent 使用 `load_receipt_image` 工具从收据图像中提取结构化费用数据。
- 邮件 Agent 使用 `generate_expense_email` 工具将提取的数据生成专业的费用报销邮件。
- 通过 `add_edge` 的 `WorkflowBuilder` 创建一个顺序管道：OCRAgent → 邮件 Agent。

### 代码单元格 12

行为约束：instructions 引导模型，不能替代执行器的权限验证、次数限制和结果检查。

```python
ocr_agent = client.as_agent(
    name="OCRAgent",
    instructions=(
        "You are an expert OCR assistant specialized in extracting structured data from receipt images. "
        "Analyze the receipt image supplied in the user message and extract "
        "travel-related expense details in the format: 'date|description|amount|category' separated by semicolons. "
        "Follow these rules: "
        "- Date: Convert dates (e.g., '4/4/22') to 'dd-MMM-yyyy' (e.g., '04-Apr-2022'). "
        "- Description: Extract item names. "
        "- Amount: Use numeric values (e.g., '4.50' from '$4.50'). "
        "- Category: Infer from context (e.g., 'Meals' for food, 'Transportation' for travel, "
        "'Accommodation' for lodging, 'Miscellaneous' otherwise). "
        "Ignore totals, subtotals, or service charges unless they are itemized expenses. "
        "If no expenses are found, return 'No expenses detected'. "
        "Return only the structured data, no additional text."
    ),
)

email_agent = client.as_agent(
    name="EmailAgent",
    tools=[generate_expense_email],
    instructions=(
        "You are an expense claim email generator. Take the travel expense data from the previous agent "
        "(in 'date|description|amount|category' format separated by semicolons) and use the "
        "'generate_expense_email' tool to produce a professional expense claim email. "
        "Pass the semicolon-separated expense data directly to the tool."
    ),
)
```

## 主函数

构建顺序工作流并运行它，以处理收据图像并生成报销邮件。

> **注意：** 此工作流当前将收据图像作为 base64 文本传递，大多数聊天模型（包括 gpt-5-mini）不会将其视为图像。
> 图像大小可能还会超过模型的上下文窗口。建议使用 Azure AI Vision（或其他 OCR 工具）运行 OCR，并仅传递提取的文本，或重构为将图像作为 `image_url` 消息发送。
> 如果你只是想避免上下文错误，可以尝试使用更小的收据图像或具有更大上下文窗口的模型。

### 代码单元格 15

输出观察：print 展示应用可观察结果；预存输出和现场结果可能不同，它不是模型内部思考记录。

```python
workflow = WorkflowBuilder(start_executor=ocr_agent) \
    .add_edge(ocr_agent, email_agent) \
    .build()

prompt = (
    "Please extract the raw text from the receipt image at 'receipt.jpg', "
    "focusing on travel expenses like dates, descriptions, amounts, and categories "
    "(e.g., Transportation, Accommodation, Meals, Miscellaneous). "
    "Then generate a professional expense claim email."
)

last_author = None
receipt_message = Message(
    role="user",
    contents=[prompt, load_receipt_image("receipt.jpg")],
)

events = workflow.run(
    receipt_message,
    stream=True,
)
async for event in events:
    if event.type == "output" and isinstance(event.data, AgentResponseUpdate):
        update = event.data
        author = update.author_name
        if author != last_author:
            if last_author is not None:
                print()
            print(f"\n{'='*50}")
            print(f"# Agent - {author}:")
            print(f"{'='*50}")
            last_author = author
        print(update.text, end="", flush=True)
```


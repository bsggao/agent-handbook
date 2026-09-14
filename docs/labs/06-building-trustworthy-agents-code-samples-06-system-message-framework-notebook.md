---
title: "06 · 06-system-message-framework"
outline: [2, 3]
---

# 06 · 06-system-message-framework

[返回：构建可信赖的 Agent](/lessons/trust.md) · [不可变原始文件](https://github.com/microsoft/ai-agents-for-beginners/blob/25b7985f3b2dc37a84f4a7387ccd3c9f0e5b1595/06-building-trustworthy-agents/code_samples/06-system-message-framework.ipynb)

::: warning 原课程完整 Notebook · 静态阅读与代码解析
代码按英文源文件顺序保留，中文说明以同版本译本为基础。原始安装单元格可能含无版本上限的 `-U`；请跳过它们，先按[准备篇](/lessons/setup.md)固定依赖。云端服务、模型权限、网站布局和部分 SDK 接口需在你自己的环境验证。本站没有执行云端请求；第 18 章的离线验证状态单独记录在[检查报告](/guide/verification.md)。
:::

## 运行准备

Python 3.12+；在独立虚拟环境安装源仓库依赖与本页中声明的额外依赖。原文件路径：`upstream/06-building-trustworthy-agents/code_samples/06-system-message-framework.ipynb`。以原仓库根目录为工作目录，在 Jupyter 中按顺序执行；身份与环境变量见准备篇。

```bash
cd upstream
python -m jupyterlab
```

[下载原始 Notebook](/notebooks/06-building-trustworthy-agents/code_samples/06-system-message-framework.ipynb)。输出为上游文件保存的历史结果，不能用作本站实测证明。

### 代码单元格 1

配置加载：从本地环境读取端点与部署名；缺少变量时先修复配置，不要把密钥写进代码。

```python
import os
from dotenv import load_dotenv

load_dotenv()

from azure.identity import DefaultAzureCredential, get_bearer_token_provider
from openai import OpenAI

# This sample uses the Azure OpenAI Responses API via the stable /openai/v1/ endpoint.
# GitHub Models is deprecated (retiring July 2026) and does not support the Responses API,
# so we call Azure OpenAI directly instead.
endpoint = os.environ["AZURE_OPENAI_ENDPOINT"]
deployment = os.environ["AZURE_OPENAI_DEPLOYMENT"]
```

### 代码单元格 2

阅读提示：跟踪本单元格读取的变量、修改的状态以及返回值。按原顺序执行，确认依赖的前序变量已经存在。

```python
# Authenticate with Entra ID (run `az login` first). No API version is needed with the v1 endpoint.
token_provider = get_bearer_token_provider(
    DefaultAzureCredential(),
    "https://cognitiveservices.azure.com/.default",
)

client = OpenAI(
    base_url=f"{endpoint.rstrip('/')}/openai/v1/",
    api_key=token_provider,
)
```

### 代码单元格 3

阅读提示：跟踪本单元格读取的变量、修改的状态以及返回值。按原顺序执行，确认依赖的前序变量已经存在。

```python
role = "travel agent"
company = "contoso travel"
responsibility = "booking flights"
```

### 代码单元格 4

输出观察：print 展示应用可观察结果；预存输出和现场结果可能不同，它不是模型内部思考记录。

```python
response = client.responses.create(
    model=deployment,
    input=[
        {"role": "system", "content": """You are an expert at creating AI agent assistants. 
You will be provided a company name, role, responsibilities and other
information that you will use to provide a system prompt for.
To create the system prompt, be descriptive as possible and provide a structure that a system using an LLM can better understand the role and responsibilities of the AI assistant."""},
        {"role": "user", "content": f"You are {role} at {company} that is responsible for {responsibility}."},
    ],
    # Optional parameters
    temperature=1.0,
    max_output_tokens=1000,
    top_p=1.0,
    store=False,
)

print(response.output_text)
```


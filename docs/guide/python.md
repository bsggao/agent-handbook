---
title: Python 阅读小抄
description: Python 阅读小抄 · AI Agent 中文学习指南
---

# Python 阅读小抄

这份补充讲解只覆盖阅读课程示例最常见的语法。Python 3.12+ 即可运行标准库片段；框架类型还需安装对应依赖。

## 字典、列表与类型注解

```python
result = {"city": "Tokyo", "available": True}
cities = ["Tokyo", "Bali"]
def check(city: str) -> dict:
    return {"city": city, "available": city in cities}
print(check("Tokyo"))
```

`dict` 是键值映射，`list` 是有序集合。`True/False/None` 大致对应 JavaScript 的 `true/false/null`，注意大小写。`city: str` 和 `-> dict` 描述预期类型，Python 不会只因这些注解就自动阻止错误参数；框架或应用仍需运行时验证。

`[x for x in items if condition]` 是列表推导式，类似 JS 的 `items.filter(...).map(...)`。先写成普通 `for` 循环也完全可以。

## 缩进、函数与装饰器

Python 用缩进标记代码块，通常四个空格。`@tool` 是装饰器：框架据此把函数签名、说明和执行函数包装成工具。它不会在定义时自动调用函数，也不是给模型执行 Python 的通行证。

`Annotated[str, "目的地名称"]` 为类型附加说明，供 schema 生成使用。`BaseModel` 定义结构化字段；只有实际将类型传给输出格式选项并检查解析结果，才能约束这次响应。

## async、await 与入口

完整标准库示例，保存为 `async_demo.py`，运行 `python3 async_demo.py`：

```python
import asyncio
async def main():
    await asyncio.sleep(0.01)
    print("异步任务已完成")
if __name__ == "__main__":
    asyncio.run(main())
```

`async def` 定义协程，`await` 等待异步结果。Notebook 通常支持顶层 `await`；普通脚本不能把 Notebook 的 `await agent.run(...)` 原样放在文件顶层。异步不自动意味着多角色并行；是否并发取决于调度方式。

## 上下文管理、异常与环境变量

`with` / `async with` 用于进入与退出资源范围，适合连接、文件或客户端清理。`try/except` 处理明确错误，`finally` 负责收尾；不要用空的 `except: pass` 吞掉所有失败。

```python
import os
endpoint = os.environ.get("AZURE_AI_PROJECT_ENDPOINT")
if not endpoint:
    raise ValueError("缺少项目端点，请检查本地环境变量")
```

`.env` 不会凭空加载；`load_dotenv()` 来自 `python-dotenv`。不要打印全部环境变量来排错，其中可能有密钥。网站前端无需读取这些变量。

## Notebook 不等于按段复制的脚本

单元格执行顺序影响变量状态；重启内核后应按顺序运行。`%pip` 是 Notebook 命令，不是 Python 语法；源安装单元格可能升级包，应按本课程准备篇先固定版本。保存输出是历史结果，重新运行可能不同。

遇到 `NameError` 先检查前一个定义单元格；遇到 `ModuleNotFoundError` 检查 Jupyter 内核是不是刚才安装依赖的虚拟环境。更多问题见[排错指南](./faq.md)。

---
title: "04 · test_demo_plugins"
outline: [2, 3]
---

# 04 · test_demo_plugins

[返回：工具调用](/lessons/tools.md) · [不可变原始文件](https://github.com/microsoft/ai-agents-for-beginners/blob/25b7985f3b2dc37a84f4a7387ccd3c9f0e5b1595/04-tool-use/code_samples/test_demo_plugins.py)

::: info 原课程脚本 · 未联网执行
保留原始框架与完整代码。依赖、变量、入口以脚本及其相邻 README 为准；本页为代码导读，未声称所有外部服务均已验证。
:::

输出观察：print 展示应用可观察结果；预存输出和现场结果可能不同，它不是模型内部思考记录。

```python
from demo_tool_agent import TimePlugin, CalculatorPlugin

def test_calculator_add():
    calc = CalculatorPlugin()
    result = calc.add(5, 7)
    assert result == 12
    print("test_calculator_add passed")

def test_calculator_subtract():
    calc = CalculatorPlugin()
    result = calc.subtract(10, 4)
    assert result == 6
    print("test_calculator_subtract passed")

def test_time_plugin():
    # We can't easily test exact time, but we can check format
    time_plugin = TimePlugin()
    time_str = time_plugin.get_current_time()
    # Expect format YYYY-MM-DD HH:MM:SS
    assert len(time_str) == 19
    assert "-" in time_str
    assert ":" in time_str
    print("test_time_plugin passed")

if __name__ == "__main__":
    try:
        test_calculator_add()
        test_calculator_subtract()
        test_time_plugin()
        print("All tests passed!")
    except AssertionError as e:
        print(f"Test failed: {e}")
    except Exception as e:
        print(f"An error occurred: {e}")

```

---
title: "11 · MCP_SETUP"
outline: [2, 3]
---

# 11 · MCP_SETUP

[返回：Agent 协议：MCP、A2A、NLWeb](/lessons/protocols.md) · [不可变原始文件](https://github.com/microsoft/ai-agents-for-beginners/blob/25b7985f3b2dc37a84f4a7387ccd3c9f0e5b1595/11-agentic-protocols/code_samples/github-mcp/MCP_SETUP.md)

::: info 原课程补充材料
根据对应简体中文译本整理。原代码片段未进行云端验证。
:::

# MCP服务器集成指南

## 前置条件
- 已安装Node.js（版本14或更高）
- npm包管理器
- 配置好所需依赖的Python环境

## 设置步骤

1. **安装MCP服务器包** 
   ```bash
   npm install -g @modelcontextprotocol/server-github
   ```

2. **启动MCP服务器** 
   ```bash
   npx @modelcontextprotocol/server-github
   ```  
   服务器应启动并显示一个连接URL。

3. **验证连接** 
   - 在Chainlit界面中寻找插头图标（🔌）  
   - 插头图标旁应显示数字（1），表示连接成功  
   - 控制台应显示：“GitHub插件设置成功完成”（以及其他状态信息）

## 故障排除

### 常见问题

1. **端口冲突** 
   ```bash
   Error: listen EADDRINUSE: address already in use
   ```  
   解决方法：使用以下命令更改端口：  
   ```bash
   npx @modelcontextprotocol/server-github --port 3001
   ```

2. **认证问题** 
   - 确保GitHub凭据配置正确  
   - 检查.env文件是否包含所需的Token  
   - 验证GitHub API访问权限

3. **连接失败** 
   - 确认服务器运行在预期端口上  
   - 检查防火墙设置  
   - 验证Python环境安装了所需的包

## 连接验证

当以下情况满足时，你的MCP服务器已正确连接：  
1. 控制台显示“GitHub插件设置成功完成”  
2. 连接日志显示“✓ MCP连接状态：活跃”  
3. GitHub命令可在聊天界面中正常工作

## 环境变量

在你的.env文件中需要包含以下内容：  
```
GITHUB_TOKEN=your_github_token
MCP_SERVER_PORT=3000  # Optional, default is 3000
```

## 测试连接

在聊天中发送以下测试消息：  
```
Show me the repositories for username: [GitHub Username]
```  
成功的响应将显示仓库信息。

---

 **免责声明** ：  
本文档使用AI翻译服务 [Co-op Translator](https://github.com/Azure/co-op-translator) 进行翻译。尽管我们努力确保翻译的准确性，但请注意，自动翻译可能包含错误或不准确之处。原始语言的文档应被视为权威来源。对于关键信息，建议使用专业人工翻译。我们不对因使用此翻译而产生的任何误解或误读承担责任。
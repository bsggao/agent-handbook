"""Small, explicit source corrections. Never mutate the immutable upstream snapshot."""
import re

def correct(text, source, english=None):
    # Use the actual English code, not translated/escaped Python identifiers or stale algorithms.
    if english:
        ef=re.findall(r'```[\s\S]*?```',english);zf=re.findall(r'```[\s\S]*?```',text)
        if len(ef)==len(zf):
            seq=iter(ef)
            def block(match):
                english_block=next(seq)
                return match[0] if match[0].startswith('```mermaid') else english_block
            text=re.sub(r'```[\s\S]*?```',block,text)
    if '09-metacognition' in source:
        text=re.sub(r'元认知指的是涉及思考自身思维.*?争论。','元认知原指对认知过程的监控与调节。在本课程的工程语境中，指系统根据任务结果、外部反馈与评价规则检查并调整后续行动；这是一种反馈控制设计，不证明模型具有自我意识，也不要求展示隐藏推理。',text,flags=re.S)
        text=re.sub(r'元认知，即“关于思考的思考”.*?自身推理过程。','元认知设计模式让应用显式记录目标、候选方案、评价结果和修订动作。开发者能检查这些输出及其依据；它们与模型内部推理并不是一回事。',text,flags=re.S)
        text=text.replace('基于自我意识和过往经验','基于可观察反馈和历史记录').replace('基于内部反馈调整推理过程','基于检查结果调整下一步策略')
        text=text.replace('请确保将 `your_azure_openai_api_key` 替换为您的真实 Azure OpenAI API 密钥，`https://your-endpoint.com/...` 替换为您 Azure OpenAI 部署的实际端点 URL。','此处 URL 与密钥字符串是历史示意占位符，不是可运行配置。真实实验应通过本地环境变量加载凭据，并按当前所用 SDK 版本构造端点；不要将真实密钥填入正文或提交到代码仓库。')
    if '12-context-engineering' in source:
        text=text.replace('研究表明限制工具少于 30 个更有效。','原文给出少于 30 个工具的经验建议，不能视为通用阈值；应通过具体模型与任务集验证。')
    if '13-agent-memory' in source:
        text=text.replace('与传统的文本分块和嵌入方法相比，它提供“超越人类的精确度和召回率”。','实际精确率与召回率需要在具体数据和任务集上测量，不能保证优于其他检索方式。')
        text=text.replace('使用 Mem0 和 Azure AI Search 结合 Microsoft Agent Framework 实现记忆','实际使用 Python 内存字典与 Microsoft Agent Framework 演示偏好记忆（原 README 对 Mem0 / Azure AI Search 的描述与代码不符）')
        text=re.sub(r'这提供了.*?超人.*?。','准确率和召回率取决于数据、索引与任务，需要实测比较。',text)
        text=re.sub(r'这提供了.*?超越人类.*?。','准确率和召回率取决于数据、索引与任务，需要实测比较。',text)
    if '16-deploying-scalable-agents' in source:
        text=text.replace('生产就绪的客户支持代理','用于理解生产机制的客户支持示例').replace('生产就绪的客户支持 Agent','用于理解生产机制的客户支持示例')
    if '17-creating-local-ai-agents' in source:
        text=text.replace('代码和文档永远不会离开本机。没有任何提示、代码片段或客户数据跨网络边界。','可以把推理与资料处理留在本机；是否存在外传还要检查工具、遥测与混合路由。')
        text=text.replace('停电期间','设备仍有电且依赖已缓存的断网期间').replace('停电时','设备仍有电的断网环境')
        text=text.replace('**8 GB RAM 是实际最低要求**；16 GB 以上更舒适。','上游以 **8 GB RAM** 为实验起点、建议 16 GB 以上；实际需求取决于模型、量化和运行时，不能作为所有硬件的最低保证。')
        text=text.replace('一个前沿云端模型有数千亿参数和数据中心支撑。SLM 有几个亿参数，必须适配你笔记本的内存。','大模型常需要更多计算资源；小语言模型通常参数更少，可选择适合设备内存的量化版本。本例 Qwen 7B 的“7B”指约 70 亿参数，不是几亿。')
        text=text.replace('这意味着 OpenAI SDK 和 Microsoft 代理框架的 OpenAI 客户端只需更改 `base_url` 即可对接。你关于构建代理学到的一切都能直接迁移；唯一变化是端点从云变成了 `localhost`。','本例使用 OpenAI SDK 的 Chat Completions 接口。其他客户端是否可迁移还要核对接口类型、模型工具能力、消息与参数兼容性，不能保证只改 `base_url`。')
        text=text.replace('代理只有能调用工具才是真正的代理。','本课构建的本地代理需要可靠的工具调用能力。')
        text=text.replace('**Qwen** 模型专门训练用于函数调用，稳定输出格式良好的工具调用结构','本课选择的 **Qwen** 模型具有工具调用支持，但输出格式与成功率仍要在所选运行时验证')
        text=text.replace('以隐私、成本和离线操作为代价换取广度','以部分通用能力与设备资源消耗，换取本地处理、离线运行和无按 Token 推理计费的可能')
        text=text.replace('代码和数据永远不离机','可把代码和数据处理留在本机，需另查网络工具').replace('因此您的云端代理代码只需一行改动即可迁移','迁移仍需核对具体 API 与模型能力')
        text=text.replace('OpenAI SDK 和代理框架的 OpenAI 客户端只需修改 `base_url`（并用本地占位 API key）便可使用。代理代码其他部分保持不变。','本例 OpenAI SDK 使用本地 `base_url` 和本地连接参数。其他框架客户端需核对是否使用相同的 Chat Completions 接口，工具能力与参数也要实测。')
        text=text.replace('磁盘上的 Chroma','本例进程内 Chroma；显式持久化后才保存到磁盘').replace('无组件接触云端','推理与检索可以在本地完成；首次模型下载与其他工具的网络行为仍需检查')
        text=text.replace('（Chroma 向量数据库 - 存储在磁盘上）','Chroma 向量数据库：本例为内存模式')
        text=text.replace('（Chroma vector database - on disk）','Chroma vector database - in memory in this sample')
    if '18-securing-ai-agents' in source:
        text=text.replace('2. 使用 SHA-256 对规范化字节进行哈希。\n3. 使用 Ed25519 私钥对哈希值进行签名。','2. 使用 Ed25519 私钥直接对 JCS 规范字节签名；PureEdDSA 内部处理哈希。\n3. 将签名放在负载之外的 signature 对象中。')
        text=text.replace('重新计算规范哈希','重新计算 JCS 规范字节')
        text=text.replace('那些字节的 SHA-256 哈希值也发生了变化。签名（它是针对原始哈希的）不再与新的哈希匹配。','原签名针对原始 JCS 字节，不能验证修改后的字节。')
        text=text.replace('由Ed25519对规范负载字节的SHA-256进行签名','由 Ed25519 直接对 JCS 规范负载字节签名')
        text=text.replace('这也是本课程遵循的互联网草案（draft-farley-acta-signed-receipts）中共签名路径的格式。','这是本课自行定义的教学组合，不宣称符合独立 Internet-Draft（draft-farley-acta-signed-receipts）的线格式。')
        text=text.replace('加密签名','数字签名').replace('回执','收据')
        text=re.sub(r'删除之后的每一个收据。.*?这需要私钥。','链验证失败：相邻后继的前序引用与实际链不匹配。未修改收据的独立签名仍可能有效；检测尾部截断还需要外部锚点。',text)
        text=re.sub(r'    C --> D\[SHA-256 哈希\]\n    D --> E\[Ed25519 签名\]', '    C --> E[Ed25519 对规范字节签名]',text)
        text=text.replace('本课使用的收据格式遵循正在标准化过程中的 IETF 互联网草案','本课借鉴一份独立 IETF Internet-Draft 的规范化与签名范围约定，教学平铺结构不同于草案的 payload/signature 封装，不宣称符合其线格式；参考草案')
        text=text.replace('加密收据','密码学收据').replace('标准 JSON 负载','规范 JSON 负载')
        text=text.replace('但对于受监管的工作负载（金融、医疗、受欧盟 AI 法案约束的）则不行。','跨组织审计可能需要更强的可验证证据；具体监管要求取决于适用制度，本课程不是法律合规判断。')
        text=text.replace('审计员不需要信任你。','审计员仍需要可信的身份到公钥绑定与密钥管理。')
        text=text.replace('篡改任何字段都会使签名无效。','篡改已签名负载字段会使验签失败。')
        text=text.replace('移除或重新排序其中一张收据会破坏之后所有收据。即使单个签名被绕过，链条级别的篡改也能被发现。','移除或重排会让相邻链接或序号检查失败，整条链不能通过验证；未改动收据的独立数字签名仍可能有效。')
        text=text.replace('无网络调用，无服务依赖，无需信任第三方。','验签计算可离线进行，但必须从独立可信渠道确定公钥。该最小函数使用收据自带公钥，只演示数学验签，不证明真实身份。')
        text=text.replace('任何修改，不论多小，都会破坏签名。','已签名负载的修改会被验签检测到。')
        text=text.replace('对规范化的 SHA-256 摘要签名','直接对 JCS 规范字节签名（参数摘要与链哈希另行使用 SHA-256）')
        text=text.replace('同一互联网草案（`draft-farley-acta-signed-receipts`）中的联签方案是该模式的标准轨形态。','本课 `human.approval.v1` 是教学组合，并非该独立 Internet-Draft 定义的收据类型；也不是已经成为标准的线协议。')
        text=text.replace('进而改变 SHA-256 哈希值，使签名无效','因此直接对这些规范字节的验签失败')
        text=text.replace('哈希保持收据体积小且内容私密','哈希使收据体积有界并减少原文直接暴露，但不是加密；可枚举内容仍可能被猜测')
        text=re.sub(r'所有在被删除收据之后的收据。.*?私钥。','链检查失败：紧邻后继的前序引用与实际链不匹配，序号也可能断裂。其他未修改收据的独立签名并不因此失效。还需外部锚定链头，才能发现整段尾部截断。',text,flags=re.S) if '所有在被删除收据之后的收据。' in text else text
        text=text.replace('任何持有第三份收据的人均可证明第一和第二份在签署时存在，而无需公开其内容','该组合承诺把第三份收据绑定到前两份的指定字节，但检查匹配仍需相应原始收据；可信时间与完整的选择性披露还需额外机制')
    return text

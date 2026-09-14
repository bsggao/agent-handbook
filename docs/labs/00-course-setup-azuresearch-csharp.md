---
title: "00 · AzureSearch"
outline: [2, 3]
---

# 00 · AzureSearch

[返回：环境配置与学习准备](/lessons/setup.md) · [不可变原始文件](https://github.com/microsoft/ai-agents-for-beginners/blob/25b7985f3b2dc37a84f4a7387ccd3c9f0e5b1595/00-course-setup/AzureSearch.cs)

::: info 原课程脚本 · 未联网执行
保留原始框架与完整代码。依赖、变量、入口以脚本及其相邻 README 为准；本页为代码导读，未声称所有外部服务均已验证。
:::

检索过程：跟踪查询、候选结果和实际选入的证据；检索为空时应明确返回缺失，而不是补写答案。

```csharp
#:package Azure.Search.Documents@11.7.0
#:package Azure.Identity@1.21.0
#:property PublishAot=false

using Azure;
using Azure.Identity;
using Azure.Search.Documents;
using Azure.Search.Documents.Indexes;
using Azure.Search.Documents.Indexes.Models;

var serviceEndpoint = new Uri(Environment.GetEnvironmentVariable("AZURE_SEARCH_SERVICE_ENDPOINT")!);
var indexName = "sample-index";

// Keyless (recommended): uses your `az login` identity via Entra ID RBAC.
// Requires the "Search Service Contributor" and "Search Index Data Contributor" roles.
var credential = new DefaultAzureCredential();
// Fallback (key-based auth): the `using Azure;` directive above already imports
// AzureKeyCredential; replace the credential line above with:
// var credential = new AzureKeyCredential(Environment.GetEnvironmentVariable("AZURE_SEARCH_API_KEY")!);

var indexClient = new SearchIndexClient(serviceEndpoint, credential);

var fields = new List<SearchField>()
{
    new SimpleField("id", SearchFieldDataType.String) { IsKey = true },
    new SearchableField("content")
};

var index = new SearchIndex(name: indexName, fields: fields);

var response = await indexClient.CreateOrUpdateIndexAsync(index);
Console.WriteLine($"Index '{response.Value.Name}' ready.");

var searchClient = new SearchClient(serviceEndpoint, indexName, credential);

var documents = new[]
{
    new { id = "1", content = "Hello world" },
    new { id = "2", content = "Azure Cognitive Search" }
};

var result = await searchClient.UploadDocumentsAsync(documents);
Console.WriteLine($"Uploaded {result.Value.Results.Count} documents to index '{response.Value.Name}'.");

```

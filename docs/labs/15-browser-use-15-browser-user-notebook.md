---
title: "15 · 15-browser-user"
outline: [2, 3]
---

# 15 · 15-browser-user

[返回：Computer Use 与 Browser Use](/lessons/browser-use.md) · [不可变原始文件](https://github.com/microsoft/ai-agents-for-beginners/blob/25b7985f3b2dc37a84f4a7387ccd3c9f0e5b1595/15-browser-use/15-browser-user.ipynb)

::: warning 原课程完整 Notebook · 静态阅读与代码解析
代码按英文源文件顺序保留，中文说明以同版本译本为基础。原始安装单元格可能含无版本上限的 `-U`；请跳过它们，先按[准备篇](/lessons/setup.md)固定依赖。云端服务、模型权限、网站布局和部分 SDK 接口需在你自己的环境验证。本站没有执行云端请求；第 18 章的离线验证状态单独记录在[检查报告](/guide/verification.md)。
:::

## 运行准备

Python 3.12+；在独立虚拟环境安装源仓库依赖与本页中声明的额外依赖。原文件路径：`upstream/15-browser-use/15-browser-user.ipynb`。以原仓库根目录为工作目录，在 Jupyter 中按顺序执行；身份与环境变量见准备篇。

```bash
cd upstream
python -m jupyterlab
```

[下载原始 Notebook](/notebooks/15-browser-use/15-browser-user.ipynb)。输出为上游文件保存的历史结果，不能用作本站实测证明。

## 使用 AI 驱动的网页自动化寻找最便宜的 Airbnb

本笔记本展示了如何构建一个智能网页自动化 Agent，搜索 Airbnb，提取价格，并找到斯德哥尔摩最便宜的房源。你将学习如何将 **Playwright** 与 **Browser-Use** 集成，实现强大的 AI 驱动自动化。

## 你将学到：
1. **Playwright + Browser-Use 集成** ：结合浏览器管理与 AI 自动化
2. **基于视觉的价格提取** ：让 AI “看见” 并读取网页上的价格
3. **结构化数据提取** ：使用类型安全的 Pydantic 模型提取房源数据
4. **价格比较逻辑** ：从多个房源中找到最便宜的选项
5. **实际应用** ：实用的价格比较自动化

## 先决条件：
- 已配置 Azure OpenAI 部署
- 安装 Playwright（`pip install playwright`）
- 了解异步 Python
- 基础网页自动化知识

## 理解 Playwright + Browser-Use 架构

此笔记本使用了 Browser-Use 文档中的 **官方 Playwright 集成** 模式。

### 架构流程：
```
┌──────────────────┐
│   Playwright     │ ◄─── Manages browser lifecycle
│  Browser Manager │      Handles CDP connection
└────────┬─────────┘      Provides browser instance
         │
         │ playwright_browser parameter
         ▼
┌──────────────────┐
│  Browser-Use     │ ◄─── AI-powered automation
│  Browser Object  │      Wraps Playwright browser
└────────┬─────────┘      Provides Agent interface
         │
         │ uses
         ▼
┌──────────────────┐
│   Agent          │ ◄─── Vision + Decision Making
│ (with LLM)       │      Structured output extraction
└──────────────────┘      Natural language tasks
         │
         │ powered by
         ▼
┌──────────────────┐
│  Azure OpenAI    │ ◄─── GPT-4 Vision
│  (LLM + Vision)  │      Analyzes screenshots
└──────────────────┘      Extracts structured data
```

### 为什么采用这种方法？

 **Playwright 提供：** 
- ✅ 强大的浏览器生命周期管理
- ✅ 完整的 Chrome DevTools 协议控制
- ✅ 稳定的页面和上下文处理
- ✅ 内置的等待与同步

 **Browser-Use 提供：** 
- ✅ AI 驱动的元素查找（无需 CSS 选择器！）
- ✅ 基于视觉的页面理解
- ✅ 使用 Pydantic 的结构化输出提取
- ✅ 自然语言任务执行

 **两者协同实现：** 
- 🎯 “搜索斯德哥尔摩 Airbnb” → Agent 导航
- 👁️ 视觉读取页面上的所有价格
- 📊 结构化提取 → 清晰的 Python 对象
- 💰 价格比较逻辑 → 找出最便宜的

### 我们的任务流程：
1. **Playwright** 启动 Chrome 浏览器
2. **Browser-Use Agent** 导航到 Airbnb.com
3. **Agent 搜索** “斯德哥尔摩，瑞典”
4. **视觉模型** 读取并提取所有房源价格
5. **结构化输出** 返回类型化数据（Pydantic 模型）
6. **Python 代码** 比较价格并找到最便宜的
7. **用丰富格式** 显示结果

### 代码单元格 3

阅读提示：跟踪本单元格读取的变量、修改的状态以及返回值。按原顺序执行，确认依赖的前序变量已经存在。

```text
%pip install browser_use langchain-openai playwright
```

### 代码单元格 4

阅读提示：跟踪本单元格读取的变量、修改的状态以及返回值。按原顺序执行，确认依赖的前序变量已经存在。

```python
!playwright install chromium
```

### 代码单元格 5

配置加载：从本地环境读取端点与部署名；缺少变量时先修复配置，不要把密钥写进代码。

数据结构：Pydantic 模型定义字段类型；只有传入实际的 response_format 并检查解析结果，才能约束本次输出。

输出观察：print 展示应用可观察结果；预存输出和现场结果可能不同，它不是模型内部思考记录。

```python
import asyncio
import os
import re
from typing import Optional, List
from IPython.display import display, HTML, Markdown
from dotenv import load_dotenv

# Playwright imports
from playwright.async_api import async_playwright

# Browser-Use imports - USE BROWSER-USE'S AZURE OPENAI!
# Changed from langchain_openai
from browser_use import Agent, Browser, ChatAzureOpenAI
from pydantic import BaseModel, Field

print("✅ All packages imported successfully")
```

::: details 原文件保存的输出（不是本项目实测）

```text
✅ All packages imported successfully
```

:::

### 代码单元格 6

配置加载：从本地环境读取端点与部署名；缺少变量时先修复配置，不要把密钥写进代码。

输出观察：print 展示应用可观察结果；预存输出和现场结果可能不同，它不是模型内部思考记录。

```python
# Load environment variables
load_dotenv()

# Azure OpenAI Configuration
azure_openai_deployment = os.getenv("AZURE_OPENAI_CHAT_DEPLOYMENT_NAME")
azure_openai_endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
azure_openai_api_key = os.getenv("AZURE_OPENAI_API_KEY")
api_version = os.getenv("AZURE_OPENAI_API_VERSION")

# Verify configuration
print("✅ Azure OpenAI Configuration:")
print(f"   Endpoint: {azure_openai_endpoint}")
print(f"   Deployment: {azure_openai_deployment}")
print(f"   API Version: {api_version}")
```

::: details 原文件保存的输出（不是本项目实测）

```text
✅ Azure OpenAI Configuration:
   Endpoint: https://foundry-aiteam2510.cognitiveservices.azure.com/
   Deployment: gpt-5-mini
   API Version: 2024-12-01-preview
```

:::

## 初始化 Azure OpenAI LLM

LLM 驱动 Agent 的决策和视觉能力。我们使用：
- **温度：0.3** 以实现一致且可预测的自动化
- **视觉能力** 用于“观察”和理解页面内容
- **结构化输出** 用于提取数据到 Pydantic 模型

### 代码单元格 8

输出观察：print 展示应用可观察结果；预存输出和现场结果可能不同，它不是模型内部思考记录。

```python
# Initialize Azure OpenAI with Browser-Use's ChatAzureOpenAI
llm = ChatAzureOpenAI(
    # Your deployment name (e.g., 'gpt-5-mini')
    model=azure_openai_deployment,
    # Browser-Use reads these from environment variables automatically:
    # AZURE_OPENAI_ENDPOINT
    # AZURE_OPENAI_API_KEY
    # AZURE_OPENAI_API_VERSION (optional, defaults to latest)
)

print("✅ LLM initialized successfully")
print(f"   Model: {azure_openai_deployment}")
print(f"   Endpoint: {azure_openai_endpoint}")
print(f"   Integration: Browser-Use ChatAzureOpenAI")
```

::: details 原文件保存的输出（不是本项目实测）

```text
✅ LLM initialized successfully
   Model: gpt-5-mini
   Endpoint: https://foundry-aiteam2510.cognitiveservices.azure.com/
   Integration: Browser-Use ChatAzureOpenAI
```

:::

## 定义结构化输出模型

我们使用 Pydantic 模型从 Airbnb 搜索结果中提取结构化数据。Agent 将使用 GPT-4 Vision 自动读取页面并将数据提取到这些模型中。

这确保了所有提取数据的类型安全和验证。

### 代码单元格 10

数据结构：Pydantic 模型定义字段类型；只有传入实际的 response_format 并检查解析结果，才能约束本次输出。

检索过程：跟踪查询、候选结果和实际选入的证据；检索为空时应明确返回缺失，而不是补写答案。

输出观察：print 展示应用可观察结果；预存输出和现场结果可能不同，它不是模型内部思考记录。

```python
# UPDATE THIS CELL - Add URL field to AirbnbListing
class AirbnbListing(BaseModel):
    """Single Airbnb listing with price information"""
    title: str = Field(description="Name/title of the listing")
    price_per_night: float = Field(
        description="Price per night as a number (extract just the numeric value, ignore currency symbols)")
    currency: str = Field(
        default="SEK", description="Currency code (SEK for Swedish Krona)")
    rating: Optional[float] = Field(
        default=None, description="Rating score if visible")
    url: Optional[str] = Field(
        default=None, description="Full URL link to the listing page")  # ✅ NEW!


class SearchResult(BaseModel):
    """Complete search results from Airbnb"""
    location: str = Field(description="Search location (Stockholm, Sweden)")
    total_listings_found: int = Field(
        description="Number of listings found on the page")
    listings: List[AirbnbListing] = Field(
        description="List of all listings with prices extracted from the page")
    cheapest_listing: AirbnbListing = Field(
        description="The listing with the lowest price per night")
    average_price: float = Field(
        description="Average price per night across all listings")
    price_range: str = Field(description="Price range as 'min - max SEK'")


print("✅ Structured output models defined")
print("   AirbnbListing: Individual listing data with clickable URLs")
print("   SearchResult: Complete search results with price analysis")
```

::: details 原文件保存的输出（不是本项目实测）

```text
✅ Structured output models defined
   AirbnbListing: Individual listing data with clickable URLs
   SearchResult: Complete search results with price analysis
```

:::

## 显示辅助函数

这些函数在笔记本中提供丰富的教育输出，带有格式化的 HTML。

### 代码单元格 13

数据结构：Pydantic 模型定义字段类型；只有传入实际的 response_format 并检查解析结果，才能约束本次输出。

输出观察：print 展示应用可观察结果；预存输出和现场结果可能不同，它不是模型内部思考记录。

```python
class ListingInfo(BaseModel):
    """Information about the Airbnb listing"""
    title: str = Field(description="The name/title of the listing")
    location: str = Field(description="City and country of the listing")
    price_per_night: Optional[str] = Field(
        description="Price per night if visible")
    rating: Optional[str] = Field(description="Rating score if visible")


class BookingDates(BaseModel):
    """Selected booking dates"""
    check_in: str = Field(
        description="Check-in date in format: Month DD, YYYY")
    check_out: str = Field(
        description="Check-out date in format: Month DD, YYYY")
    nights: int = Field(description="Number of nights")


class BookingResult(BaseModel):
    """Complete booking result information"""
    success: bool = Field(description="Whether the booking flow was completed")
    listing_info: Optional[ListingInfo] = Field(
        description="Details about the listing")
    booking_dates: Optional[BookingDates] = Field(description="Selected dates")
    total_price: Optional[str] = Field(description="Total price if shown")
    message: str = Field(description="Status message or error description")


print("✅ Structured output models defined")
print("   ListingInfo: Extract listing details")
print("   BookingDates: Capture selected dates")
print("   BookingResult: Final booking status")
```

::: details 原文件保存的输出（不是本项目实测）

```text
✅ Structured output models defined
   ListingInfo: Extract listing details
   BookingDates: Capture selected dates
   BookingResult: Final booking status
```

:::

## 显示辅助函数

这些函数在笔记本中提供丰富且具有教育意义的输出。

### 代码单元格 15

输出观察：print 展示应用可观察结果；预存输出和现场结果可能不同，它不是模型内部思考记录。

```python
def display_step(step_number: int, title: str, description: str, color: str = "#2E8B57"):
    """Display a workflow step with formatting"""
    html = f"""
    <div style='
        margin: 20px 0; 
        padding: 20px; 
        border-left: 5px solid {color}; 
        background: linear-gradient(to right, rgba(46, 139, 87, 0.05), transparent); 
        border-radius: 8px;
    '>
        <h3 style='color: {color}; margin: 0 0 10px 0;'>
            Step {step_number}: {title}
        </h3>
        <p style='margin: 0; line-height: 1.6; color: #333;'>{description}</p>
    </div>
    """
    display(HTML(html))


def display_action(action_type: str, details: str, emoji: str = "⚙️"):
    """Display an action being performed"""
    html = f"""
    <div style='
        margin: 10px 20px;
        padding: 12px 16px;
        background: rgba(0, 123, 255, 0.05);
        border: 1px solid #007BFF;
        border-radius: 6px;
        font-family: monospace;
        font-size: 14px;
    '>
        <strong style='color: #007BFF;'>{emoji} {action_type}:</strong>
        <span style='color: #555; margin-left: 10px;'>{details}</span>
    </div>
    """
    display(HTML(html))


def display_result(success: bool, message: str):
    """Display a result with success/failure indication"""
    color = "#28a745" if success else "#dc3545"
    emoji = "✅" if success else "❌"
    html = f"""
    <div style='
        margin: 20px 0;
        padding: 15px 20px;
        border-left: 5px solid {color};
        background: rgba({"40, 167, 69" if success else "220, 53, 69"}, 0.1);
        border-radius: 8px;
    '>
        <strong style='color: {color}; font-size: 16px;'>{emoji} {message}</strong>
    </div>
    """
    display(HTML(html))


def display_screenshot(screenshot_base64: str, caption: str = ""):
    """Display a screenshot in the notebook"""
    html = f"""
    <div style='margin: 20px 0; text-align: center;'>
        <img src='data:image/png;base64,{screenshot_base64}' 
             style='max-width: 100%; border: 2px solid #ddd; border-radius: 8px; box-shadow: 0 4px 6px rgba(0,0,0,0.1);'/>
        {f"<p style='margin-top: 10px; color: #666; font-style: italic;'>{caption}</p>" if caption else ""}
    </div>
    """
    display(HTML(html))


print("✅ Helper functions loaded")
```

::: details 原文件保存的输出（不是本项目实测）

```text
✅ Helper functions loaded
```

:::

## Airbnb 预订 Agent 类

该类协调整个预订工作流程，策略性地结合了 Agent 和执行者方法。

### 代码单元格 17

异步执行：async def 定义协程，await 等待结果；普通 .py 脚本需要 asyncio.run() 入口，Notebook 支持顶层 await。

检索过程：跟踪查询、候选结果和实际选入的证据；检索为空时应明确返回缺失，而不是补写答案。

输出观察：print 展示应用可观察结果；预存输出和现场结果可能不同，它不是模型内部思考记录。

```python
class AirbnbSearchAgent:
    """
    Intelligent Airbnb search agent using Playwright + Browser-Use integration.
    
    This agent:
    1. Navigates to Airbnb.com
    2. Searches for listings in Stockholm
    3. Extracts all visible prices using AI vision
    4. Compares prices and finds the cheapest listing
    """
    
    def __init__(self, llm, playwright_browser):
        self.llm = llm
        # Browser-Use wraps the Playwright browser
        # Reference: https://docs.browser-use.com/examples/templates/playwright-integration
        self.browser = Browser(playwright_browser=playwright_browser)
        
    async def take_screenshot(self, caption: str = ""):
        """Take and display a screenshot of current page"""
        try:
            page = await self.browser.get_current_page()
            screenshot_base64 = await page.screenshot(format='png')
            display_screenshot(screenshot_base64, caption)
        except Exception as e:
            print(f"⚠️  Could not capture screenshot: {str(e)}")
    
    async def search_stockholm(self) -> SearchResult:
        """
        Main workflow: Search Airbnb for Stockholm and find cheapest listing.
        
        Returns:
            SearchResult: Structured data with all listings and price analysis
        """
        
        # Step 1: Navigate and search
        display_step(
            1, 
            "Navigate & Search (AI Agent)", 
            "Using AI agent with vision to navigate Airbnb and search for Stockholm listings. "
            "The agent will handle pop-ups, cookie banners, and search automatically."
        )
        
        try:
            # Agent navigates to Airbnb and searches
            search_agent = Agent(
                task=(
                    "Navigate to https://www.airbnb.com. "
                    "Close any pop-ups, cookie banners, or login prompts if they appear. "
                    "Search for 'Stockholm, Sweden' in the search box. "
                    "Wait for the search results page to fully load with listing cards visible."
                ),
                llm=self.llm,
                browser=self.browser,
                use_vision=True  # Critical: enables screenshot analysis
            )
            
            display_action("Agent", "Navigating to Airbnb and searching for Stockholm...")
            await search_agent.run()
            
            # Wait for results to load
            await asyncio.sleep(3)
            await self.take_screenshot("Search results page loaded")
            
            display_result(True, "Successfully loaded Stockholm search results")
            
        except Exception as e:
            display_result(False, f"Search failed: {str(e)}")
            raise
        
        # Step 2: Extract prices with vision
        display_step(
            2,
            "Extract Prices (Vision + LLM)",
            "Using GPT-4 Vision to read all listing prices from the page and extract "
            "structured data into Pydantic models. The AI 'sees' the page like a human."
        )
        
        try:
            page = await self.browser.get_current_page()
            
            display_action("Vision", "AI is analyzing the page and reading prices...")
            
            # Use page.extract_content with structured output
            # Reference: https://docs.browser-use.com/customize/actor/all-parameters
            # This uses LLM to parse the visible page content
            extraction_prompt = """
            Extract ALL Airbnb listings visible on this page.
            
            For each listing, extract:
            - Title/name of the property
            - Price per night (numeric value only, without currency symbols)
            - Currency (SEK for Swedish Krona)
            - Rating if visible
            
            After extracting all listings:
            - Identify which listing has the LOWEST price
            - Calculate the average price across all listings
            - Determine the price range (min to max)
            
            Focus on the listing cards on the search results page.
            Only include listings where you can clearly see the price.
            """
            
            # Extract structured data using LLM vision
            search_results = await page.extract_content(
                prompt=extraction_prompt,
                structured_output=SearchResult,
                llm=self.llm
            )
            
            display_action(
                "Extracted", 
                f"Found {search_results.total_listings_found} listings with prices"
            )
            
            # Display some sample prices
            if len(search_results.listings) > 0:
                sample_prices = [f"{l.price_per_night:.0f} SEK" for l in search_results.listings[:5]]
                display_action(
                    "Sample Prices", 
                    f"{', '.join(sample_prices)}{'...' if len(search_results.listings) > 5 else ''}"
                )
            
            display_result(True, "Price extraction completed successfully")
            
            return search_results
            
        except Exception as e:
            display_result(False, f"Price extraction failed: {str(e)}")
            raise

print("✅ AirbnbSearchAgent class defined")
print("   Integration: Playwright browser + Browser-Use Agent")
print("   Capabilities: Vision-based price extraction with structured output")
```

::: details 原文件保存的输出（不是本项目实测）

```text
✅ AirbnbSearchAgent class defined
   Integration: Playwright browser + Browser-Use Agent
   Capabilities: Vision-based price extraction with structured output
```

:::

## 执行搜索

现在让我们运行完整的工作流程，找到斯德哥尔摩最便宜的Airbnb！

这将会：
1. 启动一个真实的Chrome浏览器（可见）
2. 使用AI进行导航和搜索
3. 通过视觉识别提取所有价格
4. 显示最便宜的选项

### 代码单元格 19

异步执行：async def 定义协程，await 等待结果；普通 .py 脚本需要 asyncio.run() 入口，Notebook 支持顶层 await。

检索过程：跟踪查询、候选结果和实际选入的证据；检索为空时应明确返回缺失，而不是补写答案。

输出观察：print 展示应用可观察结果；预存输出和现场结果可能不同，它不是模型内部思考记录。

```python
# UPDATED AirbnbSearchAgent class - Add keep_alive parameter
class AirbnbSearchAgent:
    """
    Intelligent Airbnb search agent using Browser-Use integration via CDP.
    
    This agent:
    1. Connects to Chrome via CDP (Chrome DevTools Protocol)
    2. Both Playwright and Browser-Use share the same browser instance
    3. Searches for listings in Stockholm
    4. Extracts prices using AI vision
    5. Finds the cheapest listing
    """

    def __init__(self, llm, cdp_url: str):
        """
        Initialize agent with LLM and CDP connection.
        
        Args:
            llm: Language model for AI decisions
            cdp_url: Chrome DevTools Protocol URL (e.g., 'http://localhost:9222')
        """
        self.llm = llm
        # Browser-Use connects to Chrome via CDP
        # IMPORTANT: keep_alive=True prevents browser from closing after Agent completes
        self.browser = Browser(
            cdp_url=cdp_url,
            keep_alive=True  # ✅ This keeps the browser open!
        )

    async def take_screenshot(self, caption: str = ""):
        """Take and display a screenshot of current page"""
        try:
            # Get pages and use the active one
            pages = await self.browser.get_pages()
            if not pages:
                print("⚠️  No pages available for screenshot")
                return

            page = pages[0]  # Use first page (active page)
            screenshot_bytes = await page.screenshot()
            import base64
            screenshot_base64 = base64.b64encode(screenshot_bytes).decode()
            display_screenshot(screenshot_base64, caption)
        except Exception as e:
            print(f"⚠️  Could not capture screenshot: {str(e)}")

    async def search_stockholm(self) -> SearchResult:
        """
        Main workflow: Search Airbnb for Stockholm and find cheapest listing.
        
        Returns:
            SearchResult: Structured data with all listings and price analysis
        """

        # Step 1: Navigate and search
        display_step(
            1,
            "Navigate & Search (AI Agent)",
            "Using AI agent with vision to navigate Airbnb and search for Stockholm listings. "
            "The agent will handle pop-ups, cookie banners, and search automatically."
        )

        try:
            # Agent navigates to Airbnb and searches
            search_agent = Agent(
                task=(
                    "Navigate to https://www.airbnb.com. "
                    "Close any pop-ups, cookie banners, or login prompts if they appear. "
                    "Search for 'Stockholm, Sweden' in the search box. "
                    "Wait for the search results page to fully load with listing cards visible."
                ),
                llm=self.llm,
                browser=self.browser,
                use_vision=True  # Critical: enables screenshot analysis
            )

            display_action(
                "Agent", "Navigating to Airbnb and searching for Stockholm...")
            await search_agent.run()

            # Wait for results to load
            await asyncio.sleep(3)
            await self.take_screenshot("Search results page loaded")

            display_result(
                True, "Successfully loaded Stockholm search results")

        except Exception as e:
            display_result(False, f"Search failed: {str(e)}")
            raise

        # Step 2: Extract prices with vision
        display_step(
            2,
            "Extract Prices (Vision + LLM)",
            "Using GPT-4 Vision to read all listing prices from the page and extract "
            "structured data into Pydantic models. The AI 'sees' the page like a human."
        )

        try:
            # Get the pages created by the Agent
            pages = await self.browser.get_pages()

            if not pages:
                raise RuntimeError(
                    "No pages available after Agent run. Browser might have closed.")

            # Use the first (active) page
            page = pages[0]

            display_action(
                "Vision", "AI is analyzing the page and reading prices...")

            # Extract structured data using LLM vision
            extraction_prompt = """
Extract ALL Airbnb Home listings visible on this page. DO NOT include "Experiences" or other non-home listings.

For each listing, extract:
- Title/name of the property
- Price per night (numeric value only, without currency symbols)
- Currency (SEK for Swedish Krona)
- Rating if visible
- URL: The full link to the listing detail page (should start with https://www.airbnb.com/rooms/)

After extracting all listings:
- Identify which listing has the LOWEST price
- Calculate the average price across all listings
- Determine the price range (min to max)

Focus on the listing cards on the search results page.
Only include listings where you can clearly see the price.
IMPORTANT: Extract the actual URL/link for each listing so users can click on it.
"""

            search_results = await page.extract_content(
                prompt=extraction_prompt,
                structured_output=SearchResult,
                llm=self.llm
            )

            display_action(
                "Extracted",
                f"Found {search_results.total_listings_found} listings with prices"
            )

            # Display some sample prices
            if len(search_results.listings) > 0:
                sample_prices = [
                    f"{l.price_per_night:.0f} SEK" for l in search_results.listings[:5]]
                display_action(
                    "Sample Prices",
                    f"{', '.join(sample_prices)}{'...' if len(search_results.listings) > 5 else ''}"
                )

            display_result(True, "Price extraction completed successfully")

            return search_results

        except Exception as e:
            display_result(False, f"Price extraction failed: {str(e)}")
            raise


print("✅ AirbnbSearchAgent class defined")
print("   Integration: CDP-based connection for Playwright + Browser-Use")
print("   Capabilities: Vision-based price extraction with structured output")
print("   Browser Mode: keep_alive=True (prevents auto-close)")
```

::: details 原文件保存的输出（不是本项目实测）

```text
✅ AirbnbSearchAgent class defined
   Integration: CDP-based connection for Playwright + Browser-Use
   Capabilities: Vision-based price extraction with structured output
   Browser Mode: keep_alive=True (prevents auto-close)
```

:::

### 代码单元格 20

异步执行：async def 定义协程，await 等待结果；普通 .py 脚本需要 asyncio.run() 入口，Notebook 支持顶层 await。

检索过程：跟踪查询、候选结果和实际选入的证据；检索为空时应明确返回缺失，而不是补写答案。

代码执行边界：这里演示生成代码的执行；不要对不可信模型输出直接 exec。实际应用应使用隔离环境、时间/资源限制和最小权限。

```python
import subprocess
import tempfile


async def start_chrome_with_cdp(port: int = 9222):
    """
    Start Chrome with CDP (Chrome DevTools Protocol) enabled.
    Returns the Chrome process.
    """
    # Create temporary directory for Chrome user data
    user_data_dir = tempfile.mkdtemp(prefix='chrome_cdp_')

    # Chrome paths for different platforms
    chrome_paths = [
        '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome',  # macOS
        '/usr/bin/google-chrome',  # Linux
        '/usr/bin/chromium-browser',  # Linux Chromium
        'chrome',  # Windows/PATH
        'chromium',  # Generic
    ]

    chrome_exe = None
    for path in chrome_paths:
        if os.path.exists(path) or path in ['chrome', 'chromium']:
            try:
                test_proc = await asyncio.create_subprocess_exec(
                    path, '--version',
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL
                )
                await test_proc.wait()
                chrome_exe = path
                break
            except Exception:
                continue

    if not chrome_exe:
        raise RuntimeError(
            '❌ Chrome not found. Please install Chrome or Chromium.')

    # Chrome command arguments
    cmd = [
        chrome_exe,
        f'--remote-debugging-port={port}',
        f'--user-data-dir={user_data_dir}',
        '--no-first-run',
        '--no-default-browser-check',
        'about:blank',
    ]

    # Start Chrome process
    process = await asyncio.create_subprocess_exec(
        *cmd,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL
    )

    # Wait for Chrome to start and CDP to be ready
    import aiohttp
    cdp_ready = False
    for _ in range(20):  # 20 second timeout
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f'http://localhost:{port}/json/version',
                    timeout=aiohttp.ClientTimeout(total=1)
                ) as response:
                    if response.status == 200:
                        cdp_ready = True
                        break
        except Exception:
            pass
        await asyncio.sleep(1)

    if not cdp_ready:
        process.terminate()
        raise RuntimeError('❌ Chrome failed to start with CDP')

    print(f"✅ Chrome started with CDP on port {port}")
    return process


async def main():
    """
    Main execution function for Airbnb price comparison.
    
    Uses CDP to connect both Playwright and Browser-Use to the same Chrome instance.
    """

    display(HTML("""
    <div style='
        padding: 30px;
        background: linear-gradient(135deg, #FF5A5F 0%, #FF385C 100%);
        color: white;
        border-radius: 12px;
        margin: 30px 0;
        box-shadow: 0 10px 30px rgba(0,0,0,0.2);
    '>
        <h2 style='margin: 0 0 15px 0;'>🏠 Find the Cheapest Airbnb in Stockholm</h2>
        <p style='margin: 0; font-size: 16px; line-height: 1.8;'>
            This demo uses <strong>CDP (Chrome DevTools Protocol)</strong> integration:<br>
            • <strong>Chrome</strong> runs with remote debugging enabled<br>
            • <strong>Playwright</strong> connects to Chrome via CDP<br>
            • <strong>Browser-Use</strong> connects to same Chrome via CDP<br>
            • <strong>GPT-4 Vision</strong> reads and extracts prices<br>
            • <strong>Structured Output</strong> returns type-safe data
        </p>
        <p style='margin: 15px 0 0 0; font-size: 14px; opacity: 0.9;'>
            📊 Watch the browser as the AI agent searches and analyzes prices!
        </p>
    </div>
    """))

    chrome_process = None
    playwright_browser = None

    try:
        # Step 1: Start Chrome with CDP
        display_action(
            "Chrome", "Starting Chrome with CDP (remote debugging)...")
        chrome_process = await start_chrome_with_cdp(port=9222)
        cdp_url = 'http://localhost:9222'

        # Step 2: Connect Playwright to CDP (optional - for custom Playwright actions)
        display_action(
            "Playwright", "Connecting Playwright to Chrome via CDP...")
        playwright = await async_playwright().start()
        playwright_browser = await playwright.chromium.connect_over_cdp(cdp_url)
        display_result(True, "Playwright connected successfully")

        # Step 3: Create Browser-Use agent with CDP connection
        display_action(
            "Browser-Use", "Creating Browser-Use agent with CDP connection...")
        agent = AirbnbSearchAgent(llm=llm, cdp_url=cdp_url)
        display_result(True, "Agent initialized with CDP integration")

        # Step 4: Search and extract prices
        result = await agent.search_stockholm()

        # Step 5: Display results
        display(
            HTML("<hr style='margin: 40px 0; border: none; border-top: 2px solid #ddd;'>"))

        display(HTML("""
        <div style='padding: 20px; background: #f8f9fa; border-radius: 8px; margin: 20px 0;'>
            <h3 style='margin: 0 0 15px 0; color: #333;'>📊 Search Results</h3>
        </div>
        """))

        # Display summary stats
        display(HTML(f"""
        <div style='margin: 20px; padding: 20px; background: white; border-radius: 8px; box-shadow: 0 2px 8px rgba(0,0,0,0.1);'>
            <h4 style='margin: 0 0 15px 0; color: #FF5A5F;'>📈 Price Analysis</h4>
            <table style='width: 100%; border-collapse: collapse;'>
                <tr>
                    <td style='padding: 10px; border-bottom: 1px solid #eee; font-weight: bold;'>Location:</td>
                    <td style='padding: 10px; border-bottom: 1px solid #eee;'>{result.location}</td>
                </tr>
                <tr>
                    <td style='padding: 10px; border-bottom: 1px solid #eee; font-weight: bold;'>Total Listings Found:</td>
                    <td style='padding: 10px; border-bottom: 1px solid #eee;'>{result.total_listings_found}</td>
                </tr>
                <tr>
                    <td style='padding: 10px; border-bottom: 1px solid #eee; font-weight: bold;'>Average Price:</td>
                    <td style='padding: 10px; border-bottom: 1px solid #eee;'>{result.average_price:.2f} SEK/night</td>
                </tr>
                <tr>
                    <td style='padding: 10px; border-bottom: 1px solid #eee; font-weight: bold;'>Price Range:</td>
                    <td style='padding: 10px; border-bottom: 1px solid #eee;'>{result.price_range}</td>
                </tr>
            </table>
        </div>
        """))

        # Display the CHEAPEST listing with clickable link
        cheapest = result.cheapest_listing

        # Create View Listing button if URL exists
        view_button = ""
        if cheapest.url:
            view_button = f"""
            <a href="{cheapest.url}" target="_blank" style="
                display: inline-block;
                margin-top: 15px;
                padding: 12px 24px;
                background: #FF5A5F;
                color: white;
                text-decoration: none;
                border-radius: 8px;
                font-weight: bold;
                transition: background 0.3s;
            " onmouseover="this.style.background='#E00007'" onmouseout="this.style.background='#FF5A5F'">
                🔗 View Listing on Airbnb
            </a>
            """

        display(HTML(f"""
        <div style='
            margin: 20px; 
            padding: 25px; 
            background: linear-gradient(135deg, #FFD700 0%, #FFA500 100%);
            border-radius: 12px; 
            box-shadow: 0 4px 12px rgba(255,165,0,0.3);
            border: 3px solid #FFD700;
        '>
            <h3 style='margin: 0 0 15px 0; color: #333; font-size: 24px;'>
                🏆 CHEAPEST AIRBNB IN STOCKHOLM
            </h3>
            <div style='background: white; padding: 20px; border-radius: 8px; margin-top: 15px;'>
                <h4 style='margin: 0 0 10px 0; color: #FF5A5F;'>{cheapest.title}</h4>
                <p style='margin: 10px 0; font-size: 28px; font-weight: bold; color: #28a745;'>
                    {cheapest.price_per_night:.2f} {cheapest.currency}/night
                </p>
                {f"<p style='margin: 10px 0; color: #666;'>⭐ Rating: {cheapest.rating}/5.0</p>" if cheapest.rating else ""}
                <p style='margin: 15px 0 0 0; color: #666; font-size: 14px;'>
                    💰 Saves you <strong>{(result.average_price - cheapest.price_per_night):.2f} SEK</strong> compared to average price!
                </p>
                {view_button}
            </div>
        </div>
        """))

        # Display all listings in a clickable table
        if len(result.listings) > 1:
            listings_html = """
            <div style='margin: 20px; padding: 20px; background: white; border-radius: 8px; box-shadow: 0 2px 8px rgba(0,0,0,0.1);'>
                <h4 style='margin: 0 0 15px 0; color: #FF5A5F;'>📋 All Listings Found (Click to View)</h4>
                <table style='width: 100%; border-collapse: collapse;'>
                    <thead>
                        <tr style='background: #f8f9fa;'>
                            <th style='padding: 12px; text-align: left; border-bottom: 2px solid #dee2e6;'>Rank</th>
                            <th style='padding: 12px; text-align: left; border-bottom: 2px solid #dee2e6;'>Listing</th>
                            <th style='padding: 12px; text-align: right; border-bottom: 2px solid #dee2e6;'>Price/Night</th>
                            <th style='padding: 12px; text-align: center; border-bottom: 2px solid #dee2e6;'>Rating</th>
                            <th style='padding: 12px; text-align: center; border-bottom: 2px solid #dee2e6;'>Link</th>
                        </tr>
                    </thead>
                    <tbody>
            """

            sorted_listings = sorted(
                result.listings, key=lambda x: x.price_per_night)

            for idx, listing in enumerate(sorted_listings, 1):
                is_cheapest = listing.price_per_night == cheapest.price_per_night
                row_style = "background: #fff3cd;" if is_cheapest else ""
                badge = "🏆 " if is_cheapest else ""

                # Create clickable link if URL exists
                if listing.url:
                    link_html = f'<a href="{listing.url}" target="_blank" style="color: #FF5A5F; text-decoration: none; font-weight: bold; padding: 6px 12px; border: 1px solid #FF5A5F; border-radius: 4px; transition: all 0.3s;" onmouseover="this.style.background=\'#FF5A5F\'; this.style.color=\'white\'" onmouseout="this.style.background=\'transparent\'; this.style.color=\'#FF5A5F\'">🔗 View</a>'
                    title_html = f'<a href="{listing.url}" target="_blank" style="color: #333; text-decoration: none; font-weight: 500;" onmouseover="this.style.color=\'#FF5A5F\'" onmouseout="this.style.color=\'#333\'">{listing.title[:50]}...</a>'
                else:
                    link_html = '<span style="color: #999;">N/A</span>'
                    title_html = f'{listing.title[:50]}...'

                listings_html += f"""
                    <tr style='{row_style}'>
                        <td style='padding: 10px; border-bottom: 1px solid #eee;'>{badge}{idx}</td>
                        <td style='padding: 10px; border-bottom: 1px solid #eee;'>{title_html}</td>
                        <td style='padding: 10px; border-bottom: 1px solid #eee; text-align: right; font-weight: bold;'>
                            {listing.price_per_night:.2f} {listing.currency}
                        </td>
                        <td style='padding: 10px; border-bottom: 1px solid #eee; text-align: center;'>
                            {f"⭐ {listing.rating}" if listing.rating else "N/A"}
                        </td>
                        <td style='padding: 10px; border-bottom: 1px solid #eee; text-align: center;'>
                            {link_html}
                        </td>
                    </tr>
                """

            listings_html += """
                    </tbody>
                </table>
                <p style='margin-top: 15px; color: #666; font-size: 13px; font-style: italic;'>
                    💡 Tip: Click on any listing title or the "View" button to open it in a new tab
                </p>
            </div>
            """

            display(HTML(listings_html))

        display_result(True, "Price comparison completed successfully!")

    except Exception as e:
        display_result(False, f"Error during search: {str(e)}")
        import traceback
        print(traceback.format_exc())

    finally:
        # Cleanup
        display_action("Cleanup", "Closing browser and cleaning up...")

        if playwright_browser:
            await playwright_browser.close()

        if chrome_process:
            chrome_process.terminate()
            try:
                await asyncio.wait_for(chrome_process.wait(), 5)
            except TimeoutError:
                chrome_process.kill()

        display_result(True, "Cleanup complete")

    # Display educational summary
    display(HTML("""
    <div style='
        margin: 40px 0 20px 0;
        padding: 25px;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border-radius: 12px;
    '>
        <h3 style='margin: 0 0 15px 0;'>🎓 What You Just Learned</h3>
        <ul style='margin: 0; padding-left: 20px; line-height: 2;'>
            <li><strong>CDP Integration:</strong> Chrome DevTools Protocol connects Playwright + Browser-Use</li>
            <li><strong>Vision-Based Extraction:</strong> GPT-4 Vision reads prices like a human</li>
            <li><strong>Structured Output:</strong> Type-safe data extraction with Pydantic models</li>
            <li><strong>Price Comparison:</strong> Automated analysis to find best deals</li>
            <li><strong>Clickable URLs:</strong> Direct links to Airbnb listings for easy viewing</li>
            <li><strong>Real-World Application:</strong> Practical web scraping for price monitoring</li>
        </ul>
    </div>
    """))

# Run the demo
await main()
```

::: details 原文件保存的输出（不是本项目实测）

```text
<IPython.core.display.HTML object>
<IPython.core.display.HTML object>
✅ Chrome started with CDP on port 9222

<IPython.core.display.HTML object>
<IPython.core.display.HTML object>
<IPython.core.display.HTML object>
<IPython.core.display.HTML object>
<IPython.core.display.HTML object>
INFO     [Agent] 🔗 Found URL in task: https://www.airbnb.com, adding as initial action...

<IPython.core.display.HTML object>
INFO     [Agent] 🚀 Task: Navigate to https://www.airbnb.com. Close any pop-ups, cookie banners, or login prompts if they appear. Search for 'Stockholm, Sweden' in the search box. Wait for the search results page to fully load with listing cards visible.
INFO     [service] ────────────────────────────────────────
INFO     [service] 🔐 To view this run in Browser Use Cloud, authenticate with:
INFO     [service]     👉  browser-use auth
INFO     [service]     or: python -m browser_use.cli auth
INFO     [service] ────────────────────────────────────────

INFO     [Agent]   🦾 [ACTION 1/1] go_to_url: url: https://www.airbnb.com, new_tab: False
INFO     [tools] 🔗 Navigated to https://www.airbnb.com
INFO     [Agent] 

INFO     [Agent] 📍 Step 1:
ERROR    [Agent] ❌ Result failed 1/4 times:
 LLM call timed out after 60 seconds. Keep your thinking and output short.
INFO     [Agent] 

INFO     [Agent] 📍 Step 2:
INFO     [Agent]   👍 Eval: Successfully loaded Airbnb homepage and identified the search input box for destination.
INFO     [Agent]   🎯 Next goal: Input 'Stockholm, Sweden' into the destination search box and click the search button to load results.
INFO     [Agent]   🦾 [ACTION 1/2] input_text: index: 27, text: Stockholm, Sweden, clear_existing: True
WARNING  [BrowserSession] ⚠️ Some framework events may have failed to trigger
INFO     [BrowserSession] ⌨️ Typed "Stockholm, Sweden" into element with index 27
INFO     [service] Page changed after action: actions click_element_by_index are not yet executed
INFO     [Agent] 

INFO     [Agent] 📍 Step 3:
INFO     [Agent]   👍 Eval: Successfully input 'Stockholm, Sweden' into the destination search box but did not yet click the search button to load results.
INFO     [Agent]   🎯 Next goal: Click the search button to perform the search and wait for the listings page to load with visible listing cards.
INFO     [Agent]   🦾 [ACTION 1/1] click_element_by_index: index: 34, while_holding_ctrl: False
INFO     [tools] 🖱️ Clicked element
INFO     [Agent] 

INFO     [Agent] 📍 Step 4:
INFO     [Agent]   👍 Eval: Successfully clicked the search button and loaded the Airbnb search results page with visible listing cards for Stockholm.
INFO     [Agent]   🎯 Next goal: Confirm no pop-ups or cookie banners are present and finalize task as completed since listings are visible.
INFO     [Agent]   🦾 [ACTION 1/1] done: text: I have navigated to Airbnb.com, searched for Stockholm, Sweden, and confirmed that the search results page is fully loa
INFO     [Agent] 
📄  Final Result: 
I have navigated to Airbnb.com, searched for 'Stockholm, Sweden', and confirmed that the search results page is fully loaded with listing cards visible. There were no pop-ups or cookie banners to close. Task completed successfully.


INFO     [Agent] ✅ Task completed successfully
⚠️  Could not capture screenshot: a bytes-like object is required, not 'str'

<IPython.core.display.HTML object>
<IPython.core.display.HTML object>
<IPython.core.display.HTML object>
<IPython.core.display.HTML object>
<IPython.core.display.HTML object>
<IPython.core.display.HTML object>
<IPython.core.display.HTML object>
<IPython.core.display.HTML object>
<IPython.core.display.HTML object>
<IPython.core.display.HTML object>
<IPython.core.display.HTML object>
<IPython.core.display.HTML object>
<IPython.core.display.HTML object>
WARNING  [cdp_use.client] WebSocket connection closed: no close frame received or sent

<IPython.core.display.HTML object>
<IPython.core.display.HTML object>
```

:::

## 主要收获与最佳实践

### 何时使用 Agent 与 Actor

| 场景 | 使用 Agent | 使用 Actor |
|----------|-----------|-----------|
| **动态布局** | ✅ AI 适应变化 | ❌ CSS 选择器失效 |
| **已知结构** | ❌ 比直接控制慢 | ✅ 快速且精确 |
| **查找元素** | ✅ 自然语言查询 | ❌ 需要精确选择器 |
| **时序控制** | ❌ 可预测性较差 | ✅ 完全时序控制 |
| **复杂工作流** | ✅ 处理意外 UI | ❌ 需要显式编码 |

### 浏览器使用最佳实践

1. **初期探索用 Agent** ：让 AI 先浏览复杂网站
2. **精确操作用 Actor** ：针对可预测元素用 CSS 选择器
3. **始终处理错误** ：网站会变——构建降级策略
4. **使用结构化输出** ：Pydantic 模型确保类型安全数据
5. **策略性添加延迟** ：触发变更后用 `asyncio.sleep()`
6. **截图调试** ：视觉调试极为有用
7. **组合方法** ：混合工作流发挥两种范式优势

### 现实应用场景

- **旅游预订** ：监控价格，自动订购，比较选项
- **电商** ：跟踪库存，价格比较，自动购买
- **数据采集** ：抓取动态站点，提取结构化数据
- **测试** ：基于视觉验证的自动化 UI 测试
- **监控** ：检查网站变化，对特定情况报警
- **表单自动化** ：智能填写复杂多步表单


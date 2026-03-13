# websearch_duc_tool - Web Search and Summarization Tool

[![Python](https://img.shields.io/badge/Python-3.9%2B-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## 📋 Overview

`websearch_duc_tool` is a comprehensive web search and summarization tool that performs the following functions:

1. **DuckDuckGo HTML Scraping**: Scraps DuckDuckGo search results to extract URLs for specific queries
2. **Web Page Rendering**: Extracts meaningful content from scraped URLs using headless browser rendering
3. **Intelligent Summarization**: Uses AI to summarize search results and return concise, relevant information

## 🎯 Features

### Core Capabilities

- ✅ **DuckDuckGo Search Scraping**: Scrape search results from DuckDuckGo HTML endpoint for any query
- ✅ **URL Extraction**: Parse and extract relevant URLs from search result pages
- ✅ **Web Content Rendering**: Render JavaScript-heavy web pages using Playwright
- ✅ **Content Extraction**: Extract meaningful content from rendered web pages (remove ads, navigation, etc.)
- ✅ **AI Summarization**: Summarize extracted content using LLM (OpenAI GPT-4o-mini / Claude)
- ✅ **Source Attribution**: Include citations and source links in summaries
- ✅ **Modular Architecture**: Following test-driven development with atomic modules

### Technical Highlights

- **Async/await**: Full async support for high-performance scraping
- **Fallback Strategy**: Multiple parsing strategies (BeautifulSoup, regex) for reliability
- **URL Decoding**: Automatic handling of DuckDuckGo redirect URLs
- **Rate Limiting**: Respectful request timing with retry logic
- **Deduplication**: Remove duplicate results from search

## 🏗️ Architecture

```
┌──────────────────────────────────────────────┐
│            user_interface.py                │
│          (Tool/Agent Interface)             │
└────────────────────────┬─────────────────────┘
                         ↓
┌──────────────────────────────────────────────┐
│              orchestrator.py                 │
│      (Pipeline Orchestration)                │
│    Search → Extract → Render → Summarize    │
└───────────────────┬──────────────────────────┘
             │
     ┌───────┴───────┐
     ↓               ↓
┌───────┐      ┌──────────┐
│scraper│      │ renderer │
│(ddg)  │      │(playwright)│
└───────┘      └──────────┘
                         ↓
                  ┌──────────┐
                  │summarizer│
                  │  (llm)   │
                  └──────────┘
```

**Data Flow**:
1. User provides search query
2. DuckDuckGoScraper searches and extracts URLs
3. WebRenderer extracts content from top N URLs
4. Summarizer processes content with LLM
5. Returns structured summary with citations

## 🚀 Installation

### Prerequisites

- Python 3.9+
- Playwright browsers (installed automatically)
- LLM API key (OpenAI, Anthropic, etc.)

### Setup

```bash
# Clone the repository
git clone <repo-url>
cd websearch_duc_tool

# Install dependencies
pip install -e .

# Install Playwright browsers
playwright install chromium

# Set up environment variables
cp .env.example .env
# Edit .env with your API keys
```

## 📖 Usage

### As a Python Tool

```python
from websearch_duc_tool import WebSearchAgent

# Initialize the agent
agent = WebSearchAgent(
    llm_provider="openai",
    api_key="your-api-key"
)

# Search and summarize
result = agent.search("latest Python async patterns 2026")

print(result["summary"])
print(f"Sources: {result['sources']}")
```

### As a Sub-Agent

```python
from websearch_duc_tool import WebSearchTool

# Register as a tool for AI agents
tool = WebSearchTool(agent_framework="crewai")

class WebResearcher:
    tools = [tool]
    
    def research(self, query):
        return tool.search(query)
```

## 📁 Project Structure

```
websearch_duc_tool/
├── src/
│   └── websearch_duc_tool/
│       ├── __init__.py
│       ├── duckduckgo_scraper.py   # DuckDuckGo HTML scraping
│       ├── renderer.py             # Web page rendering with Playwright
│       ├── summarizer.py           # LLM-based summarization
│       ├── orchestrator.py         # Pipeline orchestration
│       └── tools.py                # Tool/agent interface
├── tests/
│   ├── test_scraper.py             # Unit tests for scraper
│   ├── test_renderer.py            # Unit tests for renderer
│   ├── test_summarizer.py          # Unit tests for summarizer
│   └── test_orchestrator.py        # Integration tests
├── pyproject.toml                  # Dependencies
├── AGENTS.md                       # Behavioral guidelines
└── README.md                       # This file
```

## 🔧 Configuration

### Environment Variables (.env)

```ini
# LLM Provider
LLM_PROVIDER=openai
OPENAI_API_KEY=your_key_here

# Search Config
MAX_SEARCH_RESULTS=10
SUMMARIZE_TOP_N=3

# Performance
REQUEST_TIMEOUT=15.0
MAX_RETRIES=3
RATE_LIMIT_DELAY=0.5
```

## 🧪 Testing

```bash
# Run all tests
pytest -v

# Run with coverage
pytest --cov=src/websearch_duc_tool --cov-report=html

# Run specific module
pytest tests/test_scraper.py -v
```

## 🔄 Development Workflow

Following [AGENTS.md](AGENTS.md) guidelines:

1. **Plan**: Create todo list for each feature
2. **Develop**: One module at a time with tests
3. **Test**: pytest -v after each module
4. **Commit**: Atomic commits with conventional messages
5. **Push**: Push to remote after completion

## 📄 License

MIT License - see [LICENSE](LICENSE)

---

*Built following AGENTS.md behavioral guidelines with test-driven development*


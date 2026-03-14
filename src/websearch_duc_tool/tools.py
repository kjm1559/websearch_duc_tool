from typing import Dict, Union, Optional
import asyncio
from .orchestrator import WebSearchOrchestrator


class WebSearchTool:
    """Tool interface for agent frameworks."""

    def __init__(self, orchestrator: Optional[WebSearchOrchestrator] = None):
        self.orchestrator = orchestrator or WebSearchOrchestrator()

    async def search(self, query: str) -> Dict:
        """Search web and return summarized results."""
        return await self.orchestrator.search(query)

    def description(self) -> str:
        """Return tool description for agent frameworks."""
        return """Search the web using DuckDuckGo, extract content from top results, and provide AI-powered summaries with citations."""


class WebSearchAgent:
    """Simple agent interface."""

    def __init__(
        self,
        llm_provider: str = "openai",
        api_key: Optional[str] = None,
        **kwargs
    ):
        self.orchestrator = WebSearchOrchestrator(
            llm_provider=llm_provider,
            api_key=api_key,
            **kwargs
        )

    async def search(self, query: str) -> Dict:
        """Search and summarize."""
        return await self.orchestrator.search(query)

    def search_sync(self, query: str) -> Dict:
        """Synchronous search wrapper."""
        return asyncio.run(self.search(query))

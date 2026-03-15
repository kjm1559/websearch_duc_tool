from typing import List, Dict, Union, Optional
from .duckduckgo_scraper import DuckDuckGoScraper
from .renderer import WebRenderer
from .summarizer import Summarizer
import os


class WebSearchOrchestrator:
    """Orchestrates the complete search -> extract -> summarize pipeline."""

    def __init__(
        self,
        llm_provider: str = "openai",
        api_key: Optional[str] = None,
        llm_model: Optional[str] = None,
        llm_base_url: Optional[str] = None,
        search_base_url: Optional[str] = None,
        max_search_results: int = 10,
        summarize_top_n: int = 3,
        request_timeout: float = 60.0
    ):
        self.llm_provider = llm_provider
        self.api_key = api_key or os.getenv("OPENAI_API_KEY", "")
        self.llm_model = llm_model or os.getenv("OPENAI_MODEL", "gpt-4o-mini")
        self.llm_base_url = llm_base_url or os.getenv("OPENAI_BASE_URL", "")
        self.search_base_url = search_base_url or os.getenv("DUCKDUCKGO_BASE_URL", "")
        self.max_search_results = max_search_results
        self.summarize_top_n = summarize_top_n
        self.request_timeout = request_timeout

    async def search(
        self,
        query: str,
        max_results: Union[int, None] = None
    ) -> Dict:
        """Complete search pipeline: search -> extract -> summarize."""
        max_results = max_results or self.max_search_results

        # Stage 1: DuckDuckGo search
        scraper_kwargs = {"timeout": self.request_timeout}
        if self.search_base_url:
            scraper_kwargs["base_url"] = self.search_base_url
        async with DuckDuckGoScraper(**scraper_kwargs) as scraper:
            search_results = await scraper.search(query, max_results=max_results)

        if not search_results:
            return {
                "query": query,
                "summary": "No search results found.",
                "sources": [],
                "confidence": "low"
            }

        # Stage 2: Extract content from top URLs
        urls = [r["url"] for r in search_results[:self.summarize_top_n]]

        async with WebRenderer(timeout=self.request_timeout) as renderer:
            extracted_contents = await renderer.batch_extract(urls)

        # Stage 3: Summarize with LLM
        summarizer_kwargs = {
            "provider": self.llm_provider,
            "api_key": self.api_key,
            "model": self.llm_model
        }
        if self.llm_base_url:
            summarizer_kwargs["base_url"] = self.llm_base_url
        async with Summarizer(**summarizer_kwargs) as summarizer:
            result = await summarizer.summarize(
                query=query,
                search_results=extracted_contents
            )

        return {
            "query": query,
            "summary": result["summary"],
            "sources": result["sources"],
            "confidence": result["confidence"],
            "results_count": len(search_results)
        }

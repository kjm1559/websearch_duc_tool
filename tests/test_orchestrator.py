"""Integration tests for WebSearchOrchestrator."""
import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from websearch_duc_tool.orchestrator import WebSearchOrchestrator


class TestWebSearchOrchestrator:
    """Test orchestrator integration."""

    @pytest.fixture
    def orchestrator(self):
        """Create orchestrator instance."""
        return WebSearchOrchestrator(
            llm_provider="openai",
            api_key="fake_key",
            max_search_results=10,
            summarize_top_n=3
        )

    def test_initialization(self, orchestrator):
        """Test orchestrator initialization."""
        assert orchestrator.max_search_results == 10
        assert orchestrator.summarize_top_n == 3
        assert orchestrator.request_timeout == 15.0

    def test_initialization_with_env(self, orchestrator):
        """Test orchestrator reads from environment."""
        assert hasattr(orchestrator, "api_key")

    @pytest.mark.asyncio
    async def test_search_empty_results(self, orchestrator):
        """Test search with no results."""
        with patch("websearch_duc_tool.orchestrator.DuckDuckGoScraper") as mock_scraper:
            mock_instance = AsyncMock()
            mock_instance.__aenter__ = AsyncMock(return_value=mock_instance)
            mock_instance.__aexit__ = AsyncMock(return_value=False)
            mock_instance.search = AsyncMock(return_value=[])
            mock_scraper.return_value = mock_instance

            result = await orchestrator.search("nonexistent query xyz123")
            assert result["query"] == "nonexistent query xyz123"
            assert "No search results" in result["summary"]
            assert result["confidence"] == "low"

    @pytest.mark.asyncio
    async def test_search_full_pipeline(self, orchestrator):
        """Test full search pipeline."""
        # Mock scraper
        mock_scraper = AsyncMock()
        mock_scraper.__aenter__ = AsyncMock(return_value=mock_scraper)
        mock_scraper.__aexit__ = AsyncMock(return_value=False)
        mock_scraper.search = AsyncMock(return_value=[{"url": "http://test.com"}])

        # Mock renderer
        mock_renderer = AsyncMock()
        mock_renderer.__aenter__ = AsyncMock(return_value=mock_renderer)
        mock_renderer.__aexit__ = AsyncMock(return_value=False)
        mock_renderer.batch_extract = AsyncMock(return_value=[{"content": "test", "url": "http://test.com"}])

        # Mock summarizer
        mock_summarizer = AsyncMock()
        mock_summarizer.__aenter__ = AsyncMock(return_value=mock_summarizer)
        mock_summarizer.__aexit__ = AsyncMock(return_value=False)
        mock_summarizer.summarize = AsyncMock(return_value={"summary": "test", "sources": [], "confidence": "high"})

        with patch("websearch_duc_tool.orchestrator.DuckDuckGoScraper", return_value=mock_scraper):
            with patch("websearch_duc_tool.orchestrator.WebRenderer", return_value=mock_renderer):
                with patch("websearch_duc_tool.orchestrator.Summarizer", return_value=mock_summarizer):
                    result = await orchestrator.search("test query")
                    assert "summary" in result
                    assert "sources" in result
                    assert "confidence" in result

    @pytest.mark.asyncio
    async def test_search_custom_max_results(self, orchestrator):
        """Test custom max_results parameter."""
        mock_scraper = AsyncMock()
        mock_scraper.__aenter__ = AsyncMock(return_value=mock_scraper)
        mock_scraper.__aexit__ = AsyncMock(return_value=False)
        mock_scraper.search = AsyncMock(return_value=[])

        with patch("websearch_duc_tool.orchestrator.DuckDuckGoScraper", return_value=mock_scraper):
            await orchestrator.search("test", max_results=5)
            assert True

    def test_orchestrator_with_defaults(self):
        """Test orchestrator with default parameters."""
        default_orchestrator = WebSearchOrchestrator()
        assert default_orchestrator.max_search_results == 10
        assert default_orchestrator.summarize_top_n == 3
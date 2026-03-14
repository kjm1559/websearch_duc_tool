"""Unit tests for DuckDuckGoScraper."""
import pytest
import asyncio
from websearch_duc_tool.duckduckgo_scraper import DuckDuckGoScraper


class TestDuckDuckGoScraper:
    """Test DuckDuckGo scraper functionality."""

    @pytest.fixture
    def scraper(self):
        """Create scraper instance."""
        return DuckDuckGoScraper(timeout=15.0)

    def test_initialization(self, scraper):
        """Test scraper initialization."""
        assert scraper.timeout == 15.0
        assert scraper.session is None

    def test_headers(self, scraper):
        """Test browser headers."""
        headers = scraper._get_headers()
        assert "User-Agent" in headers
        assert "Mozilla/5.0" in headers["User-Agent"]
        assert "Accept" in headers

    def test_decode_url_no_redirect(self, scraper):
        """Test URL without redirect."""
        url = "https://example.com/page"
        result = scraper._decode_url(url)
        assert result == url

    def test_decode_url_with_ddg_redirect(self, scraper):
        """Test DuckDuckGo redirect URL."""
        url = "https://duckduckgo.com/l/?uddg=https%3A%2F%2Fexample.com%2Fpage"
        result = scraper._decode_url(url)
        assert "uddg" not in result
        assert "example.com" in result

    def test_clean_html_removal(self, scraper):
        """Test HTML tag removal."""
        text = "<p>Hello <b>World</b>!</p>"
        result = scraper._clean_html(text)
        assert "<" not in result
        assert "Hello" in result
        assert "World" in result
        assert "!" in result

    def test_clean_html_normalize_whitespace(self, scraper):
        """Test whitespace normalization."""
        text = "  Multiple   spaces    here  "
        result = scraper._clean_html(text)
        assert result == "Multiple spaces here"

    @pytest.mark.asyncio
    async def test_async_context_manager(self, scraper):
        """Test async context manager."""
        async with scraper as s:
            assert s.session is not None
        assert scraper.session is not None

    @pytest.mark.asyncio
    async def test_search_returns_list(self, scraper):
        """Test search returns list."""
        async with scraper:
            results = await scraper.search("Python programming language")
        assert isinstance(results, list)

    @pytest.mark.asyncio
    async def test_search_empty_results_on_invalid_query(self, scraper):
        """Test search with invalid query returns empty list."""
        async with scraper:
            results = await scraper.search("invalid query * ! @ # xyz123")
        assert isinstance(results, list)

    @pytest.mark.asyncio
    async def test_search_result_structure(self, scraper):
        """Test search result structure."""
        async with scraper:
            results = await scraper.search("Python programming", max_results=2)
        if results:
            result = results[0]
            assert "title" in result
            assert "url" in result
            assert "snippet" in result
            assert isinstance(result["title"], str)
            assert isinstance(result["url"], str)
            assert isinstance(result["snippet"], str)

    @pytest.mark.asyncio
    async def test_extract_urls(self, scraper):
        """Test URL extraction."""
        async with scraper:
            urls = await scraper.extract_urls("Python programming", max_results=3)
        assert isinstance(urls, list)
        if urls:
            assert all(isinstance(url, str) for url in urls)

    @pytest.mark.asyncio
    async def test_max_results_limit(self, scraper):
        """Test max results limit."""
        async with scraper:
            results = await scraper.search("Python", max_results=2)
        assert len(results) <= 2

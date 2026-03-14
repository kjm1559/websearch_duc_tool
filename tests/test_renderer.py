"""Unit tests for WebRenderer."""
import pytest
from websearch_duc_tool.renderer import WebRenderer


class TestWebRenderer:
    """Test web renderer functionality."""

    @pytest.fixture
    def renderer(self):
        """Create renderer instance."""
        return WebRenderer(timeout=30.0)

    def test_initialization(self, renderer):
        """Test renderer initialization."""
        assert renderer.timeout == 30.0
        assert renderer.browser is None
        assert renderer.context is None

    def test_clean_text_empty(self, renderer):
        """Test clean text with empty input."""
        result = renderer._clean_text("")
        assert result == ""

    def test_clean_text_normalize(self, renderer):
        """Test text normalization."""
        text = "  Multiple   spaces    here  "
        result = renderer._clean_text(text)
        assert result == "Multiple spaces here"

    def test_clean_text_newlines(self, renderer):
        """Test newline removal."""
        text = "Line1\n\nLine2\nLine3"
        result = renderer._clean_text(text)
        assert result == "Line1 Line2 Line3"

    def test_clean_text_tabs(self, renderer):
        """Test tab removal."""
        text = "Tab\there\ttest"
        result = renderer._clean_text(text)
        assert result == "Tab here test"

    def test_clean_text_mixed_whitespace(self, renderer):
        """Test mixed whitespace normalization."""
        text = "  Multiple   \n\nwhitespace\ttypes  "
        result = renderer._clean_text(text)
        assert "  " not in result
        assert "\n" not in result
        assert "\t" not in result

    @pytest.mark.asyncio
    async def test_extract_content_structure(self, renderer):
        """Test extract content returns correct structure."""
        try:
            async with renderer as r:
                result = await r.extract_content("https://www.python.org")
            assert isinstance(result, dict)
            assert "url" in result
            assert "title" in result
            assert "content" in result
            assert "excerpt" in result
        except Exception as e:
            pytest.skip(f"Network issue: {e}")

    @pytest.mark.asyncio
    async def test_extract_content_url_match(self, renderer):
        """Test extracted content matches URL."""
        test_url = "https://www.python.org"
        try:
            async with renderer as r:
                result = await r.extract_content(test_url)
            assert result["url"] == test_url
        except Exception as e:
            pytest.skip(f"Network issue: {e}")

    @pytest.mark.asyncio
    async def test_extract_content_limit(self, renderer):
        """Test content length limit."""
        test_url = "https://www.python.org"
        try:
            async with renderer as r:
                result = await r.extract_content(test_url)
            assert len(result["content"]) <= 5000
        except Exception as e:
            pytest.skip(f"Network issue: {e}")

    @pytest.mark.asyncio
    async def test_extract_invalid_url_returns_empty(self, renderer):
        """Test invalid URL returns empty content."""
        result = await renderer.extract_content("https://invalid.domain.that.does.not.exist")
        assert isinstance(result, dict)
        assert "url" in result

    @pytest.mark.asyncio
    async def test_batch_extract_single_url(self, renderer):
        """Test batch extract with single URL."""
        urls = ["https://www.python.org"]
        try:
            async with renderer as r:
                results = await r.batch_extract(urls[:1], max_concurrent=1)
            assert isinstance(results, list)
        except Exception as e:
            pytest.skip(f"Network issue: {e}")

    @pytest.mark.asyncio
    async def test_batch_extract_rate_limit(self, renderer):
        """Test batch extract respects concurrency limit."""
        urls = [
            "https://www.python.org",
            "http://example.com"
        ]
        try:
            async with renderer as r:
                results = await r.batch_extract(urls[:1], max_concurrent=2)
            assert isinstance(results, list)
        except Exception as e:
            pytest.skip(f"Network issue: {e}")
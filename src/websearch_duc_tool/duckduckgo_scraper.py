from urllib.parse import urlparse, parse_qs, unquote
import httpx
from bs4 import BeautifulSoup
import re
from typing import List, Dict
import asyncio


class DuckDuckGoScraper:
    """DuckDuckGo HTML scraper with async HTTP client."""

    BASE_URL = "https://html.duckduckgo.com/html/"

    def __init__(self, timeout: float = 15.0):
        self.timeout = timeout
        self.session = None

    async def __aenter__(self):
        self.session = httpx.AsyncClient(
            timeout=self.timeout,
            headers=self._get_headers(),
            follow_redirects=True
        )
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.aclose()

    def _get_headers(self) -> Dict[str, str]:
        """Return realistic browser headers."""
        return {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.5",
            "Accept-Encoding": "gzip, deflate",
            "Connection": "keep-alive",
        }

    def _decode_url(self, url: str) -> str:
        """Decode DuckDuckGo redirect URLs."""
        if "uddg=" not in url:
            return url

        parsed = urlparse(url)
        params = parse_qs(parsed.query)
        return unquote(params["uddg"][0]) if "uddg" in params else url

    def _clean_html(self, text: str) -> str:
        """Remove HTML tags and normalize whitespace."""
        text = re.sub(r"<[^>]+>", " ", text)
        text = re.sub(r"\s+", " ", text).strip()
        return text

    async def search(
        self,
        query: str,
        max_results: int = 10
    ) -> List[Dict[str, str]]:
        """Search DuckDuckGo and return results."""
        params = {"q": query}

        try:
            response = await self.session.get(self.BASE_URL, params=params)
            response.raise_for_status()

            soup = BeautifulSoup(response.text, "lxml")
            result_divs = soup.select("div.result")

            results = []
            for div in result_divs[:max_results]:
                title_elem = div.select_one("a.result__a")
                if not title_elem:
                    continue

                title = self._clean_html(title_elem.get_text())
                href = title_elem.get("href")
                url = self._decode_url(str(href)) if href else ""

                snippet_elem = div.select_one("a.result__snippet")
                snippet = self._clean_html(snippet_elem.get_text()) if snippet_elem else ""

                results.append({
                    "title": title,
                    "url": url,
                    "snippet": snippet
                })

            return results

        except httpx.HTTPError as e:
            print(f"Search failed: {e}")
            return []

    async def extract_urls(
        self,
        query: str,
        max_results: int = 10
    ) -> List[str]:
        """Extract only URLs from search results."""
        results = await self.search(query, max_results)
        return [r["url"] for r in results]

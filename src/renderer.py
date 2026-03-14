from playwright.async_api import async_playwright, Page
from bs4 import BeautifulSoup
from typing import List, Dict
import asyncio


class WebRenderer:
    """Web page renderer using Playwright for JavaScript-heavy pages."""

    def __init__(self, timeout: float = 30.0):
        self.timeout = timeout
        self.browser = None
        self.context = None

    async def __aenter__(self):
        self.playwright = await async_playwright().start()
        self.browser = await self.playwright.chromium.launch(
            headless=True,
            args=["--disable-blink-features=AutomationControlled"]
        )
        self.context = await self.browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        )
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        try:
            if self.context:
                await self.context.close()
            if self.browser:
                await self.browser.close()
            if self.playwright:
                await self.playwright.stop()
        except Exception:
            pass

    def _clean_text(self, text: str) -> str:
        """Clean and normalize extracted text."""
        if not text:
            return ""
        cleaned = " ".join(text.split())
        return cleaned.strip()

    async def extract_content(self, url: str, page: Page = None) -> Dict[str, str]:
        """Extract meaningful content from a URL."""
        try:
            # Use provided page or create new one
            if page is None:
                page = await self.context.new_page()

            await page.goto(url, timeout=self.timeout * 1000, wait_until="networkidle")
            await asyncio.sleep(1)  # Wait for dynamic content

            html = await page.content()
            soup = BeautifulSoup(html, "lxml")

            # Remove unwanted elements
            for tag in soup.find_all(["script", "style", "nav", "footer", "header"]):
                tag.decompose()

            # Extract main content
            main_content = soup.find("main") or soup.find("article") or soup.find("body")
            if not main_content:
                main_content = soup

            title = soup.find("title")
            title_text = title.get_text().strip() if title else ""

            text_content = main_content.get_text()
            text_content = self._clean_text(text_content)

            # Extract metadata
            meta_desc = soup.find("meta", attrs={"name": "description"})
            description = meta_desc["content"] if meta_desc and meta_desc.get("content") else ""

            return {
                "url": url,
                "title": title_text,
                "description": description,
                "content": text_content[:5000],  # Limit length
                "excerpt": text_content[:200] + "..." if len(text_content) > 200 else text_content
            }

        except Exception as e:
            print(f"Failed to extract content from {url}: {e}")
            return {
                "url": url,
                "title": "",
                "description": "",
                "content": "",
                "excerpt": ""
            }
        finally:
            if page and self.context:
                try:
                    await page.close()
                except Exception:
                    pass

    async def batch_extract(
        self,
        urls: List[str],
        max_concurrent: int = 3
    ) -> List[Dict[str, str]]:
        """Extract content from multiple URLs with rate limiting."""
        semaphore = asyncio.Semaphore(max_concurrent)

        async def limited_extract(url: str) -> Dict[str, str]:
            async with semaphore:
                return await self.extract_content(url)

        tasks = [limited_extract(url) for url in urls]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        # Filter out exceptions
        return [
            result for result in results
            if isinstance(result, dict) and result.get("content")
        ]

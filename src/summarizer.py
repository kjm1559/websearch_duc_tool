from openai import AsyncOpenAI
import asyncio
from typing import List, Dict, Optional
import os


class Summarizer:
    """LLM-based content summarization."""

    def __init__(
        self,
        provider: str = "openai",
        api_key: Optional[str] = None,
        model: Optional[str] = None,
        base_url: Optional[str] = None
    ):
        self.provider = provider
        self.api_key = api_key or os.getenv("OPENAI_API_KEY", "")
        self.model = model or os.getenv("OPENAI_MODEL", "gpt-4o-mini")
        self.base_url = base_url or os.getenv("OPENAI_BASE_URL", "")
        self.client = None

    async def __aenter__(self):
        if self.provider == "openai":
            if self.base_url:
                self.client = AsyncOpenAI(
                    api_key=self.api_key,
                    base_url=self.base_url
                )
            else:
                self.client = AsyncOpenAI(api_key=self.api_key)
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        pass

    def _create_summary_prompt(
        self,
        query: str,
        contents: List[Dict[str, str]]
    ) -> str:
        context = "\n\n".join([
            f"Source {i+1}: [{item['title']}]({item['url']})\n{item['content'][:500]}"
            for i, item in enumerate(contents[:5])
        ])

        return f"""Based on these search results about '{query}' provide a concise summary:

{context}

Requirements:
1. Summarize key points in 2-3 paragraphs
2. Include specific facts and data points
3. Cite sources clearly
4. Mention conflicting information if any
5. Provide confidence level (high/medium/low)

Format:
Summary:
[Your summary here]

Citations:
[Source 1]
[Source 2]"""

    async def summarize(
        self,
        query: str,
        search_results: List[Dict[str, str]],
        max_sources: int = 5
    ) -> Dict:
        """Summarize search results."""
        if not search_results:
            return {
                "summary": "No search results available.",
                "sources": [],
                "confidence": "low"
            }

        # Prepare content from search results
        contents = [
            {
                "title": r.get("title", ""),
                "url": r.get("url", ""),
                "content": r.get("content", "") or r.get("excerpt", "")
            }
            for r in search_results[:max_sources]
        ]

        prompt = self._create_summary_prompt(query, contents)

        try:
            if self.provider == "openai" and self.client:
                response = await self.client.chat.completions.create(
                    model=self.model,
                    messages=[
                        {
                            "role": "system",
                            "content": "You are a helpful research assistant that summarizes web search results with citations."
                        },
                        {
                            "role": "user",
                            "content": prompt
                        }
                    ],
                    max_tokens=1000,
                    temperature=0.3
                )

                summary_text = response.choices[0].message.content or ""
                reasoning = response.choices[0].message.reasoning or ""
                
                # For Ollama/qwen3.5: reasoning contains the actual response
                if reasoning and not summary_text:
                    summary_text = reasoning

                return {
                    "summary": summary_text,
                    "sources": [r["url"] for r in search_results[:max_sources]],
                    "confidence": "high"
                }

            else:
                # Fallback: simple concatenation
                summary = "\n\n".join([
                    f"{item['title']} ({item['url']}): {item['content'][:200]}"
                    for item in contents
                ])

                return {
                    "summary": summary,
                    "sources": [r["url"] for r in search_results[:max_sources]],
                    "confidence": "medium"
                }

        except Exception as e:
            print(f"Summarization failed: {e}")
            return {
                "summary": f"Error during summarization: {str(e)}",
                "sources": [],
                "confidence": "low"
            }

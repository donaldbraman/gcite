"""
cite-assist API client for semantic search.
"""

import httpx
from typing import List, Dict, Optional
import logging
from tenacity import retry, stop_after_attempt, wait_exponential

from config.settings import settings

logger = logging.getLogger(__name__)


class CiteAssistClient:
    """Client for cite-assist semantic search API."""

    def __init__(self):
        """Initialize the cite-assist client."""
        self.base_url = settings.CITE_ASSIST_API_URL
        self.api_key = settings.CITE_ASSIST_API_KEY
        self.client = httpx.AsyncClient(
            base_url=self.base_url,
            timeout=30.0
        )

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        reraise=True
    )
    async def search(
        self,
        query: str,
        limit: int = 20,
        search_mode: str = "chunks"
    ) -> List[Dict]:
        """
        Search cite-assist for relevant chunks.

        Args:
            query: Search query
            limit: Maximum number of results to return
            search_mode: "chunks", "summaries", or "both"

        Returns:
            List of chunk dictionaries with metadata

        Raises:
            httpx.HTTPStatusError: If the API returns an error status
            httpx.TimeoutException: If the request times out
        """
        payload = {
            "query": query,
            "limit": limit,
            "search_mode": search_mode
        }

        headers = {}
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"

        try:
            logger.info(f"Searching cite-assist for: '{query}' (limit={limit})")
            response = await self.client.post(
                "/api/v1/search",
                json=payload,
                headers=headers
            )

            response.raise_for_status()
            data = response.json()

            results = data.get("results", [])
            logger.info(f"cite-assist returned {len(results)} results")

            return results

        except httpx.TimeoutException:
            logger.warning("cite-assist request timeout, retrying...")
            raise
        except httpx.HTTPStatusError as e:
            if e.response.status_code >= 500:
                logger.warning(f"cite-assist server error {e.response.status_code}, retrying...")
                raise
            else:
                # Client errors (4xx) should not retry
                logger.error(f"cite-assist client error {e.response.status_code}")
                return []

    async def close(self):
        """Close the HTTP client."""
        await self.client.aclose()


# Dependency for FastAPI
async def get_cite_assist_client() -> CiteAssistClient:
    """Dependency to get cite-assist client instance."""
    client = CiteAssistClient()
    try:
        yield client
    finally:
        await client.close()

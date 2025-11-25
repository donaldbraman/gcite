"""
Rank Agent - Re-order chunks by importance and relevance.
"""

import json
import logging
from typing import List, Dict, Optional

from .base import BaseAgent

logger = logging.getLogger(__name__)


class RankAgent(BaseAgent):
    """AI agent for ranking citation chunks by importance."""

    async def rank(
        self,
        query: str,
        context: Optional[str],
        chunks: List[Dict]
    ) -> List[Dict]:
        """
        Rank chunks by relevance and importance.

        Args:
            query: User's search query
            context: Optional context
            chunks: List of filtered chunks

        Returns:
            Chunks sorted by importance with rank assignments
        """
        if not self.enabled:
            logger.info("Rank agent disabled - returning chunks in original order")
            # Assign sequential ranks
            for i, chunk in enumerate(chunks):
                chunk['agent_rank'] = i + 1
            return chunks

        if not chunks:
            return []

        if len(chunks) == 1:
            # No need to rank single chunk
            chunks[0]['agent_rank'] = 1
            return chunks

        logger.info(f"Ranking {len(chunks)} chunks")

        try:
            # Prepare chunks summary for ranking
            chunks_summary = []
            for i, chunk in enumerate(chunks):
                metadata = chunk.get('metadata', {})
                chunks_summary.append({
                    "id": i,
                    "text_preview": chunk.get('text', '')[:200],
                    "source": metadata.get('title', 'Unknown'),
                    "year": metadata.get('year', 'Unknown'),
                    "similarity_score": chunk.get('score', 0.0)
                })

            # Build prompt
            prompt = f"""You are a citation ranking specialist. Rank these chunks by their importance and relevance to the query.

Query: {query}
{f"Context: {context}" if context else ""}

Chunks to rank:
{json.dumps(chunks_summary, indent=2)}

Rank by:
1. Direct relevance to query (primary factor)
2. Strength and quality of evidence
3. Source credibility and impact
4. Recency (prefer newer unless historical context needed)

Respond ONLY with valid JSON in this exact format:
{{
  "ranked_ids": [2, 0, 5, 1],
  "reasoning": "brief explanation of ranking logic"
}}"""

            # Generate response
            response_text = await self.generate_content(
                prompt,
                temperature=0.2,
                max_output_tokens=500
            )

            if not response_text:
                # API error - return original order
                logger.warning("Rank agent failed - using original order")
                for i, chunk in enumerate(chunks):
                    chunk['agent_rank'] = i + 1
                return chunks

            # Parse JSON response
            cleaned_text = response_text.strip()
            if cleaned_text.startswith('```'):
                lines = cleaned_text.split('\n')
                cleaned_text = '\n'.join(
                    line for line in lines
                    if not line.startswith('```')
                )

            result = json.loads(cleaned_text)
            ranked_ids = result.get('ranked_ids', [])
            reasoning = result.get('reasoning', '')

            logger.info(f"Ranking reasoning: {reasoning}")

            # Reorder chunks based on ranking
            ranked_chunks = []
            used_ids = set()

            for rank, chunk_id in enumerate(ranked_ids):
                if chunk_id < len(chunks) and chunk_id not in used_ids:
                    chunk = chunks[chunk_id].copy()
                    chunk['agent_rank'] = rank + 1
                    chunk['rank_reasoning'] = reasoning
                    ranked_chunks.append(chunk)
                    used_ids.add(chunk_id)

            # Add any chunks not in ranking (shouldn't happen, but safety)
            for i, chunk in enumerate(chunks):
                if i not in used_ids:
                    chunk = chunk.copy()
                    chunk['agent_rank'] = len(ranked_chunks) + 1
                    chunk['rank_reasoning'] = "Not included in agent ranking"
                    ranked_chunks.append(chunk)

            logger.info(f"Successfully ranked {len(ranked_chunks)} chunks")
            return ranked_chunks

        except json.JSONDecodeError as e:
            logger.warning(f"JSON parse error in ranking: {e}")
            # Return original order on parse error
            for i, chunk in enumerate(chunks):
                chunk['agent_rank'] = i + 1
            return chunks

        except Exception as e:
            logger.error(f"Ranking error: {e}", exc_info=True)
            # Return original order on error
            for i, chunk in enumerate(chunks):
                chunk['agent_rank'] = i + 1
            return chunks


# Dependency for FastAPI
async def get_rank_agent() -> RankAgent:
    """Dependency to get rank agent instance."""
    return RankAgent()

"""
Filter Agent - Relevance evaluation for citation chunks.
"""

import asyncio
import json
import logging
from typing import List, Dict, Optional

from .base import BaseAgent

logger = logging.getLogger(__name__)


class FilterAgent(BaseAgent):
    """AI agent for filtering irrelevant citation chunks."""

    async def filter(
        self,
        query: str,
        context: Optional[str],
        chunks: List[Dict],
        threshold: float = 0.7
    ) -> List[Dict]:
        """
        Filter chunks by relevance to the query.

        Args:
            query: User's search query
            context: Optional context about user's intent
            chunks: List of chunks from semantic search
            threshold: Minimum confidence score to keep (0.0-1.0)

        Returns:
            Filtered list of chunks with relevance scores
        """
        if not self.enabled:
            logger.info("Filter agent disabled - returning all chunks")
            return chunks

        if not chunks:
            return []

        logger.info(f"Filtering {len(chunks)} chunks with threshold {threshold}")

        # Evaluate chunks in parallel for performance
        tasks = [
            self._evaluate_chunk(query, context, chunk)
            for chunk in chunks
        ]

        evaluations = await asyncio.gather(*tasks, return_exceptions=True)

        # Filter based on threshold
        filtered = []
        for chunk, evaluation in zip(chunks, evaluations):
            # Handle exceptions from individual evaluations
            if isinstance(evaluation, Exception):
                logger.warning(f"Evaluation failed: {evaluation}")
                # On error, default to keeping chunk
                chunk['agent_filtered'] = False
                chunk['relevance_score'] = chunk.get('score', 0.5)
                filtered.append(chunk)
                continue

            if evaluation['relevant'] and evaluation['confidence'] >= threshold:
                chunk['agent_filtered'] = True
                chunk['relevance_score'] = evaluation['confidence']
                chunk['filter_reasoning'] = evaluation['reasoning']
                filtered.append(chunk)
            else:
                logger.debug(
                    f"Filtered out chunk (confidence={evaluation['confidence']:.2f}): "
                    f"{chunk.get('text', '')[:50]}..."
                )

        logger.info(f"Filtered to {len(filtered)} chunks ({len(filtered)/len(chunks)*100:.1f}%)")
        return filtered

    async def _evaluate_chunk(
        self,
        query: str,
        context: Optional[str],
        chunk: Dict
    ) -> Dict:
        """
        Evaluate a single chunk for relevance.

        Args:
            query: User's search query
            context: Optional context
            chunk: Chunk data with text and metadata

        Returns:
            Dictionary with relevance evaluation
        """
        # Extract chunk data
        chunk_text = chunk.get('text', '')
        metadata = chunk.get('metadata', {})
        source_title = metadata.get('title', 'Unknown')
        year = metadata.get('year', 'Unknown')

        # Build prompt
        prompt = f"""You are a citation relevance evaluator. Determine if this chunk is relevant to the user's query.

Query: {query}
{f"Context: {context}" if context else ""}

Chunk Text:
{chunk_text}

Source: {source_title} ({year})

Evaluate:
1. Does this chunk directly address the query topic?
2. Is the information substantive (not just tangential mention)?
3. Would this be a good citation for someone writing about the query topic?
4. Is the source credible and relevant?

Respond ONLY with valid JSON in this exact format:
{{
  "relevant": true,
  "confidence": 0.95,
  "reasoning": "brief explanation"
}}"""

        try:
            # Generate response
            response_text = await self.generate_content(
                prompt,
                temperature=0.1,  # Low temp for consistent evaluation
                max_output_tokens=200
            )

            if not response_text:
                # API error - default to keeping chunk
                return {
                    "relevant": True,
                    "confidence": 0.5,
                    "reasoning": "Error in evaluation - defaulted to keeping chunk"
                }

            # Parse JSON response
            # Clean response text (remove markdown code blocks if present)
            cleaned_text = response_text.strip()
            if cleaned_text.startswith('```'):
                # Remove markdown code blocks
                lines = cleaned_text.split('\n')
                cleaned_text = '\n'.join(
                    line for line in lines
                    if not line.startswith('```')
                )

            result = json.loads(cleaned_text)

            # Validate result structure
            if not isinstance(result, dict):
                raise ValueError("Response is not a dictionary")
            if 'relevant' not in result or 'confidence' not in result:
                raise ValueError("Missing required fields")

            # Ensure confidence is in range
            result['confidence'] = max(0.0, min(1.0, float(result['confidence'])))

            return result

        except json.JSONDecodeError as e:
            logger.warning(f"JSON parse error: {e}, response: {response_text[:100]}")
            # Default to keeping chunk on parse error
            return {
                "relevant": True,
                "confidence": 0.5,
                "reasoning": f"JSON parse error: {str(e)}"
            }
        except Exception as e:
            logger.error(f"Evaluation error: {e}", exc_info=True)
            # Default to keeping chunk on error
            return {
                "relevant": True,
                "confidence": 0.5,
                "reasoning": f"Error in evaluation: {str(e)}"
            }


# Dependency for FastAPI
async def get_filter_agent() -> FilterAgent:
    """Dependency to get filter agent instance."""
    return FilterAgent()

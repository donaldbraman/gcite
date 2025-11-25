"""
Format Agent - Create professional citation output.
"""

import json
import logging
from typing import List, Dict

from .base import BaseAgent

logger = logging.getLogger(__name__)


class FormatAgent(BaseAgent):
    """AI agent for formatting citations professionally."""

    async def format(
        self,
        chunks: List[Dict],
        style: str = "APA",
        include_context: bool = True
    ) -> str:
        """
        Format chunks as professional citations.

        Args:
            chunks: Ranked chunks to format
            style: Citation style (APA, MLA, Chicago, Bluebook)
            include_context: Include contextual snippets

        Returns:
            Formatted citation text ready for clipboard
        """
        if not chunks:
            return "No citations found."

        if not self.enabled:
            logger.info("Format agent disabled - using basic formatting")
            return self._format_basic(chunks, style, include_context)

        logger.info(f"Formatting {len(chunks)} chunks in {style} style")

        try:
            # Prepare chunks for formatting
            chunks_data = []
            for chunk in chunks:
                metadata = chunk.get('metadata', {})
                chunks_data.append({
                    "rank": chunk.get('agent_rank', 0),
                    "text": chunk.get('text', ''),
                    "source": {
                        "title": metadata.get('title', 'Unknown'),
                        "authors": metadata.get('authors', []),
                        "year": metadata.get('year', 'Unknown'),
                        "citation": metadata.get('citation', '')
                    },
                    "relevance": chunk.get('relevance_score', 0.0)
                })

            # Build prompt
            prompt = f"""You are a citation formatting specialist. Format these chunks as professional citations.

Citation Style: {style}
Include Context: {include_context}

Chunks to format:
{json.dumps(chunks_data, indent=2)}

Format requirements:
1. Clean, professional output ready to paste into a document
2. Proper {style} citation style formatting
3. Include relevance indicators (use stars: ★★★★★ for high, ★★★☆☆ for medium, etc.)
4. Group by source if multiple chunks from same paper
5. Include key quotes from the text
6. Add visual separators (use ─ characters) for readability
7. Make it immediately useful for academic writing

Output the formatted citations as plain text."""

            # Generate response
            response_text = await self.generate_content(
                prompt,
                temperature=0.3,  # Slightly higher for creative formatting
                max_output_tokens=2000
            )

            if not response_text:
                # API error - use basic formatting
                logger.warning("Format agent failed - using basic formatting")
                return self._format_basic(chunks, style, include_context)

            # Add header and footer
            output = self._add_wrapper(response_text, len(chunks))

            logger.info(f"Successfully formatted {len(chunks)} chunks")
            return output

        except Exception as e:
            logger.error(f"Formatting error: {e}", exc_info=True)
            # Fallback to basic formatting
            return self._format_basic(chunks, style, include_context)

    def _format_basic(
        self,
        chunks: List[Dict],
        style: str,
        include_context: bool
    ) -> str:
        """
        Basic formatting fallback when AI agent unavailable.

        Args:
            chunks: Chunks to format
            style: Citation style
            include_context: Include context snippets

        Returns:
            Basic formatted output
        """
        lines = []

        for chunk in chunks:
            rank = chunk.get('agent_rank', 0)
            text = chunk.get('text', '')
            relevance = chunk.get('relevance_score', 0.0)
            metadata = chunk.get('metadata', {})

            title = metadata.get('title', 'Unknown')
            citation = metadata.get('citation', '')

            # Calculate stars based on relevance
            stars = '★' * int(relevance * 5) + '☆' * (5 - int(relevance * 5))

            lines.extend([
                f"[{rank}] {title}",
                "─" * 50,
                f"Relevance: {stars} ({relevance:.2f})",
                ""
            ])

            if include_context:
                lines.extend([
                    f'"{text}"',
                    ""
                ])

            lines.extend([
                f"Citation: {citation}",
                "",
                "─" * 50,
                ""
            ])

        output = "\n".join(lines)
        return self._add_wrapper(output, len(chunks))

    def _add_wrapper(self, content: str, count: int) -> str:
        """
        Add header and footer to formatted output.

        Args:
            content: Formatted content
            count: Number of citations

        Returns:
            Content with header and footer
        """
        return f"""━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📚 CITATION RESULTS ({count} citations)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

{content.strip()}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Generated by gCite • cite-assist + Gemini AI
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"""


# Dependency for FastAPI
async def get_format_agent() -> FormatAgent:
    """Dependency to get format agent instance."""
    return FormatAgent()

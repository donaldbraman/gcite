"""
API route handlers for gCite backend.
"""

from fastapi import APIRouter, HTTPException, Depends
import logging
import time

from .models import SearchRequest, SearchResponse, Chunk, Source
from services.cite_assist import CiteAssistClient, get_cite_assist_client
from agents.filter import FilterAgent, get_filter_agent
from agents.rank import RankAgent, get_rank_agent
from agents.format import FormatAgent, get_format_agent

router = APIRouter()
logger = logging.getLogger(__name__)


@router.post("/search", response_model=SearchResponse)
async def search_citations(
    request: SearchRequest,
    cite_assist: CiteAssistClient = Depends(get_cite_assist_client),
    filter_agent: FilterAgent = Depends(get_filter_agent),
    rank_agent: RankAgent = Depends(get_rank_agent),
    format_agent: FormatAgent = Depends(get_format_agent)
):
    """
    Search for relevant citations with AI-powered filtering, ranking, and formatting.

    Process (Phase 2):
    1. Semantic search via cite-assist
    2. AI filtering for relevance (optional)
    3. AI ranking by importance
    4. AI formatting for output

    If AI agents are disabled (no API key), falls back to basic formatting.
    """
    start_time = time.time()

    try:
        # Step 1: Semantic search via cite-assist
        logger.info(f"Searching for: {request.query}")
        # Get more results than requested to allow for filtering
        search_limit = request.max_results * 2 if request.filter else request.max_results
        raw_results = await cite_assist.search(
            query=request.query,
            limit=search_limit
        )

        if not raw_results:
            return SearchResponse(
                query=request.query,
                results_count=0,
                chunks=[],
                formatted_output="No results found. Try refining your query.",
                processing_time_ms=int((time.time() - start_time) * 1000)
            )

        # Convert raw results to dict format for agents
        chunks_data = []
        for result in raw_results:
            chunks_data.append({
                "chunk_id": result.get("chunk_id", ""),
                "text": result.get("text", ""),
                "metadata": result.get("metadata", {}),
                "source_key": result.get("source_key", ""),
                "score": result.get("score", 0.0)
            })

        # Step 2: AI filtering (if enabled)
        if request.filter and filter_agent.enabled:
            logger.info("Filtering chunks with AI")
            filtered_data = await filter_agent.filter(
                query=request.query,
                context=request.context,
                chunks=chunks_data,
                threshold=request.min_relevance
            )
        else:
            filtered_data = chunks_data
            logger.info("Skipping AI filtering")

        # Limit to requested number after filtering
        filtered_data = filtered_data[:request.max_results]

        if not filtered_data:
            return SearchResponse(
                query=request.query,
                results_count=0,
                chunks=[],
                formatted_output="No relevant citations found after filtering. Try broadening your query.",
                processing_time_ms=int((time.time() - start_time) * 1000)
            )

        # Step 3: AI ranking (if enabled)
        if rank_agent.enabled:
            logger.info("Ranking chunks with AI")
            ranked_data = await rank_agent.rank(
                query=request.query,
                context=request.context,
                chunks=filtered_data
            )
        else:
            ranked_data = filtered_data
            # Assign sequential ranks
            for i, chunk in enumerate(ranked_data):
                chunk['agent_rank'] = i + 1
            logger.info("Skipping AI ranking")

        # Convert to Chunk objects
        chunks = []
        for chunk_data in ranked_data:
            metadata = chunk_data.get('metadata', {})
            chunk = Chunk(
                id=chunk_data.get("chunk_id", ""),
                text=chunk_data.get("text", ""),
                source=Source(
                    title=metadata.get("title", "Unknown"),
                    authors=metadata.get("authors", []),
                    year=metadata.get("year", 0),
                    citation=metadata.get("citation", ""),
                    item_key=chunk_data.get("source_key")
                ),
                relevance_score=chunk_data.get("relevance_score", chunk_data.get("score", 0.0)),
                agent_filtered=chunk_data.get("agent_filtered", False),
                agent_rank=chunk_data.get("agent_rank", 0)
            )
            chunks.append(chunk)

        # Step 4: AI formatting (if enabled)
        if format_agent.enabled:
            logger.info("Formatting output with AI")
            # Convert chunks back to dict for formatting
            chunks_for_format = []
            for chunk in chunks:
                chunks_for_format.append({
                    "agent_rank": chunk.agent_rank,
                    "text": chunk.text,
                    "metadata": {
                        "title": chunk.source.title,
                        "authors": chunk.source.authors,
                        "year": chunk.source.year,
                        "citation": chunk.source.citation
                    },
                    "relevance_score": chunk.relevance_score
                })

            formatted_output = await format_agent.format(
                chunks=chunks_for_format,
                style=request.citation_style.value,
                include_context=request.include_context
            )
        else:
            logger.info("Using basic formatting")
            formatted_output = _format_basic(chunks, request.citation_style.value)

        processing_time = int((time.time() - start_time) * 1000)
        logger.info(f"Search completed in {processing_time}ms with {len(chunks)} results")

        return SearchResponse(
            query=request.query,
            results_count=len(chunks),
            chunks=chunks,
            formatted_output=formatted_output,
            processing_time_ms=processing_time
        )

    except Exception as e:
        logger.error(f"Search failed: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Search failed: {str(e)}"
        )


def _format_basic(chunks: list[Chunk], style: str) -> str:
    """
    Basic formatting without AI (Phase 1).
    Phase 2 will replace this with AI-powered formatting.
    """
    if not chunks:
        return "No citations found."

    lines = [
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━",
        f"📚 CITATION RESULTS ({len(chunks)} found)",
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━",
        ""
    ]

    for chunk in chunks:
        lines.extend([
            f"[{chunk.agent_rank}] {chunk.source.title}",
            "─────────────────────────────────────────────────",
            f"Relevance: {chunk.relevance_score:.2f}",
            "",
            f'"{chunk.text}"',
            "",
            f"Citation: {chunk.source.citation}",
            "",
            "─────────────────────────────────────────────────",
            ""
        ])

    lines.extend([
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━",
        "Generated by gCite • cite-assist semantic search",
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    ])

    return "\n".join(lines)

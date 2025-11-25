"""
Pydantic data models for API requests and responses.
"""

from pydantic import BaseModel, Field
from typing import List, Optional
from enum import Enum


class CitationStyle(str, Enum):
    """Supported citation styles."""
    APA = "APA"
    MLA = "MLA"
    CHICAGO = "Chicago"
    BLUEBOOK = "Bluebook"


class SearchRequest(BaseModel):
    """Search request from client."""
    query: str = Field(..., min_length=1, max_length=1000, description="Search query")
    context: Optional[str] = Field(None, max_length=2000, description="Optional context about user's intent")
    max_results: int = Field(10, ge=1, le=50, description="Maximum number of results to return")
    citation_style: CitationStyle = Field(CitationStyle.APA, description="Citation format style")
    filter: bool = Field(True, description="Enable AI filtering (Phase 2)")
    min_relevance: float = Field(0.7, ge=0.0, le=1.0, description="Minimum relevance score")
    include_context: bool = Field(True, description="Include context snippets in output")


class Source(BaseModel):
    """Source metadata for a citation."""
    title: str = Field(..., description="Title of the source")
    authors: List[str] = Field(..., description="List of author names")
    year: int = Field(..., description="Publication year")
    citation: str = Field(..., description="Formatted citation string")
    item_key: Optional[str] = Field(None, description="Zotero item key")


class Chunk(BaseModel):
    """Citation chunk with metadata."""
    id: str = Field(..., description="Unique chunk identifier")
    text: str = Field(..., description="Chunk text content")
    source: Source = Field(..., description="Source metadata")
    relevance_score: float = Field(..., ge=0.0, le=1.0, description="Relevance score")
    agent_filtered: bool = Field(False, description="Whether chunk was AI-filtered")
    agent_rank: Optional[int] = Field(None, description="AI-assigned rank")


class SearchResponse(BaseModel):
    """Search response to client."""
    query: str = Field(..., description="Original query")
    results_count: int = Field(..., description="Number of results returned")
    chunks: List[Chunk] = Field(..., description="List of citation chunks")
    formatted_output: str = Field(..., description="Formatted citation text")
    processing_time_ms: int = Field(..., description="Processing time in milliseconds")


class HealthResponse(BaseModel):
    """Health check response."""
    status: str = Field(..., description="Service status")
    timestamp: float = Field(..., description="Current timestamp")


class RootResponse(BaseModel):
    """Root endpoint response."""
    service: str = Field(..., description="Service name")
    version: str = Field(..., description="API version")
    status: str = Field(..., description="Service status")

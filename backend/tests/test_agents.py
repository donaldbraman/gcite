"""
Tests for Gemini AI agents.
"""

import pytest
from agents.base import BaseAgent
from agents.filter import FilterAgent
from agents.rank import RankAgent
from agents.format import FormatAgent


class TestBaseAgent:
    """Tests for BaseAgent class."""

    def test_base_agent_init_without_api_key(self, monkeypatch):
        """Test base agent initialization without API key."""
        monkeypatch.setenv("GOOGLE_GENAI_API_KEY", "")
        agent = BaseAgent()
        assert agent.enabled is False
        assert agent.model is None

    def test_base_agent_init_with_api_key(self, monkeypatch):
        """Test base agent initialization with API key."""
        from config import settings
        # Mock the settings directly
        monkeypatch.setattr(settings.settings, "GOOGLE_GENAI_API_KEY", "test_key_12345")
        agent = BaseAgent()
        assert agent.enabled is True
        assert agent.model is not None


class TestFilterAgent:
    """Tests for FilterAgent."""

    @pytest.mark.asyncio
    async def test_filter_agent_disabled(self, monkeypatch):
        """Test filter agent when disabled returns all chunks."""
        monkeypatch.setenv("GOOGLE_GENAI_API_KEY", "")

        agent = FilterAgent()
        chunks = [
            {"text": "chunk 1", "metadata": {}},
            {"text": "chunk 2", "metadata": {}}
        ]

        result = await agent.filter("test query", None, chunks, 0.7)
        assert len(result) == 2
        assert result == chunks

    @pytest.mark.asyncio
    async def test_filter_agent_empty_chunks(self, monkeypatch):
        """Test filter agent with empty chunks list."""
        monkeypatch.setenv("GOOGLE_GENAI_API_KEY", "test_key")

        agent = FilterAgent()
        result = await agent.filter("test query", None, [], 0.7)
        assert result == []


class TestRankAgent:
    """Tests for RankAgent."""

    @pytest.mark.asyncio
    async def test_rank_agent_disabled(self, monkeypatch):
        """Test rank agent when disabled returns chunks in original order."""
        monkeypatch.setenv("GOOGLE_GENAI_API_KEY", "")

        agent = RankAgent()
        chunks = [
            {"text": "chunk 1", "metadata": {}},
            {"text": "chunk 2", "metadata": {}},
            {"text": "chunk 3", "metadata": {}}
        ]

        result = await agent.rank("test query", None, chunks)
        assert len(result) == 3
        assert result[0]["agent_rank"] == 1
        assert result[1]["agent_rank"] == 2
        assert result[2]["agent_rank"] == 3

    @pytest.mark.asyncio
    async def test_rank_agent_empty_chunks(self, monkeypatch):
        """Test rank agent with empty chunks list."""
        monkeypatch.setenv("GOOGLE_GENAI_API_KEY", "test_key")

        agent = RankAgent()
        result = await agent.rank("test query", None, [])
        assert result == []

    @pytest.mark.asyncio
    async def test_rank_agent_single_chunk(self, monkeypatch):
        """Test rank agent with single chunk (no ranking needed)."""
        monkeypatch.setenv("GOOGLE_GENAI_API_KEY", "test_key")

        agent = RankAgent()
        chunks = [{"text": "single chunk", "metadata": {}}]

        result = await agent.rank("test query", None, chunks)
        assert len(result) == 1
        assert result[0]["agent_rank"] == 1


class TestFormatAgent:
    """Tests for FormatAgent."""

    @pytest.mark.asyncio
    async def test_format_agent_empty_chunks(self):
        """Test format agent with empty chunks list."""
        agent = FormatAgent()
        result = await agent.format([], "APA", True)
        assert result == "No citations found."

    @pytest.mark.asyncio
    async def test_format_agent_basic_fallback(self, monkeypatch):
        """Test format agent uses basic formatting when disabled."""
        monkeypatch.setenv("GOOGLE_GENAI_API_KEY", "")

        agent = FormatAgent()
        chunks = [{
            "agent_rank": 1,
            "text": "Test citation text",
            "metadata": {
                "title": "Test Paper",
                "authors": ["Author, A."],
                "year": 2024,
                "citation": "Author, A. (2024). Test Paper."
            },
            "relevance_score": 0.9
        }]

        result = await agent.format(chunks, "APA", True)
        assert "Test Paper" in result
        assert "Test citation text" in result
        assert "Author, A. (2024)" in result
        assert "📚 CITATION RESULTS" in result

    def test_format_basic_fallback_method(self):
        """Test the _format_basic method directly."""
        agent = FormatAgent()
        chunks = [{
            "agent_rank": 1,
            "text": "Test text",
            "metadata": {
                "title": "Test",
                "authors": [],
                "year": 2024,
                "citation": "Test (2024)"
            },
            "relevance_score": 0.8
        }]

        result = agent._format_basic(chunks, "APA", True)
        assert "Test" in result
        assert "Test text" in result
        assert "★★★★" in result  # 4 stars for 0.8 relevance

    def test_format_wrapper(self):
        """Test the _add_wrapper method."""
        agent = FormatAgent()
        content = "Test content"
        result = agent._add_wrapper(content, 5)

        assert "📚 CITATION RESULTS (5 citations)" in result
        assert "Test content" in result
        assert "Generated by gCite" in result

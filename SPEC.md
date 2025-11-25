# gCite Technical Specification

**Version:** 0.2.0
**Last Updated:** 2025-01-25
**Status:** Draft

**Version 0.2.0 Improvements:**
- Added comprehensive error handling and resilience patterns
- Implemented caching strategy with Redis for cost optimization
- Added monitoring & observability with Prometheus/OpenTelemetry
- Detailed edge case handling and degraded mode operations

## Table of Contents

1. [System Overview](#system-overview)
2. [Architecture](#architecture)
3. [Component Specifications](#component-specifications)
4. [Agent Design](#agent-design)
5. [API Specification](#api-specification)
6. [Data Models](#data-models)
7. [Integration Points](#integration-points)
8. [Performance Requirements](#performance-requirements)
9. [Security Specifications](#security-specifications)
10. [Testing Strategy](#testing-strategy)
11. [Error Handling & Resilience](#error-handling--resilience)
12. [Caching Strategy](#caching-strategy)
13. [Monitoring & Observability](#monitoring--observability)
14. [Edge Cases & Degraded Modes](#edge-cases--degraded-modes)
15. [Deployment](#deployment)

---

## System Overview

### Purpose

gCite provides intelligent, context-aware citation search for Google Docs users by combining:
1. **Semantic search** from cite-assist (vector similarity)
2. **Agentic filtering** using Gemini 2.5 Flash Lite (relevance analysis)
3. **Smart formatting** with clipboard output (universal compatibility)

### Core Innovation

Traditional citation tools rely purely on keyword matching or simple semantic similarity. gCite adds an **agentic layer** that:
- Understands query intent
- Filters false positives from semantic search
- Re-ranks by actual relevance
- Synthesizes multi-chunk citations
- Formats context-appropriately

### Key Differentiators

| Feature | Traditional Tools | gCite |
|---------|------------------|-------|
| Search Method | Keyword matching | Semantic + AI filtering |
| Results Quality | Many irrelevant hits | AI-filtered, highly relevant |
| Output Location | Direct insertion | Clipboard (universal) |
| Citation Quality | Auto-formatted only | AI-enhanced, synthesized |
| Cost | $10-50/month | ~$6/month |
| Speed | 2-5 seconds | <2 seconds |

---

## Architecture

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                         Frontend Layer                       │
│  ┌────────────────────────────────────────────────────────┐ │
│  │           Google Apps Script Add-on                    │ │
│  │  • Text selection capture                              │ │
│  │  • User preference management                          │ │
│  │  • API communication                                   │ │
│  │  • Clipboard integration                               │ │
│  └────────────────────────────────────────────────────────┘ │
└───────────────────────────┬─────────────────────────────────┘
                            │
                            │ HTTPS POST
                            │ JSON payload
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                      Backend API Layer                       │
│  ┌────────────────────────────────────────────────────────┐ │
│  │              FastAPI Application                       │ │
│  │  • Request validation                                  │ │
│  │  • Authentication                                      │ │
│  │  • Rate limiting                                       │ │
│  │  • Error handling                                      │ │
│  └────────────────────────────────────────────────────────┘ │
└───────────────┬───────────────────────┬─────────────────────┘
                │                       │
                │                       │
    ┌───────────▼──────────┐   ┌───────▼───────────────┐
    │   cite-assist API    │   │   Gemini AI Agents    │
    │   Integration        │   │                       │
    │  • Semantic search   │   │  • Filter Agent       │
    │  • Chunk retrieval   │   │  • Rank Agent         │
    │  • Metadata fetch    │   │  • Format Agent       │
    └───────────┬──────────┘   └───────┬───────────────┘
                │                       │
                │                       │
                └───────────┬───────────┘
                            │
                            ▼
                   ┌─────────────────┐
                   │  Output Service │
                   │  • Formatting   │
                   │  • Clipboard    │
                   └─────────────────┘
```

### Component Interaction Flow

```
1. User Action
   ├─ Select text in Google Doc
   └─ Click "Search Citations"

2. Apps Script
   ├─ Capture selection
   ├─ Get user preferences
   ├─ POST to backend API
   └─ Show loading state

3. Backend API
   ├─ Validate request
   ├─ Extract query & context
   └─ Initiate parallel processing:
      ├─ Query cite-assist API (semantic search)
      └─ Prepare agent context

4. cite-assist API
   ├─ Embed query with ModernBERT
   ├─ Search Qdrant vector DB
   ├─ Retrieve top 20 chunks
   └─ Return with metadata

5. Filter Agent (Gemini)
   ├─ Analyze query intent
   ├─ Evaluate each chunk
   ├─ Score relevance (0.0-1.0)
   └─ Filter below threshold

6. Rank Agent (Gemini)
   ├─ Re-rank filtered chunks
   ├─ Apply contextual weighting
   ├─ Consider source quality
   └─ Return ranked list

7. Format Agent (Gemini)
   ├─ Apply citation style
   ├─ Synthesize related chunks
   ├─ Add context snippets
   └─ Format for readability

8. Response to Apps Script
   ├─ Return formatted output
   ├─ Include metadata
   └─ Performance metrics

9. Apps Script Display
   ├─ Show results in sidebar
   ├─ Copy to clipboard
   └─ Update UI
```

---

## Component Specifications

### 1. Google Apps Script Add-on

#### Purpose
Provide user interface within Google Docs for citation search.

#### Technical Stack
- **Language**: JavaScript (Apps Script)
- **UI Framework**: HTML/CSS (Bootstrap optional)
- **APIs Used**:
  - `DocumentApp` - Document manipulation
  - `UrlFetchApp` - HTTP requests
  - `PropertiesService` - User preferences
  - `HtmlService` - Sidebar rendering

#### Key Files

**Code.gs**
```javascript
/**
 * Main entry point and menu creation
 */
function onOpen() {
  DocumentApp.getUi()
    .createMenu('gCite')
    .addItem('Search Citations', 'showSidebar')
    .addItem('Settings', 'showSettings')
    .addToUi();
}

/**
 * Get selected text from document
 * @return {string} Selected text or empty string
 */
function getSelectedText() {
  const selection = DocumentApp.getActiveDocument().getSelection();
  if (!selection) return '';

  const elements = selection.getRangeElements();
  return elements.map(e => e.getElement().asText().getText()).join(' ');
}

/**
 * Call gCite backend API
 * @param {Object} params - Search parameters
 * @return {Object} Search results
 */
function searchCitations(params) {
  const apiUrl = getApiUrl();
  const apiKey = getApiKey();

  const options = {
    method: 'post',
    contentType: 'application/json',
    headers: {
      'Authorization': `Bearer ${apiKey}`
    },
    payload: JSON.stringify(params),
    muteHttpExceptions: true
  };

  try {
    const response = UrlFetchApp.fetch(apiUrl, options);
    const statusCode = response.getResponseCode();

    if (statusCode !== 200) {
      throw new Error(`API error: ${statusCode}`);
    }

    return JSON.parse(response.getContentText());
  } catch (error) {
    Logger.log('API call failed: ' + error);
    return { error: error.toString() };
  }
}

/**
 * Get API configuration
 */
function getApiUrl() {
  const props = PropertiesService.getUserProperties();
  return props.getProperty('GCITE_API_URL') ||
         'https://gcite-api.your-domain.com';
}

function getApiKey() {
  const props = PropertiesService.getUserProperties();
  return props.getProperty('GCITE_API_KEY') || '';
}

/**
 * Save user preferences
 */
function savePreferences(prefs) {
  const props = PropertiesService.getUserProperties();
  props.setProperties(prefs);
}

/**
 * Get user preferences
 */
function getPreferences() {
  const props = PropertiesService.getUserProperties();
  return {
    citationStyle: props.getProperty('citationStyle') || 'APA',
    maxResults: parseInt(props.getProperty('maxResults')) || 10,
    includeContext: props.getProperty('includeContext') === 'true',
    minRelevance: parseFloat(props.getProperty('minRelevance')) || 0.7
  };
}
```

**Sidebar.html**
```html
<!DOCTYPE html>
<html>
<head>
  <base target="_top">
  <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css">
  <style>
    body {
      font-family: Arial, sans-serif;
      padding: 15px;
      background: #f8f9fa;
    }
    .search-container {
      background: white;
      padding: 20px;
      border-radius: 8px;
      box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    .result-card {
      background: white;
      border: 1px solid #dee2e6;
      border-radius: 6px;
      padding: 15px;
      margin: 10px 0;
      transition: box-shadow 0.2s;
    }
    .result-card:hover {
      box-shadow: 0 4px 8px rgba(0,0,0,0.15);
    }
    .relevance-bar {
      height: 4px;
      background: linear-gradient(to right, #28a745, #ffc107, #dc3545);
      border-radius: 2px;
      margin: 8px 0;
    }
    .citation-text {
      font-size: 0.9em;
      color: #495057;
      line-height: 1.6;
    }
    .source-info {
      font-size: 0.85em;
      color: #6c757d;
      margin-top: 10px;
    }
    .copy-btn {
      font-size: 0.85em;
    }
    .loading {
      text-align: center;
      padding: 40px;
      color: #6c757d;
    }
    .spinner {
      border: 3px solid #f3f3f3;
      border-top: 3px solid #3498db;
      border-radius: 50%;
      width: 40px;
      height: 40px;
      animation: spin 1s linear infinite;
      margin: 0 auto;
    }
    @keyframes spin {
      0% { transform: rotate(0deg); }
      100% { transform: rotate(360deg); }
    }
  </style>
</head>
<body>
  <div class="search-container">
    <h5>🔍 gCite Search</h5>

    <div class="mb-3">
      <label class="form-label">Query</label>
      <textarea id="query" class="form-control" rows="3"
                placeholder="Enter search query or click 'Use Selection'"></textarea>
    </div>

    <div class="d-flex gap-2">
      <button onclick="useSelection()" class="btn btn-outline-primary">
        Use Selection
      </button>
      <button onclick="search()" class="btn btn-primary">
        Search
      </button>
    </div>
  </div>

  <div id="results" class="mt-3"></div>

  <script>
    function useSelection() {
      google.script.run
        .withSuccessHandler(text => {
          document.getElementById('query').value = text;
        })
        .withFailureHandler(err => {
          showError('Failed to get selection: ' + err);
        })
        .getSelectedText();
    }

    function search() {
      const query = document.getElementById('query').value.trim();
      if (!query) {
        alert('Please enter a query');
        return;
      }

      showLoading();

      google.script.run
        .withSuccessHandler(displayResults)
        .withFailureHandler(showError)
        .searchCitations({
          query: query,
          max_results: 10,
          filter: true
        });
    }

    function showLoading() {
      document.getElementById('results').innerHTML = `
        <div class="loading">
          <div class="spinner"></div>
          <p class="mt-3">Searching and filtering results...</p>
        </div>
      `;
    }

    function displayResults(data) {
      if (data.error) {
        showError(data.error);
        return;
      }

      let html = `
        <div class="alert alert-success">
          Found ${data.results_count} relevant citations
          (${data.processing_time_ms}ms)
        </div>
      `;

      if (data.chunks && data.chunks.length > 0) {
        data.chunks.forEach((chunk, idx) => {
          html += `
            <div class="result-card">
              <div class="d-flex justify-content-between align-items-start">
                <strong>[${idx + 1}] ${escapeHtml(chunk.source.title)}</strong>
                <span class="badge bg-primary">${chunk.relevance_score.toFixed(2)}</span>
              </div>

              <div class="relevance-bar" style="width: ${chunk.relevance_score * 100}%"></div>

              <div class="citation-text">
                "${escapeHtml(chunk.text)}"
              </div>

              <div class="source-info">
                ${escapeHtml(chunk.source.citation)}
              </div>

              <button onclick="copyChunk(${idx})" class="btn btn-sm btn-outline-secondary copy-btn mt-2">
                Copy Citation
              </button>
            </div>
          `;
        });

        html += `
          <button onclick="copyAll()" class="btn btn-primary w-100 mt-3">
            Copy All to Clipboard
          </button>
        `;
      } else {
        html += `
          <div class="alert alert-warning">
            No relevant citations found. Try refining your query.
          </div>
        `;
      }

      document.getElementById('results').innerHTML = html;
    }

    function showError(error) {
      document.getElementById('results').innerHTML = `
        <div class="alert alert-danger">
          <strong>Error:</strong> ${escapeHtml(error.toString())}
        </div>
      `;
    }

    function copyChunk(index) {
      // Implementation for copying single chunk
      alert('Single chunk copy not yet implemented');
    }

    function copyAll() {
      // Implementation for copying all results
      alert('Copy all not yet implemented - will copy formatted citations to clipboard');
    }

    function escapeHtml(text) {
      const div = document.createElement('div');
      div.textContent = text;
      return div.innerHTML;
    }
  </script>
</body>
</html>
```

#### User Preferences Schema

```javascript
{
  "citationStyle": "APA" | "MLA" | "Chicago" | "Bluebook",
  "maxResults": 1-20,
  "includeContext": boolean,
  "includeScores": boolean,
  "minRelevance": 0.0-1.0,
  "apiUrl": "https://...",
  "apiKey": "..."
}
```

### 2. Backend API

#### Purpose
Orchestrate semantic search from cite-assist and agentic filtering from Gemini.

#### Technical Stack
- **Framework**: FastAPI 0.109+
- **Language**: Python 3.13
- **ASGI Server**: Uvicorn
- **Dependencies**:
  - `fastapi` - Web framework
  - `pydantic` - Data validation
  - `google-generativeai` - Gemini AI
  - `httpx` - Async HTTP client
  - `python-dotenv` - Environment config

#### File Structure

```
backend/
├── api/
│   ├── __init__.py
│   ├── main.py           # FastAPI app
│   ├── routes.py         # Endpoint handlers
│   ├── models.py         # Pydantic models
│   └── dependencies.py   # Shared dependencies
├── agents/
│   ├── __init__.py
│   ├── base.py          # Base agent class
│   ├── filter.py        # Filter agent
│   ├── rank.py          # Ranking agent
│   └── format.py        # Formatting agent
├── services/
│   ├── __init__.py
│   ├── cite_assist.py   # cite-assist client
│   ├── clipboard.py     # Clipboard service
│   └── cache.py         # Response caching
├── config/
│   ├── __init__.py
│   └── settings.py      # Configuration
├── utils/
│   ├── __init__.py
│   └── logging.py       # Logging setup
└── tests/
    ├── __init__.py
    ├── test_agents.py
    ├── test_api.py
    └── test_integration.py
```

#### API Implementation

**api/main.py**
```python
"""
gCite Backend API
FastAPI application for intelligent citation search
"""

from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import time
import logging

from .models import SearchRequest, SearchResponse
from .routes import router
from config.settings import settings

# Initialize FastAPI app
app = FastAPI(
    title="gCite API",
    description="Intelligent citation search with AI filtering",
    version="0.1.0"
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routes
app.include_router(router, prefix="/api")

# Logging setup
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "service": "gCite API",
        "version": "0.1.0",
        "status": "operational"
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": time.time()
    }

@app.middleware("http")
async def log_requests(request, call_next):
    """Log all requests"""
    start_time = time.time()

    response = await call_next(request)

    process_time = (time.time() - start_time) * 1000
    logger.info(
        f"{request.method} {request.url.path} "
        f"completed in {process_time:.2f}ms "
        f"with status {response.status_code}"
    )

    return response

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "api.main:app",
        host=settings.API_HOST,
        port=settings.API_PORT,
        reload=settings.DEBUG
    )
```

**api/routes.py**
```python
"""
API route handlers
"""

from fastapi import APIRouter, HTTPException, Depends
from typing import List
import logging

from .models import SearchRequest, SearchResponse, Chunk
from services.cite_assist import CiteAssistClient
from agents.filter import FilterAgent
from agents.rank import RankAgent
from agents.format import FormatAgent
from config.settings import settings

router = APIRouter()
logger = logging.getLogger(__name__)

@router.post("/search", response_model=SearchResponse)
async def search_citations(
    request: SearchRequest,
    cite_assist: CiteAssistClient = Depends(),
    filter_agent: FilterAgent = Depends(),
    rank_agent: RankAgent = Depends(),
    format_agent: FormatAgent = Depends()
):
    """
    Search for relevant citations

    Process:
    1. Semantic search via cite-assist
    2. AI filtering for relevance
    3. AI ranking by importance
    4. AI formatting for output
    """
    import time
    start_time = time.time()

    try:
        # Step 1: Semantic search
        logger.info(f"Searching for: {request.query}")
        raw_chunks = await cite_assist.search(
            query=request.query,
            limit=20  # Get more than needed for filtering
        )

        if not raw_chunks:
            return SearchResponse(
                query=request.query,
                results_count=0,
                chunks=[],
                formatted_output="No results found.",
                processing_time_ms=int((time.time() - start_time) * 1000)
            )

        # Step 2: Filter with AI
        if request.filter:
            logger.info(f"Filtering {len(raw_chunks)} chunks")
            filtered_chunks = await filter_agent.filter(
                query=request.query,
                context=request.context,
                chunks=raw_chunks,
                threshold=request.min_relevance
            )
        else:
            filtered_chunks = raw_chunks

        # Step 3: Rank with AI
        logger.info(f"Ranking {len(filtered_chunks)} chunks")
        ranked_chunks = await rank_agent.rank(
            query=request.query,
            context=request.context,
            chunks=filtered_chunks
        )

        # Limit to requested number
        final_chunks = ranked_chunks[:request.max_results]

        # Step 4: Format with AI
        logger.info(f"Formatting {len(final_chunks)} chunks")
        formatted_output = await format_agent.format(
            chunks=final_chunks,
            style=request.citation_style,
            include_context=request.include_context
        )

        processing_time = int((time.time() - start_time) * 1000)

        return SearchResponse(
            query=request.query,
            results_count=len(final_chunks),
            chunks=final_chunks,
            formatted_output=formatted_output,
            processing_time_ms=processing_time
        )

    except Exception as e:
        logger.error(f"Search failed: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))
```

**api/models.py**
```python
"""
Pydantic data models
"""

from pydantic import BaseModel, Field
from typing import List, Optional
from enum import Enum

class CitationStyle(str, Enum):
    APA = "APA"
    MLA = "MLA"
    CHICAGO = "Chicago"
    BLUEBOOK = "Bluebook"

class SearchRequest(BaseModel):
    """Search request from client"""
    query: str = Field(..., min_length=1, max_length=1000)
    context: Optional[str] = Field(None, max_length=2000)
    max_results: int = Field(10, ge=1, le=50)
    citation_style: CitationStyle = CitationStyle.APA
    filter: bool = True
    min_relevance: float = Field(0.7, ge=0.0, le=1.0)
    include_context: bool = True

class Source(BaseModel):
    """Source metadata"""
    title: str
    authors: List[str]
    year: int
    citation: str
    item_key: Optional[str] = None

class Chunk(BaseModel):
    """Citation chunk with metadata"""
    id: str
    text: str
    source: Source
    relevance_score: float
    agent_filtered: bool = False
    agent_rank: Optional[int] = None

class SearchResponse(BaseModel):
    """Search response to client"""
    query: str
    results_count: int
    chunks: List[Chunk]
    formatted_output: str
    processing_time_ms: int
```

#### Agent Configuration

**config/settings.py**
```python
"""
Application configuration
"""

from pydantic_settings import BaseSettings
from typing import List

class Settings(BaseSettings):
    """Application settings"""

    # API Configuration
    API_HOST: str = "0.0.0.0"
    API_PORT: int = 8001
    DEBUG: bool = False

    # CORS
    CORS_ORIGINS: List[str] = [
        "https://script.google.com",
        "https://docs.google.com"
    ]

    # cite-assist Integration
    CITE_ASSIST_API_URL: str = "http://localhost:8000"
    CITE_ASSIST_API_KEY: str = ""

    # Gemini AI
    GOOGLE_GENAI_API_KEY: str
    GEMINI_MODEL: str = "gemini-2.5-flash-lite"

    # Agent Configuration
    AGENT_FILTER_THRESHOLD: float = 0.7
    AGENT_MAX_CHUNKS: int = 20
    AGENT_TIMEOUT_SECONDS: int = 5

    # Caching
    CACHE_ENABLED: bool = True
    CACHE_TTL_SECONDS: int = 3600

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

settings = Settings()
```

---

## Agent Design

### Overview

Three specialized Gemini 2.5 Flash Lite agents work in sequence:

1. **Filter Agent**: Removes irrelevant chunks
2. **Rank Agent**: Orders by relevance and quality
3. **Format Agent**: Creates citation output

### Filter Agent

**Purpose**: Evaluate chunk relevance to query

**Implementation**: `agents/filter.py`

```python
"""
Filter Agent - Relevance evaluation
"""

import google.generativeai as genai
from typing import List, Dict
import json
import asyncio
from config.settings import settings

class FilterAgent:
    """AI agent for filtering irrelevant chunks"""

    def __init__(self):
        genai.configure(api_key=settings.GOOGLE_GENAI_API_KEY)
        self.model = genai.GenerativeModel(settings.GEMINI_MODEL)

    async def filter(
        self,
        query: str,
        context: str,
        chunks: List[Dict],
        threshold: float = 0.7
    ) -> List[Dict]:
        """
        Filter chunks by relevance

        Args:
            query: User's search query
            context: Optional context about user's intent
            chunks: List of chunks from semantic search
            threshold: Minimum relevance score to keep

        Returns:
            Filtered list of chunks
        """
        # Evaluate chunks in parallel
        tasks = [
            self._evaluate_chunk(query, context, chunk)
            for chunk in chunks
        ]

        evaluations = await asyncio.gather(*tasks)

        # Filter based on threshold
        filtered = []
        for chunk, evaluation in zip(chunks, evaluations):
            if evaluation['relevant'] and evaluation['confidence'] >= threshold:
                chunk['agent_filtered'] = True
                chunk['relevance_score'] = evaluation['confidence']
                chunk['filter_reasoning'] = evaluation['reasoning']
                filtered.append(chunk)

        return filtered

    async def _evaluate_chunk(
        self,
        query: str,
        context: str,
        chunk: Dict
    ) -> Dict:
        """Evaluate single chunk"""

        prompt = f"""
You are a citation relevance evaluator. Determine if this chunk is relevant to the user's query.

Query: {query}
{f"Context: {context}" if context else ""}

Chunk Text:
{chunk['text']}

Source: {chunk['source']['title']} ({chunk['source']['year']})

Evaluate:
1. Does this chunk directly address the query topic?
2. Is the information substantive (not just tangential mention)?
3. Would this be a good citation for someone writing about the query topic?
4. Is the source credible and relevant?

Respond ONLY with valid JSON:
{{
  "relevant": true/false,
  "confidence": 0.0-1.0,
  "reasoning": "brief explanation"
}}
"""

        try:
            response = await self.model.generate_content_async(
                prompt,
                generation_config={
                    "temperature": 0.1,  # Low temp for consistent evaluation
                    "max_output_tokens": 200
                }
            )

            result = json.loads(response.text)
            return result

        except Exception as e:
            # On error, default to keeping chunk
            return {
                "relevant": True,
                "confidence": 0.5,
                "reasoning": f"Error in evaluation: {str(e)}"
            }
```

### Rank Agent

**Purpose**: Re-order chunks by importance

**Implementation**: `agents/rank.py`

```python
"""
Rank Agent - Importance ranking
"""

import google.generativeai as genai
from typing import List, Dict
import json
from config.settings import settings

class RankAgent:
    """AI agent for ranking chunks by importance"""

    def __init__(self):
        genai.configure(api_key=settings.GOOGLE_GENAI_API_KEY)
        self.model = genai.GenerativeModel(settings.GEMINI_MODEL)

    async def rank(
        self,
        query: str,
        context: str,
        chunks: List[Dict]
    ) -> List[Dict]:
        """
        Rank chunks by relevance and importance

        Args:
            query: User's search query
            context: Optional context
            chunks: List of filtered chunks

        Returns:
            Chunks sorted by importance
        """
        if not chunks:
            return []

        # Prepare chunks for ranking
        chunks_summary = [
            {
                "id": i,
                "text_preview": chunk['text'][:200],
                "source": chunk['source']['title'],
                "year": chunk['source']['year']
            }
            for i, chunk in enumerate(chunks)
        ]

        prompt = f"""
You are a citation ranking specialist. Rank these chunks by their importance and relevance to the query.

Query: {query}
{f"Context: {context}" if context else ""}

Chunks:
{json.dumps(chunks_summary, indent=2)}

Rank by:
1. Direct relevance to query (primary factor)
2. Strength and quality of evidence
3. Source credibility and impact
4. Recency (prefer newer unless historical context needed)

Respond ONLY with valid JSON array of IDs in ranked order:
{{
  "ranked_ids": [2, 0, 5, 1, ...],
  "reasoning": "brief explanation of ranking logic"
}}
"""

        try:
            response = await self.model.generate_content_async(
                prompt,
                generation_config={
                    "temperature": 0.2,
                    "max_output_tokens": 500
                }
            )

            result = json.loads(response.text)
            ranked_ids = result['ranked_ids']

            # Reorder chunks
            ranked_chunks = []
            for rank, chunk_id in enumerate(ranked_ids):
                if chunk_id < len(chunks):
                    chunk = chunks[chunk_id].copy()
                    chunk['agent_rank'] = rank + 1
                    ranked_chunks.append(chunk)

            # Add any chunks not in ranking (shouldn't happen)
            ranked_ids_set = set(ranked_ids)
            for i, chunk in enumerate(chunks):
                if i not in ranked_ids_set:
                    chunk['agent_rank'] = len(ranked_chunks) + 1
                    ranked_chunks.append(chunk)

            return ranked_chunks

        except Exception as e:
            # On error, return original order
            for i, chunk in enumerate(chunks):
                chunk['agent_rank'] = i + 1
            return chunks
```

### Format Agent

**Purpose**: Create professional citation output

**Implementation**: `agents/format.py`

```python
"""
Format Agent - Citation formatting
"""

import google.generativeai as genai
from typing import List, Dict
from config.settings import settings

class FormatAgent:
    """AI agent for formatting citations"""

    def __init__(self):
        genai.configure(api_key=settings.GOOGLE_GENAI_API_KEY)
        self.model = genai.GenerativeModel(settings.GEMINI_MODEL)

    async def format(
        self,
        chunks: List[Dict],
        style: str = "APA",
        include_context: bool = True
    ) -> str:
        """
        Format chunks as professional citations

        Args:
            chunks: Ranked chunks to format
            style: Citation style (APA, MLA, Chicago, Bluebook)
            include_context: Include contextual snippets

        Returns:
            Formatted citation text ready for clipboard
        """
        if not chunks:
            return "No citations found."

        prompt = f"""
You are a citation formatting specialist. Format these chunks as professional citations.

Citation Style: {style}
Include Context: {include_context}

Chunks:
{json.dumps([
    {
        "rank": chunk['agent_rank'],
        "text": chunk['text'],
        "source": chunk['source'],
        "relevance": chunk['relevance_score']
    }
    for chunk in chunks
], indent=2)}

Format as:
1. Clean, professional output ready to paste
2. Proper {style} citation style
3. Include relevance indicators (stars or scores)
4. Group by source if multiple chunks from same paper
5. Include key quotes and context
6. Add visual separators for readability

Make it immediately useful for pasting into a document.
"""

        try:
            response = await self.model.generate_content_async(
                prompt,
                generation_config={
                    "temperature": 0.3,
                    "max_output_tokens": 2000
                }
            )

            formatted = response.text

            # Add header and footer
            output = f"""
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📚 CITATION RESULTS ({len(chunks)} chunks)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

{formatted}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Generated by gCite • cite-assist + Gemini AI
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""
            return output.strip()

        except Exception as e:
            # Fallback to basic formatting
            return self._basic_format(chunks, style)

    def _basic_format(self, chunks: List[Dict], style: str) -> str:
        """Fallback formatting if AI fails"""
        output = []
        for chunk in chunks:
            output.append(f"[{chunk['agent_rank']}] {chunk['source']['citation']}")
            output.append(f'"{chunk['text']}"')
            output.append(f"Relevance: {chunk['relevance_score']:.2f}")
            output.append("")

        return "\n".join(output)
```

---

## Data Models

### Request/Response Models

**SearchRequest**
```json
{
  "query": "bail reform reduces recidivism",
  "context": "writing legal brief about bail reform",
  "max_results": 10,
  "citation_style": "Bluebook",
  "filter": true,
  "min_relevance": 0.7,
  "include_context": true
}
```

**SearchResponse**
```json
{
  "query": "bail reform reduces recidivism",
  "results_count": 5,
  "processing_time_ms": 1432,
  "formatted_output": "...",
  "chunks": [
    {
      "id": "chunk_abc123",
      "text": "Pretrial detention increases recidivism...",
      "source": {
        "title": "Distortion of Justice",
        "authors": ["Stevenson, M."],
        "year": 2018,
        "citation": "Stevenson, M. (2018)...",
        "item_key": "ABC123"
      },
      "relevance_score": 0.94,
      "agent_filtered": true,
      "agent_rank": 1
    }
  ]
}
```

### Internal Data Models

**ChunkData** (from cite-assist)
```python
{
    "chunk_id": "uuid",
    "text": "chunk text content",
    "source_key": "item_key from Zotero",
    "metadata": {
        "title": "...",
        "authors": [...],
        "year": 2018,
        "page": 45
    },
    "similarity_score": 0.87
}
```

**AgentEvaluation**
```python
{
    "chunk_id": "uuid",
    "relevant": true,
    "confidence": 0.94,
    "reasoning": "Directly addresses bail reform and recidivism with empirical data",
    "key_points": [
        "Empirical evidence",
        "Recidivism outcomes",
        "Bail reform impact"
    ]
}
```

---

## Integration Points

### cite-assist API Integration

**Endpoint**: `POST http://localhost:8000/api/v1/search`

**Request:**
```json
{
  "query": "bail reform reduces recidivism",
  "limit": 20,
  "search_mode": "chunks"
}
```

**Response:**
```json
{
  "results": [
    {
      "chunk_id": "...",
      "text": "...",
      "score": 0.87,
      "source": {...}
    }
  ]
}
```

**Client Implementation:**

```python
"""
cite-assist API client
"""

import httpx
from typing import List, Dict, Optional
from config.settings import settings

class CiteAssistClient:
    """Client for cite-assist semantic search API"""

    def __init__(self):
        self.base_url = settings.CITE_ASSIST_API_URL
        self.api_key = settings.CITE_ASSIST_API_KEY
        self.client = httpx.AsyncClient(
            base_url=self.base_url,
            timeout=30.0
        )

    async def search(
        self,
        query: str,
        limit: int = 20,
        search_mode: str = "chunks"
    ) -> List[Dict]:
        """
        Search cite-assist for relevant chunks

        Args:
            query: Search query
            limit: Max results to return
            search_mode: "chunks", "summaries", or "both"

        Returns:
            List of chunk dictionaries
        """
        payload = {
            "query": query,
            "limit": limit,
            "search_mode": search_mode
        }

        headers = {}
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"

        response = await self.client.post(
            "/api/v1/search",
            json=payload,
            headers=headers
        )

        response.raise_for_status()
        data = response.json()

        return data.get("results", [])

    async def close(self):
        """Close HTTP client"""
        await self.client.aclose()
```

### Gemini AI Integration

**Configuration:**
```python
import google.generativeai as genai

genai.configure(api_key=settings.GOOGLE_GENAI_API_KEY)
model = genai.GenerativeModel("gemini-2.5-flash-lite")
```

**Usage:**
```python
response = await model.generate_content_async(
    prompt,
    generation_config={
        "temperature": 0.1,
        "max_output_tokens": 500
    }
)
```

---

## Performance Requirements

### Latency Targets

| Component | Target | Max Acceptable |
|-----------|--------|----------------|
| cite-assist search | < 500ms | < 1000ms |
| Filter agent (per chunk) | < 200ms | < 500ms |
| Rank agent | < 300ms | < 800ms |
| Format agent | < 400ms | < 1000ms |
| **Total end-to-end** | **< 2000ms** | **< 3000ms** |

### Throughput

- **Target**: 100 requests/minute
- **Peak**: 500 requests/minute

### Cost Optimization

**Gemini API Costs** (as of 2025-01):
- Input: $0.001 per 1K tokens
- Output: $0.002 per 1K tokens

**Per Query Estimate:**
- Filter agent: ~500 tokens input + 100 output = $0.0007
- Rank agent: ~300 tokens input + 100 output = $0.0005
- Format agent: ~400 tokens input + 500 output = $0.0014

**Total per query: ~$0.0026**

With 1000 queries/month: **~$2.60/month**

---

## Security Specifications

### Authentication

**Apps Script → Backend API:**
- Bearer token authentication
- API keys stored in User Properties
- Rate limiting by API key

**Backend → cite-assist:**
- Optional API key
- Localhost trusted by default

**Backend → Gemini:**
- API key from environment variables
- Never exposed to client

### Data Privacy

- **No storage**: All requests are stateless
- **No logging of content**: Only metadata logged
- **cite-assist data stays local**: Never sent to cloud except Gemini filtering
- **Gemini sees**: Only chunks, not full papers
- **User tracking**: None

### Rate Limiting

```python
from fastapi import Request
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)

@app.post("/api/search")
@limiter.limit("10/minute")
async def search(request: Request, ...):
    ...
```

---

## Testing Strategy

### Unit Tests

**Test Coverage Targets:**
- Agents: 90%+
- API routes: 85%+
- Services: 85%+
- Overall: 80%+

**Example: Test Filter Agent**
```python
import pytest
from agents.filter import FilterAgent

@pytest.mark.asyncio
async def test_filter_agent_relevance():
    """Test filter agent correctly identifies relevant chunks"""
    agent = FilterAgent()

    query = "bail reform reduces recidivism"
    chunks = [
        {
            "text": "Pretrial detention increases recidivism by 30%",
            "source": {"title": "Bail Study", "year": 2020}
        },
        {
            "text": "The sky is blue and grass is green",
            "source": {"title": "Nature Facts", "year": 2020}
        }
    ]

    filtered = await agent.filter(query, "", chunks, threshold=0.7)

    assert len(filtered) == 1
    assert "recidivism" in filtered[0]["text"].lower()
```

### Integration Tests

```python
@pytest.mark.asyncio
async def test_full_search_flow():
    """Test complete search flow"""
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "http://localhost:8001/api/search",
            json={
                "query": "test query",
                "max_results": 5
            }
        )

        assert response.status_code == 200
        data = response.json()
        assert "chunks" in data
        assert "formatted_output" in data
```

### Performance Tests

```python
import pytest
import time

@pytest.mark.asyncio
async def test_search_latency():
    """Ensure search completes within 3 seconds"""
    start = time.time()

    # Run search
    result = await search_citations(...)

    elapsed = time.time() - start
    assert elapsed < 3.0  # 3 second max
```

---

## Error Handling & Resilience

### Error Categories

**1. cite-assist Unavailable**
- **Cause**: cite-assist service down or unreachable
- **Detection**: Connection timeout, HTTP 5xx errors
- **Response**: Return user-friendly error, suggest checking cite-assist status
- **Recovery**: Retry with exponential backoff (3 attempts)

**2. Gemini API Errors**
- **Cause**: Rate limits, quota exceeded, API downtime
- **Detection**: HTTP 429, 500, timeout
- **Response**: Fall back to basic filtering/formatting
- **Recovery**: Circuit breaker pattern (5 failures → 30s cooldown)

**3. Invalid JSON from Agents**
- **Cause**: Agent returns malformed JSON
- **Detection**: JSON parse error
- **Response**: Use default values, log for analysis
- **Recovery**: Graceful degradation to basic formatting

**4. No Results Found**
- **Cause**: Query has no matching chunks
- **Detection**: Empty results from cite-assist
- **Response**: Helpful message suggesting query refinement
- **Recovery**: N/A (user action required)

### Retry Logic

```python
from tenacity import retry, stop_after_attempt, wait_exponential

class CiteAssistClient:
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        reraise=True
    )
    async def search(self, query: str, limit: int = 20) -> List[Dict]:
        """Search with automatic retry on failure"""
        try:
            response = await self.client.post(...)
            response.raise_for_status()
            return response.json()
        except httpx.TimeoutException:
            logger.warning("cite-assist timeout, retrying...")
            raise
        except httpx.HTTPStatusError as e:
            if e.response.status_code >= 500:
                logger.warning(f"cite-assist server error {e.response.status_code}, retrying...")
                raise
            else:
                # Client errors (4xx) should not retry
                logger.error(f"cite-assist client error {e.response.status_code}")
                return []
```

### Circuit Breaker Pattern

```python
from circuitbreaker import circuit

class FilterAgent:
    @circuit(failure_threshold=5, recovery_timeout=30, expected_exception=Exception)
    async def filter(self, query: str, context: str, chunks: List[Dict], threshold: float = 0.7) -> List[Dict]:
        """Filter with circuit breaker for Gemini API"""
        try:
            # Normal filtering logic
            ...
        except CircuitBreakerError:
            # Circuit open - skip filtering
            logger.warning("Filter agent circuit open, passing all chunks through")
            return chunks  # Return unfiltered
```

### Graceful Degradation

**Degraded Mode Hierarchy:**
1. **Full Mode**: cite-assist + all 3 agents (Filter, Rank, Format)
2. **Degraded Mode 1**: cite-assist + basic ranking (skip agent filtering)
3. **Degraded Mode 2**: cite-assist only (skip all agents, basic formatting)
4. **Failed**: Return error message

```python
async def search_with_fallback(request: SearchRequest) -> SearchResponse:
    """Search with graceful degradation"""
    try:
        # Try full mode
        return await full_search(request)
    except GeminiAPIError:
        logger.warning("Gemini unavailable, degrading to basic mode")
        try:
            # Try without agents
            return await basic_search(request)
        except CiteAssistError:
            logger.error("cite-assist unavailable")
            raise HTTPException(503, "Search service unavailable")
```

### Error Response Format

```json
{
  "error": {
    "code": "CITE_ASSIST_UNAVAILABLE",
    "message": "Unable to connect to citation database. Please ensure cite-assist is running.",
    "details": {
      "service": "cite-assist",
      "url": "http://localhost:8000",
      "suggestion": "Run 'podman start qdrant' and restart cite-assist"
    },
    "timestamp": "2025-01-25T10:30:00Z"
  }
}
```

---

## Caching Strategy

### Why Cache?

**Benefits:**
- Reduce Gemini API costs (most expensive component)
- Improve response time for repeated queries
- Handle rate limits gracefully
- Offline-friendly for common queries

### What to Cache?

**Cache Targets:**
1. **cite-assist search results** - 1 hour TTL
2. **Agent filter evaluations** - 6 hours TTL
3. **Agent rank results** - 6 hours TTL
4. **Formatted output** - 1 hour TTL

**Do NOT cache:**
- User preferences (always fresh)
- Error responses
- Partial results

### Implementation

**Backend Caching (Redis):**

```python
"""
services/cache.py - Redis caching service
"""

import redis.asyncio as redis
import json
import hashlib
from typing import Optional, Any
from config.settings import settings

class CacheService:
    """Redis-based caching for search results"""

    def __init__(self):
        self.redis = redis.from_url(
            settings.REDIS_URL,
            encoding="utf-8",
            decode_responses=True
        )

    def _make_key(self, prefix: str, query: str, **params) -> str:
        """Generate cache key from query and parameters"""
        # Create deterministic key from query + params
        key_data = f"{query}:{json.dumps(params, sort_keys=True)}"
        key_hash = hashlib.sha256(key_data.encode()).hexdigest()[:16]
        return f"gcite:{prefix}:{key_hash}"

    async def get(self, prefix: str, query: str, **params) -> Optional[Any]:
        """Get cached result"""
        key = self._make_key(prefix, query, **params)
        cached = await self.redis.get(key)
        if cached:
            return json.loads(cached)
        return None

    async def set(self, prefix: str, query: str, value: Any, ttl: int = 3600, **params):
        """Set cached result with TTL"""
        key = self._make_key(prefix, query, **params)
        await self.redis.setex(
            key,
            ttl,
            json.dumps(value)
        )

    async def invalidate(self, prefix: str, query: str, **params):
        """Invalidate cached result"""
        key = self._make_key(prefix, query, **params)
        await self.redis.delete(key)
```

**Usage in Routes:**

```python
@router.post("/search", response_model=SearchResponse)
async def search_citations(
    request: SearchRequest,
    cache: CacheService = Depends()
):
    """Search with caching"""

    # Try cache first
    cache_key_params = {
        "max_results": request.max_results,
        "citation_style": request.citation_style,
        "filter": request.filter,
        "min_relevance": request.min_relevance
    }

    cached_result = await cache.get("search", request.query, **cache_key_params)
    if cached_result and settings.CACHE_ENABLED:
        logger.info(f"Cache HIT for query: {request.query}")
        return SearchResponse(**cached_result)

    # Cache miss - perform search
    logger.info(f"Cache MISS for query: {request.query}")
    result = await perform_search(request)

    # Store in cache
    if settings.CACHE_ENABLED:
        await cache.set(
            "search",
            request.query,
            result.model_dump(),
            ttl=3600,  # 1 hour
            **cache_key_params
        )

    return result
```

### Cache Invalidation

**Automatic:**
- TTL expiration (1-6 hours depending on component)

**Manual:**
- User can force refresh (bypass cache)
- Admin API to clear cache

**Selective:**
```python
# Clear all caches for a specific query
await cache.invalidate("search", query)
await cache.invalidate("filter", query)
await cache.invalidate("rank", query)
```

---

## Monitoring & Observability

### Metrics Collection

**Key Metrics:**

```python
from prometheus_client import Counter, Histogram, Gauge

# Request metrics
search_requests_total = Counter(
    'gcite_search_requests_total',
    'Total search requests',
    ['status', 'degraded_mode']
)

search_latency = Histogram(
    'gcite_search_latency_seconds',
    'Search latency',
    ['component'],
    buckets=[0.1, 0.5, 1.0, 2.0, 3.0, 5.0]
)

# Agent metrics
agent_calls_total = Counter(
    'gcite_agent_calls_total',
    'Agent API calls',
    ['agent', 'status']
)

agent_cost_total = Counter(
    'gcite_agent_cost_dollars',
    'Cumulative agent costs',
    ['agent']
)

chunks_filtered = Histogram(
    'gcite_chunks_filtered',
    'Number of chunks after filtering',
    buckets=[0, 1, 2, 5, 10, 20, 50]
)

# Cache metrics
cache_hits = Counter('gcite_cache_hits_total', 'Cache hits', ['prefix'])
cache_misses = Counter('gcite_cache_misses_total', 'Cache misses', ['prefix'])

# Error metrics
errors_total = Counter(
    'gcite_errors_total',
    'Total errors',
    ['error_type', 'component']
)
```

**Instrumentation:**

```python
@router.post("/search")
async def search_citations(request: SearchRequest):
    """Search with metrics"""
    start_time = time.time()
    degraded_mode = "none"

    try:
        # Perform search
        result = await perform_search(request)

        # Record success
        search_requests_total.labels(status="success", degraded_mode=degraded_mode).inc()
        search_latency.labels(component="total").observe(time.time() - start_time)

        return result

    except GeminiAPIError:
        degraded_mode = "no_agents"
        errors_total.labels(error_type="gemini_api", component="agents").inc()
        # Try degraded mode...
    except CiteAssistError:
        errors_total.labels(error_type="cite_assist", component="search").inc()
        search_requests_total.labels(status="failure", degraded_mode=degraded_mode).inc()
        raise
```

### Logging

**Structured Logging:**

```python
import structlog

logger = structlog.get_logger()

# Log search request
logger.info(
    "search_started",
    query=request.query,
    max_results=request.max_results,
    filter_enabled=request.filter
)

# Log agent execution
logger.info(
    "agent_executed",
    agent="filter",
    input_chunks=len(chunks),
    output_chunks=len(filtered),
    threshold=threshold,
    duration_ms=duration
)

# Log errors with context
logger.error(
    "cite_assist_error",
    error=str(e),
    query=query,
    url=cite_assist_url,
    retry_attempt=attempt
)
```

### Tracing

**OpenTelemetry Integration:**

```python
from opentelemetry import trace
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor

tracer = trace.get_tracer(__name__)

# Instrument FastAPI
FastAPIInstrumentor.instrument_app(app)

# Trace agent calls
@tracer.start_as_current_span("filter_agent.filter")
async def filter(self, query: str, chunks: List[Dict]) -> List[Dict]:
    span = trace.get_current_span()
    span.set_attribute("query", query)
    span.set_attribute("chunks_in", len(chunks))

    filtered = await self._do_filter(...)

    span.set_attribute("chunks_out", len(filtered))
    return filtered
```

### Dashboards

**Grafana Panels:**
1. **Request Rate**: search_requests_total over time
2. **Latency P50/P95/P99**: search_latency percentiles
3. **Error Rate**: errors_total / search_requests_total
4. **Cache Hit Rate**: cache_hits / (cache_hits + cache_misses)
5. **Agent Costs**: agent_cost_total cumulative
6. **Degraded Mode %**: degraded_mode != "none" percentage

### Alerts

**Critical Alerts:**
- Error rate > 10% (5 min window)
- P95 latency > 5s (5 min window)
- cite-assist unavailable
- Gemini API quota exceeded

**Warning Alerts:**
- Error rate > 5%
- P95 latency > 3s
- Cache hit rate < 30%
- Agent costs > $10/day

---

## Edge Cases & Degraded Modes

### Citation Deduplication

**Problem**: Same source appears multiple times with different chunks

**Solution:**

```python
def deduplicate_chunks(chunks: List[Dict]) -> List[Dict]:
    """Group chunks by source, keep top N per source"""
    from collections import defaultdict

    by_source = defaultdict(list)
    for chunk in chunks:
        source_key = chunk['source']['item_key']
        by_source[source_key].append(chunk)

    # Keep top 3 chunks per source
    deduplicated = []
    for source_key, source_chunks in by_source.items():
        # Sort by relevance
        sorted_chunks = sorted(
            source_chunks,
            key=lambda c: c['relevance_score'],
            reverse=True
        )
        deduplicated.extend(sorted_chunks[:3])

    # Re-sort by overall relevance
    return sorted(deduplicated, key=lambda c: c['relevance_score'], reverse=True)
```

### Context Window Limits

**Problem**: Too many chunks exceed Gemini context window

**Solution:**

```python
def chunk_batches_for_context(chunks: List[Dict], max_tokens: int = 30000) -> List[List[Dict]]:
    """Split chunks into batches that fit context window"""
    import tiktoken
    encoder = tiktoken.encoding_for_model("gpt-4")  # Approximation

    batches = []
    current_batch = []
    current_tokens = 0

    for chunk in chunks:
        chunk_tokens = len(encoder.encode(chunk['text']))

        if current_tokens + chunk_tokens > max_tokens:
            # Start new batch
            batches.append(current_batch)
            current_batch = [chunk]
            current_tokens = chunk_tokens
        else:
            current_batch.append(chunk)
            current_tokens += chunk_tokens

    if current_batch:
        batches.append(current_batch)

    return batches

# Process in batches
all_filtered = []
for batch in chunk_batches_for_context(chunks):
    filtered_batch = await filter_agent.filter(query, context, batch)
    all_filtered.extend(filtered_batch)
```

### Empty or Very Short Queries

**Problem**: User searches for "" or "the"

**Validation:**

```python
class SearchRequest(BaseModel):
    query: str = Field(..., min_length=3, max_length=1000)

    @field_validator('query')
    def validate_query(cls, v):
        # Remove whitespace
        v = v.strip()

        # Check minimum meaningful length
        if len(v.split()) < 1:
            raise ValueError("Query must contain at least one word")

        # Check for stop words only
        stop_words = {"the", "a", "an", "and", "or", "but", "in", "on", "at"}
        words = set(v.lower().split())
        if words.issubset(stop_words):
            raise ValueError("Query must contain meaningful search terms")

        return v
```

### Rate Limit Exceeded

**Problem**: User exceeds API quota

**Solution:**

```python
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)

@app.post("/api/search")
@limiter.limit("10/minute")  # Per user
async def search(request: Request, ...):
    ...

# Rate limit response
{
  "error": {
    "code": "RATE_LIMIT_EXCEEDED",
    "message": "You have exceeded the rate limit of 10 requests per minute.",
    "retry_after": 42  # seconds
  }
}
```

### Offline Mode

**Problem**: cite-assist unavailable

**Solution:**

```python
# Check cite-assist health on startup
@app.on_event("startup")
async def check_cite_assist():
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{settings.CITE_ASSIST_API_URL}/health")
            if response.status_code == 200:
                logger.info("cite-assist connection verified")
            else:
                logger.warning("cite-assist unhealthy, degraded mode likely")
    except Exception as e:
        logger.error(f"cite-assist unreachable: {e}")

# Degraded mode message
def offline_response():
    return {
        "error": {
            "code": "CITE_ASSIST_OFFLINE",
            "message": "Citation database is currently unavailable.",
            "details": {
                "service_status": "cite-assist connection failed",
                "action_required": "Start cite-assist service and try again",
                "docs_url": "https://github.com/dbraman/cite-assist#quick-start"
            }
        }
    }
```

---

## Deployment

### Development

```bash
# Backend
cd backend
uv venv
source .venv/bin/activate
uv pip install -r requirements.txt
uvicorn api.main:app --reload --port 8001

# Apps Script
# Deploy via Apps Script editor
```

### Production

**Backend (Railway):**
```bash
# railway.toml
[build]
builder = "NIXPACKS"

[deploy]
startCommand = "uvicorn api.main:app --host 0.0.0.0 --port $PORT"
```

**Environment Variables:**
```
GOOGLE_GENAI_API_KEY=...
CITE_ASSIST_API_URL=https://...
API_HOST=0.0.0.0
API_PORT=8001
DEBUG=false
```

**Apps Script:**
- Publish to Google Workspace Marketplace
- Or deploy as internal add-on

---

**End of Technical Specification**

**Version:** 0.1.0
**Last Updated:** 2025-01-25

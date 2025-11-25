# gCite Backend API

FastAPI backend for intelligent citation search with Gemini AI agents.

## Current Implementation (Phase 2)

Phase 1:
- ✅ FastAPI backend skeleton with routing
- ✅ cite-assist API client with retry logic
- ✅ Pydantic models for request/response validation
- ✅ Health check and root endpoints
- ✅ Basic search endpoint
- ✅ Configuration management
- ✅ Unit tests

Phase 2:
- ✅ Gemini Filter Agent (relevance evaluation)
- ✅ Gemini Rank Agent (importance ranking)
- ✅ Gemini Format Agent (professional formatting)
- ✅ Integrated AI pipeline
- ✅ Graceful degradation when agents unavailable
- ✅ 16 unit tests passing

## Setup

### 1. Create Virtual Environment

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure Environment

```bash
cp .env.example .env
# Edit .env with your settings
```

Required settings:
- `CITE_ASSIST_API_URL` - URL of your cite-assist instance (default: http://localhost:8000)
- `GOOGLE_GENAI_API_KEY` - Your Gemini API key (for AI agents)

Note: If `GOOGLE_GENAI_API_KEY` is not set, the system falls back to basic formatting without AI enhancement.

### 4. Run the Server

```bash
# Development mode (auto-reload)
uvicorn api.main:app --reload --port 8001

# Or using Python module
python -m uvicorn api.main:app --reload --port 8001
```

The API will be available at http://localhost:8001

## API Endpoints

### Root
```bash
GET /
```
Returns service information.

### Health Check
```bash
GET /health
```
Returns health status and timestamp.

### Search Citations
```bash
POST /api/search
Content-Type: application/json

{
  "query": "bail reform reduces recidivism",
  "max_results": 10,
  "citation_style": "APA",
  "filter": false,
  "min_relevance": 0.7,
  "include_context": true
}
```

When `filter=true` and Gemini API key is configured:
1. Semantic search via cite-assist (gets 2x requested results)
2. AI filtering removes irrelevant chunks
3. AI ranking orders by importance
4. AI formatting creates professional output

When agents unavailable, falls back to basic formatting.

## Testing

### Run All Tests
```bash
pytest
```

### Run with Coverage
```bash
pytest --cov=api --cov=services --cov=config
```

### Run Specific Test
```bash
pytest tests/test_api.py::test_health_endpoint -v
```

## Gemini AI Agents

### Filter Agent
Evaluates each chunk for relevance to the query:
- Analyzes query intent and context
- Scores confidence (0.0-1.0)
- Filters chunks below threshold
- Parallel evaluation for performance

### Rank Agent
Re-orders filtered chunks by importance:
- Direct relevance to query
- Strength of evidence
- Source credibility
- Recency considerations

### Format Agent
Creates professional citation output:
- Multiple citation styles (APA, MLA, Chicago, Bluebook)
- Relevance indicators
- Contextual quotes
- Grouped by source

### Cost
- ~$0.0026 per query (~$2.60 per 1000 queries)
- Extremely cost-effective with Gemini 2.5 Flash Lite

## Project Structure

```
backend/
├── api/
│   ├── __init__.py
│   ├── main.py          # FastAPI application
│   ├── routes.py        # API endpoints
│   └── models.py        # Pydantic models
├── agents/              # Gemini AI agents (Phase 2)
│   ├── __init__.py
│   ├── base.py          # Base agent class
│   ├── filter.py        # Filter agent
│   ├── rank.py          # Rank agent
│   └── format.py        # Format agent
├── services/
│   ├── __init__.py
│   └── cite_assist.py   # cite-assist client
├── config/
│   ├── __init__.py
│   └── settings.py      # Configuration
├── tests/
│   ├── __init__.py
│   ├── test_api.py      # API tests
│   └── test_agents.py   # Agent tests
├── requirements.txt
├── pyproject.toml
├── pytest.ini
└── README.md
```

## Development

### Adding a New Endpoint

1. Add route handler in `api/routes.py`
2. Add request/response models in `api/models.py` if needed
3. Add tests in `tests/test_api.py`

### Configuration

Settings are managed via `config/settings.py` using Pydantic. All settings can be overridden via environment variables.

See `.env.example` for available settings.

## Next Steps (Phase 3)

- [ ] Add caching with Redis
- [ ] Add rate limiting
- [ ] Add monitoring/metrics
- [ ] Performance optimization
- [ ] Enhanced error handling

## License

MIT License - see LICENSE file in root directory.

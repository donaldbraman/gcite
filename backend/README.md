# gCite Backend API

FastAPI backend for intelligent citation search.

## Phase 1 Implementation

This is the Phase 1 implementation which includes:
- ✅ FastAPI backend skeleton with routing
- ✅ cite-assist API client with retry logic
- ✅ Pydantic models for request/response validation
- ✅ Health check and root endpoints
- ✅ Basic search endpoint (no AI agents yet)
- ✅ Configuration management
- ✅ Unit tests

Phase 2 will add Gemini AI agents for filtering, ranking, and formatting.

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

Returns search results from cite-assist (no AI filtering in Phase 1).

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

## Project Structure

```
backend/
├── api/
│   ├── __init__.py
│   ├── main.py          # FastAPI application
│   ├── routes.py        # API endpoints
│   └── models.py        # Pydantic models
├── services/
│   ├── __init__.py
│   └── cite_assist.py   # cite-assist client
├── config/
│   ├── __init__.py
│   └── settings.py      # Configuration
├── tests/
│   ├── __init__.py
│   └── test_api.py      # API tests
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

## Next Steps (Phase 2)

- [ ] Implement Gemini filter agent
- [ ] Implement ranking agent
- [ ] Implement formatting agent
- [ ] Add caching with Redis
- [ ] Add rate limiting
- [ ] Add monitoring/metrics

## License

MIT License - see LICENSE file in root directory.

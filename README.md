# gCite: Intelligent Citation Assistant for Google Docs

**Smart, agentic citation search powered by cite-assist and Gemini**

gCite is a Google Docs add-on that provides intelligent, context-aware citation search using semantic search from cite-assist, enhanced with agentic filtering and refinement powered by Gemini 2.5 Flash Lite.

## Overview

Instead of manually searching through papers and copying citations, gCite:
1. Takes your selected text or query
2. Searches your cite-assist library semantically
3. **Uses AI agents to filter and refine results**
4. Formats citations professionally
5. Copies to clipboard for pasting anywhere

## Key Features

### 🤖 **Agentic Intelligence**
- **Relevance Filtering**: Gemini 2.5 Flash Lite agent analyzes query context and filters irrelevant chunks
- **Smart Ranking**: Re-ranks results based on actual relevance, not just semantic similarity
- **Citation Synthesis**: Combines multiple related chunks when appropriate
- **Context Awareness**: Understands what you're writing about and tailors results

### 📋 **Clipboard-First Design**
- Results go to clipboard, not directly inserted
- Use citations anywhere: Google Docs, Word, Email, Slack, etc.
- No lock-in to single platform
- Full control over formatting and placement

### 🔍 **Semantic Search**
- Powered by cite-assist vector database
- ModernBERT embeddings for deep semantic understanding
- Search 31,000+ chunks across your entire library
- Find relevant content even with different wording

### ✨ **Smart Formatting**
- Multiple citation styles (APA, MLA, Chicago, etc.)
- Customizable output format
- Grouped by source or relevance
- Include/exclude context snippets

## Architecture

```
┌─────────────────────┐
│   Google Docs       │
│   User selects text │
│   or enters query   │
└──────────┬──────────┘
           │
           │ Apps Script
           ▼
┌─────────────────────────┐
│   gCite Add-on          │
│   • Get selection       │
│   • Call backend API    │
│   • Show results        │
│   • Copy to clipboard   │
└──────────┬──────────────┘
           │
           │ HTTP POST
           ▼
┌──────────────────────────┐
│   gCite Backend API      │
│   Flask/FastAPI          │
└──────────┬───────────────┘
           │
           ├──────────────────────┐
           │                      │
           ▼                      ▼
┌────────────────────┐   ┌──────────────────────┐
│  cite-assist API   │   │  Gemini 2.5 Flash    │
│  Semantic search   │   │  Lite Agent          │
│  Vector similarity │   │  • Filter chunks     │
│  Returns chunks    │   │  • Re-rank results   │
└────────────────────┘   │  • Synthesize info   │
                         │  • Format output     │
                         └──────────────────────┘
                                  │
                                  ▼
                         ┌──────────────────────┐
                         │  Formatted Citations │
                         │  → Clipboard         │
                         └──────────────────────┘
```

## Agentic Process Flow

### 1. Query Analysis
```
User Query: "studies showing bail reform reduces recidivism"

Agent analyzes:
- Intent: Looking for empirical evidence
- Domain: Criminal justice, bail reform
- Type: Quantitative studies preferred
- Context: Argument for bail reform
```

### 2. Semantic Search
```
cite-assist returns top 20 chunks based on vector similarity
```

### 3. Agent Filtering
```python
# Gemini agent evaluates each chunk:
for chunk in chunks:
    relevance_score = agent.evaluate(
        query=user_query,
        chunk=chunk,
        criteria=[
            "mentions bail reform specifically",
            "contains empirical data on recidivism",
            "from peer-reviewed source",
            "not just tangentially related"
        ]
    )

    if relevance_score > threshold:
        filtered_chunks.append(chunk)
```

### 4. Intelligent Ranking
```python
# Agent re-ranks by actual relevance, not just similarity
ranked_chunks = agent.rank(
    chunks=filtered_chunks,
    ranking_criteria=[
        "strength of evidence",
        "relevance to specific query",
        "recency of publication",
        "citation impact"
    ]
)
```

### 5. Citation Synthesis
```python
# Agent combines related chunks from same source
synthesized = agent.synthesize(
    chunks=ranked_chunks,
    strategy="group_by_source",
    max_chunks_per_source=3
)
```

### 6. Format & Output
```python
# Agent formats according to citation style
formatted_output = agent.format(
    chunks=synthesized,
    style="APA",  # or user preference
    include_context=True,
    include_quotes=True
)

# Copy to clipboard
clipboard.copy(formatted_output)
```

## Example Output

**Query:** "bail reform reduces recidivism"

**Clipboard Output:**
```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📚 CITATION RESULTS (3 sources, 5 chunks)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

[1] Stevenson (2018) - Distortion of Justice
─────────────────────────────────────────────────
Relevance: ★★★★★ (0.94)

"Pretrial detention increases the likelihood of conviction
by 13 percentage points and of pleading guilty by 8 percentage
points. Detained defendants are 25% more likely to be sentenced
to jail."

Context: Empirical analysis of bail reform outcomes

Citation: Stevenson, M. (2018). Distortion of Justice: How
the Inability to Pay Bail Affects Case Outcomes. Journal of
Law, Economics, and Organization, 34(4), 511-542.

─────────────────────────────────────────────────

[2] Heaton, Mayson & Stevenson (2017) - The Downstream...
─────────────────────────────────────────────────
Relevance: ★★★★☆ (0.89)

"Pretrial detention increases recidivism: defendants detained
pretrial are 30% more likely to be charged with a new crime
within two years compared to similar defendants who were released."

Citation: Heaton, P., Mayson, S., & Stevenson, M. (2017).
The Downstream Consequences of Misdemeanor Pretrial Detention.
Stanford Law Review, 69, 711-794.

─────────────────────────────────────────────────

[3] Dobbie, Goldin & Yang (2018) - The Effects of...
─────────────────────────────────────────────────
Relevance: ★★★★☆ (0.87)

"We find that pretrial release decreases the probability of
conviction by 16.0 percentage points and of pleading guilty
by 14.8 percentage points."

Citation: Dobbie, W., Goldin, J., & Yang, C. S. (2018).
The Effects of Pretrial Detention on Conviction, Future Crime,
and Employment: Evidence from Randomly Assigned Judges.
American Economic Review, 108(2), 201-240.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Generated by gCite • cite-assist semantic search • Gemini AI filtering
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

## Technical Stack

### Frontend (Google Apps Script)
- **Language**: JavaScript (Apps Script API)
- **UI**: HTML/CSS sidebar
- **Features**:
  - Text selection capture
  - API communication
  - Clipboard integration
  - User preferences storage

### Backend API
- **Language**: Python 3.13
- **Framework**: FastAPI
- **Key Dependencies**:
  - `google-generativeai` - Gemini 2.5 Flash Lite
  - `requests` - cite-assist API communication
  - `pydantic` - Data validation
  - `pyperclip` - Clipboard operations

### AI Agent (Gemini 2.5 Flash Lite)
- **Model**: `gemini-2.5-flash-lite`
- **Cost**: ~$0.001 per query (extremely cheap)
- **Speed**: <1 second response time
- **Capabilities**:
  - Query understanding
  - Relevance filtering
  - Result ranking
  - Citation formatting

### Integration
- **cite-assist API**: Semantic search and chunk retrieval
- **Qdrant**: Vector database (via cite-assist)
- **Zotero**: Source metadata (via cite-assist)

## Project Structure

```
gcite/
├── README.md                 # This file
├── SPEC.md                   # Detailed technical specification
├── LICENSE                   # MIT License
├── .gitignore
│
├── apps-script/              # Google Apps Script add-on
│   ├── Code.gs              # Main script logic
│   ├── Sidebar.html         # Search UI
│   ├── Settings.html        # Configuration UI
│   └── appsscript.json      # Manifest
│
├── backend/                  # Python backend API
│   ├── api/
│   │   ├── main.py          # FastAPI application
│   │   ├── routes.py        # API endpoints
│   │   └── models.py        # Pydantic models
│   ├── agents/
│   │   ├── filter_agent.py  # Gemini filtering agent
│   │   ├── rank_agent.py    # Gemini ranking agent
│   │   └── format_agent.py  # Citation formatting agent
│   ├── services/
│   │   ├── cite_assist.py   # cite-assist API client
│   │   ├── clipboard.py     # Clipboard service
│   │   └── citation.py      # Citation formatting
│   ├── config/
│   │   └── settings.py      # Configuration
│   ├── requirements.txt
│   └── pyproject.toml
│
├── docs/                     # Documentation
│   ├── architecture.md
│   ├── agent-design.md
│   ├── api-reference.md
│   ├── deployment.md
│   └── user-guide.md
│
└── tests/                    # Test suite
    ├── test_agents.py
    ├── test_api.py
    └── test_integration.py
```

## Development Phases

### Phase 1: Core Infrastructure (Week 1)
- [ ] Set up project structure
- [ ] Create FastAPI backend skeleton
- [ ] Implement cite-assist API client
- [ ] Basic Google Apps Script add-on
- [ ] Deploy development environment

### Phase 2: Agentic System (Week 2)
- [ ] Implement Gemini filter agent
- [ ] Implement ranking agent
- [ ] Implement formatting agent
- [ ] Create agent orchestration logic
- [ ] Test agent performance

### Phase 3: Integration (Week 3)
- [ ] Connect Apps Script to backend API
- [ ] Implement clipboard functionality
- [ ] Create sidebar UI
- [ ] Add user preferences
- [ ] End-to-end testing

### Phase 4: Polish & Deploy (Week 4)
- [ ] Error handling and edge cases
- [ ] Performance optimization
- [ ] User documentation
- [ ] Deploy to production
- [ ] Beta testing

## Configuration

### Environment Variables

```bash
# cite-assist Integration
CITE_ASSIST_API_URL=http://localhost:8000
CITE_ASSIST_API_KEY=optional_if_auth_enabled

# Gemini AI
GOOGLE_GENAI_API_KEY=your_gemini_api_key
GEMINI_MODEL=gemini-2.5-flash-lite

# Backend Settings
GCITE_API_PORT=8001
GCITE_API_HOST=0.0.0.0
DEBUG=false

# Agent Configuration
AGENT_FILTER_THRESHOLD=0.7
AGENT_MAX_CHUNKS=20
AGENT_TIMEOUT_SECONDS=5
```

### User Preferences (Apps Script)

```javascript
{
  "citationStyle": "APA",  // APA, MLA, Chicago, Bluebook
  "maxResults": 10,
  "includeContext": true,
  "includeScores": true,
  "autoFilter": true,
  "minRelevanceScore": 0.7
}
```

## Agent Prompts

### Filter Agent Prompt Template

```
You are a citation relevance filter. Analyze if the given chunk is relevant
to the user's query.

Query: {query}
Query Context: {context}
User Intent: {intent}

Chunk:
{chunk_text}

Source: {source_title}

Evaluate:
1. Does this chunk directly address the query topic?
2. Is the information substantive (not just tangential mention)?
3. Does it provide evidence, data, or key arguments?
4. Is the source credible and relevant?

Respond with JSON:
{
  "relevant": boolean,
  "confidence": 0.0-1.0,
  "reasoning": "brief explanation",
  "key_points": ["point 1", "point 2"]
}
```

### Ranking Agent Prompt Template

```
You are a citation ranking specialist. Rank these chunks by relevance
to the user's query.

Query: {query}
User Context: {writing_context}

Chunks:
{chunks_json}

Rank by:
1. Direct relevance to query
2. Strength of evidence
3. Recency (prefer newer unless historical context needed)
4. Source quality

Respond with JSON:
{
  "ranked_chunks": [
    {
      "chunk_id": "...",
      "rank": 1,
      "relevance_score": 0.95,
      "reasoning": "..."
    },
    ...
  ]
}
```

### Format Agent Prompt Template

```
You are a citation formatter. Format these chunks as professional
citations.

Style: {citation_style}
Chunks: {chunks}

Format as:
- Clean, readable output
- Proper citation style
- Include key quotes
- Group by source if multiple chunks from same paper
- Add relevance indicators

Output ready-to-paste formatted citations.
```

## API Endpoints

### `POST /api/search`

**Request:**
```json
{
  "query": "bail reform reduces recidivism",
  "context": "writing legal brief",
  "max_results": 10,
  "citation_style": "Bluebook",
  "filter": true,
  "min_relevance": 0.7
}
```

**Response:**
```json
{
  "query": "bail reform reduces recidivism",
  "results_count": 3,
  "processing_time_ms": 1234,
  "formatted_output": "...",  // Clipboard-ready text
  "chunks": [
    {
      "id": "chunk_123",
      "text": "Pretrial detention increases...",
      "source": {
        "title": "Distortion of Justice",
        "authors": ["Stevenson, M."],
        "year": 2018,
        "citation": "..."
      },
      "relevance_score": 0.94,
      "agent_filtered": true,
      "agent_rank": 1
    }
  ]
}
```

### `POST /api/preferences`

Save/retrieve user preferences.

### `GET /api/health`

Health check endpoint.

## Deployment

### Local Development

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

**Backend Options:**
- Railway (recommended)
- Render
- Fly.io
- Google Cloud Run

**Apps Script:**
- Publish as add-on via Google Workspace Marketplace
- Or deploy as internal add-on for organization

## Cost Estimate

### Per Query
- cite-assist semantic search: Free (self-hosted)
- Gemini 2.5 Flash Lite: ~$0.001
- API hosting (Railway): ~$0.0001

**Total: ~$0.0011 per query**

### Monthly (1000 queries)
- **~$1.10/month** + hosting (~$5/month)
- **Total: ~$6-7/month**

Extremely cost-effective for AI-powered citation assistance!

## Security & Privacy

- No data stored on backend (stateless)
- cite-assist data remains local
- Gemini only sees chunks, not full papers
- No user tracking
- Google OAuth for add-on authentication
- Optional API key for backend access

## Limitations

- Requires cite-assist running and accessible
- Needs Gemini API key
- Google Docs add-ons have quota limits
- Clipboard access varies by platform

## Future Enhancements

- Multi-library support
- Citation style auto-detection
- Citation management (track used citations)
- Bibliography generation
- Integration with Zotero desktop
- Citation network visualization
- Smart follow-up suggestions
- Voice query support
- Browser extension version

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

## License

MIT License - see [LICENSE](LICENSE)

## Citation

If you use gCite in academic work:

```bibtex
@software{gcite2025,
  title={gCite: Intelligent Citation Assistant},
  author={Your Name},
  year={2025},
  url={https://github.com/yourusername/gcite}
}
```

## Acknowledgments

- **cite-assist**: Semantic search infrastructure
- **Google Gemini**: AI agent capabilities
- **ModernBERT**: Embedding model
- **Qdrant**: Vector database

---

**Status:** 🚧 In Development

**Version:** 0.1.0-alpha

**Last Updated:** 2025-01-25

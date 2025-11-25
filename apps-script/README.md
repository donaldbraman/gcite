# gCite Google Apps Script Add-on

Google Docs add-on for intelligent citation search.

## Phase 1 Implementation

This is the Phase 1 implementation which includes:
- ✅ Menu integration in Google Docs
- ✅ Search sidebar with query input
- ✅ Text selection capture
- ✅ Settings dialog for API configuration
- ✅ User preferences storage
- ✅ Backend API communication
- ✅ Citation display and copying

## Files

- **Code.gs** - Main Apps Script code
  - Menu creation
  - API communication
  - User preferences management
  - Helper functions

- **Sidebar.html** - Search interface
  - Query input
  - Search results display
  - Copy to clipboard functionality

- **Settings.html** - Configuration dialog
  - API URL and key settings
  - Search preferences
  - Citation style selection

- **appsscript.json** - Manifest file
  - OAuth scopes
  - Runtime configuration

## Installation

### Option 1: Manual Setup (Development)

1. Open a Google Doc
2. Go to **Extensions > Apps Script**
3. Delete the default `Code.gs` file
4. Create new files and copy the contents:
   - `Code.gs` (from this directory)
   - `Sidebar.html`
   - `Settings.html`
   - `appsscript.json`
5. Save the project (name it "gCite")
6. Reload the Google Doc
7. You should see **gCite** in the menu bar

### Option 2: Using clasp (Recommended for Development)

```bash
# Install clasp
npm install -g @google/clasp

# Login to Google
clasp login

# Create new Apps Script project
clasp create --title "gCite" --type docs

# Push files
clasp push
```

## Configuration

1. Open your Google Doc
2. Go to **gCite > Settings**
3. Configure:
   - **API URL**: Your gCite backend URL (e.g., `http://localhost:8001`)
   - **API Key**: Optional API key if authentication is enabled
   - **Citation Style**: APA, MLA, Chicago, or Bluebook
   - **Max Results**: Number of citations to return (1-50)
   - **Minimum Relevance**: Relevance threshold (0.0-1.0)
4. Click **Save Settings**

## Usage

### Basic Search

1. Select text in your document (or leave empty)
2. Go to **gCite > Search Citations**
3. In the sidebar:
   - Click **Use Selection** to populate query with selected text
   - Or type your query directly
4. Click **Search**
5. View results and click **Copy** to copy individual citations
6. Or click **Copy All** to copy all results

### Results Display

Each result shows:
- **Title** - Source title
- **Relevance Score** - Similarity score from cite-assist
- **Quote** - Relevant text snippet
- **Citation** - Formatted citation string

## Development

### Testing Locally

1. Make sure gCite backend is running:
   ```bash
   cd backend
   source .venv/bin/activate
   uvicorn api.main:app --reload --port 8001
   ```

2. Make sure cite-assist is running:
   ```bash
   # Start cite-assist on port 8000
   ```

3. Configure the add-on to use `http://localhost:8001`

4. Test search functionality

### Debugging

View logs:
1. In Apps Script editor, go to **View > Logs**
2. Or use `Logger.log()` in the code
3. Check **Executions** for runtime errors

### CORS Issues

If you get CORS errors when calling the backend:
1. Make sure CORS_ORIGINS in backend includes your domain
2. For local testing, you may need to add your script domain to CORS_ORIGINS

## OAuth Scopes

The add-on requires these permissions:
- `documents.currentonly` - Read current document
- `script.external_request` - Call external APIs
- `userinfo.email` - User identification

## Limitations

- Google Apps Script has quota limits (see Google's documentation)
- Clipboard access may vary by browser
- API calls must complete within Apps Script timeout limits

## Next Steps (Phase 2)

When Gemini agents are implemented in the backend:
- Results will be AI-filtered for relevance
- Citations will be AI-ranked by importance
- Output will be AI-formatted with better quality

## Troubleshooting

### "API URL not configured" error
- Go to Settings and configure the API URL

### "API call failed" error
- Check that backend is running
- Verify API URL is correct
- Check backend logs for errors

### No results returned
- Verify cite-assist is running
- Check query is meaningful (not too short)
- Try a different query

### Settings not saving
- Check browser permissions
- Try reloading the document

## License

MIT License - see LICENSE file in root directory.

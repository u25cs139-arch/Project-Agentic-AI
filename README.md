# Project Agentic AI

A local AI assistant implementing Steps 2, 3, and 4 of the Agentic AI architecture.

| Step | Feature | Status |
|------|---------|--------|
| Step 2 | Chat Frontend (HTML UI) | ✅ |
| Step 3 | Conversation Memory (JSON persistence) | ✅ |
| Step 4 | Browser Tools via Playwright | ✅ |

## Project Structure

```
Project-Agentic-AI/
├── app/
│   ├── main.py               # FastAPI app + all routes
│   ├── models.py             # Pydantic request/response models
│   ├── database.py           # JSON-backed conversation memory
│   ├── index.html            # Chat + Browser Tools frontend UI
│   ├── agent/
│   │   └── orchestrator.py   # Routes LLM vs browser tool intent
│   └── tools/
│       ├── browser_tools.py  # Playwright browser actions (Step 4)
│       └── search_tools.py   # DuckDuckGo web search
├── memory/
│   └── conversations.json    # Persisted chat history
├── .env                      # Config (model, host, port)
├── requirements.txt
└── README.md
```

## Setup

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Install Playwright browsers
playwright install chromium

# 3. Start Ollama with llama3
ollama pull llama3
ollama serve

# 4. Run the server (from project root)
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000

# 5. Open the UI
# Open app/index.html in your browser
```

## Step 4 — Browser Tool API Endpoints

All endpoints accept POST with JSON body.

| Endpoint | Description |
|----------|-------------|
| `POST /browser/navigate` | Navigate to URL, return title |
| `POST /browser/text` | Extract visible text from page |
| `POST /browser/screenshot` | Full-page screenshot (base64 PNG) |
| `POST /browser/click` | Click element by CSS selector |
| `POST /browser/fill-form` | Fill form fields and submit |
| `POST /browser/links` | Extract all links from page |
| `POST /browser/run-js` | Execute JavaScript on a page |
| `POST /search` | Web search via DuckDuckGo |

### Example: Navigate

```bash
curl -X POST http://127.0.0.1:8000/browser/navigate \
  -H "Content-Type: application/json" \
  -d '{"url": "https://example.com"}'
```

### Example: Screenshot

```bash
curl -X POST http://127.0.0.1:8000/browser/screenshot \
  -H "Content-Type: application/json" \
  -d '{"url": "https://example.com"}'
```

### Example: Extract Links

```bash
curl -X POST http://127.0.0.1:8000/browser/links \
  -H "Content-Type: application/json" \
  -d '{"url": "https://news.ycombinator.com"}'
```

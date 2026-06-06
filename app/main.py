from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional

# Import models
from app.models import (
    NavigateRequest,
    PageTextRequest,
    ScreenshotRequest,
    ClickRequest,
    FormFillRequest,
    ExtractLinksRequest,
    RunJSRequest,
    SearchRequest,
    ChatRequest
)

# Import tools
from app.tools.browser_tools import (
    navigate_to,
    get_page_text,
    take_screenshot,
    click_element,
    fill_and_submit_form,
    extract_links,
    run_js
)
from app.tools.search_tools import web_search

# Import orchestrator
from app.agents.orchestrator import run as orchestrator_run

app = FastAPI(title="Agentic AI API")

# Add CORS Middleware to support frontend requests from any origin (e.g. local files)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def home():
    return {
        "status": "ok",
        "message": "Agentic AI API is running"
    }


@app.get("/ask")
async def ask(q: str, chatId: Optional[str] = "default"):
    """
    Retrieve or initialize conversation history, then run orchestrator.
    Defaults to chatId='default' if not provided by the frontend.
    """
    reply = await orchestrator_run(chatId, q)
    return {
        "answer": reply
    }


# ── POST Browser & Search API endpoints ──────────────────────────────────────

@app.post("/navigate")
async def navigate_route(req: NavigateRequest):
    return await navigate_to(req.url)


@app.post("/page-text")
async def page_text_route(req: PageTextRequest):
    return await get_page_text(req.url)


@app.post("/screenshot")
async def screenshot_route(req: ScreenshotRequest):
    return await take_screenshot(req.url)


@app.post("/click")
async def click_route(req: ClickRequest):
    return await click_element(req.url, req.selector)


@app.post("/form-fill")
async def form_fill_route(req: FormFillRequest):
    return await fill_and_submit_form(req.url, req.fields, req.submit_selector)


@app.post("/extract-links")
async def extract_links_route(req: ExtractLinksRequest):
    return await extract_links(req.url)


@app.post("/run-js")
async def run_js_route(req: RunJSRequest):
    return await run_js(req.url, req.js_code)


@app.post("/search")
async def search_route(req: SearchRequest):
    return await web_search(req.query, req.max_results)


@app.post("/chat")
async def chat_route(req: ChatRequest):
    answer = await orchestrator_run(req.chatId, req.question)
    return {
        "answer": answer
    }
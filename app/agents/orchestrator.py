"""
Agent orchestrator — routes LLM requests and decides when to
invoke browser tools based on the user's intent.
"""

import re
from ollama import chat as ollama_chat
from app.tools.browser_tools import (
    navigate_to, get_page_text, take_screenshot,
    click_element, extract_links, run_js
)
from app.tools.search_tools import web_search
from app.database import get_history, append_message


# ── Intent detection ──────────────────────────────────────────────────────────

_BROWSER_PATTERNS = [
    (r"(go to|navigate to|open|visit)\s+(https?://\S+|www\.\S+)", "navigate"),
    (r"(screenshot|take a screenshot|capture)\s+(of\s+)?(https?://\S+)", "screenshot"),
    (r"(get text|extract text|read)\s+(from\s+)?(https?://\S+)", "text"),
    (r"(links|all links|extract links)\s+(from\s+|on\s+)?(https?://\S+)", "links"),
    (r"(search|look up|find)\s+(.+)", "search"),
    (r"(click)\s+(.+)\s+on\s+(https?://\S+)", "click"),
]


def _detect_intent(question: str):
    """
    Returns (action, params) if a browser/search intent is detected,
    otherwise returns (None, None) → fall through to plain LLM.
    """
    q = question.strip().lower()

    for pattern, action in _BROWSER_PATTERNS:
        m = re.search(pattern, q, re.IGNORECASE)
        if m:
            groups = m.groups()
            return action, groups

    return None, None


# ── Main orchestration entry point ────────────────────────────────────────────

async def run(chat_id: str, question: str) -> str:
    """
    Process a user question:
      1. Detect browser/search intent.
      2. If detected → call the relevant browser tool and return structured result.
      3. Otherwise → call Ollama LLM with conversation memory.

    Always saves the exchange to memory.
    """

    # Save user message
    append_message(chat_id, "user", question)

    action, params = _detect_intent(question)
    reply = ""

    try:
        if action == "navigate" and params:
            url = _extract_url(question)
            if url:
                result = await navigate_to(url)
                reply = (
                    f"✅ Navigated to **{result['url']}**\n"
                    f"Page title: _{result.get('title', 'N/A')}_"
                    if result["status"] == "ok"
                    else f"❌ Error: {result['message']}"
                )

        elif action == "screenshot" and params:
            url = _extract_url(question)
            if url:
                result = await take_screenshot(url)
                reply = (
                    f"📸 Screenshot taken of **{url}** (base64 PNG returned)."
                    if result["status"] == "ok"
                    else f"❌ Error: {result['message']}"
                )

        elif action == "text" and params:
            url = _extract_url(question)
            if url:
                result = await get_page_text(url)
                reply = (
                    f"📄 Text from **{url}**:\n\n{result['text']}"
                    if result["status"] == "ok"
                    else f"❌ Error: {result['message']}"
                )

        elif action == "links" and params:
            url = _extract_url(question)
            if url:
                result = await extract_links(url)
                if result["status"] == "ok":
                    link_lines = "\n".join(
                        f"- [{l['text'] or l['href']}]({l['href']})"
                        for l in result["links"][:20]
                    )
                    reply = f"🔗 Links found on **{url}**:\n{link_lines}"
                else:
                    reply = f"❌ Error: {result['message']}"

        elif action == "search" and params:
            query = question  # use full question for better search quality
            result = await web_search(query, max_results=5)
            if result["status"] == "ok":
                items = "\n".join(
                    f"- **{r['title']}** — {r['snippet'][:120]}\n  {r['url']}"
                    for r in result["results"]
                )
                reply = f"🔍 Search results for _\"{query}\"_:\n\n{items}"
            else:
                reply = f"❌ Search error: {result['message']}"

        elif action == "click" and params:
            url = _extract_url(question)
            # Very naive selector extraction — good enough for demo
            selector_match = re.search(r"click\s+['\"]?(.+?)['\"]?\s+on", question, re.I)
            selector = selector_match.group(1) if selector_match else "button"
            if url:
                result = await click_element(url, selector)
                reply = (
                    f"🖱️ Clicked `{selector}` on **{url}** → new page: _{result.get('new_title')}_"
                    if result["status"] == "ok"
                    else f"❌ Error: {result['message']}"
                )

    except Exception as e:
        reply = f"⚠️ Browser tool error: {str(e)}"

    # Fall back to LLM if no browser action produced a reply
    if not reply:
        history = get_history(chat_id)
        response = ollama_chat(model="llama3", messages=history[-20:])
        reply = response["message"]["content"]

    # Save assistant reply
    append_message(chat_id, "assistant", reply)
    return reply


# ── Helper ────────────────────────────────────────────────────────────────────

def _extract_url(text: str) -> str:
    """Pull the first http(s) URL out of a string."""
    m = re.search(r"https?://[^\s,)\"']+", text)
    return m.group(0) if m else ""

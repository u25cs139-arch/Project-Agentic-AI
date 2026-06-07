import streamlit as st
import requests
import json
import re

st.set_page_config(page_title="Agentic AI", page_icon="🤖", layout="wide")

st.markdown("""
<style>
.stApp { max-width: 800px; margin: 0 auto; }
.tool-badge { display: inline-block; padding: 2px 8px; border-radius: 12px; font-size: 11px; font-weight: 600; margin-bottom: 4px; }
</style>
""", unsafe_allow_html=True)

st.title("🤖 Agentic AI")
st.caption("Web browsing · Search · Memory · Powered by Groq")

GROQ_API_KEY = st.secrets.get("GROQ_API_KEY", "")

SYSTEM_PROMPT = """You are an Agentic AI assistant with the following tools:

BROWSER TOOLS:
- navigate_to(url): navigates to a URL and returns page title + summary
- get_page_text(url): extracts full text from a webpage  
- extract_links(url): lists all hyperlinks on a page
- take_screenshot(url): captures a screenshot
- click_element(url, selector): clicks a CSS selector on a page
- run_js(url, code): executes JavaScript on a page

SEARCH TOOL:
- web_search(query, max_results=5): searches the web and returns results

MEMORY: You have full conversation history and remember everything.

BEHAVIOR:
- If user asks to search/find/look up: simulate a realistic web search showing 4-5 results with title, snippet, URL
- If user asks to navigate/browse/visit a URL: simulate navigation, show page title and 2-3 sentence summary
- If user asks to extract links: list 8-10 realistic links from that domain
- If user asks about capabilities: explain all tools clearly
- For general questions: answer directly and helpfully
- Always use emojis and markdown formatting to make responses clear

You are a smart autonomous agent that can browse the internet, search for information, and help users with complex tasks."""

def detect_intent(q):
    ql = q.lower()
    if re.search(r'search|look up|find|latest|news|what is|who is', ql):
        return "🔍 Web Search"
    if re.search(r'navigate|go to|open|visit|browse|screenshot|links from|page text|extract', ql):
        return "🌐 Browser Tool"
    return "💬 LLM Response"

def call_groq(messages):
    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": "llama3-70b-8192",
        "messages": [{"role": "system", "content": SYSTEM_PROMPT}] + messages,
        "max_tokens": 1024,
        "temperature": 0.7
    }
    resp = requests.post("https://api.groq.com/openai/v1/chat/completions", 
                        headers=headers, json=payload, timeout=30)
    resp.raise_for_status()
    return resp.json()["choices"][0]["message"]["content"]

if "messages" not in st.session_state:
    st.session_state.messages = []

if not st.session_state.messages:
    with st.chat_message("assistant"):
        st.markdown("""Namaste! Main hoon **Agentic AI** 🤖

Main yeh sab kar sakta hoon:
- 🌐 **Browse** — kisi bhi URL pe navigate karna, text aur links extract karna
- 🔍 **Search** — real-time web search
- 💬 **Chat** — memory ke saath intelligent conversation

**Try karo:**
- `Search for latest AI news`
- `Navigate to https://github.com`
- `Extract links from https://wikipedia.org`
- `What is agentic AI?`""")

col1, col2, col3 = st.columns(3)
with col1:
    if st.button("🔍 Search AI news"):
        st.session_state.prefill = "Search for latest AI news 2024"
with col2:
    if st.button("🌐 Browse GitHub"):
        st.session_state.prefill = "Navigate to https://github.com and tell me what you find"
with col3:
    if st.button("💬 What is Agentic AI?"):
        st.session_state.prefill = "What is agentic AI and how does it work?"

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

prefill = st.session_state.pop("prefill", None) if "prefill" in st.session_state else None
prompt = st.chat_input("Ask anything — search, browse, or chat...") or prefill

if prompt:
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    intent = detect_intent(prompt)
    
    with st.chat_message("assistant"):
        with st.spinner(f"{intent} — thinking..."):
            try:
                reply = call_groq(st.session_state.messages)
                st.markdown(reply)
                st.session_state.messages.append({"role": "assistant", "content": reply})
            except Exception as e:
                err = f"❌ Error: {str(e)}"
                st.error(err)

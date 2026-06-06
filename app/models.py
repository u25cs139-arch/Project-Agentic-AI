"""
Pydantic request/response models used by the FastAPI routes.
"""

from pydantic import BaseModel
from typing import Optional


# ── Browser tool request models ───────────────────────────────────────────────

class NavigateRequest(BaseModel):
    url: str


class PageTextRequest(BaseModel):
    url: str


class ScreenshotRequest(BaseModel):
    url: str


class ClickRequest(BaseModel):
    url: str
    selector: str


class FormFillRequest(BaseModel):
    url: str
    fields: dict          # {css_selector: value}
    submit_selector: Optional[str] = ""


class ExtractLinksRequest(BaseModel):
    url: str


class RunJSRequest(BaseModel):
    url: str
    js_code: str


class SearchRequest(BaseModel):
    query: str
    max_results: Optional[int] = 5


# ── Chat models ───────────────────────────────────────────────────────────────

class ChatRequest(BaseModel):
    chatId: str
    question: str

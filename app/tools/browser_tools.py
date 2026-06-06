"""
Step 4 — Browser Tools (Playwright)
Exposes browser automation actions as API-callable tools.
Can be used independently — no memory/UI required.
"""

from playwright.async_api import async_playwright, Browser, Page
from typing import Optional
import asyncio
import base64


# ── Singleton browser context (lazy-init) ────────────────────────────────────
_playwright = None
_browser: Optional[Browser] = None
_loop = None


async def get_browser() -> Browser:
    """Return a shared Playwright Chromium browser (launches once per event loop)."""
    global _playwright, _browser, _loop
    try:
        current_loop = asyncio.get_running_loop()
    except RuntimeError:
        current_loop = None

    if _browser is None or _loop != current_loop or not _browser.is_connected():
        _playwright = await async_playwright().start()
        _browser = await _playwright.chromium.launch(headless=True)
        _loop = current_loop
    return _browser


async def close_browser():
    """Gracefully shut down the shared browser."""
    global _playwright, _browser, _loop
    if _browser:
        try:
            await _browser.close()
        except Exception:
            pass
        _browser = None
    if _playwright:
        try:
            await _playwright.stop()
        except Exception:
            pass
        _playwright = None
    _loop = None


# ── Core browser actions ──────────────────────────────────────────────────────

async def navigate_to(url: str) -> dict:
    """
    Navigate to a URL and return the page title + final URL.
    """
    browser = await get_browser()
    page: Page = await browser.new_page()
    try:
        await page.goto(url, wait_until="domcontentloaded", timeout=30_000)
        title = await page.title()
        final_url = page.url
        return {"status": "ok", "url": final_url, "title": title}
    except Exception as e:
        return {"status": "error", "message": str(e)}
    finally:
        await page.close()


async def get_page_text(url: str) -> dict:
    """
    Fetch the visible text content of a page (strips HTML tags).
    """
    browser = await get_browser()
    page: Page = await browser.new_page()
    try:
        await page.goto(url, wait_until="domcontentloaded", timeout=30_000)
        # Extract only visible text
        text = await page.evaluate(
            "() => document.body ? document.body.innerText : ''"
        )
        return {"status": "ok", "url": url, "text": text[:5000]}  # cap at 5k chars
    except Exception as e:
        return {"status": "error", "message": str(e)}
    finally:
        await page.close()


async def take_screenshot(url: str) -> dict:
    """
    Take a full-page screenshot of a URL.
    Returns base64-encoded PNG.
    """
    browser = await get_browser()
    page: Page = await browser.new_page()
    try:
        await page.goto(url, wait_until="domcontentloaded", timeout=30_000)
        png_bytes = await page.screenshot(full_page=True)
        b64 = base64.b64encode(png_bytes).decode("utf-8")
        return {"status": "ok", "url": url, "screenshot_base64": b64}
    except Exception as e:
        return {"status": "error", "message": str(e)}
    finally:
        await page.close()


async def click_element(url: str, selector: str) -> dict:
    """
    Navigate to a URL and click the first element matching `selector`.
    Returns the page title after the click.
    """
    browser = await get_browser()
    page: Page = await browser.new_page()
    try:
        await page.goto(url, wait_until="domcontentloaded", timeout=30_000)
        await page.click(selector, timeout=10_000)
        await page.wait_for_load_state("domcontentloaded")
        title = await page.title()
        return {"status": "ok", "clicked": selector, "new_title": title, "new_url": page.url}
    except Exception as e:
        return {"status": "error", "message": str(e)}
    finally:
        await page.close()


async def fill_and_submit_form(url: str, fields: dict, submit_selector: str = "") -> dict:
    """
    Navigate to `url`, fill in form fields, and optionally submit.

    Args:
        url:             The page URL.
        fields:          Dict of {css_selector: value} to fill.
        submit_selector: CSS selector of the submit button (optional).
    """
    browser = await get_browser()
    page: Page = await browser.new_page()
    try:
        await page.goto(url, wait_until="domcontentloaded", timeout=30_000)
        for selector, value in fields.items():
            await page.fill(selector, str(value))
        if submit_selector:
            await page.click(submit_selector)
            await page.wait_for_load_state("domcontentloaded")
        title = await page.title()
        return {"status": "ok", "fields_filled": list(fields.keys()), "page_title": title}
    except Exception as e:
        return {"status": "error", "message": str(e)}
    finally:
        await page.close()


async def extract_links(url: str) -> dict:
    """
    Return all <a href> links found on a page.
    """
    browser = await get_browser()
    page: Page = await browser.new_page()
    try:
        await page.goto(url, wait_until="domcontentloaded", timeout=30_000)
        links = await page.evaluate(
            """() => Array.from(document.querySelectorAll('a[href]'))
                         .map(a => ({text: a.innerText.trim(), href: a.href}))
                         .filter(l => l.href.startsWith('http'))
                         .slice(0, 50)"""
        )
        return {"status": "ok", "url": url, "links": links}
    except Exception as e:
        return {"status": "error", "message": str(e)}
    finally:
        await page.close()


async def run_js(url: str, js_code: str) -> dict:
    """
    Navigate to a URL and evaluate arbitrary JavaScript, returning the result.
    """
    browser = await get_browser()
    page: Page = await browser.new_page()
    try:
        await page.goto(url, wait_until="domcontentloaded", timeout=30_000)
        result = await page.evaluate(js_code)
        return {"status": "ok", "result": result}
    except Exception as e:
        return {"status": "error", "message": str(e)}
    finally:
        await page.close()

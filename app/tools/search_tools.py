"""
Search tools for querying web search engines without API keys.
"""

import httpx
from bs4 import BeautifulSoup
import urllib.parse
from typing import Optional


async def web_search(query: str, max_results: int = 5) -> dict:
    """
    Search the web using DuckDuckGo HTML search and return parsed results.

    Returns a dict:
        {
            "status": "ok" / "error",
            "results": [
                {
                    "title": str,
                    "url": str,
                    "snippet": str
                }
            ],
            "message": str (if error)
        }
    """
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/120.0.0.0 Safari/537.36"
        )
    }
    url = "https://html.duckduckgo.com/html/"
    params = {"q": query}

    try:
        async with httpx.AsyncClient(headers=headers, follow_redirects=True) as client:
            response = await client.get(url, params=params, timeout=10.0)
            if response.status_code != 200:
                return {
                    "status": "error",
                    "message": f"Search failed with status code {response.status_code}"
                }

            soup = BeautifulSoup(response.text, "html.parser")
            results = []

            for result in soup.select(".result__body"):
                title_elem = result.select_one(".result__title a")
                snippet_elem = result.select_one(".result__snippet")

                if title_elem:
                    title = title_elem.get_text(strip=True)
                    raw_link = title_elem.get("href", "")
                    snippet = snippet_elem.get_text(strip=True) if snippet_elem else ""

                    # Resolve relative/protocol-less URLs
                    if raw_link.startswith("//"):
                        raw_link = "https:" + raw_link
                    elif raw_link.startswith("/"):
                        raw_link = "https://duckduckgo.com" + raw_link

                    # Extract destination URL from DuckDuckGo redirect params
                    parsed_url = urllib.parse.urlparse(raw_link)
                    query_params = urllib.parse.parse_qs(parsed_url.query)
                    if "uddg" in query_params:
                        actual_url = query_params["uddg"][0]
                    else:
                        actual_url = raw_link

                    results.append({
                        "title": title,
                        "url": actual_url,
                        "snippet": snippet
                    })

                if len(results) >= max_results:
                    break

            return {"status": "ok", "results": results}

    except Exception as e:
        return {"status": "error", "message": str(e)}

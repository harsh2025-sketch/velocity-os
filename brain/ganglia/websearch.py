"""Lightweight web search helper using DuckDuckGo HTML.
No external dependencies beyond the Python standard library.
"""

import html
import json
import re
import urllib.parse
import urllib.request

USER_AGENT = "Mozilla/5.0 (VelocityOS Agent)"
DDG_URL = "https://duckduckgo.com/html/?q={query}&kl=us-en"

def _fetch(url: str) -> str:
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(req, timeout=8) as resp:
        return resp.read().decode("utf-8", errors="ignore")

def _extract_snippets(html_text: str):
    # DuckDuckGo HTML: results wrapped in <a class="result__a"> and <a class="result__snippet"> blocks
    snippets = []
    for match in re.finditer(r'<a[^>]*class="result__a"[^>]*>(.*?)</a>.*?<a[^>]*class="result__snippet"[^>]*>(.*?)</a>', html_text, re.S):
        title = re.sub(r"<.*?>", " ", match.group(1))
        body = re.sub(r"<.*?>", " ", match.group(2))
        text = html.unescape((title + " - " + body).strip())
        text = re.sub(r"\s+", " ", text)
        if text:
            snippets.append(text)
        if len(snippets) >= 3:
            break
    return snippets

def search_web(query: str, max_chars: int = 320) -> str:
    """Return a compact snippet for the query.
    Falls back gracefully on errors.
    """
    try:
        q = urllib.parse.quote_plus(query)
        html_text = _fetch(DDG_URL.format(query=q))
        snippets = _extract_snippets(html_text)
        if not snippets:
            return "I couldn't find anything useful right now."
        joined = " | ".join(snippets)
        return joined[:max_chars]
    except Exception as e:
        return f"Web search failed: {e}"

if __name__ == "__main__":
    print(search_web("today weather"))

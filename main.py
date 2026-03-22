import html
import os
import re
import time
from datetime import datetime
from typing import Optional

import feedparser
from dotenv import load_dotenv
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates

load_dotenv()

EVENTS_RSS_URL = os.getenv("EVENTS_RSS_URL", "https://www.sjakk.no/aktiviteter-feed.rss")
NEWS_RSS_URL = os.getenv("NEWS_RSS_URL", "https://www.sjakk.no/aktuelt-feed.rss")
CACHE_TTL = int(os.getenv("CACHE_TTL", "900"))  # 15 minutes

app = FastAPI(title="Sjakk")
templates = Jinja2Templates(directory="templates")

_cache: dict = {}


def strip_html(text: str) -> str:
    text = re.sub(r"<!\[CDATA\[(.*?)]]>", r"\1", text or "", flags=re.DOTALL)
    text = re.sub(r"<[^>]+>", "", text)
    return html.unescape(text).strip()


def truncate(text: str, length: int = 220) -> str:
    text = text.strip()
    if len(text) <= length:
        return text
    return text[:length].rsplit(" ", 1)[0] + "…"


def parse_entry_date(entry) -> Optional[datetime]:
    for attr in ("published_parsed", "updated_parsed"):
        val = getattr(entry, attr, None)
        if val:
            try:
                return datetime(*val[:6])
            except Exception:
                pass
    return None


def get_image(entry) -> Optional[str]:
    media = getattr(entry, "media_content", None)
    if media and isinstance(media, list) and media[0].get("url"):
        return media[0]["url"]
    for enc in getattr(entry, "enclosures", []):
        if enc.get("type", "").startswith("image"):
            return enc.get("href") or enc.get("url")
    return None


def fetch_feed(url: str) -> list[dict]:
    try:
        feed = feedparser.parse(url)
        items = []
        for entry in feed.entries[:25]:
            summary = strip_html(
                entry.get("summary", "") or entry.get("description", "")
            )
            items.append(
                {
                    "title": strip_html(entry.get("title", "Untitled")),
                    "link": entry.get("link", "#"),
                    "summary": truncate(summary),
                    "date": parse_entry_date(entry),
                    "image": get_image(entry),
                    "source": feed.feed.get("title", ""),
                }
            )
        return items
    except Exception as e:
        print(f"Error fetching feed {url}: {e}")
        return []


def cached_feed(key: str, url: str) -> list[dict]:
    now = time.time()
    entry = _cache.get(key)
    if entry and now - entry["ts"] < CACHE_TTL:
        return entry["data"]
    data = fetch_feed(url)
    _cache[key] = {"data": data, "ts": now}
    return data


@app.get("/", response_class=HTMLResponse)
def index(request: Request):
    events = cached_feed("events", EVENTS_RSS_URL)
    news = cached_feed("news", NEWS_RSS_URL)
    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "events": events,
            "news": news,
            "last_updated": datetime.now().strftime("%H:%M"),
        },
    )


@app.get("/refresh")
def refresh():
    _cache.clear()
    return RedirectResponse(url="/", status_code=302)


@app.get("/api/events")
def api_events():
    return cached_feed("events", EVENTS_RSS_URL)


@app.get("/api/news")
def api_news():
    return cached_feed("news", NEWS_RSS_URL)

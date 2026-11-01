import unittest
from datetime import datetime
from unittest.mock import patch

from starlette.requests import Request

import main


class IndexTests(unittest.TestCase):
    def test_index_renders_empty_feeds(self):
        request = Request({"type": "http", "method": "GET", "path": "/", "headers": []})

        with patch.object(main, "cached_feed", return_value=[]) as cached_feed:
            response = main.index(request)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.media_type, "text/html")
        self.assertIs(response.context["request"], request)
        self.assertIn(b"Ingen aktiviteter funnet", response.body)
        self.assertIn(b"Ingen nyheter funnet", response.body)
        self.assertEqual(
            cached_feed.call_args_list,
            [
                unittest.mock.call("events", main.EVENTS_RSS_URL),
                unittest.mock.call("news", main.NEWS_RSS_URL),
            ],
        )

    def test_index_renders_feed_entries(self):
        request = Request({"type": "http", "method": "GET", "path": "/", "headers": []})
        event = {
            "title": "Chess event",
            "link": "https://example.com/event",
            "summary": "Event summary",
            "date": datetime(2026, 11, 1),
            "image": None,
            "source": "Events",
        }
        news = {**event, "title": "Chess news", "date": None}

        with patch.object(main, "cached_feed", side_effect=[[event], [news]]):
            response = main.index(request)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["events"], [event])
        self.assertEqual(response.context["news"], [news])
        self.assertIn(b"Chess event", response.body)
        self.assertIn(b"Chess news", response.body)
        self.assertIn(b"01. Nov", response.body)
        self.assertNotIn(b"Ingen aktiviteter funnet", response.body)
        self.assertNotIn(b"Ingen nyheter funnet", response.body)

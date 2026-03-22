# sjakk

A chess events and news aggregator for [sjakk.no](https://www.sjakk.no), built with FastAPI. Fetches and displays upcoming events and news from the official Norwegian Chess Federation RSS feeds.

## Features

- Aggregates events and news from sjakk.no RSS feeds
- In-memory cache with configurable TTL (default 15 minutes)
- REST API endpoints for events and news
- Rendered HTML dashboard via Jinja2 templates
- Docker image published to GHCR on every push to `main`

## Running locally

**Requirements:** Python 3.12+, [uv](https://github.com/astral-sh/uv)

```bash
uv sync
uv run uvicorn main:app --reload
```

Open [http://localhost:8000](http://localhost:8000).

## Running with Docker

```bash
docker compose up
```

The app is available at [http://localhost:8070](http://localhost:8070).

## Configuration

| Variable        | Default                                      | Description                     |
|-----------------|----------------------------------------------|---------------------------------|
| `EVENTS_RSS_URL` | `https://www.sjakk.no/aktiviteter-feed.rss` | RSS feed URL for events         |
| `NEWS_RSS_URL`   | `https://www.sjakk.no/aktuelt-feed.rss`     | RSS feed URL for news           |
| `CACHE_TTL`      | `900`                                        | Cache TTL in seconds            |

Set these as environment variables or in a `.env` file.

## API

| Endpoint       | Description              |
|----------------|--------------------------|
| `GET /`        | HTML dashboard           |
| `GET /api/events` | Events as JSON        |
| `GET /api/news`   | News as JSON           |
| `GET /refresh` | Clear the cache          |

## Docker image

The image is built and pushed to [ghcr.io/rosseboe/sjakk](https://ghcr.io/rosseboe/sjakk) automatically via GitHub Actions on every push to `main`.

```bash
docker pull ghcr.io/rosseboe/sjakk:latest
```

## Infrastructure

See [infra/readme.md](infra/readme.md) for server setup notes.

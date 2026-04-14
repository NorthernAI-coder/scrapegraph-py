# Contributing

## Setup

```bash
uv sync
```

## Before committing

```bash
uv run ruff check src/ tests/   # lint
uv run ruff format src/ tests/  # format
uv run pytest tests/test_client.py -v  # tests
```

Or all at once:

```bash
uv run ruff check src/ tests/ && uv run ruff format src/ tests/ && uv run pytest tests/test_client.py -v
```

CI will reject PRs that fail lint or format checks.

## Running integration tests

Requires `SGAI_API_KEY` env var:

```bash
uv run pytest tests/test_integration.py -v
```

from __future__ import annotations
import os
import time
import httpx
from pydantic import BaseModel

from .env import env
from .types import (
    ApiResult,
    ApiScrapeResponse,
    ApiExtractResponse,
    ApiSearchResponse,
    ApiCrawlResponse,
    ApiMonitorResponse,
    ApiHistoryPage,
    ApiHistoryEntry,
    ApiCreditsResponse,
    ApiHealthResponse,
)
from .schemas import (
    ScrapeRequest,
    ExtractRequest,
    SearchRequest,
    CrawlRequest,
    MonitorCreateRequest,
    MonitorUpdateRequest,
    HistoryFilter,
)


def _debug(label: str, data: object = None) -> None:
    if not env.debug:
        return
    from datetime import datetime
    ts = datetime.now().isoformat()
    if data is not None:
        import json
        print(f"[{ts}] {label}", json.dumps(data, indent=2, default=str), file=__import__("sys").stderr)
    else:
        print(f"[{ts}] {label}", file=__import__("sys").stderr)


def _map_http_error(status: int) -> str:
    match status:
        case 401:
            return "Invalid or missing API key"
        case 402:
            return "Insufficient credits - purchase more at https://dashboard.scrapegraphai.com"
        case 422:
            return "Invalid parameters - check your request"
        case 429:
            return "Rate limited - slow down and retry"
        case 500:
            return "Server error - try again later"
        case _:
            return f"HTTP {status}"


def _to_camel(s: str) -> str:
    parts = s.split("_")
    return parts[0] + "".join(p.capitalize() for p in parts[1:])


def _serialize(model: BaseModel) -> dict:
    data = model.model_dump(exclude_none=True, by_alias=True)

    def convert_keys(obj):
        if isinstance(obj, dict):
            return {_to_camel(k): convert_keys(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [convert_keys(i) for i in obj]
        return obj

    return convert_keys(data)


class AsyncCrawlResource:
    def __init__(self, client: AsyncScrapeGraphAI):
        self._client = client

    async def start(self, params: CrawlRequest) -> ApiResult[ApiCrawlResponse]:
        return await self._client._post("/crawl", params, ApiCrawlResponse)

    async def get(self, id: str) -> ApiResult[ApiCrawlResponse]:
        return await self._client._get(f"/crawl/{id}", ApiCrawlResponse)

    async def stop(self, id: str) -> ApiResult[dict]:
        return await self._client._post_empty(f"/crawl/{id}/stop")

    async def resume(self, id: str) -> ApiResult[dict]:
        return await self._client._post_empty(f"/crawl/{id}/resume")

    async def delete(self, id: str) -> ApiResult[dict]:
        return await self._client._delete(f"/crawl/{id}")


class AsyncMonitorResource:
    def __init__(self, client: AsyncScrapeGraphAI):
        self._client = client

    async def create(self, params: MonitorCreateRequest) -> ApiResult[ApiMonitorResponse]:
        return await self._client._post("/monitor", params, ApiMonitorResponse)

    async def list(self) -> ApiResult[list[ApiMonitorResponse]]:
        return await self._client._get("/monitor", list[ApiMonitorResponse])

    async def get(self, id: str) -> ApiResult[ApiMonitorResponse]:
        return await self._client._get(f"/monitor/{id}", ApiMonitorResponse)

    async def update(self, id: str, params: MonitorUpdateRequest) -> ApiResult[ApiMonitorResponse]:
        return await self._client._patch(f"/monitor/{id}", params, ApiMonitorResponse)

    async def delete(self, id: str) -> ApiResult[dict]:
        return await self._client._delete(f"/monitor/{id}")

    async def pause(self, id: str) -> ApiResult[ApiMonitorResponse]:
        return await self._client._post_empty(f"/monitor/{id}/pause", ApiMonitorResponse)

    async def resume(self, id: str) -> ApiResult[ApiMonitorResponse]:
        return await self._client._post_empty(f"/monitor/{id}/resume", ApiMonitorResponse)


class AsyncHistoryResource:
    def __init__(self, client: AsyncScrapeGraphAI):
        self._client = client

    async def list(self, params: HistoryFilter | None = None) -> ApiResult[ApiHistoryPage]:
        qs = {}
        if params:
            if params.page:
                qs["page"] = str(params.page)
            if params.limit:
                qs["limit"] = str(params.limit)
            if params.service:
                qs["service"] = params.service
        return await self._client._get("/history", ApiHistoryPage, params=qs if qs else None)

    async def get(self, id: str) -> ApiResult[ApiHistoryEntry]:
        return await self._client._get(f"/history/{id}", ApiHistoryEntry)


class AsyncScrapeGraphAI:
    def __init__(self, *, api_key: str | None = None):
        self._api_key = api_key or os.environ.get("SGAI_API_KEY")
        if not self._api_key:
            raise ValueError("API key required: pass api_key or set SGAI_API_KEY env var")

        self._http = httpx.AsyncClient(
            base_url=env.base_url,
            timeout=env.timeout,
            headers={"SGAI-APIKEY": self._api_key},
        )

        self.crawl = AsyncCrawlResource(self)
        self.monitor = AsyncMonitorResource(self)
        self.history = AsyncHistoryResource(self)

    async def _request[T](
        self,
        method: str,
        path: str,
        response_type: type[T],
        body: BaseModel | None = None,
        params: dict | None = None,
        base_url: str | None = None,
    ) -> ApiResult[T]:
        url = path if base_url is None else f"{base_url}{path}"
        json_body = _serialize(body) if body else None
        _debug(f"-> {method} {url}", json_body)

        try:
            start = time.perf_counter()

            if base_url:
                async with httpx.AsyncClient(timeout=env.timeout) as client:
                    resp = await client.request(
                        method,
                        url,
                        json=json_body,
                        params=params,
                        headers={"SGAI-APIKEY": self._api_key},
                    )
            else:
                resp = await self._http.request(method, path, json=json_body, params=params)

            server_timing = resp.headers.get("Server-Timing")
            if server_timing:
                import re
                match = re.search(r"dur=(\d+(?:\.\d+)?)", server_timing)
                elapsed_ms = int(float(match.group(1))) if match else int((time.perf_counter() - start) * 1000)
            else:
                elapsed_ms = int((time.perf_counter() - start) * 1000)

            if not resp.is_success:
                error = _map_http_error(resp.status_code)
                try:
                    err_body = resp.json()
                    _debug(f"<- {resp.status_code}", err_body)
                    if "detail" in err_body:
                        d = err_body["detail"]
                        detail = d if isinstance(d, str) else str(d)
                        error = f"{error}: {detail}"
                except Exception:
                    pass
                return ApiResult(status="error", data=None, error=error, elapsed_ms=elapsed_ms)

            data = resp.json()
            _debug(f"<- {resp.status_code} ({elapsed_ms}ms)", data)
            return ApiResult(status="success", data=data, elapsed_ms=elapsed_ms)

        except httpx.TimeoutException:
            return ApiResult(status="error", data=None, error="Request timed out", elapsed_ms=0)
        except Exception as e:
            return ApiResult(status="error", data=None, error=str(e), elapsed_ms=0)

    async def _get[T](self, path: str, response_type: type[T], params: dict | None = None) -> ApiResult[T]:
        return await self._request("GET", path, response_type, params=params)

    async def _post[T](self, path: str, body: BaseModel, response_type: type[T]) -> ApiResult[T]:
        return await self._request("POST", path, response_type, body=body)

    async def _post_empty[T](self, path: str, response_type: type[T] = dict) -> ApiResult[T]:
        return await self._request("POST", path, response_type)

    async def _patch[T](self, path: str, body: BaseModel, response_type: type[T]) -> ApiResult[T]:
        return await self._request("PATCH", path, response_type, body=body)

    async def _delete(self, path: str) -> ApiResult[dict]:
        return await self._request("DELETE", path, dict)

    async def scrape(self, params: ScrapeRequest) -> ApiResult[ApiScrapeResponse]:
        return await self._post("/scrape", params, ApiScrapeResponse)

    async def extract(self, params: ExtractRequest) -> ApiResult[ApiExtractResponse]:
        return await self._post("/extract", params, ApiExtractResponse)

    async def search(self, params: SearchRequest) -> ApiResult[ApiSearchResponse]:
        return await self._post("/search", params, ApiSearchResponse)

    async def credits(self) -> ApiResult[ApiCreditsResponse]:
        return await self._get("/credits", ApiCreditsResponse)

    async def health(self) -> ApiResult[ApiHealthResponse]:
        return await self._request("GET", "/healthz", ApiHealthResponse, base_url=env.health_url)

    async def close(self) -> None:
        await self._http.aclose()

    async def __aenter__(self) -> AsyncScrapeGraphAI:
        return self

    async def __aexit__(self, *args) -> None:
        await self.close()

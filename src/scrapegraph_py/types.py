from __future__ import annotations
from typing import Generic, TypeVar, Literal
from pydantic import BaseModel

T = TypeVar("T")


class ApiResult(BaseModel, Generic[T]):
    status: Literal["success", "error"]
    data: T | None
    error: str | None = None
    elapsed_ms: int


class ApiTokenUsage(BaseModel):
    prompt_tokens: int
    completion_tokens: int


class ApiChunkerMetadata(BaseModel):
    chunks: list[dict[str, int]]


class ApiFetchWarning(BaseModel):
    reason: Literal["too_short", "empty", "bot_blocked", "spa_shell", "soft_404"]
    provider: str | None = None


class ContentPageMetadata(BaseModel):
    index: int
    images: list[dict]
    tables: list[dict]
    hyperlinks: list[str]
    dimensions: dict[str, int]


class ScrapeMetadata(BaseModel):
    provider: str | None = None
    content_type: str
    elapsed_ms: int | None = None
    warnings: list[ApiFetchWarning] | None = None
    ocr: dict | None = None


class ApiBrandingColors(BaseModel):
    primary: str
    accent: str
    background: str
    text_primary: str
    link: str


class ApiBrandingFontEntry(BaseModel):
    family: str
    fallback: str


class ApiBrandingTypography(BaseModel):
    primary: ApiBrandingFontEntry
    heading: ApiBrandingFontEntry
    mono: ApiBrandingFontEntry
    sizes: dict[str, str]


class ApiBrandingImages(BaseModel):
    logo: str
    favicon: str
    og_image: str


class ApiBrandingPersonality(BaseModel):
    tone: str
    energy: Literal["high", "medium", "low"]
    target_audience: str


class ApiBranding(BaseModel):
    color_scheme: Literal["light", "dark"]
    colors: ApiBrandingColors
    typography: ApiBrandingTypography
    images: ApiBrandingImages
    spacing: dict[str, int | str]
    framework_hints: list[str]
    personality: ApiBrandingPersonality
    confidence: float


class ApiBrandingMetadata(BaseModel):
    title: str
    description: str
    favicon: str
    language: str
    theme_color: str
    og_title: str
    og_description: str
    og_image: str
    og_url: str


class ApiScrapeScreenshotData(BaseModel):
    url: str
    width: int
    height: int


class ApiScrapeFormatError(BaseModel):
    code: str
    error: str


class ApiScrapeResponse(BaseModel):
    results: dict
    metadata: ScrapeMetadata
    errors: dict | None = None


class ApiExtractResponse(BaseModel):
    raw: str | None
    json_data: dict | None = None
    usage: ApiTokenUsage
    metadata: dict

    model_config = {"populate_by_name": True, "extra": "allow"}


class ApiSearchResult(BaseModel):
    url: str
    title: str
    content: str
    provider: str | None = None


class ApiSearchMetadata(BaseModel):
    search: dict
    pages: dict
    chunker: ApiChunkerMetadata | None = None


class ApiSearchResponse(BaseModel):
    results: list[ApiSearchResult]
    json_data: dict | None = None
    raw: str | None = None
    usage: ApiTokenUsage | None = None
    metadata: ApiSearchMetadata

    model_config = {"populate_by_name": True, "extra": "allow"}


ApiCrawlStatus = Literal["running", "completed", "failed", "paused", "deleted"]
ApiCrawlPageStatus = Literal["completed", "failed", "skipped"]


class ApiCrawlPage(BaseModel):
    url: str
    status: ApiCrawlPageStatus
    depth: int
    parent_url: str | None
    links: list[str]
    scrape_ref_id: str
    title: str
    content_type: str
    screenshot_url: str | None = None
    reason: str | None = None
    error: str | None = None


class ApiCrawlResult(BaseModel):
    status: ApiCrawlStatus
    reason: str | None = None
    total: int
    finished: int
    pages: list[ApiCrawlPage]


class ApiCrawlResponse(ApiCrawlResult):
    id: str


class TextChange(BaseModel):
    type: Literal["added", "removed"]
    line: int
    content: str


class JsonChange(BaseModel):
    path: str
    old: object
    new: object


class SetChange(BaseModel):
    added: list[str]
    removed: list[str]


class ImageChange(BaseModel):
    size: int
    changed: int
    mask: str | None = None


class ApiMonitorDiffs(BaseModel):
    markdown: list[TextChange] | None = None
    html: list[TextChange] | None = None
    json_changes: list[JsonChange] | None = None
    screenshot: ImageChange | None = None
    links: SetChange | None = None
    images: SetChange | None = None
    summary: list[TextChange] | None = None
    branding: list[JsonChange] | None = None

    model_config = {"populate_by_name": True, "extra": "allow"}


class ApiWebhookStatus(BaseModel):
    sent_at: str
    status_code: int | None
    error: str | None = None


class ApiMonitorResult(BaseModel):
    changed: bool
    diffs: ApiMonitorDiffs
    refs: dict
    webhook_status: ApiWebhookStatus | None = None


class ApiMonitorResponse(BaseModel):
    cron_id: str
    schedule_id: str
    interval: str
    status: Literal["active", "paused"]
    config: dict
    created_at: str
    updated_at: str


ApiHistoryService = Literal["scrape", "extract", "search", "monitor", "crawl"]
ApiHistoryStatus = Literal["completed", "failed", "running", "paused", "deleted"]


class ApiHistoryEntry(BaseModel):
    id: str
    service: ApiHistoryService
    status: ApiHistoryStatus
    error: object | None
    elapsed_ms: int
    created_at: str
    request_parent_id: str | None
    params: dict
    result: dict


class ApiHistoryPagination(BaseModel):
    page: int
    limit: int
    total: int


class ApiHistoryPage(BaseModel):
    data: list[ApiHistoryEntry]
    pagination: ApiHistoryPagination


class ApiJobsStatus(BaseModel):
    used: int
    limit: int


class ApiCreditsJobs(BaseModel):
    crawl: ApiJobsStatus
    monitor: ApiJobsStatus


class ApiCreditsResponse(BaseModel):
    remaining: int
    used: int
    plan: str
    jobs: ApiCreditsJobs


class ApiHealthServices(BaseModel):
    redis: Literal["ok", "down"]
    db: Literal["ok", "down"]


class ApiHealthResponse(BaseModel):
    status: str
    uptime: int
    services: ApiHealthServices | None = None

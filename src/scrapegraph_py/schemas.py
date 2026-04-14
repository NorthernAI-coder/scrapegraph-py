from __future__ import annotations
from typing import Literal, Annotated
from pydantic import BaseModel, Field, HttpUrl, model_validator

ApiService = Literal["scrape", "extract", "search", "monitor", "crawl"]
ApiStatus = Literal["completed", "failed"]
ApiHtmlMode = Literal["normal", "reader", "prune"]
ApiFetchMode = Literal["auto", "fast", "js"]
ApiScrapeFormat = Literal["markdown", "html", "links", "images", "summary", "json", "branding", "screenshot"]
ApiTimeRange = Literal["past_hour", "past_24_hours", "past_week", "past_month", "past_year"]

ApiFetchContentType = Literal[
    "text/html",
    "application/pdf",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    "application/vnd.openxmlformats-officedocument.presentationml.presentation",
    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    "image/jpeg",
    "image/png",
    "image/webp",
    "image/gif",
    "image/avif",
    "image/tiff",
    "image/heic",
    "image/bmp",
    "application/epub+zip",
    "application/rtf",
    "application/vnd.oasis.opendocument.text",
    "text/csv",
    "text/plain",
    "application/x-latex",
]


class MockConfig(BaseModel):
    min_kb: int = Field(default=1, ge=1, le=1000)
    max_kb: int = Field(default=5, ge=1, le=1000)
    min_sleep: int = Field(default=5, ge=0, le=30000)
    max_sleep: int = Field(default=15, ge=0, le=30000)
    write_to_bucket: bool = False


class FetchConfig(BaseModel):
    mode: ApiFetchMode = "auto"
    stealth: bool = False
    timeout: int = Field(default=30000, ge=1000, le=60000)
    wait: int = Field(default=0, ge=0, le=30000)
    headers: dict[str, str] | None = None
    cookies: dict[str, str] | None = None
    country: Annotated[str, Field(min_length=2, max_length=2)] | None = None
    scrolls: int = Field(default=0, ge=0, le=100)
    mock: bool | MockConfig = False


class MarkdownFormatConfig(BaseModel):
    type: Literal["markdown"] = "markdown"
    mode: ApiHtmlMode = "normal"


class HtmlFormatConfig(BaseModel):
    type: Literal["html"] = "html"
    mode: ApiHtmlMode = "normal"


class ScreenshotFormatConfig(BaseModel):
    type: Literal["screenshot"] = "screenshot"
    full_page: bool = False
    width: int = Field(default=1440, ge=320, le=3840)
    height: int = Field(default=900, ge=200, le=2160)
    quality: int = Field(default=80, ge=1, le=100)


class JsonFormatConfig(BaseModel):
    type: Literal["json"] = "json"
    prompt: Annotated[str, Field(min_length=1, max_length=10000)]
    schema_: dict[str, object] | None = Field(default=None, alias="schema")
    mode: ApiHtmlMode = "normal"


class LinksFormatConfig(BaseModel):
    type: Literal["links"] = "links"


class ImagesFormatConfig(BaseModel):
    type: Literal["images"] = "images"


class SummaryFormatConfig(BaseModel):
    type: Literal["summary"] = "summary"


class BrandingFormatConfig(BaseModel):
    type: Literal["branding"] = "branding"


ScrapeFormatEntry = (
    MarkdownFormatConfig
    | HtmlFormatConfig
    | ScreenshotFormatConfig
    | JsonFormatConfig
    | LinksFormatConfig
    | ImagesFormatConfig
    | SummaryFormatConfig
    | BrandingFormatConfig
)


class ScrapeRequest(BaseModel):
    url: HttpUrl
    content_type: ApiFetchContentType | None = None
    fetch_config: FetchConfig | None = None
    formats: list[ScrapeFormatEntry] = Field(default_factory=lambda: [MarkdownFormatConfig()])

    @model_validator(mode="after")
    def validate_unique_formats(self):
        types = [f.type for f in self.formats]
        if len(types) != len(set(types)):
            raise ValueError("duplicate format types not allowed")
        return self


class ExtractRequest(BaseModel):
    url: HttpUrl | None = None
    html: str | None = None
    markdown: str | None = None
    mode: ApiHtmlMode = "normal"
    prompt: Annotated[str, Field(min_length=1, max_length=10000)]
    schema_: dict[str, object] | None = Field(default=None, alias="schema")
    content_type: ApiFetchContentType | None = None
    fetch_config: FetchConfig | None = None

    @model_validator(mode="after")
    def validate_source(self):
        if not self.url and not self.html and not self.markdown:
            raise ValueError("Either url, html, or markdown is required")
        return self


class SearchRequest(BaseModel):
    query: Annotated[str, Field(min_length=1, max_length=500)]
    num_results: int = Field(default=3, ge=1, le=20)
    format: Literal["html", "markdown"] = "markdown"
    mode: ApiHtmlMode = "prune"
    fetch_config: FetchConfig | None = None
    prompt: Annotated[str, Field(min_length=1, max_length=10000)] | None = None
    schema_: dict[str, object] | None = Field(default=None, alias="schema")
    location_geo_code: Annotated[str, Field(max_length=10)] | None = None
    time_range: ApiTimeRange | None = None

    @model_validator(mode="after")
    def validate_schema_requires_prompt(self):
        if self.schema_ and not self.prompt:
            raise ValueError("schema requires prompt")
        return self


class MonitorCreateRequest(BaseModel):
    url: HttpUrl
    name: Annotated[str, Field(max_length=200)] | None = None
    formats: list[ScrapeFormatEntry] = Field(default_factory=lambda: [MarkdownFormatConfig()])
    webhook_url: HttpUrl | None = None
    interval: Annotated[str, Field(min_length=1, max_length=100)]
    fetch_config: FetchConfig | None = None

    @model_validator(mode="after")
    def validate_unique_formats(self):
        types = [f.type for f in self.formats]
        if len(types) != len(set(types)):
            raise ValueError("duplicate format types not allowed")
        return self


class MonitorUpdateRequest(BaseModel):
    name: Annotated[str, Field(max_length=200)] | None = None
    formats: list[ScrapeFormatEntry] | None = None
    webhook_url: HttpUrl | None = None
    interval: Annotated[str, Field(min_length=1, max_length=100)] | None = None
    fetch_config: FetchConfig | None = None

    @model_validator(mode="after")
    def validate_unique_formats(self):
        if self.formats:
            types = [f.type for f in self.formats]
            if len(types) != len(set(types)):
                raise ValueError("duplicate format types not allowed")
        return self


class CrawlRequest(BaseModel):
    url: HttpUrl
    formats: list[ScrapeFormatEntry] = Field(default_factory=lambda: [MarkdownFormatConfig()])
    max_depth: int = Field(default=2, ge=0)
    max_pages: int = Field(default=50, ge=1, le=1000)
    max_links_per_page: int = Field(default=10, ge=1)
    allow_external: bool = False
    include_patterns: list[str] | None = None
    exclude_patterns: list[str] | None = None
    content_types: list[ApiFetchContentType] | None = None
    fetch_config: FetchConfig | None = None

    @model_validator(mode="after")
    def validate_unique_formats(self):
        types = [f.type for f in self.formats]
        if len(types) != len(set(types)):
            raise ValueError("duplicate format types not allowed")
        return self


class HistoryFilter(BaseModel):
    page: int = Field(default=1, ge=1)
    limit: int = Field(default=20, ge=1, le=100)
    service: ApiService | None = None

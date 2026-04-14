from __future__ import annotations
import os


class Env:
    @property
    def debug(self) -> bool:
        return os.environ.get("SGAI_DEBUG") == "1"

    @property
    def timeout(self) -> int:
        val = os.environ.get("SGAI_TIMEOUT_S")
        return int(val) if val else 120

    @property
    def base_url(self) -> str:
        return os.environ.get("SGAI_API_URL") or "https://api.scrapegraphai.com/v2"

    @property
    def health_url(self) -> str:
        custom = os.environ.get("SGAI_API_URL")
        if custom:
            import re
            return re.sub(r"/v\d+$", "", custom)
        return "https://api.scrapegraphai.com"


env = Env()

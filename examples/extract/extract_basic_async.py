import asyncio
import json
from scrapegraph_py import AsyncScrapeGraphAI, ExtractRequest

async def main():
    async with AsyncScrapeGraphAI() as sgai:
        res = await sgai.extract(ExtractRequest(
            url="https://example.com",
            prompt="What is this page about? Extract the main heading and description.",
        ))

        if res.status == "success":
            print("Extracted:", json.dumps(res.data.get("json"), indent=2))
            print("\nTokens used:", res.data.get("usage"))
        else:
            print("Failed:", res.error)

asyncio.run(main())

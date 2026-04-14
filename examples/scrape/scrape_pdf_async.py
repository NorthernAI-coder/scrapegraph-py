import asyncio
from scrapegraph_py import AsyncScrapeGraphAI, ScrapeRequest, MarkdownFormatConfig

async def main():
    async with AsyncScrapeGraphAI() as sgai:
        res = await sgai.scrape(ScrapeRequest(
            url="https://www.w3.org/WAI/WCAG21/Techniques/pdf/img/table-word.pdf",
            content_type="application/pdf",
            formats=[MarkdownFormatConfig()],
        ))

        if res.status == "success":
            print("Markdown:", res.data.results.get("markdown", {}).get("data"))
            print(f"\nTook {res.elapsed_ms}ms")
        else:
            print("Failed:", res.error)

asyncio.run(main())

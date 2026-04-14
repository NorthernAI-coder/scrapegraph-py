import asyncio
from scrapegraph_py import AsyncScrapeGraphAI, CrawlRequest

async def main():
    async with AsyncScrapeGraphAI() as sgai:
        start_res = await sgai.crawl.start(CrawlRequest(
            url="https://example.com",
            max_pages=5,
            max_depth=2,
        ))

        if start_res.status != "success" or not start_res.data:
            print("Failed to start:", start_res.error)
        else:
            print("Crawl started:", start_res.data["id"])
            print("Status:", start_res.data["status"])

            get_res = await sgai.crawl.get(start_res.data["id"])
            if get_res.status == "success":
                print("\nProgress:", get_res.data["finished"], "/", get_res.data["total"])
                print("Pages:", [p["url"] for p in get_res.data.get("pages", [])])

asyncio.run(main())

import asyncio
from scrapegraph_py import AsyncScrapeGraphAI

async def main():
    async with AsyncScrapeGraphAI() as sgai:
        res = await sgai.credits()

        if res.status == "success":
            data = res.data
            print("Plan:", data["plan"])
            print("Remaining credits:", data["remaining"])
            print("Used credits:", data["used"])
            print("\nJob limits:")
            print("  Crawl:", data["jobs"]["crawl"]["used"], "/", data["jobs"]["crawl"]["limit"])
            print("  Monitor:", data["jobs"]["monitor"]["used"], "/", data["jobs"]["monitor"]["limit"])
        else:
            print("Failed:", res.error)

asyncio.run(main())

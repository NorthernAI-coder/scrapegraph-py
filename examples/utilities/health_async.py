import asyncio
from scrapegraph_py import AsyncScrapeGraphAI

async def main():
    async with AsyncScrapeGraphAI() as sgai:
        res = await sgai.health()

        if res.status == "success":
            data = res.data
            print("Status:", data["status"])
            print("Uptime:", data["uptime"], "seconds")
            if data.get("services"):
                print("Services:")
                print("  Redis:", data["services"]["redis"])
                print("  DB:", data["services"]["db"])
        else:
            print("Failed:", res.error)

asyncio.run(main())

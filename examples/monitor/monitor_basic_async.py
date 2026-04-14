import asyncio
from scrapegraph_py import AsyncScrapeGraphAI, MonitorCreateRequest, MarkdownFormatConfig

async def main():
    async with AsyncScrapeGraphAI() as sgai:
        res = await sgai.monitor.create(MonitorCreateRequest(
            url="https://example.com",
            name="Example Monitor",
            interval="0 * * * *",
            formats=[MarkdownFormatConfig()],
        ))

        if res.status == "success":
            print("Monitor created:", res.data.cron_id)
            print("Status:", res.data.status)
            print("Interval:", res.data.interval)
        else:
            print("Failed:", res.error)

asyncio.run(main())

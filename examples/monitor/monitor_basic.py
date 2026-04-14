from scrapegraph_py import ScrapeGraphAI, MonitorCreateRequest, MarkdownFormatConfig

sgai = ScrapeGraphAI()

res = sgai.monitor.create(MonitorCreateRequest(
    url="https://example.com",
    name="Example Monitor",
    interval="0 * * * *",
    formats=[MarkdownFormatConfig()],
))

if res.status == "success":
    print("Monitor created:", res.data["cronId"])
    print("Status:", res.data["status"])
    print("Interval:", res.data["interval"])
else:
    print("Failed:", res.error)

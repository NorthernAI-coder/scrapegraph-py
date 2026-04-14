from scrapegraph_py import ScrapeGraphAI, MonitorCreateRequest, MarkdownFormatConfig

sgai = ScrapeGraphAI()

res = sgai.monitor.create(MonitorCreateRequest(
    url="https://example.com",
    name="Example Monitor with Webhook",
    interval="0 */6 * * *",
    webhook_url="https://your-webhook-endpoint.com/hook",
    formats=[MarkdownFormatConfig()],
))

if res.status == "success":
    print("Monitor created:", res.data["cronId"])
    print("Status:", res.data["status"])
    print("Interval:", res.data["interval"])
    print("Webhook configured")
else:
    print("Failed:", res.error)

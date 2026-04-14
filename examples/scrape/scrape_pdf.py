from scrapegraph_py import ScrapeGraphAI, ScrapeRequest, MarkdownFormatConfig

sgai = ScrapeGraphAI()

res = sgai.scrape(ScrapeRequest(
    url="https://www.w3.org/WAI/WCAG21/Techniques/pdf/img/table-word.pdf",
    content_type="application/pdf",
    formats=[MarkdownFormatConfig()],
))

if res.status == "success":
    print("Markdown:", res.data.results.get("markdown", {}).get("data"))
    print(f"\nTook {res.elapsed_ms}ms")
else:
    print("Failed:", res.error)

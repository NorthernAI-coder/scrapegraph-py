from scrapegraph_py import (
    ScrapeGraphAI,
    CrawlRequest,
    MarkdownFormatConfig,
    LinksFormatConfig,
)

sgai = ScrapeGraphAI()

start_res = sgai.crawl.start(CrawlRequest(
    url="https://example.com",
    max_pages=3,
    max_depth=1,
    formats=[
        MarkdownFormatConfig(),
        LinksFormatConfig(),
    ],
))

if start_res.status != "success" or not start_res.data:
    print("Failed to start:", start_res.error)
else:
    crawl_id = start_res.data.id
    print("Crawl started:", crawl_id)
    print("Status:", start_res.data.status)

    get_res = sgai.crawl.get(crawl_id)
    if get_res.status == "success":
        print("\nProgress:", get_res.data.finished, "/", get_res.data.total)

        for page in get_res.data.get("pages", []):
            print(f"\n  Page: {page['url']}")
            print(f"  Status: {page['status']}")
            print(f"  Depth: {page['depth']}")

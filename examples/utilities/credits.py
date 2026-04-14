from scrapegraph_py import ScrapeGraphAI

sgai = ScrapeGraphAI()

res = sgai.credits()

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

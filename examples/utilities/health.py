from scrapegraph_py import ScrapeGraphAI

sgai = ScrapeGraphAI()

res = sgai.health()

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

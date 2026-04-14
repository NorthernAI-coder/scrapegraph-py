import json
from scrapegraph_py import ScrapeGraphAI, ExtractRequest

sgai = ScrapeGraphAI()

res = sgai.extract(ExtractRequest(
    url="https://example.com",
    prompt="What is this page about? Extract the main heading and description.",
))

if res.status == "success":
    print("Extracted:", json.dumps(res.data.get("json"), indent=2))
    print("\nTokens used:", res.data.get("usage"))
else:
    print("Failed:", res.error)

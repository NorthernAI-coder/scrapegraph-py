from scrapegraph_py import ScrapeGraphAI, HistoryFilter

sgai = ScrapeGraphAI()

res = sgai.history.list(HistoryFilter(limit=5))

if res.status == "success":
    data = res.data
    print(f"Total: {data['pagination']['total']}")
    print(f"Page: {data['pagination']['page']} / {(data['pagination']['total'] // data['pagination']['limit']) + 1}")

    for entry in data["data"]:
        print(f"\n  ID: {entry['id']}")
        print(f"  Service: {entry['service']}")
        print(f"  Status: {entry['status']}")
        print(f"  Created: {entry['createdAt']}")
        print(f"  Elapsed: {entry['elapsedMs']}ms")
else:
    print("Failed:", res.error)

import os, json
from datetime import datetime
from dotenv import load_dotenv
from spidra import Spidra, ScrapeParams, ScrapeUrl

load_dotenv()
client = Spidra(api_key=os.environ["SPIDRA_API_KEY"])

schema = {
    "type": "object",
    "properties": {
        "plans": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "name": {"type": "string"},
                    "price_naira": {"type": "number"},
                    "trial_offer": {"type": ["string", "null"]},
                    "max_accounts": {"type": "integer"},
                    "features": {"type": "array", "items": {"type": "string"}},
                },
                "required": ["name", "price_naira", "trial_offer", "max_accounts", "features"],
            },
        }
    },
    "required": ["plans"],
}

result = client.scrape(ScrapeParams(
    urls=[ScrapeUrl(url="https://www.spotify.com/ng/premium/#plans")],
    prompt="Extract every Premium plan. Give the monthly price in naira as a plain number. "
           "Put any free trial offer in trial_offer, or null if there is none.",
    output="json",
    schema=schema,
))

data = result.content
for plan in data["plans"]:
    plan["features"] = sorted(plan["features"])
data["plans"].sort(key=lambda p: p["name"])

snapshot = {"scraped_at": datetime.now().isoformat(), "data": data}

with open("snapshot_before.json", "w", encoding="utf-8") as f:
    json.dump(snapshot, f, indent=2, ensure_ascii=False)

print(json.dumps(snapshot, indent=2, ensure_ascii=False))
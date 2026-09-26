import os, json, requests
from dotenv import load_dotenv

load_dotenv()

before = json.load(open("snapshot_before.json", encoding="utf-8"))["data"]
after = json.load(open("snapshot_after.json", encoding="utf-8"))["data"]

if before == after:
    print("No change detected. Skipping Jev.")
    raise SystemExit

state = (f"BEFORE:\n{json.dumps(before, ensure_ascii=False)}\n\n"
         f"AFTER:\n{json.dumps(after, ensure_ascii=False)}")

def noul(q):
    return {"type": "noul", "instructions": q}

questions = {
    "price_changed": noul("Did the price of any plan change?"),
    "accounts_changed": noul("Did the number of accounts on any plan change?"),
    "features_changed": noul("Were any features added to or removed from any plan?"),
    "worse_for_customer": noul("Overall, is this change worse for customers than before?"),
    "action": {
        "type": "choice",
        "instructions": "What should a competitor-monitoring system do with this change?",
        "criteria": {
            "alert_now": "Significant change the team should see today",
            "log_only": "Minor change worth recording but not alerting on",
            "ignore": "Noise with no business meaning",
        },
    },
}

resp = requests.post(
    "https://openrouter.ai/api/alpha/decisions",
    headers={"Authorization": f"Bearer {os.environ['OPENROUTER_API_KEY']}"},
    json={"model": "typesafe/jev-1.13", "state": state, "questions": questions},
).json()

answers = resp["answers"]

def band(p):
    return "yes" if p >= 0.8 else "no" if p <= 0.3 else "REVIEW"

for key in ["price_changed", "accounts_changed", "features_changed", "worse_for_customer"]:
    p = answers[key]["noul"]
    print(f"{key:20} {p:.2f}  -> {band(p)}")

action = answers["action"]
route = action["choice"] if action["confidence"] >= 0.8 else "human_review"
print(f"\naction: {action['choice']} (confidence {action['confidence']}) -> {route}")
print("probabilities:", action["probabilities"])
print(f"cost: ${resp['usage']['cost']:.7f}")
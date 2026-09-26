# Pricing page monitor with Spidra and Jev

A small Python monitor that watches a pricing page and decides whether a change is worth your attention.

It scrapes Spotify's Nigeria Premium plans page into structured JSON with [Spidra](https://spidra.io), compares the result with an earlier snapshot, and asks [Jev](https://typesafe.ai) (through OpenRouter) a set of typed questions about what changed. Jev returns probabilities, and the script turns them into a route: alert now, log only, or send to a person for review.

This repo accompanies the article [Using Jev to decide which scraped changes are worth your attention](LINK).

## How it works

1. **`scrape.py`** sends Spidra the page URL, a plain-language prompt, and a JSON schema. It sorts the plans and features so the same page always produces the same snapshot, then saves the result to `snapshot_before.json`.
2. **`monitor.py`** loads `snapshot_before.json` and `snapshot_after.json`. If they match, it stops without calling Jev. If they differ, it asks Jev:
   - Did the price of any plan change?
   - Did the number of accounts on any plan change?
   - Were any features added or removed?
   - Is the change worse for customers?
   - Should the team be alerted, should it be logged, or should it be ignored?

   Each yes or no answer comes back as a probability from 0 to 1. The script counts 0.8 or above as yes, 0.3 or below as no, and anything in between as needing review. The final action is only taken when Jev's confidence is 0.8 or above. Otherwise, the change goes to a person.

## Setup

You need Python 3.10 or above, a [Spidra](https://app.spidra.io) API key, and an [OpenRouter](https://openrouter.ai) API key with a small amount of credit.

```bash
git clone https://github.com/Bennykillua/Jev_spidra_price_monitoring.git
cd Jev_spidra_price_monitoring
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
```

Add your keys to `.env`:

```
OPENROUTER_API_KEY=sk-or-...
SPIDRA_API_KEY=spd_...
```

On macOS with Homebrew Python, installing packages outside a virtual environment fails with an `externally-managed-environment` error, so keep the virtual environment active.

## Run it

**Try the monitor without scraping.** The `examples` folder has a before snapshot and an after snapshot where one feature was added to the Duo plan:

```bash
cp examples/snapshot_before.json examples/snapshot_after.json .
python monitor.py
```

You should see output like this:

```
price_changed        0.02  -> no
accounts_changed     0.02  -> no
features_changed     0.98  -> yes
worse_for_customer   0.12  -> no

action: alert_now (confidence 0.56) -> human_review
probabilities: {'alert_now': 0.71, 'log_only': 0.29, 'ignore': 0}
cost: $0.0000485
```

Jev's numbers can vary slightly between runs.

**Scrape the live page.** This overwrites `snapshot_before.json` with a fresh scrape:

```bash
python scrape.py
```

To test a change, copy it to `snapshot_after.json`, edit a plan, and run `python monitor.py`.

## Cost

- **Jev:** about $0.00005 per check. Nothing on days when the page
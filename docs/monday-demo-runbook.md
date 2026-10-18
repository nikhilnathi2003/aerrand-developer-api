# Monday demo runbook (step by step)

Everything is installed and ready. You only run two commands.

## Before the meeting (do this once, as a dry run)

1. Open the **Terminal** app (press Cmd+Space, type "Terminal", Enter).
2. Copy-paste this line and press Enter (it moves into the project):
   ```bash
   cd ~/Documents/Startup/aerrand-developer-api
   ```
3. Start the server — copy-paste and press Enter:
   ```bash
   ./scripts/start-local.sh
   ```
   Wait until it says **"API running at http://127.0.0.1:8000"**. Leave this window open.
4. Open a **second** Terminal tab (Cmd+T). Paste these two lines:
   ```bash
   cd ~/Documents/Startup/aerrand-developer-api
   ./scripts/demo.sh
   ```
   You'll see the whole flow print out. If it works in the dry run, it'll work live.

To stop the server afterward: click the first terminal window and press **Ctrl+C**.

## During the meeting

- Share your screen with the **second** terminal visible.
- Run `./scripts/demo.sh` and talk through each numbered section as it appears.

## What each step shows (what to say)

1. **Issue a test API key** — "A partner gets an API key, created by command. We store only a
   one-way hash of it, so even a database leak can't reveal the key."
2. **POST /v1/quotes** — "They ask for a price. The **server** calculates it — the caller can
   never send their own price. Here's the full breakdown."
3. **POST /v1/errands** — "They create the delivery using that quote. It comes back as a
   correctly-priced **test-mode** errand with its own id and handover code."
4. **GET /v1/errands/{id}** — "They can fetch it back any time."
5. **Safety rails** — "No API key → 401. Trying to create without a server quote → 400. And one
   business can never read another business's errand → 404. These are the real-API safety rails."

If asked about the distance number: "We use a distance estimate (no Google Maps key yet), so the
distance charge is close to — not identical to — Aerrand's. The pricing structure and everything
else matches their API contract."

## If something goes wrong

- "command not found" → make sure you ran the `cd ~/Documents/...` line first.
- Server won't start / port busy → in the server terminal press Ctrl+C, then run
  `./scripts/start-local.sh` again.
- Anything else → screenshot it; it's fixable.

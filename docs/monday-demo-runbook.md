# Monday demo runbook (step by step)

Everything is installed and ready. The demo is a **web page** you click through.

## Before the meeting (do this once as a dry run)

1. Open the **Terminal** app (Cmd+Space → type "Terminal" → Enter).
2. Paste this and press Enter (moves into the project):
   ```bash
   cd ~/Documents/Startup/aerrand-developer-api
   ```
3. Start the server — paste and press Enter:
   ```bash
   ./scripts/start-local.sh
   ```
   Wait until it says **"API running at http://127.0.0.1:8000"**. Leave this window open.
4. Open your browser and go to: **http://127.0.0.1:8000/**
   You'll see the **Aerrand Developer API** dashboard.

To stop the server afterwards: click the Terminal window and press **Ctrl+C**.

## During the meeting

Share your screen showing the browser page, and click through the three steps top to bottom.
Say roughly this as you click:

1. **Generate test key** — "A partner gets an API key to authenticate. We store only a one-way
   hash of it, so even a database leak can't reveal the key, and we can revoke it instantly."
2. **Get quote** — "They ask for a price. The **server** calculates it — the caller can never
   send its own price. Here's the full breakdown and the total, tax in."
3. **Create delivery** — "They book it using that quote. It comes back as a correctly-priced
   **test-mode** delivery with its own id and a handover code."
4. **Your deliveries / Refresh** — "They can see their deliveries. And only *this* business can —
   one business can never see another's (tenant isolation)."

That's the Milestone-2 story: a valid test key creates a correctly-priced test-mode delivery, live.

## If asked
- *"Is the price real?"* — "The structure matches Aerrand's pricing contract. Distance uses an
  estimate for now (no Google Maps key yet), so the distance charge is close, not identical."
- *"What's underneath?"* — "A Django API with MongoDB and Redis. The page just calls our API —
  the same API a partner's software would call."

## Backup (if the web page won't load)
Run the terminal version instead: open a second Terminal tab and run
`cd ~/Documents/Startup/aerrand-developer-api && ./scripts/demo.sh`.

## If something goes wrong
- "command not found" → make sure you ran the `cd ~/Documents/...` line first.
- Page won't load → in the server terminal press Ctrl+C, run `./scripts/start-local.sh` again,
  then refresh the browser.
- Anything else → screenshot it; it's fixable.

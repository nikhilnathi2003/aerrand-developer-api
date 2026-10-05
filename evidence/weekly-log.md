# Weekly Progress & Evidence Log — Aerrand Group-6

This is our running record of what we plan and do each week, and who did what. We update it
every week so there is clear evidence of our progress and each member's contribution. It works
alongside our GitHub issues and project board (which track the individual tasks in detail).

**Team:** Nikhil Goud Nathi (lead) · Sujith Chitram · Venkata Charan Sai Doniparthi · Sai Srinivas Uppara
**How we use it:** at the end of each week, fill in what was planned, what got done, and each
person's tasks. Link to issues/commits where useful.

---

## Week 1 — Sep 21–27, 2026

**Planned:** Attend the kickoff meeting and understand the project.

**What we did:**
- Attended the kickoff meeting with Aerrand (Sep 21).
- Received the project overview and the technical requirements document.
- Asked our first round of questions (mock data vs real system, wallet, API keys, database).

**Individual:**
- **Nikhil:** asked questions about mock data, the wallet, and how API keys are issued.
- **Sujith:** attended, took notes on the business challenge. _(add your part)_
- **Charan Sai:** attended, took notes. _(add your part)_
- **Sai Srinivas:** attended, took notes. _(add your part)_

---

## Week 2 — Sep 28–Oct 4, 2026

**Planned:** Set up the project, plan the work, and write the initial setup report.

**What we did:**
- Created the GitHub repository and project board.
- Broke the requirements into 102 tracked issues (labelled by priority, area, and phase).
- Wrote the P1 Initial Setup Report (approach, architecture, technologies, sprint plan).
- Agreed on the architecture: a separate API service, server-side pricing, webhooks via an event outbox.

**Individual:**
- **Nikhil (lead):** set up the repo, board and issues; drafted the setup report and architecture.
- **Sujith:** _(add your part — e.g. reviewed requirements for quotes/booking)_
- **Charan Sai:** _(add your part)_
- **Sai Srinivas:** _(add your part)_

---

## Week 3 — Oct 5–11, 2026  *(current)*

**Planned:** Attend the 1st open office hours; start Sprint 1 (project setup + API keys).

**What we did:**
- Attended the 1st open office hours (Oct 5) and clarified the scope:
  - API keys issued by a command, kept read-only, expiry set per client.
  - Sample data provided by Johnpaul — use that.
  - Support scheduled deliveries (not just immediate).
  - If the wallet is low, the booking is cancelled.
  - Partners track deliveries from their dashboard.
  - No cancellation after the driver picks up; otherwise a cancellation fee applies.
- Started building (Sprint 1).

**Individual tasks this week:**
- **Nikhil:** set up the project (Docker, structure, health check) and start the API key system.
- **Sujith:** start the price-quote feature using the sample data.
- **Charan Sai:** start the simple wallet (charge on booking, cancel if funds are low).
- **Sai Srinivas:** start delivery tracking and the cancellation rules.

---

## Template — copy this for each new week

```
## Week N — <start date>–<end date>, 2026

**Planned:** <goal/schedule for the week>

**What we did:**
- <item>  (link issue/commit)

**Individual tasks:**
- Nikhil: <task>
- Sujith: <task>
- Charan Sai: <task>
- Sai Srinivas: <task>
```

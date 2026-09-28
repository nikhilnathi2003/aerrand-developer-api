# GitHub setup — how this repo & board are organised

This is a **group project**, so ownership lives in a GitHub **Organization**, not one
person's account. That way no single member is a point of failure, everyone has equal
access, and the Project board (our PM tool) lives alongside the code.

## One-time setup (done by one person)

1. **Create a free org:** github.com → avatar → *Your organizations* → *New organization* →
   **Free** plan. Suggested name: `aerrand-business3-group6`.
2. **Create the repo in the org:** name `aerrand-developer-api`, **Private**.
   (Private because it references a real company's internal architecture.)
3. **Push this local repo** to it (see below).
4. **Create a Project** (org → *Projects* → *New project* → Board). This is the PM tool link
   we give the GA. Add fields: **Priority** (Must/Should/Could), **Pillar**, **Phase**.
5. **Add a second owner** (org → *People* → change a trusted teammate's role to *Owner*) so
   the org isn't locked to one account.

## Pushing this local repo (run once the org repo exists)

```bash
cd aerrand-developer-api
git remote add origin https://github.com/<ORG-NAME>/aerrand-developer-api.git
git push -u origin main
```

## Adding teammates & the GA (do this any time — no rush)

You do **not** need everyone's usernames up front. Add people as their handles come in:

- **Org → People → Invite member** → enter GitHub username *or* email → pick role *Member*.
- Add the **GA (Rustem Izmailov)** the same way once you have his handle/email.
- Give the Project board to the same people (Project → *Settings* → *Manage access*), or it's
  visible to all org members by default.

New members get push access immediately; nothing you've already done is affected.

## Turning requirements into the board

1. Open `docs/requirements.md`.
2. Create one **issue** per `FR-*` row (title = `FR-KEY-01: <summary>`).
3. Label: `priority:*`, `pillar:*`, `phase:*`.
4. Add issues to the Project; arrange columns per `docs/rollout-plan.md`.

_(Optional, later: these issues can be bulk-created from `requirements.md` with the `gh`
CLI once the repo is on GitHub.)_

## What to post back in MS Teams

Reply to Rustem's "GitHub and PM links" post in the **Business 3 - Group 6** channel with:

- **GitHub repo:** `https://github.com/<ORG-NAME>/aerrand-developer-api`
- **Project (PM tool):** `https://github.com/orgs/<ORG-NAME>/projects/1`

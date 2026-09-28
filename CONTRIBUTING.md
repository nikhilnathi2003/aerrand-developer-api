# How our team works

Small, boring conventions that keep a group repo from turning into chaos. Read once.

## Branches

- `main` is always in a working, reviewable state. **Never push directly to `main`.**
- One branch per issue: `feat/FR-KEY-05-hash-storage`, `docs/proposal-v2`, `fix/quote-rounding`.
- Prefix: `feat/`, `fix/`, `docs/`, `chore/`, `test/`.

## Pull requests

1. Open a PR from your branch into `main`.
2. Link the issue it closes (`Closes #12`).
3. **At least one teammate reviews** before merge.
4. Squash-merge to keep history clean. Delete the branch after merge.

## Commits

- Present tense, short: `Add ApiKey hash storage (FR-KEY-05)`.
- Reference the requirement ID when relevant.

## Issues & the board

- Every requirement in `docs/requirements.md` becomes an issue titled with its `FR-*` ID.
- Label each issue: `priority:must|should|could`, `pillar:<name>`, `phase:0..4`.
- Move cards across the Project board as you work: `Backlog → This Phase → In Progress → In Review → Done`.

## Secrets

- **Never commit real secrets.** `.env` is git-ignored. Commit `.env.example` with blank/dummy
  values only.
- Keys like `API_KEY_HASH_PEPPER` and `WEBHOOK_SECRET_ENCRYPTION_KEY` are shared out-of-band
  (not in git).

## Definition of done (per issue)

- Code + tests written; existing tests still pass.
- The requirement's acceptance behaviour (from the TRD) is met.
- PR reviewed and merged; board card moved to Done.

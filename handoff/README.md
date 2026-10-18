# Team handoff — each person's first contribution

Each teammate owns a small, real piece of the API in their area. Each piece is **two files**
(a module + its tests) that don't touch anyone else's files, so there are no conflicts.

| Person | Part | Files | Doc |
|--------|------|-------|-----|
| Nikhil | API keys + revocation | (done, already pushed) | — |
| Sujith | Scheduled deliveries | `scheduling.py` + `test_scheduling.py` | [sujith.md](sujith.md) |
| Charan Sai | Simple wallet | `wallet.py` + `test_wallet.py` | [charansai.md](charansai.md) |
| Sai Srinivas | Lifecycle + cancellation rules | `lifecycle.py` + `test_lifecycle.py` | [saisrinivas.md](saisrinivas.md) |

## How to push your part (do this once you've accepted the GitHub invite)

```bash
# 1. Get the code (first time only)
git clone https://github.com/nikhilnathi2003/aerrand-developer-api.git
cd aerrand-developer-api

# 2. Create your two files (copy the code from your doc above into them)

# 3. Make sure the tests pass
cd backend
python3.13 -m venv .venv && ./.venv/bin/pip install -r requirements.txt   # first time only
./.venv/bin/python manage.py test

# 4. Commit and push on your own branch
cd ..
git checkout -b feat/<your-part>        # e.g. feat/wallet
git add backend/apiv1/<your two files>
git commit -m "Add <your part>"
git push -u origin feat/<your-part>
```

Then open a **Pull Request** on GitHub (green "Compare & pull request" button) and merge it.
That's your contribution — a real commit under your name that you can explain.

> Read your module before you push it — it's short, and you should be able to say what it does.

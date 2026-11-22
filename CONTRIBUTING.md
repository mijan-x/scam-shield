# Team workflow (JU_Segfault)

Team: mijan-x (owner), Maverick-145, HasanAl-17. Everyone has write access.

## First time
```bash
git clone https://github.com/mijan-x/scam-shield && cd scam-shield
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000     # http://localhost:8000
```

## Who works where (hackathon day)
| Area | Folder | Owner |
|---|---|---|
| Assigned challenge 1 | `challenges/challenge-1/` | decide at 9:00 |
| Assigned challenge 2 | `challenges/challenge-2/` | decide at 9:00 |
| Scam Shield app and demo | `app/` | decide at 9:00 |

Working in separate folders means pushes rarely conflict.

## Every change
```bash
git pull --rebase            # always before you start and before you push
# ...edit...
python -m pytest -q tests    # if you touched app/
git add -A && git commit -m "Short description of what changed"
git push
```
- Push small and often (every 30 to 45 minutes). The 1:00 PM GitHub deadline counts only what is pushed.
- `main` auto-deploys to https://scam-shield-two-topaz.vercel.app, so do not push broken code to `app/`. For risky app changes use a branch: `git switch -c my-change`, push it, open a pull request.
- If `git pull --rebase` reports a conflict: fix the marked files, `git add` them, `git rebase --continue`. Ask before using `--force`.
- Never commit API keys or `.env`.

## Each challenge folder needs
A `README.md` with: the task, how to run it, and any AI tools or libraries used (contest rule).

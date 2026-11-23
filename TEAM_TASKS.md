# Team tasks before the final (24 Nov)

Each task is real work that improves Scam Shield. Do it from **your own GitHub account** so the
contribution is yours: `git pull --rebase`, make the change, run `python -m pytest -q tests`, commit, push.
Tick the box in this file in the same commit.

## Everyone (5 minutes)
- [ ] mijan-x: write your own line in the **Team** table in `README.md` (name and what you did).
- [ ] Maverick-145: write your own line in the **Team** table in `README.md`.
- [ ] HasanAl-17: write your own line in the **Team** table in `README.md`.

## Maverick-145 (Antu Dev Nath): detection data and patterns
- [ ] **New unseen test messages.** Add 10 scam and 10 genuine messages you have really seen or heard of
      (Bangla, Banglish, English) to `app/data/messages.csv` with split `holdout2`. Do not change any
      pattern first. Then run `python eval/run_eval.py` and paste the result into the pull request or commit message.
      Note: `run_eval.py` reports the `dev` and `holdout` splits only, so add `holdout2` to its split list, or
      the new rows will not be counted.
- [ ] **One new scam pattern** that the new messages miss (for example SIM-replacement or fake agent
      cash-out reversal). Add it to `app/library.py` with English and Bangla texts, plus a test in
      `tests/test_app.py`. `tests/test_offline_parity.py` must still pass.

## HasanAl-17 (Md. Hasan ahmed): real receipts and the trainer
- [ ] **Real receipt test log.** Run 5 genuine bKash/Nagad receipts from team phones (and 2 copies you edit
      yourself) through Payment proof on the live site. Record each result in `docs/receipt-tests.md`
      (stamp, any wrong warnings). Do not commit the screenshots or anyone's full phone number.
- [ ] **A fourth trainer scenario** (for example "fake job registration fee" or "parcel stuck at customs")
      in `app/scenarios.py`: 3 steps, 3 choices each, English and Bangla, same format as the others.

## mijan-x: demo and submission
- [ ] Rehearse the demo from the demo doc three times; fix anything that feels slow.
- [ ] Make the repository public before 9:00 AM on 24 Nov.
- [ ] On the day: create `challenges/<name>/` folders for the assigned challenges, each with a README.

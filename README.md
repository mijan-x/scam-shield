# Mobile Money Scam Shield
Team **JU_Segfault** (Jahangirnagar University) · CoU AI Hackathon 2026

Three tools for Bangladesh's mobile-money users, in Bangla and English:

1. **Payment Proof Check** (for sellers). Upload a buyer's payment screenshot plus what you expected (amount, your number, chat time, order reference). The app reads the screenshot with a vision model and compares it with your expectations: amount, recipient, time, transaction-ID format, TrxID reuse across orders, and signs of editing. Verdicts are *consistent / suspicious / likely fake*. It never says "safe": the final check is always the seller's own bKash/Nagad app.
2. **Check Before You Pay.** Paste a message or describe a call. A transparent rule library (Bangla, English, Banglish) flags PIN/OTP requests, wrong-number refunds, fake KYC, prize/job/investment scams, remote-access apps, parcel fees and more. An LLM, if enabled, adds reasoning but can never lower a risk the rules found. Voice input uses the browser's Web Speech API (Chrome/Edge, needs internet).
3. **Scam Trainer.** Three scripted scenarios (refund trick, fake care agent, fake payment proof), each with 3 steps and feedback. Works offline. With an API key there is also a free-chat mode where the AI plays the scammer and grades you.

## Run
```
python -m venv .venv && source .venv/bin/activate      # Windows: .venv\Scripts\activate
pip install -r requirements.txt
export GEMINI_API_KEY=...        # optional, free tier at aistudio.google.com (or ANTHROPIC_API_KEY)
                                 # Windows: set GEMINI_API_KEY=...
uvicorn app.main:app --port 8000
```
Open http://localhost:8000. AI provider: `GEMINI_API_KEY` (model from `GEMINI_MODEL`, default `gemini-3.5-flash-lite`) or `ANTHROPIC_API_KEY`; Gemini wins if both are set. Without a key it runs in **rules mode** (pre-transaction check and scripted trainer work; screenshot reading needs the key or manual fields). `MOCK_LLM=1` gives canned AI replies for UI testing.

## Test and evaluate
```
python -m pytest -q tests
python eval/run_eval.py          # rules only
python eval/run_eval.py --ai     # rules + AI (needs a key)
```
`app/data/messages.csv` holds 60 messages we wrote ourselves (Bangla, English, Banglish; scam and genuine). This is a **small, self-written set**, so treat the numbers as a sanity check, not a benchmark. Patterns were tuned on the `dev` rows. The `holdout` rows were written afterwards; 2 holdout misses were then fixed and moved to `dev`, and 6 fresh holdout rows were added, so only those 6 are truly unseen.

## Limits (be upfront with judges)
- The screenshot check finds inconsistencies; it cannot prove a payment is real. Edited-image detection is the vision model's judgement, not forensics.
- TrxID reuse is tracked in server memory only (resets on restart).
- Rules cover known patterns; new scam wording needs new patterns. Bangla coverage is hand-written, not exhaustive.
- No real transaction data, no integration with bKash/Nagad.

## Credits (fill in before submitting)
- Code written by the team with **Claude (Anthropic) as an AI coding assistant**.
- Runtime AI: Google Gemini API (`GEMINI_MODEL`) or Anthropic Claude API (`SHIELD_MODEL`), vision + text.
- Libraries: FastAPI, Uvicorn, python-multipart, anthropic SDK, httpx, pytest.
- Scam patterns, scenarios and the evaluation set are our own work, written from public scam warnings.
- Project code started on/after 21 Nov 2026 per contest rules.

"""Precision / recall for the Pre-transaction Check.

    python eval/run_eval.py            # rules only (no key needed)
    python eval/run_eval.py --ai       # rules + AI (needs ANTHROPIC_API_KEY)

'flagged' means risk is medium or high. 'strict' means risk is high only.
The `dev` rows were used while writing the patterns. The `holdout` rows were
written afterwards and not tuned on: report those numbers, and say how small the set is.
"""
import csv
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from app import rules  # noqa: E402


def risk_of(text: str, use_ai: bool) -> str:
    if use_ai:
        from app.main import PretxIn, pretx
        return pretx(PretxIn(text=text, lang="en"))["risk"]
    return rules.analyze(text)["risk"]


def metrics(rows, threshold):
    tp = sum(1 for r in rows if r["label"] == "scam" and r["pred"] in threshold)
    fn = sum(1 for r in rows if r["label"] == "scam" and r["pred"] not in threshold)
    fp = sum(1 for r in rows if r["label"] == "genuine" and r["pred"] in threshold)
    tn = sum(1 for r in rows if r["label"] == "genuine" and r["pred"] not in threshold)
    prec = tp / (tp + fp) if tp + fp else float("nan")
    rec = tp / (tp + fn) if tp + fn else float("nan")
    fpr = fp / (fp + tn) if fp + tn else float("nan")
    return tp, fp, fn, tn, prec, rec, fpr


def main():
    use_ai = "--ai" in sys.argv
    rows = list(csv.DictReader(open(ROOT / "eval" / "messages.csv", encoding="utf-8")))
    for r in rows:
        r["pred"] = risk_of(r["text"], use_ai)
    print(f"mode: {'rules + AI' if use_ai else 'rules only'}   rows: {len(rows)}")
    for split in ("dev", "holdout"):
        part = [r for r in rows if r["split"] == split]
        n_s = sum(1 for r in part if r["label"] == "scam")
        print(f"\n== {split}: {n_s} scam, {len(part) - n_s} genuine ==")
        for name, th in (("flagged (medium+high)", {"medium", "high"}), ("strict (high only)", {"high"})):
            tp, fp, fn, tn, p, rc, fpr = metrics(part, th)
            print(f"{name:24s} TP={tp} FP={fp} FN={fn} TN={tn}  precision={p:.2f} recall={rc:.2f} false-alarm rate={fpr:.2f}")
        for r in part:
            wrong = (r["label"] == "scam" and r["pred"] == "low") or (r["label"] == "genuine" and r["pred"] != "low")
            if wrong:
                print(f"  MISS [{r['label']} -> {r['pred']}] {r['text'][:90]}")


if __name__ == "__main__":
    main()

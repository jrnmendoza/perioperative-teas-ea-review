#!/usr/bin/env python3
"""
Build the canonical dashboard QA reconciliation table (audit Section 8).

One row per (model, contributing study): analysis, outcome, timepoint,
modality, comparator, study, randomized/analysed N, the model's pooled
effect/CI/tau2/I2/p, the study's own native effect, its result-specific
RoB 2 overall judgement where one exists, and the GRADE row it feeds where
one exists. Every value is read from an existing generated artifact
(v34_data.js, the v34_reconciliation per-model CSVs, the RoB2 and GRADE
CSVs) -- nothing here is retyped or recomputed by hand, so this table can
be regenerated after any future data change and diffed against the last
version to catch drift.

Output: 09_V34_ANALYSIS/dashboard_reconciliation_table.csv
"""
from __future__ import annotations

import csv
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
V34_DATA_JS = ROOT / "dashboard" / "v34_data.js"
RECON_DIRS = [ROOT / "TEAS EA Verification" / "v34_reconciliation" / "data",
              ROOT / "09_V34_ANALYSIS" / "01_DATA"]
ROB2_P1 = ROOT / "09_V34_ANALYSIS" / "03_ROB2" / "v34_rob2_draft_assessments.csv"
ROB2_P2 = ROOT / "09_V34_ANALYSIS" / "03_ROB2" / "v34_rob2_priority2_assessments.csv"
OUTCOME_DATA = ROOT / "TEAS EA Verification" / "v34_reconciliation" / "data" / "v34_outcome_data.csv"
GRADE_NEW = ROOT / "09_V34_ANALYSIS" / "04_GRADE" / "v34_new_model_grade.csv"
OUT = ROOT / "09_V34_ANALYSIS" / "dashboard_reconciliation_table.csv"


def read_csv(p: Path) -> list[dict]:
    if not p.exists():
        return []
    with p.open(encoding="utf-8-sig") as f:
        return list(csv.DictReader(f))


def load_v34_data() -> dict:
    text = V34_DATA_JS.read_text(encoding="utf-8")
    text = text.split("window.V34_DATA = ", 1)[1].rstrip("\n; \t")
    if text.endswith(";"):
        text = text[:-1]
    return json.loads(text)


def rob2_lookup() -> dict[tuple[str, str, str], str]:
    """Result-specific RoB2, from whichever of the two tracks assessed it:
    the v34 priority-1/2 result-specific registers (this session's work),
    or the older but still result-specific 'EXISTING_LOCKED_PRIMARY' /
    'EXISTING_RESULT_SPECIFIC' status already carried per-row in the v34
    outcome data for rows the v34 worklist never needed to re-assess.
    """
    out = {}
    for row in read_csv(ROB2_P1) + read_csv(ROB2_P2):
        key = (row["study"], row["outcome"], row["timepoint"])
        out[key] = row["overall"]
    for row in read_csv(OUTCOME_DATA):
        status = (row.get("V34 RoB2 status") or "").strip()
        if status.startswith("EXISTING_LOCKED_PRIMARY:") or status.startswith("EXISTING_RESULT_SPECIFIC:"):
            key = (row["Canonical study"], row["Outcome/result"], row["Timepoint/window"])
            out.setdefault(key, status.split(":", 1)[1].strip())
    return out


def grade_lookup() -> dict[str, dict]:
    return {row["model_id"]: row for row in read_csv(GRADE_NEW)}


def main() -> int:
    data = load_v34_data()
    rob2 = rob2_lookup()
    grade = grade_lookup()

    rows = []
    for m in data["models"]:
        mid = m["model_id"]
        csv_path = next((d / f"{mid}.csv" for d in RECON_DIRS if (d / f"{mid}.csv").exists()), None)
        study_rows = read_csv(csv_path) if csv_path else []
        if not study_rows:
            rows.append(dict(
                model_id=mid, phase=m["phase"], role=m.get("role", ""),
                measure=m["measure"], model_k=m["k"], model_estimate=m["estimate"],
                model_ci_low=m["ci_low"], model_ci_high=m["ci_high"],
                model_p_value=m["p_value"], model_tau2=m.get("tau2"), model_i2=m.get("i2"),
                study="", study_outcome="", study_timepoint="", modality="", comparator="",
                n_i="", n_c="", study_n="", study_effect="", rob2_overall="MISSING_PER_MODEL_CSV",
                grade="", note=f"no per-study CSV found at {csv_path.relative_to(ROOT)}",
            ))
            continue
        g = grade.get(mid, {})
        for r in study_rows:
            n_i = float(r.get("n_i") or 0)
            n_c = float(r.get("n_c") or 0)
            key = (r["study"], r["outcome"], r.get("window", ""))
            rows.append(dict(
                model_id=mid, phase=m["phase"], role=m.get("role", ""),
                measure=m["measure"], model_k=m["k"], model_estimate=m["estimate"],
                model_ci_low=m["ci_low"], model_ci_high=m["ci_high"],
                model_p_value=m["p_value"], model_tau2=m.get("tau2"), model_i2=m.get("i2"),
                study=r["study"], study_outcome=r["outcome"], study_timepoint=r.get("window", ""),
                modality=r.get("modality", ""), comparator=r.get("comparator_type") or r.get("comparator", ""),
                n_i=r.get("n_i", ""), n_c=r.get("n_c", ""), study_n=n_i + n_c,
                study_effect=r.get("effect", ""),
                rob2_overall=rob2.get(key, "NOT_FOUND"),
                grade=g.get("grade", ""),
                note="",
            ))

    fieldnames = ["model_id", "phase", "role", "measure", "model_k", "model_estimate",
                  "model_ci_low", "model_ci_high", "model_p_value", "model_tau2", "model_i2",
                  "study", "study_outcome", "study_timepoint", "modality", "comparator",
                  "n_i", "n_c", "study_n", "study_effect", "rob2_overall", "grade", "note"]
    with OUT.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        w.writerows(rows)

    print(f"wrote {len(rows)} rows across {len(data['models'])} models -> {OUT.relative_to(ROOT)}")

    # ---- Consistency checks against the table just built ----------------
    problems = []
    by_model: dict[str, list[dict]] = {}
    for r in rows:
        by_model.setdefault(r["model_id"], []).append(r)

    for mid, rs in by_model.items():
        m = next(x for x in data["models"] if x["model_id"] == mid)
        if rs[0]["note"]:
            problems.append(f"{mid}: {rs[0]['note']}")
            continue
        n_studies = len({r["study"] for r in rs})
        if n_studies != int(m["k"]):
            problems.append(f"{mid}: model k={m['k']} but per-study CSV has {n_studies} unique studies")
        missing_rob2 = [r["study"] for r in rs if r["rob2_overall"] in ("NOT_FOUND", "")]
        if missing_rob2:
            problems.append(f"{mid}: no result-specific RoB2 match for {missing_rob2}")

    print(f"\n{len(problems)} consistency problem(s) found:")
    for p in problems:
        print(" -", p)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())

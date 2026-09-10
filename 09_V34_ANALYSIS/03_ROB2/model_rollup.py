#!/usr/bin/env python3
"""Roll the draft result-specific RoB 2 judgements up to the models they feed.

GRADE's risk-of-bias domain is judged on the studies contributing to a specific
pooled estimate, so the useful summary is per model, not per study. This reads
the model datasets directly rather than assuming which results belong where.
"""
from __future__ import annotations
import csv
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
DATA = ROOT / "TEAS EA Verification" / "v34_reconciliation" / "data"
MDIR = ROOT / "09_V34_ANALYSIS" / "01_DATA"

RANK = {"Low": 0, "Some concerns": 1, "High": 2}


def read(p):
    with p.open(encoding="utf-8-sig") as f:
        return list(csv.DictReader(f))


def norm(v):
    return " ".join((v or "").split()).strip().lower()


def main() -> int:
    draft = {(norm(r["study"]), norm(r["outcome"]), norm(r["timepoint"])): r
             for r in read(HERE / "v34_rob2_draft_assessments.csv")}
    # Keys of the 36 results this pipeline actually assessed (as opposed to the
    # ones folded in below from an earlier adjudicated record) -- used to give
    # the dashboard a result -> model membership map for filtering.
    own_keys = set(draft)

    # Results that already carry an adjudicated result-specific judgement are
    # folded in at the same level, tagged by provenance. A model's GRADE
    # risk-of-bias domain depends on every contributing result, not only on the
    # ones drafted in this pass.
    for r in read(DATA / "v34_outcome_data.csv"):
        st = (r.get("V34 RoB2 status") or "").strip()
        if not st.startswith("EXISTING") or ":" not in st:
            continue
        key = (norm(r.get("Canonical study")), norm(r.get("Outcome/result")),
               norm(r.get("Timepoint/window")))
        if key in draft:
            continue
        lvl = st.split(":", 1)[1].strip()
        if lvl in RANK:
            draft[key] = dict(study=r.get("Canonical study", ""), overall=lvl,
                              provenance="adjudicated (existing)")

    datasets = sorted(MDIR.glob("*.csv")) + sorted(DATA.glob("v34_primary_24h_mme_*.csv")) \
        + sorted(DATA.glob("v34_intraop_*.csv")) + sorted(DATA.glob("v34_qor40_*.csv")) \
        + sorted(DATA.glob("v34_gi_first_defecation_*.csv"))

    models = defaultdict(list)
    result_models = defaultdict(set)
    for ds in datasets:
        if ds.name == "v34_model_manifest.csv":
            continue
        for r in read(ds):
            mid = r.get("model") or ds.stem
            key = (norm(r.get("study")), norm(r.get("outcome")), norm(r.get("window")))
            models[mid].append((r.get("study", ""), draft.get(key)))
            if key in own_keys:
                result_models[key].add(mid)

    out = []
    for mid, contribs in sorted(models.items()):
        judged = [d for _, d in contribs if d]
        k = len({s for s, _ in contribs})
        if not judged:
            continue
        worst = max((d["overall"] for d in judged), key=lambda v: RANK[v])
        counts = {lvl: sum(1 for d in judged if d["overall"] == lvl)
                  for lvl in ("Low", "Some concerns", "High")}
        # GRADE serious-limitation signal: any High, or a majority not Low.
        if counts["High"]:
            signal = "serious limitation likely (>=1 result at High risk)"
        elif counts["Some concerns"] == len(judged):
            signal = "no serious limitation, but no result at Low risk"
        elif counts["Low"] == len(judged):
            signal = "no serious limitation"
        else:
            signal = "mixed; assessor judgement required"
        n_existing = sum(1 for d in judged if d.get("provenance"))
        out.append(dict(
            model_id=mid, k_studies=k, results_drafted=len(judged) - n_existing,
            results_adjudicated_existing=n_existing,
            results_unjudged=len(contribs) - len(judged),
            results_total=len(judged),
            low=counts["Low"], some_concerns=counts["Some concerns"], high=counts["High"],
            worst_result=worst, grade_rob_signal=signal,
            high_risk_studies="; ".join(sorted(
                {d["study"] for d in judged if d["overall"] == "High"})) or "-",
        ))

    p = HERE / "v34_rob2_model_rollup.csv"
    with p.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(out[0].keys()), lineterminator="\n")
        w.writeheader()
        w.writerows(out)

    # Result -> contributing model(s), for dashboard filtering. Every one of
    # the 36 assessed results must appear, even if (for a priority-1 row held
    # out of every dataset for some other reason) it maps to zero models.
    rm_rows = [dict(study=draft[key]["study"], outcome=draft[key]["outcome"],
                    timepoint=draft[key]["timepoint"],
                    models="; ".join(sorted(result_models.get(key, set()))))
               # sorted, not raw set order: Python randomises string hashing per
               # process, so iterating own_keys directly reshuffled all 36 rows
               # on every run and made this generated file diff against itself.
               for key in sorted(own_keys)]
    rmp = HERE / "v34_rob2_result_models.csv"
    with rmp.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["study", "outcome", "timepoint", "models"],
                           lineterminator="\n")
        w.writeheader()
        w.writerows(rm_rows)
    print(f"wrote {rmp.relative_to(ROOT)}")

    print(f"{'model':<38} {'k':>2} {'judged':>6} {'L':>3}{'S':>3}{'H':>3}  worst          signal")
    for r in out:
        print(f"  {r['model_id']:<36} {r['k_studies']:>2} {r['results_total']:>6} "
              f"{r['low']:>3}{r['some_concerns']:>3}{r['high']:>3}  {r['worst_result']:<14} "
              f"{r['grade_rob_signal']}")
        if r["high_risk_studies"] != "-":
            print(f"      high-risk contributors: {r['high_risk_studies']}")
    print(f"\nwrote {p.relative_to(ROOT)}")
    return 0


raise SystemExit(main())

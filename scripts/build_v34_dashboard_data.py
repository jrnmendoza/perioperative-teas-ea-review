#!/usr/bin/env python3
"""
Generate dashboard/v34_data.js -- the v34 analytical layer.

Everything here is derived from the v34 reconciled master, the v34 native
outcome families, and the Stata results this project fitted in
09_V34_ANALYSIS/02_STATA/30_v34_models.do. No estimate is copied from a
previous dashboard file, and none is retyped by hand.

Three things this file exists to carry:

  1. The v34 model set, stratified by modality AND comparator. The earlier
     secondary analyses pooled across strata, which the review's own protocol
     forbids; those are superseded here rather than edited in place.
  2. An explicit WITHDRAWN register. The mixed-window rescue-opioid model must
     not survive as current evidence, and a withdrawal that is invisible to the
     reader is not a withdrawal.
  3. The source holds -- unresolved conflicts, unaccessed supplements,
     graph-only rows and pending result-specific RoB -- so the dashboard can
     show why an outcome that exists in the data is still not pooled.
"""

from __future__ import annotations

import csv
import hashlib
import json
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
VER = ROOT / "TEAS EA Verification"
V34_XLSX = VER / "TEAS_EA_RECONCILED_MASTER_DATA_v34_FINAL_LOCK_READY.xlsx"
RECON = VER / "v34_reconciliation"
OUTCOME = RECON / "data" / "v34_outcome_data.csv"
CONFLICTS = RECON / "data" / "v34_source_conflicts.csv"
MODELS = ROOT / "09_V34_ANALYSIS" / "03_RESULTS" / "v34_models.csv"
MANIFEST = ROOT / "09_V34_ANALYSIS" / "01_DATA" / "v34_model_manifest.csv"
SCAN = ROOT / "09_V34_ANALYSIS" / "v34_poolable_scan.csv"
RESOLUTION = ROOT / "09_V34_ANALYSIS" / "v34_comparator_resolution.csv"
WORKLIST = ROOT / "09_V34_ANALYSIS" / "v34_rob2_worklist.csv"
ROB2_DRAFTS = ROOT / "09_V34_ANALYSIS" / "03_ROB2" / "v34_rob2_draft_assessments.csv"
ROB2_ROLLUP = ROOT / "09_V34_ANALYSIS" / "03_ROB2" / "v34_rob2_model_rollup.csv"
ROB2_RESULT_MODELS = ROOT / "09_V34_ANALYSIS" / "03_ROB2" / "v34_rob2_result_models.csv"
ROB2_PRIORITY2 = ROOT / "09_V34_ANALYSIS" / "03_ROB2" / "v34_rob2_priority2_assessments.csv"
NEW_MODEL_GRADE = ROOT / "09_V34_ANALYSIS" / "04_GRADE" / "v34_new_model_grade.csv"
OUT = ROOT / "dashboard" / "v34_data.js"

GRADE_LEVELS = ["Very Low", "Low", "Moderate", "High"]

# Re-locked 2026-09-10 after the source-verified post-lock errata in
# "TEAS EA Verification/v34_reconciliation/POST_LOCK_ERRATA_v34.md" (Yang 2024
# nausea 0-24 h added, vomiting window relabelled). Previous lock:
# 985dc26a943cf30e1bbdac552a5eb69a6fb2d73fd252d0bc194abbdb8538d6f3
V34_SHA256 = "b1bfcfb59b28f88102a443cc350b98c46eb73743e3c951fce125813cfcdff66d"

# Human labels for the models, and the RoB outcome key each belongs to.
MODEL_META = {
    "v34_primary_24h_mme_TEAS_Sham": dict(
        label="Primary 0–24 h opioid — TEAS vs sham", unit="mg IV MME",
        role="primary", rob="opioid_24h"),
    # PROSPERO's synthesis strategy: "Primary comparisons will be TEAS versus
    # credible sham TEAS and EA versus sham EA. Supportive comparisons will
    # evaluate TEAS and EA against usual care, no stimulation, or attention
    # controls." No sham-controlled EA trial reports this outcome in absolute
    # IV MME (the only EA-vs-sham/placebo opioid contrast in the dataset,
    # Sim 2002, is weight-normalised mg/kg and feeds the Tier E scale-free SMD
    # synthesis instead, not this model). This is therefore the review's
    # SUPPORTIVE EA evidence, not its EA-arm primary comparison -- there is no
    # primary EA analysis to report, and that absence must be visible rather
    # than papered over by treating the usual-care contrast as if it were one.
    "v34_primary_24h_mme_EA_Usual_care": dict(
        label="Supportive evidence — EA vs usual care (no-stimulation comparator), 0–24 h opioid",
        unit="mg IV MME", role="supporting", rob="opioid_24h"),
    "v34_primary_24h_mme_ALL_AUDIT": dict(
        label="Primary 0–24 h opioid — combined audit synthesis", unit="mg IV MME",
        role="supporting", rob="opioid_24h"),
    "v34_intraop_remifentanil_TEAS_Sham": dict(
        label="Intraoperative remifentanil — TEAS vs sham", unit="µg",
        role="secondary", rob="intraop_remi"),
    "v34_intraop_sufentanil_TEAS_Sham": dict(
        label="Intraoperative sufentanil — TEAS vs sham", unit="µg",
        role="secondary", rob="intraop_remi"),
    "v34_qor40_24h_TEAS_Sham": dict(
        label="Global QoR-40 at 24 h — TEAS vs sham", unit="QoR-40 points",
        role="secondary", rob="qor_24h"),
    "v34_gi_first_defecation_TEAS_Sham": dict(
        label="Time to first defecation — TEAS vs sham", unit="hours",
        role="secondary", rob="flatus_time"),
    "v34_gi_first_defecation_EA_Usual_care": dict(
        label="Time to first defecation — EA vs usual care", unit="hours",
        role="secondary", rob="flatus_time"),
    "gi_first_flatus_TEAS_Sham": dict(
        label="Time to first flatus — TEAS vs sham", unit="hours",
        role="secondary", rob="flatus_time"),
    "gi_first_flatus_EA_Usual_care": dict(
        label="Time to first flatus — EA vs usual care", unit="hours",
        role="secondary", rob="flatus_time"),
    "gi_first_bowel_sounds_TEAS_Sham": dict(
        label="Time to first bowel sounds — TEAS vs sham", unit="hours",
        role="secondary", rob="flatus_time"),
    "pain_vas_24h_TEAS_Sham": dict(
        label="Pain VAS at 24 h — TEAS vs sham", unit="VAS 0–10",
        role="secondary", rob="pain_rest_24h"),
    "ponv_24h_TEAS_Sham": dict(
        label="PONV incidence 0–24 h — TEAS vs sham", unit="risk ratio",
        role="secondary", rob="ponv_24h"),
}

# Analyses withdrawn by the v34 reconciliation, with the reason a reader needs.
WITHDRAWN = [
    dict(
        analysis_id="V33_RESCUE_OPIOID_RR_24H",
        label="Binary rescue opioid use, 0–24 h / POD1",
        previous="k = 3, RR 0.519 (95% CI 0.370 to 0.727), p = 0.014",
        reason=(
            "Withdrawn as an exact-window model: the three trials did not share one "
            "time window. Tu 2024 measured 6–24 h, Liu 2026 (burn) through POD1, and "
            "only Yu 2020 reported exact 0–24 h incidence. Pooling them described no "
            "single estimand."),
        now=("The exact 0–24 h set contains one trial (Yu 2020) and is not "
             "meta-analysed. The other two results remain available in their own "
             "windows."),
        affects="A secondary rescue endpoint. The strict primary opioid-dose model (k = 7) is unaffected."),
    dict(
        analysis_id="V33_QOR40_24H_MD",
        label="Global QoR-40 at ~24 h (previous mixed-window set)",
        previous="k = 3, MD +7.34 points (95% CI −4.60 to +19.28), p = 0.118",
        reason=("The previous set mixed Yu 2020's POD1 assessment with exact 24-hour "
                "assessments, and pooled across comparator strata."),
        now=("The exact 24-hour TEAS-vs-sham set is Yao 2015 and Liang 2021 (k = 2). "
             "Yu 2020's POD1 result is kept separately, and Pan 2023's usual-care "
             "result is a separate k = 1."),
        affects="Secondary quality-of-recovery endpoint."),
]

# Secondary models that were previously reported pooled across strata.
SUPERSEDED = [
    dict(old="V33_INTRAOP_REMI_MD", old_desc="k = 8, MD −116.76 µg, pooled across modality and comparator",
         new="v34_intraop_remifentanil_TEAS_Sham",
         reason="Restratified to TEAS vs sham. EA and usual-care contrasts are reported separately and single-study strata are not pooled."),
    dict(old="V33_INTRAOP_SUF_MD", old_desc="k = 5, MD −0.12 µg, pooled across modality and comparator",
         new="v34_intraop_sufentanil_TEAS_Sham",
         reason="Restratified to TEAS vs sham. Wang 2024's SNVP and MNVP are strata within one trial and are never counted as two independent RCTs."),
    dict(old="V33_GI_DEFECATION_MD", old_desc="k = 7, MD −4.80 h, pooled across modality and comparator",
         new="v34_gi_first_defecation_TEAS_Sham",
         reason="Split into TEAS vs sham (k = 3) and EA vs usual care (k = 3). Ng 2013's EA-vs-sham contrast is a separate k = 1."),
]


def read(p: Path) -> list[dict]:
    with p.open(encoding="utf-8-sig") as f:
        return list(csv.DictReader(f))


def num(v, nd=None):
    try:
        f = float(v)
    except (TypeError, ValueError):
        return None
    return round(f, nd) if nd is not None else f


def sha256(p: Path) -> str:
    h = hashlib.sha256()
    with p.open("rb") as f:
        for c in iter(lambda: f.read(1 << 20), b""):
            h.update(c)
    return h.hexdigest()


def build_grade_new_models(gs: list[dict]) -> dict:
    ratings = [
        dict(model_id=g["model_id"], outcome=g["outcome"], window=g["window"],
             modality=g["modality"], comparator=g["comparator"], measure=g["measure"],
             k=int(g["k"]), n=int(g["n"]), estimate=float(g["estimate"]),
             ci_low=float(g["ci_low"]), ci_high=float(g["ci_high"]),
             p_value=g["p_value"], i2=float(g["i2"]), grade=g["grade"],
             domains=[
                 dict(name="Risk of bias", downgrade=int(g["rob_downgrade"]), reason=g["rob_reason"]),
                 dict(name="Inconsistency", downgrade=int(g["inconsistency_downgrade"]),
                      reason=g["inconsistency_reason"]),
                 dict(name="Imprecision", downgrade=int(g["imprecision_downgrade"]),
                      reason=g["imprecision_reason"]),
                 dict(name="Indirectness", downgrade=int(g["indirectness_downgrade"]),
                      reason=g["indirectness_reason"]),
                 dict(name="Publication bias", downgrade=int(g["publication_bias_downgrade"]),
                      reason=g["publication_bias_reason"]),
             ],
             raw_downgrade_total=int(g["raw_downgrade_total"]),
             adopted_by=g["adopted_by"], adopted_date=g["adopted_date"])
        for g in gs
    ]
    dates = sorted({g["adopted_date"] for g in gs})
    grade_counts = sorted(Counter(g["grade"] for g in gs).items(),
                          key=lambda kv: GRADE_LEVELS.index(kv[0]))
    note = (
        f"GRADE certainty for these {len(gs)} v34 models, computed by applying an "
        "EXPLICIT, STATED rule per domain -- documented in "
        "09_V34_ANALYSIS/04_GRADE/compute_new_model_grade.py -- identically to "
        f"all {len(gs)}, so each downgrade can be checked and disputed individually. "
        "This is not an independent GRADE panel's consensus judgement: GRADE "
        "certainty, like RoB 2, is an assessor judgement, and Cochrane/GRADE "
        "guidance sets bands and principles rather than a formula. "
        f"Adopted by the review lead ({' and '.join(dates)}) as the review's current "
        "GRADE rating for these models -- the later date applies the identical rule "
        "to models whose RoB 2 rollup was confirmed complete after the first pass, "
        "not a methodology change -- the same adopted (not independently "
        f"panel-reviewed) status already applied to their RoB 2 domain. Ratings: "
        f"{', '.join(f'{n} {g}' for g, n in grade_counts)}. Indirectness and "
        f"publication bias were not downgraded for any of the {len(gs)}: "
        "indirectness because each model is already stratified by modality and "
        "comparator, though surgical-population variation across contributing "
        "trials is flagged as a judgement call rather than resolved; publication "
        "bias because none reaches k=10, the threshold this review has already "
        "adopted elsewhere for interpretable small-study-effect testing, and "
        "absence of a test is not evidence of absence of bias."
    )
    return dict(
        count=len(gs), status="GRADE_RULE_BASED_ADOPTED",
        adopted_by="John Ryan N. Mendoza (review lead)",
        adopted_date=" and ".join(dates),
        ratings=ratings, note=note,
    )


def main() -> int:
    got = sha256(V34_XLSX)
    if got != V34_SHA256:
        raise SystemExit(f"ABORT: v34 master hash mismatch\n  expected {V34_SHA256}\n  found    {got}")

    outcome = read(OUTCOME)
    conflicts = read(CONFLICTS)
    models = read(MODELS)
    manifest = {m["model_id"]: m for m in read(MANIFEST)}
    scan = read(SCAN) if SCAN.exists() else []

    studies = sorted({r["Canonical study"] for r in outcome if r.get("Canonical study")})
    elig = Counter((r.get("V34 eligibility") or "").strip() for r in outcome)
    robstat = Counter((r.get("V34 RoB2 status") or "").strip() for r in outcome)

    def model_row(r):
        mid = r["model_id"]
        meta = MODEL_META.get(mid, {})
        man = manifest.get(mid, {})
        est, lo, hi = num(r["estimate"], 4), num(r["ci_low"], 4), num(r["ci_high"], 4)
        row = dict(
            model_id=mid, label=meta.get("label", mid), role=meta.get("role", "secondary"),
            rob_key=meta.get("rob", ""), unit=meta.get("unit", man.get("unit", "")),
            measure=r["measure"], phase=r["phase"],
            k=int(float(r["k"])), estimate=est, ci_low=lo, ci_high=hi,
            p_value=num(r["p_value"], 5), tau2=num(r["tau2"], 4), i2=num(r["i2"], 2),
            estimator=r["estimator"],
            studies=man.get("studies", ""),
            rob2_pending=int(man["rob2_pending"]) if man.get("rob2_pending") else None,
        )
        # A log risk ratio is exponentiated for display; the model stays on the
        # log scale, and both are carried so nothing is re-derived in the page.
        if r["measure"] == "logRR" and None not in (est, lo, hi):
            import math
            row["rr"] = round(math.exp(est), 4)
            row["rr_low"] = round(math.exp(lo), 4)
            row["rr_high"] = round(math.exp(hi), 4)
        return row

    model_rows = [model_row(r) for r in models]
    new_models = [m for m in model_rows if m["phase"] == "NEW"]
    reproduced = [m for m in model_rows if m["phase"] == "REPRODUCED"]

    grade_new_models_payload = build_grade_new_models(
        read(NEW_MODEL_GRADE) if NEW_MODEL_GRADE.exists() else [])

    payload = {
        "generated_by": "scripts/build_v34_dashboard_data.py",
        "master": V34_XLSX.name,
        "master_sha256": V34_SHA256,
        "master_version": "v34",
        "canonical_studies": len(studies),
        "outcome_rows": len(outcome),
        "strict_primary_k": next(
            (m["k"] for m in model_rows if m["model_id"] == "v34_primary_24h_mme_ALL_AUDIT"), None),

        "models": model_rows,
        "new_model_count": len(new_models),
        "reproduced_model_count": len(reproduced),

        "withdrawn": WITHDRAWN,
        "superseded": SUPERSEDED,

        "eligibility_counts": dict(elig.most_common()),
        "rob2_status_counts": dict(robstat.most_common()),

        "source_holds": {
            "unresolved_conflicts": sum(
                1 for c in conflicts
                if "unresolved" in (c.get("resolution_status", "") or c.get("current_structured_choice", "")).lower()
                or not (c.get("resolution_status") or "").strip()),
            "conflict_records": len(conflicts),
            "conflicts": [
                dict(study=c.get("study", ""), outcome=c.get("outcome", ""),
                     timepoint=c.get("timepoint", ""),
                     value_a=c.get("value_A", ""), location_a=c.get("source_location_A", ""),
                     value_b=c.get("value_B", ""), location_b=c.get("source_location_B", ""),
                     choice=c.get("current_structured_choice", ""))
                for c in conflicts],
            "supplement_access_gaps": ["Zhu 2022", "Lu 2022", "Gao 2021", "Jiang 2026",
                                       "Tu 2024", "Lu 2021", "Zheng 2025"],
            "source_not_accessed_outcomes": [
                "Gao 2021 — total length of stay (Supplementary Table S4)",
                "Gao 2021 — 30-day complications (Supplementary Table S4)"],
        },

        "comparator_resolution": (lambda rs: {
            "rows_resolved": sum(1 for r in rs if r["resolved"] == "YES"),
            "rows_unresolved": sum(1 for r in rs if r["resolved"] != "YES"),
            "by_comparator": dict(Counter(r["comparator_after"] for r in rs
                                          if r["resolved"] == "YES").most_common()),
            "by_modality": dict(Counter(r["modality_after"] for r in rs
                                        if r["resolved"] == "YES").most_common()),
            "note": ("Modality and comparator classifications left as REVIEW_REQUIRED in "
                     "the v34 native data, resolved by applying the review's documented "
                     "classifier: inert-sham markers are tested before device names, real "
                     "current at a control site is Active Electrical, and an arm with no "
                     "device -- including a balanced co-intervention -- is usual care. "
                     "Where the arm text did not decide it, the study's canonical modality "
                     "from the review's own study list was used. This is classification, "
                     "not a new scientific judgement."),
        })(read(RESOLUTION) if RESOLUTION.exists() else []),

        "rob2_worklist": (lambda rs: {
            "pairs_needing_assessment": len(rs),
            "blocking_grade": sum(1 for r in rs if r["priority"].startswith("1")),
            "not_currently_pooled": sum(1 for r in rs if r["priority"].startswith("2")),
            "blocking_list": [
                dict(study=r["study"], outcome=r["outcome"], timepoint=r["timepoint"])
                for r in rs if r["priority"].startswith("1")],
            "note": ("Result-specific RoB 2 is a judgement made by assessors, not a value "
                     "derivable from the data. No study-wide judgement was copied onto a "
                     "different result. The rows below are the ones inside a fitted model. "
                     "Each carries a source-evidence-derived judgement, anchored to quoted "
                     "text, adopted by the review lead on 2026-09-08 as the review's current "
                     "result-specific RoB 2 assessment for these results."),
        })(read(WORKLIST) if WORKLIST.exists() else []),

        "rob2_results": (lambda ds, rl, rm: {
            "count": len(ds),
            "overall_counts": dict(Counter(r["overall"] for r in ds).most_common()),
            "domain_counts": {
                d: dict(Counter(r[d] for r in ds).most_common())
                for d in ("d1_randomisation", "d2_deviations", "d3_missing",
                          "d4_measurement", "d5_reporting")},
            "results": [
                dict(study=r["study"], outcome=r["outcome"], timepoint=r["timepoint"],
                     family=r["outcome_family"],
                     intervention=r["intervention"], comparator=r["comparator"],
                     d1=r["d1_randomisation"], d2=r["d2_deviations"], d3=r["d3_missing"],
                     d4=r["d4_measurement"], d5=r["d5_reporting"],
                     overall=r["overall"], rationale=r["rationale"], flags=r["flags"],
                     source_pdf=r["source_pdf"], adopted_by=r["adopted_by"],
                     adopted_date=r["adopted_date"],
                     models=rm.get((r["study"], r["outcome"], r["timepoint"]), ""))
                for r in ds],
            "model_rollup": [
                dict(model_id=r["model_id"], k=int(r["k_studies"]),
                     judged=int(r["results_total"]),
                     low=int(r["low"]), some=int(r["some_concerns"]), high=int(r["high"]),
                     worst=r["worst_result"], signal=r["grade_rob_signal"],
                     high_risk_studies=r["high_risk_studies"])
                for r in rl],
            "status": "ROB2_RESULT_SPECIFIC_ADOPTED",
            "adopted_by": "John Ryan N. Mendoza (review lead)",
            "adopted_date": "2026-09-08",
            "note": ("Each of these judgements was derived by reading the mapped source "
                     "article against the RoB 2 signalling questions, and every domain is "
                     "anchored to quoted text with a page locator in "
                     "09_V34_ANALYSIS/03_ROB2/evidence.json. They are judged per RESULT, not "
                     "per study: D4 in particular turns on who measured that specific outcome "
                     "and whether they were blinded. Adopted by the review lead on 2026-09-08 "
                     "as the review's current result-specific RoB 2 assessment. The model "
                     "rollup shows the RoB 2 composition each pooled estimate inherits from "
                     "these results."),
        })(read(ROB2_DRAFTS) if ROB2_DRAFTS.exists() else [],
           read(ROB2_ROLLUP) if ROB2_ROLLUP.exists() else [],
           {(r["study"], r["outcome"], r["timepoint"]): r["models"]
            for r in (read(ROB2_RESULT_MODELS) if ROB2_RESULT_MODELS.exists() else [])}),

        "rob2_priority2": (lambda ds: {
            "count": len(ds),
            "assessed_count": sum(1 for r in ds if r["status"] == "ROB2_RESULT_SPECIFIC_ADOPTED"),
            "unresolved_count": sum(1 for r in ds if r["status"] == "ROB2_SOURCE_MAPPING_UNRESOLVED"),
            "overall_counts": dict(Counter(r["overall"] for r in ds).most_common()),
            "domain_counts": {
                d: dict(Counter(r[d] for r in ds).most_common())
                for d in ("d1_randomisation", "d2_deviations", "d3_missing",
                          "d4_measurement", "d5_reporting")},
            "results": [
                dict(study=r["study"], outcome=r["outcome"], timepoint=r["timepoint"],
                     family=r["outcome_family"],
                     intervention=r["intervention"], comparator=r["comparator"],
                     d1=r["d1_randomisation"], d2=r["d2_deviations"], d3=r["d3_missing"],
                     d4=r["d4_measurement"], d5=r["d5_reporting"],
                     overall=r["overall"], rationale=r["rationale"], flags=r["flags"],
                     source_pdf=r["source_pdf"], status=r["status"],
                     adopted_by=r["adopted_by"], adopted_date=r["adopted_date"],
                     provenance_note=r["provenance_note"])
                for r in ds],
            "model_rollup": [],
            "status": "ROB2_RESULT_SPECIFIC_ADOPTED",
            "adopted_by": "John Ryan N. Mendoza (review lead)",
            "adopted_date": "2026-09-08",
            "note": ("These are the results NOT currently inside any fitted model -- outcomes "
                     "reported by a single trial, held for a source conflict, or otherwise not "
                     "yet pooled -- assessed for completeness of the review's result-specific "
                     "RoB 2 register, not because a synthesis depends on them today. Judged per "
                     "RESULT against the mapped source article, same method and standard as the "
                     "36 results above. Adopted by the review lead on 2026-09-08. Two studies "
                     "(Wu 2016, Ao 2021; 7 results) were initially held as "
                     "ROB2_SOURCE_MAPPING_UNRESOLVED because an automated numeric-fingerprint "
                     "check could not confirm their source PDF; a second reviewer confirmed both "
                     "sources correct on 2026-09-09 by reading the full text directly, and those "
                     "7 results were assessed and adopted that day -- see each row's own "
                     "adopted_date and provenance_note. None remain unresolved."),
        })(read(ROB2_PRIORITY2) if ROB2_PRIORITY2.exists() else []),

        "poolable_scan": {
            "groups_examined": len(scan),
            "candidates": sum(1 for r in scan if r["verdict"].startswith("CANDIDATE")),
            "shared_arm_holds": sum(1 for r in scan if r["verdict"].startswith("HOLD")),
            "single_study": sum(1 for r in scan if "only 1 independent" in r["verdict"]),
        },

        "grade_new_models": grade_new_models_payload,

        "certainty_note": (
            "New and restratified v34 analyses now carry a result-specific risk-of-bias "
            "assessment for all 36 of the results inside a fitted model, adopted by the "
            "review lead on 2026-09-08 (see rob2_results). A GRADE certainty rating for "
            f"{grade_new_models_payload['count']} v34 models has now also been computed, "
            "domain by domain, and adopted by the review lead (see grade_new_models) -- "
            "ratings: " +
            ", ".join(f"{n} {g}" for g, n in sorted(
                Counter(r["grade"] for r in grade_new_models_payload["ratings"]).items(),
                key=lambda kv: GRADE_LEVELS.index(kv[0]))) +
            ". This is a rule-based computation applied identically across every model in "
            "grade_new_models, not an independent GRADE panel's consensus judgement, and "
            "its own note says so. A model not listed in grade_new_models and not a "
            "verified byte-for-byte reproduction of an already-graded GRADE Summary-of-"
            "Findings analysis (see the dashboard's v34 model table) has contributing "
            "results still unjudged and genuinely awaits reassessment. Previous GRADE "
            "ratings describe the earlier syntheses and are not carried across to a "
            "materially changed model."),
    }

    header = f"""// v34 ANALYTICAL LAYER — generated file, do not hand-edit.
// Regenerate with:  python3 scripts/build_v34_dashboard_data.py
//
// Master : {payload['master']}
// SHA-256: {V34_SHA256}
// Studies: {payload['canonical_studies']}   Outcome rows: {payload['outcome_rows']}
// Models : {len(new_models)} new + {len(reproduced)} independently reproduced
//
// Every estimate is read from 09_V34_ANALYSIS/03_RESULTS/v34_models.csv, fitted
// by StataNow 19.5. None is copied from an earlier dashboard file.
window.V34_DATA = """

    OUT.write_text(header + json.dumps(payload, indent=2, ensure_ascii=False) + ";\n",
                   encoding="utf-8")

    print(f"wrote {OUT.relative_to(ROOT)}")
    print(f"  master ............... {payload['master']}")
    print(f"  canonical studies .... {payload['canonical_studies']}")
    print(f"  outcome rows ......... {payload['outcome_rows']}")
    print(f"  strict primary k ..... {payload['strict_primary_k']}")
    print(f"  models ............... {len(new_models)} new + {len(reproduced)} reproduced")
    print(f"  withdrawn ............ {len(WITHDRAWN)}")
    print(f"  superseded ........... {len(SUPERSEDED)}")
    print(f"  conflict records ..... {payload['source_holds']['conflict_records']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())

#!/usr/bin/env python3
"""
Derive the v33 secondary analysis datasets straight from the v33 master.

Nothing here is hand-entered: every row is selected out of v33 Outcome_Data by
explicit rule, and the rules are the whole point. The families the brief asks
about are kept apart on purpose:

  binary rescue opioid USE      is not pooled with opioid DOSE
  rescue administration COUNTS  are not pooled with dose, and not converted to it
  INTRAOPERATIVE opioid         is not pooled with POSTOPERATIVE opioid
  PCA presses                   are not pooled with drug consumption
  non-opioid rescue (NSAIDs)    is not pooled with opioid rescue

Unit harmonisation is limited to exact same-drug rescaling (mg -> ug, x1000).
No equianalgesic MME conversion is applied to any intraoperative outcome,
because the review's MME factors are defined for the postoperative estimand.

Multi-arm trials contribute exactly one contrast per model; the chosen contrast
is recorded so the choice is auditable.
"""

from __future__ import annotations

import csv
import math
import sys
from pathlib import Path

import openpyxl

ROOT = Path(__file__).resolve().parent.parent
V33 = (ROOT / "TEAS EA Verification"
       / "TEAS_EA_RECONCILED_MASTER_DATA_v33_FINAL_LOCK_READY.xlsx")
OUT = ROOT / "08_V33_MASTER" / "01_DATA"

# For multi-arm trials, the single contrast that enters a pairwise model.
# Chosen a priori as the most-intensive / primary active arm named by the trial.
MULTIARM_PICK = {
    ("Zhu 2022", "Intraoperative opioid"): "EA day before + 30 min before",
    ("Lu 2021", "Intraoperative opioid"): "Combined PC6+CV17 TEAS",
    ("Huang 2017", "Intraoperative opioid"): None,   # rate metric, excluded anyway
}


def num(v):
    if v in (None, ""):
        return None
    try:
        return float(v)
    except (TypeError, ValueError):
        return None


def load() -> list[dict]:
    wb = openpyxl.load_workbook(V33, data_only=True)
    ws = wb["Outcome_Data"]
    rows = list(ws.iter_rows(values_only=True))
    hdr = [str(h) for h in rows[0]]
    return [dict(zip(hdr, r)) for r in rows[1:]]


def cont(r, scale=1.0):
    """Continuous contrast with MD and its SE, rescaled by an exact factor."""
    mi, si = num(r["Mean intervention"]), num(r["SD intervention"])
    mc, sc = num(r["Mean comparator"]), num(r["SD comparator"])
    ni, nc = num(r["Analyzed n intervention"]), num(r["Analyzed n comparator"])
    if None in (mi, si, mc, sc, ni, nc) or ni < 2 or nc < 2:
        return None
    mi, si, mc, sc = mi * scale, si * scale, mc * scale, sc * scale
    md = mi - mc
    se = math.sqrt(si ** 2 / ni + sc ** 2 / nc)
    sp = math.sqrt(((ni - 1) * si ** 2 + (nc - 1) * sc ** 2) / (ni + nc - 2))
    g = ((mi - mc) / sp) * (1 - 3 / (4 * (ni + nc) - 9)) if sp > 0 else None
    gse = (math.sqrt((ni + nc) / (ni * nc) + g ** 2 / (2 * (ni + nc)))
           if g is not None else None)
    return dict(n_i=int(ni), n_c=int(nc), mean_i=mi, sd_i=si, mean_c=mc, sd_c=sc,
                md=round(md, 6), se=round(se, 6),
                hedges_g=round(g, 6) if g is not None else "",
                hedges_se=round(gse, 6) if gse is not None else "")


def binary(r):
    ei, ec = num(r["Events intervention"]), num(r["Events comparator"])
    ni, nc = num(r["Analyzed n intervention"]), num(r["Analyzed n comparator"])
    if None in (ei, ec, ni, nc):
        return None
    zero = (ei == 0 or ec == 0)
    eic, ecc = ei + 0.5 * zero, ec + 0.5 * zero
    nic, ncc = ni + 0.5 * zero, nc + 0.5 * zero
    lnrr = math.log((eic / nic) / (ecc / ncc))
    se = math.sqrt(1 / eic - 1 / nic + 1 / ecc - 1 / ncc)
    return dict(n_i=int(ni), n_c=int(nc), events_i=int(ei), events_c=int(ec),
                zero_cell=int(zero), lnrr=round(lnrr, 6), se_lnrr=round(se, 6))


def write(name, rows, cols):
    OUT.mkdir(parents=True, exist_ok=True)
    p = OUT / f"{name}.csv"
    with p.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=cols, extrasaction="ignore", lineterminator="\n")
        w.writeheader()
        for r in rows:
            w.writerow(r)
    print(f"  wrote {p.name:<44} k={len(rows)}")
    return len(rows)


def main() -> int:
    D = load()
    print(f"v33 Outcome_Data: {len(D)} rows\n")
    summary = {}

    # ---------------------------------------------------------------------
    # S1. Binary rescue OPIOID use within 0-24 h / POD1.
    # Opioid rescue only. NSAID rescue (flurbiprofen, dexketoprofen) and
    # unspecified "rescue analgesia" are excluded: a different drug class is a
    # different estimand, not a different study.
    # ---------------------------------------------------------------------
    RESCUE_OPIOID_24 = {
        ("Tu 2024", "Any rescue tramadol use"),
        ("Liu 2026 (burn)", "Any rescue dezocine use"),
        ("Yu 2020", "Participants requiring rescue sufentanil"),
    }
    rows = []
    for r in D:
        k = (r["Canonical study"], r["Outcome/result"])
        if k not in RESCUE_OPIOID_24:
            continue
        b = binary(r)
        if not b:
            continue
        rows.append(dict(study=r["Canonical study"], comparison_id=r["Comparison ID"],
                         outcome=r["Outcome/result"], window=r["Timepoint/window"],
                         drug=r["Outcome/result"].split()[2] if len(r["Outcome/result"].split()) > 2 else "",
                         intervention=r["Intervention arm"], comparator=r["Comparator arm"],
                         **b))
    summary["rescue_opioid_binary_24h"] = write(
        "v33_rescue_opioid_binary_24h", rows,
        ["study", "comparison_id", "outcome", "window", "drug", "intervention",
         "comparator", "n_i", "n_c", "events_i", "events_c", "zero_cell",
         "lnrr", "se_lnrr"])

    # ---------------------------------------------------------------------
    # S2. Intraoperative remifentanil, absolute dose.
    # mg is rescaled to ug by an exact factor of 1000 (same drug, same
    # quantity). Rate metrics (ug/kg/min) are a different estimand and are
    # excluded, not converted.
    # ---------------------------------------------------------------------
    def intraop(drug_key, unit_targets):
        out = []
        for r in D:
            if r["Outcome family"] != "Intraoperative opioid":
                continue
            # Wu 2025, 103940.pdf pp. 3018-3019: randomized only on arrival
            # in PACU. Table 1 intraoperative doses predate randomization and
            # intervention; they are baseline covariates, not treatment effects.
            if r["Canonical study"] == "Wu 2025":
                continue
            res = str(r["Outcome/result"]).lower()
            unit = str(r["Unit/scale"] or "").lower()
            if drug_key not in res and drug_key not in unit:
                continue
            if "/kg" in unit or "/min" in unit or "rate" in res or "index" in res:
                continue          # rate metric: different estimand
            if str(r["Data type"]) != "Mean/SD":
                continue          # medians kept out of the MD model
            pick = MULTIARM_PICK.get((r["Canonical study"], r["Outcome family"]), "KEEP")
            if pick != "KEEP" and r["Intervention arm"] != pick:
                continue
            scale = 1000.0 if unit.startswith("mg") else 1.0
            c = cont(r, scale)
            if not c:
                continue
            out.append(dict(study=r["Canonical study"], comparison_id=r["Comparison ID"],
                            intervention=r["Intervention arm"], comparator=r["Comparator arm"],
                            unit_src=r["Unit/scale"], scale_factor=scale,
                            unit_analysis=f"ug {drug_key}",
                            multiarm=str(r["Shared-control / multi-arm issue"]),
                            **c))
        return out

    remi = intraop("remifentanil", None)
    summary["intraop_remifentanil"] = write(
        "v33_intraop_remifentanil", remi,
        ["study", "comparison_id", "intervention", "comparator", "unit_src",
         "scale_factor", "unit_analysis", "multiarm", "n_i", "n_c", "mean_i",
         "sd_i", "mean_c", "sd_c", "md", "se", "hedges_g", "hedges_se"])

    suf = intraop("sufentanil", None)
    summary["intraop_sufentanil"] = write(
        "v33_intraop_sufentanil", suf,
        ["study", "comparison_id", "intervention", "comparator", "unit_src",
         "scale_factor", "unit_analysis", "multiarm", "n_i", "n_c", "mean_i",
         "sd_i", "mean_c", "sd_c", "md", "se", "hedges_g", "hedges_se"])

    # ---------------------------------------------------------------------
    # S3. Global QoR-40 at ~24 h. QoR-15 is a different instrument and is not
    # pooled with QoR-40. Chen 2015 reports QoR-40 as a median and stays out.
    # ---------------------------------------------------------------------
    rows = []
    for r in D:
        if r["Outcome family"] not in ("Quality of recovery", "QoR"):
            continue
        if "QoR-40" not in str(r["Outcome/result"]):
            continue
        if str(r["Data type"]) != "Mean/SD":
            continue
        tp = str(r["Timepoint/window"])
        if "48" in tp:
            continue
        c = cont(r)
        if not c:
            continue
        rows.append(dict(study=r["Canonical study"], comparison_id=r["Comparison ID"],
                         window=tp, intervention=r["Intervention arm"],
                         comparator=r["Comparator arm"], **c))
    summary["qor40_24h"] = write(
        "v33_qor40_24h", rows,
        ["study", "comparison_id", "window", "intervention", "comparator",
         "n_i", "n_c", "mean_i", "sd_i", "mean_c", "sd_c", "md", "se",
         "hedges_g", "hedges_se"])

    # ---------------------------------------------------------------------
    # S4. Time to first defecation (GI recovery), hours, mean/SD.
    # ---------------------------------------------------------------------
    rows = []
    for r in D:
        if r["Outcome family"] != "GI recovery":
            continue
        if "defecation" not in str(r["Outcome/result"]).lower():
            continue
        if str(r["Data type"]) != "Mean/SD":
            continue
        if "hour" not in str(r["Unit/scale"] or "").lower():
            continue
        # Ng 2013 has a shared EA arm. Use the sham-controlled contrast
        # (the blinded comparison) once; retain the usual-care contrast only
        # in the workbook and the not-pooled register.
        if r['Canonical study'] == 'Ng 2013' and r['Comparison ID'] != 'NG13_EA_vs_SHAM_BOWEL':
            continue
        c = cont(r)
        if not c:
            continue
        rows.append(dict(study=r["Canonical study"], comparison_id=r["Comparison ID"],
                         intervention=r["Intervention arm"], comparator=r["Comparator arm"],
                         unit=r["Unit/scale"], **c))
    summary["gi_first_defecation"] = write(
        "v33_gi_first_defecation", rows,
        ["study", "comparison_id", "intervention", "comparator", "unit",
         "n_i", "n_c", "mean_i", "sd_i", "mean_c", "sd_c", "md", "se",
         "hedges_g", "hedges_se"])

    # ---------------------------------------------------------------------
    # S5. Not-pooled register: outcomes that exist but must not enter a model,
    # with the reason. Published so the exclusions are visible, not implicit.
    # ---------------------------------------------------------------------
    notpooled = [
        dict(study='Ng 2013', outcome='First bowel motion: EA vs no acupuncture',
             window='Time to event', stat='Alternative contrast with a shared EA arm',
             reason='The sham-controlled contrast is selected for this model to preserve the blinded comparison and count each participant once. covidence_1970_ng_2013.pdf, Methods and Tables 3-4.'),
        dict(study='Wu 2025', outcome='Intraoperative remifentanil and sufentanil',
             window='Intraoperative, before randomization',
             stat='Baseline covariates in Table 1; original values retained in frozen v33 master',
             reason='103940.pdf pp. 3018-3019: randomization and TEAS began on PACU arrival. Intraoperative doses cannot estimate the effect of a later intervention.'),
        dict(study="Yao 2015", outcome="Cumulative rescue administrations", window="0-24 h",
             stat="Median (IQR) 1 (1-3) vs 3.5 (2-7.8), P=0.004",
             reason="Rescue COUNT, not dose. Multiplying a median count by 0.05 ug/kg and a "
                    "mean body weight would not recover any individual-level quantity."),
        dict(study="Chen 2015 (Hyperalgesia)", outcome="Rescue sufentanil PCIA boluses",
             window="0-24 h", stat="Median (IQR) 3 (2-4) vs 7 (6-8)",
             reason="Rescue COUNT in boluses; weight-normalised per-bolus dosing not "
                    "reconstructable. Different unit from Yao 2015, so the two counts are "
                    "not pooled with each other either."),
        dict(study="Yao 2015", outcome="Time to first rescue analgesia", window="0-24 h",
             stat="Median 59 (31-1440) vs 47 (13-196) min, P=0.039",
             reason="k=1; dispersion is a reported range and the upper bound is the 24-h "
                    "censoring point. Narrative only."),
        dict(study="Liang 2021", outcome="Postoperative analgesia requirement", window="unclear",
             stat="3.8 (1.9) vs 5.0 (2.9), P=0.045",
             reason="HOLD. Source calls it a count of patients, which 3.8/35 cannot be. "
                    "Metric, unit and window all undefined."),
        dict(study="Yu 2020", outcome="Resting pain VAS", window="POD1 and POD2",
             stat="POD1 3.70 vs 4.73; POD2 1.83 vs 2.30",
             reason="CONFLICTED. Table 2 and abstract disagree on the TEAS SDs (1.53/0.98 vs "
                    "1.41/0.88) and on the POD2 P value (table stars P<0.05, Results text "
                    "says P=0.26)."),
        dict(study="Zhou 2021", outcome="Any postoperative opioid use", window="undefined",
             stat="18/41 vs 30/40",
             reason="Postoperative window not defined in the source, so it cannot join the "
                    "0-24 h binary rescue model."),
        dict(study="Liu 2026 (ESD)", outcome="Any rescue IV morphine use", window="through 48 h",
             stat="19/58 vs 40/62",
             reason="48-h window; kept out of the 0-24 h binary rescue model."),
        dict(study="Hou 2023", outcome="Any rescue flurbiprofen use", window="postoperative",
             stat="15/36 vs 28/36",
             reason="Flurbiprofen is an NSAID, not an opioid. Not pooled with opioid rescue."),
        dict(study="Oztas 2019", outcome="Rescue pethidine / dexketoprofen", window="0-24 h",
             stat="mean/SD reported",
             reason="No sourced IV MME factor for pethidine; dexketoprofen is an NSAID."),
        dict(study="Zhu 2022", outcome="Intraoperative sufentanil and remifentanil",
             window="intraoperative",
             stat="4-group omnibus P only (0.892 / 0.948)",
             reason="Two of three active contrasts are dropped from each model so the shared "
                    "usual-care arm (n=101) is not counted more than once."),
        dict(study="Lu 2021", outcome="Total remifentanil", window="intraoperative",
             stat="two active arms vs one sham arm",
             reason="Multi-arm; only the combined PC6+CV17 contrast enters the model."),
    ]
    summary["not_pooled_register"] = write(
        "v33_not_pooled_register", notpooled,
        ["study", "outcome", "window", "stat", "reason"])

    print("\nAnalysis sets built:")
    for k, v in summary.items():
        print(f"  {k:<34} k={v}")
    return 0


if __name__ == "__main__":
    sys.exit(main())

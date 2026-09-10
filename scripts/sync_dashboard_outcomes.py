#!/usr/bin/env python3
"""
Regenerate the arm-level outcome records in dashboard/data.js from the lock.

WHY THIS EXISTS
---------------
Incident 2026-09-10. dashboard/data.js used to be a hand-maintained copy of the
same numbers the locked datasets already hold. Fifteen of its arm-bearing cells
had drifted into placeholder values that matched no source and no lock.

The dashboard boot sequence (dashboard/app.js) overwrites s.outcomes[key] from
the GENERATED window.BROWSER_TARGETS for every pooled bucket, so those stale
numbers never reached a forest plot -- but they sat in the committed register,
were read by anyone inspecting data.js, and would have gone live the moment
that overwrite was relaxed.

This script removes the hand-maintained copy as a category: it derives the same
records browser_targets.js is built from, and writes them into data.js. The two
therefore cannot disagree. scripts/validate_dashboard.py asserts this sync is
current, so a hand edit to data.js is caught rather than shipped.

Records for studies the lock does not carry (narrative "not pooled -- different
opioid scope" cells) are PRESERVED verbatim: they hold no arm-level numbers and
the lock has nothing to say about them.

Usage:  python3 scripts/sync_dashboard_outcomes.py [--check]
        --check exits 1 if data.js is out of sync, without writing.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

ROOT = Path(__file__).resolve().parents[1]
DATA_JS = ROOT / "dashboard" / "data.js"

# Arm-level fields the lock owns. Anything else on an outcome record (status,
# note, favors, drug, p_val ...) is dashboard presentation and is preserved.
LOCK_FIELDS = (
    "arm1_n", "arm2_n", "arm1_mean", "arm1_sd", "arm2_mean", "arm2_sd",
    "arm1_events", "arm2_events", "mean_diff", "se", "ci_low", "ci_upp",
    "rr", "unit", "comparison_id", "source_dataset", "source_note", "result_rob",
    "converted_from",
    # Stale randomised denominators. meta_engine.js reads `arm1_total ?? arm1_n`,
    # so a leftover arm1_total silently overrides the analysed n the lock gives
    # (Tu 2024 carried 77/76 against an analysed 57/58). The lock never emits
    # these, so listing them here drops them.
    "arm1_total", "arm2_total",
)


def round_record(rec: dict) -> dict:
    """Match the precision data.js is written at; float32 noise in the CSVs
    otherwise produces values like 55.200001 that read as false precision."""
    out = {}
    for k, v in rec.items():
        if isinstance(v, float):
            out[k] = round(v, 6) if abs(v) < 1 else round(v, 4)
        else:
            out[k] = v
    return out


def favors_for(rec: dict):
    """Direction is DERIVED from the observed effect, never carried over.
    For every outcome in this review a lower value is the favourable one."""
    if isinstance(rec.get("mean_diff"), (int, float)):
        return "Intervention" if rec["mean_diff"] < 0 else "Control"
    if isinstance(rec.get("rr"), (int, float)):
        return "Intervention" if rec["rr"] < 1 else "Control"
    return None


def build_targets() -> dict:
    from build_reference_data import browser_targets
    text = DATA_JS.read_text(encoding="utf-8").split("window.STUDIES_DATA = ", 1)[1]
    studies = json.JSONDecoder().raw_decode(text)[0]
    return browser_targets(studies)


def primary_records() -> dict:
    """The locked 0-24 h primary set, exactly as primary_browser.js is built."""
    import csv
    cols = {"arm1_n": "n_i", "arm2_n": "n_c", "arm1_mean": "mean_i_mme",
            "arm1_sd": "sd_i_mme", "arm2_mean": "mean_c_mme", "arm2_sd": "sd_c_mme",
            "mean_diff": "md_mme", "se": "se_mme", "ci_low": "ci_low_mme",
            "ci_upp": "ci_upp_mme"}
    src = ROOT / "06_FINAL_ANALYSIS_V26/01_DATA/opioid_24h_primary.csv"
    out = {}
    with src.open(encoding="utf-8-sig") as fh:
        for r in csv.DictReader(fh):
            if r["inc_primary"] != "1":
                continue
            rec = {k: float(r[c]) for k, c in cols.items()}
            rec["unit"] = "mg IV MME"
            rec["comparison_id"] = r["comparison_id"]
            out[r["study_unit"]] = rec
    return out


def master_units() -> dict:
    """Raw unit per (study, outcome family) from the v34 master.

    Used only to relabel arm-level 0-24 h records that are NOT in the primary
    pool. Those carried "mg IV MME" while holding the raw published statistic --
    Jin 2023's 39.31 is mL of PCIA solution, Coura 2011's 13.1 is ug/kg fentanyl.
    No conversion is invented here; the record is labelled for what it is."""
    import openpyxl
    wb = openpyxl.load_workbook(
        ROOT / "TEAS EA Verification/TEAS_EA_RECONCILED_MASTER_DATA_v34_FINAL_LOCK_READY.xlsx",
        read_only=True, data_only=True)
    it = wb["Outcome_Data_AF_LOCK"].iter_rows(values_only=True)
    hdr = [str(h) for h in next(it)]
    out = {}
    for row in it:
        d = dict(zip(hdr, row))
        study = str(d.get("Canonical study") or "").strip()
        mi = d.get("Mean intervention")
        if not study or mi is None:
            continue
        out.setdefault(study, []).append((float(mi), d.get("Unit/scale"), d.get("Outcome/result")))
    wb.close()
    return out


def sync(check_only: bool = False) -> int:
    targets = build_targets()
    raw = DATA_JS.read_text(encoding="utf-8")
    head, body = raw.split("window.STUDIES_DATA = ", 1)
    studies, end = json.JSONDecoder().raw_decode(body)
    tail = body[end:]

    primary = primary_records()
    units = master_units()

    changed = []
    for s in studies:
        outcomes = s.get("outcomes") or {}

        # 0-24 h primary. The pooled set is generated from the lock like every
        # other bucket. Records outside the pooled set keep their (master-backed)
        # values but are relabelled with the raw unit the master records, so a
        # raw statistic is never presented as a morphine-equivalent dose.
        rec24 = outcomes.get("opioid_24h")
        if isinstance(rec24, dict):
            if s["key"] in primary:
                merged = {k: v for k, v in rec24.items() if k not in LOCK_FIELDS}
                merged.pop("status", None)
                merged.update(round_record(primary[s["key"]]))
                merged["favors"] = favors_for(merged)
                if merged != rec24:
                    changed.append(f"{s['key']}/opioid_24h")
                outcomes["opioid_24h"] = merged
            elif "arm1_mean" in rec24:
                raw = [u for m, u, _ in units.get(s["key"], [])
                       if abs(m - float(rec24["arm1_mean"])) < 0.02]
                if raw and raw[0] and rec24.get("unit") != raw[0]:
                    rec24 = dict(rec24)
                    rec24["unit"] = raw[0]
                    rec24["note"] = (
                        (rec24.get("note", "") + " ").lstrip()
                        + "Not in the locked 0-24 h primary pool; value is the raw published "
                          "statistic in the unit shown and has not been converted to morphine "
                          "equivalents. Unit label corrected 2026-09-10.").strip()
                    changed.append(f"{s['key']}/opioid_24h: unit relabelled to '{raw[0]}'")
                    outcomes["opioid_24h"] = rec24

        for bucket, records in targets.items():
            rec = records.get(s["key"])
            existing = outcomes.get(bucket)
            if rec is None:
                # The lock does not carry this study for this bucket. Keep a
                # narrative/status-only record; drop anything that still claims
                # arm-level numbers, because nothing authoritative backs them.
                if isinstance(existing, dict) and any(
                    k in existing for k in ("arm1_mean", "arm1_events")
                ):
                    changed.append(f"{s['key']}/{bucket}: unbacked arm-level record removed")
                    outcomes[bucket] = {
                        "status": "Not pooled — no locked arm-level record",
                        "note": "No row for this study/outcome in the locked dataset; "
                                "any previous arm-level values here were unsourced.",
                    }
                continue

            merged = {k: v for k, v in (existing or {}).items() if k not in LOCK_FIELDS}
            merged.pop("status", None)          # a locked record is not "unavailable"
            merged.update(round_record(rec))
            fav = favors_for(merged)
            if fav:
                merged["favors"] = fav
            if merged != existing:
                changed.append(f"{s['key']}/{bucket}")
            outcomes[bucket] = merged
        s["outcomes"] = outcomes

    if check_only:
        if changed:
            print(f"OUT OF SYNC: {len(changed)} outcome record(s) differ from the lock")
            for c in changed[:25]:
                print(f"  {c}")
            if len(changed) > 25:
                print(f"  ... and {len(changed) - 25} more")
            return 1
        print("data.js outcome records are in sync with the lock")
        return 0

    DATA_JS.write_text(
        head + "window.STUDIES_DATA = "
        + json.dumps(studies, ensure_ascii=False, indent=2) + tail,
        encoding="utf-8",
    )
    print(f"synced {len(changed)} outcome record(s) from the lock")
    for c in changed:
        print(f"  {c}")
    return 0


if __name__ == "__main__":
    sys.exit(sync(check_only="--check" in sys.argv))

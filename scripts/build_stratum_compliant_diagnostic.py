#!/usr/bin/env python3
"""
Publish what the PROTOCOL-COMPLIANT strata would give, beside the warning that
says the reported analyses are not compliant.

WHY
scripts/check_stratum_purity.py reports that three reported analyses pool across
protocol strata, and the dashboard has warned so for some time. What it could not
say was the thing a reader actually wants to know: what happens if you split them.
The review team asked, so 06_FINAL_ANALYSIS_V26/02_STATA/15_stratum_compliant_
diagnostic.do fits every compliant stratum with k >= 2 and this publishes it.

The answer is not "cleaner analyses". Target E's TEAS-vs-Sham stratum has a HIGHER
I2 than the k=7 pool it would replace, Target A's spans -129 to +104 mg MME, and
Target D 0-48 h has no estimable stratum at all. Protocol compliance and
heterogeneity turn out to be separate problems.

WHAT THIS IS NOT
Not a finding and not an alternative headline. Every number here is labelled
DIAGNOSTIC, the reported analyses and their warnings are untouched, and whether to
report stratified results is a review-team decision this informs rather than
makes.

Usage:  python3 scripts/build_stratum_compliant_diagnostic.py
"""
from __future__ import annotations

import csv
import json
import sys
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DASH = ROOT / "dashboard"
RESULTS = ROOT / "06_FINAL_ANALYSIS_V26" / "03_RESULTS" / "results_stratum_compliant_diagnostic.csv"
PURITY = DASH / "stratum_purity.js"
OUT = DASH / "stratum_compliant_diagnostic.js"

# Zhang 2018's modality is unfilled in the v34 outcome register. The source
# settles it -- "Needleless Transcutaneous Electrical Acustimulation", methods
# state TEA "is a newly developed method of EA by replacing needles with surface
# electrodes", electrodes at bilateral ST36 and PC6 -- so the membership below
# reads it as TEAS and says so. The register edit is the review team's, because
# modality feeds stratification.
SOURCE_MODALITY = {
    "Zhang 2018": ("TEAS",
                   "Source-verified: “Needleless Transcutaneous Electrical "
                   "Acustimulation”; TEA “is a newly developed method of EA by "
                   "replacing needles with surface electrodes”, electrodes at bilateral "
                   "ST36 and PC6. The v34 outcome register leaves this unfilled."),
}

# stratum id in the Stata output -> (analysis_id, modality, comparator, units)
FITTED = {
    "TE_FLATUS_TEAS_SHAM": ("AN-07-TARGET-E", "TEAS", "Sham", "hours"),
    "TE_FLATUS_EA_USUAL": ("AN-07-TARGET-E", "EA", "Usual care", "hours"),
    "TA_48H_TEAS_SHAM": ("AN-02-TARGET-A", "TEAS", "Sham", "mg IV MME"),
}


def read_js(path: Path, var: str):
    src = path.read_text(encoding="utf-8")
    start = src.index(var + " = ") + len(var + " = ")
    return json.JSONDecoder().raw_decode(src[start:])[0]


def main() -> int:
    if not RESULTS.exists():
        print(f"missing {RESULTS}; run 15_stratum_compliant_diagnostic.do first", file=sys.stderr)
        return 1
    fits = {r["stratum"]: r for r in csv.DictReader(RESULTS.open(encoding="utf-8-sig"))}
    purity = read_js(PURITY, "window.STRATUM_PURITY")

    out = {"generated_by": "scripts/build_stratum_compliant_diagnostic.py",
           "source": "06_FINAL_ANALYSIS_V26/03_RESULTS/results_stratum_compliant_diagnostic.csv",
           "status": "DIAGNOSTIC - not a finding, not an alternative headline result",
           "analyses": []}

    for f in purity["findings"]:
        if f["pure"]:
            continue
        groups: dict[tuple[str, str], list[str]] = defaultdict(list)
        notes = {}
        for c in f["contributors"]:
            mod = c["modality"]
            if c["study"] in SOURCE_MODALITY:
                mod, why = SOURCE_MODALITY[c["study"]]
                notes[c["study"]] = why
            groups[(mod, c["comparator"])].append(c["study"])

        strata = []
        for (mod, comp), studies in sorted(groups.items(), key=lambda kv: (-len(kv[1]), kv[0])):
            fit_id = next((sid for sid, (aid, m, cp, _u) in FITTED.items()
                           if aid == f["analysis_id"] and m == mod and cp == comp), None)
            row = {"modality": mod, "comparator": comp, "k": len(studies),
                   "studies": sorted(studies), "estimable": len(studies) >= 2}
            if fit_id and fit_id in fits:
                r = fits[fit_id]
                row["fit"] = {
                    "units": FITTED[fit_id][3],
                    "k": int(float(r["k"])),
                    "estimate": float(r["est"]), "ci_low": float(r["lo"]),
                    "ci_high": float(r["hi"]), "p_value": float(r["pval"]),
                    "i2": float(r["i2"]), "tau2": float(r["tau2"]),
                }
                if row["fit"]["k"] != row["k"]:
                    print(f"ABORT: {fit_id} fitted k={row['fit']['k']} but membership says "
                          f"k={row['k']}", file=sys.stderr)
                    return 1
            elif len(studies) >= 2:
                print(f"ABORT: {mod} vs {comp} in {f['analysis_id']} has k={len(studies)} "
                      f"but no fit was supplied", file=sys.stderr)
                return 1
            strata.append(row)

        out["analyses"].append({
            "analysis_id": f["analysis_id"],
            "reported_k": f["k"],
            "compliant_strata": len(strata),
            "estimable_strata": sum(1 for s in strata if s["estimable"]),
            "largest_k": max(s["k"] for s in strata),
            "strata": strata,
            "source_modality_notes": notes,
        })

    OUT.write_text(
        "// GENERATED by scripts/build_stratum_compliant_diagnostic.py -- do not hand-edit.\n"
        "// DIAGNOSTIC ONLY. Shows what the protocol-compliant strata would give; it is\n"
        "// not a finding and does not replace any reported analysis.\n"
        "window.STRATUM_COMPLIANT_DIAGNOSTIC = "
        + json.dumps(out, ensure_ascii=False, indent=2) + ";\n",
        encoding="utf-8")

    for a in out["analyses"]:
        print(f"{a['analysis_id']}: reported k={a['reported_k']} -> {a['compliant_strata']} "
              f"compliant strata, {a['estimable_strata']} estimable, largest k={a['largest_k']}")
        for s in a["strata"]:
            fit = s.get("fit")
            tail = (f"  MD {fit['estimate']:+.2f} [{fit['ci_low']:+.2f}, {fit['ci_high']:+.2f}] "
                    f"p={fit['p_value']:.4f} I2={fit['i2']:.1f}%" if fit else "  not estimable")
            print(f"    k={s['k']}  {s['modality']} vs {s['comparator']}{tail}")
    return 0


if __name__ == "__main__":
    sys.exit(main())

#!/usr/bin/env python3
"""
Resolve the modality and comparator-type classifications left as
*_REVIEW_REQUIRED in the v34 native data.

This applies the classification rule this project already uses in
06_FINAL_ANALYSIS_V26/02_STATA/00_prep_data.do, which was corrected earlier in
the project after a case-sensitivity and rule-order defect: inert-sham markers
are tested BEFORE device names, so "Sham ST36 TENS (0 mA)" is read as a sham
control rather than as an active electrical one.

It is a classification pass over descriptive arm text, not a new scientific
judgement. Anything the documented rule does not decide is left as an explicit
hold and reported, rather than guessed.

Comparator categories (as used throughout the review):
  Sham              inert/placebo device: no current, 0 mA, non-penetrating
  Active Electrical real current delivered at a non-acupoint / non-meridian site
  Usual care        no device arm at all, including a balanced co-intervention

Modality:
  TEAS  surface electrodes on the skin (TEAS, TAES, SSP, acupoint TENS)
  EA    needle electroacupuncture
"""

from __future__ import annotations

import csv
import glob
import re
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "TEAS EA Verification" / "v34_reconciliation" / "data"
OUT = ROOT / "09_V34_ANALYSIS"

# ── comparator rules, in the order the project applies them ────────────────
# 1. inert sham markers, tested first
SHAM = [
    "0 ma", "zero-current", "zero current", "no-current", "no current",
    "no stimulation", "nonpenetrating", "non-penetrating", "sub-sensory",
    "placebo", "sham", "subthreshold", "sub-threshold",
]
# 2. real current at a control site -- only after the sham test
ACTIVE_ELECTRICAL = [
    "nonacupoint", "non-acupoint", "nonmeridian", "non-meridian",
    "incision-periphery tens", "non-acupuncture point",
]
# 3. no device arm at all
USUAL_CARE = [
    "usual care", "standard care", "routine", "no teas", "no-teas", "no ea",
    "no acupuncture", "no stimulation device", "control group", "blank",
    "no intervention", "conventional",
    # Spelling variants of the same no-device arm. TAES/AES/EAS are the same
    # surface-stimulation device family as TEAS; "No-TAES ... control" is a
    # no-device arm by the same rule, not a new category.
    "no taes", "no-taes", "no aes", "no-aes", "no eas", "no-eas",
    "no-stimulation", "without teas", "without stimulation",
    "untreated", "no treatment", "nontreated", "non-treated",
]

TEAS_MARKERS = ["teas", "taes", "transcutaneous", "surface electrode", "ssp",
                "silver spike", "acupoint stimulation", "tens", "aes", "peas"]
EA_MARKERS = ["electroacupuncture", "electro-acupuncture", "needle", "ea "]


def classify_comparator(comparator: str, intervention: str) -> tuple[str, str]:
    c = (comparator or "").lower()
    if not c.strip():
        return "", "no comparator text"
    # Inert sham first. This ordering is the documented correction: a device
    # name inside a sham description must not win.
    for m in SHAM:
        if m in c:
            return "Sham", f"inert-sham marker {m!r}"
    for m in ACTIVE_ELECTRICAL:
        if m in c:
            return "Active Electrical", f"control-site marker {m!r}"
    for m in USUAL_CARE:
        if m in c:
            return "Usual care", f"no-device marker {m!r}"
    # A comparator that repeats the intervention's co-intervention without the
    # stimulation is a usual-care arm: e.g. "TAP block + TEAS" vs "TAP block".
    # A comparator that repeats the intervention's co-intervention without the
    # stimulation is a usual-care arm: "TAP block + TEAS" vs "TAP block", or
    # "ondansetron+dexamethasone+TEAS" vs "ondansetron+dexamethasone".
    # Arm-code suffixes in parentheses ("(SNVP-ODT)" vs "(SNVP-OD)") are
    # labels, not interventions, so they are removed before comparing.
    def core(t):
        t = re.sub(r"\([^)]*\)", " ", (t or "").lower())
        return re.sub(r"[^a-z0-9]+", " ", t).strip()

    iv_core, c_core = core(intervention), core(comparator)
    if c_core and iv_core.startswith(c_core):
        return "Usual care", "comparator is the intervention's co-intervention without stimulation"
    # Same comparison allowing the stimulation token to sit anywhere in the
    # intervention string rather than only as a suffix.
    if c_core:
        remainder = iv_core
        for tok in c_core.split():
            if tok in remainder:
                remainder = remainder.replace(tok, "", 1)
        remainder = remainder.strip()
        if remainder and any(m in remainder for m in ("teas", "taes", "ea", "aes", "acupoint")):
            return "Usual care", "comparator is the intervention minus the stimulation component"
    return "", "no documented rule matched"


def canonical_modalities() -> dict:
    """Modality as already classified for each study in the review's canonical
    study list. A study-level classification the review has already made is
    authoritative over anything inferred from one arm's description, so it is
    consulted before the text rule is trusted."""
    src = (ROOT / "dashboard" / "data.js").read_text(encoding="utf-8")
    out = {}
    for m in re.finditer(r'"key":\s*"([^"]+)"(.{0,1500}?)"modality":\s*"([^"]*)"', src, re.S):
        out.setdefault(m.group(1), m.group(3))
    return out


CANONICAL = canonical_modalities()


def classify_modality(intervention: str) -> tuple[str, str]:
    i = (intervention or "").lower()
    if not i.strip():
        return "", "no intervention text"
    # EA is needle-based; check it first because some EA descriptions also
    # mention electrical stimulation generally.
    for m in EA_MARKERS:
        if m in i:
            return "EA", f"needle marker {m!r}"
    for m in TEAS_MARKERS:
        if m in i:
            return "TEAS", f"surface marker {m!r}"
    return "", "no documented rule matched"


def main() -> int:
    rows = []
    for f in sorted(glob.glob(str(DATA / "v34_native_*.csv"))):
        fam = Path(f).stem.replace("v34_native_", "")
        with open(f, encoding="utf-8-sig") as fh:
            for r in csv.DictReader(fh):
                r["_family"] = fam
                rows.append(r)

    need = [r for r in rows
            if "REVIEW_REQUIRED" in r["comparator_type"] or "REVIEW_REQUIRED" in r["modality"]]
    print(f"rows needing resolution: {len(need)} of {len(rows)}\n")

    out, unresolved = [], []
    for r in need:
        mod, mod_why = (r["modality"], "already set")
        if "REVIEW_REQUIRED" in r["modality"]:
            mod, mod_why = classify_modality(r["intervention"])
            if not mod and r["study"] in CANONICAL and CANONICAL[r["study"]] in ("TEAS", "EA"):
                mod = CANONICAL[r["study"]]
                mod_why = "canonical study-level modality from the review's study list"
        comp, comp_why = (r["comparator_type"], "already set")
        if "REVIEW_REQUIRED" in r["comparator_type"]:
            comp, comp_why = classify_comparator(r["comparator"], r["intervention"])

        rec = dict(
            record_id=r["record_id"], study=r["study"], family=r["_family"],
            outcome=r["outcome"], window=r["window"],
            intervention=r["intervention"], comparator=r["comparator"],
            modality_before=r["modality"], modality_after=mod, modality_basis=mod_why,
            comparator_before=r["comparator_type"], comparator_after=comp,
            comparator_basis=comp_why,
            resolved="YES" if (mod and comp) else "NO",
        )
        out.append(rec)
        if not (mod and comp):
            unresolved.append(rec)

    p = OUT / "v34_comparator_resolution.csv"
    with p.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(out[0].keys()), lineterminator="\n")
        w.writeheader()
        w.writerows(out)

    ok = [r for r in out if r["resolved"] == "YES"]
    print(f"resolved by the documented rule : {len(ok)}")
    print(f"still unresolved (explicit hold): {len(unresolved)}\n")

    print("resolved comparator types:")
    for v, n in Counter(r["comparator_after"] for r in ok).most_common():
        print(f"  {n:>4}  {v}")
    print("\nresolved modalities:")
    for v, n in Counter(r["modality_after"] for r in ok).most_common():
        print(f"  {n:>4}  {v}")

    if unresolved:
        print(f"\nUNRESOLVED -- left as holds ({len(unresolved)}):")
        for u in unresolved[:12]:
            print(f"  {u['study']:<14} {u['outcome'][:30]:<30}")
            print(f"       iv: {u['intervention'][:64]}")
            print(f"       cm: {u['comparator'][:64]}  -> {u['comparator_basis']}")

    print(f"\nwrote {p.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())

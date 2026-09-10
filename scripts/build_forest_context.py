#!/usr/bin/env python3
"""
Extract per-study forest-plot context (effect, CI, % weight) from the Stata
log that actually produced the primary forest figure, for interactive display
alongside the (static, Stata-generated) PNG image.

WHY THIS EXISTS, AND WHY IT DOES NOT TOUCH THE IMAGE
Phase 25 of the dashboard audit brief asks for per-study hover/tap context on
forest plots. The plots themselves are static PNGs rendered by Stata's own
`meta forestplot` (06_FINAL_ANALYSIS_V26/02_STATA/01_opioid24_primary.do:89-93)
-- a raster image has no DOM to attach hover behaviour to, and reimplementing
the plot as SVG/HTML would mean re-deriving Stata's own layout and rounding by
hand, which is exactly the "regenerate statistical results using JavaScript
and assume equivalence" the brief itself prohibits (its non-negotiable rules).
So the image stays untouched, generated the same way, and this instead builds
a genuinely interactive DATA TABLE next to it carrying the same information a
reader would want from hovering a point: the per-study effect, CI and pooling
weight this review's own Stata run assigned.

WHERE THE NUMBERS COME FROM
Parsed directly from 01_opioid24_primary.log's forest block for
`meta forestplot if inc_primary == 1, subgroup(modality)` -- the exact block
that produced forest_opioid24_primary_mme.png, confirmed against the do-file's
own graph export line, not assumed from file naming.

WHAT THIS DOES NOT DUPLICATE
Modality, comparator, RoB 2 and derivability tier are NOT re-extracted here.
They already exist, once, in dashboard/data.js (STUDIES_DATA) and are read
client-side by joining on study key -- adding a second copy of that
information in this file would create exactly the kind of duplicate source
of truth this project has already been bitten by twice this session
(the translations.js/index.html static-text divergence, and the RoB2 domain
rationale). This file carries ONLY the numbers that exist nowhere else:
the per-study effect, CI and weight Stata actually computed.

Usage:  python3 scripts/build_forest_context.py
Exit:   0 on success, 1 if the expected forest block cannot be found.
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
LOG = ROOT / "06_FINAL_ANALYSIS_V26" / "02_STATA" / "logs" / "01_opioid24_primary.log"
OUT = ROOT / "dashboard" / "forest_context.js"

# One entry per figure this covers. Scoped to the primary analysis for this
# pass -- the review's single most scrutinised figure -- rather than
# attempting all 12 forest plots at once; see the audit changelog for why.
FIGURES = [
    {
        "figure": "forest_opioid24_primary_mme.png",
        "analysis_id": "AN-01-COMB",
        # Distinguishes this block from any other forest block sharing some of
        # the same study names later in the same log (e.g. the TEAS-only or
        # EA-only re-fits), so this can never silently pick up the wrong table
        # if the log's contents change.
        "block_marker": "Effect size: Mean Difference (mg IV MME)",
        "expected_studies": {"Chen 1998", "Chen 2020", "El-Rakshy 2009",
                             "He 2026 (hepatectomy/JIS)", "Seevaunnamtum 2016",
                             "Szmit 2021", "Yang 2024"},
    },
]


def parse_first_forest_block(text: str, marker: str) -> list[dict]:
    i = text.index(marker)
    block = text[i:text.index("theta", i)]
    rows = []
    for m in re.finditer(
            r"^\s*([A-Za-z][A-Za-z0-9 '()/\-]*?)\s*\|\s*(-?[\d.]+)\s+(-?[\d.]+)\s+(-?[\d.]+)\s+([\d.]+)\s*$",
            block, re.M):
        study, est, lo, hi, wt = m.groups()
        rows.append({"study": study.strip(), "estimate": float(est),
                     "ci_low": float(lo), "ci_high": float(hi), "weight_pct": float(wt)})
    return rows


def build() -> dict:
    if not LOG.exists():
        raise SystemExit(f"missing Stata log: {LOG}")
    text = LOG.read_text(encoding="utf-8", errors="replace")

    out = []
    for fig in FIGURES:
        rows = parse_first_forest_block(text, fig["block_marker"])
        got = {r["study"] for r in rows}
        if got != fig["expected_studies"]:
            raise SystemExit(
                f"{fig['figure']}: parsed studies {sorted(got)} do not match the "
                f"expected set {sorted(fig['expected_studies'])} -- the log format "
                f"may have changed; refusing to publish a mismatched forest context")
        weight_sum = sum(r["weight_pct"] for r in rows)
        if abs(weight_sum - 100.0) > 0.5:
            raise SystemExit(
                f"{fig['figure']}: per-study weights sum to {weight_sum:.2f}%, "
                f"expected ~100% -- refusing to publish")
        out.append({"figure": fig["figure"], "analysis_id": fig["analysis_id"],
                    "source": str(LOG.relative_to(ROOT)), "rows": rows})

    return {
        "generated_by": "scripts/build_forest_context.py",
        "disclaimer": ("Per-study effect, 95% CI and pooling weight, parsed from the "
                       "Stata log that produced the adjacent forest plot image. Modality, "
                       "comparator, risk of bias and derivability tier are read client-side "
                       "from the review's existing study data, not duplicated here."),
        "figures": out,
    }


def main() -> int:
    payload = build()
    OUT.write_text(
        "// GENERATED by scripts/build_forest_context.py -- do not hand-edit.\n"
        "// Per-study rows are parsed from the Stata log, verified against the "
        "expected study set and weight sum before being written.\n"
        "window.FOREST_CONTEXT = " + json.dumps(payload, indent=2, ensure_ascii=False) + ";\n",
        encoding="utf-8")
    print(f"wrote {OUT.relative_to(ROOT)}")
    for fig in payload["figures"]:
        print(f"  {fig['figure']}: {len(fig['rows'])} studies")
        for r in fig["rows"]:
            print(f"    {r['study']:26s} {r['estimate']:>8.3f} "
                  f"[{r['ci_low']:.3f}, {r['ci_high']:.3f}]  {r['weight_pct']:.2f}%")
    return 0


if __name__ == "__main__":
    sys.exit(main())

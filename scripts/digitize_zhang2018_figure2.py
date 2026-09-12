#!/usr/bin/env python3
"""
Formal digitization of Zhang 2018 Figure 2, and the QC verdict on it.

WHY THIS IS NOT "VISUALLY INFERRING"
The locked workbook's instruction for this study is specific: "Exact group
mean+/-SE values are shown only in Figure 2a; do not visually infer", and
"do not enter Figure 2 continuous outcomes into quantitative meta-analysis until
formal graph digitization or author data provide exact means/SEs." Formal
digitization is the sanctioned route; eyeballing a raster is what is forbidden.

Figure 2 is VECTOR art. Every bar is a path with exact coordinates in the PDF
content stream, and every axis tick is a positioned text run. Nothing here is
read off pixels: the bar tops, the error-bar whiskers and the tick positions are
all numbers the file itself carries. That is a stronger method than the raster
pipeline used for Gu 2019.

METHOD (same shape as 07_TIERED_V33/03_DIGITIZATION/gu2019_digitization_QC.md)
  1. Bars: filled rectangles, keyed to arm by fill colour (black = TEA,
     grey = sham-TEA). One bar -- POD 2 TEA -- is drawn as an unfilled outline
     instead of a fill, and is recovered from its two vertical edge segments.
  2. Calibration: least-squares fit of value against y over the panel's own
     numeric axis ticks. The maximum tick residual is reported; a panel is
     rejected if it exceeds 0.1 axis units.
  3. Error bars: the vertical whisker above each bar top gives SE directly.
  4. VALIDATION, and this is the point: the paper reports SIX percentage
     reductions in its Results text and tabulates none of the underlying values.
     Each digitized pair is checked against its reported percentage. A pair is
     accepted only if it reproduces to within 2 percentage points.

WHAT THIS SCRIPT DOES NOT DO
It does not enter anything into a synthesis. Admitting a digitized study to a
pooled analysis is a review-team decision, exactly like clearing an
interpretation staleness flag, and the workbook's instruction is addressed to
that decision rather than to this extraction.

Usage:  python3 scripts/digitize_zhang2018_figure2.py [--json]
"""
from __future__ import annotations

import json
import statistics
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PDF = (ROOT / "TEAS EA Verification" / "Source PDFs" /
       "Needleless Transcutaneous Electrical Acustimulation_ A Pilot Study "
       "Evaluating Improvement in Post-Operative Recovery-2.pdf")
PAGE = 3          # 0-based; Figure 2 is on printed page 4
N_PER_ARM = 21    # Table 1: 21 TEA, 21 active non-acupoint sham

BLACK = (0.0, 0.0, 0.0)
GREYS = {(0.6929884552955627, 0.7009994387626648, 0.7109941244125366),
         (0.69599449634552, 0.7039902210235596, 0.7139849066734314)}

# Reported reductions, verbatim from the Results text, with the bar pair each
# belongs to identified by the x-order of the panel it sits in.
REPORTED = {
    ("a", 0): ("time to defecation", 31.7),
    ("a", 1): ("time to first flatus", 35.9),
    ("b", 0): ("length of postoperative hospital stay", 30.2),
    ("b", 1): ("time to resuming diet", 26.5),
    ("b", 2): ("time to ambulation", 42.8),
    ("c", 1): ("VAS pain score, POD 2", 50.8),
    ("c", 2): ("VAS pain score, POD 3", 64.9),
}
TOLERANCE_PP = 2.0
PANEL_BY_BASELINE = {183.0: "a", 343.3: "b", 499.5: "c"}


def extract() -> dict:
    import pymupdf
    pg = pymupdf.open(PDF)[PAGE]

    def arm_of(fill):
        if fill == BLACK:
            return "TEA"
        return "sham" if fill in GREYS else None

    bars, verticals = [], []
    for d in pg.get_drawings():
        a = arm_of(d.get("fill"))
        for it in d["items"]:
            if it[0] == "re" and a and it[1].width >= 10 and it[1].height >= 8:
                r = it[1]
                bars.append({"arm": a, "x": (r.x0 + r.x1) / 2,
                             "top": r.y0, "base": r.y1})
            elif it[0] == "l":
                p1, p2 = it[1], it[2]
                if abs(p1.x - p2.x) < 0.6 and abs(p1.y - p2.y) > 1.5:
                    verticals.append({"x": p1.x, "y0": min(p1.y, p2.y),
                                      "y1": max(p1.y, p2.y)})

    # An outlined (unfilled) bar shows up as two parallel edges sharing a
    # baseline. POD 2 TEA is drawn that way; recover it rather than lose it.
    bases = {round(b["base"], 1) for b in bars}
    by_base_len: dict = {}
    for v in verticals:
        b = round(v["y1"], 1)
        if b in bases and v["y1"] - v["y0"] > 20:
            by_base_len.setdefault((b, round(v["y0"], 1)), []).append(v["x"])
    for (base, top), xs in by_base_len.items():
        if len(xs) == 2 and abs(xs[0] - xs[1]) > 10:
            bars.append({"arm": "TEA", "x": sum(xs) / 2, "top": top,
                         "base": base, "outlined": True})

    words = pg.get_text("words")
    panels = {}
    for b in bars:
        panels.setdefault(round(b["base"], 1), []).append(b)

    out = {}
    for base, bs in sorted(panels.items()):
        bs.sort(key=lambda b: b["x"])
        left = min(b["x"] for b in bs)
        ticks = sorted(((float(w[4]), (w[1] + w[3]) / 2) for w in words
                        if w[4].isdigit() and base - 160 < (w[1] + w[3]) / 2 < base + 6
                        and left - 45 < w[0] < left - 4), key=lambda t: t[1])
        # Keep only a strictly descending run of tick VALUES down the axis. A
        # neighbouring panel's "0" can fall inside the x/y window and, left in,
        # it corrupts the reported residual (panel c read 6.52 instead of 0.009)
        # even though the median-slope fit itself shrugs it off.
        # Longest such run, not the first: panel c's stray tick sorts FIRST, so
        # anchoring on it discarded the entire real axis behind it.
        best = []
        for start in range(len(ticks)):
            run = [ticks[start]]
            for v, y in ticks[start + 1:]:
                if v < run[-1][0]:
                    run.append((v, y))
            if len(run) > len(best):
                best = run
        ticks = best
        if len(ticks) < 3:
            continue
        slopes = [(ticks[i][0] - ticks[j][0]) / (ticks[j][1] - ticks[i][1])
                  for i in range(len(ticks)) for j in range(i + 1, len(ticks))]
        m = statistics.median(slopes)
        resid = max(abs(v - m * (base - y)) for v, y in ticks)
        # Judge the residual against the axis it sits on: 0.42 units is poor on a
        # 0-5 VAS axis and excellent on a 0-150 hour axis. An absolute threshold
        # would have rejected a panel that is calibrated to 0.28%.
        axis_range = max(v for v, _ in ticks) - min(v for v, _ in ticks)
        resid_pct = 100 * resid / axis_range if axis_range else float("inf")
        for b in bs:
            b["value"] = m * (base - b["top"])
            whisk = [v for v in verticals
                     if abs(v["x"] - b["x"]) < 1.2 and abs(v["y1"] - b["top"]) < 1.5]
            b["se"] = m * (whisk[0]["y1"] - whisk[0]["y0"]) if whisk else None
            b["sd"] = b["se"] * (N_PER_ARM ** 0.5) if b["se"] is not None else None
        out[PANEL_BY_BASELINE.get(base, str(base))] = {
            "baseline_y": base, "units_per_point": m,
            "ticks": [t[0] for t in ticks], "max_tick_residual": resid,
            "max_tick_residual_pct_of_axis": resid_pct,
            "bars": bs,
        }
    return out


def validate(panels: dict) -> list[dict]:
    rows = []
    for pname, p in panels.items():
        pairs = [p["bars"][i:i + 2] for i in range(0, len(p["bars"]) - 1, 2)]
        for idx, pair in enumerate(pairs):
            key = REPORTED.get((pname, idx))
            sham = next((b for b in pair if b["arm"] == "sham"), None)
            tea = next((b for b in pair if b["arm"] == "TEA"), None)
            if not (sham and tea):
                continue
            got = 100 * (1 - tea["value"] / sham["value"])
            row = {"panel": pname, "pair": idx,
                   "outcome": key[0] if key else "(not reported as a percentage)",
                   "sham_mean": round(sham["value"], 3), "tea_mean": round(tea["value"], 3),
                   "sham_se": round(sham["se"], 3) if sham["se"] else None,
                   "tea_se": round(tea["se"], 3) if tea["se"] else None,
                   "sham_sd": round(sham["sd"], 3) if sham["sd"] else None,
                   "tea_sd": round(tea["sd"], 3) if tea["sd"] else None,
                   "digitized_reduction_pct": round(got, 2),
                   "reported_reduction_pct": key[1] if key else None}
            if key:
                row["abs_error_pp"] = round(abs(got - key[1]), 2)
                row["validates"] = row["abs_error_pp"] <= TOLERANCE_PP
            rows.append(row)
    return rows


def main(as_json: bool) -> int:
    panels = extract()
    rows = validate(panels)
    payload = {"source": str(PDF.relative_to(ROOT)), "page": PAGE + 1,
               "n_per_arm": N_PER_ARM, "tolerance_pp": TOLERANCE_PP,
               "calibration": {k: {"ticks": v["ticks"],
                                   "units_per_point": round(v["units_per_point"], 6),
                                   "max_tick_residual": round(v["max_tick_residual"], 4),
                                   "max_tick_residual_pct_of_axis": round(v["max_tick_residual_pct_of_axis"], 4)}
                               for k, v in panels.items()},
               "results": rows}
    if as_json:
        print(json.dumps(payload, indent=2))
        return 0
    for k, v in payload["calibration"].items():
        print(f"panel {k}: ticks {v['ticks']}  units/pt {v['units_per_point']}  "
              f"max residual {v['max_tick_residual']} "
              f"({v['max_tick_residual_pct_of_axis']}% of axis)")
    print()
    hdr = f"{'outcome':38s} {'sham':>8s} {'TEA':>8s} {'dig%':>7s} {'rep%':>7s} {'err pp':>7s}  ok"
    print(hdr); print("-" * len(hdr))
    for r in rows:
        print(f"{r['outcome'][:38]:38s} {r['sham_mean']:8.3f} {r['tea_mean']:8.3f} "
              f"{r['digitized_reduction_pct']:7.2f} "
              f"{(r['reported_reduction_pct'] if r['reported_reduction_pct'] is not None else float('nan')):7.2f} "
              f"{r.get('abs_error_pp', float('nan')):7.2f}  {r.get('validates','-')}")
    checked = [r for r in rows if "validates" in r]
    print(f"\n{sum(r['validates'] for r in checked)}/{len(checked)} reported reductions "
          f"reproduced within {TOLERANCE_PP} pp")
    return 0


if __name__ == "__main__":
    sys.exit(main("--json" in sys.argv))

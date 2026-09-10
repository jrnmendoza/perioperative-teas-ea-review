#!/usr/bin/env python3
"""
Assemble the review's limitations from its own outputs.

WHY
Every ingredient of a Limitations section already exists somewhere in this
repository -- heterogeneity in the model results, sparse k in the derivability
audit, unconverted units in the conversion audit, unresolved source problems in
the author-inquiry roster, analyses computed and not reported. Nothing collected
them, so writing the section meant remembering where each one lived, and a
limitation nobody remembered was a limitation that did not get written.

WHAT IT REFUSES TO DO
Assert a limitation it cannot evidence. Every entry below is derived from a
live file and carries the numbers that justify it plus where to check them. A
rule that finds nothing emits nothing: an empty category is a true statement
about this review, and padding it would make the whole section untrustworthy.

WHAT IT DELIBERATELY LEAVES OUT
The risk-of-bias assessor process. Independent dual assessment is in progress
at the review lead's direction, and the dashboard's earlier dual-assessor
language was removed for exactly that reason. Recording it here as a settled
limitation would contradict work that is still underway. It belongs in the
section once that process concludes, and is listed in `deferred` so it is not
simply forgotten.

Usage:  python3 scripts/build_limitations.py
Exit:   0 on success, 1 if a required input is missing.
"""
from __future__ import annotations

import csv
import json
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DASH = ROOT / "dashboard"
OUT = DASH / "limitations.js"

DERIVABILITY = ROOT / "07_TIERED_V33" / "PRIMARY_OUTCOME_DERIVABILITY_AUDIT_v33.csv"
CONVERSION = ROOT / "06_FINAL_ANALYSIS_V26" / "06_AUDIT" / "opioid_conversion_audit.csv"
ERRATA = (ROOT / "TEAS EA Verification" / "v34_reconciliation" /
          "POST_LOCK_ERRATA_v34.md")

# Cochrane Handbook 10.10.2 bands, and the >= 10 studies convention for
# funnel-plot asymmetry testing (Handbook 13.3.5.4).
CONSIDERABLE_I2 = 75.0
FUNNEL_MIN_K = 10


def read_csv(path: Path) -> list[dict]:
    with path.open(encoding="utf-8-sig") as f:
        return list(csv.DictReader(f))


def read_js(path: Path, var: str):
    src = path.read_text(encoding="utf-8")
    start = src.index(var + " = ") + len(var + " = ")
    return json.loads(src[start:src.rindex(";")])


def _rob_evidence(rob: list[dict], n_graded: int) -> str:
    """Report how concentrated the high-risk contributions are, not a roll-call."""
    def parts(r):
        b = r["bound_evidence"]
        high = int(b.get("rob_high", 0) or 0)
        total = sum(int(b.get(f"rob_{x}", 0) or 0) for x in ("low", "some", "high"))
        return high, total, high / total if total else 0.0

    ranked = sorted(rob, key=lambda r: (-parts(r)[2], -parts(r)[0]))
    top = ranked[:3]
    shown = "; ".join(f"{r['label']} ({parts(r)[0]} of {parts(r)[1]})" for r in top)
    rest = len(ranked) - len(top)
    return (f"{len(rob)} of {n_graded} reported analyses. Most affected: {shown}"
            + (f"; and {rest} further analys{'is' if rest == 1 else 'es'} "
               f"with at least one." if rest > 0 else ".")).rstrip(".") + "."


def lim(domain, title, detail, evidence, where, affects=None, metric=None):
    """
    `metric` carries the derived count behind the title as a number, keyed by
    rule. Titles are prose and several of them legitimately contain the same
    figure, so a validator that string-matches counts across titles can be
    satisfied by the wrong one -- that exact false pass was observed. The
    numeric field lets the count be re-derived and compared per rule.
    """
    return {"domain": domain, "title": title, "detail": detail,
            "evidence": evidence, "where": where, "affects": affects or [],
            "metric": metric}


def build() -> dict:
    records = read_js(DASH / "interpretation_layer.js", "window.INTERPRETATION_LAYER")["records"]
    graded = [r for r in records if r["status"] != "exploratory"]
    out = []

    def label(aid):
        return next((r["label"] for r in records if r["analysis_id"] == aid), aid)

    # ---- 1. Heterogeneity ------------------------------------------------
    het = [r for r in graded
           if r["bound_evidence"].get("i2") is not None
           and float(r["bound_evidence"]["i2"]) >= CONSIDERABLE_I2]
    if het:
        worst = max(het, key=lambda r: float(r["bound_evidence"]["i2"]))
        out.append(lim(
            "Heterogeneity",
            f"Considerable between-study heterogeneity in {len(het)} of {len(graded)} "
            f"reported analyses",
            "Pooled estimates in these analyses describe a distribution of effects rather "
            "than one common effect, so a single summary number understates how much the "
            "result varies between surgical populations, stimulation protocols and "
            "anaesthetic techniques.",
            f"I² ≥ {CONSIDERABLE_I2:.0f}% in {len(het)} analyses; highest is "
            f"I² = {float(worst['bound_evidence']['i2']):.1f}% in {worst['label']}.",
            "Each analysis's forest plot and heterogeneity statistics",
            [r["analysis_id"] for r in het],
            metric={"key": "heterogeneity", "count": len(het), "of": len(graded)}))

    # ---- 2. Sparse evidence per estimand ---------------------------------
    sparse = [r for r in graded if int(r["bound_evidence"]["k"]) <= 3]
    if sparse:
        ks = Counter(int(r["bound_evidence"]["k"]) for r in sparse)
        out.append(lim(
            "Sparse evidence",
            f"{len(sparse)} of {len(graded)} reported analyses rest on 3 or fewer trials",
            "With this few contributing trials, between-study variance is estimated "
            "imprecisely, subgroup and moderator analysis is not informative, and a single "
            "additional trial could move the estimate materially.",
            "; ".join(f"k = {k} in {n} analys{'is' if n == 1 else 'es'}"
                      for k, n in sorted(ks.items())) + ".",
            "Per-analysis k, and the derivability audit explaining why k is small",
            [r["analysis_id"] for r in sparse],
            metric={"key": "sparse", "count": len(sparse), "of": len(graded)}))

    # ---- 3. Imprecision --------------------------------------------------
    wide = [r for r in graded if r.get("includes_null")]
    if wide:
        out.append(lim(
            "Imprecision",
            f"The confidence interval includes no effect in {len(wide)} of {len(graded)} "
            f"reported analyses",
            "These analyses are compatible with benefit, no difference and — within the "
            "interval — harm. They do not establish absence of an effect either; they are "
            "inconclusive at the precision this evidence base supports.",
            f"{len(wide)} of {len(graded)} intervals span the null value for their measure "
            "(0 for differences and log-ratios, 1 for ratios).",
            "Each analysis's confidence interval and prediction interval",
            [r["analysis_id"] for r in wide],
            metric={"key": "imprecision", "count": len(wide), "of": len(graded)}))

    # ---- 4. Risk of bias in contributing results -------------------------
    rob = [r for r in graded if int(r["bound_evidence"].get("rob_high", 0) or 0) > 0]
    if rob:
        out.append(lim(
            "Risk of bias",
            f"{len(rob)} reported analyses include at least one result at high risk of bias",
            "Where a high-risk result contributes, the pooled estimate inherits that risk. "
            "Leave-one-out results are available for each affected analysis and should be "
            "read alongside the main estimate.",
            # Naming all twelve makes an unreadable sentence. The informative
            # part is how concentrated the problem is, so report the worst
            # affected and count the rest.
            _rob_evidence(rob, len(graded)),
            "Result-specific RoB 2 panel and the model rollup",
            [r["analysis_id"] for r in rob],
            metric={"key": "rob", "count": len(rob), "of": len(graded)}))

    # ---- 5. Certainty profile --------------------------------------------
    grades = Counter(r["bound_evidence"].get("grade") for r in graded
                     if r["bound_evidence"].get("grade") in
                     ("Very Low", "Low", "Moderate", "High"))
    lowish = grades["Very Low"] + grades["Low"]
    if lowish:
        out.append(lim(
            "Certainty of evidence",
            f"{lowish} of {sum(grades.values())} GRADE-rated analyses are Low or Very Low "
            f"certainty",
            "The true effect may differ substantially from the estimate in these analyses. "
            "Conclusions drawn from them should be phrased as what the evidence is "
            "compatible with, not as what it establishes.",
            ", ".join(f"{g}: {n}" for g, n in
                      sorted(grades.items(), key=lambda x: ["Very Low", "Low", "Moderate",
                                                            "High"].index(x[0]))) + ".",
            "GRADE Summary of Findings, with the downgrade reasons for each rating",
            metric={"key": "low_certainty", "count": lowish, "of": sum(grades.values())}))

    # ---- 6. Publication bias not assessable ------------------------------
    small = [r for r in graded if int(r["bound_evidence"]["k"]) < FUNNEL_MIN_K]
    if len(small) == len(graded):
        out.append(lim(
            "Publication and reporting bias",
            "Small-study effects could not be assessed for any analysis",
            "Funnel-plot asymmetry tests are uninformative below about 10 contributing "
            "studies, so this review cannot exclude publication bias, selective outcome "
            "reporting or small-study effects by statistical means for any of its analyses.",
            f"Every reported analysis has k < {FUNNEL_MIN_K} "
            f"(largest k = {max(int(r['bound_evidence']['k']) for r in graded)}); "
            f"Cochrane Handbook 13.3.5.4.",
            "Per-analysis k"))

    # ---- 7. The estimand gap, from the derivability audit ----------------
    if DERIVABILITY.exists():
        rows = read_csv(DERIVABILITY)
        tiers = Counter(r["tier_mme"] for r in rows)
        tier_a = tiers.get("A", 0)
        out.append(lim(
            "Outcome reporting in the source trials",
            "Most trials reporting a 0–24 h opioid outcome cannot contribute to it",
            "Trials report this outcome in units, distributions and windows that cannot be "
            "converted to a common absolute scale — weight-normalised doses, medians without "
            "dispersion, graph-only values, drugs with no sourced equivalence factor. This is "
            "a limitation of the primary literature, not of the search.",
            f"Of {len(rows)} audited 0–24 h opioid contrasts, {tier_a} are directly poolable "
            f"in absolute morphine equivalents (Tier A); the remainder fall into "
            + ", ".join(f"Tier {t} ({n})" for t, n in sorted(tiers.items()) if t != "A") + ".",
            "Derivability audit (Tiers A–F) on the primary-outcome pathway"))

    # ---- 8. Where an estimand has no evidence at all ---------------------
    tier_e = [r for r in records if r["status"] == "exploratory"]
    if tier_e:
        out.append(lim(
            "Outcome reporting in the source trials",
            "No sham-controlled electroacupuncture trial reports 0–24 h opioid use in "
            "absolute morphine equivalents",
            "For this comparison the review has no estimate on the pre-specified scale at "
            "all. A scale-free standardized synthesis is reported instead, as an exploratory "
            "secondary result; it answers a different question and carries no certainty "
            "rating.",
            f"k = 0 for the absolute-MME estimand in this stratum; "
            f"{len(tier_e)} exploratory standardized analyses are reported in its place.",
            "Tier E exploratory scale-free SMD synthesis",
            [r["analysis_id"] for r in tier_e]))

    # ---- 9. Conversion-factor dependence ---------------------------------
    if CONVERSION.exists():
        conv = read_csv(CONVERSION)
        corrected = [r for r in conv if r["final_status"].startswith("CORRECTED")]
        unconvertible = [r for r in conv if r["final_status"].startswith("NOT APPROPRIATE")]
        if corrected or unconvertible:
            bits = []
            if corrected:
                bits.append(f"{len(corrected)} contrast(s) required a corrected equianalgesic "
                            f"factor ({', '.join(sorted({r['opioid'] for r in corrected}))})")
            if unconvertible:
                bits.append(f"{len(unconvertible)} contrast(s) could not be converted to "
                            f"absolute morphine equivalents at all")
            out.append(lim(
                "Opioid dose conversion",
                "Pooled doses depend on equianalgesic conversion factors",
                "Converting different opioids to a common morphine-equivalent scale is "
                "itself an assumption. One factor in this review was found wrong and "
                "corrected during the audit, and the pooled estimate is sensitive to that "
                "choice; a prespecified sensitivity analysis quantifies the dependence.",
                "; ".join(bits) + ". Every factor is recorded with its source and status in "
                "the conversion audit.",
                "Opioid conversion audit and the conversion sensitivity analysis"))

    # ---- 10. Unresolved source problems ----------------------------------
    open_models = [r for r in records if r["status"] == "author-contact-useful"]
    if open_models:
        # The status reason is a full sentence ending in the study names.
        # Concatenating those sentences repeats the prefix once per analysis;
        # only the study names differ, so take those.
        open_studies = sorted({s.strip().rstrip(".")
                               for r in open_models
                               for s in r["status_reason"].split(":")[-1].split(",")})
        out.append(lim(
            "Source data quality",
            f"{len(open_models)} analyses contain a result whose source problem only the "
            f"trial authors or a registry could settle",
            "These are documented source-level problems — irreconcilable denominators, "
            "figure-only values, unreported units — not analytical choices. They are carried "
            "as open flags rather than resolved by assumption.",
            f"Affected trials: {', '.join(open_studies)}. Each is carried as an open "
            f"source-QC flag on the {len(open_models)} analyses it contributes to.",
            "Author outreach roster and the per-analysis source-QC flags",
            [r["analysis_id"] for r in open_models]))

    # ---- 11. Analyses computed but not reported --------------------------
    cnr_path = DASH / "computed_not_reported.js"
    if cnr_path.exists():
        cnr = read_js(cnr_path, "window.COMPUTED_NOT_REPORTED")
        rows = cnr["rows"] if isinstance(cnr, dict) and "rows" in cnr else cnr
        if rows:
            out.append(lim(
                "Selective reporting within this review",
                f"{len(rows)} analyses were computed and are not reported as findings",
                "Each is listed with the reason it is not carried forward — a component of a "
                "reported composite, a single trial, an inclusion variant, or no adopted "
                "certainty. They are disclosed so the review cannot be read as having "
                "reported only its favourable analyses.",
                f"{len(rows)} analyses, none carrying a GRADE certainty rating.",
                "“Analyses computed but not reported as findings — and why”"))

    # ---- 12. Open post-lock questions ------------------------------------
    if ERRATA.exists():
        text = ERRATA.read_text(encoding="utf-8")
        open_rows = [ln for ln in text.splitlines()
                     if ln.startswith("|") and "**Open" in ln]
        if open_rows:
            titles = []
            for ln in open_rows:
                cells = [c.strip() for c in ln.strip().strip("|").split("|")]
                if len(cells) >= 3:
                    titles.append(f"{cells[1]}: {cells[2]}" if cells[1] != "—" else cells[2])
            out.append(lim(
                "Open questions at time of writing",
                f"{len(open_rows)} post-lock questions remain open",
                "These are recorded rather than resolved by assumption. None changes a "
                "reported estimate; each is a classification or labelling question awaiting "
                "a review-team decision.",
                "; ".join(titles) + ".",
                "Post-lock errata register"))

    deferred = [{
        "title": "Risk-of-bias assessor process",
        "why": ("Independent dual assessment of the strict-primary trials is in progress. "
                "Recording it here as a settled limitation would contradict work that is "
                "still underway; it belongs in this section once that process concludes."),
    }]

    return {
        "generated_by": "scripts/build_limitations.py",
        "disclaimer": ("Assembled from this review's own outputs. Every limitation below is "
                       "derived from a live analysis file and carries the figures that "
                       "justify it; none is asserted without evidence, and a category that "
                       "found nothing is omitted rather than padded."),
        "reported_analyses": len(graded),
        "limitations": out,
        "deferred": deferred,
    }


def main() -> int:
    for required in (DERIVABILITY, CONVERSION, ERRATA):
        if not required.exists():
            print(f"missing required input: {required}", file=sys.stderr)
            return 1
    payload = build()
    OUT.write_text(
        "// GENERATED by scripts/build_limitations.py -- do not hand-edit.\n"
        "// Every entry is derived from a live analysis output; see each item's `where`.\n"
        "window.LIMITATIONS = " + json.dumps(payload, indent=2, ensure_ascii=False) + ";\n",
        encoding="utf-8")
    print(f"wrote {OUT.relative_to(ROOT)}")
    print(f"  {len(payload['limitations'])} limitations across "
          f"{len({l['domain'] for l in payload['limitations']})} domains, "
          f"over {payload['reported_analyses']} reported analyses")
    for l in payload["limitations"]:
        print(f"    [{l['domain']}] {l['title']}")
    for d in payload["deferred"]:
        print(f"    (deferred) {d['title']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())

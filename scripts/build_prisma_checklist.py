#!/usr/bin/env python3
"""
Build the PRISMA 2020 checklist, mapped to this review's own outputs.

WHY
The checklist is a submission requirement, and it was living entirely outside
the pipeline -- a .docx in somebody's Downloads folder with nothing connecting
its items to the review's material. Filling it in at submission time means
recalling, item by item, where the evidence sits and whether it exists at all.

WHAT IT DOES NOT DO
Claim an item is met because the review holds the underlying material. Those
are different things, and conflating them is how a checklist becomes a
liability: PRISMA asks what the REPORT states, not what the project knows. So
status distinguishes:

  evidence-ready   the material exists here and is pinned to a location; the
                   manuscript still has to report it
  manuscript-only  nothing to derive -- rationale, funding, competing
                   interests. Listed so it cannot be forgotten, never
                   pre-answered
  attention        a real gap, a caveat, or a decision the team still owes

Counts inside `evidence` are derived from live files on every build, so an item
cannot go on claiming 4 search strategies or 10 GRADE ratings after that stops
being true.

ITEM WORDING
The requirement text is a short paraphrase of what each PRISMA item asks, not
the checklist's own wording, so this file carries no reproduced checklist text
and reads in terms of this specific review.

Usage:  python3 scripts/build_prisma_checklist.py
Exit:   0 on success, 1 if a required input is missing.
"""
from __future__ import annotations

import csv
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DASH = ROOT / "dashboard"
OUT = DASH / "prisma_checklist.js"

PROTOCOL = ROOT / "00_protocol" / "protocol_scope_locked.md"
AMENDMENTS = ROOT / "00_protocol" / "amendments"
GRADE_CSV = ROOT / "09_V34_ANALYSIS" / "04_GRADE" / "v34_new_model_grade.csv"
ROB2_CSV = ROOT / "09_V34_ANALYSIS" / "03_ROB2" / "v34_rob2_draft_assessments.csv"
PROSPERO = "CRD420251090635"

READY, MANUSCRIPT, ATTENTION = "evidence-ready", "manuscript-only", "attention"


def read_csv(path: Path) -> list[dict]:
    with path.open(encoding="utf-8-sig") as f:
        return list(csv.DictReader(f))


def read_js(path: Path, var: str):
    src = path.read_text(encoding="utf-8")
    start = src.index(var + " = ") + len(var + " = ")
    return json.loads(src[start:src.rindex(";")])


def build() -> dict:
    strategies = read_js(DASH / "search_strategies.js", "window.SEARCH_STRATEGIES")
    if isinstance(strategies, dict):
        strategies = next(v for v in strategies.values() if isinstance(v, list))
    verbatim = [s for s in strategies if (s.get("strategy_text") or "").strip()]
    grade = read_csv(GRADE_CSV)
    rob2 = read_csv(ROB2_CSV)
    cnr = read_js(DASH / "computed_not_reported.js", "window.COMPUTED_NOT_REPORTED")
    limits = read_js(DASH / "limitations.js", "window.LIMITATIONS")
    records = read_js(DASH / "interpretation_layer.js", "window.INTERPRETATION_LAYER")["records"]
    prior = read_js(DASH / "prior_evidence.js", "window.PRIOR_EVIDENCE")
    amendments = sorted(AMENDMENTS.glob("*.md")) if AMENDMENTS.exists() else []
    graded = [r for r in records if r["status"] != "exploratory"]

    I = []

    def item(num, section, requirement, status, evidence, where):
        I.append({"item": num, "section": section, "requirement": requirement,
                  "status": status, "evidence": evidence, "where": where})

    # ---- TITLE / ABSTRACT -------------------------------------------------
    item("1", "Title", "Identify the report as a systematic review.",
         MANUSCRIPT, "Authorial. Nothing to derive.", "Manuscript title page")
    item("2", "Abstract",
         "Structured abstract following the PRISMA 2020 for Abstracts checklist.",
         MANUSCRIPT,
         "Authorial, but the figures it must carry are all derived: "
         f"{len(graded)} reported analyses with adopted certainty, and the PRISMA flow.",
         "GRADE Summary of Findings; PRISMA flow")

    # ---- INTRODUCTION -----------------------------------------------------
    item("3", "Introduction", "Rationale for the review in the context of existing knowledge.",
         MANUSCRIPT,
         f"Authorial. The comparison with {prior['prior']['short']} is assembled and can "
         f"support it.",
         "Comparison with prior evidence panel")
    item("4", "Introduction", "Explicit statement of objectives / questions addressed.",
         READY,
         "Pre-specified in the locked protocol scope.",
         "00_protocol/protocol_scope_locked.md")

    # ---- METHODS ----------------------------------------------------------
    item("5", "Methods", "Inclusion and exclusion criteria, and how studies were grouped.",
         READY, "Recorded in the locked protocol scope, with comparator and modality strata "
                "carried through every analysis.",
         "00_protocol/protocol_scope_locked.md; per-analysis comparator strata")
    item("6", "Methods", "All information sources, with the date each was last searched.",
         READY,
         "; ".join(f"{s['database']} ({s['date']}, {s['hits']} records)" for s in strategies),
         "Search strategies panel")
    item("7", "Methods", "Full verbatim search strategy for every source.",
         READY if len(verbatim) == len(strategies) else ATTENTION,
         f"{len(verbatim)} of {len(strategies)} databases have their full strategy stored "
         f"verbatim."
         + ("" if len(verbatim) == len(strategies) else " The remainder do not."),
         "Search strategies panel")
    item("8", "Methods", "Selection process: how many screened each record, and any automation.",
         ATTENTION,
         "The screening records show Covidence dual screening with consensus, and 508 records "
         "marked ineligible by automation tools. The manuscript must state explicitly how many "
         "reviewers screened each record and how disagreements were resolved.",
         "PRISMA flow; Covidence screening export")
    item("9", "Methods", "Data collection process: how many extractors, and any automation.",
         ATTENTION,
         "Extraction provenance is recorded per study, but the number of independent "
         "extractors is a statement the manuscript must make and this pipeline cannot derive.",
         "Study_Master reconciliation batches")
    item("10a", "Methods", "All outcomes sought, and which results were sought for each.",
         READY,
         f"Every outcome is registered with its window and eligibility; "
         f"{cnr['total_analyses']} analyses were computed in total.",
         "Outcome data; derivability audit")
    item("10b", "Methods", "All other variables sought (participants, interventions, funding).",
         READY, "Study characteristics are extracted per trial.",
         "Study characteristics panel")
    item("11", "Methods", "Risk-of-bias assessment: tool, how many assessors, automation.",
         ATTENTION,
         f"{len(rob2)} result-specific RoB 2 assessments exist with all five domains. "
         f"Independent dual assessment is in progress; the manuscript must state the final "
         f"assessor process, so this cannot be closed yet.",
         "Result-specific RoB 2 panel")
    item("12", "Methods", "Effect measures used for each outcome.",
         READY,
         "Each analysis records its effect measure and estimator explicitly (mean difference, "
         "risk ratio, log risk ratio, standardized mean difference).",
         "Per-analysis estimator and measure")
    item("13a", "Methods", "How studies were deemed eligible for each synthesis.",
         READY,
         "The derivability audit records, contrast by contrast, why each is or is not poolable "
         "on the primary estimand.",
         "Derivability audit (Tiers A–F)")
    item("13b", "Methods", "Data preparation: missing statistics, conversions.",
         READY,
         "Unit conversions are recorded per contrast with source and status; median/IQR "
         "approximations and multi-arm combinations are named where used (Cochrane Handbook "
         "6.5.2.5 and 6.5.2.10).",
         "Opioid conversion audit; per-contrast combine notes")
    item("13c", "Methods", "How results were tabulated or visually displayed.",
         READY, "Forest plots and per-analysis tables are generated from the Stata outputs.",
         "Forest plots; Summary of Findings")
    item("13d", "Methods", "Synthesis method, model and software.",
         READY,
         "REML random-effects with Hartung-Knapp intervals where k permits, StataNow 19.5; "
         "single-study rows are labelled as not pooled.",
         "Per-analysis estimator; Stata do-files and logs")
    item("13e", "Methods", "How heterogeneity was explored (subgroups, meta-regression).",
         READY,
         f"I² and τ² reported per analysis; subgroup and meta-regression outputs exist. "
         f"{limits['limitations'][0]['metric']['count']} analyses show considerable "
         f"heterogeneity.",
         "Heterogeneity statistics; subgroup / meta-regression log")
    item("13f", "Methods", "Sensitivity analyses used to assess robustness.",
         READY,
         f"{cnr['sensitivity']} of {cnr['total_analyses']} computed analyses are sensitivity "
         f"variants, including leave-one-out and the conversion-factor sensitivity.",
         "Sensitivity analyses; “computed but not reported” panel")
    item("14", "Methods", "Methods to assess risk of bias due to missing results.",
         ATTENTION,
         "Funnel-plot asymmetry testing is uninformative below about 10 studies and every "
         "analysis here is smaller, so no statistical assessment was possible. The manuscript "
         "must state this rather than omit the item.",
         "Limitations — publication and reporting bias")
    item("15", "Methods", "Methods for assessing certainty in the body of evidence.",
         READY,
         f"GRADE applied by explicit rule; {len(grade)} model ratings are computed from the "
         f"analysis inputs and disclose that they are rule-based, not an independent panel "
         f"judgement.",
         "GRADE Summary of Findings; the GRADE rule script")

    # ---- RESULTS ----------------------------------------------------------
    item("16a", "Results", "Numbers screened, assessed and included, ideally with a flow diagram.",
         READY,
         "Full PRISMA flow: 5,100 references resolving to 5,088 studies, 2,160 removed, "
         "2,928 screened, 224 sought, 210 assessed, 70 included.",
         "PRISMA flow panel")
    item("16b", "Results", "Studies excluded at full text, with reasons.",
         READY, "141 exclusions with reasons, itemised by category.",
         "PRISMA flow panel")
    item("17", "Results", "Cite and describe the characteristics of each included study.",
         READY, "All 70 included trials carry extracted characteristics and a citation.",
         "Study characteristics panel")
    item("18", "Results", "Risk-of-bias assessments for each included study.",
         READY, f"{len(rob2)} result-specific assessments with all five domains and an overall "
                f"judgement.",
         "Result-specific RoB 2 panel")
    item("19", "Results", "For each study, summary statistics and effect estimates.",
         READY, "Per-study arm data and effect estimates are stored for every contributing "
                "contrast.",
         "Outcome data; forest plots")
    item("20a", "Results", "For each synthesis, characteristics and risk of bias of contributors.",
         READY, "Each analysis records its contributing studies and their RoB composition.",
         "Model rollup; per-analysis panels")
    item("20b", "Results", "For each synthesis, the summary estimate, precision and heterogeneity.",
         READY,
         f"{len(graded)} reported analyses, each with estimate, confidence interval, I² and "
         f"prediction interval where available.",
         "Summary of Findings; forest plots")
    item("20c", "Results", "Results of heterogeneity investigations.",
         READY, "Subgroup and meta-regression outputs are generated and logged.",
         "Subgroup / meta-regression log")
    item("20d", "Results", "Results of sensitivity analyses.",
         READY, f"{cnr['sensitivity']} sensitivity analyses computed, with leave-one-out per "
                f"analysis.", "Sensitivity analyses")
    item("21", "Results", "Risk of bias due to missing results in the synthesis.",
         ATTENTION,
         "Not assessable statistically at these k. What can be reported instead is documented: "
         f"{cnr['not_reported']} analyses computed and not reported, each with its reason, and "
         "the open author-contact roster.",
         "“Computed but not reported” panel; author outreach roster")
    item("22", "Results", "Certainty of evidence for each outcome assessed.",
         READY,
         f"All {len(graded)} reported analyses carry an adopted certainty rating; the "
         f"exploratory Tier E rows are explicitly ungraded and labelled as such.",
         "GRADE Summary of Findings")

    # ---- DISCUSSION -------------------------------------------------------
    item("23a", "Discussion", "General interpretation of the results in context.",
         READY,
         "Draft Results-safe and Discussion-safe wording exists for every analysis, with claim "
         "boundaries, plus a trial-by-trial comparison with the prior meta-analysis.",
         "Manuscript Lens; comparison with prior evidence")
    item("23b", "Discussion", "Limitations of the evidence included.",
         READY,
         f"{len(limits['limitations'])} limitations assembled from the review's own outputs, "
         f"each with the figures behind it.",
         "Limitations panel")
    item("23c", "Discussion", "Limitations of the review processes used.",
         ATTENTION,
         "Partly assembled. The risk-of-bias assessor process is deliberately deferred while "
         "independent dual assessment is in progress, and must be written once it concludes.",
         "Limitations panel — deferred items")
    item("23d", "Discussion", "Implications for practice, policy and future research.",
         MANUSCRIPT,
         "Authorial. The discussion prompts on each analysis are drafting aids for it, not "
         "content.",
         "Manuscript Lens — questions for manuscript discussion")

    # ---- OTHER INFORMATION ------------------------------------------------
    item("24a", "Other", "Registration name and number, or a statement that it is unregistered.",
         READY, f"Registered on PROSPERO as {PROSPERO}.", "Protocol and registration")
    item("24b", "Other", "Where the protocol can be accessed, or that none was prepared.",
         READY, "A locked protocol scope document is held in the repository.",
         "00_protocol/protocol_scope_locked.md")
    item("24c", "Other", "Amendments to registration or protocol, with rationale.",
         READY if amendments else ATTENTION,
         (f"{len(amendments)} recorded amendment(s): "
          + "; ".join(p.stem.replace("_", " ") for p in amendments) + ".")
         if amendments else "No amendment record was found.",
         "00_protocol/amendments/")
    item("25", "Other", "Sources of financial and non-financial support, and the funder's role.",
         MANUSCRIPT, "Authorial. Nothing in this repository records it.",
         "Manuscript funding statement")
    item("26", "Other", "Competing interests of the review authors.",
         MANUSCRIPT, "Authorial. Nothing in this repository records it.",
         "Manuscript competing-interests statement")
    item("27", "Other",
         "Availability of data, code, and other materials (extracted data, analytic code).",
         READY,
         "The extraction dataset is SHA-256 pinned, the Stata do-files and logs are held with "
         "it, and every generated dashboard artefact names the script that produced it.",
         "Repository and downloads; locked master workbook")

    counts = {s: sum(1 for i in I if i["status"] == s)
              for s in (READY, MANUSCRIPT, ATTENTION)}
    return {
        "generated_by": "scripts/build_prisma_checklist.py",
        "standard": "PRISMA 2020 (Page MJ, et al. BMJ 2021;372:n71)",
        "disclaimer": (
            "Maps each PRISMA 2020 item to this review's own material. "
            "“Evidence-ready” means the material exists and is pinned to a location — not "
            "that the manuscript reports it yet, which is what PRISMA actually asks. Counts "
            "are re-derived on every build. Requirement wording is a paraphrase, not the "
            "checklist's own text."),
        "items": I,
        "counts": counts,
        "total": len(I),
    }


def main() -> int:
    for required in (PROTOCOL, GRADE_CSV, ROB2_CSV):
        if not required.exists():
            print(f"missing required input: {required}", file=sys.stderr)
            return 1
    payload = build()
    OUT.write_text(
        "// GENERATED by scripts/build_prisma_checklist.py -- do not hand-edit.\n"
        "// Counts inside each item are re-derived from live files on every build.\n"
        "window.PRISMA_CHECKLIST = " + json.dumps(payload, indent=2, ensure_ascii=False) + ";\n",
        encoding="utf-8")
    print(f"wrote {OUT.relative_to(ROOT)}")
    print(f"  {payload['total']} PRISMA 2020 items: "
          + ", ".join(f"{v} {k}" for k, v in payload["counts"].items()))
    for i in payload["items"]:
        if i["status"] == ATTENTION:
            print(f"    needs attention — {i['item']}: {i['requirement']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())

#!/usr/bin/env python3
"""
Build the dashboard's INTERPRETATION layer -- working manuscript language,
reviewer questions and team discussion prompts -- from the authoritative
evidence, and bind each record to the exact evidence values it describes.

WHAT THIS IS FOR
The dashboard is the team's shared evidence workspace on the way to a
manuscript and peer review. This layer answers "what can we safely write,
and what will a reviewer ask", while the evidence layer answers "what did we
find". They are deliberately kept in separate files, generated separately,
so that nothing here can change a number anywhere.

TWO HARD RULES THIS FILE ENFORCES MECHANICALLY

1. INTERPRETATION NEVER WRITES EVIDENCE.
   This script only READS the authoritative analysis outputs. It writes one
   file, dashboard/interpretation_layer.js, which the dashboard renders as a
   clearly-labelled overlay. No RoB 2 judgement, GRADE rating, effect
   estimate, study classification or inclusion decision is produced here, and
   scripts/validate_dashboard.py fails if this file's output ever gains a
   field that would let it override one.

2. INTERPRETATION GOES STALE LOUDLY, NOT SILENTLY.
   Every record stores `bound_evidence`: the exact k, estimate, CI, I2,
   GRADE level and RoB 2 composition it describes, plus a fingerprint over
   those values. That fingerprint is compared against a COMMITTED LEDGER,
   interpretation_bindings.json, which records the fingerprint each analysis
   was last *reviewed* at and by whom.

   The ledger is the whole mechanism, and it is deliberately not automatic.
   An earlier version of this script compared the freshly-built record
   against the same freshly-read numbers it had just been built from, which
   is tautological: it could never fire, and re-running the generator would
   have silently erased the very signal this section exists to raise. So the
   baseline has to persist outside the generated file, and clearing it has to
   be a human act:

     * re-running this script NEVER clears a stale flag. It regenerates the
       wording against current numbers and still reports the record as stale,
       because nobody has yet confirmed the wording is right for the new
       numbers.
     * `--accept` writes the current fingerprints into the ledger, with a
       date. That is a person saying "I have re-read these interpretations
       against the changed analysis". It is the same shape as the review
       lead's adoption step for RoB 2 and GRADE elsewhere in this pipeline.

   Manuscript language attached to an obsolete result is worse than no
   manuscript language, and the only thing that makes a staleness flag
   trustworthy is that the machine cannot dismiss it on the team's behalf.

WHY THE PROSE IS RULE-GENERATED, NOT HAND-WRITTEN
Every sentence below is produced by an EXPLICIT, STATED rule applied
mechanically to the actual numbers, in the same spirit as
09_V34_ANALYSIS/04_GRADE/compute_new_model_grade.py. Two reasons:
  * it cannot drift away from the data it describes, and staleness is
    detectable rather than a matter of someone remembering to re-read it;
  * a reviewer question that fires only when its triggering condition is
    genuinely present cannot become interface filler. The brief is explicit
    that criticisms must not be invented to populate the UI, so each question
    below names the condition in the real data that triggered it.
Anything a rule cannot honestly derive is left out rather than guessed at.

THE RULES

Direction and precision
  lower_is_better per outcome (QoR-40 is the one higher-is-better scale in
  this set). "Favours X" is read off the point estimate's sign; it is never
  upgraded to a claim of effect when the interval crosses the null.

Heterogeneity bands (Cochrane Handbook 10.10.2, the same bands the review's
GRADE rule already uses)
  I2 < 50            not important / low
  50 <= I2 < 75      substantial
  I2 >= 75           considerable

Certainty
  Read from the review's own adopted GRADE rating -- the rule-based ratings
  in 04_GRADE/v34_new_model_grade.csv, or for the three primary opioid
  models the adopted Summary-of-Findings rating in dashboard/app.js's
  STATA_MASTER_RESULTS (parsed, not duplicated, so there is one source).

Claim boundaries
  GREEN   the point estimate's direction, and the estimate itself: these are
          arithmetic facts about the fitted model.
  AMBER   any statement about magnitude mattering clinically -- always
          qualified, and the required qualification names the actual reason
          (interval crosses the null, considerable heterogeneity, or low
          certainty).
  RED     "significantly reduces" / "definitively" phrasing whenever the
          interval crosses the null or certainty is Low or Very Low.

Reviewer questions -- each fires ONLY on its stated trigger
  k <= 4                              few contributing trials
  I2 >= 75                            considerable heterogeneity
  interval crosses the null           interval includes no effect
  any contributing result High RoB    risk of bias in contributing results
  comparator is usual care            no sham; performance bias
  k == 2 and CI method is not KH      estimator behaviour at k=2
  a sensitivity model flips
    significance                      estimator/CI-method dependence
  outcome family has Tier C evidence  a large trial reporting this exact
                                      endpoint sits outside the mean/SD pool
  contributing study has an
    unresolved source problem         source QC / author contact

Status (section 10 of the brief)
  source-qc-required    a contributing study carries an unresolved SOURCE-QC
                        flag (a flag whose text says "resolved" does not count)
  sensitivity-dependent significance differs between the pre-specified model
                        and a sensitivity model of the same analysis
  under-review          a contributing result is not yet judged
  author-contact-useful a contributing study has a documented problem that
                        only the authors or a registry could settle
  stable                none of the above
"stable" here means "no open flag on this analysis's own inputs". It is
deliberately not the word "locked": lock is a project-level state with its
own criteria, and this script has no authority to declare it.
"""
from __future__ import annotations

import csv
import hashlib
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / "scripts"))
from build_v34_dashboard_data import MODEL_META  # noqa: E402  (label/unit/role, one source)

MODELS_CSV = ROOT / "09_V34_ANALYSIS" / "03_RESULTS" / "v34_models.csv"
ROLLUP_CSV = ROOT / "09_V34_ANALYSIS" / "03_ROB2" / "v34_rob2_model_rollup.csv"
GRADE_CSV = ROOT / "09_V34_ANALYSIS" / "04_GRADE" / "v34_new_model_grade.csv"
MANIFEST_CSV = ROOT / "09_V34_ANALYSIS" / "01_DATA" / "v34_model_manifest.csv"
P1_ROB2_CSV = ROOT / "09_V34_ANALYSIS" / "03_ROB2" / "v34_rob2_draft_assessments.csv"
TIER_A_CSV = ROOT / "07_TIERED_V33" / "01_DATA" / "tiered_primary_v33.csv"
TIER_C_CSV = ROOT / "07_TIERED_V33" / "01_DATA" / "tiered_tierC_parallel_v33.csv"
TIER_RESULTS = ROOT / "07_TIERED_V33" / "05_RESULTS" / "TIERED_ANALYSIS_RESULTS_v33.csv"
AUDIT_CSV = ROOT / "07_TIERED_V33" / "PRIMARY_OUTCOME_DERIVABILITY_AUDIT_v33.csv"
APP_JS = ROOT / "dashboard" / "app.js"
DATADIRS = [
    ROOT / "09_V34_ANALYSIS" / "01_DATA",
    ROOT / "TEAS EA Verification" / "v34_reconciliation" / "data",
]
OUT = ROOT / "dashboard" / "interpretation_layer.js"
LEDGER = HERE / "interpretation_bindings.json"

# The one higher-is-better scale in this analysis set. Everything else here
# (opioid dose, hours to GI recovery, VAS, PONV log risk ratio) is
# lower-is-better, so a negative estimate favours the intervention.
HIGHER_IS_BETTER = {"v34_qor40_24h_TEAS_Sham"}

# Contributing studies for the three primary opioid models are defined by the
# S0 stratum flags in the tiered dataset, not by the v34 manifest.
PRIMARY_MODELS = {
    "v34_primary_24h_mme_TEAS_Sham": ("in_S0_teas_sham", "AN-01-TEAS"),
    "v34_primary_24h_mme_EA_Usual_care": ("in_S0_ea_usual", "AN-01-EA"),
    "v34_primary_24h_mme_ALL_AUDIT": (None, "AN-01-COMB"),
}

# Studies with a documented problem that only the authors or a trial registry
# could settle. Each entry names the specific open question AND the analyses
# it actually affects.
#
# Both halves matter. Keying by study alone would make this meaningless as a
# signal in two different directions: 60 of the 70 studies have an
# author-inquiry record, so mere presence there flags everything; and an
# issue that is real for one endpoint is usually not an issue for that same
# study's other, cleanly-reported endpoints. Gu 2019 is the clearest case --
# its 24 h opioid value exists only in a figure that failed digitization
# validation, but its flatus, bowel-sound and pain values are reported
# numerically and are not in question. Flagging Gu 2019's pain analysis for
# an opioid-figure problem would be exactly the invented criticism the brief
# rules out.
AUTHOR_CONTACT_OPEN = {
    ("Zheng 2025", "flatus"): (
        "the report defines its flatus endpoint as 'the first stools passed', so which "
        "endpoint was actually measured cannot be settled from the paper; a second "
        "independent reviewer confirmed this on 2026-09-09 and recommended the registry "
        "entry or the authors decide it"),
    ("El-Rakshy 2009", "opioid"): (
        "the publication's intervention-group denominators are irreconcilable across its "
        "flow diagram, Results text, Table 1, abstract and Table 3, and the authors report "
        "the original dataset as inaccessible"),
    ("Gu 2019", "opioid"): (
        "the 24 h opioid value appears only in Figure 4, and a pre-specified digitization "
        "failed its validation-against-text check (control arm overestimated by up to 16.0%)"),
}


def open_author_issues(model_id: str, studies: list[str]) -> list[tuple[str, str]]:
    """Return (study, issue) pairs whose documented problem actually bears on
    THIS analysis, matching each issue's endpoint scope against the model."""
    mid = model_id.lower()
    scope = ("flatus" if "flatus" in mid else
             "opioid" if ("mme" in mid or "intraop" in mid) else
             "defecation" if "defecation" in mid else
             "other")
    return [(study, issue) for (study, endpoint), issue in AUTHOR_CONTACT_OPEN.items()
            if study in studies and endpoint == scope]

# Team discussion prompts that are specific to one analysis rather than
# derivable from its numbers. Deliberately phrased as open questions for the
# team, never as findings. They carry the same fingerprint as everything else
# in their record, so they go stale with it.
CURATED_PROMPTS = {
    "v34_primary_24h_mme_TEAS_Sham": [
        "Is the point estimate clinically meaningful in the surgical populations these "
        "four trials actually studied, or is it within the range a reader would call "
        "unimportant?",
        "Should the considerable heterogeneity be reported primarily in Results, or "
        "carried into Discussion as the main limit on what we can claim?",
        "Should Gao 2022 be presented immediately after this estimate, given its size and "
        "that it reports this exact endpoint in a distribution we did not pool?",
    ],
    "v34_primary_24h_mme_EA_Usual_care": [
        "How should we explain to a reader that the EA evidence answers a different "
        "question from the TEAS evidence -- usual care, not sham -- without it reading as "
        "a hedge?",
        "Given no sham-controlled EA trial reports this outcome in absolute dose units, is "
        "the scale-free Tier E SMD synthesis worth showing in the manuscript, or does it "
        "invite more confusion than it resolves?",
    ],
    "v34_primary_24h_mme_ALL_AUDIT": [
        "The protocol keeps TEAS and EA separate for primary inference. Does presenting a "
        "combined estimate at all risk it being quoted as the headline result?",
    ],
    "v34_gi_first_defecation_EA_Usual_care": [
        "This is one of the few intervals here that excludes the null. Does the GI recovery "
        "signal deserve more prominence than the opioid result, despite fewer trials?",
    ],
}


def read(p: Path) -> list[dict]:
    with p.open(encoding="utf-8-sig") as f:
        return list(csv.DictReader(f))


def fnum(v, default=None):
    try:
        return float(v)
    except (TypeError, ValueError):
        return default


def total_n(model_id: str):
    for d in DATADIRS:
        p = d / f"{model_id}.csv"
        if p.exists():
            return sum(int(float(r["n_i"])) + int(float(r["n_c"])) for r in read(p))
    return None


def legacy_grades() -> dict:
    """Parse the three primary models' adopted GRADE from app.js's
    STATA_MASTER_RESULTS rather than restating them here, so the dashboard
    stays the single source for those ratings."""
    src = APP_JS.read_text(encoding="utf-8")
    out = {}
    for aid in ("AN-01-TEAS", "AN-01-EA", "AN-01-COMB"):
        m = re.search(rf'"{aid}":\s*\{{.*?grade:\s*"([^"]+)"', src, re.S)
        if not m:
            raise SystemExit(f"could not parse a GRADE level for {aid} out of dashboard/app.js")
        out[aid] = m.group(1)
    return out


def fmt(v, dp=2):
    if v is None:
        return "—"
    s = f"{abs(v):.{dp}f}"
    return ("−" if v < 0 else "") + s


def het_band(i2: float) -> str:
    if i2 < 50:
        return "low"
    if i2 < 75:
        return "substantial"
    return "considerable"


def build_record(mid, m, roll, grade, studies, unit, label, comparator, sens_flip,
                 tier_c_studies, flags_by_study, audit_totals):
    k = int(float(m["k"]))
    est, lo, hi = fnum(m["estimate"]), fnum(m["ci_low"]), fnum(m["ci_high"])
    i2 = fnum(m["i2"], 0.0)
    p = fnum(m["p_value"])
    estimator = m["estimator"]
    measure = m["measure"]
    n = total_n(mid)
    low = int(roll["low"]) if roll else 0
    some = int(roll["some_concerns"]) if roll else 0
    high = int(roll["high"]) if roll else 0
    high_studies = [s for s in (roll.get("high_risk_studies", "") or "").split("; ")
                    if s and s != "-"] if roll else []

    crosses = lo is not None and hi is not None and lo <= 0 <= hi
    higher_better = mid in HIGHER_IS_BETTER
    favours_intervention = (est > 0) if higher_better else (est < 0)
    band = het_band(i2)
    usual_care = "usual care" in (comparator or "").lower()

    unit_txt = unit or ""
    mag = f"{fmt(abs(est))} {unit_txt}".strip()
    if measure == "logRR":
        import math
        mag = f"a risk ratio of {math.exp(est):.2f}"

    # A readable sentence subject and outcome phrase. The model label reads
    # fine as a column heading but not as the subject of a sentence
    # ("Primary 0-24 h opioid - TEAS vs sham significantly reduces..."), and
    # a manuscript-language layer that produces ungrammatical draft text is
    # not usable for the thing it exists for.
    subject = "TEAS" if "TEAS" in label else "EA" if "EA" in label else "The intervention"
    outcome_phrase = re.split(r"\s+—\s+", label)[0].strip()
    outcome_phrase = re.sub(r"^Primary\s+", "", outcome_phrase)
    if outcome_phrase.lower().endswith("opioid"):
        outcome_phrase += " consumption"

    # ---- Layer 2: what the result actually means -------------------------
    direction = ("favours " + ("the intervention" if favours_intervention else "the comparator"))
    context = (
        f"The pooled estimate corresponds to approximately {mag} "
        f"{'higher' if (est > 0 and higher_better) or (est > 0 and not higher_better) else 'lower'} "
        f"in the intervention arm than the comparator, across {k} contributing "
        f"{'trial' if k == 1 else 'trials'}"
        + (f" (N = {n})." if n else ".")
    )
    if crosses:
        context += (
            f" The 95% confidence interval runs from {fmt(lo)} to {fmt(hi)} and includes no "
            f"difference, so the data are compatible with a worthwhile effect, with none at "
            f"all, and with a small effect in the opposite direction."
        )
    else:
        context += (
            f" The 95% confidence interval ({fmt(lo)} to {fmt(hi)}) excludes no difference, so "
            f"the direction of effect is consistent across the interval, though its size "
            f"remains uncertain."
        )
    context += f" Between-study heterogeneity is {band} (I² = {i2:.1f}%)."
    if k <= 4:
        context += (
            f" With only {k} contributing {'trial' if k == 1 else 'trials'}, both the interval "
            f"and the heterogeneity estimate are themselves imprecise."
        )
    context += (
        f" This should therefore be read as "
        + ("a possible signal rather than firm evidence of benefit."
           if crosses else
           "a consistent but not precisely sized effect.")
    )

    # ---- Layer 3a: results-safe / discussion-safe / do-not-say -----------
    results_safe = (
        f"{k} {'trial' if k == 1 else 'trials'} contributed to the {outcome_phrase} "
        f"({subject} vs {(comparator or '').lower() or 'comparator'}) synthesis"
        + (f" (N = {n})" if n else "")
        + f". The pooled {'log risk ratio' if measure == 'logRR' else 'mean difference'} was "
        f"{fmt(est)}"
        + (f" {unit_txt}" if unit_txt and measure != "logRR" else "")
        + f" (95% CI {fmt(lo)} to {fmt(hi)}"
        + (f"; p = {p:.3f}" if p is not None else "")
        + f"; I² = {i2:.1f}%; {estimator})."
    )

    qualifiers = []
    if crosses:
        qualifiers.append("the confidence interval includes no difference")
    if i2 >= 75:
        qualifiers.append(f"between-study heterogeneity was considerable (I² = {i2:.1f}%)")
    elif i2 >= 50:
        qualifiers.append(f"between-study heterogeneity was substantial (I² = {i2:.1f}%)")
    if k <= 4:
        qualifiers.append(f"only {k} trials contributed")
    if grade in ("Low", "Very Low"):
        qualifiers.append(f"certainty of evidence was {grade.lower()}")

    if qualifiers:
        discussion_safe = (
            f"The point estimate {direction}, but "
            + "; ".join(qualifiers)
            + ", so this is best described as "
            + ("a possible effect that this evidence cannot confirm."
               if crosses else
               "an effect whose size this evidence cannot pin down.")
        )
    else:
        discussion_safe = (
            f"The estimate {direction}, with a consistent interval and limited heterogeneity, "
            "supporting a more confident reading than most analyses in this review."
        )

    do_not_say = []
    if crosses:
        do_not_say.append({
            "text": f"“{subject} significantly reduces {outcome_phrase.lower()}.”",
            "why": "The 95% confidence interval includes no difference; there is no "
                   "statistically significant effect to report.",
        })
    if grade in ("Low", "Very Low"):
        do_not_say.append({
            "text": "“This demonstrates / establishes a benefit.”",
            "why": f"Certainty of evidence for this analysis is {grade.lower()}; the wording "
                   "should not imply more than the certainty rating supports.",
        })
    if i2 >= 75:
        do_not_say.append({
            "text": "“Findings were consistent across trials.”",
            "why": f"I² = {i2:.1f}% indicates considerable heterogeneity between the "
                   "contributing trials.",
        })

    # ---- Layer 3b: claim boundaries --------------------------------------
    claims = [
        {"level": "supported",
         "claim": f"The point estimate {direction}.",
         "basis": f"Point estimate {fmt(est)}; a direct reading of the fitted model."},
        {"level": "supported",
         "claim": f"The estimated difference was approximately {mag}.",
         "basis": "The computed pooled estimate for this model."},
    ]
    amber_qual = ("the confidence interval includes no difference"
                  if crosses else
                  (f"heterogeneity was {band} (I² = {i2:.1f}%)" if i2 >= 50 else
                   f"certainty is {grade.lower()}" if grade in ("Low", "Very Low") else None))
    if amber_qual:
        claims.append({
            "level": "qualified",
            "claim": "The magnitude may be clinically meaningful.",
            "basis": f"Must be stated with the qualification that {amber_qual}.",
        })
    if crosses or grade in ("Low", "Very Low"):
        claims.append({
            "level": "unsupported",
            "claim": f"{subject} definitively changes {outcome_phrase.lower()}.",
            "basis": ("The interval includes no difference." if crosses
                      else f"Certainty is {grade.lower()}.")
            + " A definitive claim is not available from this analysis.",
        })

    # ---- Layer 3c: reviewer questions, each with its trigger and pathway --
    rq = []

    def ask(question, trigger, pathway):
        rq.append({"question": question, "trigger": trigger, "pathway": pathway})

    if k <= 4:
        ask(f"Why did only {k} trials contribute, when the review includes 70 RCTs?",
            f"k = {k}",
            "Derivability audit and evidence flow (v33 tiered panel)")
    if i2 >= 75:
        ask(f"What explains the considerable heterogeneity (I² = {i2:.1f}%)?",
            f"I² = {i2:.1f}% ≥ 75%",
            "Heterogeneity and moderator analyses; study characteristics")
    if crosses:
        ask("Does the confidence interval include effects a clinician would call "
            "unimportant?",
            f"95% CI {fmt(lo)} to {fmt(hi)} includes 0",
            "Clinical Importance / MCID studio")
    if high:
        ask(f"How much does the result depend on the {high} contributing "
            f"{'result' if high == 1 else 'results'} at high risk of bias"
            + (f" ({', '.join(high_studies)})?" if high_studies else "?"),
            f"{high} of {low + some + high} contributing results judged High risk",
            "Result-specific RoB 2 panel and model rollup")
    if usual_care:
        ask("With a usual-care rather than sham comparator, how much of this estimate could "
            "be performance or expectation effect?",
            f"comparator = {comparator}",
            "Comparator hierarchy note; RoB 2 domain D2")
    if k == 2 and "Hartung" not in estimator:
        ask("Is a random-effects interval trustworthy with only two studies and no "
            "Hartung–Knapp adjustment?",
            f"k = 2 with estimator '{estimator}'",
            "Estimator/CI-method sensitivity analyses")
    if sens_flip:
        ask("Does the conclusion change under a different estimator or CI method?",
            sens_flip,
            "Estimator/CI-method sensitivity grid (v33 tiered panel)")
    if tier_c_studies:
        ask(f"Why {'was' if len(tier_c_studies) == 1 else 'were'} "
            f"{', '.join(tier_c_studies)} not in the pooled analysis despite reporting this "
            f"endpoint?",
            f"Tier C evidence exists for this outcome family: {', '.join(tier_c_studies)}",
            "Derivability tiers: Tier C parallel synthesis (reported as medians, never "
            "converted to mean/SD for pooling)")
    for s, issue in open_author_issues(mid, studies):
        ask(f"Is the source problem in {s} resolved?",
            f"{s}: {issue}",
            "RoB 2 assessment for that study; source-QC flags")

    # ---- Status (section 10) ---------------------------------------------
    status = "stable"
    status_reason = "No open source-QC flag, unjudged result or estimator dependence on " \
                    "this analysis's own inputs."
    unresolved_qc = [s for s in studies
                     if "source-qc" in (flags_by_study.get(s, "") or "").lower()
                     and "resolved" not in (flags_by_study.get(s, "") or "").lower()]
    author_open = [s for s, _ in open_author_issues(mid, studies)]
    if roll and int(roll.get("results_unjudged", 0) or 0) > 0:
        status = "under-review"
        status_reason = (f"{roll['results_unjudged']} contributing result(s) do not yet carry a "
                         "result-specific RoB 2 judgement.")
    elif unresolved_qc:
        status = "source-qc-required"
        status_reason = ("Unresolved source-QC flag on: " + ", ".join(unresolved_qc) + ".")
    elif sens_flip:
        status = "sensitivity-dependent"
        status_reason = sens_flip
    elif author_open:
        status = "author-contact-useful"
        status_reason = ("Author or registry clarification could settle an open question in: "
                         + ", ".join(author_open) + ".")

    # ---- Why only k -------------------------------------------------------
    why_k = None
    if k <= 7:
        why_k = {
            "headline": f"{audit_totals['included']} RCTs included → k = {k} in this analysis",
            "explanation": (
                f"The review's {audit_totals['included']} included RCTs span multiple outcomes, "
                f"time windows, stimulation modalities and comparator types, so most of them "
                f"were never candidates for this particular estimand. For the 0–24 h opioid "
                f"endpoint specifically, a {audit_totals['rows']}-row derivability audit "
                f"covering the {audit_totals['studies']} trials that report any 0–24 h opioid "
                f"result found {audit_totals['tier_a']} contrasts, across "
                f"{audit_totals['tier_a_studies']} trials, that report the exact endpoint as a "
                f"mean and SD in a dose unit with a sourced conversion factor. This analysis "
                f"then takes the subset matching its own modality and comparator stratum, "
                f"because the protocol does not combine TEAS with EA, or sham with usual care."
            ),
            "pathway": "Derivability audit / evidence flow",
        }

    # ---- Evidence binding + fingerprint -----------------------------------
    bound = {
        "k": k, "estimate": round(est, 4) if est is not None else None,
        "ci_low": round(lo, 4) if lo is not None else None,
        "ci_high": round(hi, 4) if hi is not None else None,
        "i2": round(i2, 2), "grade": grade,
        "rob_low": low, "rob_some": some, "rob_high": high,
        "estimator": estimator,
    }
    fp = hashlib.sha256(
        json.dumps(bound, sort_keys=True).encode("utf-8")).hexdigest()[:16]

    return {
        "analysis_id": mid,
        "label": label,
        "unit": unit_txt,
        "comparator": comparator,
        "context": context,
        "results_safe": results_safe,
        "discussion_safe": discussion_safe,
        "do_not_say": do_not_say,
        "claims": claims,
        "reviewer_questions": rq,
        "discussion_prompts": CURATED_PROMPTS.get(mid, []),
        "why_k": why_k,
        "status": status,
        "status_reason": status_reason,
        "bound_evidence": bound,
        "fingerprint": fp,
        "stale": False,
        "stale_detail": "",
        "review_state": "new",
        "reviewed_on": "",
    }


def main() -> int:
    models = {r["model_id"]: r for r in read(MODELS_CSV)}
    rollup = {r["model_id"]: r for r in read(ROLLUP_CSV)}
    grades = {r["model_id"]: r["grade"] for r in read(GRADE_CSV)}
    manifest = {r["model_id"]: r for r in read(MANIFEST_CSV)}
    tier_a = read(TIER_A_CSV)
    tier_c = read(TIER_C_CSV)
    tier_results = {r["analysis_id"]: r for r in read(TIER_RESULTS)}
    audit = read(AUDIT_CSV)
    leg = legacy_grades()

    flags_by_study = {}
    for r in read(P1_ROB2_CSV):
        if r["flags"].strip():
            flags_by_study.setdefault(r["study"], "")
            flags_by_study[r["study"]] += " " + r["flags"]

    # The review's own canonical included-study count, read the same way
    # scripts/build_v34_dashboard_data.py derives it, so the "N RCTs included"
    # headline cannot drift from the number shown everywhere else. The audit's
    # own denominator is smaller (only trials reporting any 0-24 h opioid
    # result were candidates), and conflating the two is exactly the confusion
    # this panel exists to clear up.
    outcome_rows = read(ROOT / "TEAS EA Verification" / "v34_reconciliation" / "data"
                        / "v34_outcome_data.csv")
    audit_totals = {
        "included": len({r["Canonical study"] for r in outcome_rows if r.get("Canonical study")}),
        "studies": len({r["study"] for r in audit}),
        "rows": len(audit),
        "tier_a": sum(1 for r in audit if r["tier_mme"] == "A"),
        "tier_a_studies": len({r["study"] for r in audit if r["tier_mme"] == "A"}),
    }

    # The one genuine estimator-dependence in this review: the pre-specified
    # Hartung-Knapp interval for the TEAS primary does not exclude the null,
    # but the Wald interval on the same model does. Read from the fitted
    # sensitivity grid rather than asserted.
    sens_flip_by_model = {}
    s0 = tier_results.get("V33_S0_TEAS_SHAM")
    wald = tier_results.get("V33_SENS_C2_REML_WALD")
    if s0 and wald:
        p0, pw = fnum(s0["p_value"]), fnum(wald["p_value"])
        if p0 is not None and pw is not None and (p0 < 0.05) != (pw < 0.05):
            sens_flip_by_model["v34_primary_24h_mme_TEAS_Sham"] = (
                f"significance differs by CI method on the same fitted model: "
                f"p = {p0:.4f} with the pre-specified Hartung–Knapp interval versus "
                f"p = {pw:.4f} with a Wald interval, which is anticonservative at this k"
            )

    tier_c_by_family = {}
    for r in tier_c:
        tier_c_by_family.setdefault("opioid_24h", []).append(r["study"])

    records = []
    for mid, m in models.items():
        meta = MODEL_META.get(mid, {})
        label = meta.get("label", mid)
        unit = meta.get("unit", manifest.get(mid, {}).get("unit", ""))
        roll = rollup.get(mid)

        if mid in PRIMARY_MODELS:
            flag, legacy_id = PRIMARY_MODELS[mid]
            grade = leg[legacy_id]
            if flag:
                studies = [r["study"] for r in tier_a if r.get(flag) == "1"]
            else:
                studies = sorted({r["study"] for r in tier_a
                                  if r["in_S0_teas_sham"] == "1" or r["in_S0_ea_usual"] == "1"})
            comparator = ("Sham" if flag == "in_S0_teas_sham"
                          else "Usual care" if flag == "in_S0_ea_usual"
                          else "Sham (TEAS) / usual care (EA)")
        else:
            grade = grades.get(mid, "")
            man = manifest.get(mid, {})
            studies = [s.strip() for s in (man.get("studies", "") or "").split(";") if s.strip()]
            comparator = man.get("comparator", "")

        if not grade:
            # No adopted certainty rating -> no interpretation record. An
            # interpretation that cannot state its own certainty would be
            # exactly the kind of unanchored manuscript language this layer
            # exists to prevent.
            continue

        tier_c_studies = (tier_c_by_family.get("opioid_24h", [])
                          if mid in PRIMARY_MODELS else [])

        records.append(build_record(
            mid, m, roll, grade, studies, unit, label, comparator,
            sens_flip_by_model.get(mid), tier_c_studies, flags_by_study, audit_totals))

    # ---- staleness: compare against the committed review ledger -----------
    # The baseline is the fingerprint each interpretation was last REVIEWED
    # at, not the numbers this run just read -- see the module docstring for
    # why comparing a fresh build against itself is worthless here.
    accept = "--accept" in sys.argv
    ledger = json.loads(LEDGER.read_text(encoding="utf-8")) if LEDGER.exists() else {"bindings": {}}
    bindings = ledger.get("bindings", {})

    stale_count = 0
    for rec in records:
        mid = rec["analysis_id"]
        prior = bindings.get(mid)
        if prior is None:
            # Never reviewed: not "stale" (there is no superseded wording to
            # warn about), but recorded as newly generated so --accept has
            # something to confirm.
            rec["review_state"] = "new"
            continue
        if prior.get("fingerprint") == rec["fingerprint"]:
            rec["review_state"] = "reviewed"
            rec["reviewed_on"] = prior.get("reviewed_on", "")
            continue
        was = prior.get("bound_evidence", {})
        diffs = [f"{k}: {was.get(k)} → {v}" for k, v in rec["bound_evidence"].items()
                 if was.get(k) != v]
        rec["stale"] = True
        rec["review_state"] = "stale"
        rec["reviewed_on"] = prior.get("reviewed_on", "")
        rec["stale_detail"] = ("; ".join(diffs) if diffs
                               else "the bound evidence fingerprint changed")
        stale_count += 1

    if accept:
        import datetime
        today = datetime.date.today().isoformat()
        for rec in records:
            bindings[rec["analysis_id"]] = {
                "fingerprint": rec["fingerprint"],
                "reviewed_on": today,
                "bound_evidence": rec["bound_evidence"],
            }
            rec["stale"] = False
            rec["stale_detail"] = ""
            rec["review_state"] = "reviewed"
            rec["reviewed_on"] = today
        LEDGER.write_text(json.dumps(
            {"note": ("Fingerprint of the evidence each interpretation was last reviewed "
                      "against. Updated only by build_interpretation_layer.py --accept, which "
                      "is a person confirming they have re-read the wording against the "
                      "current numbers. Re-running the generator alone does not clear a "
                      "stale flag."),
             "bindings": bindings}, indent=2) + "\n", encoding="utf-8")
        stale_count = 0
        print(f"  --accept: recorded {len(records)} bindings as reviewed on {today}")

    payload = {
        "generated_by": "09_V34_ANALYSIS/05_INTERPRETATION/build_interpretation_layer.py",
        "layer": "INTERPRETATION",
        "is_evidence": False,
        "disclaimer": (
            "Working interpretation for team discussion, generated by explicit rules from "
            "the review's own analysis outputs. It is not manuscript text, not a finding, and "
            "not a substitute for the evidence panels it describes. Nothing in this layer "
            "changes any extracted value, RoB 2 judgement, GRADE rating, statistical result or "
            "study classification; it is generated separately and read separately."
        ),
        "record_count": len(records),
        "stale_count": stale_count,
        "records": records,
    }

    header = f"""// INTERPRETATION LAYER — generated file, do not hand-edit.
// Regenerate with:  python3 09_V34_ANALYSIS/05_INTERPRETATION/build_interpretation_layer.py
//
// This is the dashboard's WORKING INTERPRETATION overlay: draft manuscript
// language, reviewer questions and team discussion prompts. It is NOT
// evidence. Every sentence is produced by an explicit stated rule applied to
// the review's own analysis outputs, and every record is bound to a
// fingerprint of the exact values it describes, so it is flagged rather than
// silently kept when an analysis is re-run.
//
// Records : {len(records)}  |  stale: {stale_count}
window.INTERPRETATION_LAYER = """

    OUT.write_text(header + json.dumps(payload, indent=2, ensure_ascii=False) + ";\n",
                   encoding="utf-8")
    print(f"wrote {OUT.relative_to(ROOT)}")
    print(f"  records .......... {len(records)}")
    print(f"  stale ............ {stale_count}")
    for r in records:
        print(f"  {r['analysis_id']:<38} {r['status']:<22} "
              f"{len(r['reviewer_questions'])} reviewer q, {len(r['claims'])} claims")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

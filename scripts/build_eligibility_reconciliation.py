#!/usr/bin/env python3
"""
The dedicated eligibility reconciliation pass for the seven post-lock additions.

WHY THIS EXISTS
Seven studies were added to the register after the v26 lock (Wu 2016, Gao 2022,
Liu 2015, Oztas 2019, Song 2020, Szmit 2021, Zhang 2018). One -- Szmit 2021 --
was admitted to two analyses. The dashboard has since said of the rest that they
are "not yet pooled into any target pending a dedicated eligibility
reconciliation pass". This is that pass.

WHAT IT DOES AND DOES NOT DECIDE
It assigns each study-outcome a DISPOSITION and the rule behind it, and records
what would unblock the ones that are blocked. It pools nothing. Admitting a study
to a locked analysis stays a review-team act, the same way clearing an
interpretation staleness flag does -- this pass exists so that act can be taken
on evidence rather than on an open-ended deferral.

THE TAXONOMY
Every blocker is one of five kinds, and the kind determines whether the pass can
resolve it:

  data_absent        the source does not report the value. Only author contact
                     changes this.
  derivation_invalid the value is reported but no defensible derivation reaches
                     the review's scale. Permanent unless the estimand changes.
  scope_mismatch     the value is real and sound but outside the target's own
                     definition. Permanent unless a target is rescoped.
  qc_hold            an unresolved question about the data, held pending
                     adjudication. THIS is what a reconciliation pass can settle.
  eligible           clears on data grounds; awaiting a review-team admission.

Usage:  python3 scripts/build_eligibility_reconciliation.py [--check]
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT_JS = ROOT / "dashboard" / "eligibility_reconciliation.js"
QC_DIG = "07_TIERED_V33/03_DIGITIZATION/figure_only_values_QC_2026-09-12.md"

PASS_DATE = "2026-09-12"

R = [
 # ---- Szmit 2021: already admitted, recorded so the set is complete ---------
 dict(study="Szmit 2021", outcome="opioid_24h", target="Primary 0-24 h opioid",
      disposition="admitted", changed=False,
      rule="Admitted before this pass; recorded here so all seven are accounted for.",
      evidence="Contributes to the strict primary 24-h opioid analysis and the Target D "
               "nausea 0-24 h stratum."),

 # ---- Zhang 2018 -----------------------------------------------------------
 dict(study="Zhang 2018", outcome="flatus_time", target="Target E (time to first flatus)",
      disposition="eligible", changed=True,
      rule="Target E takes time-to-event flatus with no clock-window requirement; its six "
           "members carry time_window 'Postoperative' or 'From surgery to first ...'.",
      evidence=f"Unblocked {PASS_DATE} by formal vector digitisation of Figure 2a: TEA "
               "51.33 +/- 2.78 SE vs sham-TEA 80.05 +/- 4.40 SE hours, n=21 per arm "
               "(SD 12.74 vs 20.15). The extraction reproduces all seven percentage "
               f"reductions the paper reports, this one to 0.02 pp. See {QC_DIG}.",
      unblocks="Review-team admission. This is the only one of the seven that a data "
               "problem was blocking and that is now solved."),
 dict(study="Zhang 2018", outcome="pain_rest_24h", target="Target C (pain at rest ~24 h)",
      disposition="scope_mismatch", changed=True,
      rule="Target C takes clock-defined 24-hour endpoints. Both current members carry "
           "time_window exactly '24 h'. A day label is not a clock-defined window -- the "
           "same rule already excluded Liu 2015's POD 1 PONV from Target D.",
      evidence="The value is now digitised and the panel validates at POD 2 (0.10 pp) and "
               "POD 3 (0.54 pp), so the data are sound. The timepoint is not: it is POD 1, "
               "and the paper states treatment ran 'daily from POD 1 to POD 3', so the POD 1 "
               "score falls on the first treatment day with no statement of whether it "
               "precedes or follows the sessions. Consistent with that, the digitised POD 1 "
               "values show TEA slightly WORSE than sham (3.96 vs 3.77) and the paper reports "
               "reductions only from POD 2.",
      unblocks="Rescoping Target C to accept day-labelled endpoints -- which would also "
               "reopen Liu 2015. Not recommended by this pass."),

 # ---- Song 2020: the QC hold this pass actually resolves --------------------
 dict(study="Song 2020", outcome="pain_rest_24h", target="Target C (pain at rest ~24 h)",
      disposition="eligible", changed=True,
      rule="A qc_hold is resolved by reading the source. The hold was 'pending resolution of "
           "the ITT (85) vs per-protocol (78) denominator inconsistency'.",
      evidence="There is no inconsistency. The paper defines both populations and reconciles "
               "them exactly: 109 assessed, 15 ineligible, 9 refused, 85 enrolled; "
               "'we included 85 patients in the ITT population and 78 in the PP population "
               "(three patients were allergic to TEAS, two patients were transferred to the "
               "intensive care unit after surgery, and two patients removal of the drainage "
               "tube was delayed)' -- 3+2+2 = 7, and 85-7 = 78. It also names the primary: "
               "'All analyses were based on the intention-to-treat (ITT) population'. The "
               "register's 42/43 = 85 is that ITT population. The comparator is a true sham "
               "('The control group also underwent this sham treatment'). The outcome itself "
               "is a clean 24-h VAS, 2.76+/-1.1 vs 3.23+/-1.1, P=0.053, directly reported.",
      unblocks="Review-team admission. The blocker was a question, and the source answers it."),
 dict(study="Song 2020", outcome="ponv_24h", target="Target D (PONV 0-24 h)",
      disposition="eligible", changed=True,
      rule="Same qc_hold, same resolution.",
      evidence="24-h PONV 3/42 vs 10/43, P=0.039, directly reported events and totals over "
               "the ITT population.",
      unblocks="Review-team admission, and a decision on which Target D stratum it joins."),
 dict(study="Song 2020", outcome="intraop_opioid", target="Target F (intraoperative)",
      disposition="scope_mismatch", changed=False,
      rule="Target F's intraoperative stratum is scoped to remifentanil mass.",
      evidence="Intraoperative sufentanil 18.54+/-2.3 vs 19.09+/-2.7 ug, P=0.322.",
      unblocks="Rescoping the stratum to accept other intraoperative opioids."),

 # ---- Gao 2022: the one that needs a RULE decision, not a data decision -----
 dict(study="Gao 2022", outcome="pain_rest_24h", target="Target C (pain at rest ~24 h)",
      disposition="qc_hold", changed=True,
      rule="Held because 'patients could not be fully blinded to real stimulation'.",
      evidence="The data are not in question: 24-h pain VAS 2.0+/-1.7 vs 2.2+/-1.8, P=0.006, "
               "mean/SD directly reported, clean 24-h window, n=1,655.",
      unblocks="A review-team ruling on the hold itself. THIS PASS'S RECOMMENDATION: the "
               "blocker is a risk-of-bias concern, and this review already has an architecture "
               "for those -- result-specific RoB 2 feeding GRADE. Excluding a trial from "
               "pooling instead of rating it down is a different instrument, and it is applied "
               "inconsistently here: incomplete patient blinding is a limitation shared by "
               "every sham-controlled stimulation trial in the review, and the others are "
               "pooled. Either the hold should become a RoB 2 Domain 2 judgement, or the same "
               "exclusion should be applied to the other sham-controlled trials. Note the "
               "consequence before deciding: at n=1,655 this trial would dominate Target C.",
      caution="Admitting it would roughly quadruple Target C's sample. That is a reason to "
              "decide deliberately, not a reason to decide either way."),
 dict(study="Gao 2022", outcome="ponv_24h", target="Target D (PONV 0-24 h)",
      disposition="qc_hold", changed=True,
      rule="Same blinding hold.",
      evidence="Composite PONV 243/827 vs 283/828, P=0.036; vomiting 86/827 vs 147/828, "
               "P<0.001; nausea 18/827 vs 42/828, P=0.003 -- all directly reported.",
      unblocks="The same ruling as above."),
 dict(study="Gao 2022", outcome="opioid_24h", target="Primary 0-24 h opioid",
      disposition="derivation_invalid", changed=True,
      rule="A median/IQR may be converted only where the normality the Wan et al. estimators "
           "assume is tenable.",
      evidence=f"Settled {PASS_DATE}: 33 (0-50) vs 30 (0-60) ug, and the paper's own preceding "
               "row shows only 597/827 and 588/828 patients received an analgesic pump at all, "
               "so ~28% used none. That spike at zero is why Q1 = 0 in both arms. The "
               "conversion would give 27.67 +/- 37.13 and 30.00 +/- 44.56, placing ~23% of "
               f"patients below zero micrograms. See {QC_DIG}.",
      unblocks="Nothing available. The median, IQR and P value stand as source truth."),

 # ---- Wu 2016 --------------------------------------------------------------
 dict(study="Wu 2016", outcome="opioid_24h", target="Primary 0-24 h opioid",
      disposition="data_absent", changed=False,
      rule="A pooled contrast needs a reported quantity.",
      evidence="Rescue IV tramadol demand was lower with TAES (P<0.05) but exact quantities "
               "are not reported.",
      unblocks="Author contact."),
 dict(study="Wu 2016", outcome="pain_rest_24h", target="Target C (pain at rest ~24 h)",
      disposition="data_absent", changed=True,
      rule="A digitisation is admissible only if the source reports something independent of "
           "the figure to validate it against (the Gu 2019 standard).",
      evidence=f"Settled {PASS_DATE}: the paper reports no VAS number anywhere in its text. "
               "Checked mechanically -- 27 'mean +/- SD' patterns appear in the paper, none "
               f"within 200 characters of a pain mention. See {QC_DIG}.",
      unblocks="Author contact."),
 dict(study="Wu 2016", outcome="ponv_24h", target="Target D (PONV)",
      disposition="scope_mismatch", changed=False,
      rule="A Target D stratum is defined by its ascertainment window.",
      evidence="Nausea/vomiting 3/27 vs 8/27 vs 9/27 are reported, but the postoperative "
               "ascertainment window is not stated, so the row cannot be assigned to the "
               "0-24 h or 0-48 h stratum.",
      unblocks="Author contact for the window."),

 # ---- Liu 2015 -------------------------------------------------------------
 dict(study="Liu 2015", outcome="opioid_24h", target="Primary 0-24 h opioid",
      disposition="data_absent", changed=False,
      rule="A pooled contrast needs a reported quantity.",
      evidence="PCIA composition and rate are given, but cumulative 0-24 h total/bolus use is "
               "not reported.",
      unblocks="Author contact."),
 dict(study="Liu 2015", outcome="pain_rest_24h", target="Target C (pain at rest ~24 h)",
      disposition="data_absent", changed=True,
      rule="Same Gu 2019 standard.",
      evidence=f"Settled {PASS_DATE}: 34 'mean +/- SD' patterns in the paper, none within 200 "
               f"characters of a pain mention. See {QC_DIG}.",
      unblocks="Author contact."),
 dict(study="Liu 2015", outcome="ponv_24h", target="Target D (PONV 0-24 h)",
      disposition="scope_mismatch", changed=False,
      rule="Target D strata are clock-defined; POD 1 is a day label.",
      evidence="POD1 nausea 11/44 vs 9/44; vomiting 9/44 vs 8/44.",
      unblocks="Rescoping Target D -- which would also reopen Zhang 2018's POD 1 pain."),
 dict(study="Liu 2015", outcome="intraop_opioid", target="Target F (intraoperative)",
      disposition="scope_mismatch", changed=False,
      rule="Target F's intraoperative stratum is scoped to remifentanil mass.",
      evidence="Total intraoperative sufentanil 95.6+/-21.76 vs 117.7+/-37.95 ug, P=0.02.",
      unblocks="Rescoping the stratum."),

 # ---- Oztas 2019 -----------------------------------------------------------
 dict(study="Oztas 2019", outcome="opioid_24h", target="Primary 0-24 h opioid",
      disposition="derivation_invalid", changed=False,
      rule="An MME pool needs a sourced equianalgesic ratio; the review forbids inventing one.",
      evidence="0-24 h IV PCA tramadol 228.40+/-87.89 vs 357.81+/-123.70 mg is reported, but "
               "no sourced parenteral tramadol:morphine ratio was located (searched 2026-09-07 "
               "against this project's equianalgesic reference family).",
      unblocks="Locating a citable parenteral tramadol:morphine ratio. This is the one blocker "
               "in the set that a literature search rather than an author could lift."),
 dict(study="Oztas 2019", outcome="pain_rest_24h", target="Target C (pain at rest ~24 h)",
      disposition="scope_mismatch", changed=False,
      rule="Target C takes ~24-hour endpoints.",
      evidence="Resting pain 3.00+/-1.30 vs 4.88+/-1.78 was assessed after the 22-h "
               "intervention rather than at a clean ~24 h timepoint; overall RoB is High.",
      unblocks="Nothing clean; the measurement is tied to the intervention's end, not a clock."),
 dict(study="Oztas 2019", outcome="ponv_24h", target="Target D (PONV)",
      disposition="data_absent", changed=False,
      rule="A pooled contrast needs reported group values.",
      evidence="Exact group values for nausea/vomiting were not reported.",
      unblocks="Author contact."),
]


def build() -> dict:
    by_disp: dict[str, int] = {}
    for r in R:
        by_disp[r["disposition"]] = by_disp.get(r["disposition"], 0) + 1
    studies = sorted({r["study"] for r in R})
    return {
        "generated_by": "scripts/build_eligibility_reconciliation.py",
        "pass_date": PASS_DATE,
        "scope": "the seven studies added to the register after the v26 lock",
        "studies": studies,
        "pools_nothing": True,
        "rows": R,
        "tally": dict(sorted(by_disp.items())),
        "newly_eligible": [f"{r['study']} - {r['outcome']}" for r in R
                           if r["disposition"] == "eligible"],
        "needs_rule_decision": [f"{r['study']} - {r['outcome']}" for r in R
                                if r["disposition"] == "qc_hold"],
    }


def main(check_only: bool) -> int:
    payload = build()
    text = ("// Generated by scripts/build_eligibility_reconciliation.py; do not edit.\n"
            "// The dedicated eligibility reconciliation pass for the seven post-lock\n"
            "// additions. Assigns a disposition per study-outcome; pools nothing.\n"
            "window.ELIGIBILITY_RECONCILIATION = "
            + json.dumps(payload, ensure_ascii=False, indent=2) + ";\n")
    if check_only:
        if not OUT_JS.exists() or OUT_JS.read_text(encoding="utf-8") != text:
            print("OUT OF DATE: dashboard/eligibility_reconciliation.js differs", file=sys.stderr)
            return 1
        print("eligibility_reconciliation.js is current")
        return 0
    OUT_JS.write_text(text, encoding="utf-8")
    print(f"{len(R)} study-outcome dispositions across {len(payload['studies'])} studies")
    for k, v in payload["tally"].items():
        print(f"  {k:20s} {v}")
    print("\nnewly eligible (awaiting review-team admission):")
    for s in payload["newly_eligible"]:
        print(f"  {s}")
    print("\nneeds a rule decision, not a data decision:")
    for s in payload["needs_rule_decision"]:
        print(f"  {s}")
    return 0


if __name__ == "__main__":
    sys.exit(main("--check" in sys.argv))

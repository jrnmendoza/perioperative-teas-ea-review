#!/usr/bin/env python3
"""
Set each trial's country to its COUNTRY OF CONDUCT, verified from the source PDF.

WHY
The register recorded "China" for all 63 trials that carried a country, and left
7 blank. Reading the source publications showed eight of those 63 were run
somewhere else. "63/63 in China" and "a multi-country evidence base" support
different generalisability claims, and the manuscript's Characteristics table
inherits whichever the register says.

WHICH COUNTRY
The review team's decision is COUNTRY OF CONDUCT -- where the patients were
recruited and treated -- not the lead author's affiliation. The two differ for
Lee 2011, whose first affiliation is Victoria University in Melbourne while the
paper states "Hysterectomized patients at the China Medical University Hospital
[Taichung] were invited to be subjects": conduct is Taiwan.

Every value below carries the sentence it was read from. Nothing is inferred
from an author's name, a journal's country, or a sister trial.

Usage:  python3 scripts/apply_country_of_conduct.py [--check]
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA_JS = ROOT / "dashboard" / "data.js"

META = {
    "China":     {"code": "CN", "lat": 35.8617,  "lng": 104.1954, "flag": "🇨🇳"},
    "Hong Kong": {"code": "HK", "lat": 22.3193,  "lng": 114.1694, "flag": "🇭🇰"},
    "Taiwan":    {"code": "TW", "lat": 23.6978,  "lng": 120.9605, "flag": "🇹🇼"},
    "Singapore": {"code": "SG", "lat": 1.3521,   "lng": 103.8198, "flag": "🇸🇬"},
    "Malaysia":  {"code": "MY", "lat": 4.2105,   "lng": 101.9758, "flag": "🇲🇾"},
    "Brazil":    {"code": "BR", "lat": -14.2350, "lng": -51.9253, "flag": "🇧🇷"},
    "Poland":    {"code": "PL", "lat": 51.9194,  "lng": 19.1451,  "flag": "🇵🇱"},
    "Turkey":    {"code": "TR", "lat": 38.9637,  "lng": 35.2433,  "flag": "🇹🇷"},
}

# study -> (country of conduct, verbatim evidence from the source PDF)
CONDUCT = {
    # --- corrections: register said China, the paper says otherwise -----------
    "Sim 2002": ("Singapore",
                 "Department of Anaesthesia, National University Hospital Singapore"),
    "Wong 2006": ("Hong Kong",
                  "Surgical Unit of a tertiary referral university-teaching hospital in Hong Kong "
                  "(Prince of Wales Hospital, Shatin)"),
    # Identity re-assigned 2026-09-12: Yeh 2010 is the Altern Ther Health Med report,
    # Yeh 2011 the Int J Nurs Stud report. The evidence sentences follow the papers.
    "Yeh 2010": ("Taiwan",
                 "carried out by the orthopedic departments of a 4000-bed medical center in "
                 "northern Taiwan"),
    "Coura 2011": ("Brazil",
                   "conducted in the Unimed Hospital Centre, Joinville-SC, Brazil, "
                   "from April 2009 to June 2010"),
    "Lee 2011": ("Taiwan",
                 "Hysterectomized patients at the China Medical University Hospital [Taichung] "
                 "were invited to be subjects in the study. Lead affiliation is Victoria "
                 "University, Melbourne; country of CONDUCT is Taiwan."),
    "Yeh 2011": ("Taiwan",
                 "Nursing Department, Veterans General Hospital, Taipei, Taiwan, ROC"),
    "Ng 2013": ("Hong Kong",
                "conducted the study from October 2008 through October 2010 at the Prince of "
                "Wales Hospital, a university teaching hospital in Hong Kong"),
    "Seevaunnamtum 2016": ("Malaysia",
                           "conducted at a 990-bed multidisciplinary tertiary government "
                           "hospital in Malaysia"),
    # --- fills: register held no country at all -------------------------------
    "Szmit 2021": ("Poland",
                   "Department and Clinic of General, Minimally Invasive and Endocrine Surgery, "
                   "Wroclaw Medical University, 50-556 Wroclaw, Poland"),
    "Oztas 2019": ("Turkey",
                   "School of Nursing, Yuksek Ihtisas University, Ankara, Turkey"),
    "Gao 2022": ("China",
                 "Department of Anesthesiology, Center for Brain Science, The First Affiliated "
                 "Hospital of Xi'an Jiaotong University, Xi'an, China"),
    "Song 2020": ("China",
                  "Department of Anesthesiology, Shengjing Hospital of China Medical "
                  "University, Shenyang, China"),
    "Wu 2016": ("China",
                "the Cancer Hospital of Harbin Medical University (Harbin, China)"),
    "Liu 2015": ("China",
                 "Department of Anesthesiology, Beijing 100093 China"),
    "Zhang 2018": ("China",
                   "Department of Gastroenterology, Changzheng Hospital affiliated to Second "
                   "Military Medical University, Shanghai, 200003, China"),
}


def apply(check_only: bool = False) -> int:
    raw = DATA_JS.read_text(encoding="utf-8")
    head, body = raw.split("window.STUDIES_DATA = ", 1)
    studies, end = json.JSONDecoder().raw_decode(body)
    tail = body[end:]

    changed, problems = [], []
    for s in studies:
        want = CONDUCT.get(s["key"])
        if not want:
            continue
        country, evidence = want
        if country not in META:
            problems.append(f"{s['key']}: no country_meta defined for {country!r}")
            continue
        if s.get("country") != country or s.get("country_meta") != META[country]:
            changed.append(f"{s['key']}: {s.get('country') or '(none)'} -> {country}")
        s["country"] = country
        s["country_meta"] = dict(META[country])
        s["country_evidence"] = evidence

    if problems:
        print("\n".join(problems), file=sys.stderr)
        return 1
    if check_only:
        if changed:
            print(f"OUT OF DATE: {len(changed)} country value(s) differ")
            for c in changed:
                print(f"  {c}")
            return 1
        print("country-of-conduct values are current")
        return 0

    DATA_JS.write_text(
        head + "window.STUDIES_DATA = "
        + json.dumps(studies, ensure_ascii=False, indent=2) + tail,
        encoding="utf-8")
    print(f"applied {len(changed)} country change(s)")
    for c in changed:
        print(f"  {c}")
    return 0


if __name__ == "__main__":
    sys.exit(apply(check_only="--check" in sys.argv))

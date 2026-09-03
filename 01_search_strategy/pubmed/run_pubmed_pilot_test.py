#!/usr/bin/env python3
"""Count PubMed v0.1 lines and test the frozen sentinel PMID intersection.

This script never retrieves the complete pilot result set. It performs three
count-only searches and one targeted search limited to sentinel PMIDs.
"""

from __future__ import annotations

import csv
from datetime import datetime
import json
import os
from pathlib import Path
import time
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET


ROOT = Path(__file__).resolve().parents[2]
PUBMED = ROOT / "01_search_strategy" / "pubmed"
SENTINELS = ROOT / "01_search_strategy" / "master" / "known_report_validation_set.csv"
ANIMAL_ONLY = "NOT (animals[mh] NOT humans[mh])"


def load(name: str) -> str:
    return " ".join((PUBMED / name).read_text(encoding="utf-8").split())


def esearch(term: str, retmax: int = 0) -> tuple[int, list[str]]:
    params = {
        "db": "pubmed",
        "term": term,
        "retmode": "xml",
        "retmax": str(retmax),
        "tool": "perioperative_teas_ea_review_2026",
    }
    api_key = os.environ.get("NCBI_API_KEY")
    if api_key:
        params["api_key"] = api_key
    url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi"
    request = urllib.request.Request(url, data=urllib.parse.urlencode(params).encode("utf-8"))
    with urllib.request.urlopen(request, timeout=60) as response:
        root = ET.fromstring(response.read())
    errors = [node.text or "" for node in root.findall(".//ERROR")]
    warnings = [node.text or "" for node in root.findall(".//Warning")]
    if errors or warnings:
        raise RuntimeError(f"NCBI query diagnostic: errors={errors!r}; warnings={warnings!r}")
    count = int(root.findtext("Count", "0"))
    ids = [node.text or "" for node in root.findall("./IdList/Id")]
    return count, ids


def main() -> None:
    teas = load("pubmed_v0_1_teas_line.txt")
    ea = load("pubmed_v0_1_ea_line.txt")
    surgery = load("pubmed_v0_1_surgery_line.txt")
    rct = load("pubmed_v0_1_rct_line.txt")
    teas_line = f"{teas} AND {surgery} AND {rct} {ANIMAL_ONLY}"
    ea_line = f"{ea} AND {surgery} AND {rct} {ANIMAL_ONLY}"
    combined = f"({teas} OR {ea}) AND {surgery} AND {rct} {ANIMAL_ONLY}"

    with SENTINELS.open(encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle))
    denominator = [row for row in rows if row["pubmed_recall_denominator"] == "yes"]
    pmids = [row["pmid"] for row in denominator]
    sentinel_clause = "(" + " OR ".join(f"{pmid}[pmid]" for pmid in pmids) + ")"

    results: dict[str, object] = {
        "database": "PubMed",
        "strategy_version": "v0.1",
        "executed_at_local": datetime.now().astimezone().isoformat(timespec="seconds"),
        "execution_type": "pilot count and targeted sentinel intersection; no full result retrieval",
        "ncbi_api_key_status": "available" if os.environ.get("NCBI_API_KEY") else "not_available",
        "counts": {},
    }
    for label, query in (("TEAS_line", teas_line), ("EA_line", ea_line), ("combined", combined)):
        count, _ = esearch(query, retmax=0)
        results["counts"][label] = count  # type: ignore[index]
        time.sleep(0.12 if os.environ.get("NCBI_API_KEY") else 0.36)
    teas_match_count, teas_matched = esearch(f"({teas_line}) AND {sentinel_clause}", retmax=len(pmids))
    time.sleep(0.12 if os.environ.get("NCBI_API_KEY") else 0.36)
    ea_match_count, ea_matched = esearch(f"({ea_line}) AND {sentinel_clause}", retmax=len(pmids))
    time.sleep(0.12 if os.environ.get("NCBI_API_KEY") else 0.36)
    match_count, matched = esearch(f"({combined}) AND {sentinel_clause}", retmax=len(pmids))
    matched_set = set(matched)
    results["sentinel_recall"] = {
        "numerator": sum(pmid in matched_set for pmid in pmids),
        "denominator": len(pmids),
        "intersection_count": match_count,
        "matched_pmids": sorted(matched_set, key=int),
        "missed_pmids": [pmid for pmid in pmids if pmid not in matched_set],
        "TEAS_line_intersection_count": teas_match_count,
        "TEAS_line_matched_pmids": sorted(set(teas_matched), key=int),
        "EA_line_intersection_count": ea_match_count,
        "EA_line_matched_pmids": sorted(set(ea_matched), key=int),
    }
    print(json.dumps(results, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()

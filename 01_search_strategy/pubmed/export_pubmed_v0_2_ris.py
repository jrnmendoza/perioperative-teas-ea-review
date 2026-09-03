#!/usr/bin/env python3
"""Retrieve PubMed v0.2 and create a deterministic Covidence-ready RIS.

The script preserves raw ESearch and EFetch XML, writes a PMID list and RIS,
validates one unique RIS record per unique PMID, and records checksums. It
refuses to overwrite an existing dated export directory.
"""

from __future__ import annotations

import csv
from datetime import datetime
import hashlib
import json
import os
from pathlib import Path
import re
import time
import urllib.error
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET


ROOT = Path(__file__).resolve().parents[2]
QUERY_FILE = ROOT / "01_search_strategy/pubmed/pubmed_v0_2_transport.txt"
SENTINEL_FILE = ROOT / "01_search_strategy/master/known_report_validation_set.csv"
RUN_DATE = datetime.now().astimezone().date().isoformat()
RUN_STAMP = datetime.now().astimezone().isoformat(timespec="seconds")
RAW_DIR = ROOT / f"02_search_exports/raw/pubmed/{RUN_DATE}_v0_2"
DERIVED_DIR = ROOT / f"02_search_exports/derived/pubmed/{RUN_DATE}_v0_2"
MANIFEST_DIR = ROOT / "02_search_exports/manifests"
BASE = f"PubMed_TEAS_EA_v0_2_{RUN_DATE}"


def normalize(value: str) -> str:
    return " ".join(value.replace("\r", " ").replace("\n", " ").split())


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def request_eutils(endpoint: str, params: dict[str, str]) -> bytes:
    payload = dict(params)
    payload["tool"] = "perioperative_teas_ea_review_2026"
    api_key = os.environ.get("NCBI_API_KEY")
    if api_key:
        payload["api_key"] = api_key
    request = urllib.request.Request(
        f"https://eutils.ncbi.nlm.nih.gov/entrez/eutils/{endpoint}",
        data=urllib.parse.urlencode(payload).encode("utf-8"),
    )
    for attempt in range(5):
        try:
            with urllib.request.urlopen(request, timeout=180) as response:
                return response.read()
        except urllib.error.HTTPError as exc:
            if exc.code not in {429, 500, 502, 503, 504} or attempt == 4:
                raise
            time.sleep(2 * (attempt + 1))
    raise RuntimeError("NCBI request retry loop exhausted")


def text_of(node: ET.Element | None) -> str:
    return normalize("".join(node.itertext())) if node is not None else ""


def unique(values: list[str]) -> list[str]:
    seen: set[str] = set()
    output: list[str] = []
    for value in values:
        value = normalize(value)
        if value and value not in seen:
            seen.add(value)
            output.append(value)
    return output


def article_date(article: ET.Element) -> tuple[str, str]:
    date_node = article.find("./MedlineCitation/Article/ArticleDate")
    if date_node is None:
        date_node = article.find("./MedlineCitation/Article/Journal/JournalIssue/PubDate")
    year = date_node.findtext("Year", "") if date_node is not None else ""
    month = date_node.findtext("Month", "") if date_node is not None else ""
    day = date_node.findtext("Day", "") if date_node is not None else ""
    if not year and date_node is not None:
        match = re.search(r"\b(18|19|20)\d{2}\b", date_node.findtext("MedlineDate", ""))
        year = match.group(0) if match else ""
    return year, "/".join(value for value in (year, month, day) if value)


def parse_article(article: ET.Element) -> dict[str, object]:
    pmid = article.findtext("./MedlineCitation/PMID", "").strip()
    if not re.fullmatch(r"\d+", pmid):
        raise ValueError(f"Missing or malformed PMID: {pmid!r}")
    article_node = article.find("./MedlineCitation/Article")
    if article_node is None:
        raise ValueError(f"PMID {pmid}: missing Article node")
    authors: list[str] = []
    for author in article_node.findall("./AuthorList/Author"):
        collective = author.findtext("CollectiveName", "")
        if collective:
            authors.append(collective)
            continue
        last = author.findtext("LastName", "")
        fore = author.findtext("ForeName", "") or author.findtext("Initials", "")
        name = ", ".join(value for value in (last, fore) if value)
        if name:
            authors.append(name)
    abstracts: list[str] = []
    for abstract in article_node.findall("./Abstract/AbstractText"):
        value = text_of(abstract)
        label = normalize(abstract.attrib.get("Label", ""))
        abstracts.append(f"{label}: {value}" if label and value else value)
    doi = ""
    for identifier in article.findall("./PubmedData/ArticleIdList/ArticleId"):
        if identifier.attrib.get("IdType") == "doi":
            doi = text_of(identifier)
            break
    if not doi:
        for identifier in article_node.findall("./ELocationID"):
            if identifier.attrib.get("EIdType") == "doi":
                doi = text_of(identifier)
                break
    year, date = article_date(article)
    mesh = [text_of(node) for node in article.findall("./MedlineCitation/MeshHeadingList/MeshHeading/DescriptorName")]
    return {
        "ris_type": "JOUR",
        "pmid": pmid,
        "title": text_of(article_node.find("./ArticleTitle")),
        "authors": unique(authors),
        "journal": text_of(article_node.find("./Journal/Title")),
        "journal_abbreviation": text_of(article.find("./MedlineCitation/MedlineJournalInfo/ISOAbbreviation")),
        "year": year,
        "date": date,
        "volume": text_of(article_node.find("./Journal/JournalIssue/Volume")),
        "issue": text_of(article_node.find("./Journal/JournalIssue/Issue")),
        "pages": text_of(article_node.find("./Pagination/MedlinePgn")),
        "abstract": normalize(" ".join(abstracts)),
        "doi": doi,
        "issn": text_of(article_node.find("./Journal/ISSN")),
        "languages": unique([text_of(node) for node in article_node.findall("./Language")]),
        "publication_types": unique([text_of(node) for node in article_node.findall("./PublicationTypeList/PublicationType")]),
        "mesh": unique(mesh),
        "url": f"https://pubmed.ncbi.nlm.nih.gov/{pmid}/",
    }


def parse_book(article: ET.Element) -> dict[str, object]:
    document = article.find("./BookDocument")
    if document is None:
        raise ValueError("PubmedBookArticle missing BookDocument")
    pmid = document.findtext("./PMID", "").strip()
    if not re.fullmatch(r"\d+", pmid):
        raise ValueError(f"Missing or malformed book PMID: {pmid!r}")
    authors: list[str] = []
    for author in document.findall("./AuthorList/Author"):
        collective = author.findtext("CollectiveName", "")
        if collective:
            authors.append(collective)
            continue
        last = author.findtext("LastName", "")
        fore = author.findtext("ForeName", "") or author.findtext("Initials", "")
        name = ", ".join(value for value in (last, fore) if value)
        if name:
            authors.append(name)
    date_node = document.find("./Book/PubDate")
    year = date_node.findtext("Year", "") if date_node is not None else ""
    month = date_node.findtext("Month", "") if date_node is not None else ""
    day = date_node.findtext("Day", "") if date_node is not None else ""
    abstracts: list[str] = []
    for abstract in document.findall("./Abstract/AbstractText"):
        value = text_of(abstract)
        label = normalize(abstract.attrib.get("Label", ""))
        abstracts.append(f"{label}: {value}" if label and value else value)
    return {
        "ris_type": "CHAP",
        "pmid": pmid,
        "title": text_of(document.find("./ArticleTitle")),
        "authors": unique(authors),
        "journal": text_of(document.find("./Book/BookTitle")),
        "journal_abbreviation": "",
        "year": year,
        "date": "/".join(value for value in (year, month, day) if value),
        "volume": "",
        "issue": "",
        "pages": "",
        "abstract": normalize(" ".join(abstracts)),
        "doi": "",
        "issn": "",
        "languages": unique([text_of(node) for node in document.findall("./Language")]),
        "publication_types": unique([text_of(node) for node in document.findall("./PublicationType")]),
        "mesh": [],
        "url": f"https://pubmed.ncbi.nlm.nih.gov/{pmid}/",
    }


def write_ris(path: Path, records: list[dict[str, object]]) -> None:
    lines: list[str] = []
    for record in records:
        pmid = str(record["pmid"])
        lines.extend([f"TY  - {record['ris_type']}", f"ID  - {pmid}", f"AN  - PMID:{pmid}"])
        mappings = (
            ("TI", record["title"]),
            ("T2", record["journal"]),
            ("JF", record["journal"]),
            ("JO", record["journal_abbreviation"]),
            ("PY", record["year"]),
            ("DA", record["date"]),
            ("VL", record["volume"]),
            ("IS", record["issue"]),
            ("SP", record["pages"]),
            ("AB", record["abstract"]),
            ("DO", record["doi"]),
            ("SN", record["issn"]),
        )
        if record["title"]:
            lines.append(f"TI  - {normalize(str(record['title']))}")
        for author in record["authors"]:  # type: ignore[union-attr]
            lines.append(f"AU  - {normalize(str(author))}")
        for tag, value in mappings[1:]:
            if value:
                lines.append(f"{tag}  - {normalize(str(value))}")
        for language in record["languages"]:  # type: ignore[union-attr]
            lines.append(f"LA  - {normalize(str(language))}")
        for publication_type in record["publication_types"]:  # type: ignore[union-attr]
            lines.append(f"M3  - {normalize(str(publication_type))}")
        for keyword in record["mesh"]:  # type: ignore[union-attr]
            lines.append(f"KW  - {normalize(str(keyword))}")
        lines.extend([f"N1  - PMID: {pmid}", f"UR  - {record['url']}", "ER  - ", ""])
    path.write_bytes("\r\n".join(lines).encode("utf-8"))


def main() -> None:
    if RAW_DIR.exists() or DERIVED_DIR.exists():
        raise FileExistsError("Refusing to overwrite an existing dated v0.2 export directory")
    RAW_DIR.mkdir(parents=True)
    DERIVED_DIR.mkdir(parents=True)
    MANIFEST_DIR.mkdir(parents=True, exist_ok=True)

    query = QUERY_FILE.read_text(encoding="utf-8").strip()
    query_sha = hashlib.sha256(query.encode("utf-8")).hexdigest()
    esearch_bytes = request_eutils(
        "esearch.fcgi",
        {"db": "pubmed", "term": query, "retmode": "xml", "retmax": "0", "usehistory": "y"},
    )
    esearch_path = RAW_DIR / f"{BASE}_ESearch.xml"
    esearch_path.write_bytes(esearch_bytes)
    esearch = ET.fromstring(esearch_bytes)
    count = int(esearch.findtext("Count", "0"))
    query_key = esearch.findtext("QueryKey", "")
    webenv = esearch.findtext("WebEnv", "")
    if not count or not query_key or not webenv:
        raise RuntimeError("ESearch did not return a usable count/history")

    efetch_bytes = request_eutils(
        "efetch.fcgi",
        {
            "db": "pubmed",
            "query_key": query_key,
            "WebEnv": webenv,
            "retmode": "xml",
            "rettype": "abstract",
            "retstart": "0",
            "retmax": str(count),
        },
    )
    xml_path = RAW_DIR / f"{BASE}_Records.xml"
    xml_path.write_bytes(efetch_bytes)
    root = ET.fromstring(efetch_bytes)
    articles = root.findall("./PubmedArticle")
    books = root.findall("./PubmedBookArticle")
    records: list[dict[str, object]] = []
    for child in root:
        if child.tag == "PubmedArticle":
            records.append(parse_article(child))
        elif child.tag == "PubmedBookArticle":
            records.append(parse_book(child))
        else:
            raise RuntimeError(f"Unexpected PubMed XML record type: {child.tag}")
    pmids = [str(record["pmid"]) for record in records]
    if len(records) != count or len(set(pmids)) != count:
        raise RuntimeError(f"Count mismatch: ESearch={count}, XML={len(records)}, unique PMIDs={len(set(pmids))}")

    pmid_path = DERIVED_DIR / f"{BASE}_PMIDs.txt"
    pmid_path.write_text("\n".join(pmids) + "\n", encoding="utf-8")
    ris_path = DERIVED_DIR / f"Covidence_{BASE}_N-{count}.ris"
    write_ris(ris_path, records)
    ris_text = ris_path.read_text(encoding="utf-8")
    ris_pmids = re.findall(r"(?m)^AN  - PMID:(\d+)\s*$", ris_text)
    if len(ris_pmids) != count or len(set(ris_pmids)) != count or set(ris_pmids) != set(pmids):
        raise RuntimeError("RIS validation failed")
    if len(re.findall(r"(?m)^TY  - \S+\s*$", ris_text)) != count:
        raise RuntimeError("RIS TY record count failed")
    if len(re.findall(r"(?m)^ER  -\s*$", ris_text)) != count:
        raise RuntimeError("RIS ER record count failed")

    with SENTINEL_FILE.open(encoding="utf-8", newline="") as handle:
        sentinel_rows = [row for row in csv.DictReader(handle) if row["pubmed_recall_denominator"] == "yes"]
    sentinel_pmids = [row["pmid"] for row in sentinel_rows]
    retrieved_sentinels = [pmid for pmid in sentinel_pmids if pmid in set(pmids)]
    missed_sentinels = [pmid for pmid in sentinel_pmids if pmid not in set(pmids)]

    files = [QUERY_FILE, esearch_path, xml_path, pmid_path, ris_path]
    manifest = {
        "review": "Perioperative_TEAS_EA_Review_2026",
        "database": "PubMed",
        "strategy_version": "v0.2",
        "status": "full PubMed citation export prepared for manual Covidence upload; not uploaded",
        "run_timestamp": RUN_STAMP,
        "query_sha256": query_sha,
        "ncbi_api_key_status": "available" if os.environ.get("NCBI_API_KEY") else "not_available",
        "esearch_count": count,
        "xml_record_count": len(records),
        "xml_journal_article_count": len(articles),
        "xml_book_article_count": len(books),
        "unique_pmid_count": len(set(pmids)),
        "ris_record_count": len(ris_pmids),
        "sentinel_recall": {
            "numerator": len(retrieved_sentinels),
            "denominator": len(sentinel_pmids),
            "missed_pmids": missed_sentinels,
        },
        "files": [
            {"path": str(path.relative_to(ROOT)), "bytes": path.stat().st_size, "sha256": sha256(path)}
            for path in files
        ],
    }
    manifest_path = MANIFEST_DIR / f"{BASE}_manifest.json"
    manifest_path.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"count": count, "ris": str(ris_path), "manifest": str(manifest_path), "sentinel_recall": manifest["sentinel_recall"]}, indent=2))


if __name__ == "__main__":
    main()

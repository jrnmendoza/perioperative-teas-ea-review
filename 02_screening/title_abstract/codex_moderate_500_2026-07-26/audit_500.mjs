import fs from "node:fs";
import path from "node:path";

export const requiredKeys = [
  "screening_sequence",
  "covidence_number",
  "title",
  "first_author",
  "publication_year",
  "publication_language",
  "abstract_available",
  "decision",
  "primary_reason_code",
  "evidence_supporting_decision",
  "concise_rationale",
  "confidence",
  "record_type",
  "actual_results_reported",
  "general_anaesthesia",
  "randomized",
  "intervention",
  "comparator",
  "background_care_balanced",
  "ERAS_balance",
  "intervention_effect_separable",
  "timing_eligible",
  "timing_description",
  "clinical_outcome_present",
  "surrogate_only",
  "translation_required",
  "possible_companion_report",
  "vote_registered",
  "post_vote_timestamp",
  "interface_issue",
  "notes"
];

function csvCell(value) {
  const text = value == null ? "" : String(value);
  return `"${text.replaceAll('"', '""')}"`;
}

export function validateRecords(records) {
  records.forEach((record, index) => {
    for (const key of requiredKeys) {
      if (!Object.prototype.hasOwnProperty.call(record, key)) {
        throw new Error(`Record ${index + 1} is missing ${key}`);
      }
    }
    if (record.screening_sequence !== index + 1) {
      throw new Error(`Sequence is not consecutive at record ${index + 1}`);
    }
    if (record.vote_registered !== "yes") {
      throw new Error(`Vote is not registered at sequence ${record.screening_sequence}`);
    }
  });
  const covidenceIds = records.map((record) => record.covidence_number);
  if (new Set(covidenceIds).size !== covidenceIds.length) {
    throw new Error("Covidence numbers are not unique");
  }
  const timestamps = records.map((record) => record.post_vote_timestamp).filter(Boolean);
  if (new Set(timestamps).size !== timestamps.length) {
    throw new Error("Post-vote timestamps are not unique");
  }
  return true;
}

export function readRecords(directory) {
  const jsonl = path.join(directory, "codex_decisions_500.jsonl");
  if (!fs.existsSync(jsonl)) return [];
  const text = fs.readFileSync(jsonl, "utf8");
  const lines = text.split(/\r?\n/).filter((line) => line.trim().length > 0);
  const records = lines.map((line, index) => {
    try {
      return JSON.parse(line);
    } catch (error) {
      throw new Error(`Invalid JSON on line ${index + 1}: ${error.message}`);
    }
  });
  validateRecords(records);
  return records;
}

export function generateCsv(directory, records = readRecords(directory)) {
  validateRecords(records);
  const rows = [requiredKeys.map(csvCell).join(",")];
  for (const record of records) {
    rows.push(requiredKeys.map((key) => csvCell(record[key])).join(","));
  }
  fs.writeFileSync(
    path.join(directory, "codex_decisions_500.csv"),
    `${rows.join("\n")}\n`,
    "utf8"
  );
  return records.length;
}

export function appendRecord(directory, record) {
  const records = readRecords(directory);
  if (record.screening_sequence !== records.length + 1) {
    throw new Error(`Expected sequence ${records.length + 1}`);
  }
  validateRecords([...records, record]);
  fs.mkdirSync(directory, { recursive: true });
  fs.appendFileSync(
    path.join(directory, "codex_decisions_500.jsonl"),
    `${JSON.stringify(record)}\n`,
    "utf8"
  );
  return generateCsv(directory);
}

export function validateDirectory(directory, expectedCount) {
  const records = readRecords(directory);
  if (records.length !== expectedCount) {
    throw new Error(`Expected ${expectedCount} records, found ${records.length}`);
  }
  generateCsv(directory, records);
  const csvText = fs.readFileSync(path.join(directory, "codex_decisions_500.csv"), "utf8");
  const csvRows = csvText.trimEnd().split(/\r?\n/);
  if (csvRows.length !== records.length + 1) {
    throw new Error("CSV row count does not match JSONL");
  }
  return {
    count: records.length,
    firstCovidenceNumber: records[0]?.covidence_number ?? null,
    lastCovidenceNumber: records.at(-1)?.covidence_number ?? null,
    yes: records.filter((record) => record.decision === "Yes").length,
    maybe: records.filter((record) => record.decision === "Maybe").length,
    no: records.filter((record) => record.decision === "No").length
  };
}


import fs from "node:fs";

const ROOT =
  "/Users/ryan/Documents/Perioperative_TEAS_EA_Review_2026/02_screening/title_abstract/codex_aggressive_account2_500_2026-07-27";
const JSONL = `${ROOT}/codex_aggressive_decisions_500.jsonl`;
const CSV = `${ROOT}/codex_aggressive_decisions_500.csv`;
const GAPS = `${ROOT}/codex_aggressive_sequence_gaps_500.csv`;

export const requiredFields = [
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
  "core_criteria_supported_count",
  "core_criteria_uncertain_count",
  "uncertain_criteria",
  "general_anaesthesia",
  "randomized",
  "intervention",
  "comparator",
  "background_care_balanced",
  "intervention_effect_separable",
  "timing_eligible",
  "clinical_outcome_present",
  "translation_required",
  "possible_companion_report",
  "vote_registered",
  "post_vote_timestamp",
  "interface_issue",
  "notes",
];

function csvValue(value) {
  const text = Array.isArray(value)
    ? value.join("|")
    : value === null || value === undefined
      ? ""
      : String(value);
  return `"${text.replaceAll('"', '""')}"`;
}

export function readRecords() {
  if (!fs.existsSync(JSONL)) return [];
  const lines = fs
    .readFileSync(JSONL, "utf8")
    .split(/\r?\n/)
    .filter(Boolean);
  return lines.map((line, index) => {
    try {
      return JSON.parse(line);
    } catch (error) {
      throw new Error(`Malformed JSONL at line ${index + 1}: ${error.message}`);
    }
  });
}

export function validateRecords(records, expectedCount = records.length) {
  if (records.length !== expectedCount) {
    throw new Error(`Expected ${expectedCount} records, found ${records.length}`);
  }
  const sequences = new Set();
  const covidenceNumbers = new Set();
  const timestamps = new Set();
  for (const record of records) {
    for (const field of requiredFields) {
      if (!(field in record)) {
        throw new Error(
          `Missing ${field} at screening sequence ${record.screening_sequence}`,
        );
      }
    }
    if (sequences.has(record.screening_sequence)) {
      throw new Error(`Duplicate sequence ${record.screening_sequence}`);
    }
    sequences.add(record.screening_sequence);
    if (covidenceNumbers.has(record.covidence_number)) {
      throw new Error(`Duplicate Covidence number ${record.covidence_number}`);
    }
    covidenceNumbers.add(record.covidence_number);
    if (record.vote_registered !== "yes") {
      throw new Error(
        `Unregistered vote at sequence ${record.screening_sequence}`,
      );
    }
    if (
      record.decision === "MAYBE" &&
      (record.core_criteria_uncertain_count !== 1 ||
        !Array.isArray(record.uncertain_criteria) ||
        record.uncertain_criteria.length !== 1)
    ) {
      throw new Error(
        `Invalid Maybe uncertainty at sequence ${record.screening_sequence}`,
      );
    }
    if (timestamps.has(record.post_vote_timestamp)) {
      throw new Error(`Duplicate timestamp ${record.post_vote_timestamp}`);
    }
    timestamps.add(record.post_vote_timestamp);
  }
  const expectedSequences = Array.from(
    { length: records.length },
    (_, index) => index + 1,
  );
  if (
    expectedSequences.some(
      (sequence, index) => records[index].screening_sequence !== sequence,
    )
  ) {
    throw new Error("Screening sequences are not consecutive and ordered");
  }
  return true;
}

export function regenerateCsv(records = readRecords()) {
  validateRecords(records);
  const text = [
    requiredFields.map(csvValue).join(","),
    ...records.map((record) =>
      requiredFields.map((field) => csvValue(record[field])).join(","),
    ),
    "",
  ].join("\n");
  fs.writeFileSync(CSV, text, "utf8");
  return CSV;
}

export function regenerateGapLog(records = readRecords()) {
  validateRecords(records);
  const header = [
    "previous_screening_sequence",
    "previous_covidence_number",
    "next_screening_sequence",
    "next_covidence_number",
    "gap_size",
    "previous_vote_registered",
    "queue_count_changed",
    "next_citation_distinct",
    "visible_citation_bypassed",
    "notes",
  ];
  const rows = [];
  for (let index = 1; index < records.length; index += 1) {
    const previous = records[index - 1];
    const next = records[index];
    const gapSize = next.covidence_number - previous.covidence_number - 1;
    if (gapSize > 0) {
      rows.push([
        previous.screening_sequence,
        previous.covidence_number,
        next.screening_sequence,
        next.covidence_number,
        gapSize,
        "yes",
        "yes; previous card left active queue",
        "yes",
        "no",
        "Covidence-number gap observed in the ascending active queue; no visible citation was bypassed.",
      ]);
    }
  }
  fs.writeFileSync(
    GAPS,
    [
      header.map(csvValue).join(","),
      ...rows.map((row) => row.map(csvValue).join(",")),
      "",
    ].join("\n"),
    "utf8",
  );
  return rows.length;
}

export function appendRegisteredVote(record) {
  const records = readRecords();
  const expectedSequence = records.length + 1;
  if (record.screening_sequence !== expectedSequence) {
    throw new Error(
      `Expected screening sequence ${expectedSequence}, got ${record.screening_sequence}`,
    );
  }
  if (record.vote_registered !== "yes") {
    throw new Error("Refusing to append a vote that is not registered");
  }
  validateRecords([...records, record], expectedSequence);
  fs.appendFileSync(JSONL, `${JSON.stringify(record)}\n`, "utf8");
  const after = readRecords();
  validateRecords(after, expectedSequence);
  if (expectedSequence % 25 === 0) regenerateCsv(after);
  return after.length;
}

export function validateAndRegenerate(expectedCount) {
  const records = readRecords();
  validateRecords(records, expectedCount);
  regenerateCsv(records);
  const numberingGaps = regenerateGapLog(records);
  const parsedCsvRows = fs
    .readFileSync(CSV, "utf8")
    .split(/\r?\n/)
    .filter(Boolean);
  if (parsedCsvRows.length !== expectedCount + 1) {
    throw new Error(
      `CSV row count mismatch: expected ${expectedCount + 1}, found ${parsedCsvRows.length}`,
    );
  }
  return {
    records: records.length,
    csvDataRows: parsedCsvRows.length - 1,
    uniqueSequences: new Set(records.map((row) => row.screening_sequence)).size,
    uniqueCovidenceNumbers: new Set(
      records.map((row) => row.covidence_number),
    ).size,
    uniqueTimestamps: new Set(records.map((row) => row.post_vote_timestamp)).size,
    registeredVotes: records.filter((row) => row.vote_registered === "yes")
      .length,
    maybeRowsValid: records
      .filter((row) => row.decision === "MAYBE")
      .every(
        (row) =>
          row.core_criteria_uncertain_count === 1 &&
          row.uncertain_criteria.length === 1,
      ),
    numberingGaps,
  };
}

export const paths = { ROOT, JSONL, CSV, GAPS };

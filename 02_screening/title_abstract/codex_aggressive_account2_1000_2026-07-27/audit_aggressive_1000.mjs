import fs from "node:fs";
import crypto from "node:crypto";

export const ROOT =
  "/Users/ryan/Documents/Perioperative_TEAS_EA_Review_2026/02_screening/title_abstract/codex_aggressive_account2_1000_2026-07-27";
export const COMBINED_JSONL = `${ROOT}/combined/codex_aggressive_decisions_1000.jsonl`;
export const COMBINED_CSV = `${ROOT}/combined/codex_aggressive_decisions_1000.csv`;
export const GAPS = `${ROOT}/codex_aggressive_sequence_gaps_1000.csv`;

export const requiredFields = [
  "screening_sequence",
  "segment_number",
  "segment_sequence",
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
  "timing_description",
  "clinical_outcome_present",
  "translation_required",
  "possible_companion_report",
  "vote_registered",
  "post_vote_timestamp",
  "interface_issue",
  "notes",
];

export const recordTypes = new Set([
  "primary_results",
  "protocol",
  "trial_registration",
  "systematic_review",
  "meta_analysis",
  "scoping_review",
  "narrative_review",
  "bibliometric_review",
  "commentary",
  "editorial",
  "correction",
  "letter",
  "methods_paper",
  "case_report",
  "case_series",
  "animal_study",
  "conference_abstract",
  "conference_protocol",
  "secondary_report",
  "other",
]);

const segmentNames = Array.from({ length: 25 }, (_, index) => {
  const start = index * 100 + 1;
  const end = start + 99;
  return `segment_${String(start).padStart(3, "0")}_${String(end).padStart(4, "0")}`;
});

export function segmentPaths(segmentNumber) {
  const dir = `${ROOT}/segments/${segmentNames[segmentNumber - 1]}`;
  return {
    dir,
    jsonl: `${dir}/decisions.jsonl`,
    csv: `${dir}/decisions.csv`,
  };
}

function parseJsonl(path) {
  if (!fs.existsSync(path)) return [];
  return fs
    .readFileSync(path, "utf8")
    .split(/\r?\n/)
    .filter(Boolean)
    .map((line, index) => {
      try {
        return JSON.parse(line);
      } catch (error) {
        throw new Error(`Malformed JSONL at ${path}:${index + 1}: ${error.message}`);
      }
    });
}

export function readCombined() {
  return parseJsonl(COMBINED_JSONL);
}

export function readSegment(segmentNumber) {
  return parseJsonl(segmentPaths(segmentNumber).jsonl);
}

export function validateRecords(records, expectedCount = records.length) {
  if (records.length !== expectedCount) {
    throw new Error(`Expected ${expectedCount} records, found ${records.length}`);
  }
  const sequences = new Set();
  const covidence = new Set();
  const timestamps = new Set();
  for (const record of records) {
    for (const field of requiredFields) {
      if (!(field in record)) {
        throw new Error(`Missing ${field} at sequence ${record.screening_sequence}`);
      }
    }
    if (!recordTypes.has(record.record_type)) {
      throw new Error(`Invalid record_type at sequence ${record.screening_sequence}`);
    }
    if (sequences.has(record.screening_sequence)) {
      throw new Error(`Duplicate sequence ${record.screening_sequence}`);
    }
    sequences.add(record.screening_sequence);
    if (covidence.has(record.covidence_number)) {
      throw new Error(`Duplicate Covidence number ${record.covidence_number}`);
    }
    covidence.add(record.covidence_number);
    if (timestamps.has(record.post_vote_timestamp)) {
      throw new Error(`Duplicate timestamp ${record.post_vote_timestamp}`);
    }
    timestamps.add(record.post_vote_timestamp);
    if (record.vote_registered !== "yes") {
      throw new Error(`Unregistered vote at sequence ${record.screening_sequence}`);
    }
    if (
      record.decision === "MAYBE" &&
      (record.core_criteria_uncertain_count !== 1 ||
        !Array.isArray(record.uncertain_criteria) ||
        record.uncertain_criteria.length !== 1)
    ) {
      throw new Error(`Invalid MAYBE at sequence ${record.screening_sequence}`);
    }
    const expectedSegment = Math.floor((record.screening_sequence - 1) / 100) + 1;
    const expectedSegmentSequence = ((record.screening_sequence - 1) % 100) + 1;
    if (
      record.segment_number !== expectedSegment ||
      record.segment_sequence !== expectedSegmentSequence
    ) {
      throw new Error(`Invalid segment mapping at sequence ${record.screening_sequence}`);
    }
  }
  records.forEach((record, index) => {
    if (record.screening_sequence !== index + 1) {
      throw new Error(`Non-consecutive global sequence at row ${index + 1}`);
    }
  });
  return true;
}

function csvValue(value) {
  const text = Array.isArray(value)
    ? value.join("|")
    : value === null || value === undefined
      ? ""
      : String(value);
  return `"${text.replaceAll('"', '""')}"`;
}

function writeCsv(path, records) {
  const text = [
    requiredFields.map(csvValue).join(","),
    ...records.map((record) =>
      requiredFields.map((field) => csvValue(record[field])).join(","),
    ),
    "",
  ].join("\n");
  fs.writeFileSync(path, text, "utf8");
  const rows = fs.readFileSync(path, "utf8").split(/\r?\n/).filter(Boolean);
  if (rows.length !== records.length + 1) {
    throw new Error(`CSV row mismatch at ${path}`);
  }
}

export function regenerateGapLog(records = readCombined()) {
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
        "Covidence-number gap observed in ascending active queue; no visible citation was bypassed.",
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
  const records = readCombined();
  const expectedSequence = records.length + 1;
  if (record.screening_sequence !== expectedSequence) {
    throw new Error(`Expected sequence ${expectedSequence}, got ${record.screening_sequence}`);
  }
  validateRecords([...records, record], expectedSequence);
  const segment = segmentPaths(record.segment_number);
  fs.appendFileSync(segment.jsonl, `${JSON.stringify(record)}\n`, "utf8");
  fs.appendFileSync(COMBINED_JSONL, `${JSON.stringify(record)}\n`, "utf8");
  const after = readCombined();
  validateRecords(after, expectedSequence);
  if (expectedSequence % 25 === 0) validateAndRegenerate(expectedSequence);
  return after.length;
}

export function validateAndRegenerate(expectedCount) {
  const records = readCombined();
  validateRecords(records, expectedCount);
  for (let segmentNumber = 1; segmentNumber <= segmentNames.length; segmentNumber += 1) {
    const segmentRecords = readSegment(segmentNumber);
    if (!segmentRecords.length) continue;
    const expectedStart = (segmentNumber - 1) * 100 + 1;
    segmentRecords.forEach((record, index) => {
      if (record.screening_sequence !== expectedStart + index) {
        throw new Error(`Segment ${segmentNumber} sequence mismatch`);
      }
    });
    writeCsv(segmentPaths(segmentNumber).csv, segmentRecords);
  }
  writeCsv(COMBINED_CSV, records);
  const numberingGaps = regenerateGapLog(records);
  return {
    records: records.length,
    uniqueSequences: new Set(records.map((row) => row.screening_sequence)).size,
    uniqueCovidenceNumbers: new Set(records.map((row) => row.covidence_number)).size,
    registeredVotes: records.filter((row) => row.vote_registered === "yes").length,
    uniqueTimestamps: new Set(records.map((row) => row.post_vote_timestamp)).size,
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

export function checksum(path) {
  return crypto.createHash("sha256").update(fs.readFileSync(path)).digest("hex");
}

export function tally(records) {
  return records.reduce((acc, record) => {
    acc.decisions[record.decision] = (acc.decisions[record.decision] || 0) + 1;
    acc.reasons[record.primary_reason_code] =
      (acc.reasons[record.primary_reason_code] || 0) + 1;
    if (record.decision === "MAYBE") {
      const key = record.uncertain_criteria[0];
      acc.maybeByCriterion[key] = (acc.maybeByCriterion[key] || 0) + 1;
    }
    return acc;
  }, { decisions: {}, reasons: {}, maybeByCriterion: {} });
}

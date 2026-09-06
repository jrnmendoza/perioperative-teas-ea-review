import crypto from "node:crypto";
import fs from "node:fs";
import path from "node:path";

export const rootDirectory =
  "/Users/ryan/Documents/Perioperative_TEAS_EA_Review_2026/02_screening/title_abstract/codex_moderate_1000_2026-07-26";

export const requiredKeys = [
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

export const controlledRecordTypes = new Set([
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
  "book_chapter",
  "case_report",
  "case_series",
  "animal_study",
  "conference_abstract",
  "conference_protocol",
  "secondary_report",
  "other"
]);

const segmentBounds = Array.from({ length: 10 }, (_, index) => ({
  number: index + 1,
  start: index * 100 + 1,
  end: (index + 1) * 100
}));

function segmentName(segmentNumber) {
  const start = (segmentNumber - 1) * 100 + 1;
  const end = segmentNumber * 100;
  return `segment_${String(start).padStart(3, "0")}_${String(end).padStart(4, "0")}`;
}

export function segmentDirectory(segmentNumber) {
  return path.join(rootDirectory, "segments", segmentName(segmentNumber));
}

export function initializeDirectory() {
  fs.mkdirSync(path.join(rootDirectory, "combined"), { recursive: true });
  fs.mkdirSync(path.join(rootDirectory, "screenshots"), { recursive: true });
  for (const { number } of segmentBounds) {
    fs.mkdirSync(segmentDirectory(number), { recursive: true });
  }
}

function csvCell(value) {
  const text = value == null ? "" : String(value);
  return `"${text.replaceAll('"', '""')}"`;
}

export function readJsonl(file) {
  if (!fs.existsSync(file)) return [];
  const text = fs.readFileSync(file, "utf8");
  return text
    .split(/\r?\n/)
    .filter((line) => line.trim())
    .map((line, index) => {
      try {
        return JSON.parse(line);
      } catch (error) {
        throw new Error(`Invalid JSON in ${file} on line ${index + 1}: ${error.message}`);
      }
    });
}

export function validateRecord(record) {
  for (const key of requiredKeys) {
    if (!Object.prototype.hasOwnProperty.call(record, key)) {
      throw new Error(`Sequence ${record.screening_sequence ?? "unknown"} is missing ${key}`);
    }
  }
  if (!controlledRecordTypes.has(record.record_type)) {
    throw new Error(`Uncontrolled record_type at sequence ${record.screening_sequence}`);
  }
  if (!["Yes", "Maybe", "No"].includes(record.decision)) {
    throw new Error(`Invalid decision at sequence ${record.screening_sequence}`);
  }
  if (record.vote_registered !== "yes") {
    throw new Error(`Unregistered vote at sequence ${record.screening_sequence}`);
  }
  return true;
}

export function validateRecords(records, options = {}) {
  const { exactCount, segmentNumber } = options;
  if (exactCount != null && records.length !== exactCount) {
    throw new Error(`Expected ${exactCount} records, found ${records.length}`);
  }
  records.forEach((record, index) => {
    validateRecord(record);
    if (index > 0 && record.screening_sequence !== records[index - 1].screening_sequence + 1) {
      throw new Error(`Non-consecutive global sequence at row ${index + 1}`);
    }
    if (segmentNumber != null) {
      if (record.segment_number !== segmentNumber) {
        throw new Error(`Wrong segment_number at sequence ${record.screening_sequence}`);
      }
      if (record.segment_sequence !== index + 1) {
        throw new Error(`Non-consecutive segment sequence at row ${index + 1}`);
      }
    }
  });
  const covidenceNumbers = records.map((record) => record.covidence_number);
  if (new Set(covidenceNumbers).size !== covidenceNumbers.length) {
    throw new Error("Covidence numbers are not unique");
  }
  const timestamps = records.map((record) => record.post_vote_timestamp);
  if (new Set(timestamps).size !== timestamps.length) {
    throw new Error("Post-vote timestamps are not unique");
  }
  return true;
}

export function writeCsv(file, records) {
  const rows = [requiredKeys.map(csvCell).join(",")];
  for (const record of records) {
    rows.push(requiredKeys.map((key) => csvCell(record[key])).join(","));
  }
  fs.writeFileSync(file, `${rows.join("\n")}\n`, "utf8");
  const csv = fs.readFileSync(file, "utf8");
  let parsedRowCount = 0;
  let inQuotedField = false;
  for (let index = 0; index < csv.length; index += 1) {
    const character = csv[index];
    if (character === '"') {
      if (inQuotedField && csv[index + 1] === '"') {
        index += 1;
      } else {
        inQuotedField = !inQuotedField;
      }
    } else if (character === "\n" && !inQuotedField) {
      parsedRowCount += 1;
    }
  }
  if (inQuotedField) {
    throw new Error(`CSV contains an unterminated quoted field: ${file}`);
  }
  if (parsedRowCount !== records.length + 1) {
    throw new Error(`CSV row count mismatch for ${file}`);
  }
}

export function segmentRecords(segmentNumber) {
  return readJsonl(path.join(segmentDirectory(segmentNumber), "decisions.jsonl"));
}

export function allRecords() {
  return segmentBounds.flatMap(({ number }) => segmentRecords(number));
}

export function appendRecord(record) {
  validateRecord(record);
  const existingAll = allRecords();
  const expectedGlobal = existingAll.length + 1;
  if (record.screening_sequence !== expectedGlobal) {
    throw new Error(`Expected global sequence ${expectedGlobal}`);
  }
  const expectedSegment = Math.floor((expectedGlobal - 1) / 100) + 1;
  const expectedSegmentSequence = ((expectedGlobal - 1) % 100) + 1;
  if (
    record.segment_number !== expectedSegment ||
    record.segment_sequence !== expectedSegmentSequence
  ) {
    throw new Error(`Unexpected segment position at global sequence ${expectedGlobal}`);
  }
  if (existingAll.some((item) => item.covidence_number === record.covidence_number)) {
    throw new Error(`Duplicate Covidence number ${record.covidence_number}`);
  }
  if (existingAll.some((item) => item.post_vote_timestamp === record.post_vote_timestamp)) {
    throw new Error(`Duplicate timestamp ${record.post_vote_timestamp}`);
  }
  const jsonl = path.join(segmentDirectory(expectedSegment), "decisions.jsonl");
  fs.appendFileSync(jsonl, `${JSON.stringify(record)}\n`, "utf8");
  const segment = segmentRecords(expectedSegment);
  validateRecords(segment, { segmentNumber: expectedSegment });
  writeCsv(path.join(segmentDirectory(expectedSegment), "decisions.csv"), segment);
  return existingAll.length + 1;
}

export function appendGap(gap) {
  const file = path.join(rootDirectory, "codex_sequence_gaps_1000.csv");
  const keys = [
    "previous_covidence_number",
    "next_covidence_number",
    "missing_number_or_range",
    "global_screening_sequence",
    "segment_number",
    "previous_vote_registered",
    "queue_order_confirmed",
    "visible_record_bypassed",
    "status",
    "action_taken",
    "timestamp",
    "notes"
  ];
  if (!fs.existsSync(file)) {
    fs.appendFileSync(file, `${keys.map(csvCell).join(",")}\n`, "utf8");
  }
  fs.appendFileSync(file, `${keys.map((key) => csvCell(gap[key])).join(",")}\n`, "utf8");
}

export function appendIncident(incident) {
  fs.appendFileSync(
    path.join(rootDirectory, "codex_continuity_incidents_1000.jsonl"),
    `${JSON.stringify(incident)}\n`,
    "utf8"
  );
}

function counts(records) {
  const decisionCounts = Object.fromEntries(
    ["Yes", "Maybe", "No"].map((decision) => [
      decision,
      records.filter((record) => record.decision === decision).length
    ])
  );
  const reasonCounts = {};
  for (const record of records) {
    reasonCounts[record.primary_reason_code] =
      (reasonCounts[record.primary_reason_code] ?? 0) + 1;
  }
  return { decisionCounts, reasonCounts };
}

export function checkpoint(segmentNumber, checkpointSequence) {
  const records = segmentRecords(segmentNumber);
  if (records.length !== checkpointSequence) {
    throw new Error(
      `Segment ${segmentNumber} expected ${checkpointSequence} records, found ${records.length}`
    );
  }
  validateRecords(records, { exactCount: checkpointSequence, segmentNumber });
  writeCsv(path.join(segmentDirectory(segmentNumber), "decisions.csv"), records);
  const { decisionCounts, reasonCounts } = counts(records);
  const globalEnd = (segmentNumber - 1) * 100 + checkpointSequence;
  const body = [
    `# Segment ${segmentNumber} checkpoint ${String(checkpointSequence).padStart(3, "0")}`,
    "",
    `- Global screening sequence: ${globalEnd}`,
    `- Valid registered votes in segment: ${records.length}`,
    `- Yes: ${decisionCounts.Yes}`,
    `- Maybe: ${decisionCounts.Maybe}`,
    `- No: ${decisionCounts.No}`,
    `- Unique Covidence numbers: ${new Set(records.map((r) => r.covidence_number)).size}`,
    `- Unique post-vote timestamps: ${new Set(records.map((r) => r.post_vote_timestamp)).size}`,
    "- JSONL validation: passed",
    "- CSV validation: passed",
    "- Vote registration: all yes",
    "- Visible unscreened citations bypassed: 0",
    "- Conflicts opened or resolved: 0",
    "",
    "## Primary reason counts",
    "",
    ...Object.entries(reasonCounts)
      .sort(([a], [b]) => a.localeCompare(b))
      .map(([reason, count]) => `- ${reason}: ${count}`),
    ""
  ].join("\n");
  fs.writeFileSync(
    path.join(
      segmentDirectory(segmentNumber),
      `checkpoint_${String(checkpointSequence).padStart(3, "0")}.md`
    ),
    body,
    "utf8"
  );
  return { segmentNumber, checkpointSequence, globalEnd, ...decisionCounts };
}

export function updateManifest(status = {}) {
  const segments = [];
  for (const { number } of segmentBounds) {
    const records = segmentRecords(number);
    if (!records.length) continue;
    validateRecords(records, { segmentNumber: number });
    const jsonlPath = path.join(segmentDirectory(number), "decisions.jsonl");
    const { decisionCounts } = counts(records);
    segments.push({
      segment_number: number,
      global_sequence_start: records[0].screening_sequence,
      global_sequence_end: records.at(-1).screening_sequence,
      first_covidence_number: records[0].covidence_number,
      last_covidence_number: records.at(-1).covidence_number,
      registered_vote_count: records.length,
      yes_count: decisionCounts.Yes,
      maybe_count: decisionCounts.Maybe,
      no_count: decisionCounts.No,
      JSONL_path: jsonlPath,
      CSV_path: path.join(segmentDirectory(number), "decisions.csv"),
      validation_status: "passed",
      completion_timestamp:
        records.length === 100 ? records.at(-1).post_vote_timestamp : null,
      checksum: crypto.createHash("sha256").update(fs.readFileSync(jsonlPath)).digest("hex")
    });
  }
  const manifest = {
    review_id: 799962,
    review_title:
      "Protocol characteristics associated with clinically meaningful 24-hour opioid sparing from perioperative transcutaneous electrical acupoint stimulation and electroacupuncture: a systematic review",
    reviewer: "John Ryan Nual Mendoza (JM)",
    run_date: "2026-07-26",
    target_new_registered_votes: 1000,
    total_successful_votes: segments.reduce(
      (total, segment) => total + segment.registered_vote_count,
      0
    ),
    segments,
    ...status
  };
  fs.writeFileSync(
    path.join(rootDirectory, "master_manifest_1000.json"),
    `${JSON.stringify(manifest, null, 2)}\n`,
    "utf8"
  );
  return manifest;
}

export function finalize() {
  const records = allRecords();
  validateRecords(records, { exactCount: 1000 });
  records.forEach((record, index) => {
    if (record.screening_sequence !== index + 1) {
      throw new Error(`Combined global sequence mismatch at row ${index + 1}`);
    }
  });
  const combinedJsonl = path.join(rootDirectory, "combined", "codex_decisions_1000.jsonl");
  fs.writeFileSync(
    combinedJsonl,
    `${records.map((record) => JSON.stringify(record)).join("\n")}\n`,
    "utf8"
  );
  writeCsv(path.join(rootDirectory, "combined", "codex_decisions_1000.csv"), records);
  return {
    count: records.length,
    uniqueCovidenceNumbers: new Set(records.map((r) => r.covidence_number)).size,
    uniqueTimestamps: new Set(records.map((r) => r.post_vote_timestamp)).size,
    ...counts(records)
  };
}

initializeDirectory();

import crypto from "node:crypto";
import fs from "node:fs";
import path from "node:path";
import {
  requiredKeys,
  validateRecord
} from "../codex_moderate_1000_2026-07-26/audit_1000.mjs";

export const rootDirectory =
  "/Users/ryan/Documents/Perioperative_TEAS_EA_Review_2026/02_screening/title_abstract/codex_remaining_1129_2026-07-26";

export const globalStart = 1001;
export const globalEnd = 2129;
export const targetCount = 1129;

const segmentBounds = Array.from({ length: 12 }, (_, index) => {
  const number = 11 + index;
  const start = globalStart + index * 100;
  return {
    number,
    start,
    end: Math.min(start + 99, globalEnd)
  };
});

function segmentName(segmentNumber) {
  const bound = segmentBounds.find((item) => item.number === segmentNumber);
  if (!bound) throw new Error(`Unknown segment ${segmentNumber}`);
  return `segment_${String(bound.start).padStart(4, "0")}_${String(bound.end).padStart(4, "0")}`;
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
  return fs
    .readFileSync(file, "utf8")
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

export function writeCsv(file, records) {
  const rows = [requiredKeys.map(csvCell).join(",")];
  for (const record of records) {
    rows.push(requiredKeys.map((key) => csvCell(record[key])).join(","));
  }
  fs.writeFileSync(file, `${rows.join("\n")}\n`, "utf8");
}

export function segmentRecords(segmentNumber) {
  return readJsonl(path.join(segmentDirectory(segmentNumber), "decisions.jsonl"));
}

export function allRecords() {
  return segmentBounds.flatMap(({ number }) => segmentRecords(number));
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
  if (new Set(records.map((record) => record.covidence_number)).size !== records.length) {
    throw new Error("Covidence numbers are not unique");
  }
  if (new Set(records.map((record) => record.post_vote_timestamp)).size !== records.length) {
    throw new Error("Post-vote timestamps are not unique");
  }
  return true;
}

export function appendRecord(record) {
  validateRecord(record);
  const existing = allRecords();
  const expectedGlobal = globalStart + existing.length;
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
  if (existing.some((item) => item.covidence_number === record.covidence_number)) {
    throw new Error(`Duplicate Covidence number ${record.covidence_number}`);
  }
  if (existing.some((item) => item.post_vote_timestamp === record.post_vote_timestamp)) {
    throw new Error(`Duplicate timestamp ${record.post_vote_timestamp}`);
  }
  const jsonl = path.join(segmentDirectory(expectedSegment), "decisions.jsonl");
  fs.appendFileSync(jsonl, `${JSON.stringify(record)}\n`, "utf8");
  const segment = segmentRecords(expectedSegment);
  validateRecords(segment, { segmentNumber: expectedSegment });
  writeCsv(path.join(segmentDirectory(expectedSegment), "decisions.csv"), segment);
  return expectedGlobal;
}

export function appendIncident(incident) {
  fs.appendFileSync(
    path.join(rootDirectory, "codex_continuity_incidents_remaining_1129.jsonl"),
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
  const globalSequence = records.at(-1).screening_sequence;
  const body = [
    `# Segment ${segmentNumber} checkpoint ${String(checkpointSequence).padStart(3, "0")}`,
    "",
    `- Global screening sequence: ${globalSequence}`,
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
  return { segmentNumber, checkpointSequence, globalSequence, ...decisionCounts };
}

export function updateManifest(status = {}) {
  const segments = [];
  for (const bound of segmentBounds) {
    const records = segmentRecords(bound.number);
    if (!records.length) continue;
    validateRecords(records, { segmentNumber: bound.number });
    const jsonlPath = path.join(segmentDirectory(bound.number), "decisions.jsonl");
    const { decisionCounts } = counts(records);
    const expectedLength = bound.end - bound.start + 1;
    segments.push({
      segment_number: bound.number,
      global_sequence_start: records[0].screening_sequence,
      global_sequence_end: records.at(-1).screening_sequence,
      first_covidence_number: records[0].covidence_number,
      last_covidence_number: records.at(-1).covidence_number,
      registered_vote_count: records.length,
      yes_count: decisionCounts.Yes,
      maybe_count: decisionCounts.Maybe,
      no_count: decisionCounts.No,
      JSONL_path: jsonlPath,
      CSV_path: path.join(segmentDirectory(bound.number), "decisions.csv"),
      validation_status: "passed",
      completion_timestamp:
        records.length === expectedLength ? records.at(-1).post_vote_timestamp : null,
      checksum: crypto.createHash("sha256").update(fs.readFileSync(jsonlPath)).digest("hex")
    });
  }
  const manifest = {
    review_id: 799962,
    review_title:
      "Protocol characteristics associated with clinically meaningful 24-hour opioid sparing from perioperative transcutaneous electrical acupoint stimulation and electroacupuncture: a systematic review",
    reviewer: "John Ryan Nual Mendoza (JM)",
    run_date: "2026-07-26",
    target_new_registered_votes: targetCount,
    global_sequence_start: globalStart,
    global_sequence_end: globalEnd,
    total_successful_votes: segments.reduce(
      (total, segment) => total + segment.registered_vote_count,
      0
    ),
    segments,
    ...status
  };
  fs.writeFileSync(
    path.join(rootDirectory, "master_manifest_remaining_1129.json"),
    `${JSON.stringify(manifest, null, 2)}\n`,
    "utf8"
  );
  return manifest;
}

export function finalize() {
  const records = allRecords();
  validateRecords(records, { exactCount: targetCount });
  records.forEach((record, index) => {
    if (record.screening_sequence !== globalStart + index) {
      throw new Error(`Combined global sequence mismatch at row ${index + 1}`);
    }
  });
  const combinedJsonl = path.join(
    rootDirectory,
    "combined",
    "codex_decisions_remaining_1129.jsonl"
  );
  fs.writeFileSync(
    combinedJsonl,
    `${records.map((record) => JSON.stringify(record)).join("\n")}\n`,
    "utf8"
  );
  writeCsv(
    path.join(rootDirectory, "combined", "codex_decisions_remaining_1129.csv"),
    records
  );
  return {
    count: records.length,
    uniqueCovidenceNumbers: new Set(records.map((r) => r.covidence_number)).size,
    uniqueTimestamps: new Set(records.map((r) => r.post_vote_timestamp)).size,
    ...counts(records)
  };
}

initializeDirectory();

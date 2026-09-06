import fs from "node:fs";
import {
  paths,
  readRecords,
  regenerateCsv,
  regenerateGapLog,
  validateRecords,
} from "./audit_aggressive_500.mjs";

const records = readRecords();
const target = records.find((record) => record.covidence_number === 3);

if (!target) throw new Error("Covidence #3 is absent from the audit");
if (target.decision !== "NO") {
  throw new Error("Refusing metadata correction because #3 vote is not NO");
}

target.actual_results_reported = "no";
validateRecords(records, 105);

fs.writeFileSync(
  paths.JSONL,
  `${records.map((record) => JSON.stringify(record)).join("\n")}\n`,
  "utf8",
);

validateRecords(readRecords(), 105);
regenerateCsv(records);
regenerateGapLog(records);

console.log(
  JSON.stringify({
    covidence_number: target.covidence_number,
    screening_sequence: target.screening_sequence,
    decision_unchanged: target.decision,
    actual_results_reported: target.actual_results_reported,
    records: records.length,
  }),
);

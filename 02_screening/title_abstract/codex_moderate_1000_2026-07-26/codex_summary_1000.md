# Screening summary — completed 1,000-record run

Status: Complete. Exactly 1,000 successfully registered Covidence votes were preserved in ten validated, append-only 100-record segments.

- Review ID: 799962
- Completed: 26 July 2026
- Final live queue: Screen references 1,129; Awaiting other reviewer 1,812; conflicts 0
- Completed segments: 10
- Last audited citation: #2618
- Next untouched citation: #2619
- Combined audit files: `combined/codex_decisions_1000.jsonl` and `combined/codex_decisions_1000.csv`
- Raw append-only decisions: Yes 14; Maybe 194; No 792
- Unique Covidence numbers: 1,000
- Unique post-vote timestamps: 1,000

Post-vote quality-control changes were recorded as append-only continuity incidents; original decision rows were not rewritten. The final two corrections were:

- #2605: Maybe → No; electroacupuncture for post-stroke spasticity was nonsurgical.
- #2608: Maybe → No; retrospective electroacupuncture for urinary incontinence was nonsurgical.

# Earlier continuity history

- Review ID: 799962
- Live queue at checkpoint 550: Screen references 1,579; Awaiting 1,362; conflicts 0
- Completed segments: 5
- Segment 6 progress: 50/100
- Last audited citation: #1829
- Next untouched citation: #1835

The append-only ledger contains 550 valid votes. The one-record discrepancy caused by the earlier timeout was resolved: Covidence #1828 (“Acupuncture,” 2010; DOI 10.1211/fact.15.2.0065) had a registered No vote, verified from its disabled vote control in the Awaiting other reviewer queue. It was restored as audit sequence 549, and #1829 was then screened as sequence 550.

Corrections completed after checkpoint 550:

- #1812: Maybe → No; randomized electroacupuncture for gallstone clearance was nonsurgical treatment.
- #1823: Maybe → No; treatment targeted persistent non-acute pain after back surgery, outside the eligible perioperative timing window.
- #1825: Maybe → No; prospective cohort with matched historic controls, not an RCT.

Corrections completed after checkpoint 475:

- #1717 and #1729: No → Maybe.
- #1733: Maybe → No.
- #1744, #1745, and #1762: Maybe → No after checkpoint-500 QC.

Corrections completed after checkpoint 450:

- #1706: No → Maybe.
- #1608 and #1626: Maybe → No.

Unresolved corrections identified at checkpoint 475:

- #1717: No → Maybe recommended.
- #1729: No → Maybe recommended for consistency with duplicate #941.
- #1733: Maybe → No recommended because EA was inseparably combined with external Chinese medicine.

Corrections completed after checkpoint 400:

- #1480: No → Yes.
- #1456: Maybe → No.
- #1486: Maybe → No.

Unresolved corrections identified at checkpoint 450:

- #1706: No → Maybe recommended. TEAS was combined with enflurane anaesthesia for craniocerebral operations, but no abstract is available to establish randomization or comparison.
- #1608: Maybe → No recommended. Electroacupuncture was delivered during adjuvant chemotherapy rather than eligible surgery.
- #1626: Maybe → No recommended. Cesarean delivery used spinal anaesthesia without general anaesthesia.

Corrections completed after checkpoint 325:

- #1185: Maybe → Yes.
- #1186: No → Yes.

Unresolved corrections identified at checkpoint 400:

- #1480: No → Yes recommended. This prospective randomized double-blind placebo-controlled trial used active versus inactive ReliefBand stimulation at P6 under general anaesthesia, beginning before surgery ended, and reported clinical PONV outcomes.
- #1456: Maybe → No recommended. TEAS was combined inseparably with acupoint pressing.
- #1486: Maybe → No recommended. Cesarean delivery used combined spinal–epidural anaesthesia without general anaesthesia.

Screening stopped without changing these three votes.

The user explicitly instructed that #934 remain No. This override is recorded separately and the original audit row was not rewritten.

Corrections completed during checkpoints 250 and 275:

- #945, #955, and #960 were changed from Maybe to No for surrogate-only outcomes, regional-only anaesthesia/instrument validation, and a paediatric-only population, respectively.
- #1022, #1030, #1036, #1038, #1040, #1041, #1045, #1047, and #1048 were confirmed as registry/protocol records without participant results and changed to No.
- #1034 was changed to No because combined TEAS and EA effects could not be separated.

Records #1058–#1179 were predominantly trial registrations and were classified as No without results. #1095 remains Maybe because it appears to report results but general anaesthesia is not established from the citation.

No other reviewer decision was viewed and no conflict was opened or resolved. Original audit rows remain append-only; completed corrections and user overrides are stored separately.

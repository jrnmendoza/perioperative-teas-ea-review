#!/usr/bin/env python3
"""Stage preparatory RoB drafts separately; never write the frozen masters."""
import csv
import hashlib
from pathlib import Path
import openpyxl

ROOT = Path(__file__).resolve().parents[1]
HERE = Path(__file__).resolve().parent
SETS = {
    'v33_rescue_opioid_binary_24h': 'Binary rescue opioid use (0-24h/POD1)',
    'v33_intraop_remifentanil': 'Intraoperative remifentanil',
    'v33_intraop_sufentanil': 'Intraoperative sufentanil',
    'v33_qor40_24h': 'Global QoR-40 at ~24h',
    'v33_gi_first_defecation': 'Time to first defecation',
}
# Explicit matches reviewed against Corrected_RoB2's Selected result and
# Timepoint/window. Every unmatched result remains pending, without borrowing.
MATCHES = {
    ('Xing 2022', 'Intraoperative remifentanil'),
    ('Liu 2015', 'Intraoperative sufentanil'),
    ('Yao 2015', 'Global QoR-40 at ~24h'),
    ('Yu 2020', 'Global QoR-40 at ~24h'),
    ('Ng 2013', 'Time to first defecation'),
}


def read(path):
    with path.open(encoding='utf-8-sig', newline='') as f:
        return list(csv.DictReader(f))


def write(path, rows):
    with path.open('w', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0]), lineterminator='\n')
        writer.writeheader()
        writer.writerows(rows)


def main():
    source = HERE / 'inputs/v33_rob2_gap_register_CHATGPT_DRAFT_COMPLETED.csv'
    drafts = read(source)
    gaps = read(ROOT / '08_V33_MASTER/01_DATA/v33_rob2_gap_register.csv')
    expected = {(r['study'], r['needed_result']) for r in gaps}
    actual = [(r['study'], r['result_assessed']) for r in drafts]
    assert len(actual) == len(set(actual)) and set(actual) == expected
    allowed = {'Low', 'Some concerns', 'High', 'Cannot be judged'}
    for r in drafts:
        assert all(r[f'd{i}_judgement'] in allowed for i in range(1, 6))
        assert r['overall_draft'] in allowed
        r.update(result_id=hashlib.sha256('\x1f'.join(r[k] for k in
                 ('study', 'result_assessed', 'timepoint_window', 'comparison')).encode()).hexdigest()[:16],
                 assessment_status='PREPARATORY DRAFT — NOT ADJUDICATED',
                 adjudicated_by='', adjudicated_on='',
                 source_sha256=hashlib.sha256(source.read_bytes()).hexdigest(),
                 source_verified_by='',
                 disposition='EXCLUDED: outcome predates PACU randomization' if r['study'] == 'Wu 2025'
                 else 'PENDING HUMAN ADJUDICATION')
    write(HERE / 'v34_RoB2_Draft.csv', drafts)
    by_pair = {(r['study'], r['result_assessed']): r for r in drafts}
    workbook = openpyxl.load_workbook(ROOT / 'TEAS EA Verification/TEAS_EA_RECONCILED_MASTER_DATA_v33_FINAL_LOCK_READY.xlsx', data_only=True)
    records = list(workbook['Corrected_RoB2'].values)
    rob = {r[0]: dict(zip(records[0], r)) for r in records[1:]}
    coverage = []
    for filename, result in SETS.items():
        for r in read(ROOT / f'08_V33_MASTER/01_DATA/{filename}.csv'):
            pair = r['study'], result
            matched = pair in MATCHES
            draft = by_pair.get(pair, {})
            coverage.append(dict(analysis_set=filename, study=r['study'], comparison_id=r['comparison_id'],
                                 result_assessed=result,
                                 assessment_status='EXISTING RESULT-SPECIFIC ASSESSMENT' if matched else 'PENDING',
                                 existing_selected_result=rob.get(r['study'], {}).get('Selected result', ''),
                                 overall=rob[r['study']]['Overall RoB 2'] if matched else '',
                                 draft_result_id=draft.get('result_id', ''),
                                 adjudicated_by='',
                                 required_action='' if matched else ('Adjudicate draft against sources' if draft else 'New result-specific assessment required')))
    write(HERE / 'result_rob2_coverage.csv', coverage)
    print(f'Staged {len(drafts)} unadjudicated drafts; {len(coverage)} analysed contrasts, '
          f'{sum(r["assessment_status"] == "PENDING" for r in coverage)} pending.')


if __name__ == '__main__':
    main()

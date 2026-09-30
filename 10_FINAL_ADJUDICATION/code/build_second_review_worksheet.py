"""Second-review worksheet for the items that have one assessor only.

One row per item awaiting second review:
  - baseline/protocol characteristics (14_CHARACTERISTICS/baseline_protocol_extraction.csv, second_review 'pending');
  - structured narrative outcomes (15_NARRATIVE_OUTCOMES: recovery milestones, harms, satisfaction/acceptability), every
    row with data whose second_review is 'pending';
  - later-window QoR GRADE bodies (08_QOR_ANALYSIS/qor_grade_later.csv) while second_review.csv does not cover that file.
Each row gives what was decided, where in the source it comes from and the quotation or rationale, and leaves the
reviewer columns blank. This file never records a review: a completed review is entered in the source record
(second_review column, or second_review.csv with the file's hash) and the worksheet is then regenerated.

Output: 02_DECISIONS/v38/second_review_worksheet.csv
"""
import csv, pathlib

ROOT = pathlib.Path(__file__).resolve().parents[2]; D = ROOT / '10_FINAL_ADJUDICATION'
OUT = D / '02_DECISIONS/v38/second_review_worksheet.csv'
COLS = ['item_type', 'record', 'report_or_body', 'field', 'value', 'locator', 'quotation_or_rationale', 'source_pdf', 'source_sha256',
        'first_assessment', 'reviewer_confirmation', 'reviewer_initials', 'review_date', 'reviewer_comments', 'resolution']
rows = lambda p: list(csv.DictReader(open(p, encoding='utf-8')))
REVIEW_BLANK = dict(reviewer_confirmation='', reviewer_initials='', review_date='', reviewer_comments='', resolution='')

def build():
    out = []
    rec = '10_FINAL_ADJUDICATION/14_CHARACTERISTICS/baseline_protocol_extraction.csv'
    for r in rows(ROOT / rec):
        if r['second_review'] != 'pending': continue
        loc = f"p.{r['page']}" + (f"; p.{r['page2']}" if r['quote2'] else '') if r['page'] else 'full text searched'
        quote = f"“{r['quote']}”" + (f" / “{r['quote2']}”" if r['quote2'] else '') if r['quote'] else ''
        out.append(dict(item_type='Characteristic', record=rec, report_or_body=r['report_id'], field=r['field'],
                        value=r['value'] or r['status'], locator=loc, quotation_or_rationale=quote + (f" Note: {r['note']}" if r['note'] else ''),
                        source_pdf=r['source_pdf'], source_sha256=r['source_sha256'], first_assessment=f"{r['status']}; {r['extracted_by']}", **REVIEW_BLANK))
    narrative = [('recovery_milestones.csv', 'Recovery milestone', 'domain', lambda r: f"{r['outcome']} · {r['comparison']}: {r['value_i']} vs {r['value_c']} ({r['statistic']}; {r['direction']})"),
                 ('harms_structured.csv', 'Harm', 'category', lambda r: f"{r['event']} · {r['arm_i']} {r['events_i']}/{r['n_i']} vs {r['arm_c']} {r['events_c']}/{r['n_c']} ({r['reporting']}; {r['attribution']})"),
                 ('satisfaction_acceptability.csv', 'Satisfaction / acceptability', 'construct', lambda r: f"{r['instrument']}, {r['time_point']} · {r['comparison']}: {r['value_i']} vs {r['value_c']} ({r['statistic']})")]
    for name, kind, field, value in narrative:
        rec = f'10_FINAL_ADJUDICATION/15_NARRATIVE_OUTCOMES/{name}'
        if not (ROOT / rec).exists(): continue
        for r in rows(ROOT / rec):
            if r['second_review'] != 'pending' or not r['quote']: continue
            out.append(dict(item_type=kind, record=rec, report_or_body=r['report_id'], field=r[field], value=value(r),
                            locator=f"p.{r['page']}" + (f"; p.{r['page2']}" if r['quote2'] else ''),
                            quotation_or_rationale=f"“{r['quote']}”" + (f" / “{r['quote2']}”" if r['quote2'] else '') + (f" Note: {r['note']}" if r['note'] else ''),
                            source_pdf=r['source_pdf'], source_sha256=r['source_sha256'], first_assessment=f"{r['extracted_by']}", **REVIEW_BLANK))
    grade = '10_FINAL_ADJUDICATION/08_QOR_ANALYSIS/qor_grade_later.csv'
    covered = {r['file'] for r in rows(D / '02_DECISIONS/v38/second_review.csv')}
    if (ROOT / grade).exists() and grade not in covered:
        dom = ['risk_of_bias', 'inconsistency', 'indirectness', 'imprecision', 'publication_bias']
        for g in rows(ROOT / grade):
            why = ' | '.join(f"{k.replace('_', ' ')} −{g[k + '_downgrades']}: {g[k]}" for k in dom)
            out.append(dict(item_type='GRADE body', record=grade, report_or_body=g['model_id'], field='certainty',
                            value=g['certainty'], locator=f"k={g['k']}, N={g['N']}, MD {float(g['effect']):.2f} ({float(g['ci_low']):.2f} to {float(g['ci_high']):.2f})",
                            quotation_or_rationale=why, source_pdf='', source_sha256='', first_assessment=g['decision_status'], **REVIEW_BLANK))
    return out

if __name__ == '__main__':
    out = build()
    with open(OUT, 'w', newline='', encoding='utf-8') as fh:
        w = csv.DictWriter(fh, COLS); w.writeheader(); w.writerows(out)
    from collections import Counter
    print(f'{len(out)} worksheet rows:', dict(Counter(r['item_type'] for r in out)))

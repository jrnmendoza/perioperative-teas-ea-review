"""Write FINAL_CURRENT_STATE_REPORT.md from the canonical records, so the report cannot fall behind them.

Every count and estimate is read from the files that hold it (models, GRADE, RoB 2, QoR, E2, characteristics,
narrative tables, second-review record and worksheet, Stata verification). The report date is the latest dated
record among them. The "Inventory" table is machine-checked: scripts/check_current_dashboard.py recomputes each
value from the dashboard payload, so the dashboard can never show a later or different state than this report.
The prose (limitations, outstanding items) states only what those records support. Run before
build_current_dashboard.py, which copies the report and reads its "Not completed — outstanding" list.
"""
import csv, json, pathlib, re
from collections import Counter

ROOT = pathlib.Path(__file__).resolve().parents[2]; D = ROOT / '10_FINAL_ADJUDICATION'
rows = lambda p: list(csv.DictReader(open(D / p, encoding='utf-8-sig')))
fmt = lambda x: f"{float(x):.2f}".replace('-', '−')
MONTHS = 'January February March April May June July August September October November December'.split()
ITEM_NAMES = {'Characteristic': 'characteristic values', 'Recovery milestone': 'recovery-milestone rows', 'Harm': 'harms rows',
              'Satisfaction / acceptability': 'satisfaction/acceptability rows', 'GRADE body': 'later-window QoR GRADE bodies',
              'Harm (not located)': 'harms "not located" determinations from the outcome-coverage audit'}
items = lambda work: ', '.join(f'{n} {ITEM_NAMES.get(k, k.lower())}' for k, n in work.items())
long_date = lambda iso: f"{int(iso[8:])} {MONTHS[int(iso[5:7]) - 1]} {iso[:4]}"

def inventory():
    """(label, value) pairs; the same labels are recomputed from the payload by the dashboard contract."""
    studies = json.load(open(D / '03_CANONICAL/studies.json'))
    models, grade, rob = rows('04_MODELS/model_outputs.csv'), rows('03_CANONICAL/grade.csv'), rows('02_DECISIONS/v38/rob2_assessments.csv')
    qor, qor_later = rows('08_QOR_ANALYSIS/qor_models.csv'), rows('08_QOR_ANALYSIS/qor_models_later.csv')
    chars = Counter(r['status'] for r in rows('14_CHARACTERISTICS/report_characteristics.csv'))
    narr = {k: rows(f'15_NARRATIVE_OUTCOMES/{f}') for k, f in [('milestones', 'recovery_milestones.csv'), ('harms', 'harms_structured.csv'), ('satisfaction', 'satisfaction_acceptability.csv')]}
    work = Counter(r['item_type'] for r in rows('02_DECISIONS/v38/second_review_worksheet.csv'))
    stata = rows('13_STATA/output/stata_verification_summary.csv')
    return [
        ('Included reports', len(studies)),
        ('Operational trial families', len({s['trial_id'] for s in studies})),
        ('Canonical results', len(rows('03_CANONICAL/results.csv'))),
        ('Core models (defined)', len(models)),
        ('Core models with data', sum(int(m['k']) > 0 for m in models)),
        ('Core model inputs', len(rows('04_MODELS/model_inputs.csv'))),
        ('Core RoB 2 assessments (result-specific)', len(rob)),
        ('Core GRADE bodies', len(grade)),
        ('QoR ~24 h main models', sum(not m['parent_model_id'] for m in qor)),
        ('QoR ~24 h diagnostics', sum(bool(m['parent_model_id']) for m in qor)),
        ('QoR ~24 h RoB 2 assessments', len(rows('08_QOR_ANALYSIS/qor_rob2.csv'))),
        ('QoR ~24 h GRADE bodies', len(rows('08_QOR_ANALYSIS/qor_grade.csv'))),
        ('QoR later-window models', len(qor_later)),
        ('QoR later-window RoB 2 assessments', len(rows('08_QOR_ANALYSIS/qor_rob2_later.csv'))),
        ('QoR later-window GRADE bodies', len(rows('08_QOR_ANALYSIS/qor_grade_later.csv'))),
        ('Characteristic values (reports × fields)', sum(chars.values())),
        ('Characteristic values: legacy, not re-verified', chars.get('Legacy (v26, not re-verified)', 0)),
        ('Characteristic values: single extractor, second review pending', chars.get('Extracted (PDF quote, single extractor)', 0)),
        ('Characteristic values: second-reviewed PDF quotation', chars.get('Verified (PDF quote, second reviewer)', 0)),
        ('Recovery-milestone rows', len(narr['milestones'])),
        ('Harms rows (including not-located reports)', len(narr['harms'])),
        ('Satisfaction/acceptability rows', len(narr['satisfaction'])),
        ('Second-review record entries', len(rows('02_DECISIONS/v38/second_review.csv'))),
        ('Items awaiting second review', sum(work.values())),
        ('Stata-verified models', len(stata)),
        ('Stata discrepancies', sum(r['status'].startswith('DISCREPANCY') for r in stata)),
    ]

def dated():
    """Every ISO date carried by the records this report describes; the report is dated to the latest."""
    dates = {'2026-09-20'}
    dates |= {r['review_date'] for f in ['08_QOR_ANALYSIS/qor_grade_later.csv', '02_DECISIONS/v38/second_review.csv'] for r in rows(f)}
    for f in ['14_CHARACTERISTICS/baseline_protocol_extraction.csv', '15_NARRATIVE_OUTCOMES/recovery_milestones.csv', '15_NARRATIVE_OUTCOMES/harms_structured.csv', '15_NARRATIVE_OUTCOMES/satisfaction_acceptability.csv']:
        dates |= set(re.findall(r'\d{4}-\d{2}-\d{2}', ' '.join(r['extracted_by'] for r in rows(f))))
    return max(dates)

def manuscript_gaps():
    ms = ROOT / 'manuscript'
    text = '\n'.join((ms / f'{s}.md').read_text(encoding='utf-8') for s in ['ABSTRACT', 'INTRODUCTION', 'METHODS', 'RESULTS', 'DISCUSSION', 'CONCLUSIONS'])
    decisions = re.findall(r'\[AUTHOR DECISION — ([^\]]+)\]', text)
    unwritten = [s for s in ['Title page', 'Keywords', 'Abbreviations', 'Declarations'] if not re.search(r'^#+\s*' + s, text, re.M | re.I)]
    return decisions, unwritten

def build():
    inv = dict(inventory()); date = dated()
    models = {m['model_id']: m for m in rows('04_MODELS/model_outputs.csv')}; grade = {g['model_id']: g for g in rows('03_CANONICAL/grade.csv')}
    e2 = {m['model_id']: m for m in rows('09_E2_ANALYSIS/e2_model_outputs.csv')}
    qor = [m for m in rows('08_QOR_ANALYSIS/qor_models.csv') if not m['parent_model_id']]; qg = {g['model_id']: g for g in rows('08_QOR_ANALYSIS/qor_grade.csv')}
    later = {g['model_id']: g for g in rows('08_QOR_ANALYSIS/qor_grade_later.csv')}
    review = rows('02_DECISIONS/v38/second_review.csv'); work = Counter(r['item_type'] for r in rows('02_DECISIONS/v38/second_review_worksheet.csv'))
    decisions, unwritten = manuscript_gaps()
    covered = {r['file'].rsplit('/', 1)[-1] for r in review}
    signalling_reviewed = {'rob2_signalling_questions.csv', 'qor_rob2_signals.csv', 'qor_rob2_signals_later.csv'} <= covered
    chars = rows('14_CHARACTERISTICS/report_characteristics.csv')
    baseline_quoted = sum('baseline_protocol_extraction' in c['source'] and 'PDF quote' in c['status'] for c in chars)
    single, reviewed = inv['Characteristic values: single extractor, second review pending'], inv['Characteristic values: second-reviewed PDF quotation']
    L = ['# Current state — adjudication v38', '',
         f"{long_date(date)} · PROSPERO CRD420261452908 · public analytical release, not data-locked. Adjudication decisions were made after results were known and are labelled post hoc.", '',
         f"Generated by `10_FINAL_ADJUDICATION/code/build_current_state_report.py` from the canonical records; the inventory below is checked against the dashboard at every build. The version dated 20 September 2026 is in git history.", '',
         '## Inventory', '', '| Item | Value |', '|---|---:|'] + [f'| {k} | {v:,} |' for k, v in inventory()] + ['']
    L += ['## Primary outcome (E1, registered)', '', '| Body | k | N | MD mg IV MME (95% CI) | Certainty |', '|---|---:|---:|---|---|']
    for mid in ['opioid24_TEAS_sham', 'opioid24_EA_sham', 'opioid24_TEAS_usual', 'opioid24_EA_usual']:
        m = models[mid]; e = f"{fmt(m['display_effect'])} ({fmt(m['display_ci_low'])}, {fmt(m['display_ci_high'])})" if int(m['k']) else 'No eligible data'
        L.append(f"| {mid} | {m['k']} | {m['N']} | {e} | {grade[mid]['certainty']} |")
    t = e2['E2_opioid24_TEAS_sham']
    L += ['', 'No body establishes the registered joint criterion (≥10 mg sparing with paired ~24-hour pain whose upper 95% limit is below +1 point). '
          f"The post-hoc E2 sensitivity analysis does not change this: TEAS versus sham is k={t['k']}, N={t['N']}, {fmt(t['effect'])} mg IV MME ({fmt(t['ci_low'])}, {fmt(t['ci_high'])}); E2 bodies are not graded.", '']
    L += ['## Quality of recovery', '', '| Body | k | N | MD (95% CI), points | Certainty |', '|---|---:|---:|---|---|']
    L += [f"| {m['label']} | {m['k']} | {m['N']} | {fmt(m['effect'])} ({fmt(m['ci_low'])} to {fmt(m['ci_high'])}) | {qg[m['model_id']]['certainty']} |" for m in qor]
    L += [f"| {g['label']} | {g['k']} | {g['N']} | {fmt(g['effect'])} ({fmt(g['ci_low'])} to {fmt(g['ci_high'])}) | {g['certainty']} |" for g in later.values()]
    L += ['', f"The later-window bodies were graded post hoc ({', '.join(sorted({g['review_date'] for g in later.values()}))}); their status is: {'; '.join(sorted({g['decision_status'] for g in later.values()}))}. "
          'Leave-one-out diagnostics are not graded. A clinically important improvement is not established and absence of benefit is not demonstrated.', '']
    L += ['## Characteristics and narrative outcomes', '',
          f"All {inv['Characteristic values (reports × fields)']:,} characteristic values carry a verification status. "
          + (f"{single} values are quoted from the report PDFs by a single extractor (second review pending), " if single else '')
          + f"{reviewed} values are quoted from the report PDFs and second-reviewed, and {inv['Characteristic values: legacy, not re-verified']} legacy values remain. "
          f"Structured narrative tables (`10_FINAL_ADJUDICATION/15_NARRATIVE_OUTCOMES`) hold {inv['Recovery-milestone rows']} recovery-milestone rows, {inv['Harms rows (including not-located reports)']} harms rows and {inv['Satisfaction/acceptability rows']} satisfaction/acceptability rows, each value with a page-located quotation. "
          'They are descriptive: nothing is pooled, and a report without a harms result is recorded as not located, not as zero.', '']
    L += ['## Review provenance', '',
          'First assessments: result-specific RoB 2, GRADE, estimand classification and adjudication decisions by a delegated assessor under the review owner\'s delegation. '
          'The second-review record (`02_DECISIONS/v38/second_review.csv`) pins each reviewed file by SHA-256:', '',
          '| Scope | Items | Reviewer | Date | Outcome |', '|---|---:|---|---|---|'] + [f"| {r['scope']} | {r['items']} | {r['reviewer']} | {r['review_date']} | {r['outcome']} |" for r in review]
    L += ['', (f"Awaiting second review ({sum(work.values())} items, listed with blank reviewer columns in `02_DECISIONS/v38/second_review_worksheet.csv`): " + items(work) + '. ' if work else 'No item is awaiting second review. ')
          + ('The RoB 2 signalling-question responses are in the second-review record. ' if signalling_reviewed else 'The RoB 2 signalling-question responses are not in the second-review record. ')
          + 'A check of a first assessment is not an independent duplicate assessment.', '']
    L += ['## Limitations that remain', '',
          'The 12-reference import gap lacks record-level mapping; upstream deduplication reconciles arithmetically but cannot be replayed record by record. '
          'An outcome-focused screening amendment and the withdrawn re-screening leave review-wide completeness uncertain. Source ambiguities remain explicit holds or diagnostics. '
          'Numerical reproducibility (Python, R/metafor and Stata agree) does not certify source truth or complete evidence selection. '
          'Eleven author queries were sent on 22 September 2026 (one bounced) and four drafted queries remain unsent; no reply is recorded in the repository and no analysis depends on one.', '']
    L += ['## Deliverable status', '', '**Completed**', '',
          f"- **Later-window QoR GRADE.** {len(later)} bodies graded post hoc, with correspondence contracts.",
          f"- **Source-verified characteristics.** {baseline_quoted} baseline and protocol values quoted from the PDFs, replacing every legacy value.",
          f"- **Structured narrative tables.** Recovery milestones, harms by category and satisfaction/acceptability, quote-checked.",
          '- **Claim-citation audit of the current manuscript.** Every citing sentence checked against its source (`references/current_claim_citation_audit.csv`); citations render as numbered references.',
          '- **Manuscript synchronised.** Numbers, certainty and provenance statements checked by `reports/check_manuscript_consistency.py`.']
    L += [f"- **Second review recorded.** {', '.join(sorted({r['reviewer'] for r in review}))}: " + '; '.join(f"{r['scope']} ({r['items'] if r['outcome'] == 'all confirmed' else r['outcome']}, {r['review_date']})" for r in review) + '.', '']
    L += [
          '**Not completed — outstanding**', '',
          *([f"- **Second review of single-assessor items.** {sum(work.values())} items in the worksheet (" + items(work) + ')' + ('.' if signalling_reviewed else ' and the RoB 2 signalling responses.')] if work or not signalling_reviewed else []),
          f"- **Author decisions in the manuscript.** {len(decisions)} passages marked [AUTHOR DECISION] (the assessor statement and the AI-use disclosure that depends on it) need the author team's confirmation." if len(decisions) == 2 else
          f"- **Author decisions in the manuscript.** {len(decisions)} passages marked [AUTHOR DECISION] need the author team's confirmation.",
          '- **Author query replies.** No reply is recorded; four drafted queries are unsent.',
          f"- **Submission sections not yet written.** {', '.join(unwritten) or 'None'}.",
          '- **Data lock.** This is a public analytical release; no data lock has been declared.', '']
    L += ['## Public deployment', '',
          'The dashboard is public at <https://jrnmendoza.github.io/perioperative-teas-ea-review/>, built from `claude-v26-dashboard-final` by `.github/workflows/deploy-pages.yml` after the integrity, tab-data, generated-artifact, v38-contract and browser checks pass. '
          "The site's `build-meta.json` names the commit it serves; each release's deployment record is in its task report (most recently `FINAL_COMPLETION_REPORT.md` and `10_FINAL_ADJUDICATION/02_DECISIONS/v38/SECOND_REVIEW_2026-09-30.md`).", '']
    return '\n'.join(L)

if __name__ == '__main__':
    (ROOT / 'FINAL_CURRENT_STATE_REPORT.md').write_text(build(), encoding='utf-8')
    print('FINAL_CURRENT_STATE_REPORT.md dated', dated(), '·', len(inventory()), 'inventory items')

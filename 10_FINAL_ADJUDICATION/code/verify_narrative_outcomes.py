"""Check the structured narrative-outcome tables (15_NARRATIVE_OUTCOMES) against the source texts and the registry.

  recovery_milestones.csv        hospital length of stay, PACU stay, extubation, emergence/orientation, ambulation/
                                 mobilisation and discharge readiness, one row per report, outcome and comparison
  harms_structured.csv           harms by separate category (intervention-related local / other, withdrawals, serious or
                                 all-cause, unattributed postoperative complications, anaesthetic side effects, mixed
                                 totals); every report appears, and a report with no harms result is "Not located (not a
                                 zero)"
  satisfaction_acceptability.csv satisfaction, acceptability of the intervention and health-related quality of life

Every row with data carries a verbatim quote (optionally a second one) that is found on its stated page of the report's
text layer (verify_regimen_extraction.quote_found); the source PDF and hash match the registry; a linked register result
exists for the same report; vocabularies are closed; nothing is marked second-reviewed unless second_review.csv covers
the file. The tables are descriptive: no row carries a pooled estimate. Exits non-zero on any failure and writes a hash
manifest when every table passes.

Usage: python3 10_FINAL_ADJUDICATION/code/verify_narrative_outcomes.py
"""
import csv, hashlib, pathlib, re
from collections import Counter
import verify_regimen_extraction as V

ROOT = V.ROOT; D = V.D; OUT = D / '15_NARRATIVE_OUTCOMES'
rows = lambda p: list(csv.DictReader(open(p, encoding='utf-8')))
DOMAINS = ('Hospital length of stay', 'PACU stay', 'Extubation', 'Emergence / recovery of orientation', 'Ambulation / mobilisation', 'Discharge readiness')
DIRECTIONS = ('Favours intervention', 'Favours control', 'No difference reported', 'Direction only (no test)', 'Not tested')
CATEGORIES = ('Intervention-related: local (skin, electrode or needle site)', 'Intervention-related: other (discomfort, device or needling problems)',
              'Withdrawal or discontinuation due to the intervention', 'Serious adverse events or death (all-cause)',
              'Postoperative complication (attribution not reported)', 'Anaesthetic or opioid side effects (not intervention harms)',
              'Any adverse event (mixed attribution)', 'No intervention-harm result located')
REPORTING = ('Counts by arm', 'Explicit zero', 'Narrative only (no counts)', 'Not located (not a zero)')
ATTRIBUTION = ('Attributed to intervention', 'Not attributed', 'Attribution not reported', 'Mixed', '')
CONSTRUCTS = ('Satisfaction', 'Acceptability of the intervention', 'Health-related quality of life')
POOLED = re.compile(r'pooled|summary estimate|random[- ]effects', re.I)
TABLES = {'recovery_milestones.csv': ('domain', DOMAINS), 'harms_structured.csv': ('category', CATEGORIES), 'satisfaction_acceptability.csv': ('construct', CONSTRUCTS)}

def check_table(name, reviewed_files, R=None):
    """All row checks for one table (R: the rows to check; default the file)."""
    errs = []; R = rows(OUT / name) if R is None else R; field, vocab = TABLES[name]
    register = {r['result_id']: r for r in csv.DictReader(open(D / '03_CANONICAL/results.csv', encoding='utf-8-sig'))}
    covered = f'10_FINAL_ADJUDICATION/15_NARRATIVE_OUTCOMES/{name}' in reviewed_files
    for i, r in enumerate(R, 2):
        rid = r['report_id']; where = f'{name}:{i} {rid}'
        if rid not in V.registry: errs.append(f'{where}: unknown report'); continue
        if r['trial_id'] != V.registry[rid]['trial_id']: errs.append(f'{where}: trial_id differs from registry')
        if r['source_pdf'] != V.registry[rid]['source_pdf'] or r['source_sha256'] != V.registry[rid]['source_sha256']: errs.append(f'{where}: source PDF/hash differs from registry')
        if r[field] not in vocab: errs.append(f'{where}: bad {field} {r[field]!r}')
        located = not (name == 'harms_structured.csv' and r['reporting'] == 'Not located (not a zero)')
        if located:
            if not (r['page'] and r['quote']): errs.append(f'{where}: a row with data needs a page and a quote')
            elif not V.quote_found(rid, r['page'], r['quote']): errs.append(f'{where}: quote not found on p{r["page"]}: {r["quote"][:70]}')
            if r['quote2'] and not V.quote_found(rid, r['page2'] or 0, r['quote2']): errs.append(f'{where}: quote2 not found on p{r["page2"]}')
        elif r['category'] != 'No intervention-harm result located' or r['quote'] or r['events_i'] or r['events_c']:
            errs.append(f'{where}: a "not located" harms row must carry no quote and no counts')
        if POOLED.search(r.get('synthesis', '')) and not re.search(r'no pool|not pooled|nothing is pooled|no counts are pooled', r['synthesis'], re.I): errs.append(f'{where}: synthesis claims pooling')
        if name == 'recovery_milestones.csv':
            if r['direction'] not in DIRECTIONS: errs.append(f'{where}: bad direction {r["direction"]!r}')
            x = register.get(r['register_result_id'])
            if r['register_result_id'] and (not x or x['study'] != rid or x['decision'] != r['register_decision']): errs.append(f'{where}: register link {r["register_result_id"]} is not a result of this report with that decision')
        if name == 'harms_structured.csv':
            if r['reporting'] not in REPORTING: errs.append(f'{where}: bad reporting {r["reporting"]!r}')
            if r['attribution'] not in ATTRIBUTION: errs.append(f'{where}: bad attribution {r["attribution"]!r}')
            if r['reporting'] == 'Explicit zero' and (r['events_i'] not in ('0',) or r['events_c'] not in ('0', 'not applicable')): errs.append(f'{where}: explicit zero with non-zero counts')
        if not re.fullmatch(r'Single extractor, \d{4}-\d{2}-\d{2}', r['extracted_by']): errs.append(f'{where}: bad extracted_by')
        if r['second_review'] != 'pending' and not (covered and re.fullmatch(r'[A-Z]{2,4}, \d{4}-\d{2}-\d{2}: confirmed', r['second_review'])): errs.append(f'{where}: second review claimed without a record')
    if name == 'harms_structured.csv':
        missing = set(V.registry) - {r['report_id'] for r in R}
        errs += [f'{name}: report {m} has no row (a report without a harms result must say "Not located")' for m in sorted(missing)]
    return errs, R

def main():
    reviewed = {r['file'] for r in rows(D / '02_DECISIONS/v38/second_review.csv')}
    errs = []; summary = []
    for name, (field, _) in TABLES.items():
        e, R = check_table(name, reviewed); errs += e
        summary.append(f"{name}: {len(R)} rows, {len({r['report_id'] for r in R})} reports, " + ', '.join(f'{k} {v}' for k, v in Counter(r[field] for r in R).items()))
    for rid in sorted({r['report_id'] for n in TABLES for r in rows(OUT / n)}):
        if hashlib.sha256((ROOT / V.registry[rid]['source_pdf']).read_bytes()).hexdigest() != V.registry[rid]['source_sha256']: errs.append(f'{rid}: PDF hash changed')
    if errs:
        print('\n'.join('FAIL ' + e for e in errs)); return 1
    print('PASS narrative outcomes\n  ' + '\n  '.join(summary))
    files = [OUT / n for n in TABLES] + [pathlib.Path(__file__)]
    (OUT / 'narrative_outcomes.sha256').write_text(''.join(f'{hashlib.sha256(f.read_bytes()).hexdigest()}  {f.relative_to(ROOT)}\n' for f in files))
    return 0

if __name__ == '__main__':
    raise SystemExit(main())

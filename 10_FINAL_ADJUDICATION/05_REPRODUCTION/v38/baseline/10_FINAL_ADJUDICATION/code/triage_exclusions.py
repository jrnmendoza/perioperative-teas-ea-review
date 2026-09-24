"""Mechanical re-screening triage of the 161 Covidence full-text exclusions (v36, 16 Sep 2026).

Flags only. These are NOT eligibility decisions: keyword presence cannot establish population, general anaesthesia,
randomization, physical modality or extractable data. Output prioritizes human dual re-screening against the
registered (20 Aug 2026) outcome list, which admits any eligible outcome, not only 24-h opioid consumption.
"""
import csv, json, pathlib, re, collections
ROOT = pathlib.Path(__file__).resolve().parents[2]; D = ROOT / '10_FINAL_ADJUDICATION'
ex = json.load(open(ROOT / 'covidence_all_161_excluded.json'))
man = {x['id']: x for x in json.load(open(D / '01_SOURCE_EVIDENCE/exclusions/manifest.json'))}
TERMS = dict(
    intervention=r'electro-?acupunct|transcutaneous electric(al)? acupoint|acupoint electrical|electrical acupoint|\bTEAS\b|\bTAES\b|\bEA\b|electroacupoint|acupuncture-like TENS',
    randomized=r'randomi[sz]ed|randomly (assigned|allocated|divided)',
    general_anaesthesia=r'general an(a)?esthe',
    opioid=r'opioid|morphine|fentanyl|sufentanil|remifentanil|hydromorphone|oxycodone|tramadol|pethidine|butorphanol|dezocine|MME',
    pain=r'\bVAS\b|\bNRS\b|pain (score|intensity)|visual analog',
    ponv=r'nausea|vomit|\bPONV\b',
    recovery_quality=r'QoR-?(9|15|40)|quality of recovery',
    gi_recovery=r'flatus|bowel sound|borborygm|defecation|gastrointestinal function|postoperative ileus',
    rescue_analgesia=r'rescue analges|additional analges|supplemental analges',
    hospital_stay=r'length of (hospital )?stay|hospital stay|discharge',
    adverse_events=r'adverse (event|effect|reaction)|complication',
)
OUTCOMES = ['opioid', 'pain', 'ponv', 'recovery_quality', 'gi_recovery', 'rescue_analgesia', 'hospital_stay', 'adverse_events']
rows = []
for r in ex:
    m = man.get(str(r['id']), {})
    if m.get('status') == 'RETRIEVED':
        text = open(ROOT / m['text_file'], errors='ignore').read(); basis = 'FULL TEXT (retrieved PDF)'
    else:
        text = (r.get('title') or '') + ' ' + (r.get('abstract') or ''); basis = 'TITLE/ABSTRACT ONLY'
    body = re.split(r'\n\s*(References|REFERENCES)\s*\n', text)[0]
    hits = {k: bool(re.search(p, body, re.I)) for k, p in TERMS.items()}
    cjk = len(re.findall(r'[一-鿿]', text))
    non_english_signal = cjk > 200 or (r.get('title') or '').strip().startswith('[')
    outcomes = [k for k in OUTCOMES if hits[k]]
    reason = r['exclusion_reason']
    if reason == 'Wrong outcomes' and hits['intervention'] and outcomes and not non_english_signal:
        tier = 'PRIORITY RE-SCREEN: registered outcome terms present'
    elif reason == 'Wrong outcomes' and outcomes:
        tier = 'RE-SCREEN: outcome terms present; intervention or language needs confirmation'
    elif reason == 'Publication language' and not non_english_signal and basis.startswith('FULL'):
        tier = 'VERIFY LANGUAGE: retrieved text appears English'
    else:
        tier = 'NO MECHANICAL FLAG (reason retained pending human confirmation)'
    rows.append(dict(covidence_id=str(r['id']), study_id=r['study_id'], title=r['title'], journal=r.get('journal_info', ''), exclusion_reason=reason,
                     excluded_on=r['excluded_on'], evidence_basis=basis, full_text_sha256=m.get('sha256', ''),
                     non_english_signal=non_english_signal, **{'term_' + k: v for k, v in hits.items()},
                     registered_outcome_terms=';'.join(outcomes), triage=tier,
                     status='TRIAGE FLAG ONLY — NOT AN ELIGIBILITY DECISION'))
out = D / '02_DECISIONS/exclusion_rescreen_triage.csv'
with open(out, 'w', newline='') as f:
    w = csv.DictWriter(f, list(rows[0])); w.writeheader(); w.writerows(rows)
print(len(rows), collections.Counter(r['triage'] for r in rows))
print(collections.Counter((r['exclusion_reason'], r['evidence_basis']) for r in rows))

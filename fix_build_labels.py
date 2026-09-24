import re

path = '/Users/ryan/Documents/dashboard-fix/10_FINAL_ADJUDICATION/code/build_current_dashboard.py'
text = open(path).read()

new_labels = """ data['e2_labels']={
  'E2_TEAS_sham_LOO_Gu_2019': 'Leave out Gu 2019 (figure–text contradiction)',
  'E2_TEAS_sham_LOO_Lee_2011': 'Leave out Lee 2011 (Table 8 contradiction)',
  'E2_TEAS_sham_LOO_He_2026': 'Without unstated-route equivalents (He 2026)',
  'E2_TEAS_sham_excl_unquantified_rescue': 'Without known unquantified rescue (Chen 1998, Lee 2011)',
  'E2_TEAS_sham_excl_E2.1': 'Without E2.1 admissions (Zhang 2025, Gu 2019)',
  'E2_EA_usual_LOO_El-Rakshy': 'Leave out El-Rakshy 2009',
  'E2_TEAS_sham_LOO_Szmit_2021': 'without Szmit 2021',
  'E2_TEAS_sham_LOO_Chen_1998': 'without Chen 1998',
  'E2_TEAS_sham_LOO_Chen_2020': 'without Chen 2020',
  'E2_TEAS_sham_LOO_Zhang_2025': 'without Zhang 2025',
  'E2_EA_usual_LOO_Seevaunnamtum': 'without Seevaunnamtum 2016',
  'E2_EA_usual_LOO_Yang': 'without Yang 2024',
  'E2_EA_usual_LOO_Lin': 'without Lin 2002',
  'E2_TEAS_sham_suf0.25': 'Sufentanil 0.25',
  'E2_TEAS_sham_suf1.0': 'Sufentanil 1.0',
  'E2_EA_usual_excl_unquantified_rescue': 'Without known unquantified rescue (= E1 body)',
  'E2_TEAS_sham_E1_restriction': 'Restricted to E1-eligible (= registered primary)'
 }
 e2_ids = {m['model_id'] for m in data['e2_analysis']['models']}
 for k in data['e2_labels'].keys():
     assert k in e2_ids, f"Label key not found in E2 model outputs: {k}"
"""

# replace everything from data['e2_labels']={ up to the closing brace
text = re.sub(r" data\['e2_labels'\]=\{.*?\}", new_labels.strip(), text, flags=re.DOTALL)

open(path, 'w').write(text)
print("Done")

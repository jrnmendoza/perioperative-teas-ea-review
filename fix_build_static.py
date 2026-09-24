import re

path = '/Users/ryan/Documents/dashboard-fix/10_FINAL_ADJUDICATION/code/build_current_dashboard.py'
text = open(path).read()

old_static = """if qor_path.exists():static+='<p>QoR addendum: three approximately-24-hour syntheses, eight new result-specific assessments and three Very-low-certainty judgments. All pooled confidence intervals include zero. See the QoR analysis tab. Four later-window QoR models (POD2/3) are also available.</p>'"""
new_static = """if qor_path.exists():static+='<p>QoR addendum: three approximately-24-hour syntheses, eight new result-specific assessments and three Very-low-certainty judgments. All pooled confidence intervals include zero. See the QoR analysis tab. Four later-window QoR models (POD2/3) are also available.</p>'
if e2_path.exists():
 e2_data = json.loads(e2_path.read_text())
 teas = next(m for m in e2_data['models'] if m['model_id'] == 'E2_opioid24_TEAS_sham')
 ea = next(m for m in e2_data['models'] if m['model_id'] == 'E2_opioid24_EA_sham')
 any_met = (teas['ci_high'] < -10)
 met_text = 'in at least one body' if any_met else 'in no body'
 ea_text = 'cannot be evaluated' if ea['ci_high'] >= -10 else 'met'
 static += f'<p>E2 post-hoc sensitivity analysis: E1 kept as primary, not graded. The joint criterion is met {met_text} (for EA vs sham it {ea_text}).</p>'"""
text = text.replace(old_static, new_static)

open(path, 'w').write(text)
print("Done")

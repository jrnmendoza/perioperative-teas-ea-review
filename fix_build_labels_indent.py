path = '/Users/ryan/Documents/dashboard-fix/10_FINAL_ADJUDICATION/code/build_current_dashboard.py'
lines = open(path).readlines()
for i, line in enumerate(lines):
    if 'data[\'e2_labels\']={' in line:
        lines[i] = "data['e2_labels']={\n"
    elif 'e2_ids = ' in line:
        lines[i] = "if 'e2_analysis' in data:\n e2_ids = {m['model_id'] for m in data['e2_analysis']['models']}\n"
    elif 'for k in data[\'e2_labels\']' in line:
        lines[i] = " for k in data['e2_labels'].keys():\n"
    elif 'assert k in e2_ids' in line:
        lines[i] = '  assert k in e2_ids, f"Label key not found in E2 model outputs: {k}"\n'
open(path, 'w').writelines(lines)
print("Done")

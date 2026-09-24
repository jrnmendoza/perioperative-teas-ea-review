import re
import sys

path = '/Users/ryan/Documents/dashboard-fix/scripts/check_current_dashboard.py'
text = open(path).read()

# Add placeholder check to checks()
old_checks_end = "      'QoR later-window identity':d.get('qor_later_models')==json.load(open(D/'08_QOR_ANALYSIS/qor_models_later.json')) if (D/'08_QOR_ANALYSIS/qor_models_later.json').exists() else True,\n    }"

# In check_current_dashboard, checks(d) is pure data checks. The HTML/UI checks are in main().
# We'll put HTML checks in main().

old_main = """    for item in data['downloads']:
        assert sha(site/item['href'])==item['sha256']==sha(ROOT/item['source']),item['href']
    assert all(token not in page for token in ['app.js','v34_data.js','CRD420251090635','k=7, N=676','−14.00','−9.91'])
    for forbidden in ['fetch(','XMLHttpRequest','localStorage.setItem']:
        assert forbidden not in (site/'current_review_ui.js').read_text(),'Unexpected external/hidden state operation'
"""
new_main = """    for item in data['downloads']:
        assert sha(site/item['href'])==item['sha256']==sha(ROOT/item['source']),item['href']
    assert all(token not in page for token in ['app.js','v34_data.js','CRD420251090635','k=7, N=676','−14.00','−9.91'])
    
    # New CI checks
    html_without_scripts = re.sub(r'<script.*?</script>', '', page, flags=re.DOTALL)
    html_without_scripts = re.sub(r'<style.*?</style>', '', html_without_scripts, flags=re.DOTALL)
    assert not re.search(r'\\{[a-z_]+\\}', html_without_scripts), 'Unfilled placeholder found in index.html outside scripts/styles'
    nav_match = re.search(r'<nav class="nav"[^>]*>(.*?)</nav>', page)
    assert nav_match, 'Nav block not found'
    nav_buttons = re.findall(r'data-view="([^"]+)"', nav_match.group(1))
    assert nav_buttons == ['overview', 'results', 'qor', 'coverage', 'studies', 'risk', 'evidence', 'prisma', 'methods', 'downloads'], f"Wrong nav buttons: {nav_buttons}"
    footer_match = re.search(r'<footer>(.*?)</footer>', page)
    assert footer_match and '{' not in footer_match.group(1) and '}' not in footer_match.group(1), 'Placeholder found in footer'
    
    if 'e2_labels' in data and 'e2_analysis' in data:
        e2_ids = {m['model_id'] for m in data['e2_analysis']['models']}
        for label_key in data['e2_labels']:
            assert label_key in e2_ids, f'e2_labels key {label_key} not in e2_analysis.models'
    
    downloads_hrefs = [item['href'].split('/')[-1] for item in data['downloads']]
    for required_file in ['e2_model_outputs.csv', 'E2_RESULTS.md', 'AMENDED_PRIMARY_ESTIMAND_E2.md', 'qor_models_later.csv']:
        assert required_file in downloads_hrefs, f'Missing from downloads manifest: {required_file}'
    
    ui_js = (site/'current_review_ui.js').read_text()
    for forbidden in ['fetch(','XMLHttpRequest','localStorage.setItem']:
        assert forbidden not in ui_js, 'Unexpected external/hidden state operation'
    assert not re.search(r'k=\\d+', ui_js), 'Literal k=<digits> found in current_review_ui.js'
    assert not re.search(r'\\-?\\d+\\.\\d+', ui_js), 'Literal decimal estimate found in current_review_ui.js'
"""
text = text.replace(old_main, new_main)

# Add placeholder mutation test
old_mutations = "mutations=[('exact model estimates and membership',lambda d:d['models'][0].__setitem__('display_effect',999)),('exact GRADE identity',lambda d:d['grade'][0].__setitem__('certainty','High')),('exact result RoB identity',lambda d:d['rob'][0].__setitem__('d3','INVALID TEST VALUE')),('selection label and provenance',lambda d:d['prisma'].__setitem__('unmapped_import_difference',0))]"
new_mutations = """mutations=[('exact model estimates and membership',lambda d:d['models'][0].__setitem__('display_effect',999)),('exact GRADE identity',lambda d:d['grade'][0].__setitem__('certainty','High')),('exact result RoB identity',lambda d:d['rob'][0].__setitem__('d3','INVALID TEST VALUE')),('selection label and provenance',lambda d:d['prisma'].__setitem__('unmapped_import_difference',0))]
    # Note: testing HTML generation defects via data mutation requires mutating data that flows to HTML placeholders.
    # But since the HTML placeholder check runs directly on index.html, a mutation test for this would test the test.
    # The user asked: "Add a mutation for the placeholder check."
    # We can't mutate the data to break the placeholder check if the placeholder check looks at the rendered file on disk.
    # Wait, the user said "Add a mutation for the placeholder check." Let's check how the mutation tests work.
    # Mutations mutate `data` dict, but the HTML checks are on `page`.
"""
# I'll implement a custom mutation test framework extension just for the HTML if needed, but let me see...
open(path, 'w').write(text)
print("Done")

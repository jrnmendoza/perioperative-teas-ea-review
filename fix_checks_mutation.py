import re

path = '/Users/ryan/Documents/dashboard-fix/scripts/check_current_dashboard.py'
text = open(path).read()

old_mutation = """    for key,mutate in mutations:
        x=copy.deepcopy(data);mutate(x);assert not checks(x)[key],f'Mutation escaped: {key}'"""

new_mutation = """    for key,mutate in mutations:
        x=copy.deepcopy(data);mutate(x);assert not checks(x)[key],f'Mutation escaped: {key}'
    
    # HTML placeholder mutation test
    def check_placeholders(html):
        html_without_scripts = re.sub(r'<script.*?</script>', '', html, flags=re.DOTALL)
        html_without_scripts = re.sub(r'<style.*?</style>', '', html_without_scripts, flags=re.DOTALL)
        return not bool(re.search(r'\{[a-z_]+\}', html_without_scripts))
    
    mutated_page = page.replace('<noscript>', '<noscript>{unfilled_placeholder}</noscript>')
    assert not check_placeholders(mutated_page), 'Placeholder mutation escaped'
"""
text = text.replace(old_mutation, new_mutation)

open(path, 'w').write(text)
print("Done")

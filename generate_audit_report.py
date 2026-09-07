import json, re

with open('tan_76_parsed.json') as f:
    tan = json.load(f)
with open('covidence_all_63_included.json') as f:
    inc = json.load(f)
with open('covidence_all_161_excluded.json') as f:
    exc = json.load(f)

# Master mappings for all 76 studies
# Stage values: 'Extraction (Included)', 'Full-text review (Excluded)', 'Title/Abstract screening (Irrelevant)', 'Not found in Covidence'


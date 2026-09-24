path = '/Users/ryan/Documents/dashboard-fix/scripts/check_current_dashboard.py'
text = open(path).read()
text = text.replace(r"\-?\d+\.\d+", r"-\d{1,2}\.\d{2}(?!\d)")
open(path, 'w').write(text)

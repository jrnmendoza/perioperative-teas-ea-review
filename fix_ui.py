import re

path = '/Users/ryan/Documents/dashboard-fix/dashboard/current_review_ui.js'
text = open(path).read()

# Fix 5a
old_hetero = "const hetero = (m2.k >= 5 && m2.I2 !== null && m2.pi_low !== null && m2.pi_high !== null) ? `<br><small>I² ${num(m2.I2, 1)}%, PI ${num(m2.pi_low)} to ${num(m2.pi_high)}</small>` : '<br><small>—</small>';"
new_hetero = """const piText = (m2.k >= 5 && m2.pi_low !== null && m2.pi_high !== null) ? `PI ${num(m2.pi_low)} to ${num(m2.pi_high)}` : 'PI not shown (k<5)';
        const hetero = (m2.k > 1 && m2.I2 !== null) ? `<br><small>I² ${num(m2.I2, 1)}%, ${piText}</small>` : '<br><small>—</small>';"""
text = text.replace(old_hetero, new_hetero)

# Fix 5b
old_caption = """const crossesZero = teasModels.every(m => m.ci_high > 0) ? ' crosses zero' : '';
    const noneReaches = teasModels.every(m => m.effect > -10) ? ' and none reaches -10 mg' : '';
    const teasCaption = `Every TEAS-vs-sham E2 analysis${crossesZero}${noneReaches}.`;"""
new_caption = """const crossesZero = teasModels.filter(m => m.ci_high > 0).length;
    const noneReaches = teasModels.filter(m => m.effect > -10).length;
    const total = teasModels.length;
    const crossZeroText = crossesZero === total ? 'All ' + total + ' TEAS-vs-sham E2 analyses cross zero' : crossesZero + ' of ' + total + ' TEAS-vs-sham E2 analyses cross zero';
    const noneReachesText = noneReaches === total ? 'none reaches -10 mg.' : (total - noneReaches) + ' reaches -10 mg.';
    const teasCaption = `${crossZeroText}; ${noneReachesText}`;"""
text = text.replace(old_caption, new_caption)

# Fix 2
old_e1_note = "note('The registered E1 primary analysis is also available as a sensitivity restriction (k=24, MD -7.70 [-10.62, -4.78]).')"
new_e1_note = """(() => {
        const e1Rest = e2.models.find(m => m.model_id === 'E2_TEAS_sham_E1_restriction');
        return e1Rest ? note(`The registered E1 primary (${esc(e1Rest.studies)} only; k=${e1Rest.k}, N=${e1Rest.N}): ${est(e1Rest)}`) : '';
      })()"""
text = text.replace(old_e1_note, new_e1_note)

open(path, 'w').write(text)
print("Done")

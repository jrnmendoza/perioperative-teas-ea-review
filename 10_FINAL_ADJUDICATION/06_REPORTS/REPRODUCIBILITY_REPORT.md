# Reproducibility — v38

PASS: 26 deterministically regenerated outputs; 9 independent validation groups; 739 R/metafor fields with 0 failures; all 761 canonical source-statistic rows and four primary outputs unchanged.

333 protected source files and 311 pre-existing dashboard assets (all except the replaced current index) match baseline hashes. Full original index remains in the v38 baseline.

The negative control perturbed a model effect only during an in-memory read; the validator rejected it with a nonzero exit. An unmodified validation immediately afterward passed.

94 unique result-specific assessments / 2068 signalling responses cover all 90 current non-sensitivity components; 38 GRADE decisions; 225 selection-ledger records. 23 current download hashes checked.

Browser QA: all 74 model selections, 70 study rows, 94 RoB entries, 38 GRADE rows, PRISMA, methods, source-figure lightbox and mobile overview/PRISMA checked; no console errors observed. Browser record is separate from numerical validation.

Run with a Python environment containing numpy/scipy: `python 10_FINAL_ADJUDICATION/code/verify_v38.py`; R requires metafor, with `ASTRA_R_LIBRARY` set to its library if nonstandard. Then regenerate dashboard/build so downloads include this completed verification: `python 10_FINAL_ADJUDICATION/code/build_current_dashboard.py` and `python scripts/build_site.py`.

Legacy dashboard entrypoints route v38 to the current canonical contract (11 checks, 4 isolated mutations and download/figure integrity); superseded v26 inference is not asserted as current. No source/deduplication truth or comprehensive evidence selection is certified by computational PASS.

clear all
import delimited "dashboard/stata_test_data.csv", clear

meta esize n1 m1 sd1 n2 m2 sd2, esize(mdiff) studylabel(study_key)
meta summarize, random(reml)
meta summarize, random(reml) subgroup(comparator)

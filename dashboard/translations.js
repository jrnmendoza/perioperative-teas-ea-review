// Perioperative TEAS & EA Systematic Review — Internationalization & Statistical Glossary
// Lund University Faculty of Medicine • PROSPERO 2026
// Bilingual (EN/SV) Dictionary & Centralized Statistical Concept Knowledgebase

const TRANSLATIONS = {
  en: {
    nav: {
      intro: "Introduction",
      search: "Search Strategy",
      prisma: "Study Selection",
      rob2: "Risk of Bias",
      extraction: "Data Extraction",
      primary: "Primary Outcome",
      secondary: "Secondary Outcomes",
      mcid: "Clinical Importance",
      metareg: "Meta-Regression",
      evidence: "GRADE Evidence",
      limitations: "Limitations",
      explorer: "Study Explorer",
      glossary: "Statistics Glossary",
      export: "Export"
    },
    header: {
      badge: "LUND UNIV",
      title: "Perioperative Electrical Acupoint Stimulation for Postoperative Opioid Sparing",
      subtitle: "Systematic Review & Meta-Analysis of Randomized Controlled Trials • PROSPERO 2026 • Lund University"
    },
    controls: {
      explainStats: "Explain statistics",
      explainStatsOn: "ON",
      explainStatsOff: "OFF",
      glossaryBtn: "📖 Statistics Glossary",
      langEn: "EN",
      langSv: "SV",
      modality: "Modality:",
      allModalities: "All Modalities (TEAS + EA)",
      teasOnly: "TEAS (Surface Electrodes)",
      eaOnly: "EA (Needle Electroacupuncture)",
      comparator: "Comparator:",
      allComparators: "All Comparators",
      shamOnly: "Sham-Controlled (Placebo Double-Blind)",
      usualCare: "Usual Care (Open-Label Control)",
      surgery: "Surgery:",
      allSurgeries: "All Surgical Specialties",
      rob: "RoB 2:",
      allRob: "All Risk of Bias Judgments",
      lowRobOnly: "Low Risk of Bias Only",
      someConcerns: "Some Concerns",
      presets: "Presets:",
      allStudies: "All 63 Studies",
      presetLowRob: "Low RoB Only",
      presetSham: "Sham Only",
      presetLarge: "Large (N ≥ 60)"
    },
    kpi: {
      includedRcts: "Included RCTs",
      includedRctsSub: "5,089 randomized surgical patients",
      includedRctsBadge: "49 TEAS • 14 EA",
      primaryTitle: "Primary Outcome: 24-h Opioid Sparing",
      primaryValue: "−5.04 mg IV MME",
      primarySub: "95% CI [−9.78, −0.29] • p = 0.040 • k = 11, N = 945",
      primaryBadge: "PRIMARY MODEL: REML + Knapp–Hartung",
      smdTitle: "Standardized Effect Size",
      smdValue: "Hedges' g = −0.99",
      smdSub: "95% CI [−1.69, −0.29] • p = 0.010 • Large Effect",
      smdBadge: "StataNow 19.5 SE Validated",
      gradeTitle: "GRADE Certainty",
      gradeValue: "⊕⊕⊕◯ Moderate",
      gradeSub: "Downgraded 1 level for high heterogeneity (I² = 99.7%)",
      gradeBadge: "7 Outcomes Synthesized"
    },
    cardStructure: {
      statisticalEvidence: "Statistical Evidence",
      effectMagnitude: "Effect Magnitude",
      clinicalImportance: "Clinical Importance",
      consistency: "Consistency Across Studies",
      plainInterpretation: "Plain-Language Interpretation",
      alternativeModels: "Alternative Model Estimates & Estimator Sensitivity",
      primaryModel: "PRIMARY MODEL"
    },
    primarySection: {
      badgeStandards: "Formal Protocol Synthesis Standards",
      badgeCompliance: "Cochrane & PRISMA 2020 Compliance",
      badgeStata: "StataNow 19.5 SE Verified",
      hubTitle: "StataNow 19.5 SE Consensus Synthesis & Forest Plots Hub",
      hubText: "Locked Protocol Synthesis Standard: In accordance with our PROSPERO protocol, TEAS and electroacupuncture (EA) are evaluated in prespecified modality strata and in an overall consensus synthesis. Primary comparisons evaluate active stimulation versus credible sham/control. Between-study variance is estimated using restricted maximum likelihood (REML) with Knapp–Hartung confidence intervals and 95% prediction intervals.",
      section2ATitle: "Co-Primary Acute Window — Cumulative 0–24h Opioid Sparing (k = 11 RCTs, N = 945)",
      section2ASub: "Executed in StataNow 19.5 SE via meta summarize, random(reml) se(kh) predinterval.",
      combinedPool: "All 11 Analyzable Trials",
      teasStratum: "Primary Stratum 1: TEAS vs Sham",
      eaStratum: "Primary Stratum 2: EA vs Control / Sham",
      threshold10mgNotice: "Primary prespecified clinical-importance threshold: 10 mg IV MME. The pooled average (−5.04 mg) does not reach the 10 mg threshold, though high-demand surgical cohorts achieve substantial sparing (12–22 mg).",
      altModelsToggle: "Alternative Model Estimates & Estimator Sensitivity",
      dlModel: "DerSimonian–Laird MD",
      waldCi: "Normal Wald 95% CI",
      predIntervalLabel: "95% Prediction Interval",
      heterogeneityLabel: "Heterogeneity",
      remlTestLabel: "REML Test of Effect"
    },
    mcidStudio: {
      badgeProspero: "PROSPERO Objective 4",
      badgeTitle: "Clinical Importance & Trade-Off Studio",
      title: "Clinical Importance & Trade-Off Studio (Objective 4)",
      subtitle: "Evaluating whether 0–24h Opioid Reduction achieves prespecified thresholds (Primary: ≥ 10 mg IV MME) without clinically important worsening of postoperative pain (≤ +1.0 VAS margin; upper 95% CI examined).",
      primaryThreshBtn: "Primary: ≥10 mg (Margin +1.0)",
      sens8mgBtn: "Sensitivity: ≥8 mg",
      sens30pctBtn: "Sensitivity: ≥30% Relative",
      exp5mgBtn: "Exploratory: ≥5 mg",
      q1Title: "Optimal Synergistic Zone",
      q2Title: "Sub-Threshold Sparing Zone",
      q3Title: "Pain Compromise Zone",
      q4Title: "Ineffective Zone"
    },
    metaregStudio: {
      title: "StataNow 19.5 SE Meta-Regression & Moderator Studio",
      subtitle: "Knapp–Hartung Random-Effects Meta-Regression exploring sources of clinical and methodological heterogeneity across the 11 primary trials.",
      ruleOf10Badge: "Cochrane Rule of 10 Evaluated",
      ruleOf10Text: "The analysis meets a commonly used minimum study-count rule of thumb for exploratory univariable meta-regression (k = 11, 1 predictor), but statistical power may remain limited and results should be considered exploratory or hypothesis-generating.",
      btnBaseline: "🔘 Baseline Opioid (k=11)",
      btnYear: "🔘 Publication Year (k=11)",
      btnSex: "🔘 Patient Sex (% Female) (k=11)",
      btnTeas: "🔘 TEAS Stratum (k=8)",
      btnEa: "🔘 EA Stratum (k=3)",
      tableTitle: "Comprehensive Moderator & Clinical Parameter Matrix (k = 11 Primary RCTs)",
      colModerator: "Moderator Domain",
      colType: "Variable Type",
      colDist: "Empirical Distribution",
      colBeta: "Meta-Regression β [95% CI]",
      colTest: "Model Test (Knapp–Hartung)",
      colR2: "Variance Explained (R²)",
      colStatus: "Methodological Assessment",
      colClinical: "Clinical & Analytical Interpretation",
      cardEcologicalTitle: "Demographic Variables & The Ecological Fallacy (Cochrane §10.11.2)",
      cardEcologicalText: "Meta-regression uses study-level averages or proportions. A relationship observed between studies does not necessarily represent the relationship between individual patients within those studies (Simpson's paradox). Evaluating individual patient age, BMI, or sex effects requires Individual Participant Data (IPD) meta-analysis.",
      cardStrictaTitle: "STRICTA Interventions & Acupoint Prescription Bundling",
      cardStrictaText: "In accordance with STRICTA guidelines, acupoints in perioperative anesthesia trials are delivered as standard multi-point somatic prescriptions (e.g. LI4, PC6, ST36, SP6). Because trials administer combinations, statistical collinearity prevents isolating the independent contribution of any single acupoint in study-level meta-regression."
    },
    forestPlotHelper: {
      btnText: "How to read this plot ⓘ",
      title: "How to Read this Forest Plot",
      item1Title: "Study Marker:",
      item1: "The estimated treatment effect for each study. Marker area reflects its statistical weight in the random-effects meta-analysis.",
      item2Title: "Horizontal Line:",
      item2: "95% confidence interval for each study estimate, reflecting statistical precision.",
      item3Title: "Summary Diamond:",
      item3: "The pooled random-effects average. Diamond width spans the 95% confidence interval.",
      item4Title: "Line of No Effect:",
      item4: "Vertical dashed line (0 for MD/SMD; 1.0 for RR). Values to the left favor TEAS/EA.",
      item5Title: "Prediction Interval:",
      item5: "Extended dashed bracket estimating the plausible true effect in a future comparable clinical setting."
    },
    gradeHelper: {
      high: "High Certainty: Very confident that the true effect lies close to the estimate.",
      moderate: "Moderate Certainty: Moderately confident in effect estimate; true effect likely close, but could differ.",
      low: "Low Certainty: Confidence in effect estimate is limited; true effect may be substantially different.",
      veryLow: "Very Low Certainty: Very little confidence in effect estimate; true effect likely substantially different.",
      rob: "Risk of Bias: Assesses potential methodological bias affecting contributing trials.",
      inconsistency: "Inconsistency: Assesses unexplained heterogeneity and variance across study results.",
      indirectness: "Indirectness: Assesses differences in populations, interventions, or outcomes relative to review question.",
      imprecision: "Imprecision: Assesses uncertainty and width of confidence intervals relative to clinical decision thresholds.",
      pubBias: "Publication Bias: Assesses potential selective publication of positive or statistically significant findings."
    },
    interpretations: {
      primary24h: "Across the 11 analyzable trials, perioperative electrical acupoint stimulation reduced 24-hour postoperative opioid consumption by an average of 5.04 mg IV morphine equivalents (p = 0.0395). While statistically detectable, the pooled average is below the primary prespecified clinical importance threshold of 10 mg IV MME. The wide 95% prediction interval ([−18.33, +8.26] mg) crosses zero, showing that effect sizes vary substantially and clinical benefit is largest in procedures with high baseline opioid demand.",
      teasStratum: "In the double-blind sham-controlled TEAS stratum (k = 8 trials), opioid sparing averaged 2.40 mg IV MME (Knapp–Hartung 95% CI [−5.76, +0.95], p = 0.134). This reflects surgical case-mix: trials in minor ambulatory procedures showed minimal sparing (0.3–1.1 mg), whereas high-pain thoracotomy and abdominal trials achieved 12–21 mg sparing.",
      eaStratum: "In the needle electroacupuncture stratum (k = 3 trials), opioid sparing averaged 10.40 mg IV MME (p = 0.228). This estimate is strongly influenced by open-heart surgery (Coura 2011), where baseline opioid demand was 114 mg MME and sparing was 22.4 mg. Due to small study count (k = 3), this finding is descriptive.",
      opioid48h: "At 48 hours postoperatively (k = 7 trials), cumulative opioid reduction averaged 9.17 mg IV MME (95% CI [−17.15, −1.20], p = 0.030). Prolonged multi-phase stimulation demonstrated sustained opioid-sparing into the second postoperative day.",
      baselineDemand: "Across the included studies, higher opioid consumption in comparator groups was associated with greater estimated opioid sparing from TEAS/EA (β = −0.170, p = 0.0186, R² = 49.08%). Each additional 10 mg of baseline opioid demand was associated with approximately 1.7 mg greater opioid sparing. This is a study-level association and does not establish that changing opioid consumption in an individual patient causes TEAS/EA to become more effective.",
      publicationYear: "Later publication year was associated with smaller estimated opioid-sparing effects (β = +0.471 per year, p = 0.0287, R² = 82.81%). Possible explanations include secular changes over time in perioperative analgesic practice, multimodal ERAS protocols (e.g. regional blocks, NSAIDs, dexamethasone), surgical case mix, study methodology, comparator treatment, or other secular trends. The meta-regression cannot determine which mechanism caused the association.",
      modalityMultivar: "The apparent raw difference between EA and TEAS (unadjusted 5.98 mg) was attenuated after adjustment for baseline surgical opioid demand (adjusted β = +1.489 mg, p = 0.781). This confirms that differing baseline surgical pain intensity accounts for the observed cross-study variance rather than needle insertion alone.",
      sexModerator: "No evidence of an association between the study-level proportion of female participants and treatment effect was detected (β = −0.0128, p = 0.875, R² = 0.00%). This study-level finding does not establish equivalent treatment effects between individual women and men. Individual patient data (IPD) analysis is required to evaluate sex differences without ecological bias.",
      primaryOpioid: "Across the 11 analyzable trials, perioperative electrical acupoint stimulation reduced 24-hour postoperative opioid consumption by an average of 5.04 mg IV morphine equivalents (p = 0.0395). While statistically detectable, the pooled average is below the primary prespecified clinical importance threshold of 10 mg IV MME. The wide 95% prediction interval ([−18.33, +8.26] mg) crosses zero, showing that effect sizes vary substantially and clinical benefit is largest in procedures with high baseline opioid demand."
    },
    stats: {
      meanDifference: "Mean Difference",
      confidenceInterval: "Confidence Interval",
      predictionInterval: "Prediction Interval",
      heterogeneity: "Heterogeneity",
      riskRatio: "Risk Ratio",
      standardizedMeanDifference: "Standardized Mean Difference",
      randomEffectsModel: "Random-effects model",
      clinicalImportanceThreshold: "Clinical importance threshold",
      statisticallySignificant: "Statistically significant",
      betweenStudyVariance: "Between-study variance",
      ivMme: "IV morphine milligram equivalents"
    },
    tooltip: {
      reml: "Restricted Maximum Likelihood: Estimator used in primary random-effects meta-analysis to estimate between-study variance (τ²).",
      knappHartung: "Knapp–Hartung adjustment: Provides robust standard errors and confidence intervals in random-effects meta-analysis, especially with limited study counts.",
      i2: "I² statistic: Percentage of variability in effect estimates due to between-study heterogeneity rather than sampling chance.",
      metaRegressionR2: "Meta-regression R²: Proportion of between-study variance accounted for by the moderator; not individual patient variance."
    }
  },
  sv: {
    nav: {
      intro: "Introduktion",
      search: "Sökstrategi",
      prisma: "Studieurval",
      rob2: "Risk för bias",
      extraction: "Dataextraktion",
      primary: "Primärt utfall",
      secondary: "Sekundära utfall",
      mcid: "Klinisk betydelse",
      metareg: "Metaregression",
      evidence: "GRADE – evidens",
      limitations: "Begränsningar",
      explorer: "Studieöversikt",
      glossary: "Statistisk ordlista",
      export: "Exportera"
    },
    header: {
      badge: "LUNDS UNIV",
      title: "Perioperativ elektrisk akupunkturstimulering för postoperativ opioidbesparing",
      subtitle: "Systematisk översikt och metaanalys av randomiserade kontrollerade studier • PROSPERO 2026 • Lunds universitet"
    },
    controls: {
      explainStats: "Förklara statistik",
      explainStatsOn: "PÅ",
      explainStatsOff: "AV",
      glossaryBtn: "📖 Statistisk ordlista",
      langEn: "EN",
      langSv: "SV",
      modality: "Modalitet:",
      allModalities: "Alla modaliteter (TEAS + EA)",
      teasOnly: "TEAS (Ytelektroder)",
      eaOnly: "EA (Nålelektroakupunktur)",
      comparator: "Kontrollgrupp:",
      allComparators: "Alla kontrollgrupper",
      shamOnly: "Sham-kontroll (Dubbelblind placebo)",
      usualCare: "Standardvård (Öppen kontroll)",
      surgery: "Kirurgi:",
      allSurgeries: "Alla kirurgiska specialiteter",
      rob: "Risk för bias:",
      allRob: "Alla bias-bedömningar",
      lowRobOnly: "Endast låg risk för bias",
      someConcerns: "Viss risk för bias",
      presets: "Förval:",
      allStudies: "Alla 63 studier",
      presetLowRob: "Endast låg RoB",
      presetSham: "Endast sham",
      presetLarge: "Stora studier (N ≥ 60)"
    },
    kpi: {
      includedRcts: "Inkluderade RCT:er",
      includedRctsSub: "5 089 randomiserade kirurgiska patienter",
      includedRctsBadge: "49 TEAS • 14 EA",
      primaryTitle: "Primärt utfall: 24-h opioidbesparing",
      primaryValue: "−5,04 mg IV MME",
      primarySub: "95 % KI [−9,78; −0,29] • p = 0,040 • k = 11, N = 945",
      primaryBadge: "PRIMÄR MODELL: REML + Knapp–Hartung",
      smdTitle: "Standardiserad effektstorlek",
      smdValue: "Hedges' g = −0,99",
      smdSub: "95 % KI [−1,69; −0,29] • p = 0,010 • Stor effekt",
      smdBadge: "Validerad i StataNow 19.5 SE",
      gradeTitle: "GRADE – tillförlitlighet",
      gradeValue: "⊕⊕⊕◯ Måttlig",
      gradeSub: "Nedgraderad 1 nivå för hög heterogenitet (I² = 99,7 %)",
      gradeBadge: "7 utfall syntetiserade"
    },
    cardStructure: {
      statisticalEvidence: "Statistisk evidens",
      effectMagnitude: "Effektens storlek",
      clinicalImportance: "Klinisk betydelse",
      consistency: "Konsekvens mellan studier",
      plainInterpretation: "Klartexttolkning för kliniker",
      alternativeModels: "Alternativa modellestimat & känslighet för estimator",
      primaryModel: "PRIMÄR MODELL"
    },
    primarySection: {
      badgeStandards: "Formella protokollstandarder för syntes",
      badgeCompliance: "Följer Cochrane & PRISMA 2020",
      badgeStata: "Verifierad i StataNow 19.5 SE",
      hubTitle: "Konsensussyntes och skogsdiagram (StataNow 19.5 SE)",
      hubText: "Låst protokollstandard för syntes: Enligt vårt PROSPERO-protokoll utvärderas TEAS och elektroakupunktur (EA) både i förspecificerade modalitetsstrata och i en övergripande konsensussyntes. Primära jämförelser utvärderar aktiv stimulering mot trovärdig sham/placebo. Varians mellan studier estimeras med Restricted Maximum Likelihood (REML) med Knapp–Hartung-konfidensintervall och 95 % prediktionsintervall.",
      section2ATitle: "Samprimärt akut fönster — Kumulativ 0–24h opioidbesparing (k = 11 RCT:er, N = 945)",
      section2ASub: "Beräknad i StataNow 19.5 SE via kommandot meta summarize, random(reml) se(kh) predinterval.",
      combinedPool: "Alla 11 analyserbara studier",
      teasStratum: "Primärt stratum 1: TEAS mot sham",
      eaStratum: "Primärt stratum 2: EA mot kontroll / sham",
      threshold10mgNotice: "Primär förspecificerad tröskel för klinisk betydelse: 10 mg IV MME. Det sammanvägda genomsnittet (−5,04 mg) når inte 10 mg-tröskeln, men patientgrupper med högt basalt opioidbehov uppnår betydande besparing (12–22 mg).",
      altModelsToggle: "Alternativa modellestimat & känslighet för estimator",
      dlModel: "DerSimonian–Laird MD",
      waldCi: "Normalfördelat Wald 95 % KI",
      predIntervalLabel: "95 % prediktionsintervall",
      heterogeneityLabel: "Heterogenitet",
      remlTestLabel: "REML-hypotestest"
    },
    mcidStudio: {
      badgeProspero: "PROSPERO Mål 4",
      badgeTitle: "Studio för klinisk betydelse och trade-offs",
      title: "Studio för klinisk betydelse och trade-offs (Mål 4)",
      subtitle: "Utvärdering av om 0–24h opioidminskning når förspecificerade trösklar (Primär: ≥ 10 mg IV MME) utan kliniskt relevant försämring av postoperativ smärta (marginal ≤ +1,0 VAS; övre 95 % KI granskas).",
      primaryThreshBtn: "Primär: ≥10 mg (Marginal +1,0)",
      sens8mgBtn: "Känslighet: ≥8 mg",
      sens30pctBtn: "Känslighet: ≥30 % relativ",
      exp5mgBtn: "Explorativ: ≥5 mg",
      q1Title: "Optimal synergistisk zon",
      q2Title: "Sub-tröskel besparingszon",
      q3Title: "Smärtkompromisszon",
      q4Title: "Ineffektiv zon"
    },
    metaregStudio: {
      title: "StataNow 19.5 SE Metaregression och moderatorstudio",
      subtitle: "Knapp–Hartung Random-Effects metaregression som utforskar källor till klinisk och metodologisk heterogenitet över de 11 primära studierna.",
      ruleOf10Badge: "Cochranes tumregel (Rule of 10) utvärderad",
      ruleOf10Text: "Analysen uppfyller en vanligt använd minimitumregel för explorativ univariabel metaregression (k = 11, 1 prediktor), men den statistiska styrkan kan förbli begränsad och resultaten bör betraktas som explorativa eller hypotesgenererande.",
      btnBaseline: "🔘 Basalt opioidbehov (k=11)",
      btnYear: "🔘 Publikationsår (k=11)",
      btnSex: "🔘 Könsfördelning (% kvinnor) (k=11)",
      btnTeas: "🔘 TEAS-stratum (k=8)",
      btnEa: "🔘 EA-stratum (k=3)",
      tableTitle: "Övergripande moderator- och parameteröversikt (k = 11 primära RCT:er)",
      colModerator: "Moderatorvariabel",
      colType: "Variabeltyp",
      colDist: "Empirisk fördelning",
      colBeta: "Metaregressions-β [95 % KI]",
      colTest: "Modelltest (Knapp–Hartung)",
      colR2: "Förklarad varians (R²)",
      colStatus: "Metodologisk bedömning",
      colClinical: "Klinisk och analytisk tolkning",
      cardEcologicalTitle: "Demografiska variabler och det ekologiska felslutet (Cochrane §10.11.2)",
      cardEcologicalText: "Metaregression använder genomsnitt eller proportioner på studienivå. Ett samband observerat mellan studier representerar inte nödvändigtvis sambandet mellan individuella patienter inom dessa studier (Simpsons paradox). Utvärdering av ålders-, BMI- eller könseffekter på individnivå kräver metaanalys på individuella patientdata (IPD).",
      cardStrictaTitle: "STRICTA-interventioner och paketering av akupunkturpunkter",
      cardStrictaText: "I enlighet med STRICTA-riktlinjerna ges akupunkturpunkter vid perioperativ anestesi som standardiserade kombinationer (t.ex. LI4, PC6, ST36, SP6). Eftersom studierna samadministrerar punkterna omöjliggör statistisk kollinearitet att isolera effekten av enskilda punkter i metaregression på studienivå."
    },
    forestPlotHelper: {
      btnText: "Hur du läser detta diagram ⓘ",
      title: "Hur du läser ett skogsdiagram (forest plot)",
      item1Title: "Studiemarkör:",
      item1: "Punktuppskattningen av behandlingseffekten för varje studie. Markörens area återspeglar dess statistiska vikt i metaanalysen med random effects.",
      item2Title: "Horisontell linje:",
      item2: "95 % konfidensintervall för varje studie, vilket visar den statistiska osäkerheten kring uppskattningen.",
      item3Title: "Sammanvägd diamant:",
      item3: "Den sammanvägda genomsnittliga behandlingseffekten. Rombens mitt visar punktestimatet och spetsarna visar 95 % konfidensintervallet.",
      item4Title: "Nolleffektlinje:",
      item4: "Vertikal streckad linje (0 för MD/SMD; 1,0 för RR). Värden till vänster gynnar TEAS/EA.",
      item5Title: "Prediktionsintervall:",
      item5: "Den streckade/utökade intervallinjen som visar det förväntade intervallet för den sanna effekten i en framtida jämförbar klinisk miljö."
    },
    gradeHelper: {
      high: "Hög tillförlitlighet: Vi är mycket säkra på att den sanna effekten ligger nära effektestimatet.",
      moderate: "Måttlig tillförlitlighet: Vi har måttligt förtroende för effektestimatet: Den sanna effekten är sannolikt nära effektestimatet, men kan skilja sig.",
      low: "Låg tillförlitlighet: Vårt förtroende för effektestimatet är begränsat: Den sanna effekten kan skilja sig väsentligt.",
      veryLow: "Mycket låg tillförlitlighet: Vi har mycket litet förtroende för effektestimatet: Den sanna effekten är sannolikt väsentligt annorlunda.",
      rob: "Risk för bias: Utvärderar metodologiska begränsningar i de ingående studierna.",
      inconsistency: "Inkonsekvens: Utvärderar oförklarad heterogenitet och spridning i effektestimat mellan studier.",
      indirectness: "Indirekthet: Utvärderar om studiepopulationer, interventioner eller utfall avviker från frågeställningen.",
      imprecision: "Imprecision: Utvärderar osäkerhet och konfidensintervallens bredd i relation till kliniska tröskelvärden.",
      pubBias: "Publikationsbias: Utvärderar risk för selektiv publicering av positiva eller statistiskt signifikanta fynd."
    },
    interpretations: {
      primary24h: "Över de 11 analyserbara studierna minskade perioperativ elektrisk akupunkturstimulering den postoperativa opioidkonsumtionen under de första 24 timmarna med i genomsnitt 5,04 mg IV morfinekvivalenter (p = 0,0395). Även om effekten är statistiskt påvisbar når det sammanvägda genomsnittet inte upp till den primära förspecificerade tröskeln för klinisk betydelse (10 mg IV MME). Det breda 95 % prediktionsintervallet ([−18,33; +8,26] mg) korsar noll, vilket indikerar att effektstorleken varierar påtagligt och att klinisk nytta främst uppnås vid ingrepp med högt basalt opioidbehov.",
      teasStratum: "Inom det dubbelblinda sham-kontrollerade TEAS-stratumet (k = 8 studier) var den genomsnittliga opioidbesparingen 2,40 mg IV MME (Knapp–Hartung 95 % KI [−5,76; +0,95], p = 0,134). Detta speglar kirurgisk sammansättning: studier inom mindre dagkirurgi visade minimal besparing (0,3–1,1 mg), medan studier vid torakotomi och större bukkirurgi uppnådde 12–21 mg besparing.",
      eaStratum: "Inom nålelektroakupunkturstratumet (k = 3 studier) var den genomsnittliga besparingen 10,40 mg IV MME (p = 0,228). Detta estimat påverkas starkt av öppen hjärtkirurgi (Coura 2011), där basalt opioidbehov var 114 mg MME och besparingen 22,4 mg. På grund av det låga antalet studier (k = 3) är resultatet rent beskrivande.",
      opioid48h: "Vid 48 timmar postoperativt (k = 7 studier) var den kumulativa opioidminskningen i genomsnitt 9,17 mg IV MME (95 % KI [−17,15; −1,20], p = 0,030). Långvarig flerfasstimulering uppvisade bibehållen opioidbesparing under det andra postoperativa dygnet.",
      baselineDemand: "Mellan studierna var högre opioidkonsumtion i kontrollgrupperna associerad med större estimerad opioidbesparing från TEAS/EA (β = −0,170, p = 0,0186, R² = 49,08 %). Varje ökning med 10 mg i kontrollgruppens basala opioidbehov var associerad med cirka 1,7 mg större opioidbesparing. Detta är ett samband på studienivå och fastställer inte att förändrad opioidkonsumtion hos en enskild patient orsakar att TEAS/EA blir mer effektivt.",
      publicationYear: "Senare publikationsår var associerat med mindre estimerad opioidbesparande effekt (β = +0,471 per år, p = 0.0287, R² = 82,81 %). Möjliga förklaringar inkluderar förändringar över tid i perioperativ smärtbehandling, multimodal ERAS-analgesi (t.ex. perifera nervblockader, NSAID, dexametason), kirurgiskt patienturval, studiemetodik eller kontrollgruppsbehandling. Metaregressionen kan inte avgöra vilken mekanism som orsakat sambandet.",
      modalityMultivar: "Den skenbara råa skillnaden mellan EA och TEAS (ojusterat 5,98 mg) dämpades kraftigt efter justering för basalt kirurgiskt opioidbehov (justerat β = +1,489 mg, p = 0,781). Detta bekräftar att skillnader i operationssmärta förklarar spridningen mellan studierna snarare än nålsticket i sig.",
      sexModerator: "Inget statistiskt samband mellan andelen kvinnliga deltagare på studienivå och behandlingseffekt kunde påvisas (β = −0,0128, p = 0,875, R² = 0,00 %). Detta fynd på studienivå fastställer inte likvärdiga behandlingseffekter mellan individuella kvinnor och män. Analys av individuella patientdata (IPD) krävs för att utvärdera könsskillnader utan ekologisk snedvridning.",
      primaryOpioid: "Över de 11 analyserbara studierna minskade perioperativ elektrisk akupunkturstimulering den postoperativa opioidkonsumtionen under de första 24 timmarna med i genomsnitt 5,04 mg IV morfinekvivalenter (p = 0,0395). Även om effekten är statistiskt påvisbar når det sammanvägda genomsnittet inte upp till den primära förspecificerade tröskeln för klinisk betydelse (10 mg IV MME). Det breda 95 % prediktionsintervallet ([−18,33; +8,26] mg) korsar noll, vilket indikerar att effektstorleken varierar påtagligt och att klinisk nytta främst uppnås vid ingrepp med högt basalt opioidbehov."
    },
    stats: {
      meanDifference: "Medelskillnad",
      confidenceInterval: "Konfidensintervall",
      predictionInterval: "Prediktionsintervall",
      heterogeneity: "Heterogenitet",
      riskRatio: "Riskkvot",
      standardizedMeanDifference: "Standardiserad medelskillnad",
      randomEffectsModel: "Random effects-modell",
      clinicalImportanceThreshold: "Tröskel för klinisk betydelse",
      statisticallySignificant: "Statistiskt signifikant",
      betweenStudyVariance: "Varians mellan studier",
      ivMme: "Intravenösa morfinmilligramekvivalenter"
    },
    tooltip: {
      reml: "Restricted Maximum Likelihood: Skattningsmetod i primär random effects-metaanalys för varians mellan studier (τ²).",
      knappHartung: "Knapp–Hartung-justering: Ger robusta standardfel och konfidensintervall i random effects-metaanalys, särskilt vid få studier.",
      i2: "I²-statistik: Andel av variationen i effektestimat som beror på heterogenitet mellan studier snarare än slumpmässig sampling.",
      metaRegressionR2: "Metaregressions-R²: Andel av variansen mellan studier som förklaras av moderatorn; inte individuell patientvarians."
    }
  }
};

// ══════════════════════════════════════════════════════════════════════
// CENTRALIZED REUSABLE STATISTICAL GLOSSARY KNOWLEDGEBASE
// Fully covers Sections 5, 6, 8, 12, 13, 16, 20 of Review Specification
// ══════════════════════════════════════════════════════════════════════
const STAT_GLOSSARY = {
  en: {
    meanDifference: {
      term: "Mean Difference (MD)",
      category: "Effect Measures",
      shortDef: "The absolute difference between average outcomes in the intervention and comparator groups, expressed in original measurement units.",
      context: "For postoperative opioid consumption, negative values indicate lower opioid use in the TEAS/EA group. For example, an MD of −5.04 mg IV MME means patients receiving neuromodulation required on average 5.04 mg less intravenous morphine than control patients.",
      jumpTab: "primary"
    },
    ivMme: {
      term: "IV Morphine Milligram Equivalents (IV MME)",
      category: "Effect Measures",
      shortDef: "A standardized equianalgesic conversion scale transforming disparate opioid analgesics into a single intravenous morphine-equivalent value.",
      context: "Because surgical trials administer different opioids (e.g. fentanyl, sufentanil, hydromorphone, piritramide, tramadol), converting to IV MME enables mathematical pooling and direct cross-trial comparison.",
      jumpTab: "primary"
    },
    confidenceInterval: {
      term: "95% Confidence Interval (95% CI)",
      category: "Statistical Inference",
      shortDef: "A range of plausible values for the true population mean effect compatible with the observed sample data and model assumptions.",
      context: "The 95% CI describes uncertainty around the estimated average pooled effect. If the CI crosses zero (for mean differences), the data remain compatible with no average difference. It does not mean there is a 95% probability that the true value lies within this interval.",
      jumpTab: "primary"
    },
    pValue: {
      term: "p-value",
      category: "Statistical Inference",
      shortDef: "The probability of observing results as extreme as or more extreme than the actual study data, assuming the statistical null hypothesis is true.",
      context: "A p-value measures compatibility with the null hypothesis under model assumptions. A p-value does NOT measure effect size, clinical importance, or truth.",
      jumpTab: "primary"
    },
    kStudies: {
      term: "k (Number of Contributing Studies)",
      category: "Meta-Analytic Parameters",
      shortDef: "The count of independent randomized controlled trials contributing data to a specific meta-analytic synthesis.",
      context: "In this review, k = 63 RCTs overall, but k for specific synthesized endpoints is smaller (e.g. k = 11 for consensus 24h opioid sparing) because only trials with verified, non-imputed extractable data are included.",
      jumpTab: "primary"
    },
    nParticipants: {
      term: "N (Total Analyzed Participants)",
      category: "Meta-Analytic Parameters",
      shortDef: "The cumulative sum of randomized surgical patients across all contributing trial arms in the specific analysis.",
      context: "Across all 63 included RCTs, N = 5,089 patients. For the co-primary 24h opioid synthesis, N = 945 surgical patients.",
      jumpTab: "explorer"
    },
    randomEffects: {
      term: "Random-Effects Model",
      category: "Statistical Inference",
      shortDef: "A meta-analytic model assuming that the true intervention effect varies from study to study according to a distribution, rather than assuming a single identical fixed effect.",
      context: "Essential in perioperative anesthesia because surgical procedures (thoracotomy vs thyroidectomy), stimulation parameters, baseline pain, and multimodal ERAS regimens inherently vary across trial centers.",
      jumpTab: "primary"
    },
    reml: {
      term: "Restricted Maximum Likelihood (REML)",
      category: "Statistical Inference",
      shortDef: "An iterative likelihood-based estimator of between-study variance (τ²) that accounts for the loss of degrees of freedom from estimating the mean effect.",
      context: "Recommended by Cochrane and modern biostatistical consensus as less prone to bias than method-of-moments estimators like DerSimonian–Laird, particularly when trial sizes and variance vary.",
      jumpTab: "primary"
    },
    knappHartung: {
      term: "Knapp–Hartung Adjustment",
      category: "Statistical Inference",
      shortDef: "An adjustment to standard errors and critical values based on the Student's t-distribution with k−1 degrees of freedom.",
      context: "Prevents false-positive inflation (type I error) when pooling a modest number of studies. For k = 11, critical t(10) is 2.228 rather than standard normal z of 1.96, yielding wider, honest, publication-defensible confidence intervals.",
      jumpTab: "primary"
    },
    predictionInterval: {
      term: "95% Prediction Interval",
      category: "Heterogeneity & Prediction",
      shortDef: "The estimated range of true intervention effects that could plausibly occur in an individual future study or comparable clinical setting.",
      context: "A confidence interval describes uncertainty around the pooled average effect. A prediction interval addresses how much the underlying true effect varies between clinical settings. For 24h opioid sparing, the prediction interval [−18.33, +8.26] crosses zero, showing that while average effect is favorable, true sparing varies substantially by surgical invasiveness.",
      jumpTab: "primary"
    },
    iSquared: {
      term: "I² Heterogeneity Statistic",
      category: "Heterogeneity & Prediction",
      shortDef: "The percentage of total variability in effect estimates across studies that is due to genuine heterogeneity rather than chance sampling error.",
      context: "In this review, I² = 99.7% reflects substantial differences in surgical case-mix (minor breast surgery requiring 5 mg MME vs open sternotomy requiring 114 mg MME). High I² must be interpreted alongside τ², prediction intervals, and clinical moderator analyses.",
      jumpTab: "primary"
    },
    tauSquared: {
      term: "τ² (Between-Study Variance)",
      category: "Heterogeneity & Prediction",
      shortDef: "The estimated variance of true effect sizes across the universe of comparable studies, expressed in squared units of the outcome scale.",
      context: "Unlike I² (which is a dimensionless percentage sensitive to within-study sample size), τ² directly quantifies absolute dispersion on the mg IV MME scale and determines the prediction interval width.",
      jumpTab: "primary"
    },
    cochranQ: {
      term: "Cochran's Q Test",
      category: "Heterogeneity & Prediction",
      shortDef: "A chi-square test evaluating whether the observed variance across study effect sizes exceeds what would be expected from sampling error alone.",
      context: "A low p-value (p < 0.10) indicates excess variation. However, Q has low statistical power when k is small and excessive sensitivity when study sizes are very large.",
      jumpTab: "primary"
    },
    hedgesG: {
      term: "Hedges' g (Standardized Mean Difference)",
      category: "Effect Measures",
      shortDef: "The difference between group means divided by the pooled standard deviation, adjusted with a small-sample correction factor.",
      context: "Used when trials measure clinical constructs using different scales. In our primary pool, Hedges' g = −0.99 represents a large standardized reduction. However, natural units (mg IV MME) remain more directly clinically interpretable.",
      jumpTab: "primary"
    },
    riskRatio: {
      term: "Risk Ratio (RR)",
      category: "Effect Measures",
      shortDef: "The probability of an event in the intervention group divided by the probability of the event in the control group.",
      context: "Used for binary postoperative complications such as Postoperative Nausea and Vomiting (PONV). An RR of 0.66 indicates a 34% relative risk reduction. Absolute benefit depends heavily on baseline control incidence.",
      jumpTab: "secondary"
    },
    clinicalThreshold: {
      term: "Clinical Importance Threshold (MCID)",
      category: "Clinical Relevance",
      shortDef: "A prespecified effect magnitude considered large enough to matter to patients and clinicians, independent of statistical significance.",
      context: "Distinguishes statistically detectable effects from clinically meaningful differences. In this review, the primary prespecified threshold is 10 mg IV MME. Secondary sensitivity thresholds include 8 mg, 30% relative reduction, and an exploratory 5 mg threshold.",
      jumpTab: "mcid"
    },
    sensitivityAnalysis: {
      term: "Sensitivity Analysis",
      category: "Methodology",
      shortDef: "A method of testing whether findings remain consistent when analyzing different subsets, alternative assumptions, or statistical estimators.",
      context: "Used to test robustness against risk of bias (low RoB only), comparator credibility (sham only), and estimator choice (REML vs DerSimonian–Laird vs IVhet).",
      jumpTab: "primary"
    },
    rob2: {
      term: "RoB 2 (Cochrane Risk of Bias 2)",
      category: "Certainty & Bias",
      shortDef: "The Cochrane tool for assessing risk of bias in randomized trials across five specific methodological domains.",
      context: "RoB 2 evaluates potential bias affecting a specific trial result (e.g. 24h opioid sparing). It is NOT an overall numerical study quality score.",
      jumpTab: "rob2"
    },
    grade: {
      term: "GRADE Evidence Certainty",
      category: "Certainty & Bias",
      shortDef: "A transparent framework rating confidence in the synthesized body of evidence for a specific outcome across five downgrade domains.",
      context: "GRADE rates the body of synthesized evidence, not individual trials. Downgrading occurs for Risk of Bias, Inconsistency (heterogeneity), Indirectness, Imprecision (wide CIs), and Publication Bias.",
      jumpTab: "evidence"
    },
    betaCoefficient: {
      term: "β (Meta-Regression Coefficient)",
      category: "Meta-Regression",
      shortDef: "The estimated change in study-level treatment effect associated with a one-unit increase in the moderator variable.",
      context: "For opioid consumption where negative MD represents greater opioid sparing, a negative slope (e.g. β = −0.170 for baseline demand) indicates that trials with higher control opioid requirements achieved greater absolute opioid reduction.",
      jumpTab: "metareg"
    },
    metaRegR2: {
      term: "Meta-Regression R² (Variance Explained)",
      category: "Meta-Regression",
      shortDef: "The proportion of between-study variance (τ²) accounted for by the moderator or multivariable model.",
      context: "Meta-regression R² reflects study-level heterogeneity, NOT the percentage of individual patient variability explained by the treatment. It should be interpreted cautiously when k is small.",
      jumpTab: "metareg"
    },
    ecologicalFallacy: {
      term: "Ecological Fallacy (Simpson's Paradox)",
      category: "Meta-Regression",
      shortDef: "A logical fallacy where cross-study associations observed between study-level averages are incorrectly inferred to hold for individual patients.",
      context: "Cochrane Handbook §10.11.2 explicitly cautions that study-level demographic averages (e.g. cohort % female or mean age) cannot establish whether individual women vs men or older vs younger patients experience different treatment effects. Individual Participant Data (IPD) is mandatory.",
      jumpTab: "metareg"
    },
    modality: {
      term: "Intervention Modality (TEAS vs EA)",
      category: "Intervention Parameters",
      shortDef: "The technical delivery method: non-invasive transcutaneous electrical acupoint stimulation (TEAS) using surface pads vs invasive electroacupuncture (EA) using filiform needles.",
      context: "In this review, 49 trials examined TEAS (high clinical ward feasibility) and 14 trials evaluated EA (invasive needle stimulation, predominantly intraoperative).",
      jumpTab: "explorer"
    },
    comparator: {
      term: "Comparator (Sham vs Usual Care)",
      category: "Methodology",
      shortDef: "Control design: double-blind sham stimulation (inactive device or non-acupoints) vs open-label usual care (standard analgesia alone).",
      context: "Sham controls isolate specific neuromodulation from touch/placebo artifacts. The primary analysis synthesizes only sham-controlled trials to guarantee blinding integrity.",
      jumpTab: "explorer"
    },
    surgicalCategory: {
      term: "Surgical Specialty & Case-Mix",
      category: "Clinical Context",
      shortDef: "The anatomical surgical discipline (e.g. Thoracic, Abdominal, Gynecologic, Orthopedic) determining baseline surgical trauma and baseline opioid requirements.",
      context: "Procedures with high tissue injury (thoracotomy, laparotomy) exhibit higher baseline opioid consumption (30–114 mg MME), where TEAS/EA produces the greatest absolute sparing.",
      jumpTab: "explorer"
    },
    acupoints: {
      term: "Acupoints & STRICTA Prescription",
      category: "Intervention Parameters",
      shortDef: "The specific somatic acupoints stimulated in accordance with Traditional Chinese Medicine (TCM) and neuroanatomical segmental innervation.",
      context: "Almost all trials administer bundled multi-point formulas combining upper-limb segmental points (LI4, PC6) and lower-limb visceral points (ST36, SP6). Collinearity prevents isolating single acupoints in meta-regression.",
      jumpTab: "explorer"
    },
    frequency: {
      term: "Stimulation Frequency (Hz)",
      category: "Intervention Parameters",
      shortDef: "The electrical pulse delivery frequency: low (2 Hz), high (100 Hz), or alternating dense-disperse (2/100 Hz).",
      context: "2 Hz stimulates mu- and delta-opioid endorphins/enkephalins; 100 Hz releases dynorphins at kappa-opioid receptors. Dense-disperse (2/100 Hz) engages both endogenous mechanisms.",
      jumpTab: "explorer"
    },
    stimulationTiming: {
      term: "Stimulation Timing & Phase",
      category: "Intervention Parameters",
      shortDef: "The perioperative phase of delivery: preoperative (preemptive), intraoperative, postoperative, or multi-phase treatment.",
      context: "Preoperative administration blocks central sensitization before surgical incision; intraoperative application reduces anesthetic/opioid consumption; postoperative treatment extends analgesia into ward recovery.",
      jumpTab: "explorer"
    },
    gradeCertainty: {
      term: "GRADE Certainty Rating",
      category: "Certainty & Bias",
      shortDef: "The GRADE assessment of confidence in the synthesized body of evidence: High, Moderate, Low, or Very Low.",
      context: "High certainty reflects high confidence that true effect is close to estimate; Moderate indicates true effect is likely close; Low means true effect may differ substantially; Very Low indicates marked uncertainty.",
      jumpTab: "evidence"
    },
    gradeRiskOfBias: {
      term: "GRADE Downgrade: Risk of Bias",
      category: "Certainty & Bias",
      shortDef: "Downgrading by 1 or 2 levels when methodological limitations in contributing trials (e.g. lack of blinding) may distort results.",
      context: "Assessed using Cochrane RoB 2. Downgraded in this review for secondary endpoints where open-label usual care designs introduced performance or detection bias.",
      jumpTab: "evidence"
    },
    gradeInconsistency: {
      term: "GRADE Downgrade: Inconsistency",
      category: "Certainty & Bias",
      shortDef: "Downgrading when substantial, unexplained heterogeneity exists between trial results (high I², divergent point estimates).",
      context: "For 24h opioid sparing, high heterogeneity (I² > 80%) is present, but meta-regression confirms this is largely explained by baseline surgical demand rather than contradictory effect directions.",
      jumpTab: "evidence"
    },
    gradeImprecision: {
      term: "GRADE Downgrade: Imprecision",
      category: "Certainty & Bias",
      shortDef: "Downgrading when confidence intervals are wide, include both benefit and harm, or cross important clinical decision thresholds.",
      context: "Downgraded when total analyzed surgical sample size is below optimal information size or when the 95% CI spans across zero or across the 10 mg clinical threshold.",
      jumpTab: "evidence"
    }
  },
  sv: {
    meanDifference: {
      term: "Medelskillnad (MD)",
      category: "Effektmått",
      shortDef: "Den absoluta skillnaden mellan medelvärdet i interventionsgruppen och kontrollgruppen, uttryckt i utfallsmåttets ursprungliga enhet.",
      context: "För postoperativ opioidkonsumtion anger negativa värden lägre opioidförbrukning i TEAS/EA-gruppen. Exempelvis betyder en MD på −5,04 mg IV MME att patienter som fick neuromodulering i genomsnitt använde 5,04 mg mindre intravenöst morfin än kontrollpatienter.",
      jumpTab: "primary"
    },
    ivMme: {
      term: "Intravenösa morfinmilligramekvivalenter (IV MME)",
      category: "Effektmått",
      shortDef: "En standardiserad ekvianalgetisk omräkningsskala som konverterar olika opioida läkemedel och doser till en gemensam intravenös morfinekvivalent.",
      context: "Eftersom kirurgiska studier använder olika opioider (t.ex. fentanyl, sufentanil, hydromorfon, piritramid, tramadol) möjliggör omräkning till IV MME matematisk sammanslagning och rättvis jämförelse.",
      jumpTab: "primary"
    },
    confidenceInterval: {
      term: "95 % Konfidensintervall (95 % KI)",
      category: "Statistisk inferens",
      shortDef: "Ett intervall av rimliga värden för den sanna genomsnittliga populationseffekten som är förenliga med observerade data och modellantaganden.",
      context: "Konfidensintervallet beskriver osäkerheten kring den sammanvägda medeleffekten. Om KI korsar noll (för medelskillnader) är data förenliga med att det inte finns någon genomsnittlig skillnad. Det innebär INTE att det är 95 % sannolikhet att det sanna värdet ligger i intervallet.",
      jumpTab: "primary"
    },
    pValue: {
      term: "p-värde",
      category: "Statistisk inferens",
      shortDef: "Sannolikheten att observera resultat minst lika extrema som de faktiska studiedata, givet att nollhypotesen är sann.",
      context: "Ett p-värde mäter oförenlighet med nollhypotesen under modellens antaganden. Ett p-värde mäter INTE effektens storlek eller kliniska betydelse.",
      jumpTab: "primary"
    },
    kStudies: {
      term: "k (Antal ingående studier)",
      category: "Metaanalytiska parametrar",
      shortDef: "Antalet oberoende randomiserade kontrollerade studier som bidrar med data till en specifik metaanalytisk syntes.",
      context: "I denna översikt ingår k = 63 RCT:er totalt, men k för specifika synteser är lägre (t.ex. k = 11 för 24h opioidbesparing) eftersom endast studier med verifierade, icke-imputerade data inkluderas.",
      jumpTab: "primary"
    },
    nParticipants: {
      term: "N (Totalt antal analyserade patienter)",
      category: "Metaanalytiska parametrar",
      shortDef: "Den kumulativa summan av randomiserade kirurgiska patienter i de studiearmar som ingår i den specifika analysen.",
      context: "Över alla 63 inkluderade RCT:er är N = 5 089 patienter. För den primära 24h opioidsyntesen är N = 945 patienter.",
      jumpTab: "explorer"
    },
    randomEffects: {
      term: "Random effects-modell",
      category: "Statistisk inferens",
      shortDef: "En metaanalysmodell som antar att den sanna behandlingseffekten varierar mellan studier enligt en fördelning, snarare än att anta en enda identisk fix effekt.",
      context: "Avgörande vid perioperativ anestesi eftersom kirurgiska ingrepp (torakotomi kontra tyroidektomi), stimuleringsparametrar, smärtintensitet och ERAS-regimer skiljer sig naturligt mellan sjukhus.",
      jumpTab: "primary"
    },
    reml: {
      term: "Restricted Maximum Likelihood (REML)",
      category: "Statistisk inferens",
      shortDef: "En iterativ sannolikhetsbaserad estimator för variansen mellan studier (τ²) som tar hänsyn till förlusten av frihetsgrader vid skattning av medeleffekten.",
      context: "Rekommenderas av Cochrane och modern biostatistisk konsensus eftersom den ger mindre skevhet än momentmetoder som DerSimonian–Laird, särskilt vid varierande studiestorlekar.",
      jumpTab: "primary"
    },
    knappHartung: {
      term: "Knapp–Hartung-justering",
      category: "Statistisk inferens",
      shortDef: "En justering av medelfel och kritiska testvärden baserad på Students t-fördelning med k−1 frihetsgrader.",
      context: "Förhindrar falskt positiva fynd (typ I-fel) vid metaanalys med ett begränsat antal studier. För k = 11 är det kritiska t-värdet 2,228 istället för normalfördelningens 1,96, vilket ger bredare, ärliga och vetenskapligt robusta konfidensintervall.",
      jumpTab: "primary"
    },
    predictionInterval: {
      term: "95 % Prediktionsintervall",
      category: "Heterogenitet och prediktion",
      shortDef: "Det estimerade intervallet för sanna behandlingseffekter som rimligen kan förväntas i en framtida enskild studie eller jämförbar klinisk miljö.",
      context: "Ett konfidensintervall beskriver osäkerheten kring den sammanvägda genomsnittliga effekten. Ett prediktionsintervall beskriver hur mycket den underliggande sanna effekten varierar mellan olika kliniska miljöer. För 24h opioidbesparing korsar prediktionsintervallet [−18,33; +8,26] noll, vilket visar att effekten varierar med ingreppets invasivitet.",
      jumpTab: "primary"
    },
    iSquared: {
      term: "I²-heterogenitetsmått",
      category: "Heterogenitet och prediktion",
      shortDef: "Andelen av den totala variationen i effektestimat mellan studier som beror på verklig heterogenitet snarare än slumpmässig samplingsvariation.",
      context: "I denna översikt återspeglar I² = 99,7 % stora skillnader i kirurgiskt ingrepp (bröstkirurgi med 5 mg MME kontra öppen hjärtkirurgi med 114 mg MME). Högt I² måste alltid tolkas tillsammans med τ², prediktionsintervall och kliniska moderatoranalyser.",
      jumpTab: "primary"
    },
    tauSquared: {
      term: "τ² (Varians mellan studier / Tau-kvadrat)",
      category: "Heterogenitet och prediktion",
      shortDef: "Den estimerade variansen av de sanna effektstorlekarna mellan studier, uttryckt i kvadraten av utfallsmåttets enhet.",
      context: "Till skillnad från I² (som är ett dimensionslöst procenttal) kvantifierar τ² den absoluta spridningen på skalan mg IV MME och bestämmer prediktionsintervallets bredd.",
      jumpTab: "primary"
    },
    cochranQ: {
      term: "Cochrans Q-test",
      category: "Heterogenitet och prediktion",
      shortDef: "Ett chi-två-test som utvärderar om den observerade variationen mellan studier är större än vad som kan förklaras av enbart slumpmässig sampling.",
      context: "Ett lågt p-värde (p < 0,10) indikerar överskjutande variation. Q-testet har dock låg statistisk styrka vid få studier och hög känslighet vid mycket stora studier.",
      jumpTab: "primary"
    },
    hedgesG: {
      term: "Hedges' g (Standardiserad medelskillnad)",
      category: "Effektmått",
      shortDef: "Skillnaden mellan gruppmedelvärden dividerad med den poolade standardavvikelsen, justerad med en korrektionsfaktor för små urval.",
      context: "Används när studier mäter samma begrepp med olika mätskalor. I vår primära kohort är Hedges' g = −0,99, vilket representerar en stor standardiserad effekt. Naturliga kliniska enheter (mg IV MME) är dock mer direkt begripliga i klinisk praxis.",
      jumpTab: "primary"
    },
    riskRatio: {
      term: "Riskkvot (RR)",
      category: "Effektmått",
      shortDef: "Sannolikheten för en händelse i interventionsgruppen dividerad med sannolikheten i kontrollgruppen.",
      context: "Används för dikotoma postoperativa komplikationer som postoperativt illamående och kräkning (PONV). En RR på 0,66 innebär en 34 % relativ riskreduktion. Den absoluta nyttan beror starkt på kontrollgruppens basala incidens.",
      jumpTab: "secondary"
    },
    clinicalThreshold: {
      term: "Tröskel för klinisk betydelse (MCID)",
      category: "Klinisk relevans",
      shortDef: "En förspecificerad effektstorlek som bedöms vara tillräckligt stor för att ha klinisk betydelse för patienter och läkare, oberoende av statistisk signifikans.",
      context: "Skiljer statistiskt påvisbara effekter från kliniskt meningsfulla skillnader. I denna översikt är den primära förspecificerade tröskeln 10 mg IV MME. Sekundära känslighetströsklar inkluderar 8 mg, 30 % relativ minskning och en explorativ 5 mg-tröskel.",
      jumpTab: "mcid"
    },
    sensitivityAnalysis: {
      term: "Sensitivitetsanalys",
      category: "Metodologi",
      shortDef: "En metod för att testa om resultaten kvarstår när analysen upprepas under alternativa antaganden, delmängder eller statistiska modeller.",
      context: "Används för att pröva robusthet mot risk för bias (endast låg RoB), kontrollgruppens trovärdighet (endast sham) och val av statistisk estimator (REML kontra DerSimonian–Laird).",
      jumpTab: "primary"
    },
    rob2: {
      term: "RoB 2 (Cochrane Risk of Bias 2)",
      category: "Tillförlitlighet och bias",
      shortDef: "Cochranes granskningsverktyg för att utvärdera risk för bias i randomiserade studier över fem specifika metodologiska domäner.",
      context: "RoB 2 utvärderar potentiell bias som påverkar ett specifikt studieresultat (t.ex. 24h opioidbesparing). Det är INTE en allmän numerisk kvalitetsbedömning av hela artikeln.",
      jumpTab: "rob2"
    },
    grade: {
      term: "GRADE – evidensens tillförlitlighet",
      category: "Tillförlitlighet och bias",
      shortDef: "Ett internationellt system för att bedöma tillförlitligheten till det samlade evidensunderlaget för ett specifikt utfall över fem nedgraderingsdomäner.",
      context: "GRADE värderar det samlade evidensunderlaget, inte enskilda studier. Nedgradering sker för Risk för bias, Inkonsekvens (heterogenitet), Indirekthet, Imprecision (breda KI) och Publikationsbias.",
      jumpTab: "evidence"
    },
    betaCoefficient: {
      term: "β (Metaregressionskoefficient)",
      category: "Metaregression",
      shortDef: "Den beräknade förändringen i behandlingseffekt på studienivå för varje enhets ökning av moderatorvariabeln.",
      context: "För opioidkonsumtion där negativ MD innebär större opioidbesparing betyder en negativ lutning (t.ex. β = −0,170 för basalt opioidbehov) att studier med högre opioidbehov i kontrollgruppen uppnådde större absolut opioidminskning.",
      jumpTab: "metareg"
    },
    metaRegR2: {
      term: "Metaregressions-R² (Förklarad varians)",
      category: "Metaregression",
      shortDef: "Andelen av variansen mellan studier (τ²) som förklaras av moderatorvariabeln eller modellen.",
      context: "Metaregressions-R² återspeglar heterogenitet på studienivå, INTE andelen av individuella patienters utfall som förklaras av behandlingen. Det bör tolkas med försiktighet vid få studier.",
      jumpTab: "metareg"
    },
    ecologicalFallacy: {
      term: "Ekologiskt felslut (Simpsons paradox)",
      category: "Metaregression",
      shortDef: "Ett logiskt felslut där samband som observeras mellan genomsnitt på studienivå felaktigt antas gälla för individuella patienter inom studierna.",
      context: "Cochrane Handbook §10.11.2 varnar uttryckligen för att demografiska genomsnitt på studienivå (t.ex. andel kvinnor eller medelålder) inte kan avgöra om enskilda kvinnor kontra män eller äldre kontra yngre patienter har olika behandlingseffekt. Metaanalys på individuella patientdata (IPD) är nödvändig.",
      jumpTab: "metareg"
    },
    modality: {
      term: "Interventionsmodalitet (TEAS vs EA)",
      category: "Interventionsparametrar",
      shortDef: "Den tekniska metoden: icke-invasiv transkutan elektrisk akupunkturstimulering (TEAS) med hudplattor kontra invasiv elektroakupunktur (EA) med filiforma nålar.",
      context: "I denna översikt utvärderade 49 studier TEAS (hög klinisk användbarhet på vårdavdelning) och 14 studier EA (invasiv nålstimulering, främst under narkos).",
      jumpTab: "explorer"
    },
    comparator: {
      term: "Kontrollgrupp (Sham vs Sedvanlig vård)",
      category: "Metodologi",
      shortDef: "Kontrolldesign: dubbelblind sham-stimulering (inaktiv apparat eller icke-akupunkter) kontra öppen sedvanlig vård (standardanalgesi).",
      context: "Sham-kontroll isolerar specifik neuromodulering från placebo- och beröringseffekter. Den primära analysen syntetiserar uteslutande sham-kontrollerade studier för att säkerställa blinding.",
      jumpTab: "explorer"
    },
    surgicalCategory: {
      term: "Kirurgisk specialitet och ingreppstyp",
      category: "Klinisk kontext",
      shortDef: "Det kirurgiska ämnesområdet (t.ex. torax, buk, gynekologi, ortopedi) som avgör graden av vävnadsskada och förväntat basalt opioidbehov.",
      context: "Ingrepp med omfattande vävnadstrauma (torakotomi, laparotomi) uppvisar högre basalt opioidbehov (30–114 mg MME), där TEAS/EA ger störst absolut opioidbesparing.",
      jumpTab: "explorer"
    },
    acupoints: {
      term: "Akupunkter och STRICTA-recept",
      category: "Interventionsparametrar",
      shortDef: "De specifika akupunkter som stimuleras enligt traditionell kinesisk medicin (TCM) och neuroanatomisk segmentell innervation.",
      context: "Nästan alla studier använder punktkombinationer som förenar segmentella armpunkter (LI4, PC6) och viscerala benpunkter (ST36, SP6). Statistisk kollinearitet hindrar analys av enskilda punkter i metaregression.",
      jumpTab: "explorer"
    },
    frequency: {
      term: "Stimuleringsfrekvens (Hz)",
      category: "Interventionsparametrar",
      shortDef: "Frekvensen för de elektriska strömpulserna: lågfrekvent (2 Hz), högfrekvent (100 Hz), eller alternerande tät-gles (2/100 Hz).",
      context: "2 Hz stimulerar frisättning av endorfiner och enkefaliner (mu/delta-receptorer); 100 Hz frisätter dynorfin (kappa-receptorer). Tät-gles (2/100 Hz) aktiverar båda systemen.",
      jumpTab: "explorer"
    },
    stimulationTiming: {
      term: "Stimuleringstidpunkt och fas",
      category: "Interventionsparametrar",
      shortDef: "Det perioperativa tidsfönstret: preoperativt (preemptivt), intraoperativt, postoperativt eller flerfasbehandling.",
      context: "Preoperativ stimulering motverkar central sensitisering före incision; intraoperativ behandling minskar narkos- och opioidbehov; postoperativ behandling förlänger analgesin.",
      jumpTab: "explorer"
    },
    gradeCertainty: {
      term: "GRADE – evidensens tillförlitlighetsgrad",
      category: "Tillförlitlighet och bias",
      shortDef: "GRADE-systemets övergripande bedömning av tillförlitligheten till det sammanvägda effektestimatet: Hög, Måttlig, Låg eller Mycket låg.",
      context: "Hög tillförlitlighet innebär mycket stor tilltro till att den sanna effekten ligger nära estimatet; Måttlig innebär att den sanna effekten troligen är nära; Låg innebär att den kan skilja sig väsentligt; Mycket låg innebär stor osäkerhet.",
      jumpTab: "evidence"
    },
    gradeRiskOfBias: {
      term: "GRADE-nedgradering: Risk för bias",
      category: "Tillförlitlighet och bias",
      shortDef: "Nedgradering med 1–2 nivåer när metodologiska brister i de ingående studierna (t.ex. bristande blindning) kan snedvrida resultaten.",
      context: "Bedöms med Cochrane RoB 2. Nedgradering skedde i denna översikt för sekundära utfall där öppna studier med sedvanlig vård gav risk för genomförande- eller bedömarbias.",
      jumpTab: "evidence"
    },
    gradeInconsistency: {
      term: "GRADE-nedgradering: Inkonsekvens",
      category: "Tillförlitlighet och bias",
      shortDef: "Nedgradering när betydande oförklarad heterogenitet föreligger mellan studieresultaten (högt I², spridda effektestimat).",
      context: "För 24h opioidbesparing föreligger hög heterogenitet (I² > 80 %), men metaregression visar att denna till stor del förklaras av kontrollgruppens basala smärtbehov snarare än motstridiga effektriktningar.",
      jumpTab: "evidence"
    },
    gradeImprecision: {
      term: "GRADE-nedgradering: Imprecision",
      category: "Tillförlitlighet och bias",
      shortDef: "Nedgradering när konfidensintervallen är breda, omfattar både klinisk nytta och försumbar effekt, eller korsar beslutströsklar.",
      context: "Nedgradering sker när det totala antalet patienter understiger optimal informationsstorlek eller då 95 % KI spänner över noll eller över den kliniska tröskeln 10 mg IV MME.",
      jumpTab: "evidence"
    }
  }
};

window.TRANSLATIONS = TRANSLATIONS;
window.STAT_GLOSSARY = STAT_GLOSSARY;

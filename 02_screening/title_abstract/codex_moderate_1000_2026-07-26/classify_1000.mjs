const includesAny = (text, patterns) => patterns.some((pattern) => text.includes(pattern));

const matchAny = (text, patterns) => patterns.some((pattern) => pattern.test(text));

const sentenceWith = (text, patterns) => {
  const sentences = text
    .split(/(?<=[.!?])\s+/)
    .map((sentence) => sentence.trim())
    .filter(Boolean);
  return (
    sentences.find((sentence) => patterns.some((pattern) => pattern.test(sentence))) ??
    sentences[0] ??
    ""
  ).slice(0, 600);
};

const defaultFields = {
  background_care_balanced: "unclear",
  ERAS_balance: "not_applicable",
  intervention_effect_separable: "unclear",
  timing_eligible: "unclear",
  timing_description: "",
  clinical_outcome_present: "unclear",
  surrogate_only: "no",
  possible_companion_report: "no",
  notes: ""
};

function languageFields(title, abstract) {
  const text = `${title} ${abstract}`;
  const translated = /^\s*\[/.test(title) || /\[(?:article in|translated from)/i.test(text);
  const nonEnglish = matchAny(title.toLowerCase(), [
    /\bensayo\b/,
    /\bestudio\b/,
    /\bwirksamkeit\b/,
    /\bwirkung\b/,
    /\btraitement\b/,
    /\bétude\b/,
    /\bklinische\b/,
    /\bzufallsverteilung\b/,
    /\bpostoperatorio\b/,
    /\bdolor\b/,
    /\bchirurgie\b/
  ]);
  return {
    publication_language: translated || nonEnglish ? "uncertain" : "English",
    translation_required: translated || nonEnglish ? "yes" : "no"
  };
}

function publicationType(title, source, abstract) {
  const t = title.toLowerCase();
  const all = `${title} ${source} ${abstract}`.toLowerCase();
  const registrySource = matchAny(source.toLowerCase(), [
    /\bclinicaltrials\.gov\b/,
    /\btrial registr/,
    /\bwho international clinical trials registry\b/,
    /\bchinese clinical trial registry\b/,
    /\binternational clinical trials registry platform\b/
  ]);
  const identifierAsTitle =
    /^(?:nct|chictr|isrctn|actrn|ctri|jprn|drks|irct|umin)[-a-z0-9]*\d{4,}\b/i.test(
      title.trim()
    );
  const registration =
    registrySource ||
    identifierAsTitle ||
    /\btrial registration record\b|\bregistry record\b/.test(t);
  if (registration) return "trial_registration";
  if (/^correction\b|\bcorrigendum\b|\berratum\b/.test(t)) return "correction";
  if (/\bprotocol amendment\b/.test(t)) return "protocol";
  if (
    matchAny(t, [
      /\bstudy protocol\b/,
      /\btrial protocol\b/,
      /\bprotocol for\b/,
      /\bprotocol of\b/,
      /:\s*(?:a |an )?(?:randomi[sz]ed )?(?:controlled )?trial protocol\b/,
      /\bdesign and rationale\b/
    ])
  ) {
    return source.toLowerCase().includes("conference") ? "conference_protocol" : "protocol";
  }
  if (/\bsystematic review\b/.test(t)) return "systematic_review";
  if (/\bmeta-analysis\b|\bmeta analysis\b/.test(t)) return "meta_analysis";
  if (/\bscoping review\b/.test(t)) return "scoping_review";
  if (/\bbibliometric\b/.test(t)) return "bibliometric_review";
  if (/\breview\b/.test(t) && !/\btrial\b|\brandom/.test(t)) return "narrative_review";
  if (/\ban update of (?:clinical|experimental|published) .*studies\b/.test(t)) {
    return "narrative_review";
  }
  if (/\beditorial\b/.test(t)) return "editorial";
  if (/\bcommentary\b/.test(t)) return "commentary";
  if (/\bcase report\b/.test(all)) return "case_report";
  if (/\bcase series\b/.test(all)) return "case_series";
  if (source.toLowerCase().includes("conference") || /\bconference abstract\b/.test(all)) {
    return "conference_abstract";
  }
  if (/\bsecondary analysis\b|\bpost hoc\b|\bfollow-up\b|\bsubgroup analysis\b/.test(all)) {
    return "secondary_report";
  }
  return "primary_results";
}

function identifyIntervention(text) {
  const lower = text.toLowerCase();
  const ea = matchAny(lower, [
    /\belectro[\s-]?acupunctur/,
    /\belectrical(?:ly)? stimulated acupuncture\b/,
    /\belectric acupuncture\b/
  ]);
  const teas = matchAny(lower, [
    /\bteas\b/,
    /\btaes\b/,
    /\btranscutaneous (?:electrical|electric) acupoint stimulation\b/,
    /\btranscutaneous acupoint electrical stimulation\b/,
    /\btranscutaneous acupoint electric stimulation\b/,
    /\belectrical acupoint stimulation\b/,
    /\bacupoint electrical stimulation\b/,
    /\belectric acupoint stimulation\b/,
    /\belectroacupoint stimulation\b/,
    /\belectro[- ]acupoint stimulation\b/,
    /\bacupuncture-like transcutaneous electrical nerve stimulation\b/,
    /\bacu-?tens\b/,
    /\blow-frequency electrical acupoint stimulation\b/
  ]);
  const ordinaryTens =
    /\btranscutaneous electrical nerve stimulation\b|\btens\b/.test(lower) && !teas;
  const wrong = matchAny(lower, [
    /\bauricular (?:acupuncture|electroacupuncture)\b/,
    /\btransauricular\b/,
    /\bbattlefield acupuncture\b/,
    /\bpress[- ]?tack\b/,
    /\bpress needle\b/,
    /\bintradermal acupuncture\b/,
    /\bwrist[-– ]ankle acupuncture\b/,
    /\bbuccal acupuncture\b/,
    /\blaser acupuncture\b/,
    /\bdry needling\b/,
    /\bacupoint injection\b/,
    /\binjection acupuncture\b/,
    /\bfloating needle\b/,
    /\bmoxibustion\b/,
    /\bcupping\b/,
    /\bacupressure\b/
  ]);
  return { ea, teas, ordinaryTens, wrong };
}

function surgeryStatus(text) {
  const lower = text.toLowerCase();
  const surgery = matchAny(lower, [
    /\bsurg(?:ery|ical|eries)\b/,
    /\boperati(?:on|ve)\b/,
    /\bperioperat/,
    /\bpostoperat/,
    /\bpreoperat/,
    /\bintraoperat/,
    /\bresection\b/,
    /\bectomy\b/,
    /\botomy\b/,
    /\bplasty\b/,
    /\barthroplast/,
    /\bcraniotom/,
    /\blaparoscop/,
    /\bthoracoscop/,
    /\bmastectom/,
    /\bgastrectom/,
    /\bcolectom/,
    /\bthyroidectom/,
    /\bcesarean\b|\bcaesarean\b/,
    /\bcardiac bypass\b|\bcoronary artery bypass\b/,
    /\bspinal fusion\b/,
    /\bhip replacement\b|\bknee replacement\b/,
    /\binguinal hernia\b/,
    /\bcontrolled hypotension\b/
  ]);
  const explicitNonSurgical = matchAny(lower, [
    /\bhealthy volunteers?\b/,
    /\bchronic (?:low back|neck|shoulder|knee|neuropathic|musculoskeletal) pain\b/,
    /\bmigraine\b/,
    /\bknee osteoarthritis\b/,
    /\bcarpal tunnel syndrome\b/,
    /\bextracorporeal shock wave lithotripsy\b/,
    /\bstroke rehabilitation\b/,
    /\bsevere acute pancreatitis\b/,
    /\bparalytic ileus\b(?!.*postoperat)/,
    /\blabor induction\b|\binduction of labo[u]?r\b/,
    /\bdental extraction\b/,
    /\bcolonoscopy\b|\bgastroscopy\b|\bbronchoscopy\b/
  ]);
  return { surgery, explicitNonSurgical };
}

function anaesthesiaStatus(text) {
  const lower = text.toLowerCase();
  if (
    matchAny(lower, [
      /\bgeneral an(?:a)?esthesia\b/,
      /\bendotracheal intubat/,
      /\btracheal intubat/,
      /\bmechanical ventilation\b/,
      /\bsevoflurane\b|\bdesflurane\b|\bremifentanil\b|\bsufentanil\b/,
      /\bbispectral index\b|\bbis-guided\b/
    ])
  ) {
    return "yes";
  }

  if (
    matchAny(lower, [
      /\bunder spinal an(?:a)?esthesia\b/,
      /\bspinal an(?:a)?esthesia alone\b/,
      /\bepidural an(?:a)?esthesia\b/,
      /\bcervical plexus block\b/,
      /\bbrachial plexus block\b/,
      /\blocal an(?:a)?esthesia\b/,
      /\bsedation only\b/,
      /\bregional an(?:a)?esthesia\b/
    ]) &&
    !/\bgeneral an(?:a)?esthesia\b/.test(lower)
  ) {
    return "no";
  }
  return "unclear";
}

function timingStatus(text) {
  const lower = text.toLowerCase();
  const treatmentText = text
    .split(/(?<=[.!?])\s+/)
    .filter((sentence) =>
      /(?:electroacupunct|\bteas\b|acupoint stimulation|electrical stimulation|treatment|intervention|session|applied|received acupuncture)/i.test(
        sentence
      )
    )
    .join(" ")
    .toLowerCase();
  const timingText = treatmentText || lower;
  if (
    matchAny(timingText, [
      /\bpreoperat/,
      /\bbefore (?:the )?(?:operation|surgery|induction)\b/,
      /\bprior to (?:the )?(?:operation|surgery|anesthetic|anaesthetic) induction\b/,
      /\bintraoperat/,
      /\bduring (?:the )?(?:operation|surgery)\b/,
      /\bimmediately after (?:the )?(?:operation|surgery)\b/,
      /\b(?:within|at) (?:[0-9]|1[0-9]|2[0-4])\s*(?:h|hr|hrs|hour|hours) after\b/,
      /\b(?:2|4|6|8|12|18|22|24)\s*h after\b/,
      /\bon the day of (?:operation|surgery)\b/
    ])
  ) {
    return { status: "yes", description: sentenceWith(text, [/preoperat/i, /intraoperat/i, /before .*surg/i, /within .*hour/i, /\b24 h/i]) };
  }
  if (
    matchAny(timingText, [
      /\b(?:weeks?|months?) after (?:operation|surgery)\b/,
      /\bpostoperative rehabilitation\b/,
      /\bafter discharge\b/,
      /\bchronic postoperative\b/,
      /\bfrom (?:postoperative )?day [2-9]\b/,
      /\b(?:began|started|commenced|initiated|applied) (?:on|from)? ?(?:postoperative )?day [2-9]\b/
    ])
  ) {
    return { status: "no", description: sentenceWith(text, [/week/i, /month/i, /rehabilitation/i, /day [2-9]/i]) };
  }
  if (
    matchAny(timingText, [
      /\bpostoperative day 1\b/,
      /\bfirst postoperative day\b/,
      /\bday after (?:operation|surgery)\b/,
      /\b1 day after (?:operation|surgery)\b/,
      /\bfrom 1 day after\b/
    ])
  ) {
    return { status: "unclear", description: sentenceWith(text, [/day 1/i, /1 day after/i, /day after/i]) };
  }
  if (/\bpostoperat/.test(timingText) || /\bafter (?:operation|surgery)\b/.test(timingText)) {
    return { status: "unclear", description: sentenceWith(text, [/postoperat/i, /after (?:operation|surgery)/i]) };
  }
  return { status: "unclear", description: "" };
}

function outcomeStatus(text) {
  const lower = text.toLowerCase();
  const clinical = matchAny(lower, [
    /\bopioid\b|\bmorphine\b|\bsufentanil\b|\bfentanyl\b|\bremifentanil\b/,
    /\bpain\b|\banalgesi/,
    /\bnausea\b|\bvomiting\b|\bponv\b/,
    /\bquality of recovery\b|\bqor[- ]?\d*/,
    /\bsleep\b/,
    /\bdelirium\b|\bcognitive\b/,
    /\bfirst flatus\b|\bdefecation\b|\bbowel\b|\bgastrointestinal function\b|\bintestinal motility\b/,
    /\bmobili[sz]ation\b|\bfunctional recovery\b|\brange of motion\b/,
    /\blength of stay\b|\bhospital stay\b/,
    /\bpatient satisfaction\b/,
    /\bcomplication\b|\badverse event\b|\bfever\b|\binfection\b/,
    /\brescue analges/
  ]);
  const surrogate = matchAny(lower, [
    /\bcytokine\b|\binterleukin\b|\btumor necrosis factor\b|\bc-reactive protein\b/,
    /\bcortisol\b|\bbiomarker\b|\bhaemodynamic\b|\bhemodynamic\b/,
    /\bblood flow\b|\bheart rate variability\b|\bneuroimaging\b|\bbispectral index\b/
  ]);
  return { clinical, surrogateOnly: surrogate && !clinical };
}

function comparatorStatus(text) {
  const lower = text.toLowerCase();
  const eligibleControl = matchAny(lower, [
    /\bsham\b/,
    /\bplacebo\b/,
    /\bcontrol group\b/,
    /\busual care\b|\broutine care\b|\bstandard care\b/,
    /\bno stimulation\b|\bwithout stimulation\b/,
    /\bblank control\b/
  ]);
  const activeOnly =
    matchAny(lower, [
      /\bversus (?:a )?drug\b/,
      /\bcompared with (?:manual )?acupuncture\b/,
      /\bcompared with (?:conventional )?tens\b/,
      /\bversus (?:conventional )?tens\b/,
      /\bcompared with rehabilitation\b/,
      /\bversus rehabilitation\b/,
      /\bcompared with (?:regional|nerve) block\b/
    ]) && !eligibleControl;
  const explicitActiveOnly = matchAny(lower, [
    /\bcomparative induction\b.*\belectroacupuncture\b.*\bremifentanil\b/,
    /\belectroacupuncture\b.*\b(?:versus|vs\.?|and)\b.*\bremifentanil\b/,
    /\bacupotomy\b.*\b(?:versus|vs\.?)\b.*\belectro-?acupuncture\b/
  ]);
  return { eligibleControl, activeOnly: activeOnly || explicitActiveOnly };
}

function randomizationStatus(text) {
  const lower = text.toLowerCase();
  if (
    matchAny(lower, [
      /\brandomi[sz]ed\b/,
      /\brandomly (?:assigned|allocated|divided)\b/,
      /\brandomly (?:and \w+ )?divided\b/,
      /\brandom number\b/
    ])
  ) {
    return "yes";
  }
  if (
    matchAny(lower, [
      /\bretrospective\b/,
      /\bobservational\b/,
      /\bnon[- ]?random/,
      /\bsingle[- ]arm\b/,
      /\buncontrolled\b/,
      /\bcase[- ]control\b/,
      /\baccording to (?:patient|clinician) (?:choice|preference)\b/,
      /\ballocation by (?:date|admission|hospital number)\b/
    ])
  ) {
    return "no";
  }
  if (
    matchAny(lower, [
      /\bdivided into (?:an? )?(?:observation|treatment|intervention).*\bcontrol group\b/,
      /\bassigned (?:into|to) .* groups?\b/,
      /\bprospective\b.*\bcontrolled trial\b/
    ])
  ) {
    return "unclear";
  }
  return "unclear";
}

function firstAuthor(authorLine) {
  const first = (authorLine || "").split(";")[0].trim();
  return first ? first.split(",")[0].trim() : "uncertain";
}

function baseRecord(live) {
  const lang = languageFields(live.title, live.abstract);
  return {
    covidence_number: live.id,
    title: live.title,
    first_author: firstAuthor(live.authorLine),
    publication_year: (live.year.match(/\b(?:19|20)\d{2}\b/) ?? ["uncertain"])[0],
    ...lang,
    abstract_available: live.abstract ? "yes" : "no",
    ...defaultFields
  };
}

function exclude(base, fields) {
  return { ...base, decision: "No", confidence: "high", ...fields };
}

function maybe(base, fields) {
  return { ...base, decision: "Maybe", confidence: "moderate", ...fields };
}

function include(base, fields) {
  return { ...base, decision: "Yes", confidence: "high", ...fields };
}

export function classify(live) {
  const base = baseRecord(live);
  const text = `${live.title}. ${live.abstract || ""}`;
  const lower = text.toLowerCase();
  let type = publicationType(live.title, live.source, live.abstract || "");
  if (
    /^(?:ChiCTR|NCT|ISRCTN|ACTRN|ITMCTR|UMIN|KCT|RBR-|DRKS|IRCT)/i.test(
      live.authorLine || ""
    )
  ) {
    type = "trial_registration";
  }
  const intervention = identifyIntervention(text);
  const surgery = surgeryStatus(text);
  const anaesthesia = anaesthesiaStatus(text);
  const timing = timingStatus(text);
  const outcome = outcomeStatus(text);
  const comparator = comparatorStatus(text);
  const randomized = randomizationStatus(text);
  const actualResults =
    matchAny(lower, [/\bresults?:/, /\bfindings?:/, /\bconclusions?:/]) &&
    !["protocol", "conference_protocol", "trial_registration"].includes(type);
  const interventionLabel =
    intervention.ea && intervention.teas ? "EA and TEAS" : intervention.ea ? "EA" : intervention.teas ? "TEAS" : intervention.ordinaryTens ? "ordinary TENS" : "not eligible/unclear";
  const common = {
    record_type: type,
    actual_results_reported: actualResults ? "yes" : "no",
    general_anaesthesia: anaesthesia,
    randomized,
    intervention: interventionLabel,
    comparator: comparator.eligibleControl ? "sham/usual-care/control" : "unclear or active-only",
    intervention_effect_separable: "unclear",
    timing_eligible: timing.status,
    timing_description: timing.description,
    clinical_outcome_present: outcome.clinical ? "yes" : "unclear",
    surrogate_only: outcome.surrogateOnly ? "yes" : "no",
    possible_companion_report: type === "secondary_report" ? "yes" : "no",
    notes: live.identifiers || ""
  };

  if (["protocol", "conference_protocol", "trial_registration"].includes(type)) {
    return exclude(base, {
      ...common,
      primary_reason_code: "EXCLUDE_PROTOCOL_NO_RESULTS",
      evidence_supporting_decision:
        type === "trial_registration"
          ? "The citation is a trial-registration record and does not report participant results."
          : "The title identifies a protocol/design report without participant results.",
      concise_rationale: "Protocol or registration without results.",
      actual_results_reported: "no",
      randomized: "not_applicable",
      general_anaesthesia: "not_applicable",
      intervention_effect_separable: "not_applicable",
      timing_eligible: "not_applicable",
      clinical_outcome_present: "not_applicable",
      surrogate_only: "not_applicable"
    });
  }

  if (
    [
      "systematic_review",
      "meta_analysis",
      "scoping_review",
      "narrative_review",
      "bibliometric_review",
      "commentary",
      "editorial",
      "correction",
      "letter",
      "case_report",
      "case_series"
    ].includes(type)
  ) {
    return exclude(base, {
      ...common,
      primary_reason_code: "EXCLUDE_PUBLICATION_TYPE",
      evidence_supporting_decision: `The citation is classified as ${type.replaceAll("_", " ")} rather than an eligible randomized results report.`,
      concise_rationale: "Ineligible publication type.",
      randomized: "not_applicable",
      general_anaesthesia: "not_applicable",
      intervention_effect_separable: "not_applicable",
      timing_eligible: "not_applicable",
      clinical_outcome_present: "not_applicable",
      surrogate_only: "not_applicable"
    });
  }

  if (
    matchAny(lower, [
      /\b(?:rats?|mice|mouse|rabbits?|swine|pigs?|dogs?|cats?|murine|rodent|guinea pigs?|sheep)\b/,
      /\banimal model\b/,
      /\bincision pain model\b/,
      /\bsciatic nerve injury\b.*\brats?\b/
    ])
  ) {
    return exclude(base, {
      ...common,
      record_type: "animal_study",
      primary_reason_code: "EXCLUDE_ANIMAL",
      evidence_supporting_decision: sentenceWith(text, [/\brats?\b/i, /\bmice\b/i, /\banimal model\b/i]),
      concise_rationale: "Animal study.",
      actual_results_reported: "yes",
      randomized: "not_applicable",
      general_anaesthesia: "not_applicable",
      intervention_effect_separable: "not_applicable",
      timing_eligible: "not_applicable",
      clinical_outcome_present: "not_applicable",
      surrogate_only: "not_applicable"
    });
  }

  if (
    matchAny((live.title || "").toLowerCase(), [
      /\bchildren\b/,
      /\bchild(?:hood)?\b/,
      /\bpaediatric\b/,
      /\bpediatric\b/,
      /\badolescents?\b/
    ]) ||
    (matchAny(lower, [
      /\bchildren\b/,
      /\bchild(?:hood)?\b/,
      /\bpaediatric\b/,
      /\bpediatric\b/,
      /\badolescents?\b/
    ]) &&
      !matchAny(lower, [/\badults?\b/, /\baged 18\b/, /\b18 years\b/]))
  ) {
    return exclude(base, {
      ...common,
      primary_reason_code: "EXCLUDE_POPULATION",
      evidence_supporting_decision: sentenceWith(text, [
        /\bchildren\b/i,
        /\bpaediatric\b/i,
        /\bpediatric\b/i,
        /\badolescents?\b/i
      ]),
      concise_rationale: "Paediatric-only population."
    });
  }

  if (
    !surgery.surgery ||
    (surgery.explicitNonSurgical &&
      !matchAny(lower, [/\bpostoperat/, /\bafter .*surgery\b/, /\bundergoing .*surgery\b/]))
  ) {
    return exclude(base, {
      ...common,
      primary_reason_code: "EXCLUDE_NON_SURGICAL",
      evidence_supporting_decision:
        sentenceWith(text, [/healthy volunteer/i, /chronic .*pain/i, /pancreatitis/i, /rehabilitation/i, /colonoscopy/i]) ||
        "The title and abstract do not describe an operative surgical population.",
      concise_rationale: "Non-operative or non-surgical population.",
      general_anaesthesia: surgery.explicitNonSurgical ? "no" : anaesthesia
    });
  }

  if (!intervention.ea && !intervention.teas) {
    if (intervention.ordinaryTens) {
      return exclude(base, {
        ...common,
        primary_reason_code: "EXCLUDE_NON_ACUPOINT_TENS",
        evidence_supporting_decision: sentenceWith(text, [/transcutaneous electrical nerve stimulation/i, /\bTENS\b/i]),
        concise_rationale: "Ordinary TENS without acupuncture-point placement.",
        intervention: "ordinary TENS"
      });
    }
    return exclude(base, {
      ...common,
      primary_reason_code: "EXCLUDE_WRONG_INTERVENTION",
      evidence_supporting_decision:
        sentenceWith(text, [/manual acupuncture/i, /auricular/i, /laser acupuncture/i, /acupressure/i, /moxibustion/i]) ||
        "The record does not describe therapeutic TEAS or needle-based electroacupuncture.",
      concise_rationale: "Wrong intervention."
    });
  }

  if (
    matchAny(lower, [
      /\bauricular (?:electro[\s-]?acupunctur|acupuncture)\b/,
      /\belectro-acupuncture-anesthesia device\b/,
      /\belectroacupuncture-anesthesia device\b/
    ])
  ) {
    return exclude(base, {
      ...common,
      primary_reason_code: "EXCLUDE_WRONG_INTERVENTION",
      evidence_supporting_decision: sentenceWith(text, [
        /\bauricular (?:electro[\s-]?acupunctur|acupuncture)\b/i,
        /\belectro-?acupuncture-anesthesia device\b/i
      ]),
      concise_rationale:
        "The electrical intervention is auricular stimulation or a nerve-localization device rather than eligible body-point TEAS or needle-based electroacupuncture.",
      intervention_effect_separable: "no"
    });
  }

  if (
    intervention.wrong &&
    matchAny(lower, [
      /\bincluded acupuncture, electroacupuncture, and intradermal acupuncture\b/,
      /\belectroacupuncture.*(?:plus|combined with).*(?:manual acupuncture|acupressure|auricular point pressing|moxibustion|cupping)\b/,
      /\belectroacupuncture.*(?:plus|combined with|and).*(?:acupoint injection|injection acupuncture)\b/,
      /\bteas.*(?:plus|combined with).*(?:acupressure|wristband pressing|auricular point pressing|aromatherapy|moxibustion|cupping)\b/
    ])
  ) {
    return exclude(base, {
      ...common,
      primary_reason_code: "EXCLUDE_INSEPARABLE_INTERVENTION",
      evidence_supporting_decision: sentenceWith(text, [/included acupuncture/i, /combined with/i, /\bplus\b/i]),
      concise_rationale: "Eligible electrical acupuncture is embedded in an inseparable multimodal intervention.",
      intervention_effect_separable: "no"
    });
  }

  if (intervention.wrong && /\bfloating needle therapy\b/.test(lower)) {
    return exclude(base, {
      ...common,
      primary_reason_code: "EXCLUDE_WRONG_INTERVENTION",
      evidence_supporting_decision: sentenceWith(text, [/floating needle/i]),
      concise_rationale: "Floating-needle therapy is not eligible TEAS or needle-based electroacupuncture.",
      intervention_effect_separable: "no"
    });
  }

  if (anaesthesia === "no") {
    return exclude(base, {
      ...common,
      primary_reason_code: "EXCLUDE_NO_GENERAL_ANAESTHESIA",
      evidence_supporting_decision: sentenceWith(text, [/spinal an/i, /epidural an/i, /plexus block/i, /local an/i, /regional an/i]),
      concise_rationale: "The procedure was conducted without general anaesthesia."
    });
  }

  if (timing.status === "no") {
    return exclude(base, {
      ...common,
      primary_reason_code: "EXCLUDE_TIMING",
      evidence_supporting_decision: timing.description || "Eligible stimulation clearly began later than 24 postoperative hours.",
      concise_rationale: "Eligible stimulation began after the first 24 postoperative hours."
    });
  }

  if (comparator.activeOnly) {
    return exclude(base, {
      ...common,
      primary_reason_code: "EXCLUDE_INELIGIBLE_ACTIVE_COMPARATOR",
      evidence_supporting_decision: sentenceWith(text, [/compared with/i, /\bversus\b/i]),
      concise_rationale: "Only an ineligible active comparator is reported.",
      intervention_effect_separable: "yes"
    });
  }

  if (randomized === "no") {
    return exclude(base, {
      ...common,
      primary_reason_code: "EXCLUDE_NON_RANDOMIZED",
      evidence_supporting_decision: sentenceWith(text, [/retrospective/i, /observational/i, /non-random/i, /single-arm/i]),
      concise_rationale: "Non-randomized study."
    });
  }

  if (outcome.surrogateOnly) {
    return exclude(base, {
      ...common,
      primary_reason_code: "EXCLUDE_NO_ELIGIBLE_OUTCOME",
      evidence_supporting_decision: sentenceWith(text, [/cytokine/i, /interleukin/i, /cortisol/i, /haemodynamic/i, /hemodynamic/i]),
      concise_rationale: "Only physiological or biomarker outcomes are reported.",
      clinical_outcome_present: "no",
      surrogate_only: "yes"
    });
  }

  if (randomized === "unclear") {
    return maybe(base, {
      ...common,
      primary_reason_code: "UNCERTAIN_RANDOMIZATION",
      evidence_supporting_decision:
        sentenceWith(text, [/divided into/i, /assigned (?:into|to)/i, /controlled trial/i]) ||
        "A concurrent comparison is described, but random allocation is not established.",
      concise_rationale: "Random allocation is the principal unresolved eligibility criterion.",
      intervention_effect_separable: comparator.eligibleControl ? "yes" : "unclear"
    });
  }

  if (anaesthesia === "unclear") {
    return maybe(base, {
      ...common,
      primary_reason_code: "UNCERTAIN_GENERAL_ANAESTHESIA",
      evidence_supporting_decision:
        "The operative setting and eligible electrical acupuncture intervention are described, but the anaesthetic technique is not stated.",
      concise_rationale: "General anaesthesia is the principal unresolved criterion.",
      intervention_effect_separable: comparator.eligibleControl ? "yes" : "unclear"
    });
  }

  if (timing.status === "unclear") {
    return maybe(base, {
      ...common,
      primary_reason_code: "UNCERTAIN_TIMING",
      evidence_supporting_decision:
        timing.description ||
        "The perioperative study is otherwise eligible, but the first stimulation time cannot be placed confidently at or before 24 postoperative hours.",
      concise_rationale: "Eligible timing is the principal unresolved criterion.",
      intervention_effect_separable: comparator.eligibleControl ? "yes" : "unclear"
    });
  }

  if (!comparator.eligibleControl) {
    return maybe(base, {
      ...common,
      primary_reason_code: "UNCERTAIN_INTERVENTION_SEPARABILITY",
      evidence_supporting_decision:
        "The abstract does not completely establish the arm structure or balance of background care.",
      concise_rationale: "An independently separable eligible comparison may exist but is not established.",
      intervention_effect_separable: "unclear"
    });
  }

  if (!outcome.clinical) {
    return maybe(base, {
      ...common,
      primary_reason_code: "UNCERTAIN_OUTCOME",
      evidence_supporting_decision:
        "The abstract emphasizes surrogate outcomes, but an eligible clinical outcome or adverse event remains plausible.",
      concise_rationale: "Clinical-outcome reporting is the principal unresolved criterion.",
      clinical_outcome_present: "unclear",
      surrogate_only: "no",
      intervention_effect_separable: "yes"
    });
  }

  return include(base, {
    ...common,
    primary_reason_code: "INCLUDE_CLEAR",
    evidence_supporting_decision:
      sentenceWith(text, [/randomi[sz]ed/i, /general an/i, /preoperat/i, /intraoperat/i]) ||
      "The abstract supports an eligible randomized perioperative TEAS or EA comparison.",
    concise_rationale: "Clearly eligible or strongly supported for full-text assessment.",
    intervention_effect_separable: "yes",
    background_care_balanced: "yes"
  });
}

# Search concept map

Status: master map for translation; PubMed pilot is the only database currently implemented.

## A. TEAS and related terminology

Concept definition: surface-electrode electrical stimulation at recognized or explicitly defined acupuncture points.

Term families:

- Exact names: transcutaneous electrical/electric acupoint stimulation; transcutaneous acupoint electrical/electric stimulation.
- Expanded names: transcutaneous electrical/electric acupuncture or acupuncture-point stimulation; electroacupoint/electro-acupoint stimulation.
- Acupuncture-like TENS phrasing.
- Acronyms TEAS and TAES only with acupuncture/acupoint and electrical/transcutaneous/stimulation context.
- TENS or the PubMed TENS subject heading only in conjunction with acupuncture-point terminology.
- Descriptive surface-electrode electrical-stimulation language coupled to acupoint/acupuncture-point language.

Ordinary TENS at non-acupuncture locations is not the target intervention. It is controlled through contextual conjunctions and screening rather than an unsafe broad NOT exclusion.

## B. Needle-based electroacupuncture

Concept definition: electrical current delivered through acupuncture needles at recognized or explicitly defined acupuncture points.

Term families:

- PubMed subject heading `Electroacupuncture`.
- electroacupuncture, electro-acupuncture, electro acupuncture.
- electric/electrical acupuncture.
- electrically stimulated/stimulating acupuncture.
- electrical/electric stimulation with acupuncture needle wording.

Modality is confirmed during screening; the search intentionally favors recall where abstracts do not fully describe needle delivery.

## C. Surgery and perioperative context

Subject-heading families: operative surgical procedures; perioperative, preoperative, intraoperative, and postoperative care/periods.

Free-text families: surg-, operativ-, operation-, perioperative, preoperative, intraoperative, postoperative, postsurgical, anaesth-, and anesth-.

General anaesthesia is not mandatory in the search and must be verified during screening.

## D. Randomized trials

For PubMed, use the Cochrane sensitivity-maximizing randomized-trial component: randomized controlled trial and controlled clinical trial publication types; randomized/randomised, placebo, randomly, trial, and groups in title/abstract; and the `drug therapy` floating subheading. Apply the standard animal-only exclusion `NOT (animals[mh] NOT humans[mh])`.

Database translations must use a validated sensitive trial filter appropriate to each database and interface.

## Prohibited mandatory electronic-search concepts

Do not require adult, human, general anaesthesia, opioid, analgesia, pain, MME, morphine, PONV, recovery, postoperative outcome, language, or date concepts. Eligibility and reporting for these attributes may be incomplete in searchable metadata.

## Combination logic

1. Build and count TEAS + surgery/perioperative + randomized-trial line.
2. Build and count EA + surgery/perioperative + randomized-trial line.
3. Combine the TEAS and EA modality concepts with OR.
4. Combine the modality union with surgery/perioperative and randomized-trial concepts.
5. Apply an animal-only exclusion when supported by the database.


# A pre-registered ligand-based screen finds no approved drug with selective MCHR1 activity

**Preprint draft — not yet author-reviewed. Not posted to bioRxiv.**

**Author:** Jacob T. Schumacher, OVS Intelligence LLC

---

## Abstract

We pre-registered, executed, and report a ligand-based drug-repurposing screen for selective melanin-concentrating hormone receptor 1 (MCHR1) activity among approved drugs. The screen was designed around selectivity, not raw MCHR1 similarity: each candidate drug was scored by its maximum Morgan-fingerprint Tanimoto similarity to 71 empirically hERG-clean MCHR1 ligands (MCHR1 pChEMBL ≥ 7 with measured hERG inactivity) minus its maximum similarity to 2,441 known potent hERG blockers. The hit criterion — selectivity score ≥ 0.25 and MCHR1 similarity ≥ 0.40 — was carried over from the program's first screen (CNR2) unchanged for cross-target comparability, and reviewed before any ranking run; the ranking script refused to execute without the reviewer's explicit attestation flag. Of 3,417 approved small-molecule drugs with defined structures, zero met the criterion. The highest score was 0.131 (vildagliptin), well separated from the threshold, and no drug cleared even the MCHR1 similarity floor. The counter-set has teeth: terfenadine and astemizole, withdrawn over QT prolongation, score maximum hERG similarity. All data, code, environment, and the date-stamped pre-registration are public; the full run reproduces with one command. We report this negative result without qualification: under the pre-registered method, no candidate justified progression.

## Introduction

The melanin-concentrating hormone receptor 1 (MCHR1) is a GPCR through which the MCH system regulates feeding, energy balance, and sleep. MCH promotes food intake, and MCHR1 antagonists were pursued for over a decade as oral anti-obesity agents: an MCHR1 antagonist with anorectic effects was reported in 2002 (Borowsky et al., 2002), and in the GLP-1 era an oral small molecule remains differentiated — no injection, cheap manufacture.

The field's history is a cautionary one. A decade of medicinal-chemistry effort produced only five Phase I candidates (GW856464, AMG-076, NGD-4715, ALB-127158, BMS-830216), and all were discontinued. The documented killer was cardiovascular: hERG binding and drug-induced QTc prolongation. A field review states it plainly: "cardiovascular risk involving hERG-binding activity and drug induced QTc prolongation has been a major hurdle for a significant number of MCHR1 research programs," and "the structural and physicochemical requirements for MCHR1 potency and hERG inhibition usually correlate with each another" (Högberg, Frimurer & Sasmal, 2012). A 2022 study is blunter: "most drugs developed as MCHR1 antagonists have failed in clinical development due to cardiotoxicity caused by hERG inhibition" (Lim et al., 2022). The honest nuance is that not every discontinued candidate died for hERG specifically — GW856464 fell to low bioavailability, ALB-127158 to insufficient CNS exposure, BMS-830216 to lack of weight reduction in Phase I — but the field-level pattern is unambiguous. To our knowledge, no MCHR1-targeted drug has received regulatory approval.

Drug repurposing is a natural strategy for a target in this position, with a specific angle: approved drugs were never optimized for MCHR1, so their chemotypes were never filtered through the MCHR1-vs-hERG trap that killed the de novo programs. But MCHR1 repurposing has its own trap. A naive similarity screen against known MCHR1 ligands happily returns hERG-blocking chemotypes — molecules carrying the cardiac liability that ended the earlier programs. Selectivity over hERG is therefore not a refinement of this screen; it is the entire point.

We conducted the screen as a pre-registered computational experiment — the second target of the Frontier Screen program, run on the same machine as the CNR2 screen (same pipeline, same hit bar, new target and counter-target). The method, reference sets, hit criteria, falsification conditions, and kill criteria were written down, reviewed, and frozen before the ranking run executed. This manuscript reports the outcome: an honest zero.

## Methods

### Target and counter-target

- **Target:** MCHR1, melanin-concentrating hormone receptor 1 (ChEMBL CHEMBL344, UniProt Q99705).
- **Selectivity counter-target:** hERG, potassium channel KCNH2 (ChEMBL CHEMBL240, UniProt Q12809).
- **Disease area of interest (primary):** obesity / metabolic disease — MCHR1 antagonists as oral appetite suppressants.
- **Disease area (secondary, literature angles, not the screen's claim):** sleep regulation (MCHR1 blockade affects rat sleep–wake architecture; Ahnaou et al., 2008), hepatic steatosis/NASH (a selective antagonist ameliorated obesity and hepatic steatosis in diet-induced obese rodents; Kawata et al., 2017; NASH mouse-model protection in Lim et al., 2022). The mood signal is contested — one study reported lack of efficacy of MCHR1 antagonists in depression and anxiety models (Basso et al., 2006) — so mood stays a literature angle, never an efficacy claim.

The sibling receptor MCHR2 was considered as a counter-target and rejected: it is functional in humans but a pseudogene in rodents, which complicated translation for the whole field, yet ChEMBL holds only 307 MCHR2 activity records — roughly one-twentieth of MCHR1's. A pre-registered selectivity metric over MCHR2 would rest on too thin a basis. It is noted as a limitation and a follow-up check, not part of the metric.

### Data sources

All bioactivity data were pulled from the ChEMBL web services (ebi.ac.uk/chembl/api/data) on 2026-09-15 (Mendez et al., 2019). Exact queries and record counts are recorded in `data/manifest_mchr1.json` in the public repository. The approved-drug library was defined as ChEMBL molecules with max_phase = 4 and a canonical SMILES string — the same library definition as the CNR2 screen.

### Cleaning

Quantitative records were restricted to Ki, IC50, EC50, and Kieq values reported in nM, standardized to pChEMBL (−log10 of the molar value). Single-point percent-inhibition records, kinetic constants, thermal-shift data, and other non-quantitative assay types were quarantined — excluded from ranking and counted in the data-quality report. Repeated evidence for the same molecule and assay type was deduplicated by median of exact values; document IDs were preserved. Full quarantine accounting is in `data_quality_report_mchr1.md`.

| Dataset | Raw records | Usable | Quarantined | Final molecules |
|---|---|---:|---:|---:|
| MCHR1 (CHEMBL344) | 6,037 | 5,322 | 715 | 4,079 |
| hERG (CHEMBL240) | 41,078 | 20,067 | 21,011 | 16,217 |

### Reference sets

- **Tier A (hERG-clean MCHR1 ligands, n = 71):** MCHR1 pChEMBL ≥ 7 (relation '=') with measured hERG inactivity, defined as hERG relation '=' with pChEMBL < 5, or hERG relation '>' whose reported bound itself clears pChEMBL < 5 (tested weaker than 10 µM). This is the tightened rule: the CNR2 screen's independent QA found that a loose '>' rule admitted uninformative bounds, so the machine now requires the bound to be informative. A record like ">2 nM" does not establish inactivity and is excluded. The tightened rule was the default from the start of this screen.
- **Tier B (MCHR1-active, hERG untested, n = 2,137):** MCHR1 pChEMBL ≥ 7, no hERG record. Reported as a secondary annotation column; excluded from the primary metric by pre-registered decision, because hERG activity unknown to the reference set would dilute the selectivity claim.
- **hERG-active counter set (n = 2,441):** hERG pChEMBL ≥ 6 (relation '='), the potent-blocker chemotypes to avoid.

### The selectivity metric

For each approved drug:

- S_mchr1 = maximum Tanimoto similarity (Morgan fingerprint, radius 2, 2048-bit) to the Tier A set
- S_herg = maximum Tanimoto similarity to the hERG-active set
- **selectivity_score = S_mchr1 − S_herg**

Rationale: a repurposing candidate should sit near known hERG-clean MCHR1 chemotypes and far from potent-hERG-blocker chemotypes. A plain MCHR1-similarity screen would return hERG blockers — the exact liability this program exists to avoid. The counter-set has real teeth: the withdrawn hERG blockers terfenadine and astemizole sit in the approved-drug library, and both score maximum hERG similarity (see Results).

### Pre-registered hit criterion and review gate

**Hit = selectivity_score ≥ 0.25 AND S_mchr1 ≥ 0.40**, decided before any ranking run and carried over from the CNR2 screen unchanged — deliberately, so the machine uses one bar across targets and results stay comparable. The bar was not tuned to MCHR1 data. The S_mchr1 floor blocks the vacuous case: a random molecule scores near zero on both terms and would otherwise look "selective." The ranking script (`scripts/03_screen.py --target MCHR1`) refused to execute the full run without the reviewer's explicit attestation flag (`--i-have-reviewed-the-prereg`); the review (2026-09-15, recorded in `preregistration/MCHR1.md` before the ranking run) confirmed the frozen thresholds and recorded the design decisions. Question 1 was answered by the human author directly (frozen bar; an honest zero is acceptable and publishable; the bar will not move after results). Questions 2–5 were delegated by the author to specialist review, each recorded with an explicit confidence grade and citations: (2) keep hERG as the primary and only counter-target, MCHR2 out of the metric — HIGH confidence; (3) obesity/metabolic primary framing, sleep/mood/NASH as literature angles only — HIGH confidence on the literature's existence; (4) accept antagonist blindness for the ligand screen, adjudicate functional direction on hits only — HIGH confidence on the underlying data facts, MEDIUM on the tradeoff judgment; (5) Tier A stays pure for the primary metric, Tier B as secondary annotation — HIGH confidence on consistency with the CNR2 precedent. A 100-drug logic test of the pipeline ran before the review; it exercised the code path on a small sample and did not determine the threshold values. The full pre-registration, including falsification conditions and kill criteria, is public at `preregistration/MCHR1.md`.

### Exclusion scope

Of 4,225 approved drugs pulled, 808 lacked a usable small-molecule structure and were excluded as out of scope for a fingerprint screen (same library definition and exclusion accounting as the CNR2 screen). The screened universe is therefore 3,417 approved small-molecule drugs with defined structures.

## Results

The full ranking run scored 3,417 approved drugs. **Zero met the pre-registered hit criterion.**

The score distribution is cleanly separated from the threshold: the maximum selectivity_score was 0.131 (vildagliptin), against a bar of 0.25, and nothing sits within 0.05 of the threshold. No drug cleared even the S_mchr1 ≥ 0.40 similarity floor. The metric resolves the space — S_mchr1 spans 0 to 0.39 across the drug set, and reference-set self-similarity is 1.0 by construction — so a drug closely resembling the known hERG-clean MCHR1 chemotypes would have scored highly; there is simply nothing in the hit zone.

Top 10 drugs by selectivity_score (all non-hits):

| Rank | Drug | S_mchr1 | S_herg | selectivity_score |
|---:|---|---|---:|---:|
| 1 | Vildagliptin | 0.3086 | 0.1778 | 0.1309 |
| 2 | Saxagliptin anhydrous | 0.2069 | 0.1375 | 0.0694 |
| 3 | Saxagliptin hydrochloride | 0.2045 | 0.1358 | 0.0687 |
| 4 | Mofezolac | 0.2836 | 0.2353 | 0.0483 |
| 5 | Metrizamide | 0.1809 | 0.1522 | 0.0287 |
| 6 | Tofacitinib | 0.2472 | 0.2198 | 0.0274 |
| 7 | Levofloxacin anhydrous | 0.2333 | 0.2069 | 0.0264 |
| 8 | Ofloxacin | 0.2333 | 0.2069 | 0.0264 |
| 9 | Levofloxacin | 0.2308 | 0.2045 | 0.0262 |
| 10 | Anagestone acetate | 0.1978 | 0.1720 | 0.0258 |

Three observations from the ranking:

1. **Iloperidone** was the drug nearest the S_mchr1 ≥ 0.40 floor (0.3913) — and it failed selectivity decisively (−0.222), because it is strongly similar to known hERG blockers (S_herg 0.6133). This is the screen working as designed: the similarity floor alone would nearly have flagged it; the selectivity term correctly rejected it. It is the MCHR1 analog of the CNR2 screen's bicalutamide case, one step further out — here the floor itself was never cleared.
2. **The top of the ranking is a coherent chemical series: gliptins** (vildagliptin, saxagliptin in two salt forms — DPP-4 inhibitors for type 2 diabetes). The metric is not degenerate; it clusters a real chemotype at the top. But at 0.13 against a 0.25 bar it is nowhere near hit territory, and there is no plausible MCHR1 repurposing story for DPP-4 inhibitors. Noted and not pursued.
3. **The counter-set has teeth.** Terfenadine and astemizole — antihistamines withdrawn over QT prolongation — both score S_herg = 1.0 with selectivity scores of −0.759 and −0.727. Known hERG blockers sit at the bottom of this ranking, exactly where the screen's design says they should.

The complete ranked list of all 3,417 drugs is published with this manuscript (`results/mchr1_screen_hits.csv`).

## Discussion

### Why the zero is believable

Three independent lines support taking this negative result at face value. First, the separation is clean: 0.131 against a 0.25 bar is not a borderline miss, nothing sits within 0.05 of the threshold, and no drug cleared even the similarity floor. Second, the metric is not degenerate — it resolves the drug set across a meaningful range (a coherent gliptin series at the top, withdrawn hERG blockers anchored at maximum counter-similarity at the bottom), and its reference self-similarity is exact, so a drug closely resembling the known hERG-clean MCHR1 chemotypes would have scored highly. It cannot speak to chemotypes unlike the reference set. Third, the result is consistent with the field's history: a decade of MCHR1 antagonist programs, five Phase I candidates all discontinued, no MCHR1-targeted drug ever approved. A hit would have been the surprising outcome, not the zero.

### Limitations

This screen is ligand-based only: it cannot see functional direction, so it cannot distinguish agonists from antagonists, and the obesity hypothesis specifically wants antagonists. That blindness was accepted by pre-registered decision. The data facts behind the tradeoff: the raw MCHR1 pull is 3,469 IC50 plus 1,879 Ki (binding) records against roughly 100 direction-informative records, and about 70% of Tier-A-eligible molecules are binding-only — requiring functional annotation up front would have gutted the similarity basis without buying reliable direction. Functional direction would have been adjudicated on hits (chemotype comparison against known antagonist series, then docking in antagonist-bound structures); there were no hits, so Phase 2b docking was not triggered and remains future work.

The Tier A basis is small: 71 hERG-clean ligands, against 1,412 in the CNR2 screen. It clears the pre-registered kill threshold (25) — the selectivity basis exists — but the chemical foundation is narrower, and the conclusion should be read with that in mind. Tier B ligands (2,137 MCHR1-active, hERG-untested) were excluded from the primary metric, so the reference set is narrower than the full MCHR1-active chemical space. Similarity is not activity: the approved-drug chemical space may simply contain no hERG-clean MCHR1 chemotype, which is itself a finding but not a biological proof that none exists. ChEMBL is literature-curated and inherits publication bias and assay heterogeneity; roughly 12% of MCHR1 and 51% of hERG raw records were quarantined as unsuitable for quantitative ranking.

Two red-team objections from the pre-registration deserve plain statements. First, hERG distance is not a cardiac safety certificate: low similarity to known hERG blockers filters the field's known killer, but hERG is one channel and QT risk has other mechanisms. No safety claim is made beyond candidacy for experimental follow-up, with the primary liability screened out by design. Second, the field died on translation as well as on hERG: rodent-to-human efficacy translation failed, and the MCHR2 rodent-pseudogene problem means animal models misled the field. Repurposing fixes the economics (known safety and pharmacokinetics) but not the translation question; the screen finds chemotypes worth testing, not a validated therapy. MCHR2 itself was excluded from the metric for thin data (307 records) and stands as a follow-up check, not a resolved question.

### What this result means

Under the pre-registered method, a systematic screen of the approved-drug chemical space found no hERG-clean MCHR1 chemotype. For repurposing programs, that is actionable information: it says the next MCHR1 therapeutic is unlikely to be found by mining approved drugs with this approach, and effort is better directed at novel chemistry or orthogonal screening modalities. Negative results of this kind are under-reported relative to their decision value; we report this one plainly.

## Conclusion

We pre-registered a selectivity-first repurposing screen for MCHR1 — built around hERG, the field's documented failure mode — ran it exactly as specified after review of the pre-registration, and found nothing above the bar. The pipeline, data, pre-registration, and full ranked output are public and reproducible with one command. The honest zero stands.

## Data and code availability

- Repository: https://github.com/Synteri/frontier-screen (MIT license)
- Pre-registration: `preregistration/MCHR1.md` (review decisions recorded 2026-09-15: Q1 answered by the human author; Q2–Q5 by specialist review with confidence grades)
- Decision log: `DECISIONS.md`; data-quality report: `data_quality_report_mchr1.md`
- Full ranked scores (3,417 drugs): `results/mchr1_screen_hits.csv`; run summary: `results/mchr1_RUN_SUMMARY.md`
- Raw ChEMBL pulls are cached locally (not committed); the pipeline re-pulls from the live ChEMBL web services (pinned code and recorded queries in `data/manifest_mchr1.json`; ChEMBL is a live database, so record counts may shift over time)
- Environment: `environment.yml` (conda); one-command run: `python scripts/01_pull_data.py --target MCHR1 && python scripts/02_clean_data.py --target MCHR1 && python scripts/03_screen.py --target MCHR1 --i-have-reviewed-the-prereg`
- Bioactivity data: ChEMBL (Mendez et al., 2019), CC-BY-SA 3.0

## AI-assistance disclosure

This work was executed by AI agents under human direction. The human author selected the target, answered the first pre-registration review question directly (frozen thresholds; an honest zero is an acceptable, publishable outcome), delegated questions 2–5 to specialist AI review — recorded with explicit confidence grades and citations in the pre-registration — and retains authorship review of this manuscript. The agents built the pipeline, ran the screen, and drafted this text. No step of the analysis was hidden from the author, and every load-bearing claim is reproducible from the public repository without contacting the author.

## References

1. Mendez D, Gaulton A, Bento AP, et al. ChEMBL: towards direct deposition of bioassay data. *Nucleic Acids Res.* 2019;47(D1):D930–D940. doi:10.1093/nar/gky1075
2. Högberg T, Frimurer TM, Sasmal PK. Melanin concentrating hormone receptor 1 (MCHR1) antagonists — still a viable approach for obesity treatment? *Bioorg Med Chem Lett.* 2012;22:6039–6047. doi:10.1016/j.bmcl.2012.08.025. Reports that hERG binding and QTc prolongation "has been a major hurdle for a significant number of MCHR1 research programs" and that the structural requirements for MCHR1 potency and hERG inhibition "usually correlate with each another."
3. Lim G, You KY, Lee JH, Jeon MK, Lee BH, Ryu JY, Oh K. Identification and new indication of melanin-concentrating hormone receptor 1 (MCHR1) antagonist derived from machine learning and transcriptome-based drug repositioning approaches. *Int J Mol Sci.* 2022;23:3807. doi:10.3390/ijms23073807. States that "most drugs developed as MCHR1 antagonists have failed in clinical development due to cardiotoxicity caused by hERG inhibition."
4. Borowsky B, Durkin MM, Ogozalek K, et al. Antidepressant, anxiolytic and anorectic effects of a melanin-concentrating hormone-1 receptor antagonist. *Nat Med.* 2002;8:825–830. doi:10.1038/nm741
5. Ahnaou A, Drinkenburg WH, Bouwknecht JA, et al. Blocking melanin-concentrating hormone MCH1 receptor affects rat sleep–wake architecture. *Eur J Pharmacol.* 2008;579:177–188. doi:10.1016/j.ejphar.2007.10.017
6. Kawata Y, Okuda S, Hotta N, et al. A novel and selective melanin-concentrating hormone receptor 1 antagonist ameliorates obesity and hepatic steatosis in diet-induced obese rodent models. *Eur J Pharmacol.* 2017;796:45–53. doi:10.1016/j.ejphar.2016.12.018
7. Basso AM, Bratcher NA, Gallagher KB, et al. Lack of efficacy of melanin-concentrating hormone-1 receptor antagonists in models of depression and anxiety. *Eur J Pharmacol.* 2006;540:115–120. doi:10.1016/j.ejphar.2006.04.043
8. RDKit: Open-Source Cheminformatics Software. https://www.rdkit.org [software citation]

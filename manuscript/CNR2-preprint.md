# A pre-registered ligand-based screen finds no approved drug with selective CB2 activity

**DRAFT — for author review only. Not posted.**

**Author (DRAFT):** Jacob T. Schumacher, OVS Intelligence LLC

---

## Abstract

We pre-registered, executed, and report a ligand-based drug-repurposing screen for selective cannabinoid CB2 receptor (CNR2) activity among approved drugs. The screen was designed around selectivity, not raw CB2 similarity: each candidate drug was scored by its maximum Morgan-fingerprint Tanimoto similarity to 1,412 empirically selective CB2 ligands (CNR2 pChEMBL ≥ 7 with measured CB1 inactivity) minus its maximum similarity to 4,352 known CB1-active molecules. The hit criterion — selectivity score ≥ 0.25 and CB2 similarity ≥ 0.40 — was fixed and reviewed before any ranking run, and the ranking script refused to execute until that review was recorded. Of 3,417 approved small-molecule drugs with defined structures, zero met the criterion. The highest score was 0.139, well separated from the threshold. The single drug clearing even the CB2 similarity floor, bicalutamide, failed on selectivity — the failure mode the screen was built to catch. All data, code, environment, and the date-stamped pre-registration are public; the full run reproduces with one command. We report this negative result without qualification: under the pre-registered method, no candidate justified progression.

## Introduction

The cannabinoid CB2 receptor (CNR2) is predominantly expressed in immune cells and peripheral tissues, and selective modulation of CB2 without CB1 engagement has long been proposed as a route to anti-inflammatory, analgesic, and anti-fibrotic pharmacology without psychoactive liability (Li et al., 2019). The clinical history of the field is instructive. CB1 blockade (rimonabant) failed on psychiatric adverse effects. On the CB2 side, the most advanced selective agonist, lenabasum (JBT-101), reached a phase 3 trial in diffuse cutaneous systemic sclerosis (RESOLVE-1) that did not meet its primary endpoint (Spiera et al., 2023). To our knowledge, no selective CB2 agonist has received regulatory approval [5].

Drug repurposing is a natural strategy for a target in this position: approved drugs carry known safety profiles, and any unreported CB2 activity among them would be immediately actionable. But CB2 repurposing has a specific trap. A naive similarity screen against known CB2 ligands happily returns non-selective cannabinoids — molecules whose CB1 activity carries the psychoactive liability that has killed earlier programs. Selectivity over CB1 is therefore not a refinement of this screen; it is the entire point.

We conducted the screen as a pre-registered computational experiment. The method, reference sets, hit criteria, falsification conditions, and kill criteria were written down, reviewed, and frozen before the ranking run executed. This manuscript reports the outcome: an honest zero.

## Methods

### Target and counter-target

- **Target:** CNR2, cannabinoid CB2 receptor (ChEMBL CHEMBL253, UniProt P34972).
- **Selectivity counter-target:** CB1, cannabinoid CB1 receptor (ChEMBL CHEMBL218, UniProt P21554).
- **Disease area of interest:** chronic pain, inflammatory disease, fibrosis — non-psychoactive cannabinoid pharmacology.

### Data sources

All bioactivity data were pulled from the ChEMBL web services (ebi.ac.uk/chembl/api/data) on 2026-09-15 (Mendez et al., 2019). Exact queries and record counts are recorded in `data/manifest.json` in the public repository. The approved-drug library was defined as ChEMBL molecules with max_phase = 4 and a canonical SMILES string.

### Cleaning

Quantitative records were restricted to Ki, IC50, EC50, and Kieq values reported in nM, standardized to pChEMBL (−log10 of the molar value). Single-point percent-inhibition records, kinetic constants (kon/koff), thermal-shift data, and other non-quantitative assay types were quarantined — excluded from ranking and counted in the data-quality report. Repeated evidence for the same molecule and assay type was deduplicated by median of exact values; document IDs were preserved. Full quarantine accounting is in `data_quality_report.md`.

| Dataset | Raw records | Usable | Quarantined | Final molecules |
|---|---|---:|---:|---:|
| CNR2 (CHEMBL253) | 22,523 | 13,680 | 8,843 | 10,020 |
| CB1 (CHEMBL218) | 25,853 | 12,775 | 13,078 | 9,366 |

7,759 molecules had measured data on both receptors — the empirical basis for the selectivity reference set.

### Reference sets

- **Tier A (selective CB2 ligands, n = 1,412):** CNR2 pChEMBL ≥ 7 (relation '=') with measured CB1 inactivity, defined as CB1 relation '=' with pChEMBL < 5, or CB1 relation '>' (true value weaker than reported).
- **Tier B (CB2-active, CB1 untested, n = 1,034):** CNR2 pChEMBL ≥ 7, no CB1 record. Reported as a secondary annotation column; excluded from the primary metric by pre-registered decision, because CB1 activity unknown to the reference set would dilute the selectivity claim.
- **CB1-active counter set (n = 4,352):** CB1 pChEMBL ≥ 6 (relation '=').

### The selectivity metric

For each approved drug:

- S_cb2 = maximum Tanimoto similarity (Morgan fingerprint, radius 2, 2048-bit) to the Tier A set
- S_cb1 = maximum Tanimoto similarity to the CB1-active set
- **selectivity_score = S_cb2 − S_cb1**

Rationale: a repurposing candidate should sit near known selective-CB2 chemotypes and far from CB1-active chemotypes. A plain CB2-similarity screen would return non-selective cannabinoids — the exact failure mode this program exists to avoid.

### Pre-registered hit criterion and review gate

**Hit = selectivity_score ≥ 0.25 AND S_cb2 ≥ 0.40**, decided before any ranking run. The S_cb2 floor blocks the vacuous case: a random molecule scores near zero on both terms and would otherwise look "selective." The ranking script (`scripts/03_screen.py`) physically refused to execute the full run until the pre-registration review was recorded; the review (2026-09-15) confirmed the thresholds, accepted an honest zero as a publishable outcome, and recorded two delegated design decisions: (1) the screen's blindness to functional direction (agonist vs. antagonist) is accepted for the ligand stage and deferred to structure-based docking on any surviving hits; (2) Tier A remains pure for the primary metric, with Tier B as secondary annotation. The full pre-registration, including falsification conditions and kill criteria, is public at `preregistration/CNR2.md`.

### Exclusion scope

Of 4,225 approved drugs pulled, 808 lacked a usable small-molecule structure and were excluded as out of scope for a fingerprint screen: proteins (178), antibodies (150), vaccines, enzymes, oligonucleotides, cells/genes, and inorganics/organometallics with no meaningful SMILES (e.g., cisplatin, oxaliplatin, cupric sulfate). The screened universe is therefore 3,417 approved small-molecule drugs with defined structures.

## Results

The full ranking run scored 3,417 approved drugs. **Zero met the pre-registered hit criterion.**

The score distribution is cleanly separated from the threshold: the maximum selectivity_score was 0.139 (ioversol), against a bar of 0.25. No near-misses cluster at the threshold. Reference-set self-similarity is 1.0 by construction, and S_cb2 spans 0–0.42 across the drug set, so the metric resolves the space; there is simply nothing in the hit zone.

Top 10 drugs by selectivity_score (all non-hits):

| Rank | Drug | S_cb2 | S_cb1 | selectivity_score |
|---:|---|---|---:|---:|
| 1 | Ioversol | 0.3016 | 0.1622 | 0.1394 |
| 2 | Piracetam | 0.3208 | 0.2000 | 0.1208 |
| 3 | Revumenib | 0.3684 | 0.2476 | 0.1208 |
| 4 | Iodixanol | 0.2857 | 0.1692 | 0.1165 |
| 5 | Iohexol | 0.2857 | 0.1692 | 0.1165 |
| 6 | Bicalutamide | 0.4219 | 0.3108 | 0.1111 |
| 7 | Iomeprol | 0.2903 | 0.1806 | 0.1098 |
| 8 | Thioguanine | 0.2632 | 0.1538 | 0.1093 |
| 9 | Gosogliptin | 0.3288 | 0.2366 | 0.0922 |
| 10 | Methoxsalen | 0.2857 | 0.1970 | 0.0887 |

Two observations from the top of the list:

1. **Bicalutamide** was the only drug in the entire library to clear even the S_cb2 ≥ 0.40 floor (0.4219) — and it failed selectivity (0.1111), because it is comparably similar to known CB1 actives. This is the screen working as designed: the similarity floor alone would have flagged it; the selectivity term correctly rejected it.
2. **The top-ranked cluster is iodinated X-ray contrast agents** (ioversol, iodixanol, iohexol, iomeprol). These are large polyiodinated molecules that rank together by mutual chemical similarity, and they are intravenous-only diagnostics with no plausible repurposing path. They were noted and not pursued.

The complete ranked list of all 3,417 drugs is published with this manuscript (`results/screen_hits.csv`).

## Discussion

### Why the zero is believable

Three independent lines support taking this negative result at face value. First, the separation is clean: 0.139 against a 0.25 bar is not a borderline miss, and nothing clusters near the threshold. Second, the metric is not degenerate — it resolves the drug set across a meaningful range and its reference self-similarity is exact, so a drug closely resembling the known selective-CB2 chemotypes would have scored highly. It cannot speak to chemotypes unlike the reference set. Third, the result is consistent with the field's history: no selective CB2 agonist has ever been approved, and the most advanced candidate failed in phase 3. A hit would have been the surprising outcome, not the zero.

### Limitations

This screen is ligand-based only: it cannot see functional direction, so it cannot distinguish agonists from antagonists, and the pain/inflammation hypothesis specifically wants agonists. That blindness was accepted by pre-registered decision; it would have been adjudicated by docking against agonist- and antagonist-bound CB2 structures on any surviving hits, of which there were none. Tier B ligands (CB2-active, CB1 untested) were excluded from the primary metric, so the reference set is narrower than the full CB2-active chemical space. Similarity is not activity: the approved-drug chemical space may simply contain no CB2-selective chemotypes, which is itself a finding but not a biological proof that none exist. ChEMBL is literature-curated and inherits publication bias and assay heterogeneity; ~40% of raw records were quarantined as unsuitable for quantitative ranking. Finally, structure-based docking (PDB 5ZTY antagonist-bound, 6KPC agonist-bound, 6PT0 CB2–Gi agonist complex) was deferred as a conditional phase and could in principle find what ligand similarity missed; it remains future work.

An adversarial check against the newest literature sharpens the scope of the claim. A February 2026 study reported weak CB2 activation by the approved HIV protease inhibitor amprenavir (EC50 760 nM, 49% maximal response) and described mycophenolate mofetil as a CB2 activator from a functional screen [5]. In our screen, amprenavir scored S_cb2 0.237 with selectivity −0.051, and mycophenolate mofetil scored S_cb2 0.264 with selectivity −0.029 — both far below the hit bar, and both slightly more similar to CB1-active chemotypes than to the selective-CB2 reference set. For amprenavir this is consistent: weak, sub-threshold activity should not clear a bar built for strong selective chemotypes. Mycophenolate illustrates the genuine blind spot: a similarity screen cannot see chemotypes unlike its reference set, so a truly novel selective scaffold in the approved-drug space could pass through undetected. The conclusion is therefore scoped exactly as pre-registered: under this method, no approved drug resembles the known selective-CB2 chemotypes strongly and selectively enough to pursue — not a proof that no CB2 activity exists among approved drugs.

### What this result means

Under the pre-registered method, a systematic screen of the approved-drug chemical space found no selective CB2 chemotype. For repurposing programs, that is actionable information: it says the next selective CB2 therapeutic is unlikely to be found by mining approved drugs with this approach, and effort is better directed at novel chemistry or orthogonal screening modalities. Negative results of this kind are under-reported relative to their decision value; we report this one plainly.

## Conclusion

We pre-registered a selectivity-first repurposing screen for CB2, ran it exactly as specified after independent review of the pre-registration, and found nothing above the bar. The pipeline, data, pre-registration, and full ranked output are public and reproducible with one command. The honest zero stands.

## Data and code availability

- Repository: https://github.com/Synteri/frontier-screen (MIT license)
- Pre-registration: `preregistration/CNR2.md` (review decisions appended 2026-09-15)
- Decision log: `DECISIONS.md`; data-quality report: `data_quality_report.md`
- Full ranked scores (3,417 drugs): `results/screen_hits.csv`; run summary: `RUN_SUMMARY.md`
- Raw ChEMBL pulls are cached locally (not committed, ~90 MB); the pipeline re-pulls deterministically from the ChEMBL web services
- Environment: `environment.yml` (conda); one-command run: `run.ps1` on Windows / `python scripts/01_pull_data.py && python scripts/02_clean_data.py && python scripts/03_screen.py --i-have-reviewed-the-prereg`
- Bioactivity data: ChEMBL (Mendez et al., 2019), CC-BY-SA 3.0

## AI-assistance disclosure

This work was executed by AI agents under human direction. The human author selected the target, reviewed and approved the pre-registration (including the hit thresholds and the acceptability of a zero result) before the ranking run, and retains authorship review of this manuscript. The agents built the pipeline, ran the screen, and drafted this text. No step of the analysis was hidden from the author, and every load-bearing claim is reproducible from the public repository without contacting the author.

## References

1. Mendez D, Gaulton A, Bento AP, et al. ChEMBL: towards direct deposition of bioassay data. *Nucleic Acids Res.* 2019;47(D1):D930–D940. doi:10.1093/nar/gky1075
2. Li X, Shen T, Hua T, et al. Crystal structure of the human cannabinoid receptor CB2. *Cell.* 2019;176:459–467.e13. doi:10.1016/j.cell.2018.12.011
3. Spiera R, Kuwana M, Khanna D, et al. Efficacy and Safety of Lenabasum, a Cannabinoid Type 2 Receptor Agonist, in a Phase 3 Randomized Trial in Diffuse Cutaneous Systemic Sclerosis. *Arthritis Rheumatol.* 2023. RESOLVE-1 did not meet its primary endpoint (ACR CRISS at week 52, lenabasum 20 mg twice daily vs placebo).
4. RDKit: Open-Source Cheminformatics Software. https://www.rdkit.org [software citation; version 2026.03.6 used]
5. Drug repurposing: conversion of the peripherally restricted HIV protease inhibitor amprenavir to potent, selective, and CNS-penetrant agonists for the cannabinoid receptor 2. *J. Med. Chem.* 2026. doi:10.1021/acs.jmedchem.5c02796 [author list to confirm at posting; states "to date, no CB2-selective compound has reached the market"]

---

## Open questions for author review — resolutions 2026-09-15

1. **Affiliation.** Resolved: OVS Intelligence, LLC. Author name "Jacob" (not "Jake") in professional settings.
2. **Lenabasum citation.** Resolved: primary source found — Spiera et al., *Arthritis Rheumatol.* 2023 (RESOLVE-1). Reference 3 updated.
3. **"No selective CB2 agonist has received regulatory approval."** Verified with a primary source: *J. Med. Chem.* 2026 states "to date, no CB2-selective compound has reached the market" (ref 5). The claim is carried by the citation and the reproducible screen, not by the author's personal domain expertise — that is the design.
4. **Disease-area framing.** Jacob: keep as is (chronic pain, inflammation, fibrosis).
5. **Docking as future work.** Agent decision (delegated): stays as future work in one honest sentence. Not closed out, not over-promised.
6. **Preprint server.** bioRxiv (pharmacology). The GitHub repo is already public; the preprint links it.
7. **Tone check.** Jacob: fine as is.

Still open for Jacob: confirm the author list on reference 5 at posting time, and flag any sentence he would not personally defend.

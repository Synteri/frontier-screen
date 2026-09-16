# Pre-registration — MCHR1 repurposing screen

Status: DRAFT for the human author's review. No ranking run happens until this
is approved (`--i-have-reviewed-the-prereg` gate in `scripts/03_screen.py`).

Second target of the Frontier Screen program. Same machine as the CNR2 screen
(same pipeline, same hit bar), new target and new counter-target, configured
via `targets/MCHR1.json`.

## Target

- **Target:** MCHR1, melanin-concentrating hormone receptor 1 — ChEMBL CHEMBL344, UniProt Q99705
- **Counter-target:** hERG, potassium channel KCNH2 — ChEMBL CHEMBL240, UniProt Q12809
- **Disease area (primary):** obesity / metabolic disease — MCHR1 antagonists as oral appetite suppressants. In the GLP-1 era an oral small molecule remains differentiated (no injection, cheap manufacture).
- **Disease area (secondary, literature angles, not the screen's claim):** sleep regulation (REM), anxiety/depression, NASH — the MCH system is implicated in all three, but the screen is built and judged on the obesity rationale.
- **Why this target:** 6,037 ChEMBL bioactivity records with the cleanest data of the Phase 1 shortlist (85% IC50 in the scout sample); zero recruiting trials on clinicaltrials.gov — genuinely neglected. No MCHR1-targeted drug has ever been approved. A field review reports that over a decade of effort produced only five Phase I candidates (GW856464, AMG-076, NGD-4715, ALB-127158, BMS-830216), all discontinued except BMS-830216 which completed a Phase I study in obese subjects. The documented killer of the field's programs was hERG binding: cardiovascular risk (QTc prolongation), and the structural/physicochemical requirements for MCHR1 potency correlate with hERG inhibition (Bioorg. Med. Chem. Lett. review of MCHR1 antagonists; Int. J. Mol. Sci. 2022, KRX-104130 paper). Repurposing angle: approved drugs were never optimized for MCHR1, so their chemotypes were never filtered through the MCHR1-vs-hERG trap that killed the de novo programs. Selectivity over hERG is therefore not a refinement of this screen; it is the entire point.

## Counter-target decision (deliberate, justified)

- **hERG (chosen):** (1) it is the field's documented failure mode — the screen is designed to reject exactly the liability that killed the programs; (2) 41,078 ChEMBL records give a deep counter-set; (3) known withdrawn hERG blockers (terfenadine, astemizole) sit in the approved-drug library, so the counter-similarity has real teeth.
- **MCHR2 (sibling receptor, considered and rejected):** biologically interesting — MCHR2 is functional in humans but a pseudogene in rodents, which complicated translation of the whole field — but ChEMBL holds only 307 MCHR2 records. A pre-registered selectivity metric over MCHR2 would rest on a thin basis and invite exactly the "selectivity illusion" falsification below. MCHR2 is noted as a limitation and a follow-up check on any hits, not part of the metric.

## Data

- Bioactivity source: ChEMBL web services (ebi.ac.uk/chembl/api/data); exact pull recorded in `data/manifest_mchr1.json`. Target/counter-target configured in `targets/MCHR1.json`.
- Approved-drug library: ChEMBL molecules with max_phase=4 and a canonical SMILES (same library definition as CNR2).
- Activity cutoff: pChEMBL computed from nM Ki/IC50/EC50/Kieq. Single-point % inhibition records are quarantined (excluded from ranking, counted in the data-quality report). Dedupe: one value per (molecule, assay type) by median of exact values — the Phase 1 scout found single-paper kinetic series inflating counts, so this step is load-bearing.
- Reference sets (from cleaned data):
  - Tier A (MCHR1-active, hERG-clean): MCHR1 pChEMBL >= 7 (relation '=') AND measured hERG inactivity: (hERG '=' with pChEMBL < 5) OR (hERG '>' with the reported bound itself clearing pChEMBL < 5, i.e. tested weaker than 10 uM). **This is the tightened rule**: the CNR2 screen's QA found the loose '>' rule admitted uninformative bounds; the machine now requires the bound to be informative. A record like ">2 nM" does not establish inactivity and is excluded.
  - Tier B (MCHR1-active, hERG untested): MCHR1 pChEMBL >= 7, no hERG record. Reported, flagged, not selectivity evidence.
  - hERG-active counter set: hERG pChEMBL >= 6 (relation '=') — potent hERG blockers, the chemotypes to avoid.

## Hit definition (decided now, not after seeing results)

For each approved drug:
- `S_mchr1` = max Tanimoto (Morgan r=2, 2048-bit) to Tier A
- `S_herg`  = max Tanimoto to the hERG-active set
- `selectivity_score` = S_mchr1 − S_herg

**Hit = selectivity_score >= 0.25 AND S_mchr1 >= 0.40.**
The bar is carried over from the CNR2 screen unchanged, deliberately: the
machine uses one bar across targets so results are comparable, and the bar
was not tuned to MCHR1 data. The S_mchr1 floor blocks the vacuous case (a
random molecule scores ~0 on both and would otherwise look "selective").
Top 10 hits by selectivity_score are written up as candidate dossiers; the
rest of the ranked list is published with the preprint regardless of outcome.

## Falsification (what would prove the result wrong)

1. **Novelty collapse:** every hit above threshold turns out to be a known or previously claimed MCHR1 ligand (literature/patent/trial check). Then the screen discovered nothing and the bet's contribution is zero.
2. **Thin reference basis:** Tier A contains fewer than 25 ligands after cleaning. Similarity to 25 molecules is not a basis for ranking 4,000 drugs — the screen would be noise with a threshold.
3. **Scaffold collapse:** all hits fall within a single chemical series. Then we found one chemotype's neighbors, not a repurposing screen.
4. **Selectivity illusion:** the top hits' hERG-cleanliness rests only on Tier B (hERG untested) rather than measured hERG data. Without measured counter-evidence the "selective" label is unearned.
5. **hERG contradiction:** a hit later shows meaningful hERG blockade experimentally. Then the ranking's central premise — distance from hERG-blocker chemotypes — failed, and the metric is not trusted until the disagreement is understood.

## Novelty-check procedure (per candidate, date-stamped)

- [ ] PubMed + Semantic Scholar: "<drug name> MCHR1", "<drug name> melanin-concentrating hormone"
- [ ] clinicaltrials.gov: "<drug name>" × "MCHR1 / melanin-concentrating"
- [ ] Google Patents / Lens: "<drug name>" × "MCHR1 / melanin concentrating hormone receptor"
- [ ] Overlap check: candidate already in Tier A/B reference sets (self-hit)
- [ ] Record search date + query + result (negative results count as results)

## Red-team plan

- **Objection 1 — antagonist blindness:** the therapeutic direction is antagonism (MCH promotes feeding; agonism would be pro-obesity — the wrong direction), but the screen cannot tell agonists from antagonists: ChEMBL binding records do not reliably encode functional direction, and annotating ~thousands of Tier A ligands from assay text is noisy. Answer required: chemotype analysis of hits against known MCHR1 antagonist series; functional direction adjudicated in Phase 2b docking on surviving hits only. Recorded as a limitation.
- **Objection 2 — hERG distance is not a cardiac safety certificate:** low similarity to known hERG blockers filters the field's known killer; it does not prove a candidate is cardiac-safe. hERG is one channel; QT risk has other mechanisms. Answer required: honest limits section; no safety claim beyond "candidate for experimental follow-up, with the field's primary liability screened out by design."
- **Objection 3 — the field died on translation, not just hERG:** rodent-to-human efficacy translation failed, and the MCHR2 rodent-pseudogene problem means animal models misled the field. An approved drug with MCHR1 activity still faces the biology risk; repurposing fixes the economics (known safety/PK) but not the translation question. Answer required: honest limits section; the screen finds chemotypes worth testing, not a validated therapy.
- Adversary: a second model pass over the top-10 dossiers arguing each one is wrong, plus the human author's review. Two AIs agreeing is weak evidence (shared failure modes); the pre-committed falsification criteria above are the stronger check.

## Kill criteria for this bet

- Cleaned quantitative MCHR1 records < 2,000 after dedupe → data basis too thin.
- Tier A < 25 hERG-clean MCHR1 ligands → selectivity basis does not exist.
- Zero hits above threshold → publish the negative result honestly or kill.
- Novelty collapse (falsification 1) → kill; the screen adds nothing.
- Any single blocker unfixable in one week → pause, don't spiral.

## Phase 2b (docking, not built yet)

Docking the hits against MCHR1 structures would test the antagonist-blindness limitation (red-team objection 1): antagonist-bound pockets select for the therapeutic direction. Candidate structures to be verified in the PDB at that time — none are pre-committed here. Build only if the ligand-based screen produces hits worth the compute.

## Review decisions — PENDING

The pre-registration above has not yet been reviewed. The author must decide:

1. **Threshold carry-over:** the 0.25 / 0.40 bar is inherited from CNR2 for cross-target comparability, not tuned to MCHR1. Confirm an honest-zero outcome stays acceptable and publishable, and the bar will not be lowered after seeing results.
2. **Counter-target choice:** hERG as the primary counter-target (field's failure mode) with MCHR2 noted but excluded from the metric. Confirm, or redirect.
3. **Disease framing:** obesity/metabolic as the primary therapeutic rationale (sleep, mood, NASH as secondary literature angles only). Confirm, or redirect.
4. **Antagonist blindness:** accepted for the ligand screen, adjudicated in Phase 2b on surviving hits only, recorded as a limitation. Confirm, or require functional annotation up front.
5. **Tier B handling:** Tier A stays pure for the primary metric; Tier B similarity reported as secondary annotation only. Confirm.

Full ranking run authorized only after these are recorded above.

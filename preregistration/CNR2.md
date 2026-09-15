# Pre-registration — CNR2 repurposing screen

Status: DRAFT for Jake's review. No ranking run happens until this is approved.
Target selected 2026-09-15 (see DECISIONS.md).

## Target

- **Target:** CNR2, cannabinoid CB2 receptor — ChEMBL CHEMBL253, UniProt P34972
- **Counter-target:** CB1, cannabinoid CB1 receptor — ChEMBL CHEMBL218, UniProt P21554
- **Disease area:** chronic pain, inflammatory disease, fibrosis (non-psychoactive cannabinoid pharmacology)
- **Why this target:** 22,523 ChEMBL bioactivity records (largest shortlist set);
  no selective CB2 agonist approved; only 3 recruiting trials, all academic —
  genuinely neglected. Repurposing angle: many approved non-cannabinoid drugs
  have unreported CB2 activity. CB1 selectivity is the entire game: CB1
  activity means psychoactive liability, the failure mode that killed the
  field's earlier programs. The screen is therefore built around selectivity,
  not raw CB2 similarity.

## Data

- Bioactivity source: ChEMBL web services (ebi.ac.uk/chembl/api/data), pulled 2026-09-15; exact pull recorded in `data/manifest.json`.
- Approved-drug library: ChEMBL molecules with max_phase=4 and a canonical SMILES.
- Activity cutoff: pChEMBL computed from nM Ki/IC50/EC50/Kieq. Single-point %
  inhibition records are quarantined (excluded from ranking, counted in the
  data-quality report). Dedupe: one value per (molecule, assay type) by median
  of exact values — the Phase 1 scout found single-paper kinetic series
  inflating counts, so this step is load-bearing.
- Reference sets (from cleaned data):
  - Tier A (selective CB2 ligands): CNR2 pChEMBL >= 7 (relation '=') AND
    measured CB1 inactivity (CB1 '=' with pChEMBL < 5, or relation '>').
  - Tier B (CB2-active, CB1 untested): CNR2 pChEMBL >= 7, no CB1 record.
    Reported, flagged, not selectivity evidence.
  - CB1-active counter set: CB1 pChEMBL >= 6 (relation '=').

## Hit definition (decided now, not after seeing results)

For each approved drug:
- `S_cb2`  = max Tanimoto (Morgan r=2, 2048-bit) to Tier A
- `S_cb1`  = max Tanimoto to the CB1-active set
- `selectivity_score` = S_cb2 − S_cb1

**Hit = selectivity_score >= 0.25 AND S_cb2 >= 0.40.**
The S_cb2 floor blocks the vacuous case (a random molecule scores ~0 on both
and would otherwise look "selective"). Top 10 hits by selectivity_score are
written up as candidate dossiers; the rest of the ranked list is published
with the preprint regardless of outcome.

## Falsification (what would prove the result wrong)

1. **Novelty collapse:** every hit above threshold turns out to be a known or
   previously claimed CB2 ligand (literature/patent/trial check). Then the
   screen discovered nothing and the bet's contribution is zero.
2. **Thin reference basis:** Tier A contains fewer than 25 ligands after
   cleaning. Similarity to 25 molecules is not a basis for ranking 4,000
   drugs — the screen would be noise with a threshold.
3. **Scaffold collapse:** all hits fall within a single chemical series
   (e.g. all aminoalkylindoles). Then we found one chemotype's neighbors,
   not a repurposing screen.
4. **Selectivity illusion:** the top hits' CB1 inactivity rests only on Tier B
   (CB1 untested) rather than measured CB1 data. Without measured
   counter-evidence the "selective" label is unearned.
5. **Docking contradiction (Phase 2b):** if pursued, and docked poses/scores
   systematically contradict the ligand-based ranking, the ranking is not
   trusted until the disagreement is understood.

## Novelty-check procedure (per candidate, date-stamped)

- [ ] PubMed + Semantic Scholar: "<drug name> CB2", "<drug name> cannabinoid receptor"
- [ ] clinicaltrials.gov: "<drug name>" × "cannabinoid / CB2"
- [ ] Google Patents / Lens: "<drug name>" × "CNR2 / cannabinoid receptor 2"
- [ ] Overlap check: candidate already in Tier A/B reference sets (self-hit)
- [ ] Record search date + query + result (negative results count as results)

## Red-team plan

- **Objection 1 — cannabinoids in disguise:** similarity to CB2 ligands may
  just recover cannabinoid scaffold space; the metric cannot see functional
  direction (agonist vs antagonist) or CB1 activity outside the counter set.
  Answer required: chemotype analysis of hits vs known cannabinoids.
- **Objection 2 — polypharmacology:** approved drugs were optimized for other
  targets; CB2 activity may ride along with disqualifying off-target effects.
  Answer required: honest limits section; no therapeutic claim beyond
  "candidate for experimental follow-up."
- **Objection 3 — shaky foundations:** 26% of CNR2 records are single-point %
  inhibition (quarantined) and EC50-heavy functional data is noisy; the
  reference set inherits that noise. Answer required: sensitivity analysis —
  re-run ranking with Tier A restricted to Ki-only records and check rank
  stability.
- Adversary: a second model pass over the top-10 dossiers arguing each one
  is wrong, plus Jake's review. Two AIs agreeing is weak evidence (shared
  failure modes); the pre-committed falsification criteria above are the
  stronger check.

## Kill criteria for this bet

- Cleaned quantitative CNR2 records < 2,000 after dedupe → data basis too thin.
- Tier A < 25 selective ligands → selectivity basis does not exist.
- Zero hits above threshold → publish the negative result honestly or kill.
- Novelty collapse (falsification 1) → kill; the screen adds nothing.
- Any single blocker unfixable in one week → pause, don't spiral.

## Phase 2b (docking, not built yet)

Viable: three CB2 structures verified in the PDB 2026-09-15 —
5ZTY (X-ray 2.8 Å, antagonist-bound), 6KPC (X-ray 3.2 Å, agonist-bound),
6PT0 (cryo-EM 3.2 Å, CB2–Gi agonist complex). Docking the hits against the
agonist- vs antagonist-bound pockets would test functional-direction
blindness (red-team objection 1). Build only if the ligand-based screen
produces hits worth the compute.

## Review decisions — 2026-09-15 (Jake)

The pre-registration above was reviewed before any ranking run. Decisions:

1. **Threshold strictness:** an honest-zero outcome is acceptable and publishable
   as a negative result. The 0.25 / 0.40 bar stands; it will not be lowered
   after seeing results to manufacture hits.
2. **Agonist/antagonist blindness:** ACCEPTED for the ligand screen, by agent
   judgment (Jake delegated). Rationale: annotating ~1,400 Tier A ligands for
   functional direction from ChEMBL assay text is noisy — many records are
   binding-only with no functional readout, and assay descriptions do not
   reliably encode direction. The screen's job is a shortlist; functional
   direction gets adjudicated in Phase 2b docking (agonist-bound 6KPC/6PT0 vs
   antagonist-bound 5ZTY) on surviving hits only. Recorded as a limitation.
3. **Tier B inclusion:** Tier A stays PURE for the primary metric, by agent
   judgment (Jake delegated). Rationale: selectivity over CB1 is the
   load-bearing claim of this screen; folding in 1,014 ligands of unknown CB1
   activity dilutes exactly what makes the result worth trusting. Tier B
   similarity is reported as a secondary annotation column on hits (supporting
   breadth, not primary evidence).

Full ranking run authorized as of this review.

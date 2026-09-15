# Decision log

Human decisions only. The agent proposes; Jake disposes. Newest first.

## 2026-09-15 — Program approved

Jake approved the Frontier Screen program: agent-executed, Jake-decided.
Bet 1 = drug-repurposing screen (this repo). Bet 2 (background) = open EEG/BCI.
Bet 3 (reserve) = acupuncture evidence-gap map. Priority logic: legibility first,
distinctiveness second, controversy only from strength.

## 2026-09-15 — Target selected: CNR2

Jake picked CNR2 (cannabinoid CB2 receptor, CHEMBL253) from the curated five.
Central design constraint: CB1 selectivity is the entire game — the screen must
rank CB2 activity AND CB1 inactivity, or the hits are worthless. Phase 2 builds
the pipeline + pre-registration; no ranking runs until Jake reviews the pre-reg.

## 2026-09-15 — Phase 2 pipeline built (pre-reg review pending)

Agent built the full CNR2 pipeline: 01_pull_data.py (ChEMBL pull, cached, manifest),
02_clean_data.py (pChEMBL standardization, %inhibition quarantined, dedupe by
molecule x type), 03_screen.py (Morgan-fingerprint ligand screen). Cleaned data:
CNR2 22,523 -> 10,020 molecules; CB1 25,853 -> 9,366 molecules; 7,759 molecules
measured on both targets. Reference sets: Tier A 1,412 selective CB2 ligands,
Tier B 1,034, CB1-active counter set 4,352. Selectivity metric:
selectivity_score = maxTanimoto(TierA) - maxTanimoto(CB1-actives); hit requires
selectivity_score >= 0.25 AND S_cb2 >= 0.40. Full ranking run is gated behind
--i-have-reviewed-the-prereg: no ranking until Jake approves preregistration/CNR2.md.
Docking spike: 5ZTY / 6KPC / 6PT0 all verified as CB2 structures (Phase 2b, not built).

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

## 2026-09-15 — Pre-registration approved, full screen authorized

Jake reviewed preregistration/CNR2.md. Q1: honest-zero outcome acceptable,
publishable as negative result; thresholds stand. Q2/Q3 delegated to agent
judgment: (a) accept agonist/antagonist blindness in the ligand screen, resolve
via Phase 2b docking on hits; (b) Tier A pure for primary metric, Tier B as
secondary annotation. Full 4,225-drug ranking authorized; runs in the agent VM
(CPU-cheap). Local PC env (conda blocked by Codex policy) deferred — only
needed for Phase 2b docking.

## 2026-09-15 — Full CNR2 screen complete: 0 hits (honest zero)

3,417 approved drugs scored, 0 hits against the pre-registered bar
(selectivity >= 0.25 and S_cb2 >= 0.40). Clean zero: top score 0.139, no
near-misses at the threshold. 808 drugs excluded as out-of-scope (biologics,
inorganics). Bicalutamide cleared the similarity floor but failed selectivity —
the failure mode the screen was built to catch. Run summary: RUN_SUMMARY.md.
Disposition (publish negative result vs pivot) is Jake's call per the
pre-registered kill criteria.

## 2026-09-15 — Jake: publish the honest zero

Disposition decided: write up the CNR2 negative result as a preprint.
Jake's framing: the purpose is not publicity, it is to do the work well so the
same machine can be re-run for other targets. The preprint + repo become the
reusable template. Next target candidate: MCHR1 (cleanest data in the scout).

## 2026-09-15 — Manuscript approved; independent QA commissioned

Jacob approved the CNR2 preprint draft ("good as is"). Manuscript committed to
manuscript/CNR2-preprint.md. bioRxiv posting is Jacob's action (needs his
account). A fresh, previously-uninvolved subagent is now doing an independent
QA pass: full pipeline reproduction from the repo, number verification against
the manuscript, pre-reg freeze-timing check via git history, adversarial
methods review, reference checks. It reports flaws; it does not fix. Next
targets (MCHR1 etc.) wait on a clear QA.

## 2026-09-15 — MCHR1 target started; pipeline parameterized

Second mining attempt: MCHR1 (CHEMBL344) with hERG (CHEMBL240, KCNH2) as the
counter-target — hERG cardiotoxicity was the documented killer of the MCHR1
antagonist programs, so selectivity over hERG is this screen's entire point,
mirroring the CNR2/CB1 structure. MCHR2 (sibling receptor) considered and
rejected: 307 ChEMBL records, too thin for a pre-registered selectivity
metric. Pipeline scripts now take --target with settings in targets/*.json;
targets/CNR2.json is frozen and reproduces the committed CNR2 result exactly
(verified: config equals original constants; loose inactivity rule identical
on truth table). The CNR2 QA fix is now the machine default: a '>' record
counts as counter-inactive only if its reported bound clears the bar
(targets/MCHR1.json: loose_gt_inactivity=false). Pre-registration drafted at
preregistration/MCHR1.md — DRAFT, awaiting human review; the ranking gate is
closed until then. Pilot (100 drugs) passes end to end: Tier A = 71 hERG-clean
MCHR1 ligands (kill threshold: 25), Tier B = 2,137, hERG-active set = 2,441.
Pull counts: MCHR1 6,037 / hERG 41,078 / approved drugs 4,225. Added retry
with backoff to the ChEMBL puller after a proxy drop killed the first hERG
pull. Full ranking NOT run — gated on pre-reg review.
## 2026-09-16 — QA remediation complete: M1 sensitivity analysis confirms the zero; manuscript fixed (1 major + 8 minor)

Independent QA (2026-09-15) returned CLEAR with 1 major + 8 minor findings and
reproduced the full pipeline exactly. All findings addressed:

- **Major M1 (Tier A ">"-bound weakness):** the frozen primary result is
  unchanged (1,412 / pre-registered rule intact). Added a documented post-hoc
  sensitivity mode (`scripts/04_sensitivity_tierA_tightened.py`) where a CB1
  ">" record counts only if its bound is itself <= 5.0 pChEMBL. Tightened Tier A
  = 1,263 (149 dropped, bounds 5.25-8.82); re-run on the full 3,417-drug
  library: 0 hits, max selectivity 0.1394, nothing near the 0.25 bar, no score
  increased vs the frozen primary. Outputs under
  `results/sensitivity_tierA_tightened/`. Manuscript carries the M1 disclosure
  in Limitations and a Results paragraph on the sensitivity check. Tightened
  rule adopted for future screens.
- **Minor fixes:** review gate described accurately (CLI attestation flag
  `--i-have-reviewed-the-prereg`, auditable via git chronology); 100-drug
  pre-threshold pilot disclosed; refs corrected (Spiera vol/pages + DOI,
  Haymer full 16-author list, Li scoped to the CB2 structure, new ref 6:
  Topol et al. Lancet 2010 CRESCENDO for rimonabant); stale draft header
  refreshed to author-approved preprint status; "re-pulls deterministically"
  replaced with honest live-database language; internal open-questions section
  removed from the preprint body (resolutions preserved in git history).
- Fresh data pull re-verified determinism: CNR2 22,523 / CB1 25,853 /
  approved 4,225 (one transient ChEMBL read timeout on CB1, succeeded on
  retry). Commits follow; bioRxiv posting still requires Jacob's account.

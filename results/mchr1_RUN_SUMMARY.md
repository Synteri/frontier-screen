# MCHR1 screen — run summary

Date: 2026-09-15 (run completed ~01:35 UTC 2026-09-16)
Pre-registration: `preregistration/MCHR1.md` — review recorded 2026-09-15
(Q1 answered by Jacob Schumacher directly; Q2–Q5 adjudicated by specialist
review with confidence grades and citations). Thresholds frozen before the run:
selectivity_score >= 0.25 AND S_mchr1 >= 0.40, carried over from CNR2 unchanged.
Review commit pushed before the ranking run; the
`--i-have-reviewed-the-prereg` gate was satisfied legitimately.

## Data basis

- MCHR1 (CHEMBL344): 6,037 ChEMBL activity records pulled; 4,079 molecules
  after cleaning/dedupe.
- hERG (CHEMBL240): 41,078 records pulled; 16,217 molecules after cleaning.
- Approved-drug library: 4,225 records pulled (max_phase=4), 3,417 with
  usable structures scored (same library definition as CNR2).
- Pull manifest: `data/manifest_mchr1.json`. Data-quality report:
  `data_quality_report_mchr1.md`.

## Reference sets (tightened ">" rule — machine default since the CNR2 QA)

- Tier A (MCHR1 pChEMBL >= 7 '=', measured hERG inactivity): **71**
- Tier B (MCHR1-active, hERG untested): 2,137
- hERG-active counter set (pChEMBL >= 6 '='): 2,441
- Kill threshold for Tier A was 25 — the selectivity basis exists (71 > 25).

## Result: 0 hits — honest zero

- 3,417 approved drugs scored. **Hits: 0.**
- Highest selectivity score: **0.1309** (vildagliptin; S_mchr1 0.3086,
  S_herg 0.1778) — well separated from the 0.25 bar.
- **No drug cleared even the S_mchr1 >= 0.40 similarity floor** (cf. CNR2,
  where bicalutamide cleared the floor but failed selectivity). Nothing
  within 0.05 of the threshold.
- Top of the ranking is a coherent chemical series (gliptins: vildagliptin,
  saxagliptin — DPP-4 inhibitors), i.e. the metric resolves chemotypes, but
  at 0.13 it is nowhere near hit territory. The metric is not degenerate;
  there is simply nothing in the hit zone.
- Full ranking: `results/mchr1_screen_hits.csv` (3,417 rows).

## Falsification checks (from the pre-registration)

1. Novelty collapse: n/a — no hits to check.
2. Thin reference basis: Tier A = 71 ≥ 25 — basis exists.
3. Scaffold collapse: n/a — no hits.
4. Selectivity illusion: n/a — no hits.
5. hERG contradiction: n/a — no hits.

## Interpretation (scoped)

Under the pre-registered ligand-based method, no approved drug sufficiently
resembled the known hERG-clean MCHR1 antagonist chemotypes to justify
progression. This is not proof that no approved drug has MCHR1 activity:
ligand similarity can miss genuinely active chemotypes unlike the reference
set (the CNR2 manuscript documents exactly such a case), the screen is
agonist/antagonist-blind by design (accepted limitation, Q4), and hERG
distance is not a cardiac safety certificate (red-team objection 2).
Phase 2b docking is not triggered (no hits).

Reproduce: `python scripts/03_screen.py --target MCHR1 --i-have-reviewed-the-prereg`
(requires the review recorded in `preregistration/MCHR1.md`).

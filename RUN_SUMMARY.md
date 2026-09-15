# CNR2 full-screen run summary — 2026-09-15

## Result: 0 hits (honest zero, pre-committed as publishable)

- Approved drugs pulled: 4,225. Scored: 3,417.
- 808 excluded, all legitimately out of scope for a fingerprint screen:
  proteins (178), antibodies (150), vaccines, enzymes, oligonucleotides,
  cells/genes, and inorganics/organometallics with no meaningful SMILES
  (cisplatin, oxaliplatin, copper, bismuth subsalicylate...).
- Hit bar (pre-registered, unchanged): selectivity_score >= 0.25 AND S_cb2 >= 0.40.
- **Hits: 0.** Top selectivity_score: 0.139 (ioversol). Only one drug cleared
  even the S_cb2 floor — bicalutamide (S_cb2 0.4219) — and it failed selectivity
  (0.1111), the exact failure mode this screen was built to catch.

## Why the zero is trustworthy (not a broken metric)

- Clean separation: top score 0.139 vs 0.25 bar. No near-misses clustered at
  the threshold. This is a clean zero, not a borderline one.
- Metric behaves sanely: S_cb2 spans 0–0.42 across the drug set; reference-set
  self-similarity is 1.0 by construction. The screen can see; there is just
  nothing in the hit zone.
- Consistent with field history: no selective CB2 agonist is approved anywhere.
  A hit would have been the surprising result, not the zero.
- Top-ranked cluster is iodinated X-ray contrast agents (ioversol, iodixanol,
  iohexol, iomeprol) — a chemotype artifact, and IV-only diagnostics, not
  repurposing candidates. Noted, not chased.

## Limitations (as pre-registered)

- Ligand-based only; functional direction (agonist vs antagonist) invisible.
- Tier B ligands excluded from primary metric (secondary column only).
- Similarity != activity; approved-drug chemical space may simply lack
  CB2-selective chemotypes — which is itself a finding.
- Structure-based docking (PDB 5ZTY/6KPC/6PT0) deferred to Phase 2b; an
  orthogonal method could in principle find what similarity missed.

## Disposition

Per pre-registered kill criteria and Jake's 2026-09-15 review: honest zero is
publishable as a negative result. Publish-vs-pivot is Jake's call.

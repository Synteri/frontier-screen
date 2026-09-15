# Frontier Screen

Bet 1 of the Frontier Screen program: a drug-repurposing screen on public data,
built to be real science and a real work sample at the same time.

**Thesis:** approved drugs, new uses. Public databases (ChEMBL, PubChem) describe
what every approved drug looks like chemically. Pick a neglected disease target,
rank existing drugs by predicted activity against it, verify novelty, write it up.

## Operating model

Agent-executed, human-decided. The agent builds the pipeline, pulls the data, runs
the analysis, and drafts the write-up. Jake makes the decisions that need judgment:
target selection, kill calls, authorship approval. Every decision lands in
`DECISIONS.md` with a date.

## Quickstart (Windows PC with NVIDIA GPU)

```powershell
# 1. Create the environment (conda or mamba)
conda env create -f environment.yml
conda activate frontier-screen

# 2. Smoke test: verifies GPU, torch, rdkit
python scripts/00_smoke_test.py

# 3. Full pipeline (after Phase 1 target selection)
.\run.ps1
```

## Layout

- `scripts/` — the pipeline, numbered in run order
- `preregistration/` — what counts as a hit, what would disprove it, novelty-check
  procedure. Written BEFORE the screen runs. Non-negotiable.
- `candidates/` — ranked candidate dossiers
- `results/` — raw and processed outputs (committed back after local runs)
- `DECISIONS.md` — the human decision log

## Status

- [x] Phase 0: repo + environment + smoke test
- [ ] Phase 1: target selection (human picks from agent-researched shortlist)
- [ ] Phase 2: pipeline build + pre-registration
- [ ] Phase 3: run, novelty check, red-team
- [ ] Phase 4: preprint + reproducibility package
- [ ] Phase 5: ship

## Disclosure

Built with AI assistance (Muse, an AI agent). That assistance is disclosed in any
preprint or publication arising from this work, per the operator's standing rule.

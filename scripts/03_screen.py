#!/usr/bin/env python3
"""03_screen.py — ligand-based repurposing screen for selective CB2 ligands.

Usage:
    python scripts/03_screen.py [--max-drugs N] [--i-have-reviewed-the-prereg]

THE SELECTIVITY METRIC (read this before trusting any hit):
  S_cb2  = max Tanimoto similarity of the candidate to the Tier-A reference
           set (selective CB2 ligands defined below).
  S_cb1  = max Tanimoto similarity of the candidate to the CB1-active set
           (molecules with measured CB1 pChEMBL >= 6).
  selectivity_score = S_cb2 - S_cb1            # in [-1, 1]

  Rationale: a repurposing candidate should sit NEAR known selective-CB2
  chemotypes and FAR from CB1-active chemotypes. A plain CB2-similarity
  screen would happily return non-selective cannabinoids — the exact
  failure mode this program exists to avoid (CB1 activity = psychoactive
  liability, the reason the field is littered with dead programs).

  A hit additionally requires S_cb2 >= 0.40: the candidate must genuinely
  resemble a selective CB2 ligand, not merely be dissimilar to CB1 ligands
  (a random molecule scores ~0 on both, giving a vacuous score near 0).

REFERENCE SETS (built from data/clean/*.csv):
  Tier A (selective CB2 ligands): CNR2 pChEMBL >= 7 with relation '=' AND
      measured CB1 inactivity, defined as (CB1 relation '=' and pChEMBL < 5)
      or (CB1 relation '>' — i.e. the true value is weaker than reported).
      This is the empirical selectivity basis; it only exists because some
      molecules were tested on BOTH targets.
  Tier B (CB2-active, CB1 untested): CNR2 pChEMBL >= 7, relation '=', no CB1
      record at all. Reported as a secondary column (S_cb2_tierB) and
      flagged — similarity here is suggestive, not selectivity evidence.
  CB1-active set: CB1 pChEMBL >= 6, relation '=', for the counter-similarity.

GATE: the full approved-drug library runs ONLY with
  --i-have-reviewed-the-prereg  (Jake's sign-off on preregistration/CNR2.md).
Without it, --max-drugs N runs a logic test on the first N drugs. This is
deliberate: no ranking run happens before human review.

Fingerprints: Morgan radius 2, 2048 bits (rdkit). Tanimoto via DataStructs.
"""
import argparse
import json
import os
import sys

import pandas as pd

CLEAN = os.path.join("data", "clean")
RAW = os.path.join("data", "raw")
RESULTS = "results"

TIER_A_CB2_MIN = 7.0   # pChEMBL >= 7  <=>  Ki/IC50 <= 100 nM on CB2
TIER_A_CB1_MAX = 5.0   # pChEMBL < 5   <=>  weaker than 10 uM on CB1
CB1_ACTIVE_MIN = 6.0   # pChEMBL >= 6  <=>  <= 1 uM on CB1
HIT_S_CB2_MIN = 0.40
HIT_SELECTIVITY_MIN = 0.25


def cb1_inactive(row):
    """Measured evidence the molecule is weak/inactive at CB1."""
    if row["relation"] == "=" and row["pchembl"] < TIER_A_CB1_MAX:
        return True
    if row["relation"] == ">":
        # true value weaker than reported -> inactive at the reported level
        return True
    return False


def _morgan_gen():
    """MorganGenerator (modern API), falling back to the legacy function."""
    try:
        from rdkit.Chem import rdFingerprintGenerator
        gen = rdFingerprintGenerator.GetMorganGenerator(radius=2, fpSize=2048)
        return gen.GetFingerprint
    except ImportError:
        from rdkit.Chem import AllChem

        def legacy(mol):
            return AllChem.GetMorganFingerprintAsBitVect(mol, 2, nBits=2048)

        return legacy


def fps_for(df, col="smiles"):
    from rdkit import Chem
    fp_fn = _morgan_gen()
    fps, ids, bad = [], [], 0
    for _, r in df.iterrows():
        m = Chem.MolFromSmiles(r[col]) if isinstance(r[col], str) else None
        if m is None:
            bad += 1
            continue
        fps.append(fp_fn(m))
        ids.append(r["molecule_chembl_id"])
    return fps, ids, bad


def build_reference_sets():
    cnr2 = pd.read_csv(os.path.join(CLEAN, "cnr2_clean.csv"))
    cb1 = pd.read_csv(os.path.join(CLEAN, "cb1_clean.csv"))
    cb1_by_mol = {r["molecule_chembl_id"]: r for _, r in cb1.iterrows()}

    tier_a, tier_b = [], []
    for _, r in cnr2.iterrows():
        if not (r["relation"] == "=" and r["pchembl"] >= TIER_A_CB2_MIN):
            continue
        mid = r["molecule_chembl_id"]
        c1 = cb1_by_mol.get(mid)
        if c1 is not None and cb1_inactive(c1):
            tier_a.append(r)
        elif c1 is None:
            tier_b.append(r)
    tier_a = pd.DataFrame(tier_a)
    tier_b = pd.DataFrame(tier_b)

    cb1_active = cb1[(cb1["relation"] == "=") &
                    (cb1["pchembl"] >= CB1_ACTIVE_MIN)]
    return tier_a, tier_b, cb1_active


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--max-drugs", type=int, default=None,
                    help="test mode: screen only the first N approved drugs")
    ap.add_argument("--i-have-reviewed-the-prereg", action="store_true",
                    help="required for a full-library run")
    args = ap.parse_args()

    full_run = args.max_drugs is None
    if full_run and not args.i_have_reviewed_the_prereg:
        print("REFUSED: full-library ranking requires "
              "--i-have-reviewed-the-prereg\n"
              "(Jake's sign-off on preregistration/CNR2.md). "
              "Use --max-drugs N for a logic test.")
        return 2

    from rdkit import DataStructs

    tier_a, tier_b, cb1_active = build_reference_sets()
    print(f"[ref] Tier A selective CB2 ligands: {len(tier_a)}")
    print(f"[ref] Tier B CB2-active/CB1-untested: {len(tier_b)}")
    print(f"[ref] CB1-active counter set: {len(cb1_active)}")
    if len(tier_a) == 0:
        print("REFUSED: empty Tier A — the selectivity basis does not exist. "
              "See pre-reg kill criteria.")
        return 3

    ref_a_fp, _, bad_a = fps_for(tier_a)
    ref_b_fp, _, bad_b = fps_for(tier_b)
    cb1_fp, _, bad_c = fps_for(cb1_active)
    print(f"[fp] unparseable SMILES skipped: A={bad_a} B={bad_b} CB1={bad_c}")

    drugs = json.load(open(os.path.join(RAW, "approved_drugs.json")))
    drugs = [d for d in drugs if d.get("canonical_smiles")]
    if args.max_drugs:
        drugs = drugs[:args.max_drugs]
    print(f"[screen] {len(drugs)} approved drugs "
          f"({'TEST MODE' if args.max_drugs else 'FULL RUN'})")

    from rdkit import Chem
    fp_fn = _morgan_gen()
    rows = []
    for d in drugs:
        m = Chem.MolFromSmiles(d["canonical_smiles"])
        if m is None:
            continue
        fp = fp_fn(m)
        s_cb2 = max(DataStructs.TanimotoSimilarity(fp, r) for r in ref_a_fp)
        s_cb2_b = max([DataStructs.TanimotoSimilarity(fp, r)
                       for r in ref_b_fp] or [0.0])
        s_cb1 = max(DataStructs.TanimotoSimilarity(fp, r) for r in cb1_fp)
        sel = s_cb2 - s_cb1
        rows.append({
            "molecule_chembl_id": d["molecule_chembl_id"],
            "pref_name": d.get("pref_name"),
            "S_cb2": round(s_cb2, 4),
            "S_cb2_tierB": round(s_cb2_b, 4),
            "S_cb1": round(s_cb1, 4),
            "selectivity_score": round(sel, 4),
            "hit": bool(s_cb2 >= HIT_S_CB2_MIN
                        and sel >= HIT_SELECTIVITY_MIN),
        })

    out = pd.DataFrame(rows).sort_values("selectivity_score", ascending=False)
    os.makedirs(RESULTS, exist_ok=True)
    fname = ("screen_hits.csv" if full_run else "screen_test.csv")
    out.to_csv(os.path.join(RESULTS, fname), index=False)
    hits = out[out["hit"]]
    print(f"[done] {len(out)} scored, {len(hits)} hits -> results/{fname}")
    if len(hits):
        print(hits[["pref_name", "molecule_chembl_id",
                     "S_cb2", "S_cb1", "selectivity_score"]]
              .head(10).to_string(index=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())

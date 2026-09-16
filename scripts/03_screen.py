#!/usr/bin/env python3
"""03_screen.py — ligand-based repurposing screen with a counter-target selectivity metric.

Usage:
    python scripts/03_screen.py [--target CNR2] [--max-drugs N]
        [--i-have-reviewed-the-prereg]

Target settings (ChEMBL IDs, thresholds, file names, score column labels)
come from targets/<TARGET>.json. Default --target CNR2 reproduces the
original committed screen exactly.

THE SELECTIVITY METRIC (read this before trusting any hit):
  S_target   = max Tanimoto similarity of the candidate to the Tier-A
               reference set (target-active ligands with measured
               counter-target inactivity, defined below).
  S_counter  = max Tanimoto similarity of the candidate to the
               counter-active set (molecules with measured counter-target
               pChEMBL >= counter_active_min).
  selectivity_score = S_target - S_counter            # in [-1, 1]

  Rationale: a repurposing candidate should sit NEAR known target-active
  chemotypes and FAR from the chemotypes that carry the field's known
  failure mode. For CNR2 the failure mode was CB1 psychoactivity; for
  MCHR1 it is hERG cardiotoxicity (the documented killer of the MCHR1
  antagonist programs). A plain target-similarity screen would happily
  return candidates carrying exactly the liability the program exists
  to avoid.

  A hit additionally requires S_target >= hit_s_target_min: the candidate
  must genuinely resemble a target-active ligand, not merely be dissimilar
  to counter-active chemotypes (a random molecule scores ~0 on both,
  giving a vacuous score near 0).

REFERENCE SETS (built from data/clean/*.csv):
  Tier A (selective target ligands): target pChEMBL >= tier_a_target_min
      with relation '=' AND measured counter-target inactivity, defined as
      (counter relation '=' and pChEMBL < tier_a_counter_max) or
      (counter relation '>' whose reported bound clears tier_a_counter_max
      — the tightened rule; the original CNR2 config keeps the legacy
      loose '>' rule via loose_gt_inactivity=true to reproduce its
      committed result exactly).
      This is the empirical selectivity basis; it only exists because some
      molecules were tested on BOTH targets.
  Tier B (target-active, counter untested): target pChEMBL >=
      tier_a_target_min, relation '=', no counter-target record at all.
      Reported as a secondary column and flagged — similarity here is
      suggestive, not selectivity evidence.
  Counter-active set: counter pChEMBL >= counter_active_min, relation '=',
      for the counter-similarity.

GATE: the full approved-drug library runs ONLY with
  --i-have-reviewed-the-prereg  (the human's sign-off on the target's
  preregistration file, named in targets/<TARGET>.json).
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


def load_target_config(name):
    """Target settings live in targets/<TARGET>.json (stdlib json, no yaml dep)."""
    path = os.path.join("targets", f"{name}.json")
    with open(path) as f:
        return json.load(f)


def counter_inactive(row, cfg):
    """Measured evidence the molecule is weak/inactive at the counter-target.

    Tightened rule (default): a '>' relation record counts only if its
    reported bound itself clears the inactivity bar — i.e. the experiment
    actually tested a concentration weaker than the bar, so the bound is
    informative. (A record like '>2 nM' says nothing about inactivity at
    the 10 uM bar and is excluded.)
    Legacy rule (CNR2 config only, to reproduce the committed result):
    any '>' record counts.
    """
    bar = cfg["tier_a_counter_max"]
    if row["relation"] == "=" and row["pchembl"] < bar:
        return True
    if row["relation"] == ">":
        if cfg["loose_gt_inactivity"]:
            # true value weaker than reported -> inactive at the reported level
            return True
        return row["pchembl"] < bar
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


def build_reference_sets(cfg):
    tkey, ckey = cfg["target_key"], cfg["counter_key"]
    tdf = pd.read_csv(os.path.join(CLEAN, f"{tkey.lower()}_clean.csv"))
    cdf = pd.read_csv(os.path.join(CLEAN, f"{ckey.lower()}_clean.csv"))
    counter_by_mol = {r["molecule_chembl_id"]: r for _, r in cdf.iterrows()}

    tier_a, tier_b = [], []
    for _, r in tdf.iterrows():
        if not (r["relation"] == "="
                and r["pchembl"] >= cfg["tier_a_target_min"]):
            continue
        mid = r["molecule_chembl_id"]
        c1 = counter_by_mol.get(mid)
        if c1 is not None and counter_inactive(c1, cfg):
            tier_a.append(r)
        elif c1 is None:
            tier_b.append(r)
    tier_a = pd.DataFrame(tier_a)
    tier_b = pd.DataFrame(tier_b)

    counter_active = cdf[(cdf["relation"] == "=") &
                         (cdf["pchembl"] >= cfg["counter_active_min"])]
    return tier_a, tier_b, counter_active


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--target", default="CNR2",
                    help="target config in targets/<TARGET>.json")
    ap.add_argument("--max-drugs", type=int, default=None,
                    help="test mode: screen only the first N approved drugs")
    ap.add_argument("--i-have-reviewed-the-prereg", action="store_true",
                    help="required for a full-library run")
    args = ap.parse_args()
    cfg = load_target_config(args.target)
    tkey, ckey = cfg["target_key"], cfg["counter_key"]

    full_run = args.max_drugs is None
    if full_run and not args.i_have_reviewed_the_prereg:
        print("REFUSED: full-library ranking requires "
              "--i-have-reviewed-the-prereg\n"
              f"(human sign-off on {cfg['prereg_file']}). "
              "Use --max-drugs N for a logic test.")
        return 2

    from rdkit import DataStructs

    tier_a, tier_b, counter_active = build_reference_sets(cfg)
    print(f"[ref] Tier A selective {tkey} ligands: {len(tier_a)}")
    print(f"[ref] Tier B {tkey}-active/{ckey}-untested: {len(tier_b)}")
    print(f"[ref] {ckey}-active counter set: {len(counter_active)}")
    if len(tier_a) == 0:
        print("REFUSED: empty Tier A — the selectivity basis does not exist. "
              "See pre-reg kill criteria.")
        return 3

    ref_a_fp, _, bad_a = fps_for(tier_a)
    ref_b_fp, _, bad_b = fps_for(tier_b)
    counter_fp, _, bad_c = fps_for(counter_active)
    print(f"[fp] unparseable SMILES skipped: A={bad_a} B={bad_b} "
          f"counter={bad_c}")

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
        s_t = max(DataStructs.TanimotoSimilarity(fp, r) for r in ref_a_fp)
        s_t_b = max([DataStructs.TanimotoSimilarity(fp, r)
                     for r in ref_b_fp] or [0.0])
        s_c = max(DataStructs.TanimotoSimilarity(fp, r) for r in counter_fp)
        sel = s_t - s_c
        rows.append({
            "molecule_chembl_id": d["molecule_chembl_id"],
            "pref_name": d.get("pref_name"),
            cfg["score_col_target"]: round(s_t, 4),
            cfg["score_col_target_tierb"]: round(s_t_b, 4),
            cfg["score_col_counter"]: round(s_c, 4),
            "selectivity_score": round(sel, 4),
            "hit": bool(s_t >= cfg["hit_s_target_min"]
                        and sel >= cfg["hit_selectivity_min"]),
        })

    out = pd.DataFrame(rows).sort_values("selectivity_score", ascending=False)
    os.makedirs(RESULTS, exist_ok=True)
    fname = (cfg["results_hits_file"] if full_run else cfg["results_test_file"])
    out.to_csv(os.path.join(RESULTS, fname), index=False)
    hits = out[out["hit"]]
    print(f"[done] {len(out)} scored, {len(hits)} hits -> results/{fname}")
    if len(hits):
        print(hits[["pref_name", "molecule_chembl_id",
                     cfg["score_col_target"], cfg["score_col_counter"],
                     "selectivity_score"]]
              .head(10).to_string(index=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())

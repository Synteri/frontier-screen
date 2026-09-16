#!/usr/bin/env python3
"""04_sensitivity_tierA_tightened.py — POST-HOC SENSITIVITY ANALYSIS.

This is NOT the pre-registered screen. It is a byte-for-byte copy of
scripts/03_screen.py with ONE rule changed, run after an independent QA
audit (2026-09-15) found that the Tier A "CB1 inactivity" rule admitted
CB1 ">"-relation records whose reported bound sits ABOVE the pre-reg's
own pChEMBL < 5 inactivity bar (149 of 1,412 members; 5 on vacuous bounds
like ">50 nM"). A ">" record with bound pChEMBL = 7 only proves the true
value is weaker than 7 — it does not establish pChEMBL < 5.

The tightened rule: a CB1 ">" record counts as inactivity evidence only
if its reported bound is itself <= 5.0 (weaker than 10 uM), which is what
actually establishes the claimed bar.

The original frozen result (scripts/03_screen.py, results/screen_hits.csv)
is untouched and remains primary. Removing reference members can only
LOWER S_cb2 scores (max over a smaller set), so the zero is mathematically
robust to this tightening — this run confirms it empirically.

Usage:
    python scripts/04_sensitivity_tierA_tightened.py --i-have-reviewed-the-prereg
"""

import argparse
import json
import os
import sys

import pandas as pd

CLEAN = os.path.join("data", "clean")
RAW = os.path.join("data", "raw")
RESULTS = os.path.join("results", "sensitivity_tierA_tightened")

TIER_A_CB2_MIN = 7.0   # pChEMBL >= 7  <=>  Ki/IC50 <= 100 nM on CB2
TIER_A_CB1_MAX = 5.0   # pChEMBL < 5   <=>  weaker than 10 uM on CB1
CB1_ACTIVE_MIN = 6.0   # pChEMBL >= 6  <=>  <= 1 uM on CB1
HIT_S_CB2_MIN = 0.40
HIT_SELECTIVITY_MIN = 0.25


def cb1_inactive(row):
    """Measured evidence the molecule is weak/inactive at CB1 (TIGHTENED).

    Change vs the pre-registered rule: a ">" record only counts when the
    reported bound itself clears the bar (bound pChEMBL <= 5.0), because
    only then does "true value weaker than reported" imply pChEMBL < 5.
    """
    if row["relation"] == "=" and row["pchembl"] < TIER_A_CB1_MAX:
        return True
    if row["relation"] == ">" and row["pchembl"] <= TIER_A_CB1_MAX:
        # true value weaker than a bound that is itself <= 5.0
        # -> true pChEMBL < 5 established
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


def cb1_inactive_original(row):
    """The PRE-REGISTERED rule (frozen primary analysis), kept for diffing.

    Treated every '>' record as inactivity evidence regardless of bound.
    """
    if row["relation"] == "=" and row["pchembl"] < TIER_A_CB1_MAX:
        return True
    if row["relation"] == ">":
        return True
    return False


def build_reference_sets():
    cnr2 = pd.read_csv(os.path.join(CLEAN, "cnr2_clean.csv"))
    cb1 = pd.read_csv(os.path.join(CLEAN, "cb1_clean.csv"))
    cb1_by_mol = {r["molecule_chembl_id"]: r for _, r in cb1.iterrows()}

    tier_a, tier_b, dropped = [], [], []
    for _, r in cnr2.iterrows():
        if not (r["relation"] == "=" and r["pchembl"] >= TIER_A_CB2_MIN):
            continue
        mid = r["molecule_chembl_id"]
        c1 = cb1_by_mol.get(mid)
        if c1 is not None and cb1_inactive(c1):
            tier_a.append(r)
        elif c1 is not None and cb1_inactive_original(c1):
            # CB1-tested: counted under the pre-registered rule, dropped by
            # the tightening (a '>' record whose bound does not clear the
            # pChEMBL < 5 bar)
            dropped.append({"molecule_chembl_id": mid,
                            "cb1_relation": c1["relation"],
                            "cb1_pchembl_bound": c1["pchembl"]})
        elif c1 is None:
            tier_b.append(r)
    tier_a = pd.DataFrame(tier_a)
    tier_b = pd.DataFrame(tier_b)

    cb1_active = cb1[(cb1["relation"] == "=") &
                    (cb1["pchembl"] >= CB1_ACTIVE_MIN)]
    return tier_a, tier_b, cb1_active, pd.DataFrame(dropped)


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

    tier_a, tier_b, cb1_active, dropped = build_reference_sets()
    print(f"[ref] Tier A selective CB2 ligands (tightened): {len(tier_a)}")
    print(f"[ref] Tier B CB2-active/CB1-untested: {len(tier_b)}")
    print(f"[ref] CB1-active counter set: {len(cb1_active)}")
    print(f"[ref] Tier A members dropped by tightening: {len(dropped)}")
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
    fname = ("screen_hits_tierA_tightened.csv" if full_run
             else "screen_test_tierA_tightened.csv")
    out.to_csv(os.path.join(RESULTS, fname), index=False)
    dropped.to_csv(os.path.join(RESULTS, "tierA_dropped_members.csv"),
                   index=False)
    hits = out[out["hit"]]
    print(f"[done] {len(out)} scored, {len(hits)} hits -> {RESULTS}/{fname}")
    if len(hits):
        print(hits[["pref_name", "molecule_chembl_id",
                     "S_cb2", "S_cb1", "selectivity_score"]]
              .head(10).to_string(index=False))
    # sensitivity summary for the manuscript
    top = out.head(10)[["pref_name", "S_cb2", "S_cb1", "selectivity_score"]]
    summary = {
        "tierA_tightened_n": int(len(tier_a)),
        "tierA_dropped_n": int(len(dropped)),
        "drugs_scored": int(len(out)),
        "hits": int(len(hits)),
        "max_selectivity_score": float(out["selectivity_score"].max()),
        "max_S_cb2": float(out["S_cb2"].max()),
        "top10": top.to_dict("records"),
    }
    with open(os.path.join(RESULTS, "summary.json"), "w") as f:
        json.dump(summary, f, indent=2)
    print(f"[done] summary -> {RESULTS}/summary.json")
    return 0


if __name__ == "__main__":
    sys.exit(main())

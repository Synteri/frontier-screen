#!/usr/bin/env python3
"""02_clean_data.py — clean ChEMBL bioactivity into ranking-ready tables.

Usage:
    python scripts/02_clean_data.py [--target CNR2]

Reads data/raw/*_activities.json, writes (names depend on the target config):
    data/clean/<target>_clean.csv      one row per (molecule, best assay type)
    data/clean/<counter>_clean.csv
    data/clean/quarantine.json      counts + reasons for excluded records
    data_quality_report*.md         counts before/after, by assay type (repo)

Cleaning rules (documented so a stranger can audit them):
  * Usable types: Ki, IC50, EC50, Kieq — standard_units must be nM.
    Kieq is treated as Ki-equivalent binding data.
  * pChEMBL = -log10(value in M). standard_relation is preserved:
      '='  exact value
      '<'  reported value is an UPPER bound  -> true pChEMBL >= reported
             (compound at least this potent; usable, flagged)
      '>'  reported value is a LOWER bound  -> true pChEMBL <= reported
             (compound at most this potent; weak evidence, flagged,
              excluded from the reference set)
  * QUARANTINE (excluded from ranking, counted in the report):
      - single-point % inhibition (standard_type 'Inhibition', units '%')
      - kinetic readouts (kon, k_off), thermal shift (Delta TM),
        fold-change (FC), ratio IC50, 'Activity' text, any non-nM units,
        null values, data_validity_comment indicating a curation problem.
  * DEDUPE (load-bearing — the Phase 1 scout found single kinetic-profiling
    papers inflating record counts): collapse to ONE value per
    (molecule_chembl_id, target, standard_type) via median of exact ('=')
    pChEMBL values; if no exact values exist, take the most potent bound.
    n_records and source document IDs are preserved in the output so the
    collapse is auditable. Per-document record counts are reported so a
    single-paper series dominating a target is visible.
  * Per (molecule, target) pick a single best value by type preference
    Ki > IC50 > EC50 > Kieq, keeping the type used in the output.
"""
import json
import math
import os
import sys
import argparse
from collections import Counter, defaultdict

import pandas as pd

RAW = os.path.join("data", "raw")
CLEAN = os.path.join("data", "clean")

USABLE_TYPES = {"Ki": 0, "IC50": 1, "EC50": 2, "Kieq": 3}  # preference order
QUARANTINE_TYPES = {"Inhibition", "kon", "k_off", "Delta TM", "FC",
                    "Ratio IC50", "Activity", "Potency", "Kd"}


def load_target_config(name):
    """Target settings live in targets/<TARGET>.json (stdlib json, no yaml dep)."""
    path = os.path.join("targets", f"{name}.json")
    with open(path) as f:
        return json.load(f)


def pchembl(value_nm):
    try:
        v = float(value_nm)
    except (TypeError, ValueError):
        return None
    if v <= 0:
        return None
    return -math.log10(v * 1e-9)


def classify(rec):
    """Return (status, reason). status in {'usable','quarantine'}."""
    stype = rec.get("standard_type")
    units = rec.get("standard_units")
    val = rec.get("standard_value")
    if stype in QUARANTINE_TYPES:
        return "quarantine", f"type={stype}"
    if stype not in USABLE_TYPES:
        return "quarantine", f"type={stype or 'null'}_unusable"
    if units != "nM":
        return "quarantine", f"units={units}"
    if val is None:
        return "quarantine", "null_value"
    if (rec.get("data_validity_comment") or "").lower().startswith("potential"):
        return "quarantine", "data_validity_flag"
    pc = pchembl(val)
    if pc is None:
        return "quarantine", "bad_value"
    return "usable", ""


def clean_target(name, target_id):
    path = os.path.join(RAW, f"{name.lower()}_activities.json")
    records = json.load(open(path))
    total = len(records)

    usable, quarantine = [], Counter()
    doc_counts = Counter()
    for rec in records:
        doc = rec.get("document_chembl_id") or "no_doc"
        doc_counts[doc] += 1
        status, reason = classify(rec)
        if status == "quarantine":
            quarantine[reason] += 1
            continue
        pc = pchembl(rec["standard_value"])
        usable.append({
            "molecule_chembl_id": rec.get("molecule_chembl_id"),
            "smiles": rec.get("canonical_smiles"),
            "standard_type": rec.get("standard_type"),
            "pchembl": round(pc, 3),
            "relation": rec.get("standard_relation") or "=",
            "assay_type": rec.get("assay_type"),  # B=binding, F=functional
            "assay_chembl_id": rec.get("assay_chembl_id"),
            "document_chembl_id": doc,
            "document_year": rec.get("document_year"),
            "target": name,
        })

    # Dedupe: one value per (molecule, standard_type); median of exact values.
    groups = defaultdict(list)
    for u in usable:
        groups[(u["molecule_chembl_id"], u["standard_type"])].append(u)

    deduped = []
    collapsed = 0
    for (mol, stype), rows in groups.items():
        exact = [r for r in rows if r["relation"] == "="]
        pool = exact if exact else rows
        # most potent bound wins when no exact value exists
        if exact:
            vals = sorted(r["pchembl"] for r in pool)
            best = vals[len(vals) // 2] if len(vals) % 2 else \
                (vals[len(vals) // 2 - 1] + vals[len(vals) // 2]) / 2
            rel = "="
        else:
            best = max(r["pchembl"] for r in pool)
            rel = min((r["relation"] for r in pool),
                      key=lambda x: {"<": 0, ">": 1}.get(x, 2))
        collapsed += len(rows) - 1
        smiles = next((r["smiles"] for r in rows if r["smiles"]), None)
        assay_types = sorted({r["assay_type"] for r in rows if r["assay_type"]})
        deduped.append({
            "molecule_chembl_id": mol,
            "smiles": smiles,
            "target": name,
            "standard_type": stype,
            "pchembl": round(best, 3),
            "relation": rel,
            "assay_types": ",".join(assay_types),
            "n_records": len(rows),
            "documents": ";".join(sorted(
                {r["document_chembl_id"] for r in rows})),
        })

    # One best value per molecule: type preference Ki > IC50 > EC50 > Kieq.
    by_mol = defaultdict(list)
    for d in deduped:
        by_mol[d["molecule_chembl_id"]].append(d)
    best_rows = []
    for mol, rows in by_mol.items():
        rows.sort(key=lambda r: USABLE_TYPES[r["standard_type"]])
        best_rows.append(rows[0])

    df = pd.DataFrame(best_rows)
    type_counts = Counter(r["standard_type"] for r in deduped)
    assay_counts = Counter()
    for r in deduped:
        for a in r["assay_types"].split(","):
            if a:
                assay_counts[a] += 1

    stats = {
        "target": name,
        "target_chembl_id": target_id,
        "raw_records": total,
        "usable_records": len(usable),
        "quarantined_records": int(sum(quarantine.values())),
        "quarantine_reasons": dict(quarantine),
        "deduped_mol_type_pairs": len(deduped),
        "collapsed_duplicates": collapsed,
        "final_molecules": len(best_rows),
        "by_standard_type": dict(type_counts),
        "by_assay_type": dict(assay_counts),
        "top_documents": [
            {"document_chembl_id": d, "records": c}
            for d, c in doc_counts.most_common(5)
        ],
    }
    return df, stats


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--target", default="CNR2",
                    help="target config in targets/<TARGET>.json")
    args = ap.parse_args()
    cfg = load_target_config(args.target)
    tkey, ckey = cfg["target_key"], cfg["counter_key"]

    os.makedirs(CLEAN, exist_ok=True)
    all_stats = {}
    for name, cid in [(tkey, cfg["target_chembl_id"]),
                      (ckey, cfg["counter_chembl_id"])]:
        print(f"[clean] {name}")
        df, stats = clean_target(name, cid)
        out = os.path.join(CLEAN, f"{name.lower()}_clean.csv")
        df.to_csv(out, index=False)
        all_stats[name] = stats
        print(f"  raw={stats['raw_records']} usable={stats['usable_records']} "
              f"quarantined={stats['quarantined_records']} "
              f"final_molecules={stats['final_molecules']}")

    with open(os.path.join(CLEAN, "quarantine.json"), "w") as f:
        json.dump({k: {"quarantine_reasons": v["quarantine_reasons"],
                       "raw_records": v["raw_records"]}
                   for k, v in all_stats.items()}, f, indent=2)

    # Overlap: molecules measured on BOTH targets (selectivity basis)
    tdf = pd.read_csv(os.path.join(CLEAN, f"{tkey.lower()}_clean.csv"))
    cdf = pd.read_csv(os.path.join(CLEAN, f"{ckey.lower()}_clean.csv"))
    both = set(tdf["molecule_chembl_id"]) & set(cdf["molecule_chembl_id"])
    all_stats["overlap"] = {
        "molecules_with_both_targets": len(both),
        f"{tkey.lower()}_only": len(set(tdf["molecule_chembl_id"]) - both),
        f"{ckey.lower()}_only": len(set(cdf["molecule_chembl_id"]) - both),
    }
    print(f"[overlap] molecules with data on both targets: {len(both)}")

    lines = [f"# Data quality report — {tkey} screen", "",
             "Generated by `scripts/02_clean_data.py`. Raw pulls cached in "
             "`data/raw/` (not committed); cleaned tables in `data/clean/`.",
             ""]
    for name in [tkey, ckey]:
        s = all_stats[name]
        lines += [
            f"## {name} ({s['target_chembl_id']})", "",
            f"- Raw ChEMBL records: **{s['raw_records']:,}**",
            f"- Usable (Ki/IC50/EC50/Kieq, nM): {s['usable_records']:,}",
            f"- Quarantined: {s['quarantined_records']:,}",
            f"- After dedupe (molecule x type): {s['deduped_mol_type_pairs']:,}",
            f"- Final molecules (one best value each): "
            f"**{s['final_molecules']:,}**",
            f"- By standard type: {dict(s['by_standard_type'])}",
            f"- By assay type (B=binding, F=functional): "
            f"{dict(s['by_assay_type'])}",
            "- Quarantine reasons: " +
            ", ".join(f"{k}={v}" for k, v in
                      sorted(s["quarantine_reasons"].items(),
                             key=lambda x: -x[1])),
            "- Top contributing documents: " +
            ", ".join(f"{d['document_chembl_id']}({d['records']})"
                      for d in s["top_documents"]),
            ""]
    o = all_stats["overlap"]
    lines += ["## Cross-target overlap", "",
              f"- Molecules with data on both {tkey} and {ckey}: **{o['molecules_with_both_targets']:,}**",
              f"- {tkey} only: {o[f'{tkey.lower()}_only']:,}; "
              f"{ckey} only: {o[f'{ckey.lower()}_only']:,}",
              "",
              "The overlap set is the empirical basis for the selectivity "
              "reference set (Tier A) in `03_screen.py`."]
    with open(cfg["quality_report_file"], "w") as f:
        f.write("\n".join(lines) + "\n")
    print(f"[ok] {cfg['quality_report_file']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())

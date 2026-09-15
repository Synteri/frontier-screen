#!/usr/bin/env python3
"""01_pull_data.py — pull ChEMBL bioactivity for CNR2/CB1 + approved-drug library.

Usage:
    python scripts/01_pull_data.py [--refresh]

Re-runnable: cached JSON in data/raw/ is reused unless --refresh is passed.
Writes data/manifest.json with source URLs, counts, timestamps, sha256.

Sources (public ChEMBL web services, no key required):
    https://www.ebi.ac.uk/chembl/api/data/activity.json
    https://www.ebi.ac.uk/chembl/api/data/molecule.json
"""
import argparse
import hashlib
import json
import os
import sys
import time
from datetime import datetime, timezone

import requests

BASE = "https://www.ebi.ac.uk/chembl/api/data"
RAW = os.path.join("data", "raw")
MANIFEST = os.path.join("data", "manifest.json")

TARGETS = {
    "CNR2": "CHEMBL253",   # cannabinoid CB2 receptor (target of the screen)
    "CB1": "CHEMBL218",    # cannabinoid CB1 receptor (counter-target: selectivity)
}

PAGE = 1000
SLEEP = 0.2  # politeness delay between paged requests

LIST_KEYS = {"activity": "activities", "molecule": "molecules"}


def fetch_paged(endpoint, params):
    """Fetch all pages of a ChEMBL list endpoint. Returns (items, total_count)."""
    list_key = LIST_KEYS[endpoint]
    items, offset, total = [], 0, None
    while True:
        q = dict(params, limit=PAGE, offset=offset)
        r = requests.get(f"{BASE}/{endpoint}.json", params=q, timeout=60)
        r.raise_for_status()
        payload = r.json()
        if total is None:
            total = payload["page_meta"]["total_count"]
            print(f"  total_count={total}")
        batch = payload[list_key]
        items.extend(batch)
        offset += len(batch)
        print(f"  fetched {offset}/{total}", end="\r")
        if offset >= total or not batch:
            break
        time.sleep(SLEEP)
    print()
    return items, total


def sha256_file(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def pull_target_activities(name, chembl_id, refresh):
    path = os.path.join(RAW, f"{name.lower()}_activities.json")
    url = f"target_chembl_id={chembl_id}"
    if os.path.exists(path) and not refresh:
        print(f"[cache] {path}")
        data = json.load(open(path))
        return path, len(data), url
    print(f"[pull] activities for {name} ({chembl_id})")
    items, total = fetch_paged("activity", {"target_chembl_id": chembl_id})
    with open(path, "w") as f:
        json.dump(items, f)
    return path, total, url


def pull_approved_drugs(refresh):
    path = os.path.join(RAW, "approved_drugs.json")
    url = "max_phase=4"
    if os.path.exists(path) and not refresh:
        print(f"[cache] {path}")
        return path, len(json.load(open(path))), url
    print("[pull] approved-drug library (max_phase=4)")
    # molecule_structures are embedded in the molecule resource
    items, total = fetch_paged("molecule", {"max_phase": 4})
    slim = [
        {
            "molecule_chembl_id": m.get("molecule_chembl_id"),
            "pref_name": m.get("pref_name"),
            "canonical_smiles": (m.get("molecule_structures") or {}).get(
                "canonical_smiles"
            ),
            "max_phase": m.get("max_phase"),
            "first_approval": m.get("first_approval"),
            "molecule_type": m.get("molecule_type"),
        }
        for m in items
    ]
    with open(path, "w") as f:
        json.dump(slim, f)
    return path, total, url


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--refresh", action="store_true",
                    help="re-download even if cache exists")
    args = ap.parse_args()

    os.makedirs(RAW, exist_ok=True)
    manifest = {
        "generated_utc": datetime.now(timezone.utc).isoformat(),
        "sources": {},
        "files": {},
    }

    for name, cid in TARGETS.items():
        path, count, url = pull_target_activities(name, cid, args.refresh)
        manifest["sources"][name] = {
            "target_chembl_id": cid,
            "filter": url,
            "record_count": count,
            "endpoint": f"{BASE}/activity.json",
        }
        manifest["files"][os.path.basename(path)] = sha256_file(path)

    path, count, url = pull_approved_drugs(args.refresh)
    manifest["sources"]["approved_drugs"] = {
        "filter": url,
        "record_count": count,
        "endpoint": f"{BASE}/molecule.json",
        "note": "slimmed to chembl_id / pref_name / canonical_smiles / "
                "max_phase / first_approval / molecule_type",
    }
    manifest["files"][os.path.basename(path)] = sha256_file(path)

    with open(MANIFEST, "w") as f:
        json.dump(manifest, f, indent=2)
    print(f"[ok] manifest -> {MANIFEST}")
    print(json.dumps(
        {k: v["record_count"] for k, v in manifest["sources"].items()},
        indent=2))


if __name__ == "__main__":
    sys.exit(main())

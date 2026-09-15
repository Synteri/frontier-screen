#!/usr/bin/env python3
"""00_smoke_test.py — verifies the local machine can run the screen.

Run:  python scripts/00_smoke_test.py
Pass criteria: Python 3.10+, torch imports, CUDA visible with >=8 GB VRAM,
rdkit imports. Warnings (not failures) if versions drift.
"""
import sys

failures = []


def check(name, ok, detail=""):
    status = "PASS" if ok else "FAIL"
    print(f"[{status}] {name} {detail}")
    if not ok:
        failures.append(name)


print("== Frontier Screen smoke test ==")

check("python >= 3.10", sys.version_info >= (3, 10), sys.version.split()[0])

try:
    import torch
    cuda = torch.cuda.is_available()
    vram = ""
    if cuda:
        free, total = torch.cuda.mem_get_info()
        vram = f"({total / 1e9:.1f} GB VRAM)"
    check("torch + CUDA", cuda, f"torch {torch.__version__} {vram}")
    if cuda and total < 8e9:
        print("[WARN] < 8 GB VRAM: stick to ligand-based methods, skip docking")
except ImportError as e:
    check("torch + CUDA", False, f"not installed ({e})")

try:
    from rdkit import rdBase
    check("rdkit", True, rdBase.rdkitVersion)
except ImportError as e:
    check("rdkit", False, f"not installed ({e})")

try:
    import pandas, numpy, sklearn  # noqa
    check("data stack", True, "pandas/numpy/sklearn")
except ImportError as e:
    check("data stack", False, f"({e})")

print()
if failures:
    print(f"SMOKE TEST FAILED: {', '.join(failures)}")
    sys.exit(1)
print("SMOKE TEST PASSED - machine is ready for Phase 2.")

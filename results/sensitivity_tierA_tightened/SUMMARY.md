# Sensitivity analysis: tightened Tier A CB1-inactivity rule

**Post-registration sensitivity check (2026-09-16).** The frozen primary
analysis (pre-registered 2026-09-15, untouched) is authoritative; this run is a
pre-posting robustness check commissioned after an independent QA audit.

## The design weakness (QA finding M1)

The pre-registered Tier A rule accepted measured CB1 inactivity as
`(CB1 relation '=' and pChEMBL < 5) OR (CB1 relation '>')`. A `>` record with
bound pChEMBL = 7 only proves the true value is *weaker than 7* — it does not
establish the pre-registration's own pChEMBL < 5 bar. 149 of the 1,412 Tier A
members (11%) rest on such records (bounds 5.25–8.82), five on vacuous bounds
such as `>50 nM`. Implemented exactly as pre-registered: a design weakness,
not a protocol deviation.

## The tightened rule

A CB1 `>` record now counts as inactivity evidence only when the reported
bound itself is ≤ 5.0 pChEMBL (weaker than 10 µM), which is what actually
establishes the claimed bar. Implementation:
`scripts/04_sensitivity_tierA_tightened.py` (single rule change vs
`scripts/03_screen.py`; pre-registration thresholds unchanged).

## Results

| Quantity | Primary (frozen) | Tightened |
|---|---|---|
| Tier A members | 1,412 | 1,263 |
| Members dropped by tightening | — | 149 (bound range 5.25–8.82) |
| Drugs scored | 3,417 | 3,417 |
| Hits (sel ≥ 0.25 and S_cb2 ≥ 0.40) | 0 | **0** |
| Max selectivity score | 0.1394 | 0.1394 |
| Max S_cb2 | — | 0.5217 |
| Drugs at/near the 0.25 threshold | 0 | 0 |

Top-10 under the tightened rule: ioversol, revumenib, piracetam, iohexol,
iodixanol, diatrizoate, diatrizoic acid, metrizoate, ioxilan, iothalamic acid —
all far below both bars.

## Verification

Removing reference members can only *lower* S_cb2 scores (max over a smaller
set), so the zero is mathematically robust to this tightening. Confirmed
empirically: across all 3,417 drugs, no selectivity score increased under the
tightened rule; 579 drugs lost their nearest (dropped) Tier A neighbor, but the
ranking maximum is unchanged and nothing approaches the 0.25 threshold.

## Files

- `screen_hits_tierA_tightened.csv` — full 3,417-drug ranking under the tightened rule
- `tierA_dropped_members.csv` — the 149 dropped Tier A members with their CB1 `>` bounds
- `summary.json` — machine-readable summary

## Disposition

The zero survives the tightening unchanged. The tightened rule is adopted as
the default Tier A definition for future screens; the M1 design weakness is
disclosed in the manuscript Limitations.

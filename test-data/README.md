# Veriflow test data — scenarios and rules

**Rules applied (UL 60335-1):** Clause **7** (rated voltage ≥ working voltage), **8.1** (accessibility / IP for HV > 60 V), **29.1** (clearance, Table 29.1), **29.2** (creepage, Table 29.2). Reinforced insulation uses **2×** minimum clearance and creepage.

**CSV columns:** `part_number`, `description`, `quantity`, `working_voltage_v`, `rated_voltage_v` (optional), `clearance_mm`, `creepage_distance_mm`, `material_group`, `pollution_degree`, `overvoltage_category`, `insulation_type` (optional: basic | supplementary | reinforced), `ip_code` (optional; e.g. IP20, IP2X).

For 230 V, pd=2, ov=2, mg=III: **min clearance 1.5 mm**, **min creepage 2.5 mm**. Reinforced: **3.0 mm** / **5.0 mm**.

---

## Numbered scenarios (bom_01 – bom_24)

| File | Scenario | Expected |
|------|----------|----------|
| **bom_01** | Single part, fully compliant; rated_voltage present | pass |
| **bom_02** | 3 parts, all compliant; rated_voltage present | pass |
| **bom_03** | Fail clearance only | fail |
| **bom_04** | Fail creepage only | fail |
| **bom_05** | Fail both | fail |
| **bom_06** | Edge clearance exact 1.5 mm | pass |
| **bom_07** | Edge creepage exact 2.5 mm | pass |
| **bom_08** | Mixed: one pass, one creepage fail | fail |
| **bom_09** | Tiny break clearance (1.4 mm) | fail |
| **bom_10** | Tiny break creepage (2.4 mm) | fail |
| **bom_11** | 300 V: one compliant, one clearance fail | fail |
| **bom_12** | Multiple failures | fail |
| **bom_13** | Partial data (some N/A) | pass |
| **bom_14** | Household mixed | fail |
| **bom_15** | Industrial 230 V, all pass | pass |
| **bom_16** | Boundary pass (0.1 over min) | pass |
| **bom_17** | Boundary fail (0.05 under) | fail |
| **bom_18** | Three parts, all pass | pass |
| **bom_19** | Three parts, one creepage fail | fail |
| **bom_20** | Stress mixed | fail |
| **bom_21** | **Clause 7:** rated_voltage &lt; working_voltage → fail | fail |
| **bom_22** | **Reinforced insulation:** 3.0 / 5.0 mm → pass | pass |
| **bom_23** | **Clause 8.1:** HV part no IP → manual_review | manual_review |
| **bom_24** | **Reinforced** but only basic spacing → fail | fail |

---

## Legacy (same columns)

- `bom_power_supply.csv` — 1 pass (29.1), 1 fail (29.2)
- `bom_power_supply_compliant.csv` — all pass
- `bom_household_appliance.csv` — multiple parts, all pass
- `bom_fail_both.csv` — both fail

---

## Advanced (bom_adv_01 – bom_adv_06)

Professional BOMs with ref_des, decimals, multi-voltage. See table in README for expected pass/fail/manual_review.

Run: **Upload & Verify** per file, or extend `scripts/run_real_life_tests.ps1` to include more files.

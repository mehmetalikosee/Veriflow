// =============================================================================
// UL 60335-1 / IEC 60664-1 — Lookup table nodes for Clause 29
// Table 29.1 (clearance) and Table 29.2 (creepage) — representative values
// (IEC 60664-1 Table F.1/F.2 style; verify against your standard edition.)
// =============================================================================

CREATE CONSTRAINT table_row_id IF NOT EXISTS FOR (t:TableRow) REQUIRE t.id IS UNIQUE;

// ----- Table 29.1: Minimum clearance (mm) — Pollution degree 2, Material group III / OVCat II -----
// working_voltage_v (≤), pollution_degree, overvoltage_category -> clearance_mm
MERGE (t:TableRow {id: "ul-60335-1-t29.1-50-2-2"})
SET t.table_ref = "29.1",
    t.working_voltage_v = 50,
    t.pollution_degree = 2,
    t.overvoltage_category = 2,
    t.clearance_mm = 0.5,
    t.requirement_id = "ul-60335-1-req-29-1-clearance";

MERGE (t:TableRow {id: "ul-60335-1-t29.1-100-2-2"})
SET t.table_ref = "29.1",
    t.working_voltage_v = 100,
    t.pollution_degree = 2,
    t.overvoltage_category = 2,
    t.clearance_mm = 0.8,
    t.requirement_id = "ul-60335-1-req-29-1-clearance";

MERGE (t:TableRow {id: "ul-60335-1-t29.1-150-2-2"})
SET t.table_ref = "29.1",
    t.working_voltage_v = 150,
    t.pollution_degree = 2,
    t.overvoltage_category = 2,
    t.clearance_mm = 1.0,
    t.requirement_id = "ul-60335-1-req-29-1-clearance";

MERGE (t:TableRow {id: "ul-60335-1-t29.1-300-2-2"})
SET t.table_ref = "29.1",
    t.working_voltage_v = 300,
    t.pollution_degree = 2,
    t.overvoltage_category = 2,
    t.clearance_mm = 1.5,
    t.requirement_id = "ul-60335-1-req-29-1-clearance";

MERGE (t:TableRow {id: "ul-60335-1-t29.1-600-2-2"})
SET t.table_ref = "29.1",
    t.working_voltage_v = 600,
    t.pollution_degree = 2,
    t.overvoltage_category = 2,
    t.clearance_mm = 2.0,
    t.requirement_id = "ul-60335-1-req-29-1-clearance";

MERGE (t:TableRow {id: "ul-60335-1-t29.1-1000-2-2"})
SET t.table_ref = "29.1",
    t.working_voltage_v = 1000,
    t.pollution_degree = 2,
    t.overvoltage_category = 2,
    t.clearance_mm = 3.0,
    t.requirement_id = "ul-60335-1-req-29-1-clearance";

MERGE (t:TableRow {id: "ul-60335-1-t29.1-1500-2-2"})
SET t.table_ref = "29.1",
    t.working_voltage_v = 1500,
    t.pollution_degree = 2,
    t.overvoltage_category = 2,
    t.clearance_mm = 4.0,
    t.requirement_id = "ul-60335-1-req-29-1-clearance";

MERGE (t:TableRow {id: "ul-60335-1-t29.1-2500-2-2"})
SET t.table_ref = "29.1",
    t.working_voltage_v = 2500,
    t.pollution_degree = 2,
    t.overvoltage_category = 2,
    t.clearance_mm = 5.5,
    t.requirement_id = "ul-60335-1-req-29-1-clearance";

// 250 V typical for household: min clearance 1.5 mm (≤300V row)
// 230 V AC: use 300 V row -> 1.5 mm clearance

// ----- Table 29.2: Minimum creepage (mm) — Pollution degree 2, Material group III -----
// working_voltage_v (≤), pollution_degree, material_group -> creepage_distance_mm
MERGE (t:TableRow {id: "ul-60335-1-t29.2-50-2-III"})
SET t.table_ref = "29.2",
    t.working_voltage_v = 50,
    t.pollution_degree = 2,
    t.material_group = "III",
    t.creepage_distance_mm = 0.8,
    t.requirement_id = "ul-60335-1-req-29-2-creepage";

MERGE (t:TableRow {id: "ul-60335-1-t29.2-100-2-III"})
SET t.table_ref = "29.2",
    t.working_voltage_v = 100,
    t.pollution_degree = 2,
    t.material_group = "III",
    t.creepage_distance_mm = 1.25,
    t.requirement_id = "ul-60335-1-req-29-2-creepage";

MERGE (t:TableRow {id: "ul-60335-1-t29.2-125-2-III"})
SET t.table_ref = "29.2",
    t.working_voltage_v = 125,
    t.pollution_degree = 2,
    t.material_group = "III",
    t.creepage_distance_mm = 1.6,
    t.requirement_id = "ul-60335-1-req-29-2-creepage";

MERGE (t:TableRow {id: "ul-60335-1-t29.2-200-2-III"})
SET t.table_ref = "29.2",
    t.working_voltage_v = 200,
    t.pollution_degree = 2,
    t.material_group = "III",
    t.creepage_distance_mm = 2.0,
    t.requirement_id = "ul-60335-1-req-29-2-creepage";

MERGE (t:TableRow {id: "ul-60335-1-t29.2-250-2-III"})
SET t.table_ref = "29.2",
    t.working_voltage_v = 250,
    t.pollution_degree = 2,
    t.material_group = "III",
    t.creepage_distance_mm = 2.5,
    t.requirement_id = "ul-60335-1-req-29-2-creepage";

MERGE (t:TableRow {id: "ul-60335-1-t29.2-400-2-III"})
SET t.table_ref = "29.2",
    t.working_voltage_v = 400,
    t.pollution_degree = 2,
    t.material_group = "III",
    t.creepage_distance_mm = 3.2,
    t.requirement_id = "ul-60335-1-req-29-2-creepage";

MERGE (t:TableRow {id: "ul-60335-1-t29.2-500-2-III"})
SET t.table_ref = "29.2",
    t.working_voltage_v = 500,
    t.pollution_degree = 2,
    t.material_group = "III",
    t.creepage_distance_mm = 4.0,
    t.requirement_id = "ul-60335-1-req-29-2-creepage";

MERGE (t:TableRow {id: "ul-60335-1-t29.2-800-2-III"})
SET t.table_ref = "29.2",
    t.working_voltage_v = 800,
    t.pollution_degree = 2,
    t.material_group = "III",
    t.creepage_distance_mm = 5.0,
    t.requirement_id = "ul-60335-1-req-29-2-creepage";

// 230 V AC household: use 250 V row -> min creepage 2.5 mm for pollution 2, material III

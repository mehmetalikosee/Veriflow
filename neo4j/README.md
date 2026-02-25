# Neo4j Knowledge Graph — ACE Veriflow

## Schema (run in order)

1. `schema/01_schema.cypher` — Constraints and indexes
2. `schema/02_ul_60335_nodes.cypher` — Standard, Clauses, Parameters
3. `seed/03_ul_60335_requirements.cypher` — Requirements and links to Parameters/Clauses
4. `seed/04_ul_60335_tables.cypher` — Table 29.1 (clearance) and Table 29.2 (creepage) lookup rows

## Query examples

```cypher
// All requirements for UL 60335-1
MATCH (s:Standard {id: "ul-60335-1"})-[:HAS_CLAUSE]->(c)-[:CONTAINS_REQUIREMENT]->(r)
RETURN c.clause_number, r.clause_ref, r.description;

// Get minimum clearance for 230 V, pollution 2, OV cat 2 (use row where working_voltage_v >= 230)
MATCH (t:TableRow)
WHERE t.table_ref = "29.1" AND t.working_voltage_v >= 230 AND t.pollution_degree = 2 AND t.overvoltage_category = 2
RETURN t.clearance_mm ORDER BY t.working_voltage_v LIMIT 1;

// Get minimum creepage for 230 V, pollution 2, material III
MATCH (t:TableRow)
WHERE t.table_ref = "29.2" AND t.working_voltage_v >= 230 AND t.pollution_degree = 2 AND t.material_group = "III"
RETURN t.creepage_distance_mm ORDER BY t.working_voltage_v LIMIT 1;
```

## UL 60335-1 references

- Clause 29: Clearances, creepage distances and solid insulation (values aligned with IEC 60664-1).
- Clause 14: Transient overvoltages.
- Clause 8: Protection against access (IP code).
- Annex L: Measurement of clearances and creepage distances.

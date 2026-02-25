// =============================================================================
// UL 60335-1 — Requirement nodes and HAS_PARAMETER / CONTAINS_REQUIREMENT
// Rule types: min, max, enum, table_lookup. Values aligned with IEC 60664-1 Table F.1/F.2
// (representative; verify against your standard edition.)
// =============================================================================

// ----- Requirement: 29.1 Minimum clearance (table-driven; here we use one row as example) -----
MERGE (r29_1:Requirement {id: "ul-60335-1-req-29-1-clearance"})
SET r29_1.clause_ref = "29.1",
    r29_1.description = "Clearance between live parts shall be not less than the value from Table 29.1 (based on working voltage, pollution degree, overvoltage category).",
    r29_1.rule_type = "min",
    r29_1.source_text = "Clearances shall be not less than those specified in Table 29.1.",
    r29_1.page_ref = "Annex B / Table 29.1",
    r29_1.confidence_required = 0.9,
    r29_1.measurement_note = "Annex L";

// Link to Clause 29.1 and Parameters
MATCH (c:Clause {id: "ul-60335-1-clause-29-1"})
MATCH (r:Requirement {id: "ul-60335-1-req-29-1-clearance"})
MERGE (c)-[:CONTAINS_REQUIREMENT]->(r);

MATCH (r:Requirement {id: "ul-60335-1-req-29-1-clearance"})
MATCH (p_clear:Parameter {id: "param-clearance-mm"})
MATCH (p_volt:Parameter {id: "param-working-voltage-v"})
MATCH (p_poll:Parameter {id: "param-pollution-degree"})
MATCH (p_ov:Parameter {id: "param-overvoltage-category"})
MERGE (r)-[:HAS_PARAMETER {role: "output", constraint: "min"}]->(p_clear)
MERGE (r)-[:HAS_PARAMETER {role: "input"}]->(p_volt)
MERGE (r)-[:HAS_PARAMETER {role: "input"}]->(p_poll)
MERGE (r)-[:HAS_PARAMETER {role: "input"}]->(p_ov);

// ----- Requirement: 29.2 Minimum creepage distance -----
MERGE (r29_2:Requirement {id: "ul-60335-1-req-29-2-creepage"})
SET r29_2.clause_ref = "29.2",
    r29_2.description = "Creepage distances shall be not less than the value from Table 29.2 (working voltage, pollution degree, material group).",
    r29_2.rule_type = "min",
    r29_2.source_text = "Creepage distances shall be not less than those specified in Table 29.2.",
    r29_2.page_ref = "Table 29.2",
    r29_2.confidence_required = 0.9,
    r29_2.measurement_note = "Annex L";

MATCH (c:Clause {id: "ul-60335-1-clause-29-2"})
MATCH (r:Requirement {id: "ul-60335-1-req-29-2-creepage"})
MERGE (c)-[:CONTAINS_REQUIREMENT]->(r);

MATCH (r:Requirement {id: "ul-60335-1-req-29-2-creepage"})
MATCH (p_creep:Parameter {id: "param-creepage-mm"})
MATCH (p_volt:Parameter {id: "param-working-voltage-v"})
MATCH (p_poll:Parameter {id: "param-pollution-degree"})
MATCH (p_mat:Parameter {id: "param-material-group"})
MERGE (r)-[:HAS_PARAMETER {role: "output", constraint: "min"}]->(p_creep)
MERGE (r)-[:HAS_PARAMETER {role: "input"}]->(p_volt)
MERGE (r)-[:HAS_PARAMETER {role: "input"}]->(p_poll)
MERGE (r)-[:HAS_PARAMETER {role: "input"}]->(p_mat);

// ----- Requirement: 14 Transient overvoltage (impulse withstand) -----
MERGE (r14:Requirement {id: "ul-60335-1-req-14-transient"})
SET r14.clause_ref = "14",
    r14.description = "Appliances shall withstand transient overvoltages; clearances shall be adequate for the declared overvoltage category and working voltage.",
    r14.rule_type = "min",
    r14.source_text = "Appliances shall be designed so that transient overvoltages do not cause danger.",
    r14.page_ref = "Clause 14",
    r14.confidence_required = 0.9;

MATCH (c:Clause {id: "ul-60335-1-clause-14"})
MATCH (r:Requirement {id: "ul-60335-1-req-14-transient"})
MERGE (c)-[:CONTAINS_REQUIREMENT]->(r);

MATCH (r:Requirement {id: "ul-60335-1-req-14-transient"})
MATCH (p_clear:Parameter {id: "param-clearance-mm"})
MATCH (p_volt:Parameter {id: "param-working-voltage-v"})
MERGE (r)-[:HAS_PARAMETER {role: "output", constraint: "min"}]->(p_clear)
MERGE (r)-[:HAS_PARAMETER {role: "input"}]->(p_volt);

// ----- Requirement: 8 Protection against access (IP code) -----
MERGE (r8:Requirement {id: "ul-60335-1-req-8-ip"})
SET r8.clause_ref = "8",
    r8.description = "Enclosures shall provide the degree of protection specified (e.g. IP20 for ordinary appliances, IPX4 or higher for splash-proof).",
    r8.rule_type = "enum",
    r8.source_text = "Enclosures of appliances shall have a degree of protection against access to live parts and against ingress of water.",
    r8.page_ref = "Clause 8, Table 8",
    r8.confidence_required = 0.9;

MATCH (c:Clause {id: "ul-60335-1-clause-8"})
MATCH (r:Requirement {id: "ul-60335-1-req-8-ip"})
MERGE (c)-[:CONTAINS_REQUIREMENT]->(r);

MATCH (r:Requirement {id: "ul-60335-1-req-8-ip"})
MATCH (p_ip:Parameter {id: "param-ip-code"})
MERGE (r)-[:HAS_PARAMETER {role: "output"}]->(p_ip);

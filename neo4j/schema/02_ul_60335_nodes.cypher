// =============================================================================
// UL 60335-1 — Standard, Clause, Requirement, Parameter nodes
// Based on UL 60335-1 / IEC 60335-1 (Household and similar electrical appliances)
// Clause 29: Clearances, creepage distances and solid insulation
// Clause 14: Transient overvoltages
// Representative values for GraphRAG; exact values must match your standard copy.
// =============================================================================

// ----- Standard -----
MERGE (s:Standard {id: "ul-60335-1"})
SET s.code = "UL 60335-1",
    s.title = "Household and Similar Electrical Appliances - Safety - Part 1: General Requirements",
    s.version = "6ED",
    s.edition = "6",
    s.publication_date = "2016-10-31";

// ----- Clauses -----
MERGE (c29:Clause {id: "ul-60335-1-clause-29"})
SET c29.clause_number = "29",
    c29.title = "Clearances, creepage distances and solid insulation",
    c29.standard_id = "ul-60335-1";

MERGE (c29_1:Clause {id: "ul-60335-1-clause-29-1"})
SET c29_1.clause_number = "29.1",
    c29_1.title = "Clearances - general",
    c29_1.standard_id = "ul-60335-1";

MERGE (c29_2:Clause {id: "ul-60335-1-clause-29-2"})
SET c29_2.clause_number = "29.2",
    c29_2.title = "Creepage distances - general",
    c29_2.standard_id = "ul-60335-1";

MERGE (c14:Clause {id: "ul-60335-1-clause-14"})
SET c14.clause_number = "14",
    c14.title = "Transient overvoltages",
    c14.standard_id = "ul-60335-1";

MERGE (c8:Clause {id: "ul-60335-1-clause-8"})
SET c8.clause_number = "8",
    c8.title = "Protection against access to live parts",
    c8.standard_id = "ul-60335-1";

// ----- Parameters (reusable across requirements) -----
MERGE (p_clear:Parameter {id: "param-clearance-mm"})
SET p_clear.name = "clearance_mm",
    p_clear.unit = "mm",
    p_clear.data_type = "float",
    p_clear.description = "Clearance in air between live parts and other live parts or earthed parts (mm)";

MERGE (p_creep:Parameter {id: "param-creepage-mm"})
SET p_creep.name = "creepage_distance_mm",
    p_creep.unit = "mm",
    p_creep.data_type = "float",
    p_creep.description = "Creepage distance along surface between conductive parts (mm)";

MERGE (p_volt:Parameter {id: "param-working-voltage-v"})
SET p_volt.name = "working_voltage_v",
    p_volt.unit = "V",
    p_volt.data_type = "float",
    p_volt.description = "Working voltage (RMS) between the two conductive parts under consideration";

MERGE (p_poll:Parameter {id: "param-pollution-degree"})
SET p_poll.name = "pollution_degree",
    p_poll.unit = "none",
    p_poll.data_type = "integer",
    p_poll.enum_values = [1, 2, 3],
    p_poll.description = "Pollution degree (1, 2, or 3) per IEC 60664-1";

MERGE (p_mat:Parameter {id: "param-material-group"})
SET p_mat.name = "material_group",
    p_mat.unit = "none",
    p_mat.data_type = "string",
    p_mat.enum_values = ["I", "II", "IIIa", "IIIb"],
    p_mat.description = "Material group (CTI) for creepage: I, II, IIIa, IIIb";

MERGE (p_ov:Parameter {id: "param-overvoltage-category"})
SET p_ov.name = "overvoltage_category",
    p_ov.unit = "none",
    p_ov.data_type = "integer",
    p_ov.enum_values = [1, 2, 3, 4],
    p_ov.description = "Overvoltage category (I–IV) for clearance";

MERGE (p_ip:Parameter {id: "param-ip-code"})
SET p_ip.name = "ip_code",
    p_ip.unit = "none",
    p_ip.data_type = "string",
    p_ip.description = "IP code (e.g. IP20, IP54) for enclosure protection";

// ----- Relationships: Standard -> Clause -----
MATCH (s:Standard {id: "ul-60335-1"})
MATCH (c:Clause) WHERE c.standard_id = "ul-60335-1"
MERGE (s)-[:HAS_CLAUSE]->(c);

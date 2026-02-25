// =============================================================================
// ACE — Veriflow: Neo4j Knowledge Graph Schema
// Standards → Requirements → Parameters (deterministic verification)
// =============================================================================

// Constraints and indexes (idempotent)
CREATE CONSTRAINT standard_id IF NOT EXISTS FOR (s:Standard) REQUIRE s.id IS UNIQUE;
CREATE CONSTRAINT requirement_id IF NOT EXISTS FOR (r:Requirement) REQUIRE r.id IS UNIQUE;
CREATE CONSTRAINT parameter_id IF NOT EXISTS FOR (p:Parameter) REQUIRE p.id IS UNIQUE;
CREATE CONSTRAINT clause_id IF NOT EXISTS FOR (c:Clause) REQUIRE c.id IS UNIQUE;

// Indexes for lookups
CREATE INDEX standard_code IF NOT EXISTS FOR (s:Standard) ON (s.code);
CREATE INDEX requirement_clause IF NOT EXISTS FOR (r:Requirement) ON (r.clause_ref);
CREATE INDEX parameter_name IF NOT EXISTS FOR (p:Parameter) ON (p.name);

// -----------------------------------------------------------------------------
// Node labels
// -----------------------------------------------------------------------------
// Standard   — e.g. UL 60335-1 (Household and similar electrical appliances)
// Clause     — Section/clause in the standard (e.g. "29", "29.1", "14")
// Requirement — A single verifiable rule (min/max, enum, formula)
// Parameter  — Measurable quantity (creepage_distance_mm, voltage_v, material_class)

// Relationship types:
// (Standard)-[:HAS_CLAUSE]->(Clause)
// (Clause)-[:CONTAINS_REQUIREMENT]->(Requirement)
// (Requirement)-[:HAS_PARAMETER]->(Parameter)
// (Requirement)-[:REFERENCES_PARAMETER {role: "input"|"output"}]->(Parameter)

// -----------------------------------------------------------------------------
// Standard
// -----------------------------------------------------------------------------
// id: unique string (e.g. "ul-60335-1")
// code: "UL 60335-1"
// title: full title
// version, edition, publication_date: optional

// -----------------------------------------------------------------------------
// Clause
// -----------------------------------------------------------------------------
// id: e.g. "ul-60335-1-clause-29"
// clause_number: "29" or "29.1"
// title: "Clearances, creepage distances and solid insulation"
// standard_id: denormalized for quick filter

// -----------------------------------------------------------------------------
// Requirement
// -----------------------------------------------------------------------------
// id: e.g. "ul-60335-1-req-29-1-clearance"
// clause_ref: "29.1" or "29"
// description: human-readable rule text
// rule_type: "min" | "max" | "enum" | "formula" | "table_lookup"
// source_text: exact excerpt from standard (for citation)
// page_ref: optional page number
// confidence_required: 0.0-1.0 (e.g. 0.9 for auto-pass)

// -----------------------------------------------------------------------------
// Parameter
// -----------------------------------------------------------------------------
// id: e.g. "param-clearance-mm"
// name: "clearance_mm" | "creepage_distance_mm" | "working_voltage_v" | "pollution_degree" | "material_group"
// unit: "mm" | "V" | "A" | "none"
// data_type: "float" | "integer" | "string" | "enum"
// enum_values: optional JSON array for enum
// description: short description for extraction guidance

// No additional DDL needed — node properties are flexible.
// Run seed scripts to create UL 60335-1 nodes and relationships.

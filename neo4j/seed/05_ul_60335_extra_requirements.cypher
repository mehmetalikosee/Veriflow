// UL 60335-1 — Extra requirements: Clause 8 (accessibility), Clause 7 (rated voltage)
// Run after 02 and 03.

MERGE (c7:Clause {id: "ul-60335-1-clause-7"})
SET c7.clause_number = "7",
    c7.title = "Marking and instructions",
    c7.standard_id = "ul-60335-1";

MERGE (c8_1:Clause {id: "ul-60335-1-clause-8-1"})
SET c8_1.clause_number = "8.1",
    c8_1.title = "Access to live parts",
    c8_1.standard_id = "ul-60335-1";

MATCH (s:Standard {id: "ul-60335-1"})
MERGE (s)-[:HAS_CLAUSE]->(c7)
MERGE (s)-[:HAS_CLAUSE]->(c8_1);

MERGE (r8_1:Requirement {id: "ul-60335-1-req-8-1-accessibility"})
SET r8_1.clause_ref = "8.1",
    r8_1.description = "Live parts shall not be accessible; enclosures and barriers shall provide adequate protection (IP code or equivalent).",
    r8_1.rule_type = "enum",
    r8_1.source_text = "Access to live parts shall be prevented.",
    r8_1.page_ref = "Access to live parts",
    r8_1.confidence_required = 0.85;

MATCH (c:Clause {id: "ul-60335-1-clause-8-1"})
MATCH (r:Requirement {id: "ul-60335-1-req-8-1-accessibility"})
MERGE (c)-[:CONTAINS_REQUIREMENT]->(r);

MERGE (r7:Requirement {id: "ul-60335-1-req-rated-voltage"})
SET r7.clause_ref = "7",
    r7.description = "Components shall have rated voltage not less than the working voltage.",
    r7.rule_type = "min",
    r7.source_text = "Rated voltage of components shall be adequate for the application.",
    r7.page_ref = "Rated voltage",
    r7.confidence_required = 0.9;

MATCH (c:Clause {id: "ul-60335-1-clause-7"})
MATCH (r:Requirement {id: "ul-60335-1-req-rated-voltage"})
MERGE (c)-[:CONTAINS_REQUIREMENT]->(r);

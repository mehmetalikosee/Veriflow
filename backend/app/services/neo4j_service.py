"""
Neo4j driver and queries for requirement/table lookups.
"""
from typing import Optional, List, Any
from neo4j import AsyncGraphDatabase
from app.core.config import settings

_driver = None


def get_driver():
    global _driver
    if _driver is None:
        _driver = AsyncGraphDatabase.driver(
            settings.NEO4J_URI,
            auth=(settings.NEO4J_USER, settings.NEO4J_PASSWORD),
        )
    return _driver


async def close_driver():
    global _driver
    if _driver:
        await _driver.close()
        _driver = None


async def get_requirement_by_id(requirement_id: str) -> Optional[dict]:
    """Fetch a requirement and its parameters."""
    driver = get_driver()
    query = """
    MATCH (r:Requirement {id: $rid})
    OPTIONAL MATCH (r)-[hp:HAS_PARAMETER]->(p:Parameter)
    OPTIONAL MATCH (c:Clause)-[:CONTAINS_REQUIREMENT]->(r)
    RETURN r, collect(DISTINCT {param: p, role: hp.role, constraint: hp.constraint}) AS params,
           c.clause_number AS clause_number, c.title AS clause_title
    """
    async with driver.session() as session:
        result = await session.run(query, rid=requirement_id)
        record = await result.single()
    if not record or not record["r"]:
        return None
    r = record["r"]
    return {
        "id": r["id"],
        "clause_ref": r["clause_ref"],
        "description": r["description"],
        "rule_type": r["rule_type"],
        "source_text": r.get("source_text"),
        "page_ref": r.get("page_ref"),
        "confidence_required": r.get("confidence_required"),
        "params": record["params"],
        "clause_number": record["clause_number"],
        "clause_title": record["clause_title"],
    }


# Fallback tables (UL 60335-1 / IEC 60664-1 Table 29.1 style) when Neo4j has no TableRow nodes
# PD2 OV-II (default)
_CLEARANCE_FALLBACK = [(50, 0.5), (100, 0.8), (150, 1.0), (300, 1.5), (600, 2.0), (1000, 3.0), (1500, 4.0), (2500, 5.5)]
# PD1 (clean) — lower clearances
_CLEARANCE_PD1 = [(50, 0.4), (100, 0.6), (150, 0.8), (300, 1.2), (600, 1.6), (1000, 2.5), (1500, 3.2), (2500, 4.5)]
# PD3 (polluted) — higher clearances
_CLEARANCE_PD3 = [(50, 0.8), (100, 1.0), (150, 1.25), (300, 2.0), (600, 2.5), (1000, 4.0), (1500, 5.0), (2500, 7.0)]


def _clearance_from_fallback(working_voltage_v: float, pollution_degree: int, overvoltage_category: int) -> Optional[float]:
    """Return minimum clearance from fallback tables for given PD/OV."""
    if overvoltage_category != 2:
        return None
    table = _CLEARANCE_FALLBACK
    if pollution_degree == 1:
        table = _CLEARANCE_PD1
    elif pollution_degree == 3:
        table = _CLEARANCE_PD3
    for v_lim, clear in table:
        if working_voltage_v <= v_lim:
            return clear
    return table[-1][1] if table else None


async def get_clearance_min_mm(working_voltage_v: float, pollution_degree: int, overvoltage_category: int) -> Optional[float]:
    """Table 29.1: minimum clearance (mm). Uses first row where working_voltage_v >= given voltage."""
    try:
        driver = get_driver()
        query = """
        MATCH (t:TableRow)
        WHERE t.table_ref = "29.1"
          AND t.working_voltage_v >= $voltage
          AND t.pollution_degree = $pd
          AND t.overvoltage_category = $ov
        RETURN t.clearance_mm AS clearance_mm
        ORDER BY t.working_voltage_v
        LIMIT 1
        """
        async with driver.session() as session:
            result = await session.run(
                query,
                voltage=working_voltage_v,
                pd=pollution_degree,
                ov=overvoltage_category,
            )
            record = await result.single()
        if record and record["clearance_mm"] is not None:
            return float(record["clearance_mm"])
    except Exception:
        pass
    # Fallback when Neo4j has no TableRow or query fails (e.g. graph not seeded)
    return _clearance_from_fallback(working_voltage_v, pollution_degree, overvoltage_category)


# Fallback table (UL 60335-1 Table 29.2 style) when Neo4j has no TableRow nodes — pollution 2, material III
_CREEPAGE_FALLBACK = [(50, 0.8), (100, 1.25), (125, 1.6), (200, 2.0), (250, 2.5), (400, 3.2), (500, 4.0), (800, 5.0)]


async def get_creepage_min_mm(working_voltage_v: float, pollution_degree: int, material_group: str) -> Optional[float]:
    """Table 29.2: minimum creepage (mm). material_group e.g. III."""
    mg = str(material_group).strip().upper() if material_group else "III"
    try:
        driver = get_driver()
        query = """
        MATCH (t:TableRow)
        WHERE t.table_ref = "29.2"
          AND t.working_voltage_v >= $voltage
          AND t.pollution_degree = $pd
          AND t.material_group = $mg
        RETURN t.creepage_distance_mm AS creepage_mm
        ORDER BY t.working_voltage_v
        LIMIT 1
        """
        async with driver.session() as session:
            result = await session.run(
                query,
                voltage=working_voltage_v,
                pd=pollution_degree,
                mg=mg,
            )
            record = await result.single()
        if record and record["creepage_mm"] is not None:
            return float(record["creepage_mm"])
    except Exception:
        pass
    # Fallback when Neo4j has no TableRow or query fails
    if pollution_degree != 2 or mg not in ("III", "IIIA", "IIIB"):
        return None
    for v_lim, creep in _CREEPAGE_FALLBACK:
        if working_voltage_v <= v_lim:
            return creep
    return _CREEPAGE_FALLBACK[-1][1] if _CREEPAGE_FALLBACK else None


async def list_requirements_for_standard(standard_id: str = "ul-60335-1") -> List[dict]:
    """List all requirements for a standard (for UI / agent)."""
    driver = get_driver()
    query = """
    MATCH (s:Standard {id: $sid})-[:HAS_CLAUSE]->(c)-[:CONTAINS_REQUIREMENT]->(r)
    RETURN r.id AS id, r.clause_ref AS clause_ref, r.description AS description, r.rule_type AS rule_type,
           c.title AS clause_title
    ORDER BY r.clause_ref
    """
    async with driver.session() as session:
        result = await session.run(query, sid=standard_id)
        records = await result.data()
    return records

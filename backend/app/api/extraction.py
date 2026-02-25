"""
BOM / technical data extraction with strict Pydantic schemas.
"""
from fastapi import APIRouter, UploadFile, File
from app.schemas.extraction import BOMExtractionResult, BOMPart, MaterialGroup, PollutionDegree, OvervoltageCategory
import openpyxl
import csv
import io

router = APIRouter()


def _parse_excel(content: bytes, filename: str) -> BOMExtractionResult:
    """Parse Excel BOM; return structured result. Placeholder: you can wire LLM later."""
    wb = openpyxl.load_workbook(io.BytesIO(content), read_only=True)
    ws = wb.active
    parts = []
    for row in ws.iter_rows(min_row=2, values_only=True):
        if not row or row[0] is None:
            continue
        rv, ins_type = None, None
        if len(row) > 10 and row[10] is not None:
            try:
                rv = float(row[10])
            except (ValueError, TypeError):
                pass
        if len(row) > 11 and row[11] is not None:
            s = str(row[11]).strip().lower()
            if s in ("basic", "supplementary", "reinforced"):
                ins_type = s
        part = BOMPart(
            part_number=str(row[0]) if row[0] is not None else "",
            description=str(row[1]) if len(row) > 1 and row[1] else None,
            quantity=int(row[2]) if len(row) > 2 and row[2] is not None else 1,
            working_voltage_v=float(row[3]) if len(row) > 3 and row[3] is not None else None,
            clearance_mm=float(row[4]) if len(row) > 4 and row[4] is not None else None,
            creepage_distance_mm=float(row[5]) if len(row) > 5 and row[5] is not None else None,
            rated_voltage_v=rv,
            insulation_type=ins_type,
        )
        parts.append(part)
    return BOMExtractionResult(
        source_file=filename,
        parts=parts,
        extraction_confidence=0.92,
        warnings=[],
    )


def _row_get(r: dict, key: str):
    """Get value from row; match header by exact or lowercase (CSV headers may vary)."""
    if key in r and r[key] not in (None, ""):
        v = r[key]
        return v.strip() if isinstance(v, str) else v
    key_lower = key.lower().strip()
    for header, val in r.items():
        if header and str(header).strip().lower() == key_lower and val not in (None, ""):
            return val.strip() if isinstance(val, str) else val
    return None


def _parse_csv(content: bytes, filename: str) -> BOMExtractionResult:
    """Parse CSV BOM. Normalize line endings and match headers case-insensitively."""
    text = content.decode("utf-8-sig").replace("\r\n", "\n").replace("\r", "\n")
    if not text.strip():
        return BOMExtractionResult(source_file=filename, parts=[], extraction_confidence=0.0, warnings=["Empty file"])
    reader = csv.DictReader(io.StringIO(text))
    parts = []
    for r in reader:
        # Also support positional columns (0=part_number, 1=desc, 2=qty, 3=voltage, 4=clearance, 5=creepage)
        values = list(r.values()) if r else []
        def _get(name: str, pos: int | None = None):
            out = _row_get(r, name)
            if out is not None and str(out).strip() != "":
                return out
            if pos is not None and pos < len(values):
                raw = values[pos]
                return raw if raw not in (None, "") else None
            return None
        qty = 1
        try:
            q = _get("quantity", 2) or 1
            qty = int(q) if q is not None else 1
        except (ValueError, TypeError):
            pass
        v, cl, cr = None, None, None
        try:
            vv = _get("working_voltage_v", 3)
            v = float(vv) if vv else None
        except (ValueError, TypeError):
            pass
        try:
            clv = _get("clearance_mm", 4)
            cl = float(clv) if clv else None
        except (ValueError, TypeError):
            pass
        try:
            crv = _get("creepage_distance_mm", 5)
            cr = float(crv) if crv else None
        except (ValueError, TypeError):
            pass
        mg = None
        mgv = _get("material_group", 6)
        if mgv:
            try:
                mg = MaterialGroup(str(mgv).strip().upper().replace(" ", ""))
            except ValueError:
                pass
        pd = None
        pdv = _get("pollution_degree", 7)
        if pdv:
            try:
                pd = PollutionDegree(int(pdv))
            except (ValueError, TypeError):
                pass
        ov = None
        ovv = _get("overvoltage_category", 8)
        if ovv:
            try:
                ov = OvervoltageCategory(int(ovv))
            except (ValueError, TypeError):
                pass
        part_number = _get("part_number", 0) or ""
        description = _get("description", 1)
        ip_code_raw = _get("ip_code", 9)
        ip_code = None
        if ip_code_raw and str(ip_code_raw).strip().upper().startswith("IP"):
            ip_code = str(ip_code_raw).strip().upper()[:4]  # IP20, IP2X, IPX4
        rv = None
        try:
            rvv = _get("rated_voltage_v", 10)
            rv = float(rvv) if rvv else None
        except (ValueError, TypeError):
            pass
        ins_type = _get("insulation_type", 11)
        if ins_type:
            ins_type = str(ins_type).strip().lower()
            if ins_type not in ("basic", "supplementary", "reinforced"):
                ins_type = None
        parts.append(
            BOMPart(
                part_number=part_number,
                description=description,
                quantity=qty,
                working_voltage_v=v,
                rated_voltage_v=rv,
                clearance_mm=cl,
                creepage_distance_mm=cr,
                material_group=mg,
                pollution_degree=pd,
                overvoltage_category=ov,
                insulation_type=ins_type or None,
                ip_code=ip_code or None,
            )
        )
    return BOMExtractionResult(
        source_file=filename,
        parts=parts,
        extraction_confidence=0.92,
        warnings=[],
    )


@router.post("/bom", response_model=BOMExtractionResult)
async def extract_bom(file: UploadFile = File(...)):
    """
    Upload BOM (Excel or CSV). Returns structured extraction with enforced schema.
    Column names for CSV: part_number, description, quantity, working_voltage_v, clearance_mm, creepage_distance_mm.
    """
    content = await file.read()
    fn = file.filename or "upload"
    if fn.lower().endswith(".xlsx") or fn.lower().endswith(".xls"):
        return _parse_excel(content, fn)
    if fn.lower().endswith(".csv"):
        return _parse_csv(content, fn)
    raise ValueError("Unsupported format. Use .xlsx or .csv.")

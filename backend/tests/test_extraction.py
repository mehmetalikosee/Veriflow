"""Extraction logic: CSV and Excel parsing."""
import io
import pytest
from app.api.extraction import _parse_csv, _parse_excel
from app.schemas.extraction import BOMExtractionResult


class TestParseCSV:
    def test_csv_minimal_columns(self):
        content = b"part_number,description,quantity\nP1,Desc,1\n"
        r = _parse_csv(content, "test.csv")
        assert r.source_file == "test.csv"
        assert len(r.parts) == 1
        assert r.parts[0].part_number == "P1"
        assert r.parts[0].quantity == 1

    def test_csv_with_voltage_and_distances(self):
        content = (
            b"part_number,description,quantity,working_voltage_v,clearance_mm,creepage_distance_mm,material_group,pollution_degree,overvoltage_category\n"
            b"PSU-230,Primary 230V,1,230,2.0,2.5,III,2,2\n"
        )
        r = _parse_csv(content, "bom.csv")
        assert len(r.parts) == 1
        assert r.parts[0].working_voltage_v == 230.0
        assert r.parts[0].clearance_mm == 2.0
        assert r.parts[0].creepage_distance_mm == 2.5
        assert str(r.parts[0].material_group) == "MaterialGroup.III"
        assert r.parts[0].pollution_degree is not None
        assert r.parts[0].overvoltage_category is not None

    def test_csv_empty_optional_values(self):
        content = b"part_number,quantity\nP2,2\n"
        r = _parse_csv(content, "test.csv")
        assert r.parts[0].working_voltage_v is None
        assert r.parts[0].clearance_mm is None


class TestParseExcel:
    def test_excel_two_rows(self):
        import openpyxl
        wb = openpyxl.Workbook()
        ws = wb.active
        ws.append(["part_number", "description", "quantity", "working_voltage_v", "clearance_mm", "creepage_distance_mm"])
        ws.append(["P1", "Desc", 1, 230.0, 2.0, 2.5])
        buf = io.BytesIO()
        wb.save(buf)
        buf.seek(0)
        content = buf.read()
        r = _parse_excel(content, "test.xlsx")
        assert len(r.parts) == 1
        assert r.parts[0].part_number == "P1"
        assert r.parts[0].working_voltage_v == 230.0
        assert r.parts[0].clearance_mm == 2.0
        assert r.parts[0].creepage_distance_mm == 2.5

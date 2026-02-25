"""
Pydantic schemas for BOM and technical data extraction (strict for governance).
"""
from pydantic import BaseModel, Field
from typing import Optional, List
from enum import Enum


class MaterialGroup(str, Enum):
    I = "I"
    II = "II"
    III = "III"   # General group III (CTI 100–175); tables may use III
    IIIa = "IIIa"
    IIIb = "IIIb"


class PollutionDegree(int, Enum):
    ONE = 1
    TWO = 2
    THREE = 3


class OvervoltageCategory(int, Enum):
    I = 1
    II = 2
    III = 3
    IV = 4


class BOMPart(BaseModel):
    """Single line from BOM."""
    part_number: str = Field(..., description="Manufacturer part number or internal ID")
    description: Optional[str] = None
    quantity: int = Field(ge=1, description="Quantity per unit")
    working_voltage_v: Optional[float] = Field(None, ge=0, le=10000, description="Max working voltage (V)")
    rated_voltage_v: Optional[float] = Field(None, ge=0, le=10000, description="Component rated voltage (V); shall be >= working_voltage_v")
    clearance_mm: Optional[float] = Field(None, ge=0, le=100, description="Measured clearance (mm)")
    creepage_distance_mm: Optional[float] = Field(None, ge=0, le=100, description="Measured creepage (mm)")
    material_group: Optional[MaterialGroup] = None
    pollution_degree: Optional[PollutionDegree] = None
    overvoltage_category: Optional[OvervoltageCategory] = None
    insulation_type: Optional[str] = Field(None, description="basic | supplementary | reinforced (affects 29.1/29.2 multipliers)")
    ip_code: Optional[str] = Field(None, pattern=r"^IP[\dX]{2}$", description="e.g. IP20, IP54, IP2X, IPX4")
    notes: Optional[str] = None


class BOMExtractionResult(BaseModel):
    """Result of BOM parsing + AI extraction (enforced schema)."""
    source_file: str = Field(..., description="Original filename")
    parts: List[BOMPart] = Field(default_factory=list)
    extraction_confidence: float = Field(ge=0, le=1, description="Overall confidence of extraction")
    warnings: List[str] = Field(default_factory=list)

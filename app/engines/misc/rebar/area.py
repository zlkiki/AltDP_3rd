"""
KS D 3504 표준 이형철근(D10~D35) 다열/혼합 배근 조합별 총 단면적 및 중심 간격 자동 계산 유틸리티
"""
import math
from pydantic import BaseModel, Field
from typing import Dict, Any, List

MODULE_INFO = {
    "id": "misc_rebar_area",
    "name": "철근 단면적·배근표 (Rebar Area Table)",
    "category": "misc",
    "group": "rebar",
    "submodule": "area",
    "description": "KS D 3504 규격 이형철근(D10~D35) 단일/혼합 직경 다열 배근 총 단면적(As), 중량 및 유효 간격 계산",
    "geomType": "rc_rect",
    "template": "rc_rect"
}

class BarAreaInput(BaseModel):
    b_section: float = Field(500.0, description="부재 단면 폭 (mm)")
    cover: float = Field(40.0, description="피복 두께 (mm)")
    stirrup_dia: float = Field(10.0, description="스터럽/대근 직경 (mm)")
    primary_bar: str = Field("D25", description="주철근 1 규격")
    primary_count: int = Field(4, description="주철근 1 수량")
    secondary_bar: str = Field("D22", description="혼합철근 2 규격 (없으면 0)")
    secondary_count: int = Field(2, description="혼합철근 2 수량")
    layers: int = Field(1, description="배근 단 수 (1단, 2단)")

def calculate(data: BarAreaInput) -> Dict[str, Any]:
    # KS D 3504 표준 철근 제원
    rebar_props = {
        "D10": {"dia": 9.53, "area": 71.33, "weight": 0.560},
        "D13": {"dia": 12.7, "area": 126.7, "weight": 0.995},
        "D16": {"dia": 15.9, "area": 198.6, "weight": 1.56},
        "D19": {"dia": 19.1, "area": 286.5, "weight": 2.25},
        "D22": {"dia": 22.2, "area": 387.1, "weight": 3.04},
        "D25": {"dia": 25.4, "area": 506.7, "weight": 3.98},
        "D29": {"dia": 28.6, "area": 642.4, "weight": 5.04},
        "D32": {"dia": 31.8, "area": 794.2, "weight": 6.23},
        "D35": {"dia": 35.8, "area": 1007.0, "weight": 7.90}
    }
    
    p_info = rebar_props.get(data.primary_bar, {"dia": 25.4, "area": 506.7, "weight": 3.98})
    s_info = rebar_props.get(data.secondary_bar, {"dia": 22.2, "area": 387.1, "weight": 3.04})
    
    As1 = data.primary_count * p_info["area"]
    As2 = data.secondary_count * s_info["area"]
    As_total = As1 + As2
    
    total_count = data.primary_count + data.secondary_count
    total_weight = (data.primary_count * p_info["weight"]) + (data.secondary_count * s_info["weight"])  # kg/m
    
    # 순 순간격(Clear Spacing) 검토
    bars_per_layer = math.ceil(total_count / data.layers) if data.layers > 0 else total_count
    # 가용 폭 = b - 2*cover - 2*stirrup_dia
    avail_w = data.b_section - 2.0 * data.cover - 2.0 * data.stirrup_dia
    
    # 철근들이 차지하는 폭
    avg_dia = (data.primary_count * p_info["dia"] + data.secondary_count * s_info["dia"]) / total_count if total_count > 0 else 25.0
    occupied_w = bars_per_layer * avg_dia
    
    spaces_count = max(1, bars_per_layer - 1)
    clear_spacing = (avail_w - occupied_w) / spaces_count if avail_w > occupied_w else 0.0
    
    # KDS 최소 순간격 한계: max(25mm, db, 4/3*25mm골재=33.3mm)
    min_clear_req = max(25.0, avg_dia, 33.3)
    dcr_space = min_clear_req / clear_spacing if clear_spacing > 0 else 999.0
    status = "OK" if dcr_space <= 1.0 else "NG"
    
    return {
        "status": status,
        "max_dcr": round(dcr_space, 3),
        "total_As_mm2": round(As_total, 1),
        "total_weight_kg_per_m": round(total_weight, 2),
        "clear_spacing_mm": round(clear_spacing, 1),
        "min_clear_req_mm": round(min_clear_req, 1),
        "bars_per_layer": bars_per_layer,
        "summary": f"철근 단면적 계산: 총 As={round(As_total,1)}mm²({total_count}본), 순간격={round(clear_spacing,1)}mm(기준 {round(min_clear_req,1)}mm, {status})",
        "visual_data": {
            "type": "rc_rect",
            "b": data.b_section,
            "h": 600.0,
            "cover": data.cover,
            "top_rebar_count": 2,
            "bot_rebar_count": bars_per_layer,
            "stirrup_space": 150.0
        }
    }

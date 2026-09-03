# app/engines/rc/wall/bmt.py
"""RC Basement Retaining Wall (지하외벽 측방 토압/정수압 삼각형 하중 휨 및 전단 설계) Engine - KDS 14 20."""
import math
from typing import Dict, Any
from pydantic import BaseModel, Field

from app.engines.common.kds_concrete import REBAR_FY, REBAR_AREA, calc_beta1, calc_eta, get_eps_cu

MODULE_INFO = {
    "id": "bmt",
    "name": "지하외벽 (Basement Wall)",
    "category": "rc",
    "group": "wall",
    "geomType": "rc_wall",
    "description": "KDS 14 20에 따른 RC 지하외벽(토압/수압 작용 1방향 또는 2방향 슬래브 거동) 단면 및 배근 검토"
}


class WallBmtInputSchema(BaseModel):
    H: float = Field(4200.0, description="지하외벽 층고 H (mm)")
    tw: float = Field(400.0, description="외벽 두께 tw (mm)")
    fck: float = Field(27.0, description="콘크리트 압축강도 (MPa)")
    rebar_grade: str = Field("SD400", description="철근 강종")
    cover: float = Field(50.0, description="토압측 순 피복 (mm)")
    
    gamma_soil: float = Field(19.0, description="흙의 단위중량 (kN/m³)")
    Ko: float = Field(0.5, description="정지토압계수 Ko")
    water_table_depth: float = Field(1.5, description="지표면에서 지하수위까지 깊이 (m)")
    surcharge_q: float = Field(10.0, description="지표면 상재하중 (kN/m²)")
    
    vert_dia: int = Field(16, description="토압측 연직 주철근 직경 (mm)")
    vert_spacing: float = Field(150.0, description="토압측 연직 주철근 간격 (mm)")
    horiz_dia: int = Field(13, description="수평 배력근 직경 (mm)")
    horiz_spacing: float = Field(200.0, description="수평 배력근 간격 (mm)")


def calculate(data: Any) -> Dict[str, Any]:
    if hasattr(data, "model_dump"):
        data = data.model_dump()
    elif hasattr(data, "dict"):
        data = data.dict()
    elif not isinstance(data, dict):
        data = {}

    H_mm = float(data.get("H", 4200.0))
    H_m = H_mm * 1e-3
    tw = float(data.get("tw", 400.0))
    fck = float(data.get("fck", 27.0))
    rebar_grade = str(data.get("rebar_grade", "SD400"))
    fy = REBAR_FY.get(rebar_grade, 400.0)
    cover = float(data.get("cover", 50.0))
    
    gamma = float(data.get("gamma_soil", 19.0))
    Ko = float(data.get("Ko", 0.5))
    hw_depth = float(data.get("water_table_depth", 1.5))
    q_sur = float(data.get("surcharge_q", 10.0))
    
    vert_dia = int(data.get("vert_dia", 16))
    vert_spacing = float(data.get("vert_spacing", 150.0))
    
    # 1. Lateral Pressures
    ps = Ko * q_sur
    p_soil = Ko * gamma * H_m
    gamma_w = 9.81
    pw = gamma_w * max(0.0, H_m - hw_depth)
    
    p_base_unfactored = ps + p_soil + pw
    p_base_factored = 1.6 * p_base_unfactored  # kN/m²
    
    # 2. Factored Design Moment & Shear
    Mu_base = (p_base_factored * (H_m ** 2)) / 15.0  # kN*m/m
    Vu_base = (p_base_factored * H_m) * 0.40         # kN/m
    
    # 3. Flexural Capacity at Base (1m strip)
    b_strip = 1000.0
    d = tw - cover - vert_dia / 2.0
    As_vert = (b_strip / vert_spacing) * REBAR_AREA.get(vert_dia, 198.6)
    
    sb = 0.85 * fck
    a = As_vert * fy / (sb * b_strip)
    phi_flex = 0.85
    Mn = As_vert * fy * (d - a / 2.0) * 1e-6  # kN*m/m
    phiMn = phi_flex * Mn
    dcr_flex = Mu_base / phiMn if phiMn > 0 else 999.0
    
    # 4. Shear Capacity at Critical Section (d from base)
    phi_v = 0.75
    Vc = (1.0 / 6.0) * math.sqrt(fck) * b_strip * d * 1e-3  # kN/m
    phiVc = phi_v * Vc
    dcr_shear = Vu_base / phiVc if phiVc > 0 else 999.0
    
    governing_dcr = max(dcr_flex, dcr_shear)
    status = "OK" if governing_dcr <= 1.0 else "NG"
    
    return {
        "status": status,
        "governing_dcr": round(governing_dcr, 3),
        "max_dcr": round(governing_dcr, 3),
        "flexure": {
            "title": "지하외벽 하단 휨모멘트 검토 (Flexural Capacity φMn)",
            "Mu": round(Mu_base, 2),
            "phiMn": round(phiMn, 2),
            "As": round(As_vert, 1),
            "dcr": round(dcr_flex, 3),
            "phi": phi_flex
        },
        "shear": {
            "title": "지하외벽 하단 전단력 검토 (Shear Capacity φVc)",
            "Vu": round(Vu_base, 2),
            "phiVc": round(phiVc, 2),
            "dcr": round(dcr_shear, 3),
            "phi": phi_v
        },
        "lateral_earth_pressure": {
            "p_surcharge_kPa": round(ps, 2),
            "p_soil_base_kPa": round(p_soil, 2),
            "p_water_base_kPa": round(pw, 2),
            "p_base_factored_kPa": round(p_base_factored, 2)
        },
        "details": {
            "geometry": {
                "wall_height_H_mm": H_mm,
                "wall_thick_tw_mm": tw,
                "effective_depth_d_mm": round(d, 1)
            },
            "reinforcement": {
                "vert_bar_dia": vert_dia,
                "vert_bar_spacing": vert_spacing,
                "vert_bar_area_As": round(As_vert, 1),
                "horiz_bar_dia": int(data.get("horiz_dia", 13)),
                "horiz_bar_spacing": float(data.get("horiz_spacing", 200.0))
            }
        },
        "summary": f"지하외벽 검토: 총 측압={p_base_factored:.1f}kN/m², 하단 휨 DCR={dcr_flex:.3f}, 전단 DCR={dcr_shear:.3f}",
        "visual_data": {
            "type": "rc_rect",
            "b": 1000.0,
            "h": tw,
            "cover": cover,
            "vert_dia": vert_dia,
        }
    }

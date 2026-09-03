# app/engines/misc/rebar/crack.py
"""Rebar Crack Control & Crack Width (간접 균열제어 철근간격 및 균열폭 산정) Engine - KDS 14 20 30."""
import math
from typing import Dict, Any
from pydantic import BaseModel, Field

from app.engines.common.kds_concrete import REBAR_FY

MODULE_INFO = {
    "id": "crack",
    "name": "균열 제어 (Crack Control)",
    "category": "misc",
    "group": "rebar",
    "geomType": "rc_rect",
    "description": "KDS 14 20 30 사용성 한계상태에 따른 간접 균열제어 최대 철근간격(s_max) 및 Frosch 식 직접 균열폭(w) 검토"
}


class CrackWidthInputSchema(BaseModel):
    b: float = Field(400.0, description="부재 폭 b (mm)")
    h: float = Field(600.0, description="부재 춤 h (mm)")
    fck: float = Field(24.0, description="콘크리트 압축강도 (MPa)")
    rebar_grade: str = Field("SD400", description="철근 강종")
    cover: float = Field(40.0, description="인장측 순 피복두께 cc (mm)")
    
    bar_dia: int = Field(22, description="인장 주근 직경 db (mm)")
    bar_spacing: float = Field(150.0, description="배치된 주근 간격 s (mm)")
    
    M_serv: float = Field(160.0, description="사용하중 휨모멘트 (kN*m)")
    exposure_condition: str = Field("건조환경 (0.3mm)", description="환경 노출 범주")


def calculate(data: Any) -> Dict[str, Any]:
    if hasattr(data, "model_dump"):
        data = data.model_dump()
    elif hasattr(data, "dict"):
        data = data.dict()
    elif not isinstance(data, dict):
        data = {}

    b = float(data.get("b", 400.0))
    h = float(data.get("h", 600.0))
    fck = float(data.get("fck", 24.0))
    rebar_grade = str(data.get("rebar_grade", "SD400"))
    fy = REBAR_FY.get(rebar_grade, 400.0)
    cc = float(data.get("cover", 40.0))
    
    db = int(data.get("bar_dia", 22))
    s_prov = float(data.get("bar_spacing", 150.0))
    M_serv_kNm = float(data.get("M_serv", 160.0))
    exposure = str(data.get("exposure_condition", "건조환경 (0.3mm)"))
    
    if "0.2" in exposure:
        w_lim = 0.20
    elif "0.4" in exposure:
        w_lim = 0.40
    else:
        w_lim = 0.30
        
    d = h - cc - 10.0 - db / 2.0
    
    # 1. Working Stress in Rebar fs
    Ec = 8500.0 * ((fck + 4.0) ** (1.0 / 3.0))
    Es = 200000.0
    jd = 0.875 * d
    num_bars = max(2, int(b / s_prov) + 1)
    As = num_bars * (math.pi * (db ** 2) / 4.0)
    
    fs = (M_serv_kNm * 1e6) / (As * jd) if As * jd > 0 else 0.67 * fy
    fs_clamped = min(fs, 0.67 * fy)
    
    # 2. Maximum Indirect Bar Spacing s_max
    s_max_1 = 375.0 * (210.0 / fs_clamped) - 2.5 * cc if fs_clamped > 0 else 300.0
    s_max_2 = 300.0 * (210.0 / fs_clamped) if fs_clamped > 0 else 300.0
    s_max = max(50.0, min(s_max_1, s_max_2))
    dcr_spacing = s_prov / s_max if s_max > 0 else 999.0
    
    # 3. Direct Crack Width Calculation (Frosch)
    dc = cc + db / 2.0
    beta_frosch = 1.0 + 0.08 * dc
    eps_s = fs_clamped / Es
    crack_width_mm = 2.0 * eps_s * beta_frosch * math.sqrt(dc ** 2 + (s_prov / 2.0) ** 2)
    
    dcr_width = crack_width_mm / w_lim if w_lim > 0 else 999.0
    governing_dcr = max(dcr_spacing, dcr_width)
    status = "OK" if governing_dcr <= 1.0 else "NG"
    
    return {
        "status": status,
        "governing_dcr": round(governing_dcr, 3),
        "max_dcr": round(governing_dcr, 3),
        "flexure": {
            "title": "간접 균열제어 철근간격 검토 (Indirect Spacing s ≤ s_max)",
            "s_provided_mm": s_prov,
            "s_max_allowable_mm": round(s_max, 1),
            "rebar_stress_fs_MPa": round(fs_clamped, 1),
            "dcr": round(dcr_spacing, 3)
        },
        "deflection": {
            "title": "Frosch 직접 균열폭 검토 (Direct Crack Width w ≤ w_lim)",
            "crack_width_w_mm": round(crack_width_mm, 3),
            "allowable_w_lim_mm": w_lim,
            "dcr": round(dcr_width, 3)
        },
        "details": {
            "exposure_and_stress": {
                "exposure_condition": exposure,
                "allowable_crack_width_mm": w_lim,
                "rebar_strain_eps_s": round(eps_s, 6),
                "Frosch_beta": round(beta_frosch, 3)
            }
        },
        "summary": f"균열 제어 검토: 철근간격={s_prov}mm(허용 {s_max:.1f}mm), 직접 균열폭 w={crack_width_mm:.3f}mm(한계 {w_lim}mm)",
        "visual_data": {
            "type": "rc_rect",
            "b": b,
            "h": h,
            "cover": cc,
            "bot_rebar_count": num_bars,
            "bot_rebar_dia": db
        }
    }

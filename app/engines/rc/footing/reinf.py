"""
RC 독립기초 상·하부 배근 상세 및 기둥 Dowel 철근 정착/이음 길이 검토 모듈
"""
import math
from pydantic import BaseModel, Field
from typing import Dict, Any

MODULE_INFO = {
    "id": "rc_footing_reinf",
    "name": "기초배근 (Footing Rebar)",
    "category": "rc",
    "group": "footing",
    "submodule": "reinf",
    "description": "기초 상·하부 2방향 주철근 배근 및 기둥 접합부 다우웰(Dowel) 정착/지압 검토",
    "geomType": "rc_footing",
    "template": "rc_footing"
}

class FootingReinfInput(BaseModel):
    B: float = Field(2500.0, description="기초 폭 B (mm)")
    L: float = Field(2500.0, description="기초 길이 L (mm)")
    H: float = Field(700.0, description="기초 두께 H (mm)")
    cx: float = Field(500.0, description="기둥 X방향 치수 cx (mm)")
    cy: float = Field(500.0, description="기둥 Y방향 치수 cy (mm)")
    fck: float = Field(24.0, description="콘크리트 압축강도 (MPa)")
    fy: float = Field(400.0, description="철근 항복강도 (MPa)")
    Pu: float = Field(1500.0, description="계수 축력 Pu (kN)")
    bot_rebar_x_dia: int = Field(19, description="하부 X방향 철근 직경 (mm)")
    bot_rebar_x_spacing: float = Field(150.0, description="하부 X방향 철근 간격 (mm)")
    bot_rebar_y_dia: int = Field(19, description="하부 Y방향 철근 직경 (mm)")
    bot_rebar_y_spacing: float = Field(150.0, description="하부 Y방향 철근 간격 (mm)")
    dowel_dia: int = Field(22, description="기둥 다우웰 직경 (mm)")
    dowel_num: int = Field(8, description="기둥 다우웰 수량 (EA)")

def calculate(data: Any) -> Dict[str, Any]:
    get_v = lambda k, default: data.get(k, default) if isinstance(data, dict) else getattr(data, k, default)
    fck = float(get_v("fck", 24.0))
    fy = float(get_v("fy", 400.0))
    B = float(get_v("B", 2500.0))
    L = float(get_v("L", 2500.0))
    H = float(get_v("H", 700.0))
    cx = float(get_v("cx", 500.0))
    cy = float(get_v("cy", 500.0))
    Pu = float(get_v("Pu", 1500.0)) * 1e3
    
    bot_rebar_x_dia = int(get_v("bot_rebar_x_dia", 19))
    bot_rebar_x_spacing = float(get_v("bot_rebar_x_spacing", 150.0))
    bot_rebar_y_dia = int(get_v("bot_rebar_y_dia", 19))
    bot_rebar_y_spacing = float(get_v("bot_rebar_y_spacing", 150.0))
    dowel_dia = int(get_v("dowel_dia", 22))
    dowel_num = int(get_v("dowel_num", 8))
    
    # 1. 다우웰 철근 수량 및 단면적
    num_dowel = dowel_num
    db_dowel = float(dowel_dia)
    As_dowel = num_dowel * (math.pi * db_dowel * db_dowel / 4.0)
    
    # 2. 콘크리트 지압강도 검토 (Bearing Strength)
    A1 = cx * cy
    A2 = min(B * L, (cx + 2 * (H - 100.0)) * (cy + 2 * (H - 100.0)))
    ratio_bearing = min(2.0, math.sqrt(A2 / A1))
    phi_bearing = 0.65
    Pnb = phi_bearing * 0.85 * fck * A1 * ratio_bearing  # N
    dcr_bearing = Pu / Pnb if Pnb > 0 else 999.0
    
    # 3. 다우웰 필요 철근량 (최소 0.005 * A1)
    As_min_dowel = 0.005 * A1
    dcr_dowel_area = As_min_dowel / As_dowel if As_dowel > 0 else 999.0
    
    # 4. 정착길이 ld 산정 (압축 정착: KDS 기준 ld = max(0.24 * fy / sqrt(fck) * db, 0.043 * fy * db, 200mm))
    ld_comp = max(0.24 * (fy / math.sqrt(fck)) * db_dowel, 0.043 * fy * db_dowel, 200.0)
    avail_len = H - 100.0
    dcr_ld = ld_comp / avail_len if avail_len > 0 else 999.0
    
    max_dcr = max(dcr_bearing, dcr_dowel_area, dcr_ld)
    status = "OK" if max_dcr <= 1.0 else "NG"
    
    rebar_x_str = f"D{bot_rebar_x_dia}@{int(bot_rebar_x_spacing)}"
    rebar_y_str = f"D{bot_rebar_y_dia}@{int(bot_rebar_y_spacing)}"
    
    return {
        "status": status,
        "max_dcr": round(max_dcr, 3),
        "dcr_bearing": round(dcr_bearing, 3),
        "dcr_dowel_area": round(dcr_dowel_area, 3),
        "dcr_embed_len": round(dcr_ld, 3),
        "Pnb_kN": round(Pnb / 1000.0, 1),
        "As_dowel_mm2": round(As_dowel, 1),
        "As_min_mm2": round(As_min_dowel, 1),
        "ld_comp_mm": round(ld_comp, 1),
        "avail_depth_mm": round(avail_len, 1),
        "summary": f"기초 다우웰 검토: 지압 DCR={round(dcr_bearing,2)}, 정착장 DCR={round(dcr_ld,2)} ({status})",
        "visual_data": {
            "type": "rc_footing",
            "B": B,
            "L": L,
            "H": H,
            "c_x": cx,
            "c_y": cy,
            "rebar_x": rebar_x_str,
            "rebar_y": rebar_y_str
        }
    }

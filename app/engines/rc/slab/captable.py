"""
RC 슬래브 두께 및 배근 간격별 허용 적재 활하중(Capacity Table) 환산 일람표 모듈
"""
import math
from pydantic import BaseModel, Field
from typing import Dict, Any, List

MODULE_INFO = {
    "id": "rc_slab_captable",
    "name": "슬래브 내력표 (Slab Capacity Table)",
    "category": "rc",
    "group": "slab",
    "submodule": "captable",
    "description": "슬래브 두께(150~250mm), 경간 및 철근 배근 규격별 허용 균등 활하중(LL, kN/m²) 산정표",
    "geomType": "rc_slab",
    "template": "rc_slab"
}

class SlabCapTableInput(BaseModel):
    span_x: float = Field(4000.0, description="슬래브 단변 경간 Lx (mm)")
    span_y: float = Field(6000.0, description="슬래브 장변 경간 Ly (mm)")
    fck: float = Field(24.0, description="콘크리트 압축강도 (MPa)")
    fy: float = Field(400.0, description="철근 항복강도 (MPa)")
    dead_load_finish: float = Field(1.5, description="마감 고정하중 (kN/m²)")

def calculate(data: SlabCapTableInput) -> Dict[str, Any]:
    Lx = data.span_x / 1000.0  # m
    fck = data.fck
    fy = data.fy
    
    thicknesses = [150.0, 180.0, 200.0, 220.0, 250.0]
    rebars = ["D10@200", "D10@150", "D13@200", "D13@150"]
    
    table_results = []
    
    for thk in thicknesses:
        d = thk - 30.0  # 유효높이
        # 자중 DL_self = (thk / 1000) * 24.0
        dl_self = (thk / 1000.0) * 24.0
        dl_tot = dl_self + data.dead_load_finish
        
        for r_code in rebars:
            if "D10" in r_code:
                ab = 71.33
            else:
                ab = 126.7
            spacing = float(r_code.split("@")[1])
            As = ab * (1000.0 / spacing)  # mm2/m
            
            # 슬래브 단위폭 휨내력 phi_Mn
            a = (As * fy) / (0.85 * fck * 1000.0)
            phi_Mn = 0.85 * As * fy * (d - a / 2.0) / 1e6  # kN·m/m
            
            # 단순지지 또는 연속 슬래브 근사 휨모멘트 식: Mu = w_u * Lx^2 / 10
            # w_u = 10 * phi_Mn / Lx^2
            wu_cap = (10.0 * phi_Mn) / (Lx**2) if Lx > 0 else 0.0
            
            # 허용 활하중: 1.2 * DL + 1.6 * LL_allow = wu_cap => LL_allow = (wu_cap - 1.2 * DL) / 1.6
            ll_allow = (wu_cap - 1.2 * dl_tot) / 1.6
            ll_allow = max(0.0, ll_allow)
            
            table_results.append({
                "thickness_mm": thk,
                "rebar": r_code,
                "As_mm2_m": round(As, 1),
                "phi_Mn_kNm": round(phi_Mn, 1),
                "wu_max_kNm2": round(wu_cap, 1),
                "LL_allow_kN_m2": round(ll_allow, 2)
            })
            
    return {
        "status": "OK",
        "governing_dcr": 0.0,
        "max_dcr": 0.0,
        "span_x_m": Lx,
        "span_y_m": data.span_y / 1000.0,
        "total_combinations": len(table_results),
        "capacity_table": table_results,
        "summary": f"슬래브 허용 활하중표 생성 완료 ({len(table_results)}개 조합)",
        "visual_data": {
            "type": "rc_slab",
            "thk": 200.0,
            "span_x": data.span_x,
            "span_y": data.span_y,
            "rebar_top_x": "D10@200",
            "rebar_bot_x": "D13@150"
        }
    }


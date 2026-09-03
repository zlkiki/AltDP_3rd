"""
AISC Design Guide 11 기반 철골 바닥구조 보행 진동(Floor Vibration) 고유진동수 및 피크 가속도(ap/g) 평가 모듈
"""
import math
from pydantic import BaseModel, Field
from typing import Dict, Any

MODULE_INFO = {
    "id": "steel_special_floor_vib",
    "name": "바닥 진동 (Floor Vibration)",
    "category": "steel",
    "group": "special",
    "submodule": "floor_vib",
    "description": "AISC DG11 기반 보행 하중에 의한 바닥판 기본 고유진동수(fn) 및 최대 피크 가속도(ap/g) 거주성 검토",
    "geomType": "steel_h",
    "template": "steel_h"
}

class FloorVibInput(BaseModel):
    span_beam: float = Field(9000.0, description="보 경간 L_beam (mm)")
    spacing_beam: float = Field(3000.0, description="보 간격 S_beam (mm)")
    span_girder: float = Field(9000.0, description="거더 경간 L_girder (mm)")
    slab_thick: float = Field(150.0, description="슬래브 전체 두께 (mm)")
    deck_depth: float = Field(50.0, description="데크 골 높이 (mm)")
    steel_Ix: float = Field(4.5e8, description="보 강재 단면 2차모멘트 Ix (mm⁴)")
    fck: float = Field(24.0, description="콘크리트 압축강도 (MPa)")
    dead_load: float = Field(3.5, description="바닥 총 고정하중 (kN/m²)")
    live_load_vib: float = Field(0.5, description="진동 평가용 활하중 (kN/m²)")
    damping_ratio: float = Field(0.025, description="감쇠비 β (사무실 0.025, 오픈플랜 0.03)")
    occupancy_type: str = Field("office", description="실 용도 (office, residential, shopping, outdoor)")

def calculate(data: FloorVibInput) -> Dict[str, Any]:
    L_b = data.span_beam / 1000.0  # m
    S_b = data.spacing_beam / 1000.0  # m
    w_tot = data.dead_load + data.live_load_vib  # kN/m2
    
    # 1. 단위 보당 등분포 질량 w_b
    w_b = w_tot * S_b  # kN/m
    
    # 2. 합성 단면 2차모멘트 Ij 근사
    # 콘크리트 슬래브 유효 강성 기여 (Ec = 8500 * (fck+4)^(1/3))
    Ec = 8500.0 * ((data.fck + 4.0)**(1.0/3.0))  # MPa
    Es = 205000.0  # MPa
    n_ratio = Es / (1.35 * Ec)
    tc_eff = data.slab_thick - data.deck_depth / 2.0
    # 환산 폭 beff_trans = min(L_b/4, S_b)*1000 / n
    beff_trans = (min(L_b * 0.25, S_b) * 1000.0) / n_ratio
    # 합성 Ij
    Ij = data.steel_Ix * 1.85  # 근사 배율
    
    # 3. 보 패널 고유진동수 fn (Dunkerley 식: fn = 0.18 * sqrt(g / delta))
    # delta_b = 5 w L^4 / (384 E I)
    g = 9.81 * 1000.0  # mm/s2
    delta_b = (5.0 * (w_b) * ((data.span_beam)**4)) / (384.0 * Es * Ij)  # mm
    fn = 0.18 * math.sqrt(g / delta_b) if delta_b > 0 else 0.0  # Hz
    
    # 4. 유효 패널 중량 W 산정 (AISC DG11)
    # B_eff = min(Cj * (Ds/Dj)^(1/4) * L_b, 2/3 * Floor_width)
    B_eff = min(2.0 * (S_b * 3.0), 18.0)  # m
    W = w_tot * (B_eff * L_b) * 1000.0  # N
    
    # 5. 피크 가속도 비 ap/g 산정 (AISC DG11 식 4.1)
    # ap/g = (Po * exp(-0.35 * fn)) / (beta * W)
    # Po: 일정 보행 가진력 (사무실 0.29 kN = 290 N)
    Po = 290.0  # N
    beta = data.damping_ratio
    ap_g_ratio = (Po * math.exp(-0.35 * fn)) / (beta * W) if (beta * W) > 0 else 999.0
    ap_g_percent = ap_g_ratio * 100.0  # % g
    
    # 6. 거주성 기준 가속도 한계 (AISC DG11: 사무실 0.5%g, 상가 1.5%g)
    limit_map = {"office": 0.5, "residential": 0.5, "shopping": 1.5, "outdoor": 5.0}
    limit_ap_g = limit_map.get(data.occupancy_type, 0.5)
    
    dcr_vib = ap_g_percent / limit_ap_g if limit_ap_g > 0 else 999.0
    status = "OK" if dcr_vib <= 1.0 and fn >= 4.0 else "NG"
    
    return {
        "status": status,
        "governing_dcr": round(dcr_vib, 3),
        "max_dcr": round(dcr_vib, 3),
        "vibration": {
            "title": "바닥판 보행진동 피크 가속도 검토 (Floor Vibration ap/g)",
            "fn_Hz": round(fn, 2),
            "limit_fn_Hz": 4.0,
            "peak_accel_percent_g": round(ap_g_percent, 3),
            "limit_accel_percent_g": round(limit_ap_g, 2),
            "dcr": round(dcr_vib, 3)
        },
        "deflection": {
            "title": "보행 하중 정적 처짐 (Static Deflection under Line Load)",
            "delta_static_mm": round(delta_b, 2),
            "panel_weight_W_kN": round(W / 1000.0, 1),
            "dcr": round(dcr_vib, 3)
        },
        "details": {
            "vibration_parameters": {
                "occupancy_type": data.occupancy_type,
                "damping_ratio_beta": data.damping_ratio,
                "walking_force_Po_N": Po,
                "effective_width_Beff_m": round(B_eff, 1),
                "composite_moment_of_inertia_Ij": round(Ij, 0)
            }
        },
        "summary": f"바닥진동 평가: 고유진동수={round(fn,2)}Hz(기준>=4Hz), 피크가속도={round(ap_g_percent,3)}%g(허용 {limit_ap_g}%g, DCR={round(dcr_vib,2)}) ({status})",
        "visual_data": {
            "type": "steel_h",
            "H": 500.0,
            "B": 200.0,
            "tw": 10.0,
            "tf": 16.0
        }
    }

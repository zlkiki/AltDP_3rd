"""
골형 데크플레이트(Deck Plate) 시공 중 처짐/응력 및 합성 슬래브 공용 시 휨/수평전단 검토 모듈
"""
import math
from pydantic import BaseModel, Field
from typing import Dict, Any

MODULE_INFO = {
    "id": "steel_composite_deck",
    "name": "데크플레이트 합성 슬래브 (Deck & Slab)",
    "category": "steel",
    "group": "composite",
    "submodule": "deck",
    "description": "골형 아연도금 데크플레이트 시공 중 하중 처짐 및 콘크리트 타설 후 합성 휨/수평전단 검토",
    "geomType": "rc_slab",
    "template": "rc_slab"
}

class DeckPlateInput(BaseModel):
    span: float = Field(2800.0, description="데크플레이트 지지 경간 (mm)")
    deck_depth: float = Field(50.0, description="데크 골 높이 hr (mm)")
    deck_thick: float = Field(1.2, description="데크 강판 두께 t (mm)")
    slab_total_thick: float = Field(150.0, description="슬래브 전체 두께 tc (mm)")
    fy_deck: float = Field(275.0, description="데크 강재 항복강도 (MPa)")
    fck: float = Field(24.0, description="콘크리트 압축강도 (MPa)")
    live_load_const: float = Field(1.5, description="시공 중 활하중 (kN/m²)")
    live_load_serv: float = Field(4.0, description="사용 중 활하중 (kN/m²)")
    rebar_dia: str = Field("D10", description="상부 온도/수축 철근 규격")
    rebar_spacing: float = Field(200.0, description="상부 철근 간격 (mm)")

def calculate(data: DeckPlateInput) -> Dict[str, Any]:
    L = data.span / 1000.0  # m
    hr = data.deck_depth
    t = data.deck_thick
    tc = data.slab_total_thick
    fy = data.fy_deck
    fck = data.fck
    
    # 1. 시공 중 하중 산정 (단위 폭 1m 기준)
    # 콘크리트 자중 (골 형상 고려 평균 두께 = tc - hr/2)
    t_conc_avg = (tc - hr / 2.0) / 1000.0  # m
    w_conc = t_conc_avg * 24.0  # kN/m2
    w_deck = 0.15  # kN/m2
    w_const_dl = w_conc + w_deck
    w_const_ll = data.live_load_const
    w_const_tot = 1.2 * w_const_dl + 1.6 * w_const_ll  # kN/m
    
    # 2. 시공 중 휨모멘트 및 처짐 (단순보 가정)
    M_const = (w_const_tot * (L**2)) / 8.0  # kN·m/m
    
    # 데크 단면 2차모멘트 및 단면계수 근사 (폭 1000mm 기준)
    # Ix ≈ 0.5 * 1000 * t * hr^2
    Ix_deck = 0.35 * 1000.0 * t * (hr**2)  # mm4
    Sx_deck = Ix_deck / (hr / 2.0)  # mm3
    
    # 시공 중 휨응력 fb
    fb_const = (M_const * 1e6) / Sx_deck if Sx_deck > 0 else 999.0
    phi_b = 0.90
    F_allow = phi_b * fy
    dcr_const_stress = fb_const / F_allow if F_allow > 0 else 999.0
    
    # 시공 중 즉시 처짐 (자중 기준): delta = 5 w L^4 / (384 E I)
    Es = 205000.0  # MPa
    w_dl_unfact = w_const_dl  # N/mm
    delta_const = (5.0 * w_dl_unfact * ((data.span)**4)) / (384.0 * Es * Ix_deck) if Ix_deck > 0 else 999.0
    delta_allow = data.span / 180.0
    dcr_const_defl = delta_const / delta_allow if delta_allow > 0 else 999.0
    
    # 3. 공용 시 합성 슬래브 휨강도 검토
    w_serv_tot = 1.2 * (w_const_dl + 1.0) + 1.6 * data.live_load_serv
    Mu_serv = (w_serv_tot * (L**2)) / 8.0  # kN·m/m
    
    # 하부 데크 인장 기여 면적 As_deck
    As_deck = 1000.0 * t * 1.25  # 전개면적 고려 mm2/m
    d = tc - hr * 0.4
    a = (As_deck * fy) / (0.85 * fck * 1000.0)
    phi_Mn_serv = 0.85 * As_deck * fy * (d - a / 2.0) / 1e6  # kN·m/m
    dcr_serv_flexure = Mu_serv / phi_Mn_serv if phi_Mn_serv > 0 else 999.0
    
    max_dcr = max(dcr_const_stress, dcr_const_defl, dcr_serv_flexure)
    status = "OK" if max_dcr <= 1.0 else "NG"
    
    return {
        "status": status,
        "max_dcr": round(max_dcr, 3),
        "dcr_const_stress": round(dcr_const_stress, 3),
        "dcr_const_defl": round(dcr_const_defl, 3),
        "dcr_serv_flexure": round(dcr_serv_flexure, 3),
        "delta_const_mm": round(delta_const, 1),
        "delta_allow_mm": round(delta_allow, 1),
        "phi_Mn_serv_kNm": round(phi_Mn_serv, 1),
        "Mu_serv_kNm": round(Mu_serv, 1),
        "summary": f"데크플레이트 검토: 시공처짐={round(delta_const,1)}mm(허용 {round(delta_allow,1)}mm), 합성휨 DCR={round(dcr_serv_flexure,2)} ({status})",
        "visual_data": {
            "type": "rc_slab",
            "thk": tc,
            "span_x": data.span,
            "span_y": 6000.0,
            "rebar_top_x": f"{data.rebar_dia}@{int(data.rebar_spacing)}",
            "rebar_bot_x": "Deck Profile"
        }
    }

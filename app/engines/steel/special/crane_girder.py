"""
KDS 14 31 10 천장 주행 크레인 거더(Crane Girder) 수직/수평 충격계수 휨/비틀림 및 피로(Fatigue) 상세 검토 모듈
"""
import math
from pydantic import BaseModel, Field
from typing import Dict, Any

MODULE_INFO = {
    "id": "steel_special_crane_girder",
    "name": "크레인 주행보 (Crane Girder)",
    "category": "steel",
    "group": "special",
    "submodule": "crane_girder",
    "description": "KDS 14 31 10 천장크레인 휠하중 수직(25%)/수평(20%) 충격계수 이축휨 및 반복 피로 응력 범위(S-N) 검토",
    "geomType": "steel_h",
    "template": "steel_h"
}

class CraneGirderInput(BaseModel):
    section_name: str = Field("H-700x300x13x24", description="강재 단면 선택 (KS 규격)")
    H: float = Field(700.0, description="H형강 높이 (mm)")
    B: float = Field(300.0, description="H형강 폭 (mm)")
    tw: float = Field(13.0, description="웨브 두께 (mm)")
    tf: float = Field(24.0, description="플랜지 두께 (mm)")
    span: float = Field(7500.0, description="거더 경간 (mm)")
    Fy: float = Field(355.0, description="강재 항복강도 (MPa)")
    wheel_load: float = Field(160.0, description="정적 최대 크레인 휠하중 (kN)")
    wheel_spacing: float = Field(2500.0, description="크레인 바퀴 축간 거리 (mm)")
    crane_class: str = Field("C", description="크레인 사용 등급 (A, B, C, D, E, F)")
    cycles: float = Field(2000000.0, description="설계 반복 하중 횟수 N")
    fatigue_category: str = Field("B", description="피로 상세 범주 (A, B, C, D, E)")

def calculate(data: CraneGirderInput) -> Dict[str, Any]:
    H = data.H
    B = data.B
    tw = data.tw
    tf = data.tf
    L = data.span
    Fy = data.Fy
    
    # 1. 단면 성질 산정
    Ix = (B * (H**3) - (B - tw) * ((H - 2.0 * tf)**3)) / 12.0  # mm4
    Sx = Ix / (H / 2.0)  # mm3
    # 상부 플랜지 + 웨브 1/6 수평 단면 2차모멘트 Iyc (상부 횡모멘트 지지)
    Iyc = (tf * (B**3)) / 12.0  # mm4
    Syc = Iyc / (B / 2.0)  # mm3
    
    # 2. 크레인 충격 계수 적용 (KDS: 수직 25%, 수평 횡하중 20%)
    P_vert = data.wheel_load * 1.25 * 1000.0  # N
    P_horiz = data.wheel_load * 0.20 * 1000.0  # N
    
    # 2개 바퀴 이동하중 최대 휨모멘트 (L=7.5m, a=2.5m)
    # M_max ≈ 2 * P * (L - a/2)^2 / (8 L) 근사
    a_dist = data.wheel_spacing
    Mx_max = (P_vert * (L - a_dist / 2.0)**2) / (4.0 * L) if L > 0 else 0.0  # N·mm
    My_max = (P_horiz * (L - a_dist / 2.0)**2) / (4.0 * L) if L > 0 else 0.0  # N·mm
    
    # 3. 조합 휨응력 검토
    fbx = Mx_max / Sx
    fby = My_max / Syc
    
    phi_b = 0.90
    F_allow = phi_b * Fy
    # 상부 플랜지 외단 최대 압축응력: f_comb = fbx + fby
    f_comb = fbx + fby
    dcr_flexure = f_comb / F_allow if F_allow > 0 else 999.0
    
    # 4. KDS 피로(Fatigue) 상세 검토
    # 범주별 피로 상수 Cf
    cf_map = {"A": 8.0e11, "B": 3.9e11, "C": 1.4e11, "D": 7.2e10, "E": 3.6e10}
    Cf = cf_map.get(data.fatigue_category, 3.9e11)
    
    # 피로 한계 응력 범위 F_SR = (Cf / N)^(1/3)
    F_SR = (Cf / data.cycles)**(1.0 / 3.0)  # MPa
    # 활하중(비충격 휠하중)에 의한 실제 작용 응력 범위 S_act
    Mx_live = (data.wheel_load * 1000.0 * (L - a_dist / 2.0)**2) / (4.0 * L)
    S_act = Mx_live / Sx
    dcr_fatigue = S_act / F_SR if F_SR > 0 else 999.0
    
    # 5. 수직 처짐 검토 (기준: L / 800)
    # delta = P * (3 L^2 - 4 a^2) / (48 E I) 근사
    Es = 205000.0
    delta_vert = (data.wheel_load * 1000.0 * (L**3)) / (48.0 * Es * Ix)
    delta_allow = L / 800.0
    dcr_defl = delta_vert / delta_allow if delta_allow > 0 else 999.0
    
    max_dcr = max(dcr_flexure, dcr_fatigue, dcr_defl)
    status = "OK" if max_dcr <= 1.0 else "NG"
    
    return {
        "status": status,
        "governing_dcr": round(max_dcr, 3),
        "max_dcr": round(max_dcr, 3),
        "flexure": {
            "title": "이축 조합 휨응력 및 피로 검토 (Biaxial Flexure & Fatigue Check)",
            "fb_comb_MPa": round(f_comb, 1),
            "F_allow_MPa": round(F_allow, 1),
            "dcr_flexure": round(dcr_flexure, 3),
            "S_act_MPa": round(S_act, 1),
            "F_SR_allow_MPa": round(F_SR, 1),
            "dcr_fatigue": round(dcr_fatigue, 3),
            "dcr": round(max(dcr_flexure, dcr_fatigue), 3)
        },
        "deflection": {
            "title": "크레인 거더 수직 처짐 검토 (Vertical Deflection L/800)",
            "delta_vert_mm": round(delta_vert, 1),
            "delta_allow_mm": round(delta_allow, 1),
            "dcr": round(dcr_defl, 3)
        },
        "details": {
            "crane_loads": {
                "static_wheel_load_kN": data.wheel_load,
                "vert_impact_load_kN": round(P_vert / 1000.0, 1),
                "horiz_impact_load_kN": round(P_horiz / 1000.0, 1),
                "Mx_max_kNm": round(Mx_max / 1e6, 2),
                "My_max_kNm": round(My_max / 1e6, 2)
            },
            "fatigue_parameters": {
                "category": data.fatigue_category,
                "design_cycles": data.cycles,
                "constant_Cf": Cf,
                "threshold_FSR_MPa": round(F_SR, 1)
            }
        },
        "summary": f"크레인 거더 검토: 조합휨 DCR={round(dcr_flexure,2)}, 피로 DCR={round(dcr_fatigue,2)}(허용 {round(F_SR,1)}MPa), 처짐={round(delta_vert,1)}mm ({status})",
        "visual_data": {
            "type": "steel_h",
            "H": H,
            "B": B,
            "tw": tw,
            "tf": tf
        }
    }

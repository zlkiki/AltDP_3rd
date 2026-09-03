"""
강보(H형강) 웨브 개구부(Web Opening) 비렌딜 전단/휨 및 수평 보강스티프너 설계 모듈
"""
import math
from pydantic import BaseModel, Field
from typing import Dict, Any

MODULE_INFO = {
    "id": "steel_composite_web_open",
    "name": "보 웨브 보강 (Web Opening Steel Beam)",
    "category": "steel",
    "group": "composite",
    "submodule": "web_open",
    "description": "H형강 보 웨브 원형/각형 개구부 비렌딜 전단 및 상하부 수평 보강판(Reinforcing Plate) 설계",
    "geomType": "steel_h",
    "template": "steel_h"
}

class SteelWebOpenInput(BaseModel):
    H: float = Field(600.0, description="H형강 높이 (mm)")
    B: float = Field(200.0, description="H형강 폭 (mm)")
    tw: float = Field(11.0, description="웨브 두께 (mm)")
    tf: float = Field(17.0, description="플랜지 두께 (mm)")
    Fy: float = Field(355.0, description="강재 항복강도 (MPa)")
    Mu: float = Field(350.0, description="개구부 위치 계수 모멘트 (kN·m)")
    Vu: float = Field(220.0, description="개구부 위치 계수 전단력 (kN)")
    open_shape: str = Field("rect", description="개구부 형태 (rect/circle)")
    open_height: float = Field(300.0, description="개구부 높이 (mm)")
    open_width: float = Field(450.0, description="개구부 길이 (mm)")
    reinf_thick: float = Field(12.0, description="상하부 수평 보강판 두께 (mm)")
    reinf_width: float = Field(80.0, description="상하부 수평 보강판 폭 (mm)")

def calculate(data: SteelWebOpenInput) -> Dict[str, Any]:
    H = data.H
    B = data.B
    tw = data.tw
    tf = data.tf
    Fy = data.Fy
    Mu = data.Mu * 1e6
    Vu = data.Vu * 1e3
    ho = data.open_height
    ao = data.open_width
    
    # 1. 상·하부 티(Tee) 단면 기하 (개구부 중심 가정)
    s_t = (H - ho) / 2.0  # 티 단면 높이
    
    # 보강판 단면적
    Ar = data.reinf_thick * data.reinf_width
    # 티 단면 유효 단면적
    At = B * tf + (s_t - tf) * tw + Ar
    
    # 2. 전단 강도 검토
    # 티 단면 웨브 유효전단면적 Aw_t = (s_t - tf) * tw
    Aw_t = (s_t - tf) * tw
    # 순수 전단강도 Vpt = 0.6 * Fy * Aw_t
    Vpt = 0.6 * Fy * Aw_t
    
    # 전체 전단강도 Vm = 2 * Vpt (상하부 대칭)
    phi_v = 0.90
    phi_Vn = phi_v * 2.0 * Vpt
    dcr_shear = Vu / phi_Vn if phi_Vn > 0 else 999.0
    
    # 3. 비렌딜 2차 휨모멘트 (M_v = Vu * (ao / 2) * 0.5)
    M_v = Vu * (ao / 4.0)  # N·mm
    # 티 단면 소성휨내력 Mpt
    # 근사 Zt = (B * tf * (s_t - tf/2) + Ar * s_t) * 0.7
    Zt = max(1e4, (B * tf * tf * 0.5 + Aw_t * (s_t / 4.0) + Ar * s_t))
    Mpt = Fy * Zt
    phi_m = 0.90
    phi_Mpt = phi_m * Mpt
    dcr_vierendeel = M_v / phi_Mpt if phi_Mpt > 0 else 999.0
    
    # 4. 전체 휨모멘트 검토 (개구부 감쇠 휨내력)
    # d_chord = H - s_t
    d_chord = H - (s_t / 2.0)
    phi_Mn_global = phi_m * (At * Fy * d_chord)
    dcr_global_m = Mu / phi_Mn_global if phi_Mn_global > 0 else 999.0
    
    max_dcr = max(dcr_shear, dcr_vierendeel, dcr_global_m)
    status = "OK" if max_dcr <= 1.0 else "NG"
    
    return {
        "status": status,
        "governing_dcr": round(max_dcr, 3),
        "max_dcr": round(max_dcr, 3),
        "shear": {
            "title": "개구부 전단강도 검토 (Web Opening Shear Capacity φVn)",
            "Vu_kN": round(Vu / 1000.0, 1),
            "phi_Vn_kN": round(phi_Vn / 1000.0, 1),
            "dcr": round(dcr_shear, 3),
            "phi": phi_v
        },
        "flexure": {
            "title": "비렌딜 및 전체 휨모멘트 검토 (Vierendeel & Global Moment φMn)",
            "Mu_global_kNm": round(Mu / 1e6, 1),
            "phi_Mn_global_kNm": round(phi_Mn_global / 1e6, 1),
            "dcr_global": round(dcr_global_m, 3),
            "M_v_kNm": round(M_v / 1e6, 1),
            "phi_Mpt_kNm": round(phi_Mpt / 1e6, 1),
            "dcr_vierendeel": round(dcr_vierendeel, 3),
            "dcr": round(max(dcr_vierendeel, dcr_global_m), 3)
        },
        "details": {
            "geometry": {
                "open_height_ho_mm": ho,
                "open_width_ao_mm": ao,
                "tee_depth_st_mm": round(s_t, 1),
                "reinf_plate": f"{data.reinf_thick}t × {data.reinf_width}mm",
                "reinf_area_Ar_mm2": round(Ar, 1)
            }
        },
        "summary": f"웨브 개구부 보강 검토: 전단 DCR={round(dcr_shear,2)}, Vierendeel 휨 DCR={round(dcr_vierendeel,2)} ({status})",
        "visual_data": {
            "type": "steel_h",
            "H": H,
            "B": B,
            "tw": tw,
            "tf": tf
        }
    }

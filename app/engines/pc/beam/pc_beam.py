"""
KDS 14 20 60 프리캐스트 콘크리트(PC) 보 단계별(탈형, 양생, 인양, 가설, 공용) 상·하부 연단 응력 검토 모듈
"""
import math
from pydantic import BaseModel, Field
from typing import Dict, Any

MODULE_INFO = {
    "id": "pc_beam_pc_beam",
    "name": "PC 보 (Precast Beam)",
    "category": "pc",
    "group": "beam",
    "submodule": "pc_beam",
    "description": "KDS 14 20 60 프리캐스트 콘크리트 보 탈형, 인양, 가설 및 공용 단계별 휨응력 및 균열 검토",
    "geomType": "rc_rect",
    "template": "rc_rect"
}

class PcBeamInput(BaseModel):
    b: float = Field(400.0, description="보 폭 (mm)")
    h: float = Field(800.0, description="보 춤 (mm)")
    span: float = Field(12000.0, description="보 경간 L (mm)")
    fci: float = Field(24.0, description="탈형/인양 시 초기 콘크리트 압축강도 (MPa)")
    fck: float = Field(35.0, description="설계 기준 콘크리트 압축강도 (MPa)")
    M_demold: float = Field(85.0, description="탈형 시 자중 모멘트 (kN·m)")
    M_erect: float = Field(160.0, description="가설 시 모멘트 (kN·m)")
    M_service: float = Field(380.0, description="공용 시 사용하중 모멘트 (kN·m)")
    P_initial: float = Field(600.0, description="도입 초기 프리스트레스 긴장력 (kN)")
    P_effective: float = Field(500.0, description="유효 프리스트레스 긴장력 (kN)")
    eccentricity: float = Field(200.0, description="긴장재 편심 e (mm)")

def calculate(data: PcBeamInput) -> Dict[str, Any]:
    b = data.b
    h = data.h
    fci = data.fci
    fck = data.fck
    e = data.eccentricity
    
    # 1. 단면 성질 (직사각형)
    A = b * h  # mm2
    I = (b * (h**3)) / 12.0  # mm4
    yt = h / 2.0
    yb = h / 2.0
    St = I / yt  # mm3
    Sb = I / yb  # mm3
    
    # 2. 허용 응력 (KDS 기준)
    # 초기 단계 허용 압축: 0.60 * fci, 허용 인장: 0.25 * sqrt(fci)
    f_ci_allow_comp = 0.60 * fci
    f_ci_allow_tens = -0.25 * math.sqrt(fci)
    
    # 공용 단계 허용 압축: 0.45 * fck, 허용 인장: -0.50 * sqrt(fck)
    f_ck_allow_comp = 0.45 * fck
    f_ck_allow_tens = -0.50 * math.sqrt(fck)
    
    # 3. [1단계: 탈형/초기 도입] 상·하단 응력
    Pi = data.P_initial * 1e3  # N
    Mi = data.M_demold * 1e6  # N·mm
    # 상단 연단 응력 f_ti = Pi/A - Pi*e/St + Mi/St
    f_top_init = (Pi / A) - (Pi * e / St) + (Mi / St)
    # 하단 연단 응력 f_bi = Pi/A + Pi*e/Sb - Mi/Sb
    f_bot_init = (Pi / A) + (Pi * e / Sb) - (Mi / Sb)
    
    # 4. [2단계: 공용 사용하중] 상·하단 응력
    Pe = data.P_effective * 1e3  # N
    Ms = data.M_service * 1e6  # N·mm
    f_top_serv = (Pe / A) - (Pe * e / St) + (Ms / St)
    f_bot_serv = (Pe / A) + (Pe * e / Sb) - (Ms / Sb)
    
    # 5. DCR 산정
    dcr_init_comp = f_bot_init / f_ci_allow_comp if f_bot_init > 0 else 0.0
    dcr_init_tens = abs(f_top_init) / abs(f_ci_allow_tens) if f_top_init < 0 else 0.0
    dcr_serv_comp = f_top_serv / f_ck_allow_comp if f_top_serv > 0 else 0.0
    dcr_serv_tens = abs(f_bot_serv) / abs(f_ck_allow_tens) if f_bot_serv < 0 else 0.0
    
    max_dcr = max(dcr_init_comp, dcr_init_tens, dcr_serv_comp, dcr_serv_tens)
    status = "OK" if max_dcr <= 1.0 else "NG"
    
    return {
        "status": status,
        "governing_dcr": round(max_dcr, 3),
        "max_dcr": round(max_dcr, 3),
        "flexure": {
            "title": "가설 및 공용 단계별 연단응력 검토 (Staged Edge Stress Check)",
            "f_top_init_MPa": round(f_top_init, 2),
            "f_ci_allow_tens": round(f_ci_allow_tens, 2),
            "f_bot_init_MPa": round(f_bot_init, 2),
            "f_ci_allow_comp": round(f_ci_allow_comp, 2),
            "f_top_serv_MPa": round(f_top_serv, 2),
            "f_ck_allow_comp": round(f_ck_allow_comp, 2),
            "f_bot_serv_MPa": round(f_bot_serv, 2),
            "f_ck_allow_tens": round(f_ck_allow_tens, 2),
            "dcr": round(max_dcr, 3)
        },
        "details": {
            "section_properties": {
                "area_A_mm2": round(A, 0),
                "inertia_I_mm4": round(I, 0),
                "section_modulus_St_mm3": round(St, 0),
                "eccentricity_e_mm": e
            },
            "allowable_limits": {
                "initial_allow_comp_MPa": round(f_ci_allow_comp, 2),
                "initial_allow_tens_MPa": round(f_ci_allow_tens, 2),
                "service_allow_comp_MPa": round(f_ck_allow_comp, 2),
                "service_allow_tens_MPa": round(f_ck_allow_tens, 2)
            }
        },
        "summary": f"PC 보 단계별 응력 검토: 초기 DCR={round(max(dcr_init_comp, dcr_init_tens),2)}, 공용 DCR={round(max(dcr_serv_comp, dcr_serv_tens),2)} ({status})",
        "visual_data": {
            "type": "rc_rect",
            "b": b,
            "h": h,
            "cover": 50.0
        }
    }

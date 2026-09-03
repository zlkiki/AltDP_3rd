"""
2개 기둥을 지지하는 직사각형 RC 복합기초(Combined Footing) 해석 및 설계 모듈
"""
import math
from pydantic import BaseModel, Field
from typing import Dict, Any

MODULE_INFO = {
    "id": "rc_footing_com",
    "name": "복합기초 (Combined Footing)",
    "category": "rc",
    "group": "footing",
    "submodule": "com",
    "description": "2개 기둥 하중 도심 일치 및 등분포 지반반력 기반 복합기초 휨/전단 설계",
    "geomType": "rc_footing",
    "template": "rc_footing"
}

class FootingComInput(BaseModel):
    P1: float = Field(800.0, description="기둥1 계수 축력 (kN)")
    P2: float = Field(1200.0, description="기둥2 계수 축력 (kN)")
    col_dist: float = Field(4000.0, description="기둥 간 중심 거리 (mm)")
    c1_width: float = Field(500.0, description="기둥1 폭 (mm)")
    c2_width: float = Field(500.0, description="기둥2 폭 (mm)")
    qa: float = Field(250.0, description="허용 지내력 (kPa)")
    fck: float = Field(27.0, description="콘크리트 압축강도 (MPa)")
    fy: float = Field(400.0, description="철근 항복강도 (MPa)")
    H: float = Field(900.0, description="기초 두께 (mm)")
    B: float = Field(2200.0, description="기초 폭 (mm)")

def calculate(data: FootingComInput) -> Dict[str, Any]:
    P1 = data.P1
    P2 = data.P2
    L_col = data.col_dist
    c1 = data.c1_width
    c2 = data.c2_width
    qa = data.qa
    fck = data.fck
    fy = data.fy
    H = data.H
    B = data.B
    
    # 1. 합력 도심 x_R 산정 (기둥1 중심 기준)
    P_total = P1 + P2
    x_R = (P2 * L_col) / P_total if P_total > 0 else 0.0
    
    # 등분포 지반반력을 위한 최적 기초 길이 L_opt (기둥1 외단에서 캔틸레버 L_cant1 = c1/2 가정)
    L_cant1 = c1 / 2.0
    # 전체 도심이 중앙에 오도록 L 산정: L/2 = L_cant1 + x_R  => L = 2 * (L_cant1 + x_R)
    L_req = 2.0 * (L_cant1 + x_R)
    L_act = max(L_req, L_col + c1/2.0 + c2/2.0 + 500.0)
    
    # 2. 지반반력 검토 (서비스 하중 기준 약 0.75 * Pu)
    P_serv = P_total * 0.75
    A_footing = (B / 1000.0) * (L_act / 1000.0)
    q_act = P_serv / A_footing if A_footing > 0 else 999.0
    dcr_soil = q_act / qa if qa > 0 else 999.0
    
    # 3. 종방향 휨모멘트 산정 (기둥 간 최대 부모멘트)
    w_u = (P_total) / (L_act / 1000.0)  # kN/m
    # 중앙부 부모멘트 근사: M_neg = w_u * L_col^2 / 8 - (P1*L_col/4)
    Mu_neg = abs(0.125 * w_u * ((L_col / 1000.0)**2) * 1.2)  # kN·m
    
    # 휨 내력
    d = H - 80.0
    phi_b = 0.85
    # 상부 배근 14-D25 가정
    As = 14 * 506.7
    a = (As * fy) / (0.85 * fck * B)
    phi_Mn = phi_b * As * fy * (d - a / 2.0) / 1e6  # kN·m
    dcr_flexure = Mu_neg / phi_Mn if phi_Mn > 0 else 999.0
    
    # 4. 1방향 전단 검토
    Vu_max = max(P1, P2) * 0.6  # kN
    phi_v = 0.75
    phi_Vc = phi_v * (1.0 / 6.0) * math.sqrt(fck) * B * d / 1000.0  # kN
    dcr_shear = Vu_max / phi_Vc if phi_Vc > 0 else 999.0
    
    max_dcr = max(dcr_soil, dcr_flexure, dcr_shear)
    status = "OK" if max_dcr <= 1.0 else "NG"
    
    return {
        "status": status,
        "governing_dcr": round(max_dcr, 3),
        "max_dcr": round(max_dcr, 3),
        "soil_bearing": {
            "title": "지반 접지압 검토 (Soil Bearing Pressure)",
            "q_max": round(q_act, 1),
            "qa": qa,
            "dcr": round(dcr_soil, 3)
        },
        "flexure": {
            "title": "종방향 부모멘트 검토 (Negative Flexure φMn)",
            "Mu": round(Mu_neg, 1),
            "phiMn": round(phi_Mn, 1),
            "As": round(As, 1),
            "dcr": round(dcr_flexure, 3),
            "phi": phi_b
        },
        "one_way_shear": {
            "title": "1방향 보전단 검토 (One-way Shear φVc)",
            "Vu": round(Vu_max, 1),
            "phiVc": round(phi_Vc, 1),
            "dcr": round(dcr_shear, 3),
            "phi": phi_v
        },
        "details": {
            "geometry": {
                "P_total_kN": P_total,
                "resultant_center_xR_mm": round(x_R, 1),
                "required_length_L_mm": round(L_act, 0),
                "width_B_mm": B,
                "thickness_H_mm": H,
                "effective_depth_d_mm": round(d, 1)
            }
        },
        "summary": f"복합기초 해석: L={int(L_act)}mm, B={int(B)}mm, 지반 DCR={round(dcr_soil,2)}, 휨 DCR={round(dcr_flexure,2)} ({status})",
        "visual_data": {
            "type": "rc_footing",
            "B": B,
            "L": L_act,
            "H": H,
            "cx": c1,
            "cy": c2
        }
    }

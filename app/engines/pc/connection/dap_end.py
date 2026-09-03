"""
PC 보 단부 턱(Dapped-End Connection) 캔틸레버 노치 전단/휨 및 사인장 균열 제어 철근 설계 모듈
"""
import math
from pydantic import BaseModel, Field
from typing import Dict, Any

MODULE_INFO = {
    "id": "pc_connection_dap_end",
    "name": "PC 단부 노치 접합부 (Dapped-End)",
    "category": "pc",
    "group": "connection",
    "submodule": "dap_end",
    "description": "KDS 14 20 24 / PCI 핸드북 기반 PC 보 노치 단부(Dapped-End) 전단, 휨 및 사인장 균열 제어 스트럿-타이 설계",
    "geomType": "rc_rect",
    "template": "rc_rect"
}

class DapEndInput(BaseModel):
    b: float = Field(400.0, description="보 폭 (mm)")
    H: float = Field(900.0, description="보 전체 높이 (mm)")
    h_nib: float = Field(450.0, description="단부 턱(Nib) 높이 (mm)")
    l_nib: float = Field(300.0, description="단부 턱 길이 (mm)")
    a_v: float = Field(150.0, description="하중 작용점~노치 모서리 거리 (mm)")
    fck: float = Field(35.0, description="콘크리트 압축강도 (MPa)")
    fy: float = Field(400.0, description="철근 항복강도 (MPa)")
    Vu: float = Field(220.0, description="단부 지점 계수 반력 (kN)")
    Nu: float = Field(44.0, description="수평 구속 인장력 (최소 0.2*Vu) (kN)")

def calculate(data: DapEndInput) -> Dict[str, Any]:
    b = data.b
    H = data.H
    hn = data.h_nib
    av = data.a_v
    fck = data.fck
    fy = data.fy
    Vu = data.Vu * 1e3  # N
    Nu = max(data.Nu * 1e3, 0.2 * Vu)  # N
    
    # 1. 턱(Nib) 휨 및 인장 주철근 (Flexure & Tension Rebar, As)
    # d_nib = hn - 40
    d_nib = hn - 40.0
    # Mu_nib = Vu * av + Nu * (hn - d_nib)
    Mu_nib = Vu * av + Nu * (hn - d_nib)  # N·mm
    phi_f = 0.85
    # 필요 주철근 As_flex = Mu / (phi * fy * 0.9 * d_nib) + Nu / (phi * fy)
    As_flex = (Mu_nib / (phi_f * fy * 0.9 * d_nib)) + (Nu / (phi_f * fy))  # mm2
    
    # 2. 노치 전단마찰 철근 (Shear Friction Rebar, Avf)
    phi_v = 0.75
    mu = 1.4  # 모놀리식 타설
    Avf = (Vu / (phi_v * fy * mu)) + (Nu / (phi_v * fy))  # mm2
    
    # 최종 수평 타이 철근 As_h = max(As_flex, Avf)
    As_h_req = max(As_flex, Avf)
    
    # 3. 행거 철근 (Hanger Reinforcement, Ash) - 전단력을 상부 본체로 전달
    # Ash = Vu / (phi * fy)
    Ash_req = Vu / (phi_f * fy)  # mm2
    
    # 4. 노치 모서리 대각선 사인장 균열 제어 철근 (Diagonal Rebar, Ad)
    # Ad = Vu / (phi * fy * sin(45))
    Ad_req = Vu / (phi_f * fy * math.sin(math.radians(45.0)))  # mm2
    
    # 5. 콘크리트 노치 전단 한계 검토 (Vu_max <= 0.2 * fck * b * d_nib)
    Vu_max_limit = 0.2 * fck * b * d_nib
    dcr_conc_limit = Vu / (phi_v * Vu_max_limit) if Vu_max_limit > 0 else 999.0
    
    status = "OK" if dcr_conc_limit <= 1.0 else "NG"
    
    return {
        "status": status,
        "governing_dcr": round(dcr_conc_limit, 3),
        "max_dcr": round(dcr_conc_limit, 3),
        "shear": {
            "title": "노치부 전단 및 콘크리트 전단한계 검토 (Nib Shear Capacity φVn)",
            "Vu_kN": round(Vu / 1000.0, 1),
            "phi_Vn_max_kN": round(phi_v * Vu_max_limit / 1000.0, 1),
            "dcr": round(dcr_conc_limit, 3),
            "phi": phi_v
        },
        "flexure": {
            "title": "턱(Nib) 휨모멘트 및 소요 철근량 (Nib Flexure & Rebar)",
            "Mu_nib_kNm": round(Mu_nib / 1e6, 2),
            "As_h_req_mm2": round(As_h_req, 1),
            "Ash_hanger_req_mm2": round(Ash_req, 1),
            "Ad_diagonal_req_mm2": round(Ad_req, 1),
            "dcr": round(dcr_conc_limit, 3)
        },
        "details": {
            "geometry": {
                "beam_width_b_mm": b,
                "overall_height_H_mm": H,
                "nib_height_hn_mm": hn,
                "nib_length_ln_mm": data.l_nib,
                "shear_span_av_mm": av
            },
            "reinforcement_requirements": {
                "horizontal_tie_As_mm2": round(As_h_req, 1),
                "hanger_rebar_Ash_mm2": round(Ash_req, 1),
                "diagonal_rebar_Ad_mm2": round(Ad_req, 1)
            }
        },
        "summary": f"Dapped-End 설계: 콘크리트 전단한계 DCR={round(dcr_conc_limit,2)}, 수평주근={int(As_h_req)}mm², 행거근={int(Ash_req)}mm², 경사근={int(Ad_req)}mm² ({status})",
        "visual_data": {
            "type": "rc_rect",
            "b": b,
            "h": H,
            "cover": 40.0
        }
    }

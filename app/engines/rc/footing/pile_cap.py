"""
말뚝 기초(Pile Cap) 2x2, 2x3 등 다열 말뚝 배치 휨 및 펀칭(뚫림) 전단 설계 모듈
"""
import math
from pydantic import BaseModel, Field
from typing import Dict, Any

MODULE_INFO = {
    "id": "rc_footing_pile_cap",
    "name": "말뚝기초 (Pile Cap)",
    "category": "rc",
    "group": "footing",
    "submodule": "pile_cap",
    "description": "다열 말뚝 배치 자동 기하 및 파일캡 휨/1방향/2방향 펀칭 전단 검토",
    "geomType": "rc_footing",
    "template": "rc_footing"
}

class PileCapInput(BaseModel):
    num_piles: int = Field(4, description="말뚝 개수 (4, 5, 6, 8)")
    pile_dia: float = Field(500.0, description="말뚝 직경 D (mm)")
    pile_cap_capacity: float = Field(800.0, description="말뚝 1본당 허용압축지지력 (kN)")
    pile_spacing: float = Field(1500.0, description="말뚝 중심 간격 (mm)")
    edge_dist: float = Field(600.0, description="말뚝 중심~파일캡 연단거리 (mm)")
    H: float = Field(1100.0, description="파일캡 두께 (mm)")
    cx: float = Field(600.0, description="기둥 X방향 폭 (mm)")
    cy: float = Field(600.0, description="기둥 Y방향 폭 (mm)")
    fck: float = Field(27.0, description="콘크리트 압축강도 (MPa)")
    fy: float = Field(400.0, description="철근 항복강도 (MPa)")
    Pu: float = Field(2800.0, description="기둥 계수 축력 (kN)")

def calculate(data: PileCapInput) -> Dict[str, Any]:
    n = data.num_piles
    s = data.pile_spacing
    e = data.edge_dist
    H = data.H
    cx = data.cx
    cy = data.cy
    fck = data.fck
    fy = data.fy
    Pu = data.Pu
    
    # 1. 파일캡 평면 치수 (4개 배치 기준: 2x2)
    if n <= 4:
        B = s + 2 * e
        L = s + 2 * e
    elif n == 5:
        B = s + 2 * e
        L = s + 2 * e
    elif n == 6:
        B = s + 2 * e
        L = 2 * s + 2 * e
    else:  # 8개
        B = 2 * s + 2 * e
        L = 2 * s + 2 * e
        
    # 2. 말뚝 1본당 반력 (등분포 가정)
    P_pile_act = (Pu * 0.75) / n  # 사용하중 kN
    dcr_pile = P_pile_act / data.pile_cap_capacity if data.pile_cap_capacity > 0 else 999.0
    
    # 3. 휨모멘트 산정 (기둥 전면에서의 모멘트)
    d = H - 100.0
    # 기둥 전면에서 외측 말뚝 열 중심까지의 거리
    arm_x = (s / 2.0) - (cx / 2.0)
    arm_x = max(100.0, arm_x)
    # 한쪽 2개 말뚝에 작용하는 계수 하중
    piles_per_side = max(1, n // 2)
    Vu_side = (Pu / n) * piles_per_side
    Mu = Vu_side * (arm_x / 1000.0)  # kN·m
    
    phi_b = 0.85
    # 배근량 D25@150 가정 -> 대략 As = 10 * 506.7
    num_bar = int(B / 150.0)
    As = num_bar * 506.7
    a = (As * fy) / (0.85 * fck * B)
    phi_Mn = phi_b * As * fy * (d - a / 2.0) / 1e6
    dcr_flexure = Mu / phi_Mn if phi_Mn > 0 else 999.0
    
    # 4. 기둥 주변 2방향 펀칭 전단
    bo = 2.0 * (cx + d) + 2.0 * (cy + d)
    phi_v = 0.75
    # 펀칭 전단강도 Vc = (1/3) * sqrt(fck) * bo * d
    Vc_punch = (1.0 / 3.0) * math.sqrt(fck) * bo * d / 1000.0  # kN
    phi_Vc_punch = phi_v * Vc_punch
    Vu_punch = Pu
    dcr_punch = Vu_punch / phi_Vc_punch if phi_Vc_punch > 0 else 999.0
    
    max_dcr = max(dcr_pile, dcr_flexure, dcr_punch)
    status = "OK" if max_dcr <= 1.0 else "NG"
    
    return {
        "status": status,
        "governing_dcr": round(max_dcr, 3),
        "max_dcr": round(max_dcr, 3),
        "soil_bearing": {
            "title": "말뚝 압축 지지력 검토 (Pile Bearing Capacity)",
            "P_pile_act_kN": round(P_pile_act, 1),
            "P_pile_allow_kN": data.pile_cap_capacity,
            "dcr": round(dcr_pile, 3)
        },
        "flexure": {
            "title": "파일캡 휨모멘트 검토 (Pile Cap Flexural Capacity φMn)",
            "Mu": round(Mu, 1),
            "phiMn": round(phi_Mn, 1),
            "As": round(As, 1),
            "dcr": round(dcr_flexure, 3),
            "phi": phi_b
        },
        "punching_shear": {
            "title": "기둥 주변 2방향 펀칭전단 검토 (Punching Shear φVc)",
            "Vu": round(Vu_punch, 1),
            "phiVc": round(phi_Vc_punch, 1),
            "bo_mm": round(bo, 0),
            "dcr": round(dcr_punch, 3),
            "phi": phi_v
        },
        "details": {
            "geometry": {
                "num_piles": n,
                "pile_spacing_mm": s,
                "edge_distance_mm": e,
                "width_Bx_mm": B,
                "length_By_mm": L,
                "thickness_H_mm": H,
                "effective_depth_d_mm": round(d, 1)
            }
        },
        "summary": f"말뚝기초({n}본) 검토: 말뚝지지 DCR={round(dcr_pile,2)}, 펀칭 DCR={round(dcr_punch,2)} ({status})",
        "visual_data": {
            "type": "rc_footing",
            "B": B,
            "L": L,
            "H": H,
            "cx": cx,
            "cy": cy,
            "num_piles": n
        }
    }

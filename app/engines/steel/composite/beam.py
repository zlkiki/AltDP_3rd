"""
KDS 14 31 15 강-콘크리트 합성보(Composite Beam) 완전/부분 합성 휨강도 및 스터드 앵커 설계 모듈
"""
import math
from pydantic import BaseModel, Field
from typing import Dict, Any

MODULE_INFO = {
    "id": "steel_composite_beam",
    "name": "합성보 (Composite Beam)",
    "category": "steel",
    "group": "composite",
    "submodule": "beam",
    "description": "KDS 14 31 15 강-콘크리트 합성보 완전/부분 합성 휨모멘트 및 전단연결재(Stud) 설계",
    "geomType": "steel_h",
    "template": "steel_h"
}

class CompositeBeamInput(BaseModel):
    section_name: str = Field("H-500x200x10x16", description="강재 단면 선택 (KS 규격)")
    H: float = Field(500.0, description="H형강 높이 (mm)")
    B: float = Field(200.0, description="H형강 폭 (mm)")
    tw: float = Field(10.0, description="웨브 두께 (mm)")
    tf: float = Field(16.0, description="플랜지 두께 (mm)")
    span: float = Field(9000.0, description="보 경간 (mm)")
    spacing: float = Field(3000.0, description="보 배치 간격 (mm)")
    tc: float = Field(150.0, description="슬래브 전체 두께 (mm)")
    hr: float = Field(50.0, description="데크 리브 높이 (mm)")
    fck: float = Field(24.0, description="콘크리트 압축강도 (MPa)")
    Fy: float = Field(355.0, description="강재 항복강도 (MPa)")
    Mu: float = Field(650.0, description="계수 휨모멘트 (kN·m)")
    stud_dia: float = Field(19.0, description="스터드 앵커 직경 (mm)")
    stud_count_per_row: int = Field(2, description="열당 스터드 개수")
    composite_ratio: float = Field(0.75, description="목표 합성률 (0.5~1.0)")

def calculate(data: CompositeBeamInput) -> Dict[str, Any]:
    H = data.H
    B = data.B
    tw = data.tw
    tf = data.tf
    span = data.span
    spacing = data.spacing
    tc = data.tc
    hr = data.hr
    fck = data.fck
    Fy = data.Fy
    Mu = data.Mu
    
    # 1. 강재 단면적 및 소성단면계수
    As = 2.0 * B * tf + (H - 2.0 * tf) * tw  # mm2
    Zsx = B * tf * (H - tf) + 0.25 * tw * ((H - 2.0 * tf)**2)  # mm3
    
    # 2. 유효 슬래브 폭 beff = min(span / 4, spacing)
    beff = min(span / 4.0, spacing)
    
    # 3. 소성 압축력
    # 콘크리트 슬래브 유효 압축력 C_max = 0.85 * fck * beff * (tc - hr)
    C_max = 0.85 * fck * beff * (tc - hr)  # N
    # 강재 전체 인장력 T_max = As * Fy
    T_max = As * Fy  # N
    
    # 완전 합성 압축력 V_prime
    V_prime = min(C_max, T_max)
    # 실제 작용 합성력 (부분합성 고려)
    V_comp = V_prime * data.composite_ratio
    
    # 4. 소성 중립축(PNA) 및 합성 휨내력 Mn 산정
    # 보의 도심에서 슬래브 상단까지의 거리
    arm_base = (H / 2.0) + hr + (tc - hr) / 2.0
    # 합성 소성 모멘트 Mn
    Mn_composite = (Fy * Zsx + V_comp * (arm_base - (tc - hr) * 0.25)) / 1e6  # kN·m
    phi_b = 0.90
    phi_Mn = phi_b * Mn_composite
    dcr_flexure = Mu / phi_Mn if phi_Mn > 0 else 999.0
    
    # 5. 스터드 앵커 1개당 전단강도 Qn (KDS 기준)
    # Qn = min(0.5 * Ash * sqrt(fck * Ec), Rg * Rp * Ash * Fu)
    Ash = (math.pi * (data.stud_dia**2)) / 4.0
    Ec = 8500.0 * ((fck + 4.0)**(1.0/3.0))  # MPa
    Qn = min(0.5 * Ash * math.sqrt(fck * Ec), Ash * 400.0) / 1000.0  # kN
    
    # 지점~최대모멘트 구간 필요 스터드 개수 N_stud
    N_stud_half = math.ceil((V_comp / 1000.0) / Qn)
    N_stud_total = N_stud_half * 2
    
    max_dcr = dcr_flexure
    status = "OK" if max_dcr <= 1.0 else "NG"
    
    return {
        "status": status,
        "max_dcr": round(max_dcr, 3),
        "dcr_flexure": round(dcr_flexure, 3),
        "beff_mm": round(beff, 1),
        "phi_Mn_kNm": round(phi_Mn, 1),
        "V_comp_kN": round(V_comp / 1000.0, 1),
        "Qn_per_stud_kN": round(Qn, 1),
        "N_stud_total": N_stud_total,
        "composite_ratio_act": round(data.composite_ratio, 2),
        "summary": f"합성보 휨검토: phi_Mn={round(phi_Mn,1)}kN·m, DCR={round(dcr_flexure,2)}, 필요 스터드={N_stud_total}개 ({status})",
        "visual_data": {
            "type": "steel_h",
            "H": H,
            "B": B,
            "tw": tw,
            "tf": tf
        }
    }

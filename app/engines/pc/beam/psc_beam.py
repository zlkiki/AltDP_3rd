"""
KDS 14 20 60 포스트텐션 프리스트레스트 콘크리트(PSC) 거더 긴장력 손실 및 극한 휨/전단 설계 모듈
"""
import math
from pydantic import BaseModel, Field
from typing import Dict, Any

MODULE_INFO = {
    "id": "pc_beam_psc_beam",
    "name": "PSC 거더 (Post-Tension Girder)",
    "category": "pc",
    "group": "beam",
    "submodule": "psc_beam",
    "description": "KDS 14 20 60 포스트텐션 긴장력 즉시/장기 손실, 극한 휨모멘트(Mn) 및 복부 전단(Vcw, Vci) 설계",
    "geomType": "rc_rect",
    "template": "rc_rect"
}

class PscBeamInput(BaseModel):
    b_top: float = Field(600.0, description="상부 플랜지 폭 (mm)")
    h_top: float = Field(150.0, description="상부 플랜지 두께 (mm)")
    bw: float = Field(250.0, description="복부 폭 (mm)")
    H: float = Field(1200.0, description="거더 전체 높이 (mm)")
    span: float = Field(20000.0, description="거더 경간 (mm)")
    fck: float = Field(40.0, description="콘크리트 압축강도 (MPa)")
    fpu: float = Field(1860.0, description="긴장재 인장강도 (MPa)")
    Aps: float = Field(1400.0, description="전체 텐던 단면적 (mm²)")
    dp: float = Field(1050.0, description="상단에서 텐던 도심까지 거리 (mm)")
    Mu: float = Field(1800.0, description="계수 휨모멘트 (kN·m)")
    Vu: float = Field(450.0, description="계수 전단력 (kN)")
    friction_mu: float = Field(0.20, description="곡률 마찰계수 μ")
    wobble_k: float = Field(0.0020, description="파상 마찰계수 k (/m)")

def calculate(data: PscBeamInput) -> Dict[str, Any]:
    b = data.b_top
    hf = data.h_top
    bw = data.bw
    H = data.H
    fck = data.fck
    fpu = data.fpu
    Aps = data.Aps
    dp = data.dp
    Mu = data.Mu
    Vu = data.Vu
    
    # 1. 텐던 긴장력 손실율 산정
    # 즉시 손실: 마찰 손실 delta_f_fric = fpo * (1 - e^-(mu*alpha + k*L))
    L = data.span / 1000.0  # m
    alpha = 0.15  # rad
    fpo = 0.75 * fpu  # MPa (초기 긴장응력)
    loss_fric_ratio = 1.0 - math.exp(-(data.friction_mu * alpha + data.wobble_k * L))
    
    # 정착구 미끄럼 및 탄성수축 손실 근사 (5%)
    # 장기 손실: 크리프, 건조수축, 릴랙세이션 (약 15%)
    loss_total_ratio = loss_fric_ratio + 0.05 + 0.15
    fpe = fpo * (1.0 - loss_total_ratio)  # 유효 프리스트레스 응력
    
    # 2. 극한 상태 텐던 응력 fps (KDS 식)
    # rho_p = Aps / (b * dp)
    rho_p = Aps / (b * dp)
    gamma_p = 0.40  # 저이완 강연선
    beta1 = 0.85 - 0.007 * (fck - 28.0) if fck > 28.0 else 0.85
    beta1 = max(0.65, min(0.85, beta1))
    fps = fpu * (1.0 - (gamma_p / beta1) * (rho_p * fpu / fck))
    
    # 3. 극한 휨내력 Mn 산정
    # a = (Aps * fps) / (0.85 * fck * b)
    a = (Aps * fps) / (0.85 * fck * b)
    Mn = Aps * fps * (dp - a / 2.0) / 1e6  # kN·m
    phi_b = 0.85
    phi_Mn = phi_b * Mn
    dcr_flexure = Mu / phi_Mn if phi_Mn > 0 else 999.0
    
    # 4. 전단강도 Vcw (복부 전단균열 강도 KDS 식)
    # fpc = Pe / Ac
    Ac = b * hf + bw * (H - hf)
    Pe = Aps * fpe  # N
    fpc = Pe / Ac
    Vcw = (0.29 * math.sqrt(fck) + 0.3 * fpc) * bw * dp / 1000.0  # kN
    phi_v = 0.75
    # 스터럽 2-D13@150 가정
    Vs = (2.0 * 126.7 * 400.0 * dp / 150.0) / 1000.0  # kN
    phi_Vn = phi_v * (Vcw + Vs)
    dcr_shear = Vu / phi_Vn if phi_Vn > 0 else 999.0
    
    max_dcr = max(dcr_flexure, dcr_shear)
    status = "OK" if max_dcr <= 1.0 else "NG"
    
    return {
        "status": status,
        "governing_dcr": round(max_dcr, 3),
        "max_dcr": round(max_dcr, 3),
        "flexure": {
            "title": "PSC 극한 휨모멘트 내력 검토 (Flexural Capacity φMn)",
            "Mu_kNm": Mu,
            "phi_Mn_kNm": round(phi_Mn, 1),
            "fps_MPa": round(fps, 1),
            "fpe_MPa": round(fpe, 1),
            "dcr": round(dcr_flexure, 3),
            "phi": phi_b
        },
        "shear": {
            "title": "복부 전단균열 및 전단보강근 검토 (Shear Capacity φVn)",
            "Vu_kN": Vu,
            "phi_Vn_kN": round(phi_Vn, 1),
            "Vcw_kN": round(Vcw, 1),
            "Vs_kN": round(Vs, 1),
            "dcr": round(dcr_shear, 3),
            "phi": phi_v
        },
        "details": {
            "prestress_losses": {
                "initial_fpo_MPa": round(fpo, 1),
                "friction_loss_ratio": round(loss_fric_ratio, 4),
                "total_loss_ratio": round(loss_total_ratio, 4),
                "effective_fpe_MPa": round(fpe, 1),
                "loss_percent": round(loss_total_ratio * 100.0, 1)
            },
            "tendon_properties": {
                "Aps_mm2": Aps,
                "fpu_MPa": fpu,
                "dp_mm": dp,
                "equivalent_stress_block_a": round(a, 1)
            }
        },
        "summary": f"포스트텐션 PSC 거더: 손실률={round(loss_total_ratio*100,1)}%, 휨 DCR={round(dcr_flexure,2)}, 전단 DCR={round(dcr_shear,2)} ({status})",
        "visual_data": {
            "type": "rc_tsect",
            "b": data.b_top,
            "h": data.H,
            "b_w": data.bw,
            "h_f": data.h_top,
            "cover": 40.0
        }
    }

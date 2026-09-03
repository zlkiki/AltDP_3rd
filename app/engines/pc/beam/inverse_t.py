"""
PC 역T형 거더(Inverted T-Beam) 하부 플랜지 보 턱(Ledge) 집중 지압 및 비틀림(Torsion) 설계 모듈
"""
import math
from pydantic import BaseModel, Field
from typing import Dict, Any

MODULE_INFO = {
    "id": "pc_beam_inverse_t",
    "name": "역T형 PC 보 (Inverse-T Beam)",
    "category": "pc",
    "group": "beam",
    "submodule": "inverse_t",
    "description": "PC 역T형 거더 하부 돌출 턱(Ledge) 집중 지압, 휨/펀칭 전단 및 편심 하중 비틀림 설계",
    "geomType": "rc_tsect",
    "template": "rc_tsect"
}

class InverseTBeamInput(BaseModel):
    bw: float = Field(400.0, description="상부 복부 폭 (mm)")
    H: float = Field(900.0, description="보 전체 높이 (mm)")
    bf_ledge: float = Field(200.0, description="하부 턱(Ledge) 돌출 폭 (mm)")
    hf_ledge: float = Field(250.0, description="하부 턱 두께 (mm)")
    fck: float = Field(35.0, description="콘크리트 압축강도 (MPa)")
    fy: float = Field(400.0, description="철근 항복강도 (MPa)")
    Pu_ledge: float = Field(120.0, description="턱에 작용하는 집중 계수하중 (kN)")
    pad_b: float = Field(150.0, description="지압 패드 폭 (mm)")
    pad_l: float = Field(200.0, description="지압 패드 길이 (mm)")
    Tu: float = Field(45.0, description="작용 계수 비틀림모멘트 (kN·m)")

def calculate(data: InverseTBeamInput) -> Dict[str, Any]:
    bw = data.bw
    H = data.H
    bf = data.bf_ledge
    hf = data.hf_ledge
    fck = data.fck
    fy = data.fy
    Pu = data.Pu_ledge * 1e3  # N
    Tu = data.Tu * 1e6  # N·mm
    
    # 1. 하부 턱(Ledge) 콘크리트 국부 지압 검토
    A_pad = data.pad_b * data.pad_l
    phi_bearing = 0.65
    Pnb = phi_bearing * 0.85 * fck * A_pad  # N
    dcr_bearing = Pu / Pnb if Pnb > 0 else 999.0
    
    # 2. 턱(Ledge) 펀칭(2방향) 전단 검토 (KDS 식)
    # 유효높이 d_ledge = hf - 40
    d_ledge = hf - 40.0
    # 위험단면 둘레 bo_ledge = pad_l + 2 * (pad_b + d_ledge)
    bo_ledge = data.pad_l + 2.0 * (data.pad_b + d_ledge)
    phi_v = 0.75
    Vn_punch = (1.0 / 3.0) * math.sqrt(fck) * bo_ledge * d_ledge  # N
    phi_Vn_punch = phi_v * Vn_punch
    dcr_punch = Pu / phi_Vn_punch if phi_Vn_punch > 0 else 999.0
    
    # 3. 턱(Ledge) 휨/행거 철근(Hanger Bar) 설계
    # 휨모멘트 M_ledge = Pu * (bf - pad_b/2)
    arm = bf - data.pad_b / 2.0
    Mu_ledge = Pu * arm  # N·mm
    # 필요 철근량 As_req = Mu / (0.85 * fy * 0.9 * d_ledge)
    As_req = Mu_ledge / (0.85 * fy * 0.9 * d_ledge)
    
    # 4. 역T형 단면 균열 비틀림모멘트 Tcr
    # Acp = bw * H + 2 * bf * hf
    Acp = bw * H + 2.0 * bf * hf
    Pcp = 2.0 * (bw + H) + 4.0 * bf
    Tcr = (1.0 / 3.0) * math.sqrt(fck) * ((Acp**2) / Pcp)  # N·mm
    phi_t = 0.75
    phi_Tn_cr = phi_t * Tcr
    dcr_torsion = Tu / phi_Tn_cr if phi_Tn_cr > 0 else 999.0
    
    max_dcr = max(dcr_bearing, dcr_punch, dcr_torsion)
    status = "OK" if max_dcr <= 1.0 else "NG"
    
    return {
        "status": status,
        "max_dcr": round(max_dcr, 3),
        "dcr_bearing": round(dcr_bearing, 3),
        "dcr_punch": round(dcr_punch, 3),
        "dcr_torsion": round(dcr_torsion, 3),
        "As_hanger_req_mm2": round(As_req, 1),
        "phi_Vn_punch_kN": round(phi_Vn_punch / 1000.0, 1),
        "phi_Tcr_kNm": round(phi_Tn_cr / 1e6, 1),
        "summary": f"역T형 Ledge 검토: 지압 DCR={round(dcr_bearing,2)}, 턱펀칭 DCR={round(dcr_punch,2)}, 비틀림 DCR={round(dcr_torsion,2)} ({status})",
        "visual_data": {
            "type": "rc_tsect",
            "b": bw + 2 * bf,
            "h": H,
            "b_w": bw,
            "h_f": hf,
            "cover": 40.0,
            "top_rebar_count": 2,
            "bot_rebar_count": 4
        }
    }

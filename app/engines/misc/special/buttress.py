"""
부벽식 옹벽(Buttressed Retaining Wall) 수평 토압 지지 T형 리브(Buttress) 휨/전단 설계 모듈
"""
import math
from pydantic import BaseModel, Field
from typing import Dict, Any

MODULE_INFO = {
    "id": "misc_special_buttress",
    "name": "버트레스 (Buttress)",
    "category": "misc",
    "group": "special",
    "submodule": "buttress",
    "description": "고높이 옹벽 전면벽 지지 T형/삼각형 단면 부벽(Buttress) 캔틸레버 휨모멘트 및 인장/전단 설계",
    "geomType": "rc_tsect",
    "template": "rc_tsect"
}

class ButtressInput(BaseModel):
    H_wall: float = Field(7000.0, description="옹벽 전체 높이 (mm)")
    spacing: float = Field(4000.0, description="부벽 간격 S (mm)")
    t_stem: float = Field(400.0, description="전면벽 두께 (mm)")
    t_rib: float = Field(500.0, description="부벽(리브) 두께 bw (mm)")
    b_rib_bot: float = Field(3500.0, description="부벽 하단 돌출 폭 (mm)")
    soil_gamma: float = Field(19.0, description="흙의 단위중량 (kN/m³)")
    soil_phi: float = Field(30.0, description="흙 내부마찰각 (deg)")
    fck: float = Field(27.0, description="콘크리트 압축강도 (MPa)")
    fy: float = Field(400.0, description="철근 항복강도 (MPa)")
    rebar_main: str = Field("12-D25", description="부벽 경사 인장 주철근 (수량-직경)")

def calculate(data: ButtressInput) -> Dict[str, Any]:
    H = data.H_wall / 1000.0  # m
    S = data.spacing / 1000.0  # m
    bw = data.t_rib
    b_bot = data.b_rib_bot
    fck = data.fck
    fy = data.fy
    
    # 1. 랭킨 주동토압 Ka
    phi_rad = math.radians(data.soil_phi)
    Ka = (1.0 - math.sin(phi_rad)) / (1.0 + math.sin(phi_rad))
    
    # 2. 부벽 1개가 분담하는 수평 토압 총력 및 전도 휨모멘트
    # 삼각형 토압 합력 P_total = 0.5 * Ka * gamma * H^2 * S
    Pa_total = 0.5 * Ka * data.soil_gamma * (H**2) * S  # kN
    # 기부 계수 휨모멘트 Mu = 1.6 * Pa_total * (H / 3)
    Mu = 1.6 * Pa_total * (H / 3.0)  # kN·m
    Vu = 1.6 * Pa_total  # kN
    
    # 3. 부벽 기부 휨내력 phi_Mn (T형 단면 거동, 인장측은 경사 외단)
    # 유효높이 d = b_bot - 100
    d = b_bot - 100.0  # mm
    
    # 주철근 단면적 As
    num_bars = 12
    db = 25.0
    if "-" in data.rebar_main:
        try:
            parts = data.rebar_main.split("-")
            num_bars = int(parts[0])
            db = float(parts[1].replace("D", "").replace("d", ""))
        except:
            pass
    ab = (math.pi * db * db) / 4.0
    As = num_bars * ab  # mm2
    
    # 압축측은 전면벽 플랜지 (유효폭 beff = min(S*1000, 12*t_stem + bw))
    beff = min(S * 1000.0, 12.0 * data.t_stem + bw)
    a = (As * fy) / (0.85 * fck * beff)
    
    phi_b = 0.85
    Mn = As * fy * (d - a / 2.0) / 1e6  # kN·m
    phi_Mn = phi_b * Mn
    dcr_flexure = Mu / phi_Mn if phi_Mn > 0 else 999.0
    
    # 4. 전단강도 검토
    phi_v = 0.75
    Vc = (1.0 / 6.0) * math.sqrt(fck) * bw * d / 1000.0  # kN
    # 스터럽 4Leg-D13@200 가정
    Vs = (4.0 * 126.7 * 400.0 * d / 200.0) / 1000.0
    phi_Vn = phi_v * (Vc + Vs)
    dcr_shear = Vu / phi_Vn if phi_Vn > 0 else 999.0
    
    max_dcr = max(dcr_flexure, dcr_shear)
    status = "OK" if max_dcr <= 1.0 else "NG"
    
    return {
        "status": status,
        "max_dcr": round(max_dcr, 3),
        "dcr_flexure": round(dcr_flexure, 3),
        "dcr_shear": round(dcr_shear, 3),
        "Mu_kNm": round(Mu, 1),
        "phi_Mn_kNm": round(phi_Mn, 1),
        "Vu_kN": round(Vu, 1),
        "phi_Vn_kN": round(phi_Vn, 1),
        "summary": f"부벽(Buttress) 검토: Mu={round(Mu,1)}kN·m, 휨 DCR={round(dcr_flexure,2)}, 전단 DCR={round(dcr_shear,2)} ({status})",
        "visual_data": {
            "type": "rc_tsect",
            "b": beff,
            "h": b_bot,
            "b_w": bw,
            "h_f": data.t_stem,
            "cover": 80.0,
            "top_rebar_count": 4,
            "bot_rebar_count": num_bars
        }
    }

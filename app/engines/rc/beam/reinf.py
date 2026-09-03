# app/engines/rc/beam/reinf.py
"""RC Beam Detailed Rebar Layer / Fiber Flexure & Shear Engine - KDS 14 20."""
import math
from typing import Dict, Any, List
from pydantic import BaseModel, Field

from app.engines.common.kds_concrete import REBAR_FY, REBAR_AREA, calc_beta1, calc_eta, get_eps_cu

MODULE_INFO = {
    "id": "reinf",
    "name": "배근상세 (Rebar Detail)",
    "category": "rc",
    "group": "beam",
    "geomType": "rc_rect",
    "description": "상부 1/2단, 하부 1/2단 및 측면 표피철근(Side Bar)의 다단 레이어별 정밀 평형해석 및 균열/휨 검토"
}


class BeamReinfInputSchema(BaseModel):
    b: float = Field(450.0, description="보 폭 b (mm)")
    h: float = Field(700.0, description="보 춤 h (mm)")
    fck: float = Field(27.0, description="콘크리트 압축강도 (MPa)")
    rebar_grade: str = Field("SD400", description="철근 강종")
    cover: float = Field(40.0, description="피복 두께 (mm)")
    
    # Layer Rebars
    top_layer1_dia: int = Field(25, description="상부 1단 직경 (mm)")
    top_layer1_num: int = Field(4, description="상부 1단 개수 (EA)")
    top_layer2_dia: int = Field(22, description="상부 2단 직경 (mm)")
    top_layer2_num: int = Field(2, description="상부 2단 개수 (EA)")
    
    bot_layer1_dia: int = Field(25, description="하부 1단 직경 (mm)")
    bot_layer1_num: int = Field(4, description="하부 1단 개수 (EA)")
    bot_layer2_dia: int = Field(22, description="하부 2단 직경 (mm)")
    bot_layer2_num: int = Field(2, description="하부 2단 개수 (EA)")
    
    side_dia: int = Field(13, description="측면 표피철근 직경 (mm)")
    side_num: int = Field(2, description="측면 표피철근 단 수 (단당 2EA)")
    
    Mu: float = Field(450.0, description="소요 휨모멘트 Mu (kN*m)")
    Vu: float = Field(200.0, description="소요 전단력 Vu (kN)")
    stirrup_dia: int = Field(10, description="스터럽 직경 (mm)")
    stirrup_spacing: float = Field(150.0, description="스터럽 간격 (mm)")


def calculate(data: Dict[str, Any]) -> Dict[str, Any]:
    b = float(data.get("b", 450.0))
    h = float(data.get("h", 700.0))
    fck = float(data.get("fck", 27.0))
    rebar_grade = str(data.get("rebar_grade", "SD400"))
    fy = REBAR_FY.get(rebar_grade, 400.0)
    cover = float(data.get("cover", 40.0))
    
    Mu_kNm = float(data.get("Mu", 450.0))
    Vu_kN = float(data.get("Vu", 200.0))
    stirrup_dia = int(data.get("stirrup_dia", 10))
    stirrup_spacing = float(data.get("stirrup_spacing", 150.0))
    
    # 1. Coordinate Placement of Layers (y from top fiber: 0 = top, h = bottom)
    layers = []
    
    # Top Layer 1
    d_t1 = cover + stirrup_dia + int(data.get("top_layer1_dia", 25)) / 2.0
    n_t1 = int(data.get("top_layer1_num", 4))
    if n_t1 > 0:
        layers.append({"d": d_t1, "As": n_t1 * REBAR_AREA.get(int(data.get("top_layer1_dia", 25)), 506.7), "desc": "Top Layer 1"})
        
    # Top Layer 2
    d_t2 = d_t1 + 25.0 + int(data.get("top_layer2_dia", 22))
    n_t2 = int(data.get("top_layer2_num", 2))
    if n_t2 > 0:
        layers.append({"d": d_t2, "As": n_t2 * REBAR_AREA.get(int(data.get("top_layer2_dia", 22)), 387.1), "desc": "Top Layer 2"})
        
    # Bottom Layer 1
    d_b1 = h - (cover + stirrup_dia + int(data.get("bot_layer1_dia", 25)) / 2.0)
    n_b1 = int(data.get("bot_layer1_num", 4))
    if n_b1 > 0:
        layers.append({"d": d_b1, "As": n_b1 * REBAR_AREA.get(int(data.get("bot_layer1_dia", 25)), 506.7), "desc": "Bot Layer 1"})
        
    # Bottom Layer 2
    d_b2 = d_b1 - (25.0 + int(data.get("bot_layer2_dia", 22)))
    n_b2 = int(data.get("bot_layer2_num", 2))
    if n_b2 > 0:
        layers.append({"d": d_b2, "As": n_b2 * REBAR_AREA.get(int(data.get("bot_layer2_dia", 22)), 387.1), "desc": "Bot Layer 2"})
        
    # Side Bars
    side_num = int(data.get("side_num", 2))
    side_dia = int(data.get("side_dia", 13))
    if side_num > 0:
        step = (d_b2 - d_t2) / (side_num + 1)
        for i in range(1, side_num + 1):
            d_s = d_t2 + step * i
            layers.append({"d": d_s, "As": 2 * REBAR_AREA.get(side_dia, 126.7), "desc": f"Side Bar {i}"})
            
    # 2. Multi-Layer Fiber Equilibrium (Positive Flexure)
    beta1 = calc_beta1(fck)
    eta = calc_eta(fck)
    ecu = get_eps_cu(fck)
    sb = eta * 0.85 * fck
    Es = 200000.0
    
    # Bisection on neutral axis c
    c_low, c_high = 1.0, h
    c_res = h / 2.0
    
    for _ in range(40):
        c_mid = (c_low + c_high) / 2.0
        a = beta1 * c_mid
        Cc = sb * a * b
        
        Fs_total = 0.0
        for lay in layers:
            eps_i = ecu * (lay["d"] - c_mid) / c_mid if c_mid > 0 else 0.0
            fs_i = max(-fy, min(fy, eps_i * Es))
            fc_i = sb if lay["d"] <= a else 0.0
            Fs_total += lay["As"] * (fs_i - fc_i)
            
        # Equilibrium: Fs_total (tension positive) - Cc = 0
        if Fs_total > Cc:
            c_low = c_mid
        else:
            c_high = c_mid
            c_res = c_mid
            
    a_res = beta1 * c_res
    Cc_res = sb * a_res * b
    Mn = Cc_res * (a_res / 2.0)
    for lay in layers:
        eps_i = ecu * (lay["d"] - c_res) / c_res if c_res > 0 else 0.0
        fs_i = max(-fy, min(fy, eps_i * Es))
        fc_i = sb if lay["d"] <= a_res else 0.0
        Mn += lay["As"] * (fs_i - fc_i) * lay["d"]
        
    d_max = max(lay["d"] for lay in layers)
    eps_t = ecu * (d_max - c_res) / c_res if c_res > 0 else 0.005
    phi_flex = 0.85 if eps_t >= 0.005 else (0.65 + 0.20 * (eps_t - 0.002) / 0.003 if eps_t > 0.002 else 0.65)
    
    phiMn_kNm = phi_flex * abs(Mn) * 1e-6
    dcr_flex = abs(Mu_kNm) / phiMn_kNm if phiMn_kNm > 0 else 999.0
    
    # 3. Shear Check
    d_eff = d_b1
    Vc = (1.0 / 6.0) * math.sqrt(fck) * b * d_eff * 1e-3
    Av = 2 * REBAR_AREA.get(stirrup_dia, 71.3)
    Vs = (Av * min(fy, 500.0) * d_eff / stirrup_spacing) * 1e-3 if stirrup_spacing > 0 else 0.0
    phi_v = 0.75
    phiVn_kN = phi_v * (Vc + Vs)
    dcr_shear = abs(Vu_kN) / phiVn_kN if phiVn_kN > 0 else 999.0
    
    governing_dcr = max(dcr_flex, dcr_shear)
    status = "OK" if governing_dcr <= 1.0 else "NG"
    
    return {
        "status": status,
        "governing_dcr": round(governing_dcr, 3),
        "flexure": {
            "dcr": round(dcr_flex, 3),
            "phiMn_kNm": round(phiMn_kNm, 1),
            "Mu_kNm": Mu_kNm,
            "c_mm": round(c_res, 1),
            "eps_t": round(eps_t, 5),
            "total_layers": len(layers)
        },
        "shear": {
            "dcr": round(dcr_shear, 3),
            "phiVn_kN": round(phiVn_kN, 1),
            "Vu_kN": Vu_kN,
            "Vc_kN": round(Vc, 1),
            "Vs_kN": round(Vs, 1)
        },
        "section": {
            "b": b, "h": h,
            "total_steel_area_mm2": round(sum(l["As"] for l in layers), 1)
        }
    }

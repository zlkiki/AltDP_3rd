"""
KDS 14 20 24 / KDS 14 20 26 스트럿-타이 모델(STM) 기반 RC 깊은 보(Deep Beam) 설계 및 검토 모듈
"""
import math
from pydantic import BaseModel, Field
from typing import Dict, Any, List

MODULE_INFO = {
    "id": "rc_beam_deep",
    "name": "깊은 보 (Deep Beam)",
    "category": "rc",
    "group": "beam",
    "submodule": "deep",
    "description": "KDS 14 20 24 스트럿-타이 모델(STM) 기반 콘크리트 깊은 보 노드 및 타이 검토",
    "geomType": "rc_rect",
    "template": "rc_rect"
}

class BeamDeepInput(BaseModel):
    b: float = Field(400.0, description="보 폭 b (mm)")
    h: float = Field(1200.0, description="보 전체 높이 h (mm)")
    ln: float = Field(2400.0, description="순경간 ln (mm)")
    fck: float = Field(27.0, description="콘크리트 압축강도 (MPa)")
    fy: float = Field(400.0, description="철근 항복강도 (MPa)")
    Vu: float = Field(650.0, description="계수 전단력/지점반력 Vu (kN)")
    Mu: float = Field(500.0, description="계수 휨모멘트 Mu (kN·m)")
    tie_rebar_dia: int = Field(25, description="하부 타이 인장철근 직경 (mm)")
    tie_rebar_num: int = Field(6, description="하부 타이 인장철근 개수 (EA)")
    web_h_dia: int = Field(13, description="수평 복부철근 직경 (mm)")
    web_h_spacing: float = Field(200.0, description="수평 복부철근 간격 (mm)")
    web_v_dia: int = Field(13, description="수직 복부철근 직경 (mm)")
    web_v_spacing: float = Field(200.0, description="수직 복부철근 간격 (mm)")

def calculate(data: Any) -> Dict[str, Any]:
    get_v = lambda k, default: data.get(k, default) if isinstance(data, dict) else getattr(data, k, default)
    b = float(get_v("b", 400.0))
    h = float(get_v("h", 1200.0))
    ln = float(get_v("ln", 2400.0))
    fck = float(get_v("fck", 27.0))
    fy = float(get_v("fy", 400.0))
    Vu = float(get_v("Vu", 650.0)) * 1000.0  # N
    Mu = float(get_v("Mu", 500.0))
    
    tie_rebar_dia = int(get_v("tie_rebar_dia", 25))
    tie_rebar_num = int(get_v("tie_rebar_num", 6))
    web_h_dia = int(get_v("web_h_dia", 13))
    web_h_spacing = float(get_v("web_h_spacing", 200.0))
    web_v_dia = int(get_v("web_v_dia", 13))
    web_v_spacing = float(get_v("web_v_spacing", 200.0))
    
    # 1. 기하 및 스트럿 각도 산정
    d = h - 100.0
    a = ln / 4.0
    theta_rad = math.atan(d / a) if a > 0 else math.atan(1.0)
    theta_deg = math.degrees(theta_rad)
    
    # 2. 스트럿 압축력 및 타이 인장력
    sin_th = math.sin(theta_rad)
    cos_th = math.cos(theta_rad)
    tan_th = math.tan(theta_rad)
    
    F_strut = Vu / sin_th if sin_th > 0 else 0.0
    F_tie = Vu / tan_th if tan_th > 0 else 0.0
    
    # 3. 타이 인장강도 검토
    num_bars = tie_rebar_num
    db = float(tie_rebar_dia)
    ab_map = {10: 71.3, 13: 126.7, 16: 198.6, 19: 286.5, 22: 387.1, 25: 506.7, 29: 642.4, 32: 794.2}
    ab = ab_map.get(int(db), math.pi * db * db / 4.0)
    As = num_bars * ab
    
    phi_t = 0.85
    Fnt = phi_t * As * fy  # N
    dcr_tie = F_tie / Fnt if Fnt > 0 else 999.0
    
    # 4. 스트럿 유효압축강도 검토 (KDS 14 20 24)
    beta_s = 0.75
    fce = 0.85 * beta_s * fck  # MPa
    ws = 200.0  # 지점판 폭 가용치 (mm)
    wt = 200.0  # 하부 타이 유효폭
    w_strut = ws * sin_th + wt * cos_th
    A_strut = b * w_strut  # mm2
    
    phi_c = 0.75
    Fns = phi_c * fce * A_strut  # N
    dcr_strut = F_strut / Fns if Fns > 0 else 999.0
    
    # 5. 최소 복부 보강철근비 검토 (수평 0.0025, 수직 0.0015)
    ab_h = ab_map.get(web_h_dia, 126.7)
    ab_v = ab_map.get(web_v_dia, 126.7)
    rho_h = (2.0 * ab_h) / (b * max(50.0, web_h_spacing))
    rho_v = (2.0 * ab_v) / (b * max(50.0, web_v_spacing))
    rho_req = 0.0025
    dcr_reinf = max(rho_req / (rho_h if rho_h > 0 else 1e-5), 0.0015 / (rho_v if rho_v > 0 else 1e-5))
    
    max_dcr = max(dcr_tie, dcr_strut, dcr_reinf)
    status = "OK" if max_dcr <= 1.0 else "NG"
    
    tie_str = f"{num_bars}-D{int(db)}"
    web_h_str = f"D{web_h_dia}@{int(web_h_spacing)}"
    web_v_str = f"D{web_v_dia}@{int(web_v_spacing)}"
    
    return {
        "status": status,
        "governing_dcr": round(max_dcr, 3),
        "max_dcr": round(max_dcr, 3),
        "strut": {
            "title": "콘크리트 압축 스트럿 검토 (Strut Capacity)",
            "F_strut_kN": round(F_strut / 1000.0, 1),
            "phi_Fns_kN": round(Fns / 1000.0, 1),
            "dcr": round(dcr_strut, 3),
            "phi": phi_c
        },
        "tie": {
            "title": "하부 인장 타이 검토 (Tie Capacity)",
            "F_tie_kN": round(F_tie / 1000.0, 1),
            "phi_Fnt_kN": round(Fnt / 1000.0, 1),
            "dcr": round(dcr_tie, 3),
            "phi": phi_t
        },
        "details": {
            "geometry": {
                "span_ln": round(ln, 0),
                "height_h": round(h, 0),
                "aspect_ratio_ln_h": round(ln / (h if h > 0 else 1), 2),
                "shear_span_a": round(a, 0),
                "strut_angle_deg": round(theta_deg, 1)
            },
            "reinforcement": {
                "tie_bars": tie_str,
                "tie_area_As": round(As, 1),
                "web_rebar_horiz": web_h_str,
                "web_rebar_vert": web_v_str,
                "rho_h": round(rho_h, 5),
                "rho_v": round(rho_v, 5),
                "rho_min": rho_req
            }
        },
        "summary": f"STM 검토: 스트럿 각도 {theta_deg:.1f}°, 타이 DCR={dcr_tie:.3f}, 스트럿 DCR={dcr_strut:.3f}",
        "visual_data": {
            "type": "rc_rect",
            "b": b,
            "h": h,
            "d": d,
            "tie_rebar": tie_str,
            "cover": 80.0,
            "top_rebar_count": 2,
            "bot_rebar_count": num_bars,
            "stirrup_space": 200.0
        }
    }

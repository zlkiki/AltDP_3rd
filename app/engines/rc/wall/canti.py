"""
역T형 / L형 RC 캔틸레버 옹벽(Cantilever Retaining Wall) 전도/활동/지지력 및 벽체 휨철근 설계 모듈
"""
import math
from pydantic import BaseModel, Field
from typing import Dict, Any

MODULE_INFO = {
    "id": "rc_wall_canti",
    "name": "캔틸레버 옹벽 (Cantilever Wall)",
    "category": "rc",
    "group": "wall",
    "submodule": "canti",
    "description": "토압 및 상재하중 재하 시 역T형 RC 캔틸레버 옹벽 전도/활동 안전율 및 저판/전면벽 배근 검토",
    "geomType": "rc_wall",
    "template": "rc_rect"
}

class WallCantiInput(BaseModel):
    H: float = Field(4500.0, description="옹벽 전체 높이 (mm)")
    B: float = Field(3000.0, description="저판 전체 폭 (mm)")
    t_stem_top: float = Field(300.0, description="전면벽 상단 두께 (mm)")
    t_stem_bot: float = Field(450.0, description="전면벽 하단 두께 (mm)")
    t_base: float = Field(500.0, description="저판 두께 (mm)")
    b_toe: float = Field(800.0, description="앞굽(Toe) 길이 (mm)")
    soil_gamma: float = Field(19.0, description="흙의 단위체적중량 (kN/m³)")
    soil_phi: float = Field(30.0, description="흙의 내부마찰각 (deg)")
    surcharge_q: float = Field(10.0, description="상재하중 (kN/m²)")
    qa: float = Field(200.0, description="허용 지내력 (kPa)")
    fck: float = Field(24.0, description="콘크리트 압축강도 (MPa)")
    fy: float = Field(400.0, description="철근 항복강도 (MPa)")
    stem_rebar_dia: int = Field(19, description="벽체 하단 주철근 직경 (mm)")
    stem_rebar_spacing: float = Field(150.0, description="벽체 하단 주철근 간격 (mm)")

def calculate(data: Any) -> Dict[str, Any]:
    get_v = lambda k, default: data.get(k, default) if isinstance(data, dict) else getattr(data, k, default)
    H = float(get_v("H", 4500.0)) / 1000.0  # m
    B = float(get_v("B", 3000.0)) / 1000.0  # m
    t_top = float(get_v("t_stem_top", 300.0)) / 1000.0  # m
    t_bot = float(get_v("t_stem_bot", 450.0)) / 1000.0  # m
    t_base = float(get_v("t_base", 500.0)) / 1000.0  # m
    b_toe = float(get_v("b_toe", 800.0)) / 1000.0  # m
    soil_gamma = float(get_v("soil_gamma", 19.0))
    soil_phi = float(get_v("soil_phi", 30.0))
    surcharge_q = float(get_v("surcharge_q", 10.0))
    qa = float(get_v("qa", 200.0))
    fck = float(get_v("fck", 24.0))
    fy = float(get_v("fy", 400.0))
    stem_rebar_dia = int(get_v("stem_rebar_dia", 19))
    stem_rebar_spacing = float(get_v("stem_rebar_spacing", 150.0))
    
    b_heel = B - b_toe - t_bot  # m
    h_stem = H - t_base  # m
    
    # 1. 랭킨 주동토압계수 Ka
    phi_rad = math.radians(soil_phi)
    Ka = (1.0 - math.sin(phi_rad)) / (1.0 + math.sin(phi_rad))
    
    # 2. 토압 및 상재하중 수평력
    # 토압 삼각형 P_ae = 0.5 * Ka * gamma * H^2
    Pa_soil = 0.5 * Ka * soil_gamma * (H**2)  # kN/m
    # 상재하중 사각형 P_aq = Ka * q * H
    Pa_q = Ka * surcharge_q * H  # kN/m
    P_total_h = Pa_soil + Pa_q  # kN/m
    
    # 전도 모멘트 Mo (저판 전면 Toe 끝단 기준)
    Mo = Pa_soil * (H / 3.0) + Pa_q * (H / 2.0)  # kN·m/m
    
    # 3. 연직하중 및 저항 모멘트 Mr
    # 콘크리트 중량 (24 kN/m3)
    W_base = B * t_base * 24.0
    W_stem = 0.5 * (t_top + t_bot) * h_stem * 24.0
    W_soil_heel = b_heel * h_stem * soil_gamma
    W_q_heel = b_heel * surcharge_q
    
    Rv = W_base + W_stem + W_soil_heel + W_q_heel  # kN/m
    
    # 저항 모멘트
    arm_base = B / 2.0
    arm_stem = b_toe + t_bot / 2.0
    arm_heel = B - b_heel / 2.0
    Mr = (W_base * arm_base + W_stem * arm_stem + 
          W_soil_heel * arm_heel + W_q_heel * arm_heel)  # kN·m/m
          
    # 4. 안정성 검토 (전도, 활동, 지내력)
    # 전도 안전율 (Fs_over >= 2.0)
    Fs_over = Mr / Mo if Mo > 0 else 99.0
    dcr_over = 2.0 / Fs_over
    
    # 활동 안전율 (Fs_slide >= 1.5, mu = tan(2/3 * phi))
    mu_fric = math.tan(2.0 / 3.0 * phi_rad)
    F_res = Rv * mu_fric
    Fs_slide = F_res / P_total_h if P_total_h > 0 else 99.0
    dcr_slide = 1.5 / Fs_slide
    
    # 지반 최대 지내력 qmax
    d_res = (Mr - Mo) / Rv if Rv > 0 else 0.0
    ecc = B / 2.0 - d_res
    if abs(ecc) <= B / 6.0:
        qmax = (Rv / B) * (1.0 + 6.0 * ecc / B)
    else:
        qmax = (2.0 * Rv) / (3.0 * d_res) if d_res > 0 else 999.0
    dcr_bearing = qmax / qa if qa > 0 else 999.0
    
    # 5. 벽체 기부(Stem Base) 휨모멘트 검토
    M_stem_u = 1.6 * (0.5 * Ka * soil_gamma * (h_stem**3) / 3.0 + Ka * surcharge_q * (h_stem**2) / 2.0)
    d_stem = (t_bot * 1000.0 - 60.0)  # mm
    db = float(stem_rebar_dia)
    spacing = max(50.0, float(stem_rebar_spacing))
    ab_map = {10: 71.3, 13: 126.7, 16: 198.6, 19: 286.5, 22: 387.1, 25: 506.7, 29: 642.4, 32: 794.2}
    ab = ab_map.get(int(db), math.pi * db * db / 4.0)
    As_stem = ab * (1000.0 / spacing)
    a = (As_stem * fy) / (0.85 * fck * 1000.0)
    phi_Mn_stem = 0.85 * As_stem * fy * (d_stem - a / 2.0) / 1e6  # kN·m/m
    dcr_stem_m = M_stem_u / phi_Mn_stem if phi_Mn_stem > 0 else 999.0
    
    max_dcr = max(dcr_over, dcr_slide, dcr_bearing, dcr_stem_m)
    status = "OK" if max_dcr <= 1.0 else "NG"
    
    return {
        "status": status,
        "governing_dcr": round(max_dcr, 3),
        "max_dcr": round(max_dcr, 3),
        "soil_bearing": {
            "title": "지반 접지압 및 전도/활동 안전성 검토 (Stability & Soil Bearing)",
            "q_max": round(qmax, 1),
            "qa": data.qa,
            "dcr": round(dcr_bearing, 3),
            "Fs_overturning": round(Fs_over, 2),
            "Fs_sliding": round(Fs_slide, 2)
        },
        "flexure": {
            "title": "전면벽 기부(Stem Base) 휨모멘트 검토 (Stem Flexural Capacity φMn)",
            "Mu": round(M_stem_u, 2),
            "phiMn": round(phi_Mn_stem, 2),
            "As": round(As_stem, 1),
            "dcr": round(dcr_stem_m, 3),
            "phi": 0.85
        },
        "details": {
            "lateral_earth_pressure": {
                "Ka": round(Ka, 3),
                "Pa_soil_kN_m": round(Pa_soil, 2),
                "Pa_surcharge_kN_m": round(Pa_q, 2),
                "P_total_horiz_kN_m": round(P_total_h, 2),
                "overturning_moment_Mo_kNm": round(Mo, 2),
                "resisting_moment_Mr_kNm": round(Mr, 2)
            },
            "stability_factors": {
                "Fs_overturning": round(Fs_over, 2),
                "allow_Fs_over": 2.0,
                "Fs_sliding": round(Fs_slide, 2),
                "allow_Fs_slide": 1.5,
                "eccentricity_m": round(ecc, 3)
            }
        },
        "summary": f"옹벽 안정성 검토: 전도FS={round(Fs_over,2)}(≥2.0), 활동FS={round(Fs_slide,2)}(≥1.5), 지내력 qmax={round(qmax,1)}kPa (DCR={round(max_dcr,2)})",
        "visual_data": {
            "type": "rc_footing",
            "B": B * 1000.0,
            "H": H * 1000.0,
            "t_base": t_base * 1000.0,
            "t_stem_bot": t_bot * 1000.0,
            "b_toe": b_toe * 1000.0,
            "rebar_x": f"D{stem_rebar_dia}@{int(stem_rebar_spacing)}",
            "rebar_y": "D13@250"
        }
    }

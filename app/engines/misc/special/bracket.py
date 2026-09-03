# app/engines/misc/special/bracket.py
"""RC Bracket & Corbel (기둥 코벨/브라켓 스트럿-타이 설계) Engine - KDS 14 20 24."""
import math
from typing import Dict, Any
from pydantic import BaseModel, Field

from app.engines.common.kds_concrete import REBAR_FY, REBAR_AREA

MODULE_INFO = {
    "id": "bracket",
    "name": "코벨 / 브라켓 (Corbel / Bracket)",
    "category": "misc",
    "group": "special",
    "geomType": "bracket",
    "description": "KDS 14 20에 따른 전단경간비(a/d <= 1.0) 기둥 브라켓/코벨 주인장철근(Asc), 전단마찰(Avf) 및 수평 폐쇄 스터럽(Ah) 검토"
}


class BracketInputSchema(BaseModel):
    b: float = Field(400.0, description="브라켓 폭 b (mm)")
    h: float = Field(600.0, description="기둥 접합부 전체 춤 h (mm)")
    h_out: float = Field(350.0, description="외단부 춤 h_out (mm)")
    a_dist: float = Field(250.0, description="전단경간 a (mm, 하중 작용점~기둥면)")
    
    fck: float = Field(27.0, description="콘크리트 압축강도 (MPa)")
    rebar_grade: str = Field("SD400", description="철근 강종")
    cover: float = Field(40.0, description="피복 두께 (mm)")
    
    Vu: float = Field(300.0, description="설계 연직하중 Vu (kN)")
    Nuc: float = Field(60.0, description="설계 수평 인장하중 Nuc (kN, >= 0.2*Vu)")
    
    main_dia: int = Field(22, description="주인장철근 직경 (mm)")
    main_num: int = Field(4, description="주인장철근 개수 (EA)")
    stir_dia: int = Field(10, description="수평 스터럽 직경 (mm)")
    stir_num_layers: int = Field(3, description="수평 스터럽 단 수 (2가닥 폐쇄형)")


def calculate(data: Any) -> Dict[str, Any]:
    get_v = lambda k, default: data.get(k, default) if isinstance(data, dict) else getattr(data, k, default)
    b = float(get_v("b", 400.0))
    h = float(get_v("h", 600.0))
    h_out = float(get_v("h_out", 350.0))
    a = float(get_v("a_dist", 250.0))
    fck = float(get_v("fck", 27.0))
    rebar_grade = str(get_v("rebar_grade", "SD400"))
    fy = REBAR_FY.get(rebar_grade, 400.0)
    cover = float(get_v("cover", 40.0))
    
    Vu_kN = float(get_v("Vu", 300.0))
    Nuc_kN = float(get_v("Nuc", 60.0))
    
    main_dia = int(get_v("main_dia", 22))
    main_num = int(get_v("main_num", 4))
    stir_dia = int(get_v("stir_dia", 10))
    stir_num_layers = int(get_v("stir_num_layers", 3))
    
    d = h - cover - main_dia / 2.0
    
    # 1. Geometry Limitations (KDS 14 20 §4.1.2)
    # a/d <= 1.0
    a_over_d = a / d if d > 0 else 999.0
    # Nuc >= 0.2 * Vu
    min_Nuc = 0.20 * Vu_kN
    Nuc_kN_eff = max(Nuc_kN, min_Nuc)
    
    # Outer depth >= 0.5 * d
    dcr_hout = (0.5 * d) / h_out if h_out > 0 else 999.0
    
    # 2. Maximum Shear Strength Vn_max (KDS 14 20)
    phi_v = 0.75
    # Vn_max = min(0.2 * fck * b * d, (3.3 + 0.08*fck)*b*d, 11*b*d)
    vn1 = 0.20 * fck * b * d * 1e-3
    vn2 = (3.3 + 0.08 * fck) * b * d * 1e-3
    vn3 = 11.0 * b * d * 1e-3
    phiVn_max = phi_v * min(vn1, vn2, vn3)  # kN
    dcr_vmax = Vu_kN / phiVn_max if phiVn_max > 0 else 999.0
    
    # 3. Shear-Friction Reinforcement Avf (mu = 1.4 for monolithic concrete)
    mu = 1.4
    Avf_req = (Vu_kN * 1e3) / (phi_v * fy * mu)  # mm²
    
    # 4. Direct Tension Reinforcement An
    An_req = (Nuc_kN_eff * 1e3) / (phi_v * fy)  # mm²
    
    # 5. Flexural Reinforcement Af
    Mu_corbel = Vu_kN * 1e3 * a + Nuc_kN_eff * 1e3 * (h - d)  # N*mm
    # Approximate flexural lever arm 0.9*d
    Af_req = Mu_corbel / (phi_v * fy * 0.90 * d)  # mm²
    
    # Primary Tension Reinforcement Asc requirement
    # Asc = max(Af + An, (2/3)*Avf + An, 0.04*(fck/fy)*b*d)
    asc1 = Af_req + An_req
    asc2 = (2.0 / 3.0) * Avf_req + An_req
    asc_min = 0.04 * (fck / fy) * b * d
    Asc_req = max(asc1, asc2, asc_min)
    
    # Provided Primary Rebar
    Asc_prov = main_num * REBAR_AREA.get(main_dia, 387.1)
    dcr_main = Asc_req / Asc_prov if Asc_prov > 0 else 999.0
    
    # 6. Horizontal Closed Stirrups Ah requirement (within upper 2/3 of d)
    # Ah >= 0.5 * (Asc - An)
    Ah_req = 0.5 * max(Asc_req - An_req, 0.0)
    Ah_prov = stir_num_layers * 2.0 * REBAR_AREA.get(stir_dia, 71.3)
    dcr_stir = Ah_req / Ah_prov if Ah_prov > 0 else 999.0
    
    governing_dcr = max(dcr_vmax, dcr_main, dcr_stir, dcr_hout)
    status = "OK" if governing_dcr <= 1.0 and a_over_d <= 1.0 else "NG"
    
    return {
        "status": status,
        "governing_dcr": round(governing_dcr, 3),
        "shear_capacity": {
            "dcr": round(dcr_vmax, 3),
            "Vu_kN": Vu_kN,
            "phiVn_max_kN": round(phiVn_max, 1),
            "a_over_d": round(a_over_d, 2),
            "a_over_d_status": "OK (<= 1.0)" if a_over_d <= 1.0 else "Exceeds 1.0 limit"
        },
        "primary_tension_rebar": {
            "dcr": round(dcr_main, 3),
            "Asc_required_mm2": round(Asc_req, 1),
            "Asc_provided_mm2": round(Asc_prov, 1),
            "main_rebar_spec": f"{main_num}-D{main_dia}"
        },
        "horizontal_stirrups": {
            "dcr": round(dcr_stir, 3),
            "Ah_required_mm2": round(Ah_req, 1),
            "Ah_provided_mm2": round(Ah_prov, 1),
            "stirrup_spec": f"{stir_num_layers} layers x 2-D{stir_dia}"
        },
        "section": {
            "b": b, "h": h, "h_out": h_out, "d": round(d, 1), "a": a
        }
    }

"""RC Beam Complete Design Engine (KDS 14 20 00 / 20 / 22 / 30).

Provides full flexural (singly/doubly reinforced, rectangular/T-beam), shear, torsion,
shear-torsion interaction verification, Branson deflection, crack width evaluation,
and DCR evaluation for reinforced concrete beams conforming to KDS 14 20.
"""

from dataclasses import dataclass, field
from enum import Enum
import math
from typing import Optional, List, Dict, Any, Tuple
from pydantic import BaseModel, Field, ConfigDict

from src.engine.db.materials import (
    ConcreteMaterial,
    RebarMaterial,
    get_phi_flexure,
    get_phi_shear
)
from src.engine.rc.rebar_layout import REBAR_DB


# ============================================================================
# 1. Pydantic v2 Enums and Input/Output Schemas (KDS 14 20 00 Standard)
# ============================================================================

class BeamShape(str, Enum):
    """Beam cross-section geometry shape."""
    RECTANGULAR = "RECTANGULAR"  # 직사각형 보
    TEE = "TEE"                  # T형 보


class SupportCondition(str, Enum):
    """Beam support boundary condition for deflection multiplier."""
    SIMPLE = "SIMPLE"            # 단순 지지 (alpha = 5/48, xi = 2.0)
    CONTINUOUS_ONE = "CONT_ONE"  # 일단 연속 (alpha = 0.08)
    CONTINUOUS_BOTH = "CONT_BOTH"# 양단 연속 (alpha = 0.05)
    CANTILEVER = "CANTILEVER"    # 캔틸레버 (alpha = 0.25)


class BeamArrangeType(str, Enum):
    """RC Beam Reinforcement Detailing Scope Option."""
    ONE_SECTION = "ONE_SECTION"          # 배근 유형-1: 전단면 (1개 단면)
    SYMMETRIC_ENDS = "SYMMETRIC_ENDS"    # 배근 유형-2: 양단부와 중앙부 (2개 단면 대칭)
    THREE_STATIONS = "THREE_STATIONS"    # 배근 유형-3: 각단부와 중앙부 (3개 단면 독립)


class RCBeamSection(BaseModel):
    """RC Beam Section Geometry and Material Specifications."""
    model_config = ConfigDict(extra="ignore")
    
    shape: BeamShape = BeamShape.RECTANGULAR
    b: float = Field(..., gt=0, description="보 복부 폭 bw (mm)")
    h: float = Field(..., gt=0, description="보 전체 높이 (mm)")
    length: float = Field(..., gt=0, description="보 유효 경간 L (mm)")
    cover: float = Field(40.0, gt=0, description="인장측 외곽 순피복 두께 (mm)")
    cover_top: float = Field(40.0, gt=0, description="압축측 외곽 순피복 두께 (mm)")
    
    # T형 보 전용 파라미터 (shape == TEE 일 때 유효)
    bf: Optional[float] = Field(None, gt=0, description="플랜지 유효폭 be (mm)")
    hf: Optional[float] = Field(None, gt=0, description="슬래브/플랜지 두께 (mm)")
    
    # 재료 물성치
    fck: float = Field(..., gt=0, description="콘크리트 설계기준압축강도 (MPa)")
    fy: float = Field(..., gt=0, description="주철근 설계기준항복강도 (MPa)")
    fyt: float = Field(..., gt=0, description="스터럽/비틀림철근 설계기준항복강도 (MPa)")
    support: SupportCondition = SupportCondition.SIMPLE


class RebarRow(BaseModel):
    """Individual horizontal row/layer of longitudinal bars."""
    model_config = ConfigDict(extra="ignore")
    
    bar_dia: str = Field(..., description="철근 호칭경 (예: 'D22', 'D25')")
    count: int = Field(..., gt=0, description="해당 단의 철근 개수")
    layer: int = Field(1, ge=1, le=3, description="배근 단수 (1단, 2단, 3단)")


class SectionRebarGroup(BaseModel):
    """Rebar arrangement for a specific beam cross-section (End-I, Center-M, End-J)."""
    model_config = ConfigDict(extra="ignore")
    
    top_bars: List[RebarRow] = Field(default_factory=list, description="상부 철근 목록")
    bot_bars: List[RebarRow] = Field(default_factory=list, description="하부 철근 목록")
    stirrup_bar: str = Field("D10", description="스터럽 철근 규격")
    stirrup_spacing: float = Field(200.0, gt=0, description="스터럽 배근 간격 s (mm)")
    stirrup_legs: int = Field(2, ge=2, description="스터럽 수직 다리수 (n legs)")


class RCBeamRebar(BaseModel):
    """Complete rebar detailing for all three critical beam stations."""
    model_config = ConfigDict(extra="ignore")
    
    arrange_type: BeamArrangeType = BeamArrangeType.SYMMETRIC_ENDS
    end_i: SectionRebarGroup = Field(..., description="End-I 단부 배근")
    center_m: SectionRebarGroup = Field(..., description="Center-M 중앙부 배근")
    end_j: SectionRebarGroup = Field(..., description="End-J 단부 배근")
    torsion_side_bar: Optional[str] = Field("D13", description="비틀림 종방향 측면 철근 규격")
    torsion_side_count: int = Field(0, ge=0, description="측면 비틀림 철근 단면당 총 개수")


class RCBeamPositionLoads(BaseModel):
    """Factored design forces and service load moments at a specific beam station."""
    model_config = ConfigDict(extra="ignore")
    
    Mu_pos: float = Field(0.0, description="정모멘트 설계계수하중 (kN·m)")
    Mu_neg: float = Field(0.0, description="부모멘트 설계계수하중 (kN·m)")
    Vu: float = Field(0.0, description="설계 계수전단력 (kN)")
    Tu: float = Field(0.0, description="설계 계수비틀림모멘트 (kN·m)")
    Ma_pos: float = Field(0.0, description="정모멘트 사용하중 모멘트 (kN·m, 처짐용)")
    Ma_neg: float = Field(0.0, description="부모멘트 사용하중 모멘트 (kN·m, 처짐용)")
    Msus: float = Field(0.0, description="지속하중에 의한 사용모멘트 (kN·m, 장기처짐용)")


class RCBeamLoads(BaseModel):
    """Design load sets across the three critical stations."""
    model_config = ConfigDict(extra="ignore")
    
    end_i: RCBeamPositionLoads
    center_m: RCBeamPositionLoads
    end_j: RCBeamPositionLoads
    deflection_limit_ratio: float = Field(240.0, gt=0, description="처짐 허용비 L / N (기본 240)")


class FlexureResult(BaseModel):
    """Flexural capacity and ductility evaluation results (KDS 14 20 20: 2022)."""
    model_config = ConfigDict(extra="ignore")
    
    Mu: float
    phi_Mn: float
    d: float
    dt: float
    c: float
    a: float
    epsilon_t: float
    epsilon_t_min: float         # 강도별 최소 허용 순인장변형률 (0.004 또는 2.0 ey)
    c_dt_ratio: float            # 중립축 깊이비 c / dt
    c_dt_limit: float            # 한계 중립축 깊이비 (c/dt)lim
    phi: float
    is_compression_yielding: bool
    As_req: float
    As_prov: float
    rho: float
    Mcr: float                   # 균열모멘트 Mcr (kN·m)
    phi_Mn_min: float            # 최소 휨강도 1.2 Mcr (kN·m)
    is_min_flexure_ok: bool      # phi_Mn >= 1.2 Mcr (또는 As >= 4/3 As_req) 만족 여부
    is_ductility_ok: bool        # epsilon_t >= epsilon_t_min 만족 여부
    dcr: float
    status: str                  # "OK" | "NG"
    is_zero_flexure: bool = False # 계수휨모멘트 0 이하 여부


class ShearResult(BaseModel):
    """Shear capacity and stirrup spacing evaluation results (KDS 14 20 22)."""
    model_config = ConfigDict(extra="ignore")
    
    Vu: float
    Vc: float
    Vs: float
    Vn: float
    phi_Vn: float
    phi: float = 0.75
    s_max: float
    Av_min: float
    Av_prov: float
    dcr: float
    status: str  # "OK" | "NG"
    is_zero_shear: bool = False   # 계수전단력 0 이하 여부


class TorsionResult(BaseModel):
    """Torsion capacity and interaction evaluation results (KDS 14 20 22)."""
    model_config = ConfigDict(extra="ignore")
    
    Tu: float
    Tth: float
    Tcr: float
    Tn: float
    phi_Tn: float
    phi: float = 0.75
    cross_section_check: str  # 콘크리트 압축파괴 방지 판정
    Al_req: float
    Al_prov: float
    dcr: float
    status: str  # "OK" | "NG"
    is_zero_torsion: bool = False # 계수비틀림 0 또는 문턱 비틀림 이하 여부


class StationCrackSpacingCheck(BaseModel):
    """KDS 14 20 30 제4.2.3절 균열방지 휨철근 간격 제한 (s <= s_max) 단면별 검토 결과."""
    model_config = ConfigDict(extra="ignore")
    
    station: str             # "end_i", "center_m", "end_j"
    rebar_pos: str           # "TOP" (단부 부모멘트) 또는 "BOTTOM" (중앙부 정모멘트)
    s_actual: float          # 실제 중심 간격 (mm)
    s_max: float             # 규준 최대 허용간격 (mm)
    cc: float                # 순피복두께 (mm)
    k_cr: float              # 환경계수 (280 또는 210)
    fs: float                # 직접 산출된 철근 사용응력 (MPa)
    dcr: float               # s_actual / s_max
    is_ok: bool              # 만족 여부


class ServiceabilityResult(BaseModel):
    """Serviceability deflection (Branson Ie) and direct crack width results (KDS 14 20 30)."""
    model_config = ConfigDict(extra="ignore")
    
    Mcr: float
    I_g: float
    I_cr: float
    I_e: float
    delta_immediate: float  # 즉시처짐 (mm)
    lambda_delta: float     # 장기처짐 계수
    delta_long_term: float  # 장기처짐 (mm)
    delta_total: float      # 총 처짐 (mm)
    delta_allow: float      # 허용 처짐 (mm)
    crack_width: float      # 직접 계산 균열폭 (mm)
    crack_allow: float      # 허용 균열폭 (mm)
    dcr_defl: float
    dcr_crack: float
    status: str  # "OK" | "NG"

    # KDS 14 20 30 제4.2.1절 지점조건 가중평균 Ie 및 단면별 Ie (cm4)
    Ie_avg: float = 0.0           # 가중평균 유효단면2차모멘트 (cm4)
    Ie_mid: float = 0.0           # 중앙부 Ie (cm4)
    Ie_end_i: float = 0.0         # End-I 단부 Ie (cm4)
    Ie_end_j: float = 0.0         # End-J 단부 Ie (cm4)
    support_condition: str = "SIMPLE" # 지점 조건
    
    # KDS 14 20 30 제4.2.3절 3-Station 각 단면별 인장철근 균열방지 간격 검토 결과
    crack_spacing_checks: Dict[str, StationCrackSpacingCheck] = Field(default_factory=dict)


# Backward-compatible / Spec alias for ServiceabilityResult
DeflectionResult = ServiceabilityResult


class RCBeamSectionResult(BaseModel):
    """Combined verification results at a single beam station."""
    model_config = ConfigDict(extra="ignore")
    
    pos_flexure: FlexureResult
    neg_flexure: FlexureResult
    shear: ShearResult
    torsion: TorsionResult
    is_zero_flexure: bool = False
    is_zero_shear: bool = False
    is_zero_torsion: bool = False


class RCBeamResult(BaseModel):
    """Comprehensive design and verification result across all 3 stations."""
    model_config = ConfigDict(extra="ignore")
    
    end_i: RCBeamSectionResult
    center_m: RCBeamSectionResult
    end_j: RCBeamSectionResult
    serviceability: ServiceabilityResult
    max_dcr: float
    governing_mode: str
    status: str  # "OK" | "NG"

    @property
    def is_safe(self) -> bool:
        return self.status == "OK"


# ============================================================================
# 2. Rebar Geometry and Database Helpers
# ============================================================================

# Extended KS Deformed Bar Properties (KS D 3504)
REBAR_EXTENDED_DB: Dict[str, Dict[str, float]] = {
    "D10": {"db": 9.53, "area": 71.33, "weight": 0.560},
    "D13": {"db": 12.7, "area": 126.7, "weight": 0.995},
    "D16": {"db": 15.9, "area": 198.6, "weight": 1.560},
    "D19": {"db": 19.1, "area": 286.5, "weight": 2.250},
    "D22": {"db": 22.2, "area": 387.1, "weight": 3.040},
    "D25": {"db": 25.4, "area": 506.7, "weight": 3.980},
    "D29": {"db": 28.6, "area": 642.4, "weight": 5.040},
    "D32": {"db": 31.8, "area": 794.2, "weight": 6.230},
    "D35": {"db": 35.8, "area": 956.6, "weight": 7.510},
}


def get_rebar_area(bar_dia: str) -> float:
    """Retrieve KS standard single bar cross-sectional area (mm2)."""
    dia_clean = bar_dia.upper().strip()
    if dia_clean in REBAR_EXTENDED_DB:
        return REBAR_EXTENDED_DB[dia_clean]["area"]
    if dia_clean in REBAR_DB:
        return REBAR_DB[dia_clean]["area"]
    # Fallback to nominal diameter calculation
    num_part = "".join(filter(str.isdigit, dia_clean))
    d_val = float(num_part) if num_part else 22.0
    return math.pi * (d_val ** 2) / 4.0


def get_rebar_db(bar_dia: str) -> float:
    """Retrieve KS standard nominal bar diameter db (mm)."""
    dia_clean = bar_dia.upper().strip()
    if dia_clean in REBAR_EXTENDED_DB:
        return REBAR_EXTENDED_DB[dia_clean]["db"]
    if dia_clean in REBAR_DB:
        return REBAR_DB[dia_clean]["db"]
    num_part = "".join(filter(str.isdigit, dia_clean))
    return float(num_part) if num_part else 22.0


def calculate_rebar_group_properties(
    bars: List[RebarRow],
    h: float,
    clear_cover: float,
    stirrup_db: float,
    is_top: bool = False
) -> Tuple[float, float, float, float]:
    """Calculate total steel area, effective depth d, dt (outermost layer), and centroid distance from surface.
    
    Returns:
        (total_area, effective_d, dt, centroid_from_surface)
    """
    if not bars:
        return (0.0, max(h - clear_cover, 1.0), max(h - clear_cover, 1.0), clear_cover)
    
    total_area = 0.0
    weighted_y = 0.0
    outermost_y = None
    
    # Layer spacing: clear vertical gap between layers = max(25mm, max bar diameter)
    max_db = max(get_rebar_db(row.bar_dia) for row in bars)
    layer_gap = max(25.0, max_db)
    
    for row in bars:
        area_single = get_rebar_area(row.bar_dia)
        row_area = area_single * row.count
        db = get_rebar_db(row.bar_dia)
        
        # Layer 1 centroid: clear_cover + stirrup_db + db / 2
        layer_idx = max(row.layer, 1)
        y_dist = clear_cover + stirrup_db + (db / 2.0) + (layer_idx - 1) * (db + layer_gap)
        
        if outermost_y is None or (layer_idx == 1 and y_dist < outermost_y):
            outermost_y = clear_cover + stirrup_db + (db / 2.0)
            
        total_area += row_area
        weighted_y += row_area * y_dist
        
    if outermost_y is None:
        outermost_y = clear_cover + stirrup_db + (max_db / 2.0)
        
    centroid_from_surface = weighted_y / total_area if total_area > 0 else clear_cover
    effective_d = max(h - centroid_from_surface, 1.0)
    dt = max(h - outermost_y, 1.0)
    
    return (total_area, effective_d, dt, centroid_from_surface)


# ============================================================================
# 3. KDS 14 20 Core Numerical Algorithms
# ============================================================================

def calculate_stress_block_factors(fck: float) -> Tuple[float, float, float]:
    """Calculate equivalent rectangular stress block factors (alpha1, beta1, ecu).
    
    Conforms to KDS 14 20 20:2022 Table 4.1-2:
    - alpha1 (eta * 0.85): 0.85 (fck <= 40 MPa), reduced for high-strength
    - beta1: 0.80 (fck <= 50 MPa), 0.76 (60 MPa), 0.74 (70 MPa), 0.72 (80 MPa), 0.70 (>=90 MPa)
    - ecu: 0.0033 (fck <= 40 MPa)
    """
    # Ultimate compressive strain ecu
    if fck <= 40.0:
        ecu = 0.0033
    else:
        ecu = max(0.0028, 0.0033 - 0.0001 * ((fck - 40.0) / 10.0))
        
    # Stress intensity factor alpha1 (eta * 0.85)
    if fck <= 40.0:
        alpha1 = 0.85
    else:
        eta = max(0.84, 1.00 - 0.003 * (fck - 40.0))
        alpha1 = eta * 0.85
        
    # Depth factor beta1 (standard KDS 14 20 20:2022 Table 4.1-2: beta1 = 0.80 for fck <= 50 MPa)
    if fck <= 50.0:
        beta1 = 0.80
    elif fck <= 60.0:
        beta1 = 0.80 - 0.004 * (fck - 50.0)
    elif fck <= 70.0:
        beta1 = 0.76 - 0.002 * (fck - 60.0)
    elif fck <= 80.0:
        beta1 = 0.74 - 0.002 * (fck - 70.0)
    elif fck <= 90.0:
        beta1 = 0.72 - 0.002 * (fck - 80.0)
    else:
        beta1 = 0.70
        
    return (alpha1, beta1, ecu)


def calculate_rc_beam_flexure(
    b: float,
    h: float,
    d: float,
    dt: Optional[float] = None,
    d_prime: float = 50.0,
    As: float = 0.0,
    As_prime: float = 0.0,
    fck: float = 24.0,
    fy: float = 400.0,
    Mu: float = 0.0,
    shape: BeamShape = BeamShape.RECTANGULAR,
    bf: Optional[float] = None,
    hf: Optional[float] = None,
    is_flange_in_compression: bool = False,
    Es: float = 200000.0,
    beta1_override: Optional[float] = None,
    alpha1_override: Optional[float] = None,
    lambda_factor: float = 1.0
) -> FlexureResult:
    """Rigorous non-linear equilibrium solver for singly/doubly/T-beam flexural capacity (KDS 14 20 20: 2022)."""
    alpha1_std, beta1_std, ecu = calculate_stress_block_factors(fck)
    alpha1 = alpha1_override if alpha1_override is not None else alpha1_std
    beta1 = beta1_override if beta1_override is not None else beta1_std
    ey = fy / Es
    dt_val = dt if (dt is not None and dt > 0) else d
    
    # ------------------------------------------------------------------------
    # KDS 14 20 20: 2022 Ductility Limit (4.1.2)
    # ------------------------------------------------------------------------
    if fy <= 400.0:
        epsilon_t_min = 0.0040
    else:
        epsilon_t_min = 2.0 * ey
        
    c_dt_limit = ecu / (ecu + epsilon_t_min)
    
    # ------------------------------------------------------------------------
    # KDS 14 20 20: 2022 Minimum Reinforcement & Cracking Moment (4.2.2)
    # ------------------------------------------------------------------------
    fr = 0.63 * lambda_factor * math.sqrt(fck)
    Ig_Nmm4 = (b * (h ** 3)) / 12.0
    yt = h / 2.0
    Mcr = (fr * Ig_Nmm4 / yt) / 1e6  # kN·m
    phi_Mn_min = 1.2 * Mcr           # kN·m
    
    # Effective compression width
    b_eff = bf if (shape == BeamShape.TEE and is_flange_in_compression and bf and bf > b) else b
    hf_val = hf if (shape == BeamShape.TEE and is_flange_in_compression and hf) else 0.0
    
    As = max(As, 0.0)
    As_prime = max(As_prime, 0.0)
    
    if As <= 0.0:
        return FlexureResult(
            Mu=round(Mu, 2),
            phi_Mn=0.0,
            d=round(d, 1),
            dt=round(dt_val, 1),
            c=0.0,
            a=0.0,
            epsilon_t=0.05,
            epsilon_t_min=round(epsilon_t_min, 5),
            c_dt_ratio=0.0,
            c_dt_limit=round(c_dt_limit, 4),
            phi=0.85,
            is_compression_yielding=False,
            As_req=0.0,
            As_prov=0.0,
            rho=0.0,
            Mcr=round(Mcr, 2),
            phi_Mn_min=round(phi_Mn_min, 2),
            is_min_flexure_ok=False,
            is_ductility_ok=True,
            dcr=999.0 if Mu > 0 else 0.0,
            status="NG"
        )
        
    T_tension = As * fy
    
    # ------------------------------------------------------------------------
    # T-Beam Flange Check (KDS 14 20 20 4.1.3)
    # ------------------------------------------------------------------------
    is_flange_overhang_active = False
    C_cf = 0.0
    
    if shape == BeamShape.TEE and is_flange_in_compression and bf and bf > b and hf_val > 0:
        # Check if depth of stress block exceeds flange thickness hf
        # Assume rectangular behavior with b_eff first
        a_rect = T_tension / (alpha1 * fck * b_eff) if (alpha1 * fck * b_eff) > 0 else 0.0
        if a_rect > hf_val:
            is_flange_overhang_active = True
            C_cf = alpha1 * fck * (bf - b) * hf_val
            
    # ------------------------------------------------------------------------
    # Neutral Axis Equilibrium: Cc(c) + Cs(c) = T
    # ------------------------------------------------------------------------
    if As_prime > 0.0:
        # Step 1: Assume compression steel yields (fs' = fy)
        Cs_yield = As_prime * (fy - alpha1 * fck)
        if is_flange_overhang_active:
            # Overhang takes C_cf, web takes C_cw = alpha1 * fck * b * a
            C_cw_yield = T_tension - Cs_yield - C_cf
            a_yield = C_cw_yield / (alpha1 * fck * b) if (alpha1 * fck * b) > 0 else 0.0
        else:
            C_c_yield = T_tension - Cs_yield
            a_yield = C_c_yield / (alpha1 * fck * b_eff) if (alpha1 * fck * b_eff) > 0 else 0.0
            
        c_yield = a_yield / beta1 if beta1 > 0 else 0.0
        eps_sp_yield = ecu * (c_yield - d_prime) / c_yield if c_yield > 0 else 0.0
        
        if eps_sp_yield >= ey and a_yield > 0:
            a = a_yield
            c = c_yield
            fs_prime = fy
            is_compression_yielding = True
        else:
            # Step 2: Compression steel does not yield, solve quadratic equilibrium for c
            # C_c = alpha1 * fck * beta1 * b_calc * c
            # C_s = As_prime * [Es * ecu * (c - d') / c - alpha1 * fck]
            b_calc = b if is_flange_overhang_active else b_eff
            extra_C = C_cf if is_flange_overhang_active else 0.0
            
            # alpha1 * fck * beta1 * b_calc * c^2 + (As_prime * Es * ecu - alpha1 * fck * As_prime + extra_C - T_tension) * c - As_prime * Es * ecu * d_prime = 0
            A_q = alpha1 * fck * beta1 * b_calc
            B_q = As_prime * Es * ecu - alpha1 * fck * As_prime + extra_C - T_tension
            C_q = - As_prime * Es * ecu * d_prime
            
            disc = max(B_q ** 2 - 4.0 * A_q * C_q, 0.0)
            c = (-B_q + math.sqrt(disc)) / (2.0 * A_q) if A_q > 0 else 1.0
            a = beta1 * c
            eps_sp = ecu * (c - d_prime) / c if c > 0 else 0.0
            fs_prime = min(max(Es * eps_sp, -fy), fy)
            is_compression_yielding = (abs(fs_prime) >= fy * 0.999)
    else:
        if is_flange_overhang_active:
            a = (T_tension - C_cf) / (alpha1 * fck * b) if (alpha1 * fck * b) > 0 else 0.0
        else:
            a = T_tension / (alpha1 * fck * b_eff) if (alpha1 * fck * b_eff) > 0 else 0.0
        c = a / beta1 if beta1 > 0 else 0.0
        fs_prime = 0.0
        is_compression_yielding = False
        
    # ------------------------------------------------------------------------
    # Net Tensile Strain epsilon_t and Strength Reduction Factor phi
    # ------------------------------------------------------------------------
    epsilon_t = ecu * (dt_val - c) / c if c > 0 else 0.05
    phi = get_phi_flexure(epsilon_t, ey)
    
    # ------------------------------------------------------------------------
    # Nominal and Design Flexural Capacity Mn, phi_Mn
    # ------------------------------------------------------------------------
    if is_flange_overhang_active:
        C_cw = alpha1 * fck * b * a
        Cs_val = As_prime * (fs_prime - alpha1 * fck) if As_prime > 0 else 0.0
        Mn_Nmm = (
            C_cf * (d - hf_val / 2.0) +
            C_cw * (d - a / 2.0) +
            Cs_val * (d - d_prime)
        )
    elif As_prime > 0.0:
        Cc_val = alpha1 * fck * b_eff * a
        Cs_val = As_prime * (fs_prime - alpha1 * fck)
        Mn_Nmm = Cc_val * (d - a / 2.0) + Cs_val * (d - d_prime)
    else:
        Mn_Nmm = T_tension * (d - a / 2.0)
        
    Mn = max(Mn_Nmm / 1e6, 0.0)  # kN·m
    phi_Mn = phi * Mn            # kN·m
    dcr = Mu / phi_Mn if phi_Mn > 0 else (0.0 if Mu == 0.0 else 999.0)
    
    # ------------------------------------------------------------------------
    # Ductility & Minimum Reinforcement Checks (KDS 14 20 20: 2022)
    # ------------------------------------------------------------------------
    rho = As / (b * d) if (b * d) > 0 else 0.0
    c_dt_ratio = (c / dt_val) if dt_val > 0 else 0.0
    is_ductility_ok = (epsilon_t >= epsilon_t_min - 1e-6)
    
    # Required steel area approximation
    jd = max(d - a / 2.0, 0.7 * d)
    As_req = (Mu * 1e6) / (phi * fy * jd) if (phi * fy * jd > 0 and Mu > 0) else 0.0
    
    # KDS 14 20 20: 2022 4.2.2 Minimum Reinforcement Check:
    # phi_Mn >= 1.2 Mcr OR Exception (4.2.2(3)): As >= 4/3 As_req
    is_min_flexure_ok = (
        (phi_Mn >= phi_Mn_min - 1e-4) or
        (As_req > 0 and As >= (4.0 / 3.0) * As_req - 1e-4) or
        (Mu <= 0.0 and As > 0)
    )
    
    status = "OK" if (dcr <= 1.001 and is_ductility_ok and is_min_flexure_ok) else "NG"
    
    return FlexureResult(
        Mu=round(Mu, 2),
        phi_Mn=round(phi_Mn, 2),
        d=round(d, 1),
        dt=round(dt_val, 1),
        c=round(c, 1),
        a=round(a, 1),
        epsilon_t=round(epsilon_t, 5),
        epsilon_t_min=round(epsilon_t_min, 5),
        c_dt_ratio=round(c_dt_ratio, 4),
        c_dt_limit=round(c_dt_limit, 4),
        phi=round(phi, 3),
        is_compression_yielding=is_compression_yielding,
        As_req=round(As_req, 1),
        As_prov=round(As, 1),
        rho=round(rho, 4),
        Mcr=round(Mcr, 2),
        phi_Mn_min=round(phi_Mn_min, 2),
        is_min_flexure_ok=is_min_flexure_ok,
        is_ductility_ok=is_ductility_ok,
        dcr=round(dcr, 3),
        status=status,
        is_zero_flexure=(Mu <= 0.0)
    )


def calculate_rc_beam_shear(
    b: float,
    d: float,
    fck: float,
    fyt: float,
    Av: float,
    s: float,
    Vu: float,
    lambda_factor: float = 1.0
) -> ShearResult:
    """Rigorous shear capacity and stirrup spacing check (KDS 14 20 22)."""
    phi_v = 0.75
    
    # Concrete shear strength Vc
    Vc_N = (1.0 / 6.0) * lambda_factor * math.sqrt(fck) * b * d
    Vc = Vc_N / 1e3  # kN
    
    # Stirrup shear strength Vs
    Vs_N = (Av * fyt * d) / s if s > 0 else 0.0
    Vs_max_N = (2.0 / 3.0) * math.sqrt(fck) * b * d
    Vs_N = min(Vs_N, Vs_max_N)
    Vs = Vs_N / 1e3
    
    Vn = Vc + Vs
    phi_Vn = phi_v * Vn
    dcr = Vu / phi_Vn if phi_Vn > 0 else (0.0 if Vu == 0.0 else 999.0)
    
    # Maximum stirrup spacing s_max (KDS 14 20 22 4.4.3: based on required Vs)
    Vs_req = max((Vu - phi_v * Vc) / phi_v, 0.0) if phi_v > 0 else 0.0
    Vs_spacing_basis = Vs_req if Vs_req > 0 else Vs
    if Vs_spacing_basis > (1.0 / 3.0) * math.sqrt(fck) * b * d / 1e3:
        s_max = min(d / 4.0, 300.0)
    else:
        s_max = min(d / 2.0, 600.0)
        
    # Minimum shear reinforcement Av_min
    Av_min = max(0.0625 * math.sqrt(fck) * (b * s) / fyt, 0.35 * (b * s) / fyt) if s > 0 else 0.0
    
    is_spacing_ok = (s <= s_max * 1.001)
    status = "OK" if (dcr <= 1.0 and is_spacing_ok) else "NG"
    
    return ShearResult(
        Vu=round(Vu, 2),
        Vc=round(Vc, 2),
        Vs=round(Vs, 2),
        Vn=round(Vn, 2),
        phi_Vn=round(phi_Vn, 2),
        phi=phi_v,
        s_max=round(s_max, 1),
        Av_min=round(Av_min, 1),
        Av_prov=round(Av, 1),
        dcr=round(dcr, 3),
        status=status,
        is_zero_shear=(Vu <= 0.0)
    )


def calculate_rc_beam_torsion(
    b: float,
    h: float,
    d: float,
    fck: float,
    fy: float,
    fyt: float,
    Av: float,
    s: float,
    side_bar_area: float,
    side_cover: float,
    Tu: float,
    Vu: float,
    Vc_kN: float,
    lambda_factor: float = 1.0
) -> TorsionResult:
    """Rigorous torsion capacity, threshold check, and combined stress verification (KDS 14 20 22)."""
    phi_t = 0.75
    Acp = b * h
    pcp = 2.0 * (b + h)
    
    # Threshold torsion Tth and cracking torsion Tcr
    Tth_Nmm = 0.0625 * lambda_factor * math.sqrt(fck) * (Acp ** 2) / pcp
    Tcr_Nmm = 0.25 * lambda_factor * math.sqrt(fck) * (Acp ** 2) / pcp
    Tth = Tth_Nmm / 1e6  # kN·m
    Tcr = Tcr_Nmm / 1e6  # kN·m
    
    Tu_abs = abs(Tu)
    is_torsion_ignored = (Tu_abs <= phi_t * Tth)
    
    # Closed stirrup dimensions Aoh, ph, Ao
    boh = max(b - 2.0 * side_cover, 10.0)
    hoh = max(h - 2.0 * side_cover, 10.0)
    Aoh = boh * hoh
    ph = 2.0 * (boh + hoh)
    Ao = 0.85 * Aoh
    
    if not is_torsion_ignored and Tu_abs > 0:
        Tn_req_Nmm = (Tu_abs / phi_t) * 1e6
        # At/s for single leg: Tn = (2 * Ao * At * fyt / s) * cot(45)
        At_over_s_req = Tn_req_Nmm / (2.0 * Ao * fyt * 1.0)
        Al_req = At_over_s_req * ph * (fyt / fy) * 1.0
        Al_min = max((0.42 * math.sqrt(fck) * Acp / fy) - (At_over_s_req * ph * (fyt / fy)), 0.0)
        
        # Provided torsion stirrup capacity
        At_prov = Av / 2.0
        Tn_Nmm = (2.0 * Ao * At_prov * fyt * 1.0) / s if s > 0 else 0.0
        Tn = Tn_Nmm / 1e6
        phi_Tn = phi_t * Tn
        torsion_dcr = Tu_abs / phi_Tn if phi_Tn > 0 else 999.0
        
        # Combined shear-torsion cross section dimension check
        vu = (Vu * 1e3) / (b * d)
        tu = (Tu_abs * 1e6 * ph) / (1.7 * (Aoh ** 2))
        combined_stress = math.sqrt(vu ** 2 + tu ** 2)
        combined_limit = phi_t * ((Vc_kN * 1e3 / (b * d)) + (2.0 / 3.0) * math.sqrt(fck))
        combined_dcr = combined_stress / combined_limit if combined_limit > 0 else 999.0
        cross_section_check = "OK (Cross section adequate)" if combined_dcr <= 1.0 else "NG (Section enlargement required)"
        
        total_dcr = max(torsion_dcr, combined_dcr)
        status = "OK" if total_dcr <= 1.0 else "NG"
    else:
        Tn = 0.0
        phi_Tn = 0.0
        Al_req = 0.0
        total_dcr = 0.0
        cross_section_check = "OK (Torsion negligible)"
        status = "OK"
        
    return TorsionResult(
        Tu=round(Tu, 2),
        Tth=round(Tth, 2),
        Tcr=round(Tcr, 2),
        Tn=round(Tn, 2),
        phi_Tn=round(phi_Tn, 2),
        phi=phi_t,
        cross_section_check=cross_section_check,
        Al_req=round(Al_req, 1),
        Al_prov=round(side_bar_area, 1),
        dcr=round(total_dcr, 3),
        status=status,
        is_zero_torsion=(Tu_abs <= 0.0 or is_torsion_ignored)
    )


def calculate_cracked_section_properties(
    b: float,
    h: float,
    d: float,
    d_prime: float,
    As: float,
    As_prime: float,
    fck: float,
    Es: float = 200000.0
) -> Tuple[float, float, float, float, float]:
    """Calculate gross and cracked section transformed properties (Ig, Icr, Mcr, kd, n).
    
    Returns:
        (Ig_mm4, Icr_mm4, Mcr_kNm, kd, n_ratio)
    """
    fcu = fck + 4.0 if fck <= 40.0 else fck + 6.0
    Ec = 8500.0 * (fcu ** (1.0 / 3.0))
    n_ratio = Es / Ec
    
    Ig_mm4 = (b * (h ** 3)) / 12.0
    yt = h / 2.0
    fr = 0.63 * 1.0 * math.sqrt(fck)
    Mcr_Nmm = (fr * Ig_mm4) / yt
    Mcr_kNm = Mcr_Nmm / 1e6
    
    # Cracked transformed section: neutral axis kd
    A_kd = 0.5 * b
    B_kd = n_ratio * As + max((n_ratio - 1.0) * As_prime, 0.0)
    C_kd = - (n_ratio * As * d + max((n_ratio - 1.0) * As_prime * d_prime, 0.0))
    disc_kd = max(B_kd ** 2 - 4.0 * A_kd * C_kd, 0.0)
    kd = (-B_kd + math.sqrt(disc_kd)) / (2.0 * A_kd) if A_kd > 0 else 0.3 * d
    
    Icr_mm4 = (b * (kd ** 3)) / 3.0 + n_ratio * As * ((d - kd) ** 2)
    if As_prime > 0 and kd > d_prime:
        Icr_mm4 += (n_ratio - 1.0) * As_prime * ((kd - d_prime) ** 2)
        
    return (Ig_mm4, Icr_mm4, Mcr_kNm, kd, n_ratio)


def calculate_effective_moment_of_inertia(
    Ig_mm4: float,
    Icr_mm4: float,
    Mcr_kNm: float,
    Ma_kNm: float
) -> float:
    """Calculate Branson effective moment of inertia Ie (mm4) for a cross-section."""
    Ma_abs = abs(Ma_kNm)
    if Ma_abs <= Mcr_kNm or Mcr_kNm <= 0.0:
        return Ig_mm4
    m_ratio = (Mcr_kNm / Ma_abs) ** 3
    Ie = m_ratio * Ig_mm4 + (1.0 - m_ratio) * Icr_mm4
    return min(Ie, Ig_mm4)


def check_crack_bar_spacing(
    station_name: str,
    rebar_pos: str,
    b: float,
    d: float,
    kd: float,
    As: float,
    fy: float,
    Ma_kNm: float,
    clear_cover: float,
    stirrup_db: float,
    bars: List[RebarRow],
    k_cr: float = 280.0,
    is_zero_load: bool = False
) -> StationCrackSpacingCheck:
    """Check maximum flexural rebar spacing for crack control (KDS 14 20 30 4.2.3).
    
    s <= s_max = 375 * (k_cr / f_s) - 2.5 * c_c <= 300 * (k_cr / f_s)
    """
    # 1. Shortest distance from concrete surface to nearest tension bar surface (cc)
    cc = clear_cover + stirrup_db
    
    # 2. Service stress in steel fs (elastic cracked section)
    jd = max(d - (kd / 3.0), 0.5 * d)
    Ma_abs = abs(Ma_kNm)
    
    if is_zero_load:
        # Zero load applied: no flexural tension stress, nominal spacing check with dcr=0
        fs_clamped = (2.0 / 3.0) * fy
        s_max_1 = 375.0 * (k_cr / fs_clamped) - 2.5 * cc
        s_max_2 = 300.0 * (k_cr / fs_clamped)
        s_max = max(min(s_max_1, s_max_2), 50.0)
        
        layer1_bars = [r for r in bars if r.layer == 1]
        if not layer1_bars and bars:
            layer1_bars = [bars[0]]
        n_layer1 = sum(r.count for r in layer1_bars)
        first_bar_dia = layer1_bars[0].bar_dia if layer1_bars else "D22"
        main_db = get_rebar_db(first_bar_dia)
        if n_layer1 >= 2:
            centerline_width = max(b - 2.0 * (cc + main_db / 2.0), 0.0)
            s_actual = centerline_width / (n_layer1 - 1)
        else:
            s_actual = max(b - 2.0 * cc, 0.0)
            
        return StationCrackSpacingCheck(
            station=station_name,
            rebar_pos=rebar_pos,
            s_actual=round(s_actual, 1),
            s_max=round(s_max, 1),
            cc=round(cc, 1),
            k_cr=round(k_cr, 1),
            fs=0.0,
            dcr=0.0,
            is_ok=True
        )
        
    if Ma_abs > 0 and As > 0 and jd > 0:
        fs = (Ma_abs * 1e6) / (As * jd)
        if fs <= 0.0:
            fs = (2.0 / 3.0) * fy
    else:
        # Fallback to (2/3) * fy when service moment is not provided
        fs = (2.0 / 3.0) * fy
        
    fs_clamped = max(min(fs, fy), 10.0)
    
    # 3. Maximum allowable spacing s_max
    s_max_1 = 375.0 * (k_cr / fs_clamped) - 2.5 * cc
    s_max_2 = 300.0 * (k_cr / fs_clamped)
    s_max = min(s_max_1, s_max_2)
    s_max = max(s_max, 50.0)  # Physical lower bound
    
    # 4. Actual spacing s_actual
    layer1_bars = [r for r in bars if r.layer == 1]
    if not layer1_bars and bars:
        layer1_bars = [bars[0]]
        
    n_layer1 = sum(r.count for r in layer1_bars)
    first_bar_dia = layer1_bars[0].bar_dia if layer1_bars else "D22"
    main_db = get_rebar_db(first_bar_dia)
    
    if n_layer1 >= 2:
        centerline_width = max(b - 2.0 * (cc + main_db / 2.0), 0.0)
        s_actual = centerline_width / (n_layer1 - 1)
    else:
        s_actual = max(b - 2.0 * cc, 0.0)
        
    dcr = s_actual / s_max if s_max > 0 else 999.0
    is_ok = (dcr <= 1.0)
    
    return StationCrackSpacingCheck(
        station=station_name,
        rebar_pos=rebar_pos,
        s_actual=round(s_actual, 1),
        s_max=round(s_max, 1),
        cc=round(cc, 1),
        k_cr=round(k_cr, 1),
        fs=round(fs_clamped, 1),
        dcr=round(dcr, 3),
        is_ok=is_ok
    )


def calculate_rc_beam_serviceability(
    b: float,
    h: float,
    d: float,
    d_prime: float,
    As: float,
    As_prime: float,
    fck: float,
    fy: float,
    Ma: float,
    Msus: float,
    length: float,
    support: SupportCondition,
    clear_cover: float,
    stirrup_db: float,
    num_tension_bars: int,
    defl_ratio: float = 240.0,
    time_duration_months: int = 60,
    w_lim: float = 0.30,
    Ie_override: Optional[float] = None,
    Ie_mid: Optional[float] = None,
    Ie_end_i: Optional[float] = None,
    Ie_end_j: Optional[float] = None,
    crack_spacing_checks: Optional[Dict[str, StationCrackSpacingCheck]] = None
) -> ServiceabilityResult:
    """Rigorous Branson Ie deflection and direct crack width evaluation (KDS 14 20 30)."""
    # Concrete Elastic Modulus Ec = 8500 * (fcu)^(1/3)
    fcu = fck + 4.0 if fck <= 40.0 else fck + 6.0
    Ec = 8500.0 * (fcu ** (1.0 / 3.0))
    Es = 200000.0
    n_ratio = Es / Ec
    
    # Gross section properties
    Ig_mm4 = (b * (h ** 3)) / 12.0
    yt = h / 2.0
    fr = 0.63 * 1.0 * math.sqrt(fck)
    Mcr_Nmm = (fr * Ig_mm4) / yt
    Mcr = Mcr_Nmm / 1e6  # kN·m
    
    # Cracked transformed section: solve for neutral axis kd
    A_kd = 0.5 * b
    B_kd = n_ratio * As + max((n_ratio - 1.0) * As_prime, 0.0)
    C_kd = - (n_ratio * As * d + max((n_ratio - 1.0) * As_prime * d_prime, 0.0))
    disc_kd = max(B_kd ** 2 - 4.0 * A_kd * C_kd, 0.0)
    kd = (-B_kd + math.sqrt(disc_kd)) / (2.0 * A_kd) if A_kd > 0 else 0.3 * d
    
    # Cracked moment of inertia Icr
    Icr_mm4 = (b * (kd ** 3)) / 3.0 + n_ratio * As * ((d - kd) ** 2)
    if As_prime > 0 and kd > d_prime:
        Icr_mm4 += (n_ratio - 1.0) * As_prime * ((kd - d_prime) ** 2)
        
    Ma_abs = abs(Ma)
    if Ma_abs <= Mcr or Mcr == 0.0:
        Ie_mm4 = Ig_mm4
    else:
        m_ratio = (Mcr / Ma_abs) ** 3
        Ie_mm4 = m_ratio * Ig_mm4 + (1.0 - m_ratio) * Icr_mm4
        Ie_mm4 = min(Ie_mm4, Ig_mm4)
        
    # Determine which Ie to use for deflection (Ie_override if provided from weighted average)
    Ie_calc = Ie_override if (Ie_override is not None and Ie_override > 0) else Ie_mm4
    
    # Support deflection coefficient alpha
    if support == SupportCondition.SIMPLE:
        alpha_defl = 5.0 / 48.0
    elif support == SupportCondition.CONTINUOUS_ONE:
        alpha_defl = 0.08
    elif support == SupportCondition.CONTINUOUS_BOTH:
        alpha_defl = 0.05
    elif support == SupportCondition.CANTILEVER:
        alpha_defl = 0.25
    else:
        alpha_defl = 5.0 / 48.0
        
    # Immediate elastic deflection delta_i
    delta_immediate = (alpha_defl * (Ma_abs * 1e6) * (length ** 2)) / (Ec * Ie_calc) if (Ec * Ie_calc) > 0 else 0.0
    
    # Long-term multiplier lambda_delta (xi = 2.0 for 5+ years)
    xi_factor = 2.0 if time_duration_months >= 60 else (1.4 if time_duration_months >= 12 else (1.2 if time_duration_months >= 6 else 1.0))
    rho_prime = As_prime / (b * d) if (b * d) > 0 else 0.0
    lambda_delta = xi_factor / (1.0 + 50.0 * rho_prime)
    
    # Sustained deflection
    sustained_ratio = (abs(Msus) / Ma_abs) if (Ma_abs > 0 and abs(Msus) > 0) else 0.70
    delta_sustained = delta_immediate * sustained_ratio
    delta_long_term = lambda_delta * delta_sustained
    delta_total = delta_immediate + delta_long_term
    
    delta_allow = length / defl_ratio if defl_ratio > 0 else 25.0
    dcr_defl = delta_total / delta_allow if delta_allow > 0 else 0.0
    
    # Direct crack width check (KDS 14 20 30 4.2)
    jd = d - kd / 3.0
    fs_service = (Ma_abs * 1e6) / (As * jd) if (As * jd) > 0 else 0.0
    fs_service = min(fs_service, 0.6 * fy)
    
    # Outermost bar centroid distance to bottom face dc
    main_db = 22.0
    dc = clear_cover + stirrup_db + (main_db / 2.0)
    n_bars = max(num_tension_bars, 2)
    A_eff = (2.0 * dc * b) / n_bars
    beta_crack = (h - kd) / (d - kd) if (d - kd) > 0 else 1.2
    
    eps_s_service = fs_service / Es
    crack_width = 1.08 * beta_crack * eps_s_service * ((dc * A_eff) ** (1.0 / 3.0)) if (dc * A_eff) > 0 else 0.0
    dcr_crack = crack_width / w_lim if w_lim > 0 else 0.0
    
    # Overall serviceability status check
    is_spacing_ok = True
    if crack_spacing_checks:
        is_spacing_ok = all(chk.is_ok for chk in crack_spacing_checks.values())
        
    status = "OK" if (dcr_defl <= 1.0 and dcr_crack <= 1.0 and is_spacing_ok) else "NG"
    
    return ServiceabilityResult(
        Mcr=round(Mcr, 2),
        I_g=round(Ig_mm4 / 1e4, 1),    # cm4
        I_cr=round(Icr_mm4 / 1e4, 1),  # cm4
        I_e=round(Ie_calc / 1e4, 1),   # cm4
        delta_immediate=round(delta_immediate, 2),
        lambda_delta=round(lambda_delta, 3),
        delta_long_term=round(delta_long_term, 2),
        delta_total=round(delta_total, 2),
        delta_allow=round(delta_allow, 2),
        crack_width=round(crack_width, 3),
        crack_allow=round(w_lim, 2),
        dcr_defl=round(dcr_defl, 3),
        dcr_crack=round(dcr_crack, 3),
        status=status,
        Ie_avg=round(Ie_calc / 1e4, 1),
        Ie_mid=round((Ie_mid if Ie_mid is not None else Ie_mm4) / 1e4, 1),
        Ie_end_i=round((Ie_end_i if Ie_end_i is not None else Ie_mm4) / 1e4, 1),
        Ie_end_j=round((Ie_end_j if Ie_end_j is not None else Ie_mm4) / 1e4, 1),
        support_condition=support.value if hasattr(support, "value") else str(support),
        crack_spacing_checks=crack_spacing_checks or {}
    )


# ============================================================================
# 4. Master Design Orchestration Function (calculate_rc_beam_design)
# ============================================================================

def calculate_rc_beam_design(
    section: RCBeamSection,
    rebar: RCBeamRebar,
    loads: RCBeamLoads
) -> RCBeamResult:
    """Master high-level verification orchestrator across 3 stations (End-I, Center-M, End-J)."""
    b = section.b
    h = section.h
    fck = section.fck
    fy = section.fy
    fyt = section.fyt
    
    # Station rebar groups and loads
    stations = [
        ("end_i", rebar.end_i, loads.end_i),
        ("center_m", rebar.center_m, loads.center_m),
        ("end_j", rebar.end_j, loads.end_j),
    ]
    
    station_results = {}
    max_dcr = 0.0
    governing_mode = "Flexure"
    
    # Torsion side bar area
    side_bar_area = 0.0
    if rebar.torsion_side_count > 0 and rebar.torsion_side_bar:
        side_bar_area = rebar.torsion_side_count * get_rebar_area(rebar.torsion_side_bar)
        
    for name, rgroup, ploads in stations:
        stirrup_db = get_rebar_db(rgroup.stirrup_bar)
        stirrup_area = rgroup.stirrup_legs * get_rebar_area(rgroup.stirrup_bar)
        
        # 1. Positive Moment Flexure (Bottom steel in tension, top in compression)
        As_bot, d_bot, dt_bot, dp_bot = calculate_rebar_group_properties(
            rgroup.bot_bars, h, section.cover, stirrup_db, is_top=False
        )
        As_top, d_top, dt_top, dp_top = calculate_rebar_group_properties(
            rgroup.top_bars, h, section.cover_top, stirrup_db, is_top=True
        )
        
        pos_flex = calculate_rc_beam_flexure(
            b=b, h=h, d=d_bot, dt=dt_bot, d_prime=dp_top,
            As=As_bot, As_prime=As_top, fck=fck, fy=fy,
            Mu=ploads.Mu_pos, shape=section.shape, bf=section.bf, hf=section.hf,
            is_flange_in_compression=True
        )
        
        # 2. Negative Moment Flexure (Top steel in tension, bottom in compression)
        # Note: In negative bending, flange of T-beam is in tension, so compression width is bw = b
        neg_flex = calculate_rc_beam_flexure(
            b=b, h=h, d=d_top, dt=dt_top, d_prime=dp_bot,
            As=As_top, As_prime=As_bot, fck=fck, fy=fy,
            Mu=ploads.Mu_neg, shape=BeamShape.RECTANGULAR, bf=None, hf=None,
            is_flange_in_compression=False
        )
        
        # 3. Shear
        d_shear = min(d_bot, h - dp_top)
        shear_res = calculate_rc_beam_shear(
            b=b, d=d_shear, fck=fck, fyt=fyt,
            Av=stirrup_area, s=rgroup.stirrup_spacing, Vu=ploads.Vu
        )
        
        # 4. Torsion
        torsion_res = calculate_rc_beam_torsion(
            b=b, h=h, d=d_shear, fck=fck, fy=fy, fyt=fyt,
            Av=stirrup_area, s=rgroup.stirrup_spacing,
            side_bar_area=side_bar_area, side_cover=section.cover,
            Tu=ploads.Tu, Vu=ploads.Vu, Vc_kN=shear_res.Vc
        )
        
        # Track governing DCR
        for mode_name, dcr_val in [
            (f"{name} Pos Flexure", pos_flex.dcr),
            (f"{name} Neg Flexure", neg_flex.dcr),
            (f"{name} Shear", shear_res.dcr),
            (f"{name} Torsion", torsion_res.dcr)
        ]:
            if dcr_val > max_dcr:
                max_dcr = dcr_val
                governing_mode = mode_name
                
        station_results[name] = RCBeamSectionResult(
            pos_flexure=pos_flex,
            neg_flexure=neg_flex,
            shear=shear_res,
            torsion=torsion_res,
            is_zero_flexure=(pos_flex.is_zero_flexure and neg_flex.is_zero_flexure),
            is_zero_shear=shear_res.is_zero_shear,
            is_zero_torsion=torsion_res.is_zero_torsion
        )
        
    # 5. Serviceability (Branson Ie Weighted Average and 3-Station Crack Spacing Check)
    # 5.1 Calculate cross-sectional properties and Ie for each station
    # End-I (Negative bending dominant: top tension, bottom compression)
    i_rgroup = rebar.end_i
    i_loads = loads.end_i
    i_stirrup_db = get_rebar_db(i_rgroup.stirrup_bar)
    i_As_bot, i_d_bot, _, i_dp_bot = calculate_rebar_group_properties(
        i_rgroup.bot_bars, h, section.cover, i_stirrup_db, is_top=False
    )
    i_As_top, i_d_top, _, i_dp_top = calculate_rebar_group_properties(
        i_rgroup.top_bars, h, section.cover_top, i_stirrup_db, is_top=True
    )
    
    # Center-M (Positive bending dominant: bottom tension, top compression)
    mid_rgroup = rebar.center_m
    mid_loads = loads.center_m
    mid_stirrup_db = get_rebar_db(mid_rgroup.stirrup_bar)
    mid_As_bot, mid_d_bot, _, mid_dp_bot = calculate_rebar_group_properties(
        mid_rgroup.bot_bars, h, section.cover, mid_stirrup_db, is_top=False
    )
    mid_As_top, mid_d_top, _, mid_dp_top = calculate_rebar_group_properties(
        mid_rgroup.top_bars, h, section.cover_top, mid_stirrup_db, is_top=True
    )
    
    # End-J (Negative bending dominant: top tension, bottom compression)
    j_rgroup = rebar.end_j
    j_loads = loads.end_j
    j_stirrup_db = get_rebar_db(j_rgroup.stirrup_bar)
    j_As_bot, j_d_bot, _, j_dp_bot = calculate_rebar_group_properties(
        j_rgroup.bot_bars, h, section.cover, j_stirrup_db, is_top=False
    )
    j_As_top, j_d_top, _, j_dp_top = calculate_rebar_group_properties(
        j_rgroup.top_bars, h, section.cover_top, j_stirrup_db, is_top=True
    )
    
    # Center-M:
    Ma_m = mid_loads.Ma_pos if mid_loads.Ma_pos > 0 else (mid_loads.Ma_neg if mid_loads.Ma_neg > 0 else 0.0)
    Ig_m, Icr_m, Mcr_m, kd_m, _ = calculate_cracked_section_properties(
        b, h, mid_d_bot, mid_dp_top, mid_As_bot, mid_As_top, fck
    )
    Ie_m = calculate_effective_moment_of_inertia(Ig_m, Icr_m, Mcr_m, Ma_m)
    
    # End-I:
    Ma_i = i_loads.Ma_neg if i_loads.Ma_neg > 0 else (i_loads.Ma_pos if i_loads.Ma_pos > 0 else 0.0)
    Ig_i, Icr_i, Mcr_i, kd_i, _ = calculate_cracked_section_properties(
        b, h, i_d_top, i_dp_bot, i_As_top, i_As_bot, fck
    )
    Ie_i = calculate_effective_moment_of_inertia(Ig_i, Icr_i, Mcr_i, Ma_i)
    
    # End-J:
    Ma_j = j_loads.Ma_neg if j_loads.Ma_neg > 0 else (j_loads.Ma_pos if j_loads.Ma_pos > 0 else 0.0)
    Ig_j, Icr_j, Mcr_j, kd_j, _ = calculate_cracked_section_properties(
        b, h, j_d_top, j_dp_bot, j_As_top, j_As_bot, fck
    )
    Ie_j = calculate_effective_moment_of_inertia(Ig_j, Icr_j, Mcr_j, Ma_j)
    
    # Reinforcement Detailing Arrange Type Linkage
    if rebar.arrange_type == BeamArrangeType.ONE_SECTION:
        Ie_i = Ie_m
        Ie_j = Ie_m
    elif rebar.arrange_type == BeamArrangeType.SYMMETRIC_ENDS:
        Ie_j = Ie_i
        
    # Boundary Support Condition weighted average (KDS 14 20 30 4.2.1(4))
    if section.support == SupportCondition.SIMPLE:
        Ie_avg = Ie_m
    elif section.support == SupportCondition.CONTINUOUS_BOTH:
        Ie_avg = 0.50 * Ie_m + 0.25 * (Ie_i + Ie_j)
    elif section.support == SupportCondition.CONTINUOUS_ONE:
        Ie_cont = max(Ie_i, Ie_j) if (Ie_i > 0 or Ie_j > 0) else Ie_m
        Ie_avg = 0.85 * Ie_m + 0.15 * Ie_cont
    elif section.support == SupportCondition.CANTILEVER:
        Ie_avg = max(Ie_i, Ie_j) if (Ie_i > 0 or Ie_j > 0) else Ie_m
    else:
        Ie_avg = Ie_m
        
    # 5.2 3-Station Crack Spacing Checks (KDS 14 20 30 4.2.3)
    crack_spacing_checks: Dict[str, StationCrackSpacingCheck] = {}
    
    i_is_zero = (i_loads.Mu_neg <= 0.0 and i_loads.Ma_neg <= 0.0 and i_loads.Mu_pos <= 0.0 and i_loads.Ma_pos <= 0.0)
    m_is_zero = (mid_loads.Mu_pos <= 0.0 and mid_loads.Ma_pos <= 0.0 and mid_loads.Mu_neg <= 0.0 and mid_loads.Ma_neg <= 0.0)
    j_is_zero = (j_loads.Mu_neg <= 0.0 and j_loads.Ma_neg <= 0.0 and j_loads.Mu_pos <= 0.0 and j_loads.Ma_pos <= 0.0)
    
    check_i = check_crack_bar_spacing(
        station_name="end_i",
        rebar_pos="TOP",
        b=b,
        d=i_d_top,
        kd=kd_i,
        As=i_As_top,
        fy=fy,
        Ma_kNm=Ma_i,
        clear_cover=section.cover_top,
        stirrup_db=i_stirrup_db,
        bars=i_rgroup.top_bars,
        k_cr=280.0,
        is_zero_load=i_is_zero
    )
    
    check_m = check_crack_bar_spacing(
        station_name="center_m",
        rebar_pos="BOTTOM",
        b=b,
        d=mid_d_bot,
        kd=kd_m,
        As=mid_As_bot,
        fy=fy,
        Ma_kNm=Ma_m,
        clear_cover=section.cover,
        stirrup_db=mid_stirrup_db,
        bars=mid_rgroup.bot_bars,
        k_cr=280.0,
        is_zero_load=m_is_zero
    )
    
    check_j = check_crack_bar_spacing(
        station_name="end_j",
        rebar_pos="TOP",
        b=b,
        d=j_d_top,
        kd=kd_j,
        As=j_As_top,
        fy=fy,
        Ma_kNm=Ma_j,
        clear_cover=section.cover_top,
        stirrup_db=j_stirrup_db,
        bars=j_rgroup.top_bars,
        k_cr=280.0,
        is_zero_load=j_is_zero
    )
    
    if rebar.arrange_type == BeamArrangeType.ONE_SECTION:
        crack_spacing_checks["center_m"] = check_m
    elif rebar.arrange_type == BeamArrangeType.SYMMETRIC_ENDS:
        crack_spacing_checks["end_i"] = check_i
        crack_spacing_checks["center_m"] = check_m
        check_j_sym = check_i.model_copy()
        check_j_sym.station = "end_j"
        crack_spacing_checks["end_j"] = check_j_sym
    else:  # THREE_STATIONS
        crack_spacing_checks["end_i"] = check_i
        crack_spacing_checks["center_m"] = check_m
        crack_spacing_checks["end_j"] = check_j
        
    # Execute full serviceability evaluation with weighted Ie
    num_bot_bars = sum(row.count for row in mid_rgroup.bot_bars)
    serv_res = calculate_rc_beam_serviceability(
        b=b, h=h, d=mid_d_bot, d_prime=mid_dp_top,
        As=mid_As_bot, As_prime=mid_As_top, fck=fck, fy=fy,
        Ma=Ma_m, Msus=mid_loads.Msus, length=section.length, support=section.support,
        clear_cover=section.cover, stirrup_db=mid_stirrup_db,
        num_tension_bars=num_bot_bars, defl_ratio=loads.deflection_limit_ratio,
        Ie_override=Ie_avg,
        Ie_mid=Ie_m,
        Ie_end_i=Ie_i,
        Ie_end_j=Ie_j,
        crack_spacing_checks=crack_spacing_checks
    )
    
    if serv_res.dcr_defl > max_dcr:
        max_dcr = serv_res.dcr_defl
        governing_mode = "Deflection"
    if serv_res.dcr_crack > max_dcr:
        max_dcr = serv_res.dcr_crack
        governing_mode = "Crack Width"
        
    for station_k, ccheck in serv_res.crack_spacing_checks.items():
        if ccheck.dcr > max_dcr:
            max_dcr = ccheck.dcr
            governing_mode = f"{station_k} Crack Spacing"
            
    overall_status = "OK" if (max_dcr <= 1.0 and serv_res.status == "OK") else "NG"
    
    return RCBeamResult(
        end_i=station_results["end_i"],
        center_m=station_results["center_m"],
        end_j=station_results["end_j"],
        serviceability=serv_res,
        max_dcr=round(max_dcr, 3),
        governing_mode=governing_mode,
        status=overall_status
    )


# ============================================================================
# 5. Backward Compatibility Layer (RCBeamInput & design_rc_beam)
# ============================================================================

@dataclass
class RCBeamInput:
    """RC Beam Geometry, Materials, Loading, and Serviceability Input Parameters (Legacy)."""
    name: str = "B1"
    b: float = 400.0           # mm (Section width bw)
    h: float = 600.0           # mm (Section total depth)
    cover: float = 50.0        # mm (Clear cover to tension rebar centroid)
    cover_prime: float = 50.0  # mm (Clear cover to compression rebar centroid)
    side_cover: float = 40.0   # mm (Clear cover to stirrup edge for torsion)
    
    # Tension Reinforcement (Bottom for positive moment, Top for negative)
    As: float = 1935.0         # mm2 (e.g., 5-D22 = 5 * 387 mm2)
    # Compression Reinforcement
    As_prime: float = 0.0      # mm2 (e.g., 2-D19 = 2 * 287 mm2)
    
    # Shear Stirrups (2 legs)
    Av: float = 142.6          # mm2 (e.g., 2-D10 = 2 * 71.3 mm2)
    s: float = 200.0           # mm (Stirrup spacing)
    
    # Factored Design Forces (Ultimate Limit State)
    Mu: float = 250.0          # kN*m (Design flexural moment)
    Vu: float = 150.0          # kN (Design shear force)
    Tu: float = 0.0            # kN*m (Design torsional moment)
    
    # Serviceability Forces & Parameters (KDS 14 20 30)
    Ma: float = 160.0          # kN*m (Service load maximum moment)
    span_length: float = 6000.0# mm (Beam clear span length L)
    sustained_ratio: float = 0.70 # Ratio of sustained load to Ma
    time_duration_months: int = 60 # Load duration (>= 60 months => xi = 2.0)
    allowable_deflection_ratio: float = 240.0 # L / 240
    w_lim: float = 0.3         # mm (Allowable crack width limit)
    num_tension_bars: int = 5  # Number of tension bars in outer layer
    
    # Materials
    concrete: ConcreteMaterial = field(default_factory=ConcreteMaterial)
    rebar: RebarMaterial = field(default_factory=RebarMaterial)
    rebar_stirrup: Optional[RebarMaterial] = None
    is_seismic: bool = False


@dataclass
class RCBeamLegacyResult:
    """RC Beam Design & Verification Output (Legacy Dataclass Format)."""
    # 1. Flexure (KDS 14 20 20)
    d: float                   # mm (Effective tension depth)
    d_prime: float             # mm (Effective compression depth)
    a: float                   # mm (Equivalent stress block depth)
    c: float                   # mm (Neutral axis depth)
    fs_prime: float            # MPa (Compression steel stress)
    is_top_yielding: bool      # True if compression steel yields
    et: float                  # Net tensile strain in extreme tension steel
    phi_b: float               # Flexural strength reduction factor
    Mn: float                  # kN*m (Nominal flexural capacity)
    phi_Mn: float              # kN*m (Design flexural capacity)
    flexure_dcr: float         # Mu / phi_Mn
    rho: float                 # As / (b * d)
    rho_min: float             # Minimum flexural rebar ratio
    rho_max: float             # Maximum rebar ratio limit (et >= 0.004)
    
    # 2. Shear (KDS 14 20 22)
    Vc: float                  # kN (Concrete nominal shear capacity)
    Vs: float                  # kN (Stirrup nominal shear capacity)
    Vs_max: float              # kN (Upper limit of Vs = 2/3 * sqrt(fck) * b * d)
    Vn: float                  # kN (Total nominal shear capacity)
    phi_v: float               # Shear reduction factor (0.75)
    phi_Vn: float              # kN (Design shear capacity)
    shear_dcr: float           # Vu / phi_Vn
    s_max: float               # mm (Maximum allowable stirrup spacing)
    Av_min: float              # mm2 (Minimum stirrup area per spacing s)
    
    # 3. Torsion & Interaction (KDS 14 20 22)
    Tcr: float                 # kN*m (Cracking torsional moment)
    Tth: float                 # kN*m (Threshold torsion limit = phi * Tcr / 4)
    is_torsion_ignored: bool   # True if Tu <= Tth
    Aoh: float                 # mm2 (Area enclosed by centerline of outermost closed stirrup)
    ph: float                  # mm (Perimeter of centerline of outermost closed stirrup)
    Ao: float                  # mm2 (Gross area enclosed by shear flow path = 0.85 * Aoh)
    At_over_s_req: float       # mm2/mm (Required single-leg torsion stirrup per unit length)
    Al_req: float              # mm2 (Required longitudinal torsional steel)
    Al_min: float              # mm2 (Minimum longitudinal torsional steel)
    Tn: float                  # kN*m (Nominal torsional capacity based on At/s)
    phi_Tn: float              # kN*m (Design torsional capacity)
    torsion_dcr: float         # Tu / phi_Tn
    combined_stress: float     # MPa (Combined shear-torsion shear stress)
    combined_limit: float      # MPa (Allowable upper limit on combined shear stress)
    combined_dcr: float        # Combined stress ratio
    
    # 4. Serviceability - Deflection & Cracking (KDS 14 20 30)
    Ig: float                  # cm4 (Gross moment of inertia)
    Mcr: float                 # kN*m (Cracking moment)
    Icr: float                 # cm4 (Cracked moment of inertia)
    Ie: float                  # cm4 (Branson effective moment of inertia)
    delta_elastic: float       # mm (Immediate elastic deflection)
    xi_factor: float           # Long-term multiplier time factor xi
    lambda_delta: float        # Long-term deflection multiplier
    delta_long: float          # mm (Long-term deflection)
    delta_total: float         # mm (Total deflection)
    delta_allowable: float     # mm (Allowable deflection limit)
    deflection_dcr: float      # delta_total / delta_allowable
    
    fs_service: float          # MPa (Service steel stress)
    crack_width: float         # mm (Estimated surface crack width)
    crack_dcr: float           # crack_width / w_lim
    
    # Overall Status
    is_safe: bool              # True if all DCR <= 1.0 and detailing limits satisfied
    summary: str


def design_rc_beam(inp: RCBeamInput) -> RCBeamLegacyResult:
    """Perform full KDS 14 20 00 structural capacity and serviceability check for an RC beam (Legacy)."""
    b = inp.b
    h = inp.h
    d = max(h - inp.cover, 1.0)
    d_prime = min(inp.cover_prime, d - 1.0)
    
    fck = inp.concrete.fck
    fy = inp.rebar.fy
    Es = inp.rebar.Es
    Ec = inp.concrete.Ec
    ecu = inp.concrete.ecu
    ey = inp.rebar.ey
    alpha1 = inp.concrete.alpha1
    beta1 = inp.concrete.beta1
    
    rebar_stirrup = inp.rebar_stirrup if inp.rebar_stirrup is not None else inp.rebar
    fyt = rebar_stirrup.fy
    
    # -------------------------------------------------------------
    # 1. Flexural Strength (Mn) - Singly & Doubly Reinforced
    # -------------------------------------------------------------
    As = max(inp.As, 0.0)
    As_prime = max(inp.As_prime, 0.0)
    
    if As_prime > 0.0 and As > 0.0:
        a_yield = (As * fy - As_prime * fy) / (alpha1 * fck * b)
        c_yield = a_yield / beta1 if beta1 > 0 else a_yield / 0.85
        eps_s_prime_yield = ecu * (c_yield - d_prime) / c_yield if c_yield > 0 else 0.0
        
        if eps_s_prime_yield >= ey and a_yield > 0:
            a = a_yield
            c = c_yield
            fs_prime = fy
            is_top_yielding = True
        else:
            A_quad = alpha1 * fck * beta1 * b
            B_quad = As_prime * Es * ecu - As * fy
            C_quad = - As_prime * Es * ecu * d_prime
            discriminant = max(B_quad ** 2 - 4.0 * A_quad * C_quad, 0.0)
            c = (-B_quad + math.sqrt(discriminant)) / (2.0 * A_quad) if A_quad > 0 else 1.0
            a = beta1 * c
            fs_prime = min(max(Es * ecu * (c - d_prime) / c, -fy), fy) if c > 0 else 0.0
            is_top_yielding = (abs(fs_prime) >= fy * 0.999)
    else:
        a = (As * fy) / (alpha1 * fck * b) if (alpha1 * fck * b) > 0 else 0.0
        c = a / beta1 if beta1 > 0 else a / 0.85
        fs_prime = 0.0
        is_top_yielding = False
        
    et = ecu * (d - c) / c if c > 0 else 0.05
    phi_b = get_phi_flexure(et, ey)
    
    if As_prime > 0.0 and c > 0:
        Cc = alpha1 * fck * a * b
        Cs = As_prime * fs_prime
        Mn_Nmm = (As * fy - Cs) * (d - 0.5 * a) + Cs * (d - d_prime)
    else:
        Mn_Nmm = As * fy * (d - 0.5 * a)
        
    Mn = max(Mn_Nmm / 1e6, 0.0)  # kN*m
    phi_Mn = phi_b * Mn
    flexure_dcr = inp.Mu / phi_Mn if phi_Mn > 0 else (0.0 if inp.Mu == 0 else 999.0)
    
    rho = As / (b * d) if (b * d) > 0 else 0.0
    # KDS 14 20 20: 2022 minimum flexure strength and ductility checks
    fr_beam = inp.concrete.f_cr
    Ig_beam = (b * (h ** 3)) / 12.0
    Mcr_beam = (fr_beam * Ig_beam / (h / 2.0)) / 1e6
    phi_Mn_min = 1.2 * Mcr_beam
    jd_val = max(d - a / 2.0, 0.7 * d)
    As_req_val = (inp.Mu * 1e6) / (phi_b * fy * jd_val) if (phi_b * fy * jd_val > 0 and inp.Mu > 0) else 0.0
    is_min_flexure_ok = (phi_Mn >= phi_Mn_min - 1e-4) or (As_req_val > 0 and As >= (4.0 / 3.0) * As_req_val - 1e-4) or (inp.Mu <= 0.0 and As > 0)
    epsilon_t_min = 0.0040 if fy <= 400.0 else 2.0 * ey
    is_ductility_ok = (et >= epsilon_t_min - 1e-6)
    rho_min = 0.0  # Obsolete KDS formula deprecated
    rho_max = 0.0  # Obsolete KDS formula deprecated
    
    # -------------------------------------------------------------
    # 2. Shear Strength (Vn) - KDS 14 20 22
    # -------------------------------------------------------------
    lambda_factor = inp.concrete.lambda_factor
    Vc_N = (1.0 / 6.0) * lambda_factor * math.sqrt(fck) * b * d
    Vc = Vc_N / 1e3  # kN
    
    Vs_N = (inp.Av * fyt * d) / inp.s if inp.s > 0 else 0.0
    Vs_max_N = (2.0 / 3.0) * math.sqrt(fck) * b * d
    Vs_N = min(Vs_N, Vs_max_N)
    Vs = Vs_N / 1e3
    Vs_max = Vs_max_N / 1e3
    
    Vn = Vc + Vs
    phi_v = get_phi_shear(inp.is_seismic)
    phi_Vn = phi_v * Vn
    shear_dcr = inp.Vu / phi_Vn if phi_Vn > 0 else (0.0 if inp.Vu == 0 else 999.0)
    
    if Vs > (1.0 / 3.0) * math.sqrt(fck) * b * d / 1e3:
        s_max = min(d / 4.0, 300.0)
    else:
        s_max = min(d / 2.0, 600.0)
        
    Av_min = max(0.0625 * math.sqrt(fck) * (b * inp.s) / fyt, 0.35 * (b * inp.s) / fyt) if inp.s > 0 else 0.0
    
    # -------------------------------------------------------------
    # 3. Torsion & Interaction (KDS 14 20 22)
    # -------------------------------------------------------------
    Acp = b * h
    pcp = 2.0 * (b + h)
    Tcr_Nmm = (1.0 / 3.0) * lambda_factor * math.sqrt(fck) * (Acp ** 2) / pcp
    Tcr = Tcr_Nmm / 1e6
    phi_t = 0.75
    Tth = phi_t * (Tcr / 4.0)
    is_torsion_ignored = (abs(inp.Tu) <= Tth)
    
    boh = max(b - 2.0 * inp.side_cover, 10.0)
    hoh = max(h - 2.0 * inp.side_cover, 10.0)
    Aoh = boh * hoh
    ph = 2.0 * (boh + hoh)
    Ao = 0.85 * Aoh
    
    if not is_torsion_ignored and abs(inp.Tu) > 0:
        Tu_abs = abs(inp.Tu)
        Tn_req_Nmm = (Tu_abs / phi_t) * 1e6
        At_over_s_req = Tn_req_Nmm / (2.0 * Ao * fyt * 1.0)
        Al_req = At_over_s_req * ph * (fyt / fy) * 1.0
        Al_min = max((0.42 * math.sqrt(fck) * Acp / fy) - (At_over_s_req * ph * (fyt / fy)), 0.0)
        
        At_prov = inp.Av / 2.0
        Tn_prov_Nmm = (2.0 * Ao * At_prov * fyt * 1.0) / inp.s if inp.s > 0 else 0.0
        Tn = Tn_prov_Nmm / 1e6
        phi_Tn = phi_t * Tn
        torsion_dcr = Tu_abs / phi_Tn if phi_Tn > 0 else 999.0
        
        vu = (inp.Vu * 1e3) / (b * d)
        tu = (Tu_abs * 1e6 * ph) / (1.7 * (Aoh ** 2))
        combined_stress = math.sqrt(vu ** 2 + tu ** 2)
        combined_limit = phi_v * ((Vc_N / (b * d)) + (2.0 / 3.0) * math.sqrt(fck))
        combined_dcr = combined_stress / combined_limit if combined_limit > 0 else 999.0
    else:
        At_over_s_req = 0.0
        Al_req = 0.0
        Al_min = 0.0
        Tn = 0.0
        phi_Tn = 0.0
        torsion_dcr = 0.0
        vu = (inp.Vu * 1e3) / (b * d)
        combined_stress = vu
        combined_limit = phi_v * ((Vc_N / (b * d)) + (2.0 / 3.0) * math.sqrt(fck))
        combined_dcr = shear_dcr
        
    # -------------------------------------------------------------
    # 4. Serviceability - Deflection & Crack (KDS 14 20 30)
    # -------------------------------------------------------------
    # 4.1 Branson Effective Moment of Inertia (Ie)
    Ig_mm4 = (b * (h ** 3)) / 12.0
    Ig = Ig_mm4 / 1e4  # cm4
    yt = h / 2.0
    fr = inp.concrete.f_cr  # MPa = 0.63 * lambda * sqrt(fck)
    Mcr_Nmm = (fr * Ig_mm4) / yt
    Mcr = Mcr_Nmm / 1e6  # kN*m
    
    # Cracked transformed section: kd
    n_ratio = Es / Ec
    A_kd = 0.5 * b
    B_kd = n_ratio * As + max((n_ratio - 1.0) * As_prime, 0.0)
    C_kd = - (n_ratio * As * d + max((n_ratio - 1.0) * As_prime * d_prime, 0.0))
    disc_kd = max(B_kd ** 2 - 4.0 * A_kd * C_kd, 0.0)
    kd = (-B_kd + math.sqrt(disc_kd)) / (2.0 * A_kd) if A_kd > 0 else 0.3 * d
    
    # Cracked moment of inertia Icr
    Icr_mm4 = (b * (kd ** 3)) / 3.0 + n_ratio * As * ((d - kd) ** 2)
    if As_prime > 0 and kd > d_prime:
        Icr_mm4 += (n_ratio - 1.0) * As_prime * ((kd - d_prime) ** 2)
    Icr = Icr_mm4 / 1e4  # cm4
    
    Ma_abs = abs(inp.Ma)
    if Ma_abs <= Mcr or Mcr == 0:
        Ie_mm4 = Ig_mm4
    else:
        m_ratio = (Mcr / Ma_abs) ** 3
        Ie_mm4 = m_ratio * Ig_mm4 + (1.0 - m_ratio) * Icr_mm4
        Ie_mm4 = min(Ie_mm4, Ig_mm4)
        
    Ie = Ie_mm4 / 1e4  # cm4
    
    # 4.2 Immediate and Long-term Deflection
    L = inp.span_length
    delta_elastic = (5.0 * (Ma_abs * 1e6) * (L ** 2)) / (48.0 * Ec * Ie_mm4) if (Ec * Ie_mm4) > 0 else 0.0
    
    # Time factor xi for sustained load
    if inp.time_duration_months >= 60:
        xi_factor = 2.0
    elif inp.time_duration_months >= 12:
        xi_factor = 1.4
    elif inp.time_duration_months >= 6:
        xi_factor = 1.2
    elif inp.time_duration_months >= 3:
        xi_factor = 1.0
    else:
        xi_factor = 0.0
        
    rho_prime = As_prime / (b * d) if (b * d) > 0 else 0.0
    lambda_delta = xi_factor / (1.0 + 50.0 * rho_prime)
    
    delta_sustained_elastic = delta_elastic * inp.sustained_ratio
    delta_long = lambda_delta * delta_sustained_elastic
    delta_total = delta_elastic + delta_long
    
    delta_allowable = L / inp.allowable_deflection_ratio if inp.allowable_deflection_ratio > 0 else 25.0
    deflection_dcr = delta_total / delta_allowable if delta_allowable > 0 else 0.0
    
    # 4.3 Direct Crack Width Check (KDS 14 20 30)
    jd = d - kd / 3.0
    fs_service = (Ma_abs * 1e6) / (As * jd) if (As * jd) > 0 else 0.0
    fs_service = min(fs_service, 0.6 * fy)
    
    dc = inp.cover
    n_bars = max(inp.num_tension_bars, 2)
    A_eff = (2.0 * dc * b) / n_bars
    beta_crack = (h - kd) / (d - kd) if (d - kd) > 0 else 1.2
    
    eps_s_service = fs_service / Es
    crack_width = 1.08 * beta_crack * eps_s_service * ((dc * A_eff) ** (1.0 / 3.0)) if (dc * A_eff) > 0 else 0.0
    crack_dcr = crack_width / inp.w_lim if inp.w_lim > 0 else 0.0
    
    # -------------------------------------------------------------
    # 5. Overall Safety & Summary
    # -------------------------------------------------------------
    max_dcr = max(flexure_dcr, shear_dcr, torsion_dcr, combined_dcr, deflection_dcr, crack_dcr)
    rebar_limits_ok = is_min_flexure_ok and is_ductility_ok and (inp.s <= s_max * 1.001)
    
    is_safe = (max_dcr <= 1.0) and rebar_limits_ok
    status = "OK" if is_safe else "NG"
    
    summary = (
        f"[{status}] DCR_max: {max_dcr:.3f} | Flexure: {flexure_dcr:.3f}, Shear: {shear_dcr:.3f}, "
        f"Deflection: {deflection_dcr:.3f} (delta={delta_total:.1f}mm), Crack: {crack_dcr:.3f} (w={crack_width:.2f}mm)"
    )
    
    return RCBeamLegacyResult(
        d=d,
        d_prime=d_prime,
        a=a,
        c=c,
        fs_prime=fs_prime,
        is_top_yielding=is_top_yielding,
        et=et,
        phi_b=phi_b,
        Mn=Mn,
        phi_Mn=phi_Mn,
        flexure_dcr=flexure_dcr,
        rho=rho,
        rho_min=rho_min,
        rho_max=rho_max,
        Vc=Vc,
        Vs=Vs,
        Vs_max=Vs_max,
        Vn=Vn,
        phi_v=phi_v,
        phi_Vn=phi_Vn,
        shear_dcr=shear_dcr,
        s_max=s_max,
        Av_min=Av_min,
        Tcr=Tcr,
        Tth=Tth,
        is_torsion_ignored=is_torsion_ignored,
        Aoh=Aoh,
        ph=ph,
        Ao=Ao,
        At_over_s_req=At_over_s_req,
        Al_req=Al_req,
        Al_min=Al_min,
        Tn=Tn,
        phi_Tn=phi_Tn,
        torsion_dcr=torsion_dcr,
        combined_stress=combined_stress,
        combined_limit=combined_limit,
        combined_dcr=combined_dcr,
        Ig=Ig,
        Mcr=Mcr,
        Icr=Icr,
        Ie=Ie,
        delta_elastic=delta_elastic,
        xi_factor=xi_factor,
        lambda_delta=lambda_delta,
        delta_long=delta_long,
        delta_total=delta_total,
        delta_allowable=delta_allowable,
        deflection_dcr=deflection_dcr,
        fs_service=fs_service,
        crack_width=crack_width,
        crack_dcr=crack_dcr,
        is_safe=is_safe,
        summary=summary
    )

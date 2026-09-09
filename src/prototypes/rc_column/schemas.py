"""Pydantic V2 Data Models and Schemas for RC Column Prototype.

Conforms 100% to docs/202_rc_column_module_specification.md.
Covers all 10 domains and 48 parameters of Midas Design+ IDD_RCS_COLUMN_PMODE_DLG.
"""

from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field


class LoadCombination(BaseModel):
    """Load combination case schema (IDD_RCS_COLM_GEN_FORCE_DLG_EC)."""
    no: int = Field(default=1, description="하중조합 번호")
    name: str = Field(default="1.4D", description="하중조합 명칭")
    Pu: float = Field(default=1800.0, description="계수 축하중 (kN, 압축=+)")
    Mux: float = Field(default=120.0, description="계수 휨모멘트 X (kN*m)")
    Muy: float = Field(default=80.0, description="계수 휨모멘트 Y (kN*m)")
    Vux: float = Field(default=45.0, description="계수 전단력 X (kN)")
    Vuy: float = Field(default=60.0, description="계수 전단력 Y (kN)")


class RCColumnFullInput(BaseModel):
    """RC Column Full Input Parameter Dictionary (10 Domains, 48 Parameters)."""
    # [도메인 1] 재질 (Materials)
    fck: float = Field(default=24.0, ge=18.0, le=80.0, description="콘크리트 압축강도 (MPa)")
    fy: float = Field(default=400.0, ge=300.0, le=600.0, description="주철근 항복강도 (MPa)")
    fys: float = Field(default=400.0, ge=300.0, le=500.0, description="띠철근 항복강도 (MPa)")
    is_lcon: bool = Field(default=False, description="경량 콘크리트 여부")
    lambda_factor: float = Field(default=1.00, ge=0.75, le=1.00, description="경량 콘크리트 계수 λ")

    # [도메인 2] 형상 및 기하 (Cross Section Geometry)
    shape: str = Field(default="RECT", description="단면 형상 (RECT / CIRCLE)")
    b: float = Field(default=600.0, ge=150.0, le=3000.0, description="사각형 너비 X (mm)")
    h: float = Field(default=600.0, ge=150.0, le=3000.0, description="사각형 높이 Y (mm)")
    r: float = Field(default=0.0, ge=0.0, description="모서리 라운딩 반경 (mm)")
    D: float = Field(default=600.0, ge=200.0, le=3000.0, description="원형 기둥 직경 (mm)")
    cc: float = Field(default=40.0, ge=20.0, le=100.0, description="외곽 순피복 두께 (mm)")

    # [도메인 3] 세장비 및 장주 (Slenderness Parameters)
    Lux: float = Field(default=3600.0, ge=500.0, le=20000.0, description="X축 비지지길이 (mm)")
    Luy: float = Field(default=3600.0, ge=500.0, le=20000.0, description="Y축 비지지길이 (mm)")
    Kx: float = Field(default=1.00, ge=0.5, le=3.0, description="X축 유효좌굴길이계수")
    Ky: float = Field(default=1.00, ge=0.5, le=3.0, description="Y축 유효좌굴길이계수")
    Cmx: float = Field(default=1.00, ge=0.4, le=1.0, description="X축 모멘트 구배계수")
    Cmy: float = Field(default=1.00, ge=0.4, le=1.0, description="Y축 모멘트 구배계수")
    beta_d: float = Field(default=0.20, ge=0.0, le=1.0, description="지속축하중비 βdns")
    chk_2nd: bool = Field(default=False, description="2차 P-Delta 효과 고려")

    # [도메인 4] 하중 및 다중 하중조합 (Forces & Load Combinations)
    Pu: float = Field(default=2000.0, description="단일 계수축력 (kN)")
    Mux: float = Field(default=250.0, ge=0.0, description="계수 휨모멘트 X (kN*m)")
    Muy: float = Field(default=150.0, ge=0.0, description="계수 휨모멘트 Y (kN*m)")
    Vux: float = Field(default=80.0, ge=0.0, description="계수 전단력 X (kN)")
    Vuy: float = Field(default=120.0, ge=0.0, description="계수 전단력 Y (kN)")
    apply_ax2sh: bool = Field(default=True, description="전단 검토 축력 연동 여부")
    load_combinations: List[LoadCombination] = Field(default_factory=list, description="다중 하중조합 목록")

    # [도메인 5] 배근 유형 및 주근/띠철근 상세 (Rebar Detailing)
    Nx: int = Field(default=4, ge=2, le=20, description="X변 주철근 개수")
    Ny: int = Field(default=4, ge=2, le=20, description="Y변 주철근 개수")
    Ncir: int = Field(default=8, ge=6, le=36, description="원형 주철근 개수")
    bar_diam: float = Field(default=25.0, description="주철근 호칭경 (mm)")
    tie_type: str = Field(default="TIED", description="횡철근 종류 (TIED / SPIRAL)")
    tie_diam: float = Field(default=10.0, description="띠철근 호칭경 (mm)")
    s_mid: float = Field(default=300.0, ge=50.0, le=500.0, description="중앙부 띠철근 간격 (mm)")
    use_end_tie: bool = Field(default=False, description="단부 띠철근 별도 적용 여부")
    s_end: float = Field(default=150.0, ge=50.0, le=300.0, description="단부 띠철근 간격 (mm)")
    tie_legs_x: int = Field(default=2, ge=2, le=6, description="X방향 타이 다리 수")
    tie_legs_y: int = Field(default=2, ge=2, le=6, description="Y방향 타이 다리 수")
    chk_tiebar: bool = Field(default=True, description="보조 타이바 전단 검토 반영 여부")
    splice_type: str = Field(default="SPLICE000", description="주근 겹침이음 (SPLICE000 / SPLICE050 / SPLICE100)")

    # [도메인 5 확장] 이종배근, 변별배근 및 타이바 형상 패턴
    rebar_mode: str = Field(default="EQUAL", description="배근 방식 (EQUAL: 균등배근, PER_FACE: 변별배근)")
    use_diff_bar: bool = Field(default=False, description="코너/변 이종배근 적용 여부")
    corner_bar_diam: float = Field(default=25.0, description="코너 주철근 호칭경 (mm)")
    side_bar_diam: float = Field(default=22.0, description="변 주철근 호칭경 (mm)")
    side_x_bars: int = Field(default=2, ge=0, le=10, description="상하 X변 각각의 중간 주철근 수")
    side_y_bars: int = Field(default=2, ge=0, le=10, description="좌우 Y변 각각의 중간 주철근 수")
    d_agg: float = Field(default=25.0, ge=15.0, le=40.0, description="굵은 골재 최대 치수 (mm)")
    tie_pattern: str = Field(default="TYPE_1", description="내부 타이바 레이아웃 (TYPE_1, TYPE_2, TYPE_3, TYPE_4)")

    # [도메인 6] 내진 설계 및 필로티 규정 (Seismic & Piloti)
    chk_seismic: bool = Field(default=False, description="내진설계 규정 적용 여부")
    frame_type: str = Field(default="OMF", description="골조 시스템 (SMF / IMF / OMF)")
    chk_piloti: bool = Field(default=False, description="필로티 기둥 상세 적용 여부")
    omega_0: float = Field(default=3.0, ge=2.0, le=3.5, description="시스템 초과강도계수 Ω0")

    # [도메인 7] 설계 옵션 및 사용성 (Design Options & Serviceability)
    chk_user_rho: bool = Field(default=False, description="철근비 범위 사용자 지정 여부")
    min_rho: float = Field(default=0.010, ge=0.005, le=0.020, description="최소 철근비 하한")
    max_rho: float = Field(default=0.040, ge=0.020, le=0.080, description="최대 철근비 상한")
    chk_serv: bool = Field(default=False, description="사용성 응력 검토 여부")
    k1: float = Field(default=0.6, description="사용성 계수 k1")
    k2: float = Field(default=0.8, description="사용성 계수 k2")
    k3: float = Field(default=0.7, description="사용성 계수 k3")


class GeometryPoint(BaseModel):
    x: float
    y: float


class RebarGeometry(BaseModel):
    x: float
    y: float
    diameter: float
    is_corner: bool = False


class TieLoopGeometry(BaseModel):
    points: List[GeometryPoint]
    closed: bool = True
    line_width: float = 1.5
    color: str = "#2563eb"


class GeometryOutput(BaseModel):
    shape: str
    b: float
    h: float
    D: float
    r: float
    outline: List[GeometryPoint]
    ties: List[TieLoopGeometry]
    rebars: List[RebarGeometry]


class PMPoint(BaseModel):
    phi_P: float
    phi_Mx: float
    phi_My: float
    c: Optional[float] = None
    eps_t: Optional[float] = None
    phi: Optional[float] = None


class CombResult(BaseModel):
    no: int
    name: str
    Pu: float
    Mux: float
    Muy: float
    Vux: float
    Vuy: float
    dcr_pm: float
    dcr_vx: float
    dcr_vy: float
    status: str


class SeismicOutput(BaseModel):
    frame_type: str
    lo: float
    so: float
    so_limit: float
    Ash_req: float
    Ash_prov_x: float
    Ash_prov_y: float
    piloti_status: str
    status: str


class SpliceOutput(BaseModel):
    splice_type: str
    splice_class: str
    ld: float
    ls_tens: float
    lsc_comp: float
    status: str


class RCColumnCheckResult(BaseModel):
    overall_status: str
    max_dcr: float
    critical_case: CombResult
    shape: str
    Ag: float
    Ast: float
    total_bars: int
    rho_g: float
    is_rho_ok: bool
    s_clear: float
    is_sclear_ok: bool
    P0: float
    phi_axial: float
    phi_Pn_max: float
    slender_ratio_x: float
    slender_ratio_y: float
    is_slender_x: bool
    is_slender_y: bool
    delta_ns_x: float
    delta_ns_y: float
    Pc_x: float
    Pc_y: float
    Mc_x: float
    Mc_y: float
    Vcx: float
    Vsx: float
    phi_Vnx: float
    Vcy: float
    Vsy: float
    phi_Vny: float
    Ec: float = 0.0
    Es: float = 200000.0
    beta1: float = 0.85
    Ig_x: float = 0.0
    Ig_y: float = 0.0
    rx: float = 0.0
    ry: float = 0.0
    s_clear_min: float = 25.0
    e_min_x: float = 0.0
    e_min_y: float = 0.0
    Vs_max_x: float = 0.0
    Vs_max_y: float = 0.0
    seismic: SeismicOutput
    splice: SpliceOutput
    curve_x: List[PMPoint]
    curve_y: List[PMPoint]
    mesh_3d: Optional[List[List[float]]] = None
    geometry: GeometryOutput
    comb_results: List[CombResult]

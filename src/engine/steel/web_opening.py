"""Steel Beam Web Opening Verification Module (KDS 14 31 10 / AISC Design Guide 2 / CHK_USWO).

Evaluates flexural and shear capacity reductions, reinforcement plate design,
and Vierendeel action for I-/H-shaped steel beams with rectangular or circular web openings.
"""

from dataclasses import dataclass, field
from enum import Enum
import math
from typing import Optional

from src.engine.materials import SteelMaterial


class OpeningShape(str, Enum):
    RECTANGULAR = "RECTANGULAR"
    CIRCULAR = "CIRCULAR"


@dataclass
class WebOpeningInput:
    """Parameters for Beam Web Opening Design."""
    name: str = "WO1"
    shape: OpeningShape = OpeningShape.RECTANGULAR
    
    # Beam Dimensions (mm)
    H: float = 500.0             # Total depth
    B: float = 200.0             # Width
    tw: float = 9.0              # Web thickness
    tf: float = 14.0             # Flange thickness
    
    # Opening Dimensions (mm)
    ao: float = 300.0            # Opening length along span (or diameter for circular)
    ho: float = 200.0            # Opening height
    e: float = 0.0               # Opening eccentricity from beam centerline (+up, -down)
    
    # Reinforcement Plates (if reinforced, top & bottom)
    has_reinforcement: bool = False
    br: float = 80.0             # Reinforcement plate width (mm)
    tr: float = 10.0             # Reinforcement plate thickness (mm)
    
    # Loading at opening centerline
    Mu: float = 200.0            # kN*m (Factored bending moment at opening)
    Vu: float = 100.0            # kN (Factored shear force at opening)
    
    material: SteelMaterial = field(default_factory=lambda: SteelMaterial(name="SM355", Fy=355.0, Fu=490.0, E=205000.0))


@dataclass
class WebOpeningResult:
    """Web Opening Capacity and Safety Verification Output."""
    shape: OpeningShape
    is_reinforced: bool
    
    # Tee Dimensions (Top & Bottom)
    s_top: float                 # mm (Height of top tee web)
    s_bot: float                 # mm (Height of bottom tee web)
    
    # Capacities at Opening
    Vp_top: float                # kN (Shear capacity of top tee)
    Vp_bot: float                # kN (Shear capacity of bottom tee)
    Vn_opening: float            # kN (Nominal shear capacity at opening)
    phi_Vn: float                # kN (Design shear capacity, phi=0.90)
    shear_dcr: float             # Vu / phi_Vn
    
    Mn_opening: float            # kN*m (Nominal flexural capacity at opening)
    phi_Mn: float                # kN*m (Design flexural capacity, phi=0.90)
    flexure_dcr: float           # Mu / phi_Mn
    
    # Vierendeel Interaction
    vierendeel_dcr: float        # (Mu / phi_Mn)^r + (Vu / phi_Vn)^r interaction
    
    max_dcr: float
    is_safe: bool
    summary: str


def check_web_opening(inp: WebOpeningInput) -> WebOpeningResult:
    """Evaluate structural capacity and Vierendeel action at beam web opening."""
    Fy = inp.material.Fy_design if hasattr(inp.material, 'Fy_design') else inp.material.Fy
    phi = 0.90
    
    H = inp.H
    B = inp.B
    tw = inp.tw
    tf = inp.tf
    ho = inp.ho if inp.shape == OpeningShape.RECTANGULAR else inp.ao
    ao = inp.ao
    e = inp.e
    
    # 1. Tee Geometry (Top Tee and Bottom Tee)
    # Distance from mid-depth to top/bottom edges of opening:
    # Top edge of opening: H/2 - (e + ho/2)
    # Top tee depth = (H/2 - e - ho/2) + tf
    s_top = max((H / 2.0) - e - (ho / 2.0) - tf, 10.0)
    s_bot = max((H / 2.0) + e - (ho / 2.0) - tf, 10.0)
    
    # Top Tee Area
    At = B * tf + s_top * tw
    Ab = B * tf + s_bot * tw
    
    if inp.has_reinforcement:
        At += inp.br * inp.tr
        Ab += inp.br * inp.tr
        
    # 2. Shear Capacity at Opening (Vn)
    # Vpt = 0.6 * Fy * s_top * tw
    Vpt = 0.60 * Fy * (s_top * tw) / 1e3
    Vpb = 0.60 * Fy * (s_bot * tw) / 1e3
    
    # Reduction for aspect ratio ao / ho
    nu_aspect = math.sqrt(1.0 / (1.0 + 0.003 * ((ao / max(ho, 1.0)) ** 2)))
    Vn_opening = (Vpt + Vpb) * nu_aspect
    phi_Vn = phi * Vn_opening
    shear_dcr = inp.Vu / phi_Vn if phi_Vn > 0 else 999.0
    
    # 3. Flexural Capacity at Opening (Mn)
    # Pure unreduced plastic moment: Mp = Fy * Zx
    h_web = H - 2.0 * tf
    Zx_net = (2.0 * (B * tf * (H / 2.0 - tf / 2.0)) + tw * ((h_web / 2.0)**2) - tw * ((ho / 2.0)**2))
    
    if inp.has_reinforcement:
        Zx_net += 2.0 * (inp.br * inp.tr * (ho / 2.0 + inp.tr / 2.0))
        
    Mn_opening = (Fy * Zx_net) / 1e6
    phi_Mn = phi * Mn_opening
    flexure_dcr = inp.Mu / phi_Mn if phi_Mn > 0 else 999.0
    
    # 4. Interaction Formula (AISC DG2 / CHK_USWO: (M/phiMn)^3 + (V/phiVn)^3 <= 1.0)
    vierendeel_dcr = (flexure_dcr ** 3 + shear_dcr ** 3) ** (1.0 / 3.0)
    max_dcr = max(flexure_dcr, shear_dcr, vierendeel_dcr)
    
    is_safe = (max_dcr <= 1.0) and (ho <= 0.70 * H)
    
    status = "OK" if is_safe else "NG"
    summary = (f"[{status}] Web Opening DCR={max_dcr:.3f} "
               f"(Flexure={flexure_dcr:.3f}, Shear={shear_dcr:.3f}, Vierendeel={vierendeel_dcr:.3f})")
    
    return WebOpeningResult(
        shape=inp.shape,
        is_reinforced=inp.has_reinforcement,
        s_top=s_top,
        s_bot=s_bot,
        Vp_top=Vpt,
        Vp_bot=Vpb,
        Vn_opening=Vn_opening,
        phi_Vn=phi_Vn,
        shear_dcr=shear_dcr,
        Mn_opening=Mn_opening,
        phi_Mn=phi_Mn,
        flexure_dcr=flexure_dcr,
        vierendeel_dcr=vierendeel_dcr,
        max_dcr=max_dcr,
        is_safe=is_safe,
        summary=summary
    )

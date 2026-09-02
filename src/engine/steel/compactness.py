"""Steel Section Compactness & Slenderness Classification (KDS 14 31 10 Table 4.1-1 & Table 4.1-2).

Classifies steel cross-sections into Compact, Non-Compact, or Slender based on
width-to-thickness ratios (lambda = b/t, h/tw, D/t) for flanges, webs, and walls under
flexure and axial compression. Computes reduction factors Q (Qs, Qa) / effective area Ae.
"""

from dataclasses import dataclass
from enum import Enum
import math
from typing import Optional


class SectionClassification(str, Enum):
    COMPACT = "Compact"           # 조밀단면 (lambda <= lambda_p)
    NON_COMPACT = "Non-Compact"   # 비조밀단면 (lambda_p < lambda <= lambda_r)
    SLENDER = "Slender"           # 세장단면 (lambda > lambda_r)


class SectionType(str, Enum):
    H_SHAPE = "H"                 # I/H-Shape
    BOX = "BOX"                   # Rectangular / Square Hollow Section
    PIPE = "PIPE"                 # Circular Hollow Section / Pipe
    ANGLE = "ANGLE"               # L-Angle
    CHANNEL = "CHANNEL"           # C-Channel
    TEE = "TEE"                   # T-Shape


@dataclass
class ElementCompactness:
    """Compactness evaluation result for an individual plate element (flange, web, etc.)."""
    element_name: str
    lambda_val: float             # Actual width-thickness ratio (b/t or h/tw or D/t)
    lambda_p: float               # Limiting ratio for compact section
    lambda_r: float               # Limiting ratio for non-compact section
    classification: SectionClassification
    is_compact: bool
    is_non_compact: bool
    is_slender: bool


@dataclass
class SectionCompactnessResult:
    """Overall section compactness classification result."""
    section_type: SectionType
    flange: Optional[ElementCompactness]
    web: Optional[ElementCompactness]
    overall_classification: SectionClassification
    is_compact: bool
    is_slender: bool
    Q: float                      # Slenderness reduction factor (1.0 for non-slender)
    Ae_ratio: float               # Ae / Ag effective area ratio


def check_h_section_compactness(
    B: float,
    tf: float,
    H: float,
    tw: float,
    Fy: float,
    E: float = 205000.0,
    stress_state: str = "flexure"  # "flexure" or "compression"
) -> SectionCompactnessResult:
    """Evaluate compactness for H-shaped rolled or welded sections (KDS 14 31 10).
    
    Flange: Unstiffened element under uniform compression (b = B / 2).
    Web: Stiffened element under flexure (h = H - 2*tf) or uniform compression.
    """
    sqrt_E_Fy = math.sqrt(E / Fy)
    
    # 1. Flange compactness (b / tf)
    b_f = B / 2.0
    lambda_f = b_f / tf if tf > 0 else 999.0
    
    if stress_state == "flexure":
        lambda_pf = 0.38 * sqrt_E_Fy
        lambda_rf = 1.00 * sqrt_E_Fy
    else:  # compression
        lambda_pf = 0.38 * sqrt_E_Fy  # KDS 14 31 10 Table 4.1-2
        lambda_rf = 0.56 * sqrt_E_Fy
        
    if lambda_f <= lambda_pf:
        class_f = SectionClassification.COMPACT
    elif lambda_f <= lambda_rf:
        class_f = SectionClassification.NON_COMPACT
    else:
        class_f = SectionClassification.SLENDER
        
    flange_elem = ElementCompactness(
        element_name="Flange",
        lambda_val=lambda_f,
        lambda_p=lambda_pf,
        lambda_r=lambda_rf,
        classification=class_f,
        is_compact=(class_f == SectionClassification.COMPACT),
        is_non_compact=(class_f == SectionClassification.NON_COMPACT),
        is_slender=(class_f == SectionClassification.SLENDER)
    )
    
    # 2. Web compactness (h / tw)
    h_w = max(H - 2.0 * tf, 1.0)
    lambda_w = h_w / tw if tw > 0 else 999.0
    
    if stress_state == "flexure":
        lambda_pw = 3.76 * sqrt_E_Fy
        lambda_rw = 5.70 * sqrt_E_Fy
    else:  # compression
        lambda_pw = 1.49 * sqrt_E_Fy
        lambda_rw = 1.49 * sqrt_E_Fy  # Compression members: no non-compact range (compact vs slender)
        
    if lambda_w <= lambda_pw:
        class_w = SectionClassification.COMPACT
    elif lambda_w <= lambda_rw:
        class_w = SectionClassification.NON_COMPACT
    else:
        class_w = SectionClassification.SLENDER
        
    web_elem = ElementCompactness(
        element_name="Web",
        lambda_val=lambda_w,
        lambda_p=lambda_pw,
        lambda_r=lambda_rw,
        classification=class_w,
        is_compact=(class_w == SectionClassification.COMPACT),
        is_non_compact=(class_w == SectionClassification.NON_COMPACT),
        is_slender=(class_w == SectionClassification.SLENDER)
    )
    
    # Overall Classification
    if class_f == SectionClassification.SLENDER or class_w == SectionClassification.SLENDER:
        overall = SectionClassification.SLENDER
    elif class_f == SectionClassification.NON_COMPACT or class_w == SectionClassification.NON_COMPACT:
        overall = SectionClassification.NON_COMPACT
    else:
        overall = SectionClassification.COMPACT
        
    # Slenderness factor Q calculation (KDS 14 31 10 4.3.4)
    Qs = 1.0
    if class_f == SectionClassification.SLENDER:
        # Unstiffened element Qs
        if lambda_f <= 1.03 * sqrt_E_Fy:
            Qs = 1.415 - 0.74 * (lambda_f / sqrt_E_Fy)
        else:
            Qs = 0.69 * E / (Fy * (lambda_f ** 2))
        Qs = min(max(Qs, 0.0), 1.0)
        
    Qa = 1.0
    if class_w == SectionClassification.SLENDER:
        # Stiffened element effective width
        f_stress = Fy * Qs
        be = 1.92 * tw * math.sqrt(E / f_stress) * (1.0 - 0.34 / lambda_w * math.sqrt(E / f_stress))
        be = min(be, h_w)
        Ag = 2.0 * (B * tf) + h_w * tw
        A_eff = 2.0 * (B * tf) + be * tw
        Qa = A_eff / Ag if Ag > 0 else 1.0
        Qa = min(max(Qa, 0.0), 1.0)
        
    Q = Qs * Qa
    Ae_ratio = Q
    
    return SectionCompactnessResult(
        section_type=SectionType.H_SHAPE,
        flange=flange_elem,
        web=web_elem,
        overall_classification=overall,
        is_compact=(overall == SectionClassification.COMPACT),
        is_slender=(overall == SectionClassification.SLENDER),
        Q=Q,
        Ae_ratio=Ae_ratio
    )


def check_box_section_compactness(
    B: float,
    H: float,
    t: float,
    Fy: float,
    E: float = 205000.0,
    stress_state: str = "flexure"
) -> SectionCompactnessResult:
    """Evaluate compactness for rectangular / square hollow structural sections (Box/HSS)."""
    sqrt_E_Fy = math.sqrt(E / Fy)
    b_clear = max(B - 3.0 * t, 1.0)
    h_clear = max(H - 3.0 * t, 1.0)
    
    lambda_f = b_clear / t if t > 0 else 999.0
    lambda_w = h_clear / t if t > 0 else 999.0
    
    if stress_state == "flexure":
        lambda_pf = 1.12 * sqrt_E_Fy
        lambda_rf = 1.40 * sqrt_E_Fy
        lambda_pw = 2.42 * sqrt_E_Fy
        lambda_rw = 5.70 * sqrt_E_Fy
    else:
        lambda_pf = 1.40 * sqrt_E_Fy
        lambda_rf = 1.40 * sqrt_E_Fy
        lambda_pw = 1.40 * sqrt_E_Fy
        lambda_rw = 1.40 * sqrt_E_Fy
        
    # Flange
    if lambda_f <= lambda_pf:
        class_f = SectionClassification.COMPACT
    elif lambda_f <= lambda_rf:
        class_f = SectionClassification.NON_COMPACT
    else:
        class_f = SectionClassification.SLENDER
        
    flange_elem = ElementCompactness(
        element_name="Flange",
        lambda_val=lambda_f,
        lambda_p=lambda_pf,
        lambda_r=lambda_rf,
        classification=class_f,
        is_compact=(class_f == SectionClassification.COMPACT),
        is_non_compact=(class_f == SectionClassification.NON_COMPACT),
        is_slender=(class_f == SectionClassification.SLENDER)
    )
    
    # Web
    if lambda_w <= lambda_pw:
        class_w = SectionClassification.COMPACT
    elif lambda_w <= lambda_rw:
        class_w = SectionClassification.NON_COMPACT
    else:
        class_w = SectionClassification.SLENDER
        
    web_elem = ElementCompactness(
        element_name="Web",
        lambda_val=lambda_w,
        lambda_p=lambda_pw,
        lambda_r=lambda_rw,
        classification=class_w,
        is_compact=(class_w == SectionClassification.COMPACT),
        is_non_compact=(class_w == SectionClassification.NON_COMPACT),
        is_slender=(class_w == SectionClassification.SLENDER)
    )
    
    if class_f == SectionClassification.SLENDER or class_w == SectionClassification.SLENDER:
        overall = SectionClassification.SLENDER
    elif class_f == SectionClassification.NON_COMPACT or class_w == SectionClassification.NON_COMPACT:
        overall = SectionClassification.NON_COMPACT
    else:
        overall = SectionClassification.COMPACT
        
    Q = 1.0
    if overall == SectionClassification.SLENDER:
        be_f = min(1.92 * t * math.sqrt(E / Fy) * (1.0 - 0.38 / lambda_f * math.sqrt(E / Fy)), b_clear)
        be_w = min(1.92 * t * math.sqrt(E / Fy) * (1.0 - 0.38 / lambda_w * math.sqrt(E / Fy)), h_clear)
        Ag = 2.0 * t * (B + H - 2.0 * t)
        A_eff = 2.0 * t * (be_f + be_w)
        Q = min(max(A_eff / Ag if Ag > 0 else 1.0, 0.0), 1.0)
        
    return SectionCompactnessResult(
        section_type=SectionType.BOX,
        flange=flange_elem,
        web=web_elem,
        overall_classification=overall,
        is_compact=(overall == SectionClassification.COMPACT),
        is_slender=(overall == SectionClassification.SLENDER),
        Q=Q,
        Ae_ratio=Q
    )


def check_pipe_section_compactness(
    D: float,
    t: float,
    Fy: float,
    E: float = 205000.0,
    stress_state: str = "flexure"
) -> SectionCompactnessResult:
    """Evaluate compactness for circular hollow sections / pipes (KDS 14 31 10)."""
    lambda_val = D / t if t > 0 else 999.0
    
    if stress_state == "flexure":
        lambda_p = 0.07 * (E / Fy)
        lambda_r = 0.31 * (E / Fy)
    else:  # compression
        lambda_p = 0.11 * (E / Fy)
        lambda_r = 0.11 * (E / Fy)
        
    if lambda_val <= lambda_p:
        overall = SectionClassification.COMPACT
    elif lambda_val <= lambda_r:
        overall = SectionClassification.NON_COMPACT
    else:
        overall = SectionClassification.SLENDER
        
    elem = ElementCompactness(
        element_name="Wall",
        lambda_val=lambda_val,
        lambda_p=lambda_p,
        lambda_r=lambda_r,
        classification=overall,
        is_compact=(overall == SectionClassification.COMPACT),
        is_non_compact=(overall == SectionClassification.NON_COMPACT),
        is_slender=(overall == SectionClassification.SLENDER)
    )
    
    Q = 1.0
    if overall == SectionClassification.SLENDER:
        Q = (0.038 * E / (Fy * (D / t))) + (2.0 / 3.0)
        Q = min(max(Q, 0.0), 1.0)
        
    return SectionCompactnessResult(
        section_type=SectionType.PIPE,
        flange=elem,
        web=None,
        overall_classification=overall,
        is_compact=(overall == SectionClassification.COMPACT),
        is_slender=(overall == SectionClassification.SLENDER),
        Q=Q,
        Ae_ratio=Q
    )


def check_angle_section_compactness(
    B: float,
    t: float,
    Fy: float,
    E: float = 205000.0
) -> SectionCompactnessResult:
    """Evaluate compactness for single angle leg under compression (KDS 14 31 10)."""
    sqrt_E_Fy = math.sqrt(E / Fy)
    lambda_val = B / t if t > 0 else 999.0
    lambda_p = 0.54 * sqrt_E_Fy
    lambda_r = 0.91 * sqrt_E_Fy
    
    if lambda_val <= lambda_p:
        overall = SectionClassification.COMPACT
    elif lambda_val <= lambda_r:
        overall = SectionClassification.NON_COMPACT
    else:
        overall = SectionClassification.SLENDER
        
    elem = ElementCompactness(
        element_name="Leg",
        lambda_val=lambda_val,
        lambda_p=lambda_p,
        lambda_r=lambda_r,
        classification=overall,
        is_compact=(overall == SectionClassification.COMPACT),
        is_non_compact=(overall == SectionClassification.NON_COMPACT),
        is_slender=(overall == SectionClassification.SLENDER)
    )
    
    Qs = 1.0
    if overall == SectionClassification.SLENDER:
        if lambda_val <= 1.52 * sqrt_E_Fy:
            Qs = 1.340 - 0.76 * (lambda_val / sqrt_E_Fy)
        else:
            Qs = 0.53 * E / (Fy * (lambda_val ** 2))
        Qs = min(max(Qs, 0.0), 1.0)
        
    return SectionCompactnessResult(
        section_type=SectionType.ANGLE,
        flange=elem,
        web=None,
        overall_classification=overall,
        is_compact=(overall == SectionClassification.COMPACT),
        is_slender=(overall == SectionClassification.SLENDER),
        Q=Qs,
        Ae_ratio=Qs
    )

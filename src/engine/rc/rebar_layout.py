"""RC Beam Reinforcement Layout and Detailing Auto-Design Engine.

Calculates optimal rebar arrangements (1-layer and 2-layer) conforming to
KDS 14 20 00 / KDS 14 20 50 bar spacing, clear cover, and aggregate clearance rules.
"""

from dataclasses import dataclass, field
import math
from typing import List, Optional, Tuple, Dict


# KS Standard Deformed Bar Database (KSD 3504)
REBAR_DB: Dict[str, Dict[str, float]] = {
    "D10": {"db": 9.53, "area": 71.33, "weight": 0.560},
    "D13": {"db": 12.7, "area": 126.7, "weight": 0.995},
    "D16": {"db": 15.9, "area": 198.6, "weight": 1.560},
    "D19": {"db": 19.1, "area": 286.5, "weight": 2.250},
    "D22": {"db": 22.2, "area": 387.1, "weight": 3.040},
    "D25": {"db": 25.4, "area": 506.7, "weight": 3.980},
    "D29": {"db": 28.6, "area": 642.4, "weight": 5.040},
    "D32": {"db": 31.8, "area": 794.2, "weight": 6.230},
}


@dataclass
class RebarLayer:
    """Individual horizontal layer of rebars in beam section."""
    layer_index: int           # 1 = outermost (bottom for positive moment), 2 = inner
    bar_size: str              # e.g., 'D22'
    num_bars: int              # e.g., 4
    db: float                  # mm (Bar diameter)
    bar_area: float            # mm2 (Single bar area)
    total_area: float          # mm2 (Layer total area)
    y_centroid: float          # mm (Distance from extreme tension face to layer centroid)
    x_coords: List[float]      # mm (X-coordinates of each bar center from left face)
    clear_spacing: float       # mm (Clear space between adjacent bars)


@dataclass
class BeamRebarArrangement:
    """Complete rebar arrangement candidate for beam section."""
    bar_size: str
    total_bars: int
    num_layers: int
    layers: List[RebarLayer]
    total_area: float          # mm2
    effective_d: float         # mm (Total effective depth d = h - y_centroid_total)
    centroid_from_bottom: float# mm (Total centroid distance from bottom face)
    is_valid: bool             # True if spacing and cover constraints are satisfied
    reason: str = ""


@dataclass
class BeamAutoDesignResult:
    """Result of automated rebar design optimization."""
    As_req: float              # mm2 (Required steel area)
    selected_arrangement: Optional[BeamRebarArrangement]
    all_candidates: List[BeamRebarArrangement] = field(default_factory=list)
    stirrup_size: str = "D10"
    stirrup_spacing: float = 200.0
    stirrup_legs: int = 2
    stirrup_area: float = 142.66  # mm2


def calculate_bar_spacing_capacity(
    b: float,
    bar_size: str,
    cover: float = 40.0,
    stirrup_db: float = 9.53,
    max_aggregate: float = 25.0
) -> Tuple[int, float]:
    """Calculate maximum number of bars that can fit in a single horizontal layer.
    
    Returns:
        (max_bars, clear_spacing)
    """
    bar_info = REBAR_DB.get(bar_size, REBAR_DB["D22"])
    db = bar_info["db"]
    min_clear_spacing = max(25.0, db, 1.33 * max_aggregate)
    
    # Available width between inner faces of stirrups
    # inner_width = b - 2 * cover - 2 * stirrup_db
    inner_width = b - 2.0 * (cover + stirrup_db)
    if inner_width <= db:
        return 0, 0.0
    
    # For n bars: (n * db) + (n - 1) * min_clear_spacing <= inner_width
    # n * (db + min_clear_spacing) - min_clear_spacing <= inner_width
    # n * (db + min_clear_spacing) <= inner_width + min_clear_spacing
    max_bars = int(math.floor((inner_width + min_clear_spacing) / (db + min_clear_spacing)))
    max_bars = max(max_bars, 1)
    
    if max_bars > 1:
        actual_clear = (inner_width - max_bars * db) / (max_bars - 1)
    else:
        actual_clear = inner_width - db
        
    return max_bars, actual_clear


def create_rebar_arrangement(
    b: float,
    h: float,
    bar_size: str,
    num_bars: int,
    cover: float = 40.0,
    stirrup_db: float = 9.53,
    max_aggregate: float = 25.0,
    vertical_bar_clearance: float = 25.0
) -> BeamRebarArrangement:
    """Create geometric layout and calculate centroids for a given bar count."""
    bar_info = REBAR_DB.get(bar_size, REBAR_DB["D22"])
    db = bar_info["db"]
    single_area = bar_info["area"]
    min_clear_spacing = max(25.0, db, 1.33 * max_aggregate)
    
    max_layer1, _ = calculate_bar_spacing_capacity(b, bar_size, cover, stirrup_db, max_aggregate)
    
    if max_layer1 < 2:
        return BeamRebarArrangement(
            bar_size=bar_size,
            total_bars=num_bars,
            num_layers=1,
            layers=[],
            total_area=num_bars * single_area,
            effective_d=h - cover - stirrup_db - db / 2.0,
            centroid_from_bottom=cover + stirrup_db + db / 2.0,
            is_valid=False,
            reason="Section width too small for 2 bars."
        )
        
    inner_left = cover + stirrup_db
    inner_width = b - 2.0 * inner_left
    
    layers: List[RebarLayer] = []
    
    if num_bars <= max_layer1:
        # Single layer
        n1 = num_bars
        if n1 > 1:
            clear_s1 = (inner_width - n1 * db) / (n1 - 1)
            step = db + clear_s1
            x_coords = [inner_left + db / 2.0 + i * step for i in range(n1)]
        else:
            clear_s1 = inner_width - db
            x_coords = [b / 2.0]
            
        y1 = cover + stirrup_db + db / 2.0
        layers.append(RebarLayer(
            layer_index=1,
            bar_size=bar_size,
            num_bars=n1,
            db=db,
            bar_area=single_area,
            total_area=n1 * single_area,
            y_centroid=y1,
            x_coords=x_coords,
            clear_spacing=clear_s1
        ))
        total_centroid = y1
        is_valid = (clear_s1 >= min_clear_spacing * 0.99)
        reason = "OK" if is_valid else f"Clear spacing {clear_s1:.1f}mm < required {min_clear_spacing:.1f}mm"
        
    else:
        # Two layers
        # Even distribution: try to place more or equal in layer 1
        n1 = min(max_layer1, int(math.ceil(num_bars / 2.0)))
        n2 = num_bars - n1
        
        # Layer 1
        clear_s1 = (inner_width - n1 * db) / (n1 - 1) if n1 > 1 else (inner_width - db)
        step1 = db + clear_s1 if n1 > 1 else 0
        x1_coords = [inner_left + db / 2.0 + i * step1 for i in range(n1)]
        y1 = cover + stirrup_db + db / 2.0
        layers.append(RebarLayer(
            layer_index=1,
            bar_size=bar_size,
            num_bars=n1,
            db=db,
            bar_area=single_area,
            total_area=n1 * single_area,
            y_centroid=y1,
            x_coords=x1_coords,
            clear_spacing=clear_s1
        ))
        
        # Layer 2
        clear_s2 = (inner_width - n2 * db) / (n2 - 1) if n2 > 1 else (inner_width - db)
        step2 = db + clear_s2 if n2 > 1 else 0
        x2_coords = [inner_left + db / 2.0 + i * step2 for i in range(n2)]
        y2 = y1 + db / 2.0 + vertical_bar_clearance + db / 2.0
        layers.append(RebarLayer(
            layer_index=2,
            bar_size=bar_size,
            num_bars=n2,
            db=db,
            bar_area=single_area,
            total_area=n2 * single_area,
            y_centroid=y2,
            x_coords=x2_coords,
            clear_spacing=clear_s2
        ))
        
        # Weighted centroid
        total_centroid = (n1 * single_area * y1 + n2 * single_area * y2) / (num_bars * single_area)
        is_valid = (clear_s1 >= min_clear_spacing * 0.99) and (clear_s2 >= min_clear_spacing * 0.99) and (n2 <= max_layer1)
        reason = "OK" if is_valid else "Two-layer bar spacing constraint violated"

    return BeamRebarArrangement(
        bar_size=bar_size,
        total_bars=num_bars,
        num_layers=len(layers),
        layers=layers,
        total_area=num_bars * single_area,
        effective_d=h - total_centroid,
        centroid_from_bottom=total_centroid,
        is_valid=is_valid,
        reason=reason
    )


def auto_design_beam_rebar(
    b: float,
    h: float,
    As_req: float,
    cover: float = 40.0,
    stirrup_size: str = "D10",
    max_aggregate: float = 25.0,
    preferred_sizes: Optional[List[str]] = None
) -> BeamAutoDesignResult:
    """Generate and select the most economical conforming rebar arrangement.
    
    Args:
        b: Beam width (mm)
        h: Beam height (mm)
        As_req: Required tension rebar area (mm2)
        cover: Clear concrete cover (mm)
        stirrup_size: Stirrup rebar grade name
        max_aggregate: Maximum coarse aggregate size (mm)
        preferred_sizes: Rebar sizes to evaluate (default: D16, D19, D22, D25, D29)
    """
    if preferred_sizes is None:
        preferred_sizes = ["D16", "D19", "D22", "D25", "D29"]
        
    stirrup_info = REBAR_DB.get(stirrup_size, REBAR_DB["D10"])
    stirrup_db = stirrup_info["db"]
    stirrup_area = stirrup_info["area"] * 2.0  # 2 legs
    
    candidates: List[BeamRebarArrangement] = []
    
    for bar_size in preferred_sizes:
        bar_info = REBAR_DB.get(bar_size)
        if not bar_info:
            continue
            
        single_area = bar_info["area"]
        # Minimum bars to meet As_req (at least 2 bars for cage integrity)
        n_min = max(int(math.ceil(As_req / single_area)), 2)
        
        # Test candidate counts up to n_min + 2
        for num_bars in range(n_min, n_min + 3):
            arr = create_rebar_arrangement(
                b=b,
                h=h,
                bar_size=bar_size,
                num_bars=num_bars,
                cover=cover,
                stirrup_db=stirrup_db,
                max_aggregate=max_aggregate
            )
            if arr.is_valid and arr.total_area >= As_req:
                candidates.append(arr)
                
    # Sort candidates by area surplus (closest to As_req) and lowest number of layers
    candidates.sort(key=lambda x: (x.total_area - As_req, x.num_layers, x.total_bars))
    
    selected = candidates[0] if len(candidates) > 0 else None
    
    return BeamAutoDesignResult(
        As_req=As_req,
        selected_arrangement=selected,
        all_candidates=candidates,
        stirrup_size=stirrup_size,
        stirrup_spacing=200.0,
        stirrup_legs=2,
        stirrup_area=stirrup_area
    )

"""KDS 41 10 15 Load Combination and Envelope Extraction Engine.

Implements Ultimate Limit State (ULS / USD / LRFD) and Serviceability Limit State (SLS / ASD)
load combinations according to Korean Design Standard KDS 41 10 15 (General Building Loads).
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple, Any
import copy


@dataclass
class MemberForces:
    """Internal cross-section member forces at a specific station."""
    P: float = 0.0          # Axial force (kN, + Tension, - Compression)
    Vx: float = 0.0         # Shear force X (kN)
    Vy: float = 0.0         # Shear force Y (kN)
    Mx: float = 0.0         # Bending moment X (kN*m)
    My: float = 0.0         # Bending moment Y (kN*m)
    T: float = 0.0          # Torsion moment (kN*m)

    def __add__(self, other: "MemberForces") -> "MemberForces":
        return MemberForces(
            P=self.P + other.P,
            Vx=self.Vx + other.Vx,
            Vy=self.Vy + other.Vy,
            Mx=self.Mx + other.Mx,
            My=self.My + other.My,
            T=self.T + other.T
        )

    def __mul__(self, factor: float) -> "MemberForces":
        return MemberForces(
            P=self.P * factor,
            Vx=self.Vx * factor,
            Vy=self.Vy * factor,
            Mx=self.Mx * factor,
            My=self.My * factor,
            T=self.T * factor
        )

    def __rmul__(self, factor: float) -> "MemberForces":
        return self.__mul__(factor)


@dataclass
class LoadCase:
    """Individual load case container (e.g. Dead, Live, Wind, Seismic)."""
    name: str
    case_type: str          # "D", "L", "Lr", "S", "W", "E"
    forces: MemberForces = field(default_factory=MemberForces)


@dataclass
class LoadCombination:
    """A specific load combination with factored scale factors."""
    name: str
    combo_type: str         # "ULS" (USD/LRFD) or "SLS" (ASD)
    factors: Dict[str, float] = field(default_factory=dict)
    factored_forces: MemberForces = field(default_factory=MemberForces)

    def evaluate(self, load_cases: Dict[str, MemberForces]) -> MemberForces:
        """Evaluate factored total forces for this combination."""
        tot = MemberForces()
        for case_name, factor in self.factors.items():
            if case_name in load_cases:
                tot = tot + (factor * load_cases[case_name])
        self.factored_forces = tot
        return tot


@dataclass
class EnvelopeResult:
    """Governing maximum and minimum envelope summary with associated concurrent forces."""
    max_P: Tuple[float, str, MemberForces] = field(default_factory=lambda: (0.0, "", MemberForces()))
    min_P: Tuple[float, str, MemberForces] = field(default_factory=lambda: (0.0, "", MemberForces()))
    max_Vx: Tuple[float, str, MemberForces] = field(default_factory=lambda: (0.0, "", MemberForces()))
    max_Vy: Tuple[float, str, MemberForces] = field(default_factory=lambda: (0.0, "", MemberForces()))
    max_Mx: Tuple[float, str, MemberForces] = field(default_factory=lambda: (0.0, "", MemberForces()))
    min_Mx: Tuple[float, str, MemberForces] = field(default_factory=lambda: (0.0, "", MemberForces()))
    max_My: Tuple[float, str, MemberForces] = field(default_factory=lambda: (0.0, "", MemberForces()))
    min_My: Tuple[float, str, MemberForces] = field(default_factory=lambda: (0.0, "", MemberForces()))
    max_T: Tuple[float, str, MemberForces] = field(default_factory=lambda: (0.0, "", MemberForces()))


class LoadCombinator:
    """KDS 41 10 15 Automated Load Combination and Envelope Solver."""

    def __init__(self):
        self.load_cases: Dict[str, MemberForces] = {}
        self.combinations: List[LoadCombination] = []

    def add_load_case(self, name: str, forces: MemberForces, case_type: str = "D") -> None:
        """Add or update an individual load case."""
        self.load_cases[name] = forces

    def generate_kds41_combinations(
        self,
        d_name: str = "D",
        l_name: str = "L",
        lr_name: Optional[str] = "Lr",
        w_names: Optional[List[str]] = None,
        e_names: Optional[List[str]] = None,
        include_sls: bool = True
    ) -> List[LoadCombination]:
        """Generate standard KDS 41 10 15 Ultimate and Serviceability combinations."""
        combos: List[LoadCombination] = []
        w_list = w_names or ["W"] if "W" in self.load_cases else []
        e_list = e_names or ["E"] if "E" in self.load_cases else []

        # 1. ULS: 1.4D
        combos.append(LoadCombination(
            name="1.4D",
            combo_type="ULS",
            factors={d_name: 1.4}
        ))

        # 2. ULS: 1.2D + 1.6L + 0.5(Lr)
        f2 = {d_name: 1.2, l_name: 1.6}
        if lr_name and lr_name in self.load_cases:
            f2[lr_name] = 0.5
        combos.append(LoadCombination(
            name="1.2D + 1.6L",
            combo_type="ULS",
            factors=f2
        ))

        # 3. ULS: 1.2D + 1.0L ± 1.0W
        for idx, w in enumerate(w_list):
            combos.append(LoadCombination(
                name=f"1.2D + 1.0L + 1.0{w}",
                combo_type="ULS",
                factors={d_name: 1.2, l_name: 1.0, w: 1.0}
            ))
            combos.append(LoadCombination(
                name=f"1.2D + 1.0L - 1.0{w}",
                combo_type="ULS",
                factors={d_name: 1.2, l_name: 1.0, w: -1.0}
            ))

        # 4. ULS: 1.2D + 1.0L ± 1.0E
        for idx, e in enumerate(e_list):
            combos.append(LoadCombination(
                name=f"1.2D + 1.0L + 1.0{e}",
                combo_type="ULS",
                factors={d_name: 1.2, l_name: 1.0, e: 1.0}
            ))
            combos.append(LoadCombination(
                name=f"1.2D + 1.0L - 1.0{e}",
                combo_type="ULS",
                factors={d_name: 1.2, l_name: 1.0, e: -1.0}
            ))

        # 5. ULS: 0.9D ± 1.0W
        for w in w_list:
            combos.append(LoadCombination(
                name=f"0.9D + 1.0{w}",
                combo_type="ULS",
                factors={d_name: 0.9, w: 1.0}
            ))
            combos.append(LoadCombination(
                name=f"0.9D - 1.0{w}",
                combo_type="ULS",
                factors={d_name: 0.9, w: -1.0}
            ))

        # 6. ULS: 0.9D ± 1.0E
        for e in e_list:
            combos.append(LoadCombination(
                name=f"0.9D + 1.0{e}",
                combo_type="ULS",
                factors={d_name: 0.9, e: 1.0}
            ))
            combos.append(LoadCombination(
                name=f"0.9D - 1.0{e}",
                combo_type="ULS",
                factors={d_name: 0.9, e: -1.0}
            ))

        # SLS (ASD) Combinations
        if include_sls:
            combos.append(LoadCombination(
                name="D + L (SLS)",
                combo_type="SLS",
                factors={d_name: 1.0, l_name: 1.0}
            ))
            for w in w_list:
                combos.append(LoadCombination(
                    name=f"D + 0.75L + 0.45{w} (SLS)",
                    combo_type="SLS",
                    factors={d_name: 1.0, l_name: 0.75, w: 0.45}
                ))
            for e in e_list:
                combos.append(LoadCombination(
                    name=f"D + 0.7{e} (SLS)",
                    combo_type="SLS",
                    factors={d_name: 1.0, e: 0.7}
                ))

        self.combinations = combos
        return combos

    def evaluate_all(self) -> List[Tuple[LoadCombination, MemberForces]]:
        """Evaluate all registered combinations against current load cases."""
        results = []
        for combo in self.combinations:
            forces = combo.evaluate(self.load_cases)
            results.append((combo, forces))
        return results

    def extract_envelope(self, combo_type: Optional[str] = "ULS") -> EnvelopeResult:
        """Extract governing envelope and concurrent member forces."""
        evals = self.evaluate_all()
        filtered = [item for item in evals if (combo_type is None or item[0].combo_type == combo_type)]
        
        if not filtered:
            return EnvelopeResult()

        first_combo, first_force = filtered[0]
        max_p = (first_force.P, first_combo.name, first_force)
        min_p = (first_force.P, first_combo.name, first_force)
        max_vx = (abs(first_force.Vx), first_combo.name, first_force)
        max_vy = (abs(first_force.Vy), first_combo.name, first_force)
        max_mx = (first_force.Mx, first_combo.name, first_force)
        min_mx = (first_force.Mx, first_combo.name, first_force)
        max_my = (first_force.My, first_combo.name, first_force)
        min_my = (first_force.My, first_combo.name, first_force)
        max_t = (abs(first_force.T), first_combo.name, first_force)

        for combo, f in filtered:
            if f.P > max_p[0]:
                max_p = (f.P, combo.name, f)
            if f.P < min_p[0]:
                min_p = (f.P, combo.name, f)

            if abs(f.Vx) > max_vx[0]:
                max_vx = (abs(f.Vx), combo.name, f)
            if abs(f.Vy) > max_vy[0]:
                max_vy = (abs(f.Vy), combo.name, f)

            if f.Mx > max_mx[0]:
                max_mx = (f.Mx, combo.name, f)
            if f.Mx < min_mx[0]:
                min_mx = (f.Mx, combo.name, f)

            if f.My > max_my[0]:
                max_my = (f.My, combo.name, f)
            if f.My < min_my[0]:
                min_my = (f.My, combo.name, f)

            if abs(f.T) > max_t[0]:
                max_t = (abs(f.T), combo.name, f)

        return EnvelopeResult(
            max_P=max_p,
            min_P=min_p,
            max_Vx=max_vx,
            max_Vy=max_vy,
            max_Mx=max_mx,
            min_Mx=min_mx,
            max_My=max_my,
            min_My=min_my,
            max_T=max_t
        )

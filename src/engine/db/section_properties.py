"""Section Geometric and Plastic Properties Calculation Engine.

Implements structural section mechanics based on KDS 14 31 10, AISC 360,
and Midas CSteelSectDB algorithms for:
- H-Section (I-Beam / Wide Flange)
- Box / Rectangular Hollow Section (RHS / SHS)
- Pipe / Circular Hollow Section (CHS)
- Channel (C-Section)
- Angle (L-Section)
- Tee (T-Section)
- Flat Bar / Plate
- Round Bar / Solid Rod
"""

import math
from dataclasses import dataclass, field
from typing import Dict, Any, Optional


@dataclass
class CalculatedSectionProperties:
    """Computed section properties output container."""
    name: str = ""
    category: str = "H-Section"
    
    # Dimensions (mm)
    H: float = 0.0          # Total height / Outer diameter
    B: float = 0.0          # Total width
    tw: float = 0.0         # Web thickness
    tf: float = 0.0         # Flange thickness
    r: float = 0.0          # Fillet / Corner radius
    
    # Cross-Sectional Area
    A: float = 0.0          # Area (cm2)
    
    # Moments of Inertia (cm4)
    Ix: float = 0.0         # Major axis (X)
    Iy: float = 0.0         # Minor axis (Y)
    
    # Elastic Section Modulus (cm3)
    Sx: float = 0.0         # Major axis (X)
    Sy: float = 0.0         # Minor axis (Y)
    
    # Plastic Section Modulus (cm3)
    Zx: float = 0.0         # Major axis (X)
    Zy: float = 0.0         # Minor axis (Y)
    
    # Radius of Gyration (cm)
    rx: float = 0.0         # Major axis (X)
    ry: float = 0.0         # Minor axis (Y)
    
    # Torsional & Warping Properties
    J: float = 0.0          # Saint-Venant Torsion constant (cm4)
    Cw: float = 0.0         # Warping constant (cm6)
    
    # Centroid & Shear Center Offsets (mm)
    xc: float = 0.0         # Centroid X from reference
    yc: float = 0.0         # Centroid Y from reference
    xs: float = 0.0         # Shear center X from centroid
    ys: float = 0.0         # Shear center Y from centroid
    
    # Principal Axis Angle (degrees)
    theta: float = 0.0      # Principal axis angle
    
    # Unit Weight (kg/m)
    weight: float = 0.0


class SectionPropertiesCalculator:
    """High-precision calculator for structural steel cross-section properties."""

    @staticmethod
    def calc_h_section(
        H: float,
        B: float,
        tw: float,
        tf: float,
        r: float = 0.0,
        name: str = "H-Section"
    ) -> CalculatedSectionProperties:
        """Calculate properties for H-Section (I-Beam / Wide Flange).
        
        Dimensions in mm. Output properties in engineering standard units (cm, cm2, cm3, cm4, cm6).
        """
        # Fillet area contribution: (4 - pi) * r^2
        fillet_area_mm2 = (4.0 - math.pi) * (r ** 2) if r > 0 else 0.0
        
        # Web clear height
        hw = H - 2.0 * tf
        if hw < 0:
            hw = 0.0

        # Area (mm2 -> cm2)
        area_mm2 = 2.0 * B * tf + hw * tw + fillet_area_mm2
        A_cm2 = area_mm2 / 100.0

        # Moment of Inertia Ix (Major) (mm4 -> cm4)
        # Ix = (B*H^3 - (B-tw)*hw^3)/12 + fillet correction
        ix_base_mm4 = (B * (H ** 3) - (B - tw) * (hw ** 3)) / 12.0
        # Fillet inertia adjustment: 2 * (1 - 5*pi/16) * r^4 + 4 * (1 - pi/4)*r^2 * (hw/2 + (1 - 2/(3*(4-pi)))*r)^2
        fillet_ix_mm4 = 0.0
        if r > 0:
            c = (1.0 - 2.0 / (3.0 * (4.0 - math.pi))) * r
            d = hw / 2.0 + c
            fillet_ix_mm4 = 4.0 * (1.0 - math.pi / 4.0) * (r ** 2) * (d ** 2)
        
        Ix_mm4 = ix_base_mm4 + fillet_ix_mm4
        Ix_cm4 = Ix_mm4 / 10000.0

        # Moment of Inertia Iy (Minor) (mm4 -> cm4)
        iy_base_mm4 = (2.0 * tf * (B ** 3) + hw * (tw ** 3)) / 12.0
        fillet_iy_mm4 = 0.0
        if r > 0:
            c = (1.0 - 2.0 / (3.0 * (4.0 - math.pi))) * r
            d = tw / 2.0 + c
            fillet_iy_mm4 = 4.0 * (1.0 - math.pi / 4.0) * (r ** 2) * (d ** 2)

        Iy_mm4 = iy_base_mm4 + fillet_iy_mm4
        Iy_cm4 = Iy_mm4 / 10000.0

        # Elastic Section Modulus (cm3)
        Sx_cm3 = (Ix_mm4 / (H / 2.0)) / 1000.0 if H > 0 else 0.0
        Sy_cm3 = (Iy_mm4 / (B / 2.0)) / 1000.0 if B > 0 else 0.0

        # Plastic Section Modulus (cm3)
        # Zx = B*tf*(H - tf) + tw*hw^2 / 4
        zx_mm3 = B * tf * (H - tf) + 0.25 * tw * (hw ** 2)
        # Zy = tf*B^2 / 2 + hw*tw^2 / 4
        zy_mm3 = 0.5 * tf * (B ** 2) + 0.25 * hw * (tw ** 2)
        Zx_cm3 = zx_mm3 / 1000.0
        Zy_cm3 = zy_mm3 / 1000.0

        # Radius of Gyration (cm)
        rx_cm = math.sqrt(Ix_cm4 / A_cm2) if A_cm2 > 0 else 0.0
        ry_cm = math.sqrt(Iy_cm4 / A_cm2) if A_cm2 > 0 else 0.0

        # Torsion Constant J (cm4)
        # Saint-Venant approximation: (2*B*tf^3 + hw*tw^3)/3 + alpha*D^4 (fillet junction)
        # AISC/Midas formula
        alpha_d = -0.042 + 0.2204 * (tw / tf) + 0.1355 * (r / tf) - 0.0865 * (tw * r / (tf ** 2))
        d_val = ((tf + r) ** 2 + tw * (r + tw / 4.0)) / (2.0 * r + tf) if (2.0 * r + tf) > 0 else tf
        j_fillet = 2.0 * alpha_d * (d_val ** 4) if r > 0 else 0.0
        j_mm4 = (2.0 * B * (tf ** 3) + hw * (tw ** 3)) / 3.0 + j_fillet
        J_cm4 = max(0.0, j_mm4 / 10000.0)

        # Warping Constant Cw (cm6)
        # Cw = Iy * (H - tf)^2 / 4 (mm6 -> cm6: / 1,000,000)
        cw_mm6 = (Iy_mm4 * ((H - tf) ** 2)) / 4.0
        Cw_cm6 = cw_mm6 / 1_000_000.0

        # Unit Weight (kg/m) = A (cm2) * 0.785
        weight = A_cm2 * 0.785

        return CalculatedSectionProperties(
            name=name,
            category="H-Section",
            H=H, B=B, tw=tw, tf=tf, r=r,
            A=round(A_cm2, 2),
            Ix=round(Ix_cm4, 2),
            Iy=round(Iy_cm4, 2),
            Sx=round(Sx_cm3, 2),
            Sy=round(Sy_cm3, 2),
            Zx=round(Zx_cm3, 2),
            Zy=round(Zy_cm3, 2),
            rx=round(rx_cm, 2),
            ry=round(ry_cm, 2),
            J=round(J_cm4, 2),
            Cw=round(Cw_cm6, 2),
            xc=round(B / 2.0, 2),
            yc=round(H / 2.0, 2),
            weight=round(weight, 2)
        )

    @staticmethod
    def calc_box_section(
        H: float,
        B: float,
        t: float,
        r_out: float = 0.0,
        name: str = "Box"
    ) -> CalculatedSectionProperties:
        """Calculate properties for Rectangular Hollow Section (Box/RHS/SHS)."""
        tw = tf = t
        hi = H - 2.0 * t
        bi = B - 2.0 * t
        if hi < 0 or bi < 0:
            raise ValueError("Box thickness exceeds outer dimensions")

        # Corner radius approximation
        area_mm2 = H * B - hi * bi
        if r_out > 0:
            corner_cut = (4.0 - math.pi) * (r_out ** 2)
            r_in = max(0.0, r_out - t)
            corner_in = (4.0 - math.pi) * (r_in ** 2)
            area_mm2 -= (corner_cut - corner_in)
            
        A_cm2 = area_mm2 / 100.0

        # Inertia Ix, Iy
        ix_mm4 = (B * (H ** 3) - bi * (hi ** 3)) / 12.0
        iy_mm4 = (H * (B ** 3) - hi * (bi ** 3)) / 12.0
        Ix_cm4 = ix_mm4 / 10000.0
        Iy_cm4 = iy_mm4 / 10000.0

        # Elastic Modulus
        Sx_cm3 = (ix_mm4 / (H / 2.0)) / 1000.0
        Sy_cm3 = (iy_mm4 / (B / 2.0)) / 1000.0

        # Plastic Modulus
        # Z = B*H^2 / 4 - bi*hi^2 / 4
        zx_mm3 = (B * (H ** 2) - bi * (hi ** 2)) / 4.0
        zy_mm3 = (H * (B ** 2) - hi * (bi ** 2)) / 4.0
        Zx_cm3 = zx_mm3 / 1000.0
        Zy_cm3 = zy_mm3 / 1000.0

        # Radius of gyration
        rx_cm = math.sqrt(Ix_cm4 / A_cm2) if A_cm2 > 0 else 0.0
        ry_cm = math.sqrt(Iy_cm4 / A_cm2) if A_cm2 > 0 else 0.0

        # Torsion Constant J for closed thin-walled box: 4*Am^2 /oint(ds/t)
        # Bredt-Batho formula: Am = (H - t) * (B - t)
        am = (H - t) * (B - t)
        perimeter = 2.0 * (H - t) + 2.0 * (B - t)
        j_mm4 = (4.0 * (am ** 2) * t) / perimeter if perimeter > 0 else 0.0
        J_cm4 = j_mm4 / 10000.0
        Cw_cm6 = 0.0  # Negligible for closed box

        return CalculatedSectionProperties(
            name=name,
            category="Box",
            H=H, B=B, tw=t, tf=t, r=r_out,
            A=round(A_cm2, 2),
            Ix=round(Ix_cm4, 2),
            Iy=round(Iy_cm4, 2),
            Sx=round(Sx_cm3, 2),
            Sy=round(Sy_cm3, 2),
            Zx=round(Zx_cm3, 2),
            Zy=round(Zy_cm3, 2),
            rx=round(rx_cm, 2),
            ry=round(ry_cm, 2),
            J=round(J_cm4, 2),
            Cw=round(Cw_cm6, 2),
            xc=round(B / 2.0, 2),
            yc=round(H / 2.0, 2),
            weight=round(A_cm2 * 0.785, 2)
        )

    @staticmethod
    def calc_pipe_section(
        D: float,
        t: float,
        name: str = "Pipe"
    ) -> CalculatedSectionProperties:
        """Calculate properties for Circular Hollow Section (Pipe/CHS)."""
        di = D - 2.0 * t
        if di < 0:
            raise ValueError("Pipe thickness exceeds radius")

        area_mm2 = math.pi * (D ** 2 - di ** 2) / 4.0
        A_cm2 = area_mm2 / 100.0

        ix_mm4 = math.pi * (D ** 4 - di ** 4) / 64.0
        iy_mm4 = ix_mm4
        Ix_cm4 = ix_mm4 / 10000.0
        Iy_cm4 = Iy_cm4 = Ix_cm4

        Sx_cm3 = (ix_mm4 / (D / 2.0)) / 1000.0
        Sy_cm3 = Sx_cm3

        # Plastic modulus for thin cylinder: Z = (D^3 - di^3)/6
        zx_mm3 = (D ** 3 - di ** 3) / 6.0
        Zx_cm3 = zx_mm3 / 1000.0
        Zy_cm3 = Zx_cm3

        r_cm = math.sqrt(Ix_cm4 / A_cm2) if A_cm2 > 0 else 0.0
        J_cm4 = 2.0 * Ix_cm4
        Cw_cm6 = 0.0

        return CalculatedSectionProperties(
            name=name,
            category="Pipe",
            H=D, B=D, tw=t, tf=t,
            A=round(A_cm2, 2),
            Ix=round(Ix_cm4, 2),
            Iy=round(Iy_cm4, 2),
            Sx=round(Sx_cm3, 2),
            Sy=round(Sy_cm3, 2),
            Zx=round(Zx_cm3, 2),
            Zy=round(Zy_cm3, 2),
            rx=round(r_cm, 2),
            ry=round(r_cm, 2),
            J=round(J_cm4, 2),
            Cw=0.0,
            xc=round(D / 2.0, 2),
            yc=round(D / 2.0, 2),
            weight=round(A_cm2 * 0.785, 2)
        )

    @staticmethod
    def calc_channel_section(
        H: float,
        B: float,
        tw: float,
        tf: float,
        name: str = "Channel"
    ) -> CalculatedSectionProperties:
        """Calculate properties for C-Channel Section."""
        hw = H - 2.0 * tf
        area_mm2 = 2.0 * B * tf + hw * tw
        A_cm2 = area_mm2 / 100.0

        # Centroid xc (from back of web)
        # Sum(A * x) / A
        q_web = (hw * tw) * (tw / 2.0)
        q_flange = 2.0 * (B * tf) * (B / 2.0)
        xc_mm = (q_web + q_flange) / area_mm2 if area_mm2 > 0 else 0.0

        # Moment of Inertia Ix (symmetric)
        ix_mm4 = (B * (H ** 3) - (B - tw) * (hw ** 3)) / 12.0
        Ix_cm4 = ix_mm4 / 10000.0

        # Moment of Inertia Iy (parallel axis theorem)
        iy_web = (hw * (tw ** 3)) / 12.0 + (hw * tw) * ((xc_mm - tw / 2.0) ** 2)
        iy_flange = 2.0 * ((tf * (B ** 3)) / 12.0 + (B * tf) * ((B / 2.0 - xc_mm) ** 2))
        iy_mm4 = iy_web + iy_flange
        Iy_cm4 = iy_mm4 / 10000.0

        Sx_cm3 = (ix_mm4 / (H / 2.0)) / 1000.0
        Sy_cm3 = (iy_mm4 / max(xc_mm, B - xc_mm)) / 1000.0

        # Plastic modulus
        zx_mm3 = B * tf * (H - tf) + 0.25 * tw * (hw ** 2)
        Zx_cm3 = zx_mm3 / 1000.0
        # Plastic neutral axis Y
        Zy_cm3 = (2.0 * tf * (B ** 2) + hw * (tw ** 2)) / 4.0 / 1000.0

        rx_cm = math.sqrt(Ix_cm4 / A_cm2) if A_cm2 > 0 else 0.0
        ry_cm = math.sqrt(Iy_cm4 / A_cm2) if A_cm2 > 0 else 0.0

        # Torsion constant J (open profile)
        j_mm4 = (2.0 * B * (tf ** 3) + hw * (tw ** 3)) / 3.0
        J_cm4 = j_mm4 / 10000.0

        # Shear center offset xs = 3*b^2 / (6*b + h) (approx)
        b_prime = B - tw / 2.0
        h_prime = H - tf
        xs_mm = (3.0 * (b_prime ** 2)) / (6.0 * b_prime + h_prime)
        
        # Warping constant Cw
        cw_mm6 = ((h_prime ** 2) * (b_prime ** 3) * tf / 12.0) * ((2.0 * h_prime + 3.0 * b_prime) / (h_prime + 6.0 * b_prime))
        Cw_cm6 = cw_mm6 / 1_000_000.0

        return CalculatedSectionProperties(
            name=name,
            category="Channel",
            H=H, B=B, tw=tw, tf=tf,
            A=round(A_cm2, 2),
            Ix=round(Ix_cm4, 2),
            Iy=round(Iy_cm4, 2),
            Sx=round(Sx_cm3, 2),
            Sy=round(Sy_cm3, 2),
            Zx=round(Zx_cm3, 2),
            Zy=round(Zy_cm3, 2),
            rx=round(rx_cm, 2),
            ry=round(ry_cm, 2),
            J=round(J_cm4, 2),
            Cw=round(Cw_cm6, 2),
            xc=round(xc_mm, 2),
            yc=round(H / 2.0, 2),
            xs=round(xs_mm, 2),
            weight=round(A_cm2 * 0.785, 2)
        )

    @staticmethod
    def calc_angle_section(
        H: float,
        B: float,
        t: float,
        name: str = "Angle"
    ) -> CalculatedSectionProperties:
        """Calculate properties for L-Angle Section."""
        area_mm2 = t * (H + B - t)
        A_cm2 = area_mm2 / 100.0

        # Centroid
        xc_mm = (B * t * (B / 2.0) + (H - t) * t * (t / 2.0)) / area_mm2
        yc_mm = (H * t * (H / 2.0) + (B - t) * t * (t / 2.0)) / area_mm2

        # Ix, Iy
        ix_mm4 = (t * (H ** 3)) / 12.0 + (H * t) * ((H / 2.0 - yc_mm) ** 2) + ((B - t) * (t ** 3)) / 12.0 + ((B - t) * t) * ((yc_mm - t / 2.0) ** 2)
        iy_mm4 = (t * (B ** 3)) / 12.0 + (B * t) * ((B / 2.0 - xc_mm) ** 2) + ((H - t) * (t ** 3)) / 12.0 + ((H - t) * t) * ((xc_mm - t / 2.0) ** 2)

        # Product of inertia Ixy
        ixy_mm4 = (H * t) * (t / 2.0 - xc_mm) * (H / 2.0 - yc_mm) + ((B - t) * t) * ((B + t) / 2.0 - xc_mm) * (t / 2.0 - yc_mm)

        Ix_cm4 = ix_mm4 / 10000.0
        Iy_cm4 = iy_mm4 / 10000.0

        Sx_cm3 = (ix_mm4 / max(yc_mm, H - yc_mm)) / 1000.0
        Sy_cm3 = (iy_mm4 / max(xc_mm, B - xc_mm)) / 1000.0

        rx_cm = math.sqrt(Ix_cm4 / A_cm2) if A_cm2 > 0 else 0.0
        ry_cm = math.sqrt(Iy_cm4 / A_cm2) if A_cm2 > 0 else 0.0

        # Principal angle theta
        theta_rad = 0.5 * math.atan2(2.0 * ixy_mm4, (iy_mm4 - ix_mm4))
        theta_deg = math.degrees(theta_rad)

        # Torsion J = sum(b*t^3)/3
        j_mm4 = (H + B - t) * (t ** 3) / 3.0
        J_cm4 = j_mm4 / 10000.0

        return CalculatedSectionProperties(
            name=name,
            category="Angle",
            H=H, B=B, tw=t, tf=t,
            A=round(A_cm2, 2),
            Ix=round(Ix_cm4, 2),
            Iy=round(Iy_cm4, 2),
            Sx=round(Sx_cm3, 2),
            Sy=round(Sy_cm3, 2),
            Zx=round(Sx_cm3 * 1.5, 2),
            Zy=round(Sy_cm3 * 1.5, 2),
            rx=round(rx_cm, 2),
            ry=round(ry_cm, 2),
            J=round(J_cm4, 2),
            Cw=0.0,
            xc=round(xc_mm, 2),
            yc=round(yc_mm, 2),
            theta=round(theta_deg, 2),
            weight=round(A_cm2 * 0.785, 2)
        )

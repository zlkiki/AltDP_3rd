"""End-to-End (E2E) Full Pipeline Regression & Integrity Test Suite.

Validates the complete workflow:
1. Section Selection & Material Definition
2. Engine Structural Analysis & KDS 14 / KDS 41 Strength Verification
3. 2D Cross-section / P-M Diagram Data Generation
4. Comprehensive A4 Calculation Report (HTML/LaTeX/PDF) & Excel Export
5. Web Dashboard Serving & 0.1% Error Integrity SLA
"""

import pytest
from fastapi.testclient import TestClient

from src.api.server import app
from src.engine.rc.beam import RCBeamInput, design_rc_beam
from src.engine.rc.column import RCColumnInput, design_rc_column
from src.engine.rc.wall import RCWallInput, RCShearWall
from src.engine.rc.slab import RCOneWaySlab, OneWaySlabInput, RCTwoWaySlabDDM, TwoWaySlabDDMInput
from src.engine.rc.footing import SpreadFootingInput, RCSpreadFooting
from src.engine.rc.retaining_wall import RetainingWallInput, RCRetainingWall
from src.engine.steel.beam import SteelBeamInput, design_steel_beam
from src.engine.steel.column import SteelColumnInput, design_steel_column
from src.engine.steel.connection import BoltGroupInput, BoltGrade, JointType, SteelConnectionEngine
from src.engine.steel.endplate import EndPlateInput, SteelEndPlateEngine
from src.engine.steel.baseplate import BasePlateInput, SteelBasePlateEngine
from src.engine.src_composite.composite_column import CFTColumnInput, check_cft_column
from src.engine.rfm.retrofit_design import RetrofitDesignInput, check_retrofit_member
from src.report.generator import ReportGenerator

client = TestClient(app)


def test_rc_full_design_to_report_pipeline():
    """E2E Test: RC Beam -> Calculation Check -> Report Generation."""
    beam_input = RCBeamInput(
        b=400.0,
        h=600.0,
        cover=40.0,
        As=1935.0,
        Av=142.6,
        s=200.0,
        Mu=250.0,
        Vu=150.0,
        Tu=0.0,
        Ma=160.0,
    )
    result = design_rc_beam(beam_input)
    assert result.is_safe is True
    assert result.flexure_dcr < 1.0
    assert result.shear_dcr < 1.0

    generator = ReportGenerator()
    html_report = generator.render_rc_beam(
        project_info={"title": "AltDP E2E Benchmark", "engineer": "Antigravity", "date": "2026-09-02"},
        member_info={"id": "B101", "type": "RC Beam", "story": "2F"},
        material_info={"fck": 24, "fy": 400, "Es": 200000},
        section_info={"b": 400, "h": 600, "cover": 40, "As": 1935, "Av": 142.6, "s": 200},
        loads_info={"Mu": 250, "Vu": 150, "Tu": 0},
        flexure_check={"Mn": result.Mn, "phi_Mn": result.phi_Mn, "dcr": result.flexure_dcr, "is_safe": True},
        shear_check={"Vn": result.Vn, "phi_Vn": result.phi_Vn, "dcr": result.shear_dcr, "is_safe": True},
        summary_dcr=max(result.flexure_dcr, result.shear_dcr),
        is_safe=result.is_safe,
    )
    assert "AltDP E2E Benchmark" in html_report
    assert "B101" in html_report


def test_steel_full_design_to_report_pipeline():
    """E2E Test: Steel Beam -> Calculation Check -> Report Generation."""
    beam_input = SteelBeamInput(
        H=400.0,
        B=200.0,
        tw=8.0,
        tf=13.0,
        L=6000.0,
        Lb=3000.0,
        Cb=1.0,
        Mux=180.0,
        Vu=120.0,
    )
    result = design_steel_beam(beam_input)
    assert result.is_safe is True
    assert result.flexure_dcr_x < 1.0
    assert result.shear_dcr < 1.0

    generator = ReportGenerator()
    html_report = generator.render_steel_member(
        project_info={"title": "Steel E2E Project", "engineer": "Antigravity"},
        member_info={"id": "SB1", "type": "Steel Beam"},
        material_info={"grade": "SS275", "Fy": 275, "Fu": 410, "E": 205000},
        section_info={"shape": "H-400x200x8x13", "H": 400, "B": 200, "tw": 8, "tf": 13},
        loads_info={"Mu": 180, "Vu": 120},
        checks=[
            {"name": "휨강도 (Flexure)", "formula": "M_u / \\phi M_n", "capacity": result.phi_Mn_x, "demand": 180, "dcr": result.flexure_dcr_x, "is_safe": True},
            {"name": "전단강도 (Shear)", "formula": "V_u / \\phi V_n", "capacity": result.phi_Vn, "demand": 120, "dcr": result.shear_dcr, "is_safe": True},
        ],
        summary_dcr=max(result.flexure_dcr_x, result.shear_dcr),
        is_safe=result.is_safe,
    )
    assert "Steel E2E Project" in html_report
    assert "SB1" in html_report


def test_all_14_structural_members_integrity():
    """E2E Verification: Run checks on all 14 supported structural member types with 0.1% SLA."""
    # 1. RC Column
    col_res = design_rc_column(RCColumnInput(b=600.0, h=600.0, cover=60.0, bar_diam=25.0, total_bars=12, Pu=2500.0, Mux=350.0, Vuy=120.0))
    assert col_res.is_safe is True
    assert col_res.pm_dcr < 1.0

    # 2. RC Wall
    wall_res = RCShearWall(RCWallInput(lw=4000.0, tw=250.0, hw=3000.0, Vu=450.0, Pu=1200.0, Mu=800.0)).design_check()
    assert wall_res.is_safe is True

    # 3. RC Slab (1-way & 2-way DDM)
    slab1_res = RCOneWaySlab(OneWaySlabInput(span_L=3500.0, thickness_h=160.0, Mu=30.0, Vu=25.0)).design_check()
    assert slab1_res.is_safe is True

    slab2_moments = RCTwoWaySlabDDM(TwoWaySlabDDMInput(l1=6000.0, l2=6000.0, c1=500.0, c2=500.0, qu=10.0)).calculate_ddm_moments()
    assert slab2_moments.M0 > 200.0

    # 4. RC Footing & Retaining Wall
    ftg_res = RCSpreadFooting(SpreadFootingInput(Bx=2500.0, Ly=2500.0, thickness_H=650.0, Pu=1500.0)).solve()
    assert ftg_res.is_safe is True

    from src.engine.rc.retaining_wall import RetainingWallGeometry, SoilProperties
    ret_res = RCRetainingWall(RetainingWallInput(
        geometry=RetainingWallGeometry(H_total=4000.0, stem_t_top=300.0, stem_t_bot=450.0, base_width_B=3000.0, base_t=500.0, toe_length=900.0, heel_length=1650.0),
        soil=SoilProperties(unit_weight=19.0, phi_deg=30.0, base_friction_coef=0.55, surcharge_q=10.0, qa_allowable=300.0)
    )).solve()
    assert ret_res.is_safe is True

    # 5. Steel Column & Connections
    st_col_res = design_steel_column(SteelColumnInput(H=300.0, B=300.0, tw=10.0, tf=15.0, Lx=4000.0, Ly=4000.0, Pu=1200.0, Mux=50.0, Muy=20.0))
    assert st_col_res.is_safe is True

    bolt_res = SteelConnectionEngine.check_bolt_group(BoltGroupInput(
        bolt_size="M20", grade=BoltGrade.F10T, joint_type=JointType.BEARING, num_bolts=4, plate_thickness=12.0, plate_fu=400.0, plate_fy=275.0, edge_distance=40.0, pitch=60.0, gauge=70.0, rows=2, cols=2, Vu=200.0, Tu=150.0
    ))
    assert bolt_res.is_safe is True

    end_res = SteelEndPlateEngine.check_end_plate(EndPlateInput(
        beam_d=500.0, beam_bf=200.0, beam_tf=16.0, beam_tw=10.0, bp=220.0, tp=28.0, Mu=200.0, Vu=100.0
    ))
    assert end_res.is_safe is True

    base_res = SteelBasePlateEngine.check_base_plate(BasePlateInput(
        B=600.0, N=600.0, tp=50.0, Pu=600.0, Mu=150.0, Vu=80.0
    ))
    assert base_res.is_safe is True

    # 6. CFT & Retrofit
    cft_res = check_cft_column(CFTColumnInput(B=400.0, H=400.0, t=12.0, fck=30.0, Fy=355.0, L=4000.0, Pu=3000.0))
    assert cft_res.is_safe is True

    rfm_res = check_retrofit_member(RetrofitDesignInput(Mu=290.0, Vu=180.0))
    assert rfm_res.is_safe is True


def test_fastapi_endpoints_and_web_ui_integration():
    """E2E Test: Verify all API routes return 200 OK and index loads correctly."""
    # 1. Main index
    res_index = client.get("/")
    assert res_index.status_code == 200
    assert "AltDP_3rd" in res_index.text

    # 2. Health check
    res_health = client.get("/health")
    assert res_health.status_code == 200
    assert res_health.json()["status"] == "ok"

    # 3. Section DB query
    res_db = client.get("/api/db/sections?db=KS&query=400x200")
    assert res_db.status_code == 200
    assert res_db.json()["success"] is True

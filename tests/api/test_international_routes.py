"""Tests for International Design Codes and Unit Converter REST API Endpoints."""

import pytest
from fastapi.testclient import TestClient
from src.api.server import app

client = TestClient(app)


class TestInternationalApiRoutes:
    """Test /api/v1/intl endpoints."""

    def test_convert_units_batch_endpoint(self):
        payload = {
            "values": {
                "depth": 500.0,
                "span": 6.0,
                "moment": 200.0,
            },
            "unit_types": {
                "depth": "LENGTH",
                "span": "SPAN_LENGTH",
                "moment": "MOMENT",
            },
            "from_system": "SI",
            "to_system": "US_IMPERIAL",
        }
        res = client.post("/api/v1/intl/convert-units", json=payload)
        assert res.status_code == 200
        data = res.json()
        assert data["status"] == "success"
        converted = data["converted_values"]
        # 500 mm in inches
        assert converted["depth"] == pytest.approx(500.0 / 25.4, rel=1e-5)
        # 6 m in feet
        assert converted["span"] == pytest.approx(6.0 / 0.3048, rel=1e-5)

    def test_convert_single_scalar_endpoint(self):
        payload = {
            "value": 25.0,
            "unit_type": "STRESS",
            "from_system": "SI",
            "to_system": "US_IMPERIAL",
        }
        res = client.post("/api/v1/intl/convert-single", json=payload)
        assert res.status_code == 200
        data = res.json()
        assert data["converted_value"] == pytest.approx(25.0 / 6.894757, rel=1e-3)

    def test_design_check_eurocode(self):
        payload_ec2 = {
            "code": "EUROCODE",
            "member_type": "RC_BEAM",
            "parameters": {
                "b": 300.0,
                "h": 600.0,
                "d": 540.0,
                "fck": 30.0,
                "fyk": 500.0,
                "As": 1500.0,
                "Mu": 200.0,
                "Vu": 100.0,
            },
        }
        res = client.post("/api/v1/intl/design-check", json=payload_ec2)
        assert res.status_code == 200
        data = res.json()
        assert data["code"] == "EUROCODE_2"
        assert data["result"]["M_Rd"] > 200.0
        assert data["is_safe"] is True

        payload_ec3 = {
            "code": "EUROCODE",
            "member_type": "STEEL_BEAM",
            "parameters": {
                "h": 400.0,
                "b": 200.0,
                "tw": 8.0,
                "tf": 13.0,
                "r": 16.0,
                "A": 8410.0,
                "Wpl_y": 1307e3,
                "Wel_y": 1156e3,
                "Iz": 1740e4,
                "It": 39.5e4,
                "Iw": 64.8e10,
                "fy": 275.0,
                "Mu": 150.0,
                "Vu": 80.0,
            },
        }
        res_ec3 = client.post("/api/v1/intl/design-check", json=payload_ec3)
        assert res_ec3.status_code == 200
        data_ec3 = res_ec3.json()
        assert data_ec3["code"] == "EUROCODE_3"
        assert data_ec3["result"]["M_b_Rd"] > 0.0

    def test_design_check_us_standards(self):
        payload_aci = {
            "code": "ACI",
            "member_type": "RC_BEAM",
            "parameters": {
                "b": 300.0,
                "h": 600.0,
                "d": 540.0,
                "fc_prime": 28.0,
                "fy": 420.0,
                "As": 1500.0,
                "Mu": 200.0,
                "Vu": 80.0,
            },
        }
        res_aci = client.post("/api/v1/intl/design-check", json=payload_aci)
        assert res_aci.status_code == 200
        assert res_aci.json()["code"] == "ACI_318_19"

        payload_aisc = {
            "code": "AISC",
            "member_type": "STEEL_BEAM",
            "parameters": {
                "d": 400.0,
                "bf": 200.0,
                "tf": 13.0,
                "tw": 8.0,
                "Ag": 8410.0,
                "Zx": 1307e3,
                "Sx": 1156e3,
                "ry": 45.0,
                "J": 39.5e4,
                "Cw": 64.8e10,
                "Fy": 345.0,
                "Mu": 200.0,
                "Vu": 100.0,
            },
        }
        res_aisc = client.post("/api/v1/intl/design-check", json=payload_aisc)
        assert res_aisc.status_code == 200
        assert res_aisc.json()["code"] == "AISC_360_16"

    def test_design_check_indian_standards(self):
        payload_is = {
            "code": "IS",
            "member_type": "RC_BEAM",
            "parameters": {
                "b": 250.0,
                "h": 500.0,
                "d": 450.0,
                "fck": 25.0,
                "fy": 415.0,
                "Ast": 1200.0,
                "Mu": 120.0,
                "Vu": 60.0,
            },
        }
        res_is = client.post("/api/v1/intl/design-check", json=payload_is)
        assert res_is.status_code == 200
        assert res_is.json()["code"] == "IS_456_2000"

    def test_pbd_hinge_evaluate_endpoint(self):
        payload_rc = {
            "member_id": 1,
            "member_type": "RC_BEAM",
            "parameters": {
                "b": 400.0,
                "h": 600.0,
                "d": 540.0,
                "fck": 27.0,
                "fy": 400.0,
                "As": 1800.0,
                "As_prime": 400.0,
                "span_len": 6000.0,
                "V_design": 80.0,
            },
            "demand_theta": 0.015,
        }
        res_rc = client.post("/api/v1/intl/pbd/hinge-evaluate", json=payload_rc)
        assert res_rc.status_code == 200
        data_rc = res_rc.json()
        assert data_rc["member_type"] == "RC_BEAM"
        assert len(data_rc["backbone_curve"]) == 9
        assert data_rc["performance_level"] in ("IO", "LS", "CP")

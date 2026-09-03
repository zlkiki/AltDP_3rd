"""API Integration tests for MIDAS Gen Interoperability Routes (Phase 16-3)."""

from fastapi.testclient import TestClient
from src.api.server import app

client = TestClient(app)

SAMPLE_MGT_TEXT = """
*NODE
1, 0.0, 0.0, 0.0
2, 6.0, 0.0, 0.0
3, 0.0, 0.0, 3.5
4, 6.0, 0.0, 3.5
*MATERIAL
1, CONC, C24, 200000.0, 0.2, 1.0e-5, 24.5, 24.0, 400.0, 500.0
*SECTION
1, DBUSER, B400x600, 600.0, 400.0, 0.0, 0.0
2, DBUSER, C600x600, 600.0, 600.0, 0.0, 0.0
*ELEMENT
1, BEAM, 1, 1, 3, 4
2, BEAM, 1, 2, 1, 3
3, BEAM, 1, 2, 2, 4
*STORY
1F, 3.5, 3.5
*FORCE-BEAM
1, 1.2D+1.6L, I, 0.0, 45.0, 0.0, 0.0, 0.0, -90.0
1, 1.2D+1.6L, M, 0.0, 5.0, 0.0, 0.0, 0.0, 110.0
*FORCE-COLUMN
2, 1.2D+1.6L, I, -1200.0, 20.0, 0.0, 0.0, 0.0, 40.0
3, 1.2D+1.6L, I, -1200.0, 20.0, 0.0, 0.0, 0.0, 40.0
"""


def test_mgt_upload_and_batch_design():
    """Test uploading MGT text and executing batch design check via REST API."""
    # 1. Upload MGT
    resp_upload = client.post("/api/v1/interop/mgt/upload", data={"mgt_text": SAMPLE_MGT_TEXT})
    assert resp_upload.status_code == 200
    data = resp_upload.json()
    assert data["success"] is True
    assert data["total_nodes"] == 4
    assert data["total_elements"] == 3

    # 2. Run batch design
    resp_batch = client.post("/api/v1/interop/batch-design", json={})
    assert resp_batch.status_code == 200
    batch_res = resp_batch.json()
    assert batch_res["total_members"] == 3
    assert batch_res["safe_count"] >= 0
    assert len(batch_res["results"]) == 3

    # 3. Get batch summary
    resp_summary = client.get("/api/v1/interop/batch-summary")
    assert resp_summary.status_code == 200
    assert resp_summary.json()["total_members"] == 3

    # 4. Check status
    resp_status = client.get("/api/v1/interop/batch-status/task_123")
    assert resp_status.status_code == 200
    assert resp_status.json()["status"] == "COMPLETED"


def test_mgt_upload_empty_fails():
    """Test upload error when neither file nor text is provided."""
    resp = client.post("/api/v1/interop/mgt/upload", data={})
    assert resp.status_code == 400

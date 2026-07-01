import uuid
import json
import httpx
import hashlib
import pytest
from datetime import datetime


pytestmark = pytest.mark.integration


class TestFullPipeline:

    BASE_URL = "http://localhost:8080"

    @pytest.fixture
    def http_client(self):
        try:
            import httpx
            return httpx.AsyncClient(base_url=self.BASE_URL, timeout=10.0)
        except ImportError:
            pytest.skip("httpx not available")

    @pytest.mark.asyncio
    async def test_full_pipeline_happy_path(self, http_client):
        system_id = str(uuid.uuid4())
        run_id = str(uuid.uuid4())

        register_payload = {
            "run_id": run_id,
            "system_id": system_id,
            "system_name": "E2ETestSystem",
            "system_version": "1.0.0",
            "vendor": "TestVendor",
            "deployment_environment": "testing",
            "data_lineage": {
                "sources": ["e2e_source"],
                "transformations": ["e2e_transform"],
                "destinations": ["e2e_dest"],
            },
            "jurisdictions": ["EU"],
            "requested_by": "e2e@test.example.com",
        }

        phase_results = {}

        try:
            resp = await http_client.post("/audit/register", json=register_payload)
            assert resp.status_code == 201
            data = resp.json()
            assert data["status"] == "REGISTERED"
            phase_results[1] = True

            await http_client.post("/audit/register-phase-result", json={
                "run_id": run_id, "phase": 1, "phase_result": "PASS",
                "artifact_hash": hashlib.sha256(json.dumps(register_payload).encode()).hexdigest(),
                "findings": [],
            })

            scope_payload = {
                "run_id": run_id,
                "jurisdictions": ["EU"],
                "system_type": "classification",
                "deployment_context": "B2B",
            }
            resp = await http_client.post("/audit/register-phase-result", json={
                "run_id": run_id, "phase": 2, "phase_result": "PASS",
                "artifact_hash": hashlib.sha256(json.dumps(scope_payload).encode()).hexdigest(),
                "findings": [],
            })
            assert resp.status_code == 200
            phase_results[2] = True

            resp = await http_client.get(f"/audit/{run_id}/status")
            assert resp.status_code == 200
            status_data = resp.json()
            assert status_data["run_id"] == run_id

        except (httpx.ConnectError, httpx.TimeoutException) as exc:
            pytest.skip(f"Orchestrator not reachable at {self.BASE_URL}: {exc}")

    @pytest.mark.asyncio
    async def test_pipeline_rejects_phase_without_registration(self, http_client):
        phantom_run_id = str(uuid.uuid4())
        try:
            resp = await http_client.post("/audit/register-phase-result", json={
                "run_id": phantom_run_id, "phase": 3, "phase_result": "PASS",
                "artifact_hash": "a" * 64, "findings": [],
            })
            assert resp.status_code in (400, 404, 500)
        except (httpx.ConnectError, httpx.TimeoutException) as exc:
            pytest.skip(f"Orchestrator not reachable: {exc}")

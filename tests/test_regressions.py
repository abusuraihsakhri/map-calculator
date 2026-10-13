"""Regression tests for numerical validation, audit integrity and API access."""
import csv
import math

import pytest
from fastapi.testclient import TestClient

from map_calc import calculate_map, process_csv, classify_map, map_alternative, pulse_pressure
from agents.api import app
from agents.base import AuditTrail
from agents.llm_factory import LLMFactory

@pytest.mark.parametrize("sbp,dbp,hr,icp", [
    (math.nan,80,None,None),
    (math.inf,80,None,None),
    (120,-math.inf,None,None),
    (120,80,math.nan,None),
    (120,80,None,math.inf),
    (120,140,None,None),
])
def test_invalid_measurements_rejected(sbp, dbp, hr, icp):
    with pytest.raises(ValueError):
        calculate_map(sbp, dbp, hr=hr, icp=icp)

@pytest.mark.parametrize("function", [map_alternative, pulse_pressure])
def test_nonfinite_alternate_entry_points(function):
    with pytest.raises(ValueError):
        function(math.nan, 80)


def test_alternative_large_finite_numbers():
    assert math.isfinite(map_alternative(1e308, 1e308))


def test_nonfinite_classification_rejected():
    with pytest.raises(ValueError):
        classify_map(math.nan)

def test_csv_nonfinite_row_reports_error(tmp_path):
    infile=tmp_path/"input.csv"
    outfile=tmp_path/"output.csv"
    infile.write_text("sbp,dbp\n120,80\nnan,80\n", encoding="utf-8")
    results=process_csv(infile,outfile)
    assert results[0]["map_mmhg"] == 93.3
    assert "error" in results[1]
    with outfile.open(newline="", encoding="utf-8") as f:
        exported=list(csv.DictReader(f))
    assert len(exported) == 2
    assert exported[1]["error"]

def test_signature_forgery_detected():
    trail=AuditTrail(secret_key="regression-test-only")
    trail.log("tester","qa","RUN",{"value":1})
    assert trail.verify_integrity()
    trail.logs[0]["actor"]="altered"
    assert not trail.verify_integrity()

def test_bad_signature_detected():
    trail=AuditTrail(secret_key="regression-test-only")
    trail.log("tester","qa","RUN",{"value":1})
    trail.logs[0]["current_hash"]="0"*64
    assert not trail.verify_integrity()

def test_returned_audit_trail_cannot_modify_internal_chain():
    trail=AuditTrail(secret_key="regression-test-only")
    trail.log("tester","qa","RUN",{"value":1})
    entries=trail.get_trail()
    entries[0]["actor"]="altered"
    assert trail.verify_integrity()
    assert trail.get_trail()[0]["actor"]=="tester"

def test_sensitive_api_requires_key(monkeypatch):
    payload={"task_id":"TEST-001","target_identifier":"KEY-01","primary_metric":10}
    client=TestClient(app)
    monkeypatch.delenv("MAP_API_KEY",raising=False)
    assert client.post("/api/audit",json=payload).status_code==503
    monkeypatch.setenv("MAP_API_KEY","regression-test-api-key")
    assert client.post("/api/audit",json=payload).status_code==401
    response=client.post("/api/audit",json=payload,headers={"X-API-Key":"regression-test-api-key"})
    assert response.status_code==200
    assert response.json()["overall_urgency"]=="ROUTINE"
    assert client.get("/api/audit/logs").status_code==401
    assert client.get("/api/audit/logs",headers={"X-API-Key":"regression-test-api-key"}).status_code==200

def test_static_page_routes():
    client=TestClient(app)
    assert "Mean arterial pressure calculator" in client.get("/").text
    assert "Backend task evaluation" in client.get("/console").text
    assert client.get("/assets/app.js").status_code==200

def test_mock_does_not_claim_clinical_verification():
    answer=LLMFactory.create("mock").invoke("Explain MAP")
    assert "not clinically evaluated" in answer
    with pytest.raises(ValueError):
        LLMFactory.create("unsupported-provider")

"""
Automated Pytest Test Suite for Map Calculator.
Domain: Clinical & Biomedical AI
Standard: CAP / CLSI / ISO Standards
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import pytest
from agents.base import PHIGuard, AuditLogger, SecurityException
from agents.models import SystemTaskPayload, UrgencyLevel, SystemIntegrityStatus
from agents.workers import InvariantQCWorker, SafetyEscalationWorker, ProtocolConformanceWorker
from agents.supervisor import SystemSupervisor
from cli import main


def test_phi_guard_enforcement():
    with pytest.raises(SecurityException):
        PHIGuard.assert_no_phi("Patient MRN-994827 blood culture positive for Staphylococcus")

    # Clean text passes
    PHIGuard.assert_no_phi("Analytical assay specimen KEY-001 optimal")


def test_specialized_workers():
    # Worker 1: QC Invariant
    p1 = SystemTaskPayload(task_id="T1", target_identifier="KEY-01", primary_metric=35.0)
    alerts1 = InvariantQCWorker.evaluate(p1)
    assert len(alerts1) == 1
    assert alerts1[0].urgency == UrgencyLevel.ELEVATED

    # Worker 2: Safety
    p2 = SystemTaskPayload(task_id="T2", target_identifier="KEY-02", primary_metric=10.0, is_critical_flag=True)
    alerts2 = SafetyEscalationWorker.evaluate(p2)
    assert len(alerts2) == 1
    assert alerts2[0].urgency == UrgencyLevel.CRITICAL_STAT

    # Worker 3: Protocol Conformance
    p3 = SystemTaskPayload(task_id="T3", target_identifier="KEY-03", primary_metric=10.0, status_descriptor="DISCORDANT_ANOMALY")
    alerts3 = ProtocolConformanceWorker.evaluate(p3)
    assert len(alerts3) == 1


def test_supervisor_consensus_and_audit():
    supervisor = SystemSupervisor(model_provider="mock")
    payload = SystemTaskPayload(
        task_id="TASK-PROD-01",
        target_identifier="KEY-PROD-01",
        primary_metric=12.0,
        secondary_metric=4.0,
        status_descriptor="NOMINAL"
    )
    dossier = supervisor.process_task(payload)
    assert dossier.overall_urgency == UrgencyLevel.ROUTINE
    assert dossier.integrity_status == SystemIntegrityStatus.VALIDATED
    assert dossier.audit_hash != ""

    # Verify cryptographic audit trail
    assert AuditLogger.verify_integrity() is True

    # CLI tests
    assert main(["audit", "--task-id", "CLI-TEST-01"]) == 0
    assert main(["chat", "Explain", "specifications"]) == 0
    assert main(["verify-audit"]) == 0


def test_cli_audit_with_critical_flag():
    """Test audit CLI with critical flag."""
    assert main(["audit", "--task-id", "CRIT-TEST", "--primary", "50", "--critical"]) == 0


def test_cli_audit_with_custom_metrics():
    """Test audit CLI with custom metrics."""
    result = main([
        "audit",
        "--task-id", "METRICS-TEST",
        "--primary", "30.5",
        "--secondary", "15.2",
        "--descriptor", "DISCORDANT_ANOMALY"
    ])
    assert result == 0


def test_cli_chat_rejects_phi():
    """Test that chat CLI rejects PHI-containing queries."""
    result = main(["chat", "Patient", "MRN-12345678", "blood", "test"])
    assert result != 0, "Chat should reject PHI-containing queries"


def test_cli_single_calculation():
    """Test single calculation CLI."""
    result = main(["single", "--sbp", "120", "--dbp", "80"])
    assert result == 0


def test_cli_single_with_all_params():
    """Test single calculation with all parameters."""
    result = main(["single", "--sbp", "120", "--dbp", "80", "--hr", "72", "--icp", "10"])
    assert result == 0


def test_cli_batch_csv(tmp_path):
    """Test batch CSV processing CLI."""
    import csv
    input_csv = tmp_path / "test_input.csv"
    output_csv = tmp_path / "test_output.csv"

    with open(input_csv, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["sbp", "dbp", "hr"])
        writer.writerow(["120", "80", "72"])
        writer.writerow(["140", "90", "85"])

    result = main(["batch", "-i", str(input_csv), "-o", str(output_csv)])
    assert result == 0
    assert output_csv.exists()

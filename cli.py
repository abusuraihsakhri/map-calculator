#!/usr/bin/env python3
"""CLI for Mean Arterial Pressure (MAP) Calculator."""
import argparse
import json
import sys

from map_calc import calculate_map, process_csv


def _run_audit(args):
    """Run a distributed component audit task."""
    try:
        from agents.base import AuditLogger, PHIGuard
        from agents.models import SystemTaskPayload
        from agents.supervisor import SystemSupervisor

        task_id = args.task_id or f"CLI-TASK-{__import__('random').randint(10000, 99999)}"
        PHIGuard.assert_no_phi(task_id)

        payload = SystemTaskPayload(
            task_id=task_id,
            target_identifier=args.target or "CLI-TARGET",
            primary_metric=args.primary or 10.0,
            secondary_metric=args.secondary or 5.0,
            status_descriptor=args.descriptor or "NOMINAL",
            is_critical_flag=args.critical,
        )
        supervisor = SystemSupervisor(model_provider="mock")
        dossier = supervisor.process_task(payload, actor="CLI")
        print(json.dumps(dossier.to_dict(), indent=2, default=str))
        return 0
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1


def _run_chat(args):
    """Run a supervisor chat query."""
    try:
        from agents.base import PHIGuard
        from agents.supervisor import SystemSupervisor

        query = " ".join(args.query_parts) if isinstance(args.query_parts, list) else str(args.query_parts)
        PHIGuard.assert_no_phi(query)
        supervisor = SystemSupervisor(model_provider="mock")
        response = supervisor.query_supervisory_chat(query)
        print(json.dumps({"query": query, "response": response}, indent=2))
        return 0
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1


def _run_verify_audit(args):
    """Verify the HMAC-SHA256 audit trail integrity."""
    try:
        from agents.base import AuditLogger

        trail = AuditLogger.get_trail()
        verified = AuditLogger.verify_integrity()
        print(json.dumps({
            "audit_trail_length": len(trail),
            "integrity_verified": verified,
            "message": "Audit trail integrity verified." if verified else "Audit trail integrity check FAILED.",
        }, indent=2))
        return 0
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1


def _run_serve(args):
    """Start the FastAPI REST server."""
    try:
        import uvicorn
        from agents.api import app
    except ImportError as e:
        print(f"Missing dependency for serve: {e}", file=sys.stderr)
        print("Install with: pip install fastapi uvicorn", file=sys.stderr)
        return 1

    uvicorn.run(app, host=args.host, port=args.port)
    return 0


def main(argv=None):
    parser = argparse.ArgumentParser(
        prog="map-calculator",
        description="Mean Arterial Pressure (MAP) Calculator",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    # Single calculation
    single = subparsers.add_parser("single", help="Single patient calculation")
    single.add_argument("--sbp", type=float, required=True, help="Systolic BP (mmHg)")
    single.add_argument("--dbp", type=float, required=True, help="Diastolic BP (mmHg)")
    single.add_argument("--hr", type=float, default=None, help="Heart rate (bpm)")
    single.add_argument("--icp", type=float, default=None, help="Intracranial pressure (mmHg)")

    # Batch processing
    batch = subparsers.add_parser("batch", help="Batch process CSV")
    batch.add_argument("-i", "--input", required=True, help="Input CSV path")
    batch.add_argument("-o", "--output", default="results.csv", help="Output CSV path")

    # Distributed component audit
    audit = subparsers.add_parser("audit", help="Run distributed component audit")
    audit.add_argument("--task-id", default=None, help="Task identifier")
    audit.add_argument("--target", default="CLI-TARGET", help="Target identifier")
    audit.add_argument("--primary", type=float, default=10.0, help="Primary metric value")
    audit.add_argument("--secondary", type=float, default=5.0, help="Secondary metric value")
    audit.add_argument("--descriptor", default="NOMINAL", help="Status descriptor")
    audit.add_argument("--critical", action="store_true", help="Mark as critical")

    # Supervisor chat
    chat = subparsers.add_parser("chat", help="Supervisor chat query")
    chat.add_argument("query_parts", nargs="+", help="Query text")

    # Verify audit trail
    subparsers.add_parser("verify-audit", help="Verify HMAC-SHA256 audit trail integrity")

    # Serve REST API
    serve = subparsers.add_parser("serve", help="Start FastAPI REST server")
    serve.add_argument("--host", default="0.0.0.0", help="Host to bind")
    serve.add_argument("--port", type=int, default=8000, help="Port to bind")

    args = parser.parse_args(argv)

    if args.command == "single":
        result = calculate_map(args.sbp, args.dbp, hr=args.hr, icp=args.icp)
        print(json.dumps(result, indent=2))
        return 0

    if args.command == "batch":
        results = process_csv(args.input, args.output)
        print(f"Processed {len(results)} records -> {args.output}")
        return 0

    if args.command == "audit":
        return _run_audit(args)

    if args.command == "chat":
        return _run_chat(args)

    if args.command == "verify-audit":
        return _run_verify_audit(args)

    if args.command == "serve":
        return _run_serve(args)

    parser.print_help()
    return 1


if __name__ == "__main__":
    sys.exit(main())

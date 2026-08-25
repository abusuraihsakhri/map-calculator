#!/usr/bin/env python3
"""
Mean Arterial Pressure (MAP) Calculator
========================================

Calculates MAP and related hemodynamic parameters:

  - MAP = DBP + (SBP - DBP) / 3
  - Alternative: MAP = (SBP + 2*DBP) / 3  (equivalent)
  - Pulse Pressure = SBP - DBP  (normal 30-50 mmHg)
  - Rate Pressure Product (RPP) = HR * SBP  (myocardial O2 demand index)
  - Cerebral Perfusion Pressure (CPP) = MAP - ICP  (if ICP known)

Clinical thresholds:
    Normal MAP: 70-100 mmHg
    MAP < 65:   Inadequate organ perfusion (sepsis resuscitation target)
    MAP > 100:  Hypertensive range
    MAP > 120:  Hypertensive urgency
    MAP > 130:  Hypertensive emergency (with end-organ damage)

    Normal Pulse Pressure: 30-50 mmHg
    Wide PP (>50): Aortic regurgitation, hyperthyroidism, anemia
    Narrow PP (<30): Heart failure, tamponade, aortic stenosis

    RPP < 10,000: Normal myocardial O2 demand
    RPP > 12,000: Increased myocardial ischemia risk
    RPP > 20,000: High risk of myocardial ischemia

Stdlib only — no external dependencies.
"""

import argparse
import csv
import json
import math
import sys


# ── Clinical thresholds ──────────────────────────────────────────────

MAP_NORMAL_LOW = 70
MAP_NORMAL_HIGH = 100
MAP_HYPERTENSIVE = 100
MAP_URGENCY = 120
MAP_EMERGENCY = 130
MAP_SEPSIS_TARGET = 65

PP_NORMAL_LOW = 30
PP_NORMAL_HIGH = 50

RPP_NORMAL = 10000
RPP_ELEVATED = 12000
RPP_HIGH_RISK = 20000


# ── Core calculations ────────────────────────────────────────────────

def mean_arterial_pressure(sbp, dbp):
    """Calculate Mean Arterial Pressure.

    MAP = DBP + (SBP - DBP) / 3
    Equivalently: MAP = (SBP + 2*DBP) / 3

    Parameters:
        sbp: systolic blood pressure in mmHg
        dbp: diastolic blood pressure in mmHg

    >>> mean_arterial_pressure(120, 80)
    93.333...
    """
    if sbp <= 0:
        raise ValueError(f"SBP must be positive, got {sbp}")
    if dbp < 0:
        raise ValueError(f"DBP must be non-negative, got {dbp}")
    if dbp > sbp:
        raise ValueError(f"DBP ({dbp}) cannot exceed SBP ({sbp})")
    return dbp + (sbp - dbp) / 3.0


def map_alternative(sbp, dbp):
    """Alternative MAP formula: (SBP + 2*DBP) / 3.

    Mathematically equivalent to DBP + (SBP-DBP)/3.
    """
    if sbp <= 0:
        raise ValueError(f"SBP must be positive, got {sbp}")
    if dbp < 0:
        raise ValueError(f"DBP must be non-negative, got {dbp}")
    if dbp > sbp:
        raise ValueError(f"DBP ({dbp}) cannot exceed SBP ({sbp})")
    return (sbp + 2 * dbp) / 3.0


def pulse_pressure(sbp, dbp):
    """Calculate Pulse Pressure: PP = SBP - DBP.

    Normal: 30-50 mmHg.
    """
    if sbp <= 0:
        raise ValueError(f"SBP must be positive, got {sbp}")
    if dbp < 0:
        raise ValueError(f"DBP must be non-negative, got {dbp}")
    if dbp > sbp:
        raise ValueError(f"DBP ({dbp}) cannot exceed SBP ({sbp})")
    return sbp - dbp


def rate_pressure_product(hr, sbp):
    """Calculate Rate Pressure Product: RPP = HR * SBP.

    Indicator of myocardial oxygen demand.
    Normal: < 10,000.  Ischemia risk: > 12,000.

    Parameters:
        hr:  heart rate in bpm
        sbp: systolic blood pressure in mmHg

    Reference: Gobel FL, et al. Circulation 1978;57:549-556.
    """
    if hr <= 0:
        raise ValueError(f"Heart rate must be positive, got {hr}")
    if sbp <= 0:
        raise ValueError(f"SBP must be positive, got {sbp}")
    return hr * sbp


def cerebral_perfusion_pressure(map_val, icp):
    """Calculate Cerebral Perfusion Pressure: CPP = MAP - ICP.

    Normal CPP: 60-80 mmHg.
    CPP < 50: Ischemia risk.

    Parameters:
        map_val: mean arterial pressure in mmHg
        icp: intracranial pressure in mmHg

    Reference: Brain Trauma Foundation Guidelines.
    """
    if map_val <= 0:
        raise ValueError(f"MAP must be positive, got {map_val}")
    if icp < 0:
        raise ValueError(f"ICP must be non-negative, got {icp}")
    return map_val - icp


# ── Classification ───────────────────────────────────────────────────

def classify_map(map_val):
    """Classify MAP value by clinical thresholds.

    Returns a dict with category, description, and clinical significance.
    """
    if map_val < 60:
        return {
            "category": "critically_low",
            "description": "Critically low (<60 mmHg)",
            "clinical_significance": "Severe hypoperfusion, immediate intervention needed",
        }
    elif map_val < MAP_SEPSIS_TARGET:
        return {
            "category": "low",
            "description": "Below sepsis target (<65 mmHg)",
            "clinical_significance": "Inadequate organ perfusion, vasopressors may be needed",
        }
    elif map_val < MAP_NORMAL_LOW:
        return {
            "category": "borderline_low",
            "description": "Borderline low (65-70 mmHg)",
            "clinical_significance": "Acceptable but monitor closely",
        }
    elif map_val <= MAP_NORMAL_HIGH:
        return {
            "category": "normal",
            "description": "Normal (70-100 mmHg)",
            "clinical_significance": "Adequate organ perfusion",
        }
    elif map_val <= MAP_URGENCY:
        return {
            "category": "elevated",
            "description": "Elevated (100-120 mmHg)",
            "clinical_significance": "Hypertensive range, lifestyle modification recommended",
        }
    elif map_val <= MAP_EMERGENCY:
        return {
            "category": "high",
            "description": "Hypertensive urgency (120-130 mmHg)",
            "clinical_significance": "May need pharmacologic intervention",
        }
    else:
        return {
            "category": "critical_high",
            "description": "Hypertensive emergency (>130 mmHg)",
            "clinical_significance": "Risk of end-organ damage, urgent treatment needed",
        }


def classify_pulse_pressure(pp):
    """Classify pulse pressure."""
    if pp < PP_NORMAL_LOW:
        return {
            "category": "narrow",
            "description": f"Narrow (<{PP_NORMAL_LOW} mmHg)",
            "clinical_significance": "Consider heart failure, tamponade, or aortic stenosis",
        }
    elif pp <= PP_NORMAL_HIGH:
        return {
            "category": "normal",
            "description": f"Normal ({PP_NORMAL_LOW}-{PP_NORMAL_HIGH} mmHg)",
            "clinical_significance": "Normal arterial compliance",
        }
    else:
        return {
            "category": "wide",
            "description": f"Wide (>{PP_NORMAL_HIGH} mmHg)",
            "clinical_significance": "Consider aortic regurgitation, hyperthyroidism, or anemia",
        }


def classify_rpp(rpp):
    """Classify Rate Pressure Product."""
    if rpp < RPP_NORMAL:
        return {
            "category": "normal",
            "description": "Normal myocardial O2 demand",
        }
    elif rpp < RPP_ELEVATED:
        return {
            "category": "borderline",
            "description": "Borderline elevated myocardial demand",
        }
    elif rpp < RPP_HIGH_RISK:
        return {
            "category": "elevated",
            "description": "Increased myocardial ischemia risk",
        }
    else:
        return {
            "category": "high_risk",
            "description": "High risk of myocardial ischemia",
        }


def classify_cpp(cpp):
    """Classify Cerebral Perfusion Pressure."""
    if cpp < 50:
        return {
            "category": "critical",
            "description": "Critical: cerebral ischemia risk",
        }
    elif cpp < 60:
        return {
            "category": "low",
            "description": "Below target, consider intervention",
        }
    elif cpp <= 80:
        return {
            "category": "normal",
            "description": "Normal cerebral perfusion",
        }
    else:
        return {
            "category": "elevated",
            "description": "Elevated, may increase ICP",
        }


# ── Comprehensive assessment ─────────────────────────────────────────

def calculate_map(sbp, dbp, hr=None, icp=None):
    """Calculate MAP and all related hemodynamic parameters.

    Parameters:
        sbp: systolic blood pressure in mmHg
        dbp: diastolic blood pressure in mmHg
        hr:  heart rate in bpm (optional, for RPP)
        icp: intracranial pressure in mmHg (optional, for CPP)

    Returns a dict with all calculated values and classifications.
    """
    map_val = mean_arterial_pressure(sbp, dbp)
    map_alt = map_alternative(sbp, dbp)
    pp = pulse_pressure(sbp, dbp)

    result = {
        "sbp_mmhg": sbp,
        "dbp_mmhg": dbp,
        "map_mmhg": round(map_val, 1),
        "map_alternative_mmhg": round(map_alt, 1),
        "pulse_pressure_mmhg": round(pp, 1),
        "map_classification": classify_map(map_val),
        "pp_classification": classify_pulse_pressure(pp),
    }

    if hr is not None:
        rpp = rate_pressure_product(hr, sbp)
        result["hr_bpm"] = hr
        result["rpp"] = round(rpp, 0)
        result["rpp_classification"] = classify_rpp(rpp)

    if icp is not None:
        cpp = cerebral_perfusion_pressure(map_val, icp)
        result["icp_mmhg"] = icp
        result["cpp_mmhg"] = round(cpp, 1)
        result["cpp_classification"] = classify_cpp(cpp)

    return result


# ── CSV batch processing ─────────────────────────────────────────────

def process_csv(input_path, output_path):
    """Process a CSV file of blood pressure measurements.

    Expected columns: sbp, dbp. Optional: hr, icp.
    """
    with open(input_path, newline="", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        fieldnames = list(reader.fieldnames or [])
        rows = list(reader)

    results = []
    for row in rows:
        try:
            sbp = float(row.get("sbp"))
            dbp = float(row.get("dbp"))
            hr = row.get("hr") or row.get("heart_rate")
            icp = row.get("icp")

            res = calculate_map(
                sbp, dbp,
                hr=float(hr) if hr else None,
                icp=float(icp) if icp else None,
            )
            flat = {
                "map_mmhg": res["map_mmhg"],
                "pulse_pressure_mmhg": res["pulse_pressure_mmhg"],
                "map_category": res["map_classification"]["category"],
                "map_description": res["map_classification"]["description"],
            }
            if "rpp" in res:
                flat["rpp"] = res["rpp"]
                flat["rpp_category"] = res["rpp_classification"]["category"]
            if "cpp_mmhg" in res:
                flat["cpp_mmhg"] = res["cpp_mmhg"]
                flat["cpp_category"] = res["cpp_classification"]["category"]
        except (ValueError, TypeError, KeyError) as e:
            flat = {"error": str(e)}

        merged = {**row, **{k: str(v) for k, v in flat.items()}}
        results.append(merged)

    all_keys = set()
    for r in results:
        all_keys.update(r.keys())
    extra = sorted(k for k in all_keys if k not in fieldnames)
    out_fields = fieldnames + extra

    with open(output_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=out_fields)
        writer.writeheader()
        writer.writerows(results)

    return results


# ── CLI ──────────────────────────────────────────────────────────────

def main(argv=None):
    parser = argparse.ArgumentParser(
        description="Mean Arterial Pressure (MAP) Calculator"
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

    args = parser.parse_args(argv)

    if args.command == "single":
        res = calculate_map(args.sbp, args.dbp, hr=args.hr, icp=args.icp)
        print(json.dumps(res, indent=2))
        return 0

    if args.command == "batch":
        results = process_csv(args.input, args.output)
        print(f"Processed {len(results)} records -> {args.output}")
        return 0

    parser.print_help()
    return 1


if __name__ == "__main__":
    sys.exit(main())

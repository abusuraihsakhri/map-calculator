"""Tests for map_calc.py — Mean Arterial Pressure Calculator.

Run with: python -m pytest test_map_calc.py -v
"""
import pytest
from map_calc import (
    mean_arterial_pressure, map_alternative, pulse_pressure,
    rate_pressure_product, cerebral_perfusion_pressure,
    classify_map, classify_pulse_pressure, classify_rpp, classify_cpp,
    calculate_map, process_csv,
)


# ── MAP calculation ─────────────────────────────────────────────────

class TestMAP:
    def test_standard(self):
        # MAP = 80 + (120-80)/3 = 93.33
        result = mean_arterial_pressure(120, 80)
        assert abs(result - 93.33) < 0.1

    def test_equal_bp(self):
        # MAP = 100 + 0/3 = 100
        assert mean_arterial_pressure(100, 100) == 100.0

    def test_low_bp(self):
        # MAP = 60 + (90-60)/3 = 70
        assert abs(mean_arterial_pressure(90, 60) - 70.0) < 0.1

    def test_high_bp(self):
        # MAP = 100 + (180-100)/3 = 126.67
        assert abs(mean_arterial_pressure(180, 100) - 126.67) < 0.1

    def test_invalid_sbp(self):
        with pytest.raises(ValueError):
            mean_arterial_pressure(0, 80)

    def test_dbp_exceeds_sbp(self):
        with pytest.raises(ValueError):
            mean_arterial_pressure(80, 120)


# ── Alternative MAP formula ─────────────────────────────────────────

class TestMAPAlternative:
    def test_equivalent(self):
        # Both formulas should give the same result
        sbp, dbp = 120, 80
        assert abs(mean_arterial_pressure(sbp, dbp) - map_alternative(sbp, dbp)) < 0.001

    def test_standard(self):
        # (120 + 2*80) / 3 = 280/3 = 93.33
        assert abs(map_alternative(120, 80) - 93.33) < 0.1


# ── Pulse pressure ──────────────────────────────────────────────────

class TestPulsePressure:
    def test_normal(self):
        assert pulse_pressure(120, 80) == 40

    def test_wide(self):
        assert pulse_pressure(160, 60) == 100

    def test_narrow(self):
        assert pulse_pressure(100, 80) == 20

    def test_equal(self):
        assert pulse_pressure(100, 100) == 0


# ── Rate Pressure Product ───────────────────────────────────────────

class TestRPP:
    def test_normal(self):
        # RPP = 72 * 120 = 8640
        assert rate_pressure_product(72, 120) == 8640

    def test_high(self):
        # RPP = 100 * 180 = 18000
        assert rate_pressure_product(100, 180) == 18000

    def test_invalid_hr(self):
        with pytest.raises(ValueError):
            rate_pressure_product(0, 120)


# ── Cerebral Perfusion Pressure ─────────────────────────────────────

class TestCPP:
    def test_normal(self):
        # CPP = 93.3 - 10 = 83.3
        result = cerebral_perfusion_pressure(93.3, 10)
        assert abs(result - 83.3) < 0.1

    def test_elevated_icp(self):
        # CPP = 93.3 - 30 = 63.3
        result = cerebral_perfusion_pressure(93.3, 30)
        assert abs(result - 63.3) < 0.1

    def test_critical_icp(self):
        # CPP = 93.3 - 60 = 33.3
        result = cerebral_perfusion_pressure(93.3, 60)
        assert abs(result - 33.3) < 0.1

    def test_invalid_icp(self):
        with pytest.raises(ValueError):
            cerebral_perfusion_pressure(93.3, -5)


# ── MAP classification ──────────────────────────────────────────────

class TestClassifyMAP:
    def test_normal(self):
        result = classify_map(85)
        assert result["category"] == "normal"

    def test_critically_low(self):
        result = classify_map(50)
        assert result["category"] == "critically_low"

    def test_sepsis_target(self):
        result = classify_map(63)
        assert result["category"] == "low"

    def test_borderline_low(self):
        result = classify_map(68)
        assert result["category"] == "borderline_low"

    def test_elevated(self):
        result = classify_map(110)
        assert result["category"] == "elevated"

    def test_hypertensive_urgency(self):
        result = classify_map(125)
        assert result["category"] == "high"

    def test_hypertensive_emergency(self):
        result = classify_map(140)
        assert result["category"] == "critical_high"


# ── Pulse pressure classification ───────────────────────────────────

class TestClassifyPP:
    def test_normal(self):
        result = classify_pulse_pressure(40)
        assert result["category"] == "normal"

    def test_narrow(self):
        result = classify_pulse_pressure(20)
        assert result["category"] == "narrow"

    def test_wide(self):
        result = classify_pulse_pressure(70)
        assert result["category"] == "wide"


# ── RPP classification ──────────────────────────────────────────────

class TestClassifyRPP:
    def test_normal(self):
        result = classify_rpp(8000)
        assert result["category"] == "normal"

    def test_elevated(self):
        result = classify_rpp(15000)
        assert result["category"] == "elevated"

    def test_high_risk(self):
        result = classify_rpp(22000)
        assert result["category"] == "high_risk"


# ── CPP classification ──────────────────────────────────────────────

class TestClassifyCPP:
    def test_normal(self):
        result = classify_cpp(70)
        assert result["category"] == "normal"

    def test_critical(self):
        result = classify_cpp(40)
        assert result["category"] == "critical"

    def test_low(self):
        result = classify_cpp(55)
        assert result["category"] == "low"


# ── Comprehensive calculate_map ─────────────────────────────────────

class TestCalculateMAP:
    def test_basic(self):
        result = calculate_map(120, 80)
        assert abs(result["map_mmhg"] - 93.3) < 0.1
        assert result["pulse_pressure_mmhg"] == 40.0

    def test_with_hr(self):
        result = calculate_map(120, 80, hr=72)
        assert "rpp" in result
        assert result["rpp"] == 8640

    def test_with_icp(self):
        result = calculate_map(120, 80, icp=10)
        assert "cpp_mmhg" in result
        assert abs(result["cpp_mmhg"] - 83.3) < 0.5

    def test_all_parameters(self):
        result = calculate_map(120, 80, hr=72, icp=10)
        assert "map_mmhg" in result
        assert "pulse_pressure_mmhg" in result
        assert "rpp" in result
        assert "cpp_mmhg" in result
        assert "map_classification" in result
        assert "pp_classification" in result
        assert "rpp_classification" in result
        assert "cpp_classification" in result

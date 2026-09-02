# Map Calculator

> **Domain:** Clinical Decision Support & Biomedical Computing  
> **Reference Guidelines & Standards:** `Standard Clinical Formulations & ISO/IEC Quality Frameworks`

<div align="center">

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
![Python](https://img.shields.io/badge/Python-3.10%20%7C%203.11%20%7C%203.12-3776AB.svg?logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-0.111-009688.svg?logo=fastapi&logoColor=white)
![Audit Trail](https://img.shields.io/badge/Audit-HMAC--SHA256_Tamper--Evident-brightgreen.svg)
![Zero-PHI Guard](https://img.shields.io/badge/Guard-Zero--PHI_Outbound-blue.svg)
![Docker](https://img.shields.io/badge/Docker-Ready-2496ED.svg?logo=docker&logoColor=white)

</div>

---

## 📖 What It Does

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

---

## ⚙️ Key Capabilities & Algorithmic Modules

### 🔬 Analytical Functions

- **`mean_arterial_pressure()`**: Calculate Mean Arterial Pressure.

MAP = DBP + (SBP - DBP) / 3
Equivalently: MAP = (SBP + 2*DBP) / 3

Parameters:
    sbp: systolic blood pressure in mmHg
    dbp: diastolic blood pressure in mmHg

>>> mean_arterial_pressure(120, 80)
93.333...
- **`map_alternative()`**: Alternative MAP formula: (SBP + 2*DBP) / 3.

Mathematically equivalent to DBP + (SBP-DBP)/3.
- **`pulse_pressure()`**: Calculate Pulse Pressure: PP = SBP - DBP.

Normal: 30-50 mmHg.
- **`rate_pressure_product()`**: Calculate Rate Pressure Product: RPP = HR * SBP.

Indicator of myocardial oxygen demand.
Normal: < 10,000.  Ischemia risk: > 12,000.

Parameters:
    hr:  heart rate in bpm
    sbp: systolic blood pressure in mmHg

Reference: Gobel FL, et al. Circulation 1978;57:549-556.
- **`cerebral_perfusion_pressure()`**: Calculate Cerebral Perfusion Pressure: CPP = MAP - ICP.

Normal CPP: 60-80 mmHg.
CPP < 50: Ischemia risk.

Parameters:
    map_val: mean arterial pressure in mmHg
    icp: intracranial pressure in mmHg

Reference: Brain Trauma Foundation Guidelines.

---

## 📐 Mathematical Formulation & Logic

```text
  Calculates MAP and related hemodynamic parameters:
  RPP_HIGH_RISK = 20000
  """Calculate Mean Arterial Pressure.
  """Alternative MAP formula: (SBP + 2*DBP) / 3.
  return (sbp + 2 * dbp) / 3.0
```

---

## 💻 CLI Quickstart & Usage

### 1. Guided Interactive Mode
```bash
python cli.py
```

### 2. Direct Parameterized Evaluation
```bash
python cli.py --sbp <value> --dbp <value> --hr <value> --icp <value>
```

### Parameter Reference
- `--sbp`: Specifies input measurement or parameter value.
- `--dbp`: Specifies input measurement or parameter value.
- `--hr`: Specifies input measurement or parameter value.
- `--icp`: Specifies input measurement or parameter value.
- `--input`: Specifies input measurement or parameter value.
- `--output`: Specifies input measurement or parameter value.

### Input Data Schema

| Field | Description | Requirement |
|:------|:------------|:------------|
| `id` | Parameter / observation metric | Required |
| `value` | Parameter / observation metric | Required |
| `qty` | Parameter / observation metric | Required |

---

## 🛡️ Security & Enterprise Architecture

* **Zero-PHI Outbound Interceptor:** Active AST and regex inspection blocking SSNs, MRNs, phone numbers, and patient identifiers.
* **Tamper-Evident HMAC-SHA256 Audit Trail:** Chained, cryptographically signed logs for every evaluation and state transition.
* **Air-Gapped LLM Reasoning Adapter:** Agnostic integration for local Ollama instances (`llama3`, `mistral`), Claude 3.5 Sonnet, GPT-4o, and deterministic test mocks.
* **Active Learning Bayesian Calibration:** Dynamic tracker updating worker reliability weights and monitoring Brier calibration drift.
* **FastAPI & Prometheus Telemetry:** Exposes OpenAPI 3.1 REST endpoints and operational Prometheus metrics (`/metrics`).

---

## 🧪 Testing & Verification

Run the automated test suite:

```bash
pytest -v
```

Execute high-throughput batch simulation benchmarks:

```bash
python simulator.py --tasks 1000 --concurrency 8
```

---

## 🐳 Container Deployment

```bash
docker build -t map-calculator .
docker run -p 8000:8000 map-calculator
```

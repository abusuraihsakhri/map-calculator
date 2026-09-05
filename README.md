# Map Calculator

> **Domain:** Clinical Decision Support & Biomedical Computing
> **Standards:** Clinical Hemodynamic Formulations & ISO/IEC Quality Frameworks

<div align="center">

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
![Python](https://img.shields.io/badge/Python-3.10%20%7C%203.11%20%7C%203.12-3776AB.svg?logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-0.111%2B-009688.svg?logo=fastapi&logoColor=white)
![Audit Trail](https://img.shields.io/badge/Audit-HMAC--SHA256_Tamper--Evident-brightgreen.svg)
![Zero-PHI Guard](https://img.shields.io/badge/Guard-Zero--PHI_Outbound-blue.svg)
![Docker](https://img.shields.io/badge/Docker-Ready-2496ED.svg?logo=docker&logoColor=white)

</div>

---

## What It Does

Mean Arterial Pressure (MAP) Calculator

Calculates MAP and related hemodynamic parameters:

- **MAP = DBP + (SBP - DBP) / 3**
- **Alternative: MAP = (SBP + 2*DBP) / 3** (equivalent)
- **Pulse Pressure = SBP - DBP** (normal 30-50 mmHg)
- **Rate Pressure Product (RPP) = HR x SBP** (myocardial O2 demand index)
- **Cerebral Perfusion Pressure (CPP) = MAP - ICP** (if ICP known)

### Clinical Thresholds

| Parameter | Range | Meaning |
|-----------|-------|---------|
| MAP < 60 | Critically low | Severe hypoperfusion, immediate intervention |
| MAP 60-65 | Below sepsis target | Inadequate organ perfusion |
| MAP 65-70 | Borderline low | Acceptable but monitor closely |
| MAP 70-100 | Normal | Adequate organ perfusion |
| MAP 100-120 | Elevated | Hypertensive range |
| MAP 120-130 | Hypertensive urgency | May need pharmacologic intervention |
| MAP > 130 | Hypertensive emergency | Risk of end-organ damage |
| PP < 30 | Narrow | Consider heart failure, tamponade, aortic stenosis |
| PP 30-50 | Normal | Normal arterial compliance |
| PP > 50 | Wide | Consider aortic regurgitation, hyperthyroidism, anemia |
| RPP < 10,000 | Normal | Normal myocardial O2 demand |
| RPP 12,000-20,000 | Elevated | Increased myocardial ischemia risk |
| RPP > 20,000 | High risk | High risk of myocardial ischemia |

---

## Key Capabilities

### Analytical Functions

- **`mean_arterial_pressure(sbp, dbp)`**: Calculate Mean Arterial Pressure
- **`map_alternative(sbp, dbp)`**: Alternative MAP formula: (SBP + 2*DBP) / 3
- **`pulse_pressure(sbp, dbp)`**: Calculate Pulse Pressure: PP = SBP - DBP
- **`rate_pressure_product(hr, sbp)`**: Calculate RPP = HR * SBP
- **`cerebral_perfusion_pressure(map_val, icp)`**: Calculate CPP = MAP - ICP
- **`calculate_map(sbp, dbp, hr=None, icp=None)`**: Comprehensive calculation with classifications

### Classification Functions

- **`classify_map(map_val)`**: Classify MAP by clinical thresholds
- **`classify_pulse_pressure(pp)`**: Classify pulse pressure
- **`classify_rpp(rpp)`**: Classify Rate Pressure Product
- **`classify_cpp(cpp)`**: Classify Cerebral Perfusion Pressure

### Enterprise Features

- **Distributed Component Audit Framework**: Multi-worker evaluation with consensus
- **Zero-PHI Outbound Guard**: Blocks SSNs, MRNs, phone numbers, patient identifiers
- **HMAC-SHA256 Audit Trail**: Tamper-evident cryptographic logging
- **FastAPI REST API**: REST endpoints with OpenAPI documentation
- **Prometheus Metrics**: Operational telemetry export

---

## Installation

```bash
# Clone the repository
git clone https://github.com/abusuraihsakhri/map-calculator.git
cd map-calculator

# Optional: Create virtual environment
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
# or: .venv\Scripts\activate  # Windows

# Install dependencies (for REST API and enterprise features)
pip install pydantic fastapi uvicorn
```

**Note:** The core MAP calculations require no external dependencies (stdlib only).

---

## Usage

### CLI Quickstart

#### Single Calculation
```bash
python cli.py single --sbp 120 --dbp 80
python cli.py single --sbp 120 --dbp 80 --hr 72 --icp 10
```

#### Batch Processing
```bash
python cli.py batch -i sample.csv -o results.csv
```

Expected CSV columns: `sbp`, `dbp` (required), `hr`, `icp` (optional)

#### Distributed Component Audit
```bash
python cli.py audit --task-id TASK-001 --primary 25.5 --secondary 10.0
python cli.py audit --task-id CRIT-001 --primary 50 --critical
```

#### Supervisor Chat
```bash
python cli.py chat "Explain hemodynamic parameters"
```

#### Verify Audit Trail
```bash
python cli.py verify-audit
```

#### Start REST API Server
```bash
python cli.py serve --host 0.0.0.0 --port 8000
```

### Python API
```python
from map_calc import calculate_map, mean_arterial_pressure, classify_map

# Basic MAP calculation
map_val = mean_arterial_pressure(120, 80)  # Returns 93.33...

# Comprehensive calculation with classifications
result = calculate_map(120, 80, hr=72, icp=10)
print(result["map_mmhg"])           # 93.3
print(result["map_classification"]["category"])  # "normal"

# Classification only
classification = classify_map(85)
print(classification["description"])  # "Normal (70-100 mmHg)"
```

### REST API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/health` | GET | Health check |
| `/metrics` | GET | Prometheus-style metrics |
| `/api/audit` | POST | Process task payload |
| `/api/chat` | POST | Supervisor chat query |
| `/api/audit/logs` | GET | Get audit trail |

---

## Testing

Run the full test suite:
```bash
python -m pytest test_map_calc.py tests/ -v
```

Run with coverage:
```bash
python -m pytest --cov=. --cov-report=html
```

---

## Security

### Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `AUDIT_SECRET_KEY` | HMAC-SHA256 key for audit trail signing | Recommended |

**Important:** Set `AUDIT_SECRET_KEY` in production. Without it, a warning is emitted and an insecure default is used.

### PHI Protection

The system includes an active PHI outbound guard that blocks:
- Medical Record Numbers (MRN)
- Social Security Numbers
- Phone numbers
- Email addresses
- Patient names (common patterns)
- Dates of birth

---

## Docker Deployment

```bash
# Build and run with Docker Compose
AUDIT_SECRET_KEY=your-secret-key docker-compose up --build

# Or with Docker directly
docker build -t map-calculator .
docker run -p 8000:8000 -e AUDIT_SECRET_KEY=your-secret-key map-calculator
```

---

## Project Structure

```
map-calculator/
├── cli.py                 # Command-line interface
├── map_calc.py            # Core MAP calculations and CSV processing
├── enrichment.py          # Enrichment engines (analytics, reporting)
├── simulator.py           # Traffic simulator
├── sample.csv             # Sample data for batch processing
├── agents/                # Enterprise distributed component framework
│   ├── __init__.py
│   ├── api.py            # FastAPI REST server
│   ├── base.py           # PHI guard, HMAC audit trail
│   ├── models.py         # Pydantic data models
│   ├── supervisor.py     # Supervisor orchestrator
│   ├── workers.py        # Specialized worker agents
│   ├── llm_factory.py    # LLM provider factory
│   ├── metrics.py        # Prometheus metrics collector
│   ├── learning.py       # Bayesian calibration engine
│   └── streamer.py       # WebSocket telemetry broadcaster
├── tests/                # Test suite
│   ├── test_map_calculator.py
│   └── test_enrichment.py
├── web/index.html        # Operations console UI
├── Dockerfile
├── docker-compose.yml
└── benchmark_dataset.json # Test benchmark cases
```

---

## License

MIT License - see [LICENSE](LICENSE) for details.

# Map Calculator

A mean arterial pressure (MAP) calculator with a standalone browser interface, Python calculation library, CSV batch utility, and an optional FastAPI service.

## Features

- **Browser calculator:** SBP and DBP inputs, optional heart rate and intracranial pressure, instant results, validation, and a CSV download. The browser interface uses no external runtime dependencies.
- **Python library:** numerical calculations and descriptive threshold classifications.
- **CLI:** individual calculations and batch CSV processing.
- **Optional backend:** a separate generic task-audit demonstration with an in-memory HMAC audit chain and API-key-protected endpoints.

## Browser use

Open `index.html` in a modern browser, or serve the repository with `python -m http.server 8001` and open `http://localhost:8001/`. Enter systolic and diastolic pressures in mmHg and select **Calculate**. HR and ICP are optional.

All calculations in the standalone browser are performed locally. The interface does not send measurements to a server, use cookies, or retain measurement history. Exported CSV files are saved only when you select **Download results CSV**.

The browser implementation uses JavaScript, not Pyodide: the arithmetic is simple enough that embedding a Python runtime would substantially increase load time without improving fidelity.

## Equations

| Parameter | Equation |
| --- | --- |
| Mean arterial pressure (MAP) | DBP + (SBP − DBP) / 3 |
| Pulse pressure (PP) | SBP − DBP |
| Rate-pressure product (RPP) | HR × SBP |
| Cerebral perfusion pressure (CPP) | MAP − ICP |

MAP calculated from peripheral cuff pressure is an **estimate**, especially at extreme heart rates, unusual waveforms, or altered vascular compliance. Calculated CPP inherits uncertainty in MAP and ICP. A MAP value alone cannot establish organ perfusion, shock, hypertensive urgency, or hypertensive emergency; clinical assessment and individualized targets remain necessary. Threshold categories in the Python API are descriptive, not diagnostic or treatment rules.

## Python CLI

The core library and its CSV processor use Python standard-library modules only (Python 3.10+).

```bash
python cli.py single --sbp 120 --dbp 80 --hr 72 --icp 10
python cli.py batch --input sample.csv --output results.csv
python -m pytest -q
```

For the test suite or optional backend, install the declared dependencies:

```bash
python -m pip install -r requirements-dev.txt
```

Batch CSV input requires `sbp` and `dbp` columns. Optional columns are `hr` (or `heart_rate`) and `icp`. Invalid measurements are returned in a row-level `error` column. Malformed headers and excess CSV fields fail explicitly. When exporting, formula-like passthrough cells are escaped to reduce spreadsheet injection risk.

Example Python usage:

```python
from map_calc import calculate_map
result = calculate_map(120, 80, hr=72, icp=10)
print(result["map_mmhg"])  # 93.3
```

## Optional FastAPI service

```bash
python -m pip install -r requirements.txt
export MAP_API_KEY="replace-with-a-long-random-api-key"
export AUDIT_SECRET_KEY="replace-with-a-long-random-audit-key"
python cli.py serve --host 127.0.0.1 --port 8000
```

- `/` — browser MAP calculator
- `/console` — separate backend task-audit console
- `/health` — public health check
- `/metrics`, `/api/audit`, `/api/chat`, `/api/audit/logs` — require an `X-API-Key` header matching `MAP_API_KEY`

The generic audit workers are **not validated clinical decision-support algorithms**. The chat endpoint currently returns an explicit mock response; no hosted language-model integration is implemented. The task registry and audit logs are held **in memory**, so they are not durable across restarts. Use a persistent logging system if audit retention is required.

For Docker Compose, set `MAP_API_KEY` and `AUDIT_SECRET_KEY` in a local `.env` file or your shell environment, then run `docker compose up --build`. A random temporary audit signing key is used for local development if `AUDIT_SECRET_KEY` is absent; production deployments should set a persistent secret.

### Privacy and security limitations

The API's identifier-pattern checks are a **best-effort filter**, not complete PHI detection or HIPAA de-identification. Do not submit identifiable clinical records or expose the demonstration service directly to the public internet. The example API key provides basic access control, not comprehensive identity management, transport security, request rate limiting, or regulatory compliance. Use HTTPS and additional controls for any nonlocal deployment.

## Development and deployment

The browser app is plain HTML, CSS and JavaScript in `index.html` and `assets/`, with relative asset paths for GitHub Pages. The `.github/workflows/pages.yml` workflow publishes those static files from `master` when GitHub Pages is configured with **GitHub Actions** as the publishing source. The FastAPI service is not hosted by GitHub Pages.

Continuous integration runs the Python test suite on multiple Python versions and checks the browser script. The app works in current Chromium, Firefox, and Safari versions with JavaScript enabled; no vendor-specific browser APIs are required beyond Blob URL downloads.

## License

MIT; see [LICENSE](LICENSE).

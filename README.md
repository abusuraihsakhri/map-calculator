# Mean Arterial Pressure (MAP) Calculator

MAP and related hemodynamic parameters for hemodynamic monitoring.

## Formulas Implemented

| Parameter | Formula | Normal Range |
|-----------|---------|-------------|
| **MAP** | DBP + (SBP - DBP) / 3 | 70-100 mmHg |
| **MAP (alt)** | (SBP + 2×DBP) / 3 | Equivalent |
| **Pulse Pressure** | SBP - DBP | 30-50 mmHg |
| **Rate Pressure Product** | HR × SBP | < 10,000 |
| **Cerebral Perfusion Pressure** | MAP - ICP | 60-80 mmHg |

## Clinical Thresholds

### MAP
| Category | Range | Significance |
|----------|-------|-------------|
| Critically low | < 60 mmHg | Severe hypoperfusion |
| Low | < 65 mmHg | Sepsis resuscitation target |
| Normal | 70-100 mmHg | Adequate perfusion |
| Elevated | 100-120 mmHg | Hypertensive range |
| Urgency | 120-130 mmHg | May need pharmacologic intervention |
| Emergency | > 130 mmHg | Risk of end-organ damage |

### Pulse Pressure
| Category | Range | Consider |
|----------|-------|---------|
| Narrow | < 30 mmHg | HF, tamponade, aortic stenosis |
| Normal | 30-50 mmHg | Normal compliance |
| Wide | > 50 mmHg | AR, hyperthyroidism, anemia |

### Rate Pressure Product (RPP)
| Category | Value | Significance |
|----------|-------|-------------|
| Normal | < 10,000 | Normal myocardial O2 demand |
| Elevated | 12,000-20,000 | Ischemia risk |
| High risk | > 20,000 | High ischemia risk |

## Quick Start

```bash
# Single calculation
python cli.py single --sbp 120 --dbp 80

# With heart rate and ICP
python cli.py single --sbp 120 --dbp 80 --hr 72 --icp 15

# Batch CSV processing
python cli.py batch -i sample.csv -o results.csv
```

## Python API

```python
from map_calc import mean_arterial_pressure, pulse_pressure, rate_pressure_product, calculate_map

# Individual calculations
map_val = mean_arterial_pressure(120, 80)  # 93.3
pp = pulse_pressure(120, 80)               # 40
rpp = rate_pressure_product(72, 120)       # 8640

# Full assessment
result = calculate_map(sbp=120, dbp=80, hr=72, icp=15)
print(result['map_mmhg'])            # 93.3
print(result['pulse_pressure_mmhg']) # 40.0
print(result['rpp'])                 # 8640.0
print(result['cpp_mmhg'])            # 78.3
```

## Dependencies

Python standard library only. No external packages required.

## License

MIT License.

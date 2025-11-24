# Dose Every Well

**Precision weighing and dosing system for microplate automation.**

A Python package for automated gravimetric workflows combining precision weighing, plate handling, and optional CNC or Opentrons integration.

[![Python](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Platform](https://img.shields.io/badge/platform-Raspberry%20Pi%20%7C%20Linux-lightgrey.svg)]()

---

## What is MicroDoser?

**MicroDoser** is a weighing station that can optionally integrate with dosing systems:

```
MicroDoser = Balance + Plate Loader + Optional Dosing System
```

### Core Components

- **✅ Sartorius Balance** - Precision gravimetric measurement
- **✅ Motorized Plate Loader** - Automated plate handling with collision avoidance
- **⚙️ CNC Dosing System** (optional) - Automated solid dispensing  
- **⚙️ Opentrons Integration** (future) - Liquid handling support

---

## Quick Start

### Installation

```bash
git clone https://github.com/AccelerationConsortium/dose_every_well.git
cd dose_every_well
pip install -e ".[rpi]"  # Include Raspberry Pi dependencies
```

### Standalone Weighing Station

Manual dosing with automated weighing:

```python
from dose_every_well import MicroDoser

doser = MicroDoser(
    balance_port='/dev/ttyUSB1',
    plate_type='shallow_plate'
)

doser.load_plate()
input("Add material, press Enter...")
mass = doser.read_balance()
print(f"Mass: {mass * 1000:.2f} mg")
doser.unload_plate()
doser.shutdown()
```

### With CNC Automated Dosing

Full automation with gravimetric verification:

```python
from dose_every_well import MicroDoser, CNCDosingSystem

# Initialize dosing system
dosing_system = CNCDosingSystem(cnc_port='/dev/ttyUSB0')
dosing_system.initialize()

# Initialize MicroDoser
doser = MicroDoser(
    balance_port='/dev/ttyUSB1',
    plate_type='shallow_plate',
    dosing_system=dosing_system
)

# Dose with verification
doser.load_plate()
result = doser.dose_to_well('A1', target_mg=5.0)
print(f"Target: {result['target_mg']:.2f} mg, Actual: {result['actual_mg']:.2f} mg")
doser.unload_plate()
doser.shutdown()
```

---

## Features

### 🎯 High-Level API
- Simple, intuitive interface for common workflows
- Automatic coordination of all hardware components
- Built-in gravimetric verification

### ⚖️ Precision Weighing
- Sartorius balance integration
- Automatic taring and measurement
- mg-level precision

### 🤖 Automated Plate Handling
- Motorized loading/unloading
- Collision avoidance for different plate types
- Configurable via YAML

### 📊 Gravimetric Verification
- Measure before and after dosing
- Calculate actual dispensed amount
- Track dosing accuracy

### 🔧 Flexible Integration
- Works standalone or with CNC
- Future-ready for Opentrons
- Modular architecture

### 📝 Production-Ready
- Comprehensive error handling
- Detailed logging
- Safe shutdown procedures

---

## Documentation

| Document | Description |
|----------|-------------|
| **[Quick Start](docs/quick-start.md)** | Installation, setup, and basic usage |
| **[Python API](docs/python-api.md)** | Complete Python API reference |
| **[Architecture & Configuration](docs/architecture.md)** | System design and configuration |
| **[Examples](docs/examples.md)** | Detailed workflow examples |

---

## Examples

Pre-built example scripts in `examples/`:

```bash
# Standalone weighing
python examples/example_standalone.py

# CNC automated dosing
python examples/example_with_cnc.py

# Calibrate flow rate
python examples/example_calibration.py
```

---

## Hardware Requirements

### Core System (Required)
- Raspberry Pi 5 (or 3/4)
- Sartorius precision balance (USB serial)
- PCA9685 16-channel PWM HAT (I2C 0x40)
- 3× Servo motors (plate loader)
- 5V 5A power supply

### For Automated Solid Dosing (Optional)
- CNC controller (GRBL-compatible, USB serial)
- 1× Servo motor (gate control)
- 1× 5V relay module (motor control)
- 1× DC motor (auger/feeder)

### For Liquid Handling (Future)
- Opentrons OT-2 robot
- Network connection

---

## System Architecture

```
┌─────────────────────────────────────────────────┐
│                  MicroDoser                     │
│  (High-level orchestration & coordination)      │
└────────┬────────────────────────┬───────────────┘
         │                        │
    ┌────▼─────┐           ┌──────▼────────┐
    │  Core    │           │    Optional    │
    │Components│           │ Dosing System  │
    └────┬─────┘           └────────┬───────┘
         │                          │
    ┌────▼─────────┐         ┌──────▼────────────┐
    │  Balance     │         │  CNCDosingSystem  │
    │  (Sartorius) │         │  (CNC + Solid     │
    ├──────────────┤         │   Doser)          │
    │ Plate Loader │         └───────────────────┘
    │ (PCA9685 +   │         
    │  3 Servos)   │         
    └──────────────┘         
```

---

## Project Structure

```
dose_every_well/
├── docs/                       # Documentation
│   ├── getting-started.md      # Installation & setup
│   ├── api-reference.md        # Complete API docs
│   ├── configuration.md        # Config guide
│   ├── examples.md             # Example workflows
│   └── architecture.md         # System design
│
├── examples/                   # Example scripts
│   ├── example_standalone.py   # Weighing station
│   ├── example_with_cnc.py     # Automated dosing
│   └── example_calibration.py  # Calibration
│
├── src/dose_every_well/        # Main package
│   ├── core.py                 # MicroDoser class
│   ├── dosing_system.py        # CNCDosingSystem
│   ├── config/                 # YAML configs
│   │   ├── standalone.yaml
│   │   └── with_cnc.yaml
│   ├── cnc_controller.py       # CNC control
│   ├── plate_loader.py         # Plate loader
│   ├── solid_doser.py          # Solid doser
│   └── sartorius_balance.py    # Balance
│
└── README.md                   # This file
```

---

## Use Cases

### 1. Manual Dosing + Automated Weighing
- User doses materials by hand
- System handles plate loading and weighing
- Ideal for method development

### 2. Fully Automated Solid Dosing
- CNC positions over wells
- Solid doser dispenses material
- Balance verifies each dose
- Ideal for high-throughput workflows

### 3. Liquid + Solid Workflows (Future)
- Opentrons handles liquids
- MicroDoser verifies masses
- Combined liquid/solid experiments

---

## Platform Support

| Platform | Status | Notes |
|----------|--------|-------|
| Raspberry Pi 5 | ✅ Tested | Requires `rpi-lgpio` |
| Raspberry Pi 3/4 | ✅ Supported | Standard GPIO |
| Linux (Ubuntu/Debian) | ✅ Supported | For CNC control only |
| macOS / Windows | ⚠️ Limited | CNC control only |

---

## Safety

**Important Safety Practices:**

- ✅ Test in simulation before hardware execution
- ✅ Verify movement boundaries match your machine
- ✅ Keep emergency stop accessible
- ✅ Clear work area before automated runs
- ✅ Monitor first runs carefully

---

## Contributing

Contributions welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

For major changes, open an issue first to discuss.

---

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## Citation

If you use this package in your research, please cite:

```bibtex
@software{dose_every_well,
  author = {Cao, Yang},
  title = {Dose Every Well: Precision Dosing and Weighing System},
  year = {2025},
  url = {https://github.com/AccelerationConsortium/dose_every_well}
}
```

---

## Author

**Yang Cao**  
Email: yangcyril.cao@utoronto.ca

---

## Acknowledgments

Built for laboratory automation workflows with a focus on microplate gravimetric applications.

---

**Need help?** Check the [documentation](docs/) or open an issue on GitHub.

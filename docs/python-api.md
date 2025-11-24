# MicroDoser - Precision Weighing and Plate Handling System

## Overview

`MicroDoser` is a high-level orchestration system for precision gravimetric workflows. It combines automated plate handling, precision weighing, and optional external dosing systems (CNC, Opentrons, or manual).

### Core Philosophy

**MicroDoser = Weighing Station + Plate Handler**

The system is built around two required components:
- ✅ **PlateLoader**: Automated plate loading/unloading
- ✅ **Balance**: Precision gravimetric measurement (Sartorius)

And one optional component:
- ⚙️ **DosingSystem**: External dosing capability (CNC with solid doser, Opentrons with pipettes, or manual)

## Architecture

```
MicroDoser (Core System)
├── PlateLoader (Required)
│   └── Automated plate handling
├── Balance (Required)
│   └── Sartorius precision balance
└── DosingSystem (Optional)
    ├── CNCDosingSystem (solid dosing)
    ├── OpentronsDosingSystem (liquid dosing - future)
    └── ManualDosingSystem (user-controlled)
```

## Quick Start

### 1. Standalone Mode (Weighing Station Only)

```python
from dose_every_well import MicroDoser

# Initialize without dosing system
doser = MicroDoser(
    balance_port='/dev/ttyUSB1',
    plate_type='shallow_plate'
)

# Load plate and weigh
doser.load_plate()

# Manual dosing workflow
input("Manually add material to well A1, press Enter...")
mass_a1 = doser.read_balance()
print(f"Well A1: {mass_a1:.4f} g")

input("Manually add material to well A2, press Enter...")
mass_a2 = doser.read_balance()
print(f"Well A2: {mass_a2:.4f} g")

doser.unload_plate()
doser.shutdown()
```

### 2. With CNC Solid Dosing

```python
from dose_every_well import MicroDoser, CNCDosingSystem

# Initialize CNC dosing system
dosing_system = CNCDosingSystem(
    cnc_port='/dev/ttyUSB0',
    doser_params={
        'i2c_address': 0x40,
        'motor_gpio_pin': 17,
        'frequency': 50
    }
)
dosing_system.initialize()

# Initialize MicroDoser with dosing system
doser = MicroDoser(
    balance_port='/dev/ttyUSB1',
    plate_type='shallow_plate',
    dosing_system=dosing_system
)

# Automated dosing workflow
doser.load_plate()

# Dose single well with verification
result = doser.dose_to_well('A1', target_mg=5.0)
print(f"Well A1:")
print(f"  Target: {result['target_mg']:.2f} mg")
print(f"  Actual: {result['actual_mg']:.2f} mg")
print(f"  Error:  {result['error_mg']:.2f} mg ({result['error_mg']/result['target_mg']*100:.1f}%)")

# Dose multiple wells
well_targets = {
    'A1': 5.0,
    'A2': 3.0,
    'A3': 7.0,
    'B1': 4.5
}
results = doser.dose_plate(well_targets, verify=True)

for well, result in results.items():
    print(f"{well}: {result['actual_mg']:.2f} mg (error: {result['error_mg']:.2f} mg)")

doser.unload_plate()
doser.shutdown()
```

## API Reference

### MicroDoser

Main class for the weighing and dosing system.

#### `__init__(balance_port, plate_type, plate_loader_params=None, dosing_system=None)`

Initialize MicroDoser system.

**Parameters:**
- `balance_port` (str): Serial port for balance (e.g., '/dev/ttyUSB1')
- `plate_type` (str): Plate configuration ('shallow_plate', 'deep_well', etc.)
- `plate_loader_params` (dict, optional): Additional parameters for PlateLoader
- `dosing_system` (optional): External dosing system instance

#### `load_plate()`

Load plate onto balance and automatically tare.

#### `unload_plate()`

Unload plate from balance.

#### `read_balance() -> float`

Read current balance value in grams.

#### `tare_balance()`

Tare (zero) the balance.

#### `weigh_well(well: str) -> float`

Position at well (if dosing system available) and read mass.

**Parameters:**
- `well` (str): Well identifier (e.g., 'A1')

**Returns:** Mass in grams

#### `dose_to_well(well, target_mg, verify=True, **kwargs) -> dict`

Dose material to a well with gravimetric feedback.

**Parameters:**
- `well` (str): Well identifier
- `target_mg` (float): Target mass in milligrams
- `verify` (bool): Whether to verify with balance
- `**kwargs`: Additional parameters for dosing system

**Returns:** Dictionary with dosing results:
```python
{
    'well': 'A1',
    'target_mg': 5.0,
    'initial_mg': 0.0,
    'final_mg': 5.2,
    'actual_mg': 5.2,
    'error_mg': 0.2
}
```

#### `dose_plate(well_targets: dict, verify=True) -> dict`

Dose multiple wells in sequence.

**Parameters:**
- `well_targets` (dict): Mapping of well IDs to target masses
  ```python
  {'A1': 5.0, 'A2': 3.0, 'B1': 7.0}
  ```
- `verify` (bool): Whether to verify each dose

**Returns:** Dictionary mapping well IDs to result dictionaries

#### `shutdown()`

Safely shutdown all components.

### CNCDosingSystem

CNC-based solid dosing integration.

#### `__init__(cnc_port, doser_params=None, well_spacing=9.0, plate_origin=(0,0))`

Initialize CNC dosing system.

**Parameters:**
- `cnc_port` (str): Serial port for CNC
- `doser_params` (dict): Parameters for SolidDoser
- `well_spacing` (float): Well spacing in mm (default 9.0 for 96-well)
- `plate_origin` (tuple): XY coordinates of well A1

#### `initialize()`

Initialize and home CNC and doser hardware.

#### `position_at_well(well: str)`

Move CNC to position over specified well.

#### `dose_to_well(well, target_mg, gate_position=None, **kwargs)`

Position and dispense solid material.

#### `calibrate_flow_rate(duration=5.0, gate_position=35)`

Interactive calibration to measure dispense flow rate.

## Configuration Files

Example configurations are provided in `config/`:

- `standalone.yaml`: Balance + loader only
- `with_cnc.yaml`: Full automation with CNC dosing

See `config/README.md` for details.

## Hardware Setup

### Required Hardware
1. **Sartorius Balance** (connected via USB serial)
2. **Raspberry Pi 5** with PCA9685 HAT
3. **PlateLoader** (servos on PCA9685 channels 3, 6, 9)

### Optional Hardware (for CNC dosing)
4. **CNC Controller** (connected via USB serial)
5. **SolidDoser** (servo on PCA9685 channel 0, relay on GPIO17)

### Port Assignment
- `/dev/ttyUSB0`: CNC controller
- `/dev/ttyUSB1`: Sartorius balance
- I2C bus 1, address 0x40: PCA9685 HAT

## Calibration

### CNC Positioning Calibration

1. Ensure CNC home position is set correctly
2. Manually position CNC over well A1
3. Record coordinates and update `plate_origin` in config

### Flow Rate Calibration

```python
from dose_every_well import CNCDosingSystem

dosing = CNCDosingSystem(cnc_port='/dev/ttyUSB0')
dosing.initialize()

# Run calibration with known duration
dosing.calibrate_flow_rate(duration=5.0, gate_position=35)

# Weigh dispensed material
measured_mg = 10.5  # Example: measured mass

# Calculate flow rate
flow_rate = measured_mg / 5.0  # mg/s
print(f"Flow rate: {flow_rate:.2f} mg/s")

# Update config or code with measured flow rate
```

## Advanced Usage

### Custom Dosing Workflows

```python
# Iterative dosing to hit target
target_mg = 5.0
tolerance_mg = 0.2

doser.tare_balance()
actual_mg = 0.0

while abs(actual_mg - target_mg) > tolerance_mg:
    remaining_mg = target_mg - actual_mg
    doser.dosing_system.dose_to_well('A1', target_mg=remaining_mg * 0.8)  # Conservative
    actual_mg = doser.read_balance() * 1000  # g to mg
    print(f"Actual: {actual_mg:.2f} mg, Target: {target_mg:.2f} mg")

print(f"Final: {actual_mg:.2f} mg (error: {actual_mg - target_mg:.2f} mg)")
```

### Integration with Opentrons (Future)

```python
from dose_every_well import MicroDoser
from dose_every_well.dosing_systems import OpentronsDosingSystem

# Opentrons handles liquid dosing
opentrons = OpentronsDosingSystem(robot_ip='192.168.1.100')
opentrons.initialize()

doser = MicroDoser(
    balance_port='/dev/ttyUSB1',
    plate_type='shallow_plate',
    dosing_system=opentrons
)

# Use Opentrons for liquid, MicroDoser for weighing
doser.load_plate()
result = doser.dose_to_well('A1', target_ul=100.0)
doser.unload_plate()
```

## Backward Compatibility

Legacy imports still work:

```python
# Old way (still works)
from dose_every_well import CNC_Controller, PlateLoader, SolidDoser

cnc = CNC_Controller(port='/dev/ttyUSB0')
loader = PlateLoader(plate_type='shallow_plate')
doser = SolidDoser(i2c_address=0x40)

# Use individually...
```

## Troubleshooting

### Balance Not Responding
- Check serial port: `ls /dev/ttyUSB*`
- Verify balance is powered on
- Test connection: `python -m serial.tools.miniterm /dev/ttyUSB1`

### CNC Not Moving
- Check CNC serial port
- Verify CNC is homed
- Test with `cnc_controller.py` directly

### Solid Doser Not Dispensing
- Check I2C connection: `i2cdetect -y 1`
- Verify GPIO permissions: `sudo usermod -a -G gpio $USER`
- Check motor power supply

### Plate Loader Collision
- Verify plate type is correct
- Check servo calibration in `plate_settings.yaml`
- Run `loader.print_collision_info()`

## Support

For issues, see:
- Hardware setup: Check wiring and power
- Software errors: Check logs and error messages
- Calibration: Run calibration routines before first use


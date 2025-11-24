# MicroDoser Configuration Files

This directory contains example configuration files for different MicroDoser operating modes.

## Available Configurations

### 1. `standalone.yaml`
**Mode**: Balance + Plate Loader only (no automated dosing)

**Use case**: 
- Manual dosing workflows
- User dispenses material by hand
- System handles plate loading and weighing

**Example**:
```python
from dose_every_well import MicroDoser

doser = MicroDoser(
    balance_port='/dev/ttyUSB1',
    plate_type='shallow_plate'
)

doser.load_plate()
input("Manually dose to well A1, press Enter...")
mass = doser.weigh_well('A1')
print(f"Dispensed: {mass:.3f} g")
doser.unload_plate()
```

### 2. `with_cnc.yaml`
**Mode**: Balance + Plate Loader + CNC Dosing System

**Use case**:
- Fully automated solid dispensing
- CNC positions doser over wells
- Gravimetric verification of each dose

**Example**:
```python
from dose_every_well import MicroDoser, CNCDosingSystem

# Initialize CNC dosing system
dosing_system = CNCDosingSystem(
    cnc_port='/dev/ttyUSB0',
    doser_params={'i2c_address': 0x40, 'motor_gpio_pin': 17}
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
result = doser.dose_to_well('A1', target_mg=5.0)
print(f"Target: {result['target_mg']:.2f} mg")
print(f"Actual: {result['actual_mg']:.2f} mg")
print(f"Error: {result['error_mg']:.2f} mg")
doser.unload_plate()
```

## Configuration Parameters

### Balance
- `port`: Serial port for balance (e.g., `/dev/ttyUSB1`)
- `type`: Balance type (currently only `SartoriusBalance`)

### Plate Loader
- `plate_type`: Plate configuration (`shallow_plate`, `deep_well`, etc.)
- `i2c_address`: PCA9685 I2C address (default: `0x40`)
- `frequency`: PWM frequency in Hz (default: `50`)

### CNC Dosing System
- `cnc_port`: Serial port for CNC controller (e.g., `/dev/ttyUSB0`)
- `doser_params`:
  - `i2c_address`: PCA9685 address for servo control
  - `motor_gpio_pin`: GPIO pin for motor relay
  - `frequency`: PWM frequency
- `well_spacing`: Distance between wells in mm (default: `9.0` for 96-well)
- `plate_origin`: XY coordinates of well A1 in mm
- `flow_rate_mg_per_s`: Calibrated flow rate (run calibration to determine)

### Workflow
- `auto_tare_on_load`: Automatically tare balance when plate is loaded
- `verify_mass_after_dose`: Use balance to verify each dose
- `use_iterative_dosing`: (Future) Iteratively dose to hit target
- `max_iterations`: Maximum dosing iterations
- `tolerance_mg`: Acceptable error in mg

## Creating Custom Configurations

Copy one of the example files and modify parameters for your setup:

```bash
cp config/with_cnc.yaml config/my_setup.yaml
# Edit my_setup.yaml with your hardware parameters
```

## Hardware Port Assignment

Common setup:
- `/dev/ttyUSB0`: CNC controller
- `/dev/ttyUSB1`: Sartorius balance
- I2C bus 1, address `0x40`: PCA9685 HAT (shared by plate loader and solid doser)

If your ports are different, update the config file accordingly.

## Calibration

Before first use with CNC dosing:

1. **CNC Positioning**: Ensure well A1 position is correctly set in CNC settings
2. **Flow Rate**: Run calibration to measure actual flow rate:
   ```python
   dosing_system.calibrate_flow_rate(duration=5.0)
   # Weigh dispensed material and update flow_rate_mg_per_s in config
   ```

## Future Configuration Options

- `with_opentrons.yaml`: Opentrons integration (planned)
- Support for multiple dosing systems simultaneously
- Advanced dosing strategies (iterative, feedback-controlled)


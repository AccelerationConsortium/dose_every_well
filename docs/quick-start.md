# Quick Start Guide

Complete guide to installing, configuring, and using MicroDoser.

---

## Installation

### Prerequisites

**Hardware (Required):**
- **Raspberry Pi 5** (primary target platform)
- Sartorius balance (USB serial connection)
- PCA9685 PWM HAT (I2C address 0x40)
- 3× Servo motors (plate loader)
- 5V 5A power supply

**Optional Hardware:**
- CNC controller (USB serial) for automated solid dosing
- 1× Servo motor (gate control)
- 1× 5V relay module (motor control)
- 1× DC motor (auger/feeder)

**Software:**
- Raspberry Pi OS (64-bit recommended)
- Python 3.8+
- pip package manager

### Install on Raspberry Pi 5

```bash
# Clone repository
git clone https://github.com/AccelerationConsortium/dose_every_well.git
cd dose_every_well

# Install (includes all Raspberry Pi dependencies by default)
pip install -e .

# Enable I2C and serial interfaces
sudo raspi-config
# Navigate to: Interface Options -> Enable I2C
# Navigate to: Interface Options -> Enable Serial Port

# Add user to required groups
sudo usermod -a -G dialout,gpio,i2c $USER
# Log out and back in for changes to take effect
```

### Install on Other Platforms (Development Only)

For development/testing on non-Raspberry Pi systems:

```bash
# Same installation command
pip install -e .

# Note: Hardware features will not work without Raspberry Pi hardware
# Some dependencies may fail to install on non-ARM platforms (this is expected)
```

### Verify Installation

```bash
# Test imports
python -c "from dose_every_well import MicroDoser, CNCDosingSystem; print('✓ Import successful')"
```

---

## Basic Usage

### 1. Standalone Weighing Station

Manual dosing with automated weighing:

```python
from dose_every_well import MicroDoser

# Initialize
doser = MicroDoser(
    balance_port='/dev/ttyUSB1',
    plate_type='shallow_plate'
)

# Use
doser.load_plate()
input("Add material to well A1, press Enter...")
mass = doser.read_balance()
print(f"A1: {mass * 1000:.2f} mg")
doser.unload_plate()
doser.shutdown()
```

### 2. With CNC Automated Dosing

Full automation with verification:

```python
from dose_every_well import MicroDoser, CNCDosingSystem

# Initialize CNC system
dosing_system = CNCDosingSystem(cnc_port='/dev/ttyUSB0')
dosing_system.initialize()

# Initialize MicroDoser
doser = MicroDoser(
    balance_port='/dev/ttyUSB1',
    plate_type='shallow_plate',
    dosing_system=dosing_system
)

# Automated workflow
doser.load_plate()
result = doser.dose_to_well('A1', target_mg=5.0)
print(f"Target: {result['target_mg']:.2f} mg")
print(f"Actual: {result['actual_mg']:.2f} mg")
print(f"Error:  {result['error_mg']:.2f} mg")
doser.unload_plate()
doser.shutdown()
```

### 3. Batch Dosing

```python
# Define targets
well_targets = {
    'A1': 5.0,   # mg
    'A2': 3.0,
    'A3': 7.0
}

# Dose entire batch
doser.load_plate()
results = doser.dose_plate(well_targets, verify=True)

# Print summary
for well, result in results.items():
    print(f"{well}: {result['actual_mg']:.2f} mg (error: {result['error_mg']:.2f} mg)")

doser.unload_plate()
doser.shutdown()
```

---

## Run Examples

Pre-built example scripts:

```bash
# Standalone weighing station
python examples/example_standalone.py

# CNC automated dosing
python examples/example_with_cnc.py

# Calibrate flow rate
python examples/example_calibration.py
```

---

## Hardware Setup

### Serial Port Assignment

Find your device ports:

```bash
# List all USB serial devices
ls /dev/ttyUSB*

# Typical setup:
# /dev/ttyUSB0 - CNC controller
# /dev/ttyUSB1 - Sartorius balance
```

### I2C Check

Verify PCA9685 HAT is detected:

```bash
# Check I2C devices
i2cdetect -y 1

# Should show 0x40 for PCA9685
```

### Permissions (Linux/Raspberry Pi)

```bash
# Add user to required groups
sudo usermod -a -G dialout $USER   # Serial port access
sudo usermod -a -G gpio $USER      # GPIO access
sudo usermod -a -G i2c $USER       # I2C access

# Log out and back in for changes to take effect
```

---

## First-Time Calibration

### 1. CNC Positioning

```python
from dose_every_well import CNCDosingSystem

dosing = CNCDosingSystem(cnc_port='/dev/ttyUSB0')
dosing.initialize()

# Manually jog CNC to well A1 position
# Record coordinates and update plate_origin in config
```

### 2. Flow Rate Calibration

```bash
# Run calibration script
python examples/example_calibration.py

# Follow prompts:
# 1. Place container on balance
# 2. Tare balance
# 3. Dispense for known duration
# 4. Weigh result
# 5. Calculate flow rate (mg/s)
```

Update flow rate in your code:

```python
dosing_system = CNCDosingSystem(
    cnc_port='/dev/ttyUSB0',
    # Update flow_rate_mg_per_s after calibration
)
```

---

## API Cheat Sheet

### MicroDoser

```python
# Initialization
doser = MicroDoser(
    balance_port='/dev/ttyUSB1',
    plate_type='shallow_plate',
    dosing_system=None  # Optional
)

# Core methods
doser.load_plate()                          # Load and tare
doser.unload_plate()                        # Unload plate
doser.read_balance()                        # Read mass (g)
doser.tare_balance()                        # Zero balance
doser.dose_to_well('A1', target_mg=5.0)    # Dose with verification
doser.dose_plate({...})                     # Batch dosing
doser.get_status()                          # System status
doser.shutdown()                            # Safe shutdown
```

### CNCDosingSystem

```python
# Initialization
dosing = CNCDosingSystem(
    cnc_port='/dev/ttyUSB0',
    doser_params={'i2c_address': 0x40, 'motor_gpio_pin': 17}
)

# Core methods
dosing.initialize()                         # Connect and home
dosing.position_at_well('A1')              # Move to well
dosing.dose_to_well('A1', target_mg=5.0)   # Dispense
dosing.calibrate_flow_rate()               # Calibration
dosing.home()                              # Return home
dosing.shutdown()                          # Safe shutdown
```

---

## Troubleshooting

### Balance Not Found

```bash
# Check connection
ls /dev/ttyUSB*

# Test manually
python -m serial.tools.miniterm /dev/ttyUSB1 9600
```

### CNC Not Responding

```bash
# Check port
ls /dev/ttyUSB*

# Test connection
python -c "from dose_every_well import CNC_Controller; c = CNC_Controller('/dev/ttyUSB0'); print(c.read_coordinates())"
```

### I2C Not Working

```bash
# Enable I2C
sudo raspi-config
# Interface Options -> I2C -> Enable

# Check devices
i2cdetect -y 1
```

### Permission Denied

```bash
# Check current groups
groups

# Should see: dialout, gpio, i2c
# If not, run the usermod commands above and log out/in
```

---

## Next Steps

- Read [Python API](python-api.md) for complete API documentation
- See [Examples](examples.md) for detailed workflows
- Check [Architecture](architecture.md) for system design and configuration
- Create your own workflows based on the examples

---

## Support

- **Documentation**: See `docs/` folder
- **Examples**: See `examples/` folder
- **Issues**: Open on GitHub
- **Email**: yangcyril.cao@utoronto.ca

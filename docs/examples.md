# MicroDoser Examples

This directory contains example scripts demonstrating different MicroDoser usage patterns.

## Examples

### 1. `example_standalone.py`
**Standalone weighing station mode** - No automated dosing

Shows how to use MicroDoser as a weighing station with automated plate handling. User manually doses material and the system weighs each well.

**Run:**
```bash
python examples/example_standalone.py
```

**Hardware required:**
- Sartorius balance
- Plate loader

### 2. `example_with_cnc.py`
**Automated solid dosing mode** - CNC + solid doser

Demonstrates fully automated solid dispensing workflow with gravimetric verification. The system loads plate, doses to multiple wells, verifies each dose, and generates a summary report.

**Run:**
```bash
python examples/example_with_cnc.py
```

**Hardware required:**
- Sartorius balance
- Plate loader
- CNC controller
- Solid doser

### 3. `example_calibration.py`
**Flow rate calibration** - Calibrate solid doser

Interactive script to calibrate the solid doser flow rate. Dispenses for a known duration, prompts user to weigh result, calculates flow rate, and optionally runs verification.

**Run:**
```bash
python examples/example_calibration.py
```

**Hardware required:**
- CNC controller
- Solid doser
- External balance (for weighing calibration samples)

## Before Running Examples

### 1. Hardware Setup
- Connect Sartorius balance to `/dev/ttyUSB1`
- Connect CNC controller to `/dev/ttyUSB0` (if using CNC examples)
- Ensure PCA9685 HAT is on I2C bus 1, address 0x40
- Verify GPIO permissions: `sudo usermod -a -G gpio $USER`

### 2. Install Dependencies
```bash
pip install matterlab_balances pyserial smbus2 RPi.GPIO adafruit-circuitpython-pca9685
```

### 3. Check Connections
```bash
# List serial ports
ls /dev/ttyUSB*

# Check I2C devices
i2cdetect -y 1

# Test balance connection
python -m serial.tools.miniterm /dev/ttyUSB1
```

### 4. Calibrate (First Time Only)
Before using CNC dosing, calibrate the flow rate:
```bash
python examples/example_calibration.py
```

## Modifying Examples

All examples can be modified for your specific setup:

### Change Serial Ports
```python
doser = MicroDoser(
    balance_port='/dev/ttyUSB2',  # Your balance port
    # ...
)

dosing_system = CNCDosingSystem(
    cnc_port='/dev/ttyACM0',  # Your CNC port
    # ...
)
```

### Change Plate Type
```python
doser = MicroDoser(
    balance_port='/dev/ttyUSB1',
    plate_type='deep_well',  # or 'custom_384_well', etc.
)
```

### Adjust Well Targets
```python
well_targets = {
    'A1': 10.0,  # 10 mg
    'A2': 15.0,  # 15 mg
    'B1': 5.0,   # 5 mg
    # ... add more wells
}
results = doser.dose_plate(well_targets)
```

## Creating Your Own Scripts

Template for custom workflows:

```python
#!/usr/bin/env python3
import logging
from dose_every_well import MicroDoser, CNCDosingSystem

logging.basicConfig(level=logging.INFO)

def main():
    # Initialize components
    dosing_system = CNCDosingSystem(cnc_port='/dev/ttyUSB0')
    dosing_system.initialize()
    
    doser = MicroDoser(
        balance_port='/dev/ttyUSB1',
        plate_type='shallow_plate',
        dosing_system=dosing_system
    )
    
    try:
        # Your workflow here
        doser.load_plate()
        
        # ... do work ...
        
        doser.unload_plate()
        
    finally:
        doser.shutdown()

if __name__ == "__main__":
    main()
```

## Troubleshooting

### Balance Not Found
```bash
# List all USB serial devices
ls -l /dev/serial/by-id/

# Try alternative port
python -c "from serial.tools import list_ports; [print(p) for p in list_ports.comports()]"
```

### CNC Not Responding
```bash
# Test CNC directly
python -c "from dose_every_well import CNC_Controller; cnc = CNC_Controller('/dev/ttyUSB0'); cnc.home()"
```

### Permission Denied
```bash
# Add user to dialout group (for serial ports)
sudo usermod -a -G dialout $USER

# Add user to gpio group (for GPIO pins)
sudo usermod -a -G gpio $USER

# Log out and back in for changes to take effect
```

### I2C Not Working
```bash
# Enable I2C
sudo raspi-config
# Interface Options -> I2C -> Enable

# Test I2C
i2cdetect -y 1
# Should show 0x40 for PCA9685
```

## Next Steps

After running the examples:
1. Calibrate your system (example_calibration.py)
2. Create custom workflows for your experiments
3. Save configurations in config/ directory
4. Add error handling and logging for production use


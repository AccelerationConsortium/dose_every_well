# Architecture & Configuration

System design, implementation details, and configuration guide for MicroDoser.

---

## Table of Contents

- [Architecture Overview](#architecture-overview)
- [Design Philosophy](#design-philosophy)
- [Component Breakdown](#component-breakdown)
- [Configuration](#configuration)
- [Extension Points](#extension-points)

---

## Architecture Overview

### Core Principle

```
MicroDoser = Weighing Station (Balance + Plate Loader) + Optional Dosing System
```

### System Diagram

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

### Repository Structure

```
dose_every_well/
├── src/dose_every_well/
│   ├── core.py                 # MicroDoser main class
│   ├── dosing_system.py        # CNCDosingSystem integration
│   ├── config/                 # YAML configurations
│   │   ├── standalone.yaml
│   │   └── with_cnc.yaml
│   ├── cnc_controller.py       # CNC control (legacy)
│   ├── plate_loader.py         # Plate loader (legacy)
│   ├── solid_doser.py          # Solid doser (legacy)
│   ├── cnc_settings.yaml       # CNC machine configs
│   └── plate_settings.yaml     # Plate loader configs
│
├── docs/                       # Documentation
├── examples/                   # Example scripts
└── README.md                   # Project overview
```

---

## Design Philosophy

### 1. Minimal Changes to Existing Code

- All existing files remain untouched
- New functionality built on top of existing classes
- Backward compatibility maintained

### 2. Modular Architecture

- Tools are integrated into dosing systems
- `CNCDosingSystem` combines CNC + solid doser
- Each dosing system is self-contained

### 3. Optional Components

- Core components (Balance + Loader) always present
- Dosing system is optional
- Easy to add new dosing systems (e.g., Opentrons)

### 4. Configuration-Driven

- YAML configs for different setups
- Easy to switch between configurations
- Hardware parameters externalized

---

## Component Breakdown

### MicroDoser (core.py)

**Purpose**: High-level orchestrator for weighing and dosing workflows

**Responsibilities**:
- Balance operations (weighing, taring)
- Plate loading/unloading coordination
- Integration with optional dosing systems
- Gravimetric verification
- Error handling and cleanup

**Key Methods**:
```python
load_plate()           # Load and tare
read_balance()         # Read mass
dose_to_well()         # Dose with verification
dose_plate()           # Batch dosing
shutdown()             # Safe shutdown
```

### CNCDosingSystem (dosing_system.py)

**Purpose**: Integrate CNC positioning with solid doser

**Responsibilities**:
- CNC positioning control
- Solid doser hardware control
- Well coordinate calculation
- Flow rate management
- Calibration utilities

**Key Methods**:
```python
initialize()              # Connect and home
position_at_well()        # Move to well
dose_to_well()            # Position and dispense
calibrate_flow_rate()     # Calibration
```

### Core Components

#### Balance (Sartorius)
- Precision gravimetric measurement
- Serial communication (USB)
- Tare and weigh operations

#### Plate Loader
- 3× Servo motors (PCA9685)
- Automated plate loading/unloading
- Collision avoidance by plate type

#### Solid Doser
- 1× Servo motor (gate control)
- 1× DC motor via relay (auger)
- Variable flow control

---

## Configuration

### Configuration Files

#### 1. Plate Loader Configuration

**Location**: `src/dose_every_well/plate_settings.yaml`

```yaml
# Servo channel assignments on PCA9685
servo_channels:
  plate_lift_1: 3      # First plate lift servo
  plate_lift_2: 6      # Second plate lift servo (synchronized)
  lid_servo: 9         # Lid open/close servo

# Servo angle limits
servo_limits:
  plate_down_angle: 90     # Plate fully lowered
  plate_up_angle: -90      # Plate fully raised
  lid_closed_angle: 178    # Lid closed
  lid_open_angle: 32       # Lid open

# Movement parameters
movement:
  default_move_speed: 20    # Degrees per step
  default_move_delay: 0.05  # Seconds between steps

# Plate types with collision avoidance
plate_types:
  shallow_plate:
    description: "Standard 96-well plates"
    plate_safe_angle: 50
    lid_safe_angle: 40
  
  deep_well:
    description: "Deep-well plates with extra clearance"
    plate_safe_angle: 40
    lid_safe_angle: 50

# PWM controller settings
pwm_controller:
  i2c_address: 0x40
  frequency: 50

# Servo pulse width (microseconds)
servo_pulse_width:
  min_pulse: 500
  max_pulse: 2500
```

#### 2. CNC Configuration

**Location**: `src/dose_every_well/cnc_settings.yaml`

```yaml
machines:
  Genmitsu 4040 PRO:
    controller:
      baud_rate: 115200
      timeout: 5
      x_low_bound: 0
      x_high_bound: 400
      y_low_bound: 0
      y_high_bound: 400
      z_low_bound: 0
      z_high_bound: 75
      step_size: 1.0  # mm per step
```

#### 3. MicroDoser Configuration

**Location**: `src/dose_every_well/config/with_cnc.yaml`

```yaml
# Core components (required)
balance:
  port: /dev/ttyUSB1
  type: SartoriusBalance

plate_loader:
  plate_type: shallow_plate
  i2c_address: 0x40
  frequency: 50

# CNC dosing system configuration
dosing_system:
  type: CNCDosingSystem
  params:
    cnc_port: /dev/ttyUSB0
    
    # Solid doser hardware parameters
    doser_params:
      i2c_address: 0x40
      motor_gpio_pin: 17
      frequency: 50
    
    # Well plate geometry
    well_spacing: 9.0  # mm (standard for 96-well plates)
    plate_origin: [0.0, 0.0]  # XY coordinates of well A1
    
    # Flow rate calibration
    flow_rate_mg_per_s: 2.0  # Update after calibration

# Workflow settings
workflow:
  auto_tare_on_load: true
  verify_mass_after_dose: true
```

### Hardware Configuration

#### I2C Address Setup

The PCA9685 HAT typically uses address `0x40`:

```bash
# Check I2C devices
i2cdetect -y 1

# Should show 0x40 for PCA9685
```

To change I2C address:
- Solder jumpers on PCA9685 board (A0-A5)
- Update `i2c_address` in config files

#### GPIO Pin Assignment

| Component | Pin | Function |
|-----------|-----|----------|
| Solid Doser Motor | GPIO 17 | Relay control |
| I2C SDA | GPIO 2 | I2C data |
| I2C SCL | GPIO 3 | I2C clock |

#### Serial Port Configuration

```bash
# Linux/Raspberry Pi - list ports
ls /dev/ttyUSB* /dev/ttyACM*

# Common assignments:
# /dev/ttyUSB0 - CNC controller
# /dev/ttyUSB1 - Sartorius balance
```

### Calibration Parameters

#### Flow Rate Calibration

After running calibration:

```python
# Update in code
dosing_system = CNCDosingSystem(
    cnc_port='/dev/ttyUSB0',
    # ...
)

# Modify _calculate_duration() method:
def _calculate_duration(self, target_mg: float) -> float:
    flow_rate = 2.5  # YOUR CALIBRATED VALUE (mg/s)
    return target_mg / flow_rate
```

Or update in YAML:

```yaml
dosing_system:
  params:
    flow_rate_mg_per_s: 2.5  # YOUR CALIBRATED VALUE
```

#### Well Plate Geometry

- **96-well plates**: 9.0 mm spacing
- **384-well plates**: 4.5 mm spacing

Update `well_spacing` in config.

#### Plate Origin

The `plate_origin` is the XYZ coordinates of well A1:

```python
dosing_system = CNCDosingSystem(
    cnc_port='/dev/ttyUSB0',
    plate_origin=(50.0, 30.0)  # X=50mm, Y=30mm from CNC home
)
```

### Custom Plate Types

Add to `plate_settings.yaml`:

```yaml
plate_types:
  my_custom_plate:
    description: "My custom plate design"
    plate_safe_angle: 45
    lid_safe_angle: 45
```

Use in code:

```python
doser = MicroDoser(
    balance_port='/dev/ttyUSB1',
    plate_type='my_custom_plate'
)
```

---

## Extension Points

### Adding New Dosing Systems

To add a new dosing system (e.g., Opentrons):

1. **Create new dosing system class**:

```python
# dosing_system_opentrons.py
class OpentronsDosingSystem:
    def __init__(self, robot_ip: str):
        self.robot_ip = robot_ip
        self.protocol = None
    
    def initialize(self):
        # Connect to Opentrons
        pass
    
    def position_at_well(self, well: str):
        # Move pipette to well
        pass
    
    def dose_to_well(self, well: str, target_ul: float):
        # Dispense liquid
        pass
    
    def shutdown(self):
        # Cleanup
        pass
```

2. **Use with MicroDoser**:

```python
from dose_every_well import MicroDoser
from dose_every_well.dosing_system_opentrons import OpentronsDosingSystem

opentrons = OpentronsDosingSystem(robot_ip='192.168.1.100')
opentrons.initialize()

doser = MicroDoser(
    balance_port='/dev/ttyUSB1',
    plate_type='shallow_plate',
    dosing_system=opentrons
)
```

### Adding Web API Layer

See separate guide: [web-api.md](web-api.md) (future)

### Adding New Plate Types

1. Add to `plate_settings.yaml`
2. Test collision avoidance
3. Document plate specifications

### Adding New CNC Machines

1. Add to `cnc_settings.yaml`
2. Calibrate movement boundaries
3. Test positioning accuracy

---

## Design Patterns

### 1. Composition Over Inheritance

MicroDoser composes existing components rather than inheriting:

```python
class MicroDoser:
    def __init__(self, balance, loader, dosing_system=None):
        self.balance = balance          # Composition
        self.loader = loader            # Composition
        self.dosing_system = dosing_system  # Composition
```

### 2. Dependency Injection

Components are injected, not created internally:

```python
# Good - injected
doser = MicroDoser(
    balance_port='/dev/ttyUSB1',
    dosing_system=CNCDosingSystem(...)
)

# Not: doser creates its own dosing_system internally
```

### 3. Optional Dependencies

Dosing system is optional - system degrades gracefully:

```python
# Works without dosing system
doser = MicroDoser(balance_port='/dev/ttyUSB1')
doser.load_plate()
mass = doser.read_balance()

# Works with dosing system
doser = MicroDoser(..., dosing_system=CNCDosingSystem(...))
doser.dose_to_well('A1', target_mg=5.0)
```

### 4. Configuration Over Code

Hardware parameters in YAML, not hardcoded:

```yaml
# Good - in config file
plate_origin: [50.0, 30.0]

# Not: hardcoded in Python
```

---

## Future Roadmap

### Planned Features

1. **Web API** - REST API for remote control
2. **Opentrons Integration** - Liquid handling support
3. **Iterative Dosing** - Feedback-controlled dosing to hit target
4. **Multi-tool Support** - Switch between tools dynamically
5. **Database Logging** - Store all dosing results
6. **Real-time Monitoring** - WebSocket status updates

### Extension Points Ready

- Abstract dosing system interface
- Modular architecture
- Configuration-driven design
- Clean separation of concerns

---

## Best Practices

### Configuration
- Version control your configs
- Document calibration values and dates
- Test after configuration changes
- Backup working configs before experimenting

### Development
- Test components individually before integration
- Use simulators when possible
- Log all operations for debugging
- Handle errors gracefully

### Deployment
- Calibrate before production use
- Monitor first runs carefully
- Have emergency stop accessible
- Document any customizations

---

## Troubleshooting Configuration

### Config not loading

```python
from pathlib import Path
import yaml

# Check file exists
config_path = Path("src/dose_every_well/plate_settings.yaml")
print(f"Config exists: {config_path.exists()}")

# Validate YAML syntax
with open(config_path) as f:
    config = yaml.safe_load(f)
    print("✓ Valid YAML")
```

### Wrong I2C address

```bash
# Scan for devices
i2cdetect -y 1

# Update config if device at different address
```

### Servo not moving correctly

1. Check servo channels match physical wiring
2. Verify PWM frequency (50 Hz for servos)
3. Adjust pulse width ranges if needed
4. Test individual servos directly

---

## See Also

- [Quick Start](quick-start.md) - Installation and basic usage
- [Python API](python-api.md) - Complete API reference
- [Examples](examples.md) - Usage examples

"""
dose_every_well - Precision Dosing and Weighing System

Main Components:
- MicroDoser: Core system (balance + plate loader + optional dosing)
- CNCDosingSystem: CNC-based solid dosing integration

Legacy Components (backward compatibility):
- CNC_Controller, CNC_Simulator: Direct CNC control
- PlateLoader: Direct plate loader control
- SolidDoser: Direct solid doser control
"""

# New high-level API
try:
    from .core import MicroDoser
    from .dosing_system import CNCDosingSystem
    _new_api_available = True
except (ImportError, Exception) as e:
    import warnings
    warnings.warn(f"MicroDoser API not available: {e}", UserWarning)
    _new_api_available = False

# Legacy API (backward compatibility)
from .cnc_controller import load_config, find_port, CNC_Controller, CNC_Simulator

try:
    from .plate_loader import PlateLoader
    from .solid_doser import SolidDoser
    _legacy_hardware_available = True
except (ImportError, NameError, Exception) as e:
    import warnings
    warnings.warn(f"Raspberry Pi hardware controllers not available: {e}", UserWarning)
    _legacy_hardware_available = False
    PlateLoader = None
    SolidDoser = None

# Build __all__ based on what's available
__all__ = ['load_config', 'find_port', 'CNC_Controller', 'CNC_Simulator']

if _new_api_available:
    __all__.extend(['MicroDoser', 'CNCDosingSystem'])

if _legacy_hardware_available:
    __all__.extend(['PlateLoader', 'SolidDoser'])

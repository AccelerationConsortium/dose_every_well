#!/usr/bin/env python3
"""
CNC-based solid dosing system.
Integrates CNC positioning with solid doser hardware.
"""

import logging
from typing import Optional, Tuple

from .cnc_controller import CNC_Controller
from .solid_doser import SolidDoser

logger = logging.getLogger(__name__)


class CNCDosingSystem:
    """
    CNC with solid doser for automated solid material dispensing.
    
    Combines:
    - CNC_Controller: XYZ positioning
    - SolidDoser: Solid material dispensing hardware
    
    Usage:
        dosing = CNCDosingSystem(
            cnc_port='/dev/ttyUSB0',
            doser_params={'i2c_address': 0x40, 'motor_gpio_pin': 17}
        )
        dosing.initialize()
        dosing.dose_to_well('A1', target_mg=5.0)
        dosing.shutdown()
    """
    
    def __init__(
        self,
        cnc_port: str,
        doser_params: Optional[dict] = None,
        well_spacing: float = 9.0,
        plate_origin: Tuple[float, float] = (0.0, 0.0)
    ):
        """
        Initialize CNC dosing system.
        
        Args:
            cnc_port: Serial port for CNC controller (e.g., '/dev/ttyUSB0')
            doser_params: Parameters for SolidDoser initialization
                         Default: {'i2c_address': 0x40, 'motor_gpio_pin': 17}
            well_spacing: Distance between wells in mm (default 9.0 for 96-well)
            plate_origin: XY coordinates of well A1 (default 0, 0)
        """
        self.cnc_port = cnc_port
        self.doser_params = doser_params or {
            'i2c_address': 0x40,
            'motor_gpio_pin': 17,
            'frequency': 50
        }
        self.well_spacing = well_spacing
        self.plate_origin = plate_origin
        
        self.cnc = None
        self.doser = None
        
        logger.info("CNCDosingSystem configured")
        logger.info(f"  CNC port: {cnc_port}")
        logger.info(f"  Well spacing: {well_spacing} mm")
        logger.info(f"  Plate origin: {plate_origin}")
    
    def initialize(self):
        """Initialize CNC and solid doser hardware."""
        logger.info("Initializing CNC Dosing System...")
        
        # Initialize CNC
        self.cnc = CNC_Controller(port=self.cnc_port)
        self.cnc.home()
        
        # Initialize solid doser
        self.doser = SolidDoser(**self.doser_params)
        self.doser.home()
        
        logger.info("CNC Dosing System ready")
    
    def position_at_well(self, well: str, plate_format: str = '96'):
        """
        Move CNC to position over specified well.
        
        Args:
            well: Well identifier (e.g., 'A1', 'B12')
            plate_format: Plate format ('96', '384', etc.)
        """
        x, y = self._well_to_coords(well, plate_format)
        logger.info(f"Positioning at well {well} -> ({x:.2f}, {y:.2f})")
        self.cnc.move_to(x, y)
    
    def dose_to_well(
        self,
        well: str,
        target_mg: float,
        gate_position: Optional[float] = None,
        **kwargs
    ):
        """
        Position at well and dispense solid material.
        
        Args:
            well: Well identifier (e.g., 'A1')
            target_mg: Target mass in milligrams
            gate_position: Optional gate position override
            **kwargs: Additional parameters passed to doser.dispense()
        """
        logger.info(f"Dosing {target_mg:.2f} mg to well {well}")
        
        # Position CNC
        self.position_at_well(well)
        
        # Calculate dispense duration based on target
        duration = self._calculate_duration(target_mg)
        
        # Dispense
        self.doser.dispense(duration=duration, gate_position=gate_position, **kwargs)
        
        logger.info(f"Dosing to {well} complete")
    
    def home(self):
        """Return CNC and doser to home positions."""
        logger.info("Homing CNC Dosing System...")
        if self.cnc:
            self.cnc.home()
        if self.doser:
            self.doser.home()
    
    def shutdown(self):
        """Safely shutdown CNC and doser."""
        logger.info("Shutting down CNC Dosing System...")
        if self.doser:
            self.doser.shutdown()
        if self.cnc:
            self.cnc.disconnect()
        logger.info("CNC Dosing System shutdown complete")
    
    def calibrate_flow_rate(self, duration: float = 5.0, gate_position: float = 35):
        """
        Helper to calibrate solid dispense flow rate.
        Run this with a balance to measure actual flow rate.
        
        Args:
            duration: Dispense duration in seconds
            gate_position: Gate opening position
        
        Returns:
            Instructions for user to measure and calculate flow rate
        """
        logger.info("=== Flow Rate Calibration ===")
        logger.info(f"Duration: {duration}s, Gate: {gate_position}")
        logger.info("Place container on balance and tare before starting")
        input("Press Enter to start dispensing...")
        
        self.doser.dispense(duration=duration, gate_position=gate_position)
        
        logger.info(f"Dispensing complete. Weigh the dispensed material.")
        logger.info(f"Flow rate (mg/s) = measured_mass_mg / {duration}")
        logger.info(f"Update _calculate_duration() with measured flow rate")
    
    def _well_to_coords(self, well: str, plate_format: str = '96') -> Tuple[float, float]:
        """
        Convert well ID to XY coordinates.
        
        Args:
            well: Well identifier (e.g., 'A1', 'H12')
            plate_format: Plate format ('96', '384')
        
        Returns:
            (x, y) coordinates in mm
        """
        # Parse well ID
        row = ord(well[0].upper()) - ord('A')
        col = int(well[1:]) - 1
        
        # Calculate position
        x = self.plate_origin[0] + (col * self.well_spacing)
        y = self.plate_origin[1] + (row * self.well_spacing)
        
        return (x, y)
    
    def _calculate_duration(self, target_mg: float) -> float:
        """
        Calculate dispense duration based on target mass.
        
        Args:
            target_mg: Target mass in milligrams
        
        Returns:
            Duration in seconds
        
        Note:
            This uses a default flow rate estimate.
            Use calibrate_flow_rate() to measure actual flow rate.
        """
        # Default flow rate estimate (mg/s)
        # TODO: Calibrate this value for your specific setup
        flow_rate = 2.0  # mg/s
        
        duration = target_mg / flow_rate
        
        logger.debug(f"Target {target_mg:.2f}mg @ {flow_rate:.2f}mg/s = {duration:.2f}s")
        
        return duration


if __name__ == "__main__":
    # Example usage
    print("=== CNC Dosing System Test ===")
    
    try:
        dosing = CNCDosingSystem(
            cnc_port='/dev/ttyUSB0',
            doser_params={'i2c_address': 0x40, 'motor_gpio_pin': 17}
        )
        
        dosing.initialize()
        
        # Test: dose to a single well
        choice = input("Run dose test to well A1 (Y/N)? ").strip().upper()
        if choice == 'Y':
            target = float(input("Target mass (mg): "))
            dosing.dose_to_well('A1', target_mg=target)
        
        # Calibration option
        choice = input("Run flow rate calibration (Y/N)? ").strip().upper()
        if choice == 'Y':
            dosing.calibrate_flow_rate()
        
    except KeyboardInterrupt:
        print("\n\nInterrupted by user")
    except Exception as e:
        logger.error(f"Error: {e}", exc_info=True)
    finally:
        if 'dosing' in locals():
            dosing.shutdown()


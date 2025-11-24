#!/usr/bin/env python3
"""
MicroDoser - Precision Weighing and Plate Handling Station

Core system that provides:
- Automated plate loading/unloading
- Precision gravimetric measurement
- Optional integration with external dosing systems (CNC, Opentrons, manual)

Usage:
    # Standalone mode (balance + loader only)
    from dose_every_well import MicroDoser
    
    doser = MicroDoser(
        balance_port='/dev/ttyUSB1',
        plate_type='shallow_plate'
    )
    
    doser.load_plate()
    mass = doser.weigh_well('A1')
    doser.unload_plate()
    doser.shutdown()
    
    # With CNC dosing system
    from dose_every_well import MicroDoser, CNCDosingSystem
    
    dosing_system = CNCDosingSystem(cnc_port='/dev/ttyUSB0')
    dosing_system.initialize()
    
    doser = MicroDoser(
        balance_port='/dev/ttyUSB1',
        plate_type='shallow_plate',
        dosing_system=dosing_system
    )
    
    doser.load_plate()
    result = doser.dose_to_well('A1', target_mg=5.0)
    doser.unload_plate()
    doser.shutdown()
"""

import logging
from typing import Optional, Dict, Any
from pathlib import Path

from matterlab_balances import SartoriusBalance
from .plate_loader import PlateLoader

logger = logging.getLogger(__name__)


class MicroDoser:
    """
    High-level orchestrator for precision weighing and plate handling.
    
    Core Components (Required):
    - Balance: Sartorius precision balance
    - PlateLoader: Automated plate loading/unloading mechanism
    
    Optional Components:
    - dosing_system: External dosing capability (CNC, Opentrons, manual)
    
    The MicroDoser provides a unified interface for gravimetric workflows,
    with or without automated dispensing.
    """
    
    def __init__(
        self,
        balance_port: str = '/dev/ttyUSB1',
        plate_type: str = 'shallow_plate',
        plate_loader_params: Optional[Dict] = None,
        dosing_system: Optional[Any] = None
    ):
        """
        Initialize MicroDoser system.
        
        Args:
            balance_port: Serial port for Sartorius balance
            plate_type: Type of plate for loader ('shallow_plate', 'deep_well', etc.)
            plate_loader_params: Optional parameters for PlateLoader initialization
            dosing_system: Optional external dosing system (e.g., CNCDosingSystem)
        """
        logger.info("Initializing MicroDoser...")
        
        # Initialize balance
        logger.info(f"Connecting to balance on {balance_port}...")
        self.balance = SartoriusBalance(com_port=balance_port)
        
        # Initialize plate loader
        logger.info(f"Initializing plate loader (plate type: {plate_type})...")
        loader_params = plate_loader_params or {}
        self.loader = PlateLoader(plate_type=plate_type, **loader_params)
        
        # Optional dosing system
        self.dosing_system = dosing_system
        if self.dosing_system:
            logger.info(f"Dosing system connected: {type(dosing_system).__name__}")
        else:
            logger.info("No dosing system connected (weighing station mode)")
        
        # State tracking
        self._plate_loaded = False
        
        logger.info("MicroDoser initialized successfully")
    
    def load_plate(self):
        """
        Load plate onto the balance using automated loader.
        Automatically tares balance after loading.
        """
        logger.info("Loading plate...")
        self.loader.load_plate()
        self._plate_loaded = True
        
        # Tare balance with empty plate
        logger.info("Taring balance...")
        self.balance.tare()
        
        logger.info("Plate loaded and balance tared")
    
    def unload_plate(self):
        """Unload plate from balance using automated loader."""
        logger.info("Unloading plate...")
        self.loader.unload_plate()
        self._plate_loaded = False
        logger.info("Plate unloaded")
    
    def read_balance(self) -> float:
        """
        Read current balance reading.
        
        Returns:
            Mass in grams
        """
        mass = self.balance.weigh()
        logger.debug(f"Balance reading: {mass:.4f} g")
        return mass
    
    def tare_balance(self):
        """Tare the balance (zero the reading)."""
        logger.info("Taring balance...")
        self.balance.tare()
    
    def weigh_well(self, well: str) -> float:
        """
        Weigh a specific well.
        
        If dosing_system is available, positions over the well first.
        Otherwise, prompts user to position manually.
        
        Args:
            well: Well identifier (e.g., 'A1')
        
        Returns:
            Mass reading in grams
        """
        logger.info(f"Weighing well {well}...")
        
        if self.dosing_system:
            # Use dosing system to position
            self.dosing_system.position_at_well(well)
        else:
            # Manual positioning
            print(f"\n⚠️  Position measurement device over well {well}")
            input("Press Enter when ready...")
        
        mass = self.read_balance()
        logger.info(f"Well {well}: {mass:.4f} g")
        
        return mass
    
    def dose_to_well(
        self,
        well: str,
        target_mg: float,
        verify: bool = True,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Dose material to a well with gravimetric feedback.
        
        Requires a dosing_system to be connected.
        
        Args:
            well: Well identifier (e.g., 'A1')
            target_mg: Target mass in milligrams
            verify: If True, reads balance before and after dosing
            **kwargs: Additional parameters passed to dosing system
        
        Returns:
            Dictionary with dosing results:
            {
                'well': str,
                'target_mg': float,
                'initial_mg': float (if verify=True),
                'final_mg': float (if verify=True),
                'actual_mg': float (if verify=True),
                'error_mg': float (if verify=True)
            }
        
        Raises:
            RuntimeError: If no dosing system is connected
        """
        if not self.dosing_system:
            raise RuntimeError(
                "No dosing system connected. "
                "Initialize MicroDoser with dosing_system parameter "
                "(e.g., dosing_system=CNCDosingSystem(...))"
            )
        
        logger.info(f"Dosing {target_mg:.2f} mg to well {well}...")
        
        result = {
            'well': well,
            'target_mg': target_mg
        }
        
        # Measure initial mass (if verification enabled)
        if verify:
            initial_mg = self.read_balance() * 1000  # g to mg
            result['initial_mg'] = initial_mg
            logger.info(f"Initial mass: {initial_mg:.3f} mg")
        
        # Dose using external system
        self.dosing_system.dose_to_well(well, target_mg=target_mg, **kwargs)
        
        # Measure final mass (if verification enabled)
        if verify:
            final_mg = self.read_balance() * 1000  # g to mg
            actual_mg = final_mg - initial_mg
            error_mg = actual_mg - target_mg
            
            result['final_mg'] = final_mg
            result['actual_mg'] = actual_mg
            result['error_mg'] = error_mg
            
            logger.info(f"Final mass: {final_mg:.3f} mg")
            logger.info(f"Actual dispensed: {actual_mg:.3f} mg")
            logger.info(f"Error: {error_mg:.3f} mg ({error_mg/target_mg*100:.1f}%)")
        
        return result
    
    def dose_plate(
        self,
        well_targets: Dict[str, float],
        verify: bool = True
    ) -> Dict[str, Dict[str, Any]]:
        """
        Dose multiple wells in sequence.
        
        Args:
            well_targets: Dictionary mapping well IDs to target masses (mg)
                         Example: {'A1': 5.0, 'A2': 3.0, 'B1': 7.0}
            verify: If True, verifies each dose with balance
        
        Returns:
            Dictionary mapping well IDs to result dictionaries
        """
        logger.info(f"Dosing {len(well_targets)} wells...")
        
        results = {}
        for well, target_mg in well_targets.items():
            result = self.dose_to_well(well, target_mg, verify=verify)
            results[well] = result
        
        logger.info(f"Plate dosing complete: {len(results)} wells")
        
        return results
    
    def home(self):
        """Return all components to home position."""
        logger.info("Homing MicroDoser...")
        
        if self.dosing_system:
            self.dosing_system.home()
        
        self.loader.home()
        
        logger.info("MicroDoser at home position")
    
    def shutdown(self):
        """Safely shutdown all components."""
        logger.info("Shutting down MicroDoser...")
        
        # Unload plate if still loaded
        if self._plate_loaded:
            self.unload_plate()
        
        # Shutdown dosing system if present
        if self.dosing_system:
            self.dosing_system.shutdown()
        
        # Shutdown loader
        self.loader.shutdown()
        
        # Balance doesn't need explicit shutdown (serial connection auto-closes)
        
        logger.info("MicroDoser shutdown complete")
    
    def get_status(self) -> Dict[str, Any]:
        """
        Get current system status.
        
        Returns:
            Dictionary with status information
        """
        status = {
            'plate_loaded': self._plate_loaded,
            'balance_connected': self.balance is not None,
            'dosing_system_connected': self.dosing_system is not None,
            'loader_status': self.loader.get_status() if hasattr(self.loader, 'get_status') else 'unknown'
        }
        
        return status


def main():
    """Example usage of MicroDoser system."""
    print("=== MicroDoser System ===")
    print("Core: Balance + Plate Loader")
    print("Optional: CNC Dosing System")
    
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    try:
        # Ask user for configuration
        mode = input("\nSelect mode:\n1. Standalone (weighing only)\n2. With CNC dosing\nChoice (1/2): ").strip()
        
        dosing_system = None
        if mode == '2':
            from .dosing_system import CNCDosingSystem
            cnc_port = input("CNC serial port [/dev/ttyUSB0]: ").strip() or '/dev/ttyUSB0'
            dosing_system = CNCDosingSystem(cnc_port=cnc_port)
            dosing_system.initialize()
        
        # Initialize MicroDoser
        balance_port = input("Balance serial port [/dev/ttyUSB1]: ").strip() or '/dev/ttyUSB1'
        plate_type = input("Plate type [shallow_plate]: ").strip() or 'shallow_plate'
        
        doser = MicroDoser(
            balance_port=balance_port,
            plate_type=plate_type,
            dosing_system=dosing_system
        )
        
        # Load plate
        print("\n1. Loading plate...")
        doser.load_plate()
        
        if mode == '2' and dosing_system:
            # Dosing workflow
            print("\n2. Running dosing test...")
            wells = input("Enter wells to dose (e.g., A1,A2,B1): ").strip().split(',')
            target = float(input("Target mass per well (mg): "))
            
            results = {}
            for well in wells:
                well = well.strip()
                result = doser.dose_to_well(well, target_mg=target)
                results[well] = result
                print(f"  {well}: {result}")
        else:
            # Manual weighing workflow
            print("\n2. Manual weighing mode...")
            while True:
                well = input("Enter well to weigh (or 'done'): ").strip()
                if well.lower() == 'done':
                    break
                mass = doser.weigh_well(well)
                print(f"  {well}: {mass:.4f} g")
        
        # Unload plate
        print("\n3. Unloading plate...")
        doser.unload_plate()
        
        # Status
        print(f"\nFinal status: {doser.get_status()}")
        
    except KeyboardInterrupt:
        print("\n\nInterrupted by user")
    except Exception as e:
        logger.error(f"Error: {e}", exc_info=True)
    finally:
        if 'doser' in locals():
            doser.shutdown()


if __name__ == "__main__":
    main()


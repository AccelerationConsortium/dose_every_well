#!/usr/bin/env python3
"""
Example: MicroDoser with CNC Dosing System
Demonstrates automated solid dosing with gravimetric verification.
"""

import logging
from dose_every_well import MicroDoser, CNCDosingSystem

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

def main():
    print("=== MicroDoser with CNC Dosing Example ===")
    print("Mode: Automated Solid Dosing\n")
    
    # Initialize CNC dosing system
    print("Initializing CNC dosing system...")
    dosing_system = CNCDosingSystem(
        cnc_port='/dev/ttyUSB0',
        doser_params={
            'i2c_address': 0x40,
            'motor_gpio_pin': 17,
            'frequency': 50
        },
        well_spacing=9.0,
        plate_origin=(0.0, 0.0)
    )
    dosing_system.initialize()
    
    # Initialize MicroDoser with dosing system
    print("Initializing MicroDoser...")
    doser = MicroDoser(
        balance_port='/dev/ttyUSB1',
        plate_type='shallow_plate',
        dosing_system=dosing_system
    )
    
    try:
        # Load plate
        print("\n1. Loading plate...")
        doser.load_plate()
        
        # Dose single well
        print("\n2. Dosing single well (A1)...")
        result = doser.dose_to_well('A1', target_mg=5.0)
        print(f"\n   Results:")
        print(f"   Target:  {result['target_mg']:.2f} mg")
        print(f"   Actual:  {result['actual_mg']:.2f} mg")
        print(f"   Error:   {result['error_mg']:.2f} mg ({result['error_mg']/result['target_mg']*100:.1f}%)")
        
        # Dose multiple wells
        print("\n3. Dosing multiple wells...")
        well_targets = {
            'A2': 3.0,
            'A3': 7.0,
            'B1': 4.5
        }
        
        results = doser.dose_plate(well_targets, verify=True)
        
        print("\n   Summary:")
        print("   Well | Target (mg) | Actual (mg) | Error (mg) | Error (%)")
        print("   " + "-" * 60)
        for well, result in results.items():
            error_pct = result['error_mg'] / result['target_mg'] * 100
            print(f"   {well:4s} | {result['target_mg']:11.2f} | {result['actual_mg']:11.2f} | {result['error_mg']:10.2f} | {error_pct:8.1f}")
        
        # Unload plate
        print("\n4. Unloading plate...")
        doser.unload_plate()
        
        print("\n✓ Complete!")
        
    except KeyboardInterrupt:
        print("\n\nInterrupted by user")
    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        doser.shutdown()


if __name__ == "__main__":
    main()


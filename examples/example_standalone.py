#!/usr/bin/env python3
"""
Example: MicroDoser in Standalone Mode
Demonstrates basic weighing station functionality without automated dosing.
"""

import logging
from dose_every_well import MicroDoser

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

def main():
    print("=== MicroDoser Standalone Example ===")
    print("Mode: Weighing Station (Manual Dosing)\n")
    
    # Initialize MicroDoser without dosing system
    doser = MicroDoser(
        balance_port='/dev/ttyUSB1',
        plate_type='shallow_plate'
    )
    
    try:
        # Load plate
        print("1. Loading plate...")
        doser.load_plate()
        print(f"   Status: {doser.get_status()}\n")
        
        # Manual dosing workflow
        print("2. Manual dosing workflow:")
        wells = ['A1', 'A2', 'A3']
        
        for well in wells:
            input(f"   Add material to well {well}, then press Enter...")
            mass_g = doser.read_balance()
            mass_mg = mass_g * 1000
            print(f"   {well}: {mass_mg:.2f} mg\n")
        
        # Unload plate
        print("3. Unloading plate...")
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


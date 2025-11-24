#!/usr/bin/env python3
"""
Example: Flow Rate Calibration for Solid Doser
Run this script to calibrate the solid doser flow rate.
"""

import logging
from dose_every_well import CNCDosingSystem

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

def main():
    print("=== Solid Doser Flow Rate Calibration ===\n")
    print("This script will help you calibrate the solid doser flow rate.")
    print("You will need:")
    print("  1. A balance to weigh dispensed material")
    print("  2. A container to collect material")
    print("  3. Material loaded in the doser hopper\n")
    
    input("Press Enter to continue...")
    
    # Initialize CNC dosing system
    print("\nInitializing CNC dosing system...")
    dosing = CNCDosingSystem(
        cnc_port='/dev/ttyUSB0',
        doser_params={
            'i2c_address': 0x40,
            'motor_gpio_pin': 17,
            'frequency': 50
        }
    )
    dosing.initialize()
    
    try:
        # Run calibration
        print("\n" + "="*60)
        print("CALIBRATION PROCEDURE")
        print("="*60)
        
        duration = float(input("\nDispense duration (seconds) [5.0]: ") or "5.0")
        gate_position = float(input("Gate position (0-35) [35]: ") or "35")
        
        print("\nSteps:")
        print("  1. Place empty container on balance")
        print("  2. Tare balance to zero")
        print("  3. Press Enter to start dispensing")
        print("  4. After dispensing completes, weigh container")
        print("  5. Enter measured mass")
        
        input("\nPress Enter when ready to dispense...")
        
        # Run dispensing
        dosing.doser.dispense(duration=duration, gate_position=gate_position)
        
        print("\n" + "="*60)
        print("RESULTS")
        print("="*60)
        
        # Get measured mass
        measured_mg = float(input("\nEnter measured mass (mg): "))
        
        # Calculate flow rate
        flow_rate = measured_mg / duration
        
        print(f"\nCalculated flow rate: {flow_rate:.2f} mg/s")
        print(f"\nTo use this calibration:")
        print(f"  1. Update CNCDosingSystem._calculate_duration() method")
        print(f"  2. Set: flow_rate = {flow_rate:.2f}  # mg/s")
        print(f"  3. Or update config file: flow_rate_mg_per_s: {flow_rate:.2f}")
        
        # Optional: Run verification
        verify = input("\nRun verification test? (y/n): ").strip().lower()
        if verify == 'y':
            print("\n" + "="*60)
            print("VERIFICATION")
            print("="*60)
            
            target_mg = float(input("\nTarget mass for verification (mg): "))
            verify_duration = target_mg / flow_rate
            
            print(f"\nWill dispense for {verify_duration:.2f} seconds")
            print("Place container on balance, tare, and press Enter...")
            input()
            
            dosing.doser.dispense(duration=verify_duration, gate_position=gate_position)
            
            verify_measured = float(input("Enter measured mass (mg): "))
            error = verify_measured - target_mg
            error_pct = (error / target_mg) * 100
            
            print(f"\nVerification Results:")
            print(f"  Target:  {target_mg:.2f} mg")
            print(f"  Actual:  {verify_measured:.2f} mg")
            print(f"  Error:   {error:.2f} mg ({error_pct:.1f}%)")
            
            if abs(error_pct) < 10:
                print("\n✓ Calibration looks good!")
            else:
                print("\n⚠ Large error - consider recalibrating")
        
        print("\n✓ Calibration complete!")
        
    except KeyboardInterrupt:
        print("\n\nInterrupted by user")
    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        dosing.shutdown()


if __name__ == "__main__":
    main()


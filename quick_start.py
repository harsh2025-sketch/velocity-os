#!/usr/bin/env python3
"""
🎯 QUICK START: Motor Cortex Calibration
"""
import subprocess
import sys
import os

def main():
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    
    print("\n" + "=" * 70)
    print("🗺️  VELOCITY MOTOR CORTEX - QUICK START")
    print("=" * 70)
    
    print("""
Choose an option:

1. Run Coordinate Mapper    (python scripts/map_coords.py)
2. Launch Velocity System   (python launch_velocity.py)
3. Test Components          (python test_components.py)
4. View Calibration Guide   (cat MOTOR_CORTEX_CALIBRATION.md)

Default (Enter = Launch System): 
""")
    
    choice = input("→ ").strip() or "2"
    
    if choice == "1":
        print("\n📍 Starting Coordinate Mapper...")
        subprocess.call(["python", "scripts/map_coords.py"])
        
    elif choice == "2":
        print("\n🚀 Launching Velocity System...")
        subprocess.call(["python", "launch_velocity.py"])
        
    elif choice == "3":
        print("\n🔧 Running Component Tests...")
        subprocess.call(["python", "test_components.py"])
        
    elif choice == "4":
        print("\n📖 Showing Calibration Guide...\n")
        try:
            with open("MOTOR_CORTEX_CALIBRATION.md", 'r') as f:
                print(f.read())
        except:
            print("Could not find MOTOR_CORTEX_CALIBRATION.md")
    else:
        print("Invalid choice. Running system launch...")
        subprocess.call(["python", "launch_velocity.py"])

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n👋 Goodbye!")
        sys.exit(0)

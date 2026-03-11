#!/usr/bin/env python3
"""
📍 COORDINATE MAPPER
Teach Velocity where things are on your screen.
Move your mouse to a target and press Enter to save it.
"""
import pyautogui
import time
import json
import os
import sys

POINTS_FILE = os.path.join(os.path.dirname(os.path.dirname(__file__)), "brain", "ganglia", "points.json")

def mapper():
    print("\n" + "=" * 60)
    print("📍 VELOCITY COORDINATE MAPPER")
    print("=" * 60)
    print("\nInstructions:")
    print("1. Enter the name of a target (e.g., 'start_button')")
    print("2. Move your mouse to that location")
    print("3. Press Enter to capture the coordinates")
    print("4. Repeat for all targets")
    print("5. Press Ctrl+C when done\n")
    
    # Load existing points
    points = {}
    if os.path.exists(POINTS_FILE):
        with open(POINTS_FILE, 'r') as f:
            points = json.load(f)
            print(f"✓ Loaded {len(points)} existing points\n")

    try:
        while True:
            name = input("📝 Enter target name (e.g., 'start_button', 'notepad_icon'): ").strip()
            
            if not name:
                print("⚠️  Name cannot be empty. Try again.")
                continue
                
            print(f"\n👉 Move your mouse to '{name}'")
            print("⏳ Waiting 3 seconds...")
            
            time.sleep(3)
            
            x, y = pyautogui.position()
            print(f"✅ Captured '{name}' at coordinates ({x}, {y})")
            
            points[name] = {"x": int(x), "y": int(y)}
            
            # Save immediately
            os.makedirs(os.path.dirname(POINTS_FILE), exist_ok=True)
            with open(POINTS_FILE, 'w') as f:
                json.dump(points, f, indent=2)
            
            print(f"💾 Saved! Total points: {len(points)}\n")
                
    except KeyboardInterrupt:
        print("\n\n" + "=" * 60)
        print("✓ MAPPING COMPLETE")
        print("=" * 60)
        if points:
            print(f"📍 {len(points)} locations mapped:")
            for name, coords in points.items():
                print(f"   • {name}: ({coords['x']}, {coords['y']})")
        print(f"💾 Saved to: {POINTS_FILE}\n")

if __name__ == "__main__":
    try:
        mapper()
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)

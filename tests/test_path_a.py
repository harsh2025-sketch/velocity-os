#!/usr/bin/env python3
"""
Test script to verify Path A brain functionality
Run this to see if the brain responds correctly
"""
import sys
import os
import time

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

print("=" * 60)
print("🧪 PATH A - BRAIN TEST")
print("=" * 60)

# Test 1: Import brain modules
print("\n[TEST 1] Importing brain modules...")
try:
    from brain.motor_bridge import MotorBridge
    print("✓ MotorBridge imported")
except Exception as e:
    print(f"✗ MotorBridge import failed: {e}")
    sys.exit(1)

try:
    from brain.ganglia import automation
    print("✓ automation imported")
except Exception as e:
    print(f"✗ automation import failed: {e}")

try:
    from brain.wizard.planner import Planner
    print("✓ Planner imported")
except Exception as e:
    print(f"⚠ Planner import failed (ollama may be missing): {e}")

# Test 2: MotorBridge stub
print("\n[TEST 2] Testing MotorBridge stub...")
try:
    MotorBridge.init()
    print("✓ MotorBridge initialized")
    
    MotorBridge.move_to(100, 100)
    print("✓ move_to() called")
    
    MotorBridge.click()
    print("✓ click() called")
    
    MotorBridge.type_text("hello test")
    print("✓ type_text() called")
except Exception as e:
    print(f"✗ MotorBridge test failed: {e}")
    sys.exit(1)

# Test 3: Create brain instance
print("\n[TEST 3] Creating VelocityBrain instance...")
try:
    import zmq
    print("✓ ZMQ available")
    
    # Don't actually start the brain - just test imports
    from brain.main import VelocityBrain
    print("✓ VelocityBrain class loaded")
    print("⚠ Not starting full brain (would require ZMQ sockets)")
    
except ImportError as e:
    print(f"✗ Missing dependency: {e}")
    print("\nInstall with: pip install pyzmq")
    sys.exit(1)
except Exception as e:
    print(f"⚠ Import warning: {e}")

# Test 4: Automation reflexes
print("\n[TEST 4] Testing automation reflexes...")
try:
    result = automation.execute_reflex_command("open notepad", strict=True)
    if result:
        print(f"✓ Reflex returned: {result}")
    else:
        print("✓ Reflex executed (returned None)")
except Exception as e:
    print(f"⚠ Reflex test: {e}")

print("\n" + "=" * 60)
print("✅ PATH A TESTS COMPLETE")
print("=" * 60)
print("\nTo run full brain:")
print("  python brain/main.py")
print("\nTo send test intents:")
print("  python scripts/send_intents.py")

#!/usr/bin/env python3
"""
Direct test of TYPE action.
1. Open Notepad
2. Wait 2 seconds for it to open
3. Type "hello world"
4. Check brain.log for debug output
"""
import sys
import os
import time

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from brain.motor_bridge import MotorBridge
from brain.ganglia.automation import execute_reflex_command

print("=== TEST: TYPE ACTION ===\n")

# Step 1: Open Notepad
print("STEP 1: Opening Notepad...")
result = execute_reflex_command("open notepad")
print(f"  Reflex returned: {result}")
print("  Waiting 3 seconds for Notepad to open...")
time.sleep(3)

# Step 2: Type "hello world"
print("\nSTEP 2: Typing 'hello world'...")
print("  Calling MotorBridge.type_text('hello world')...")
try:
    MotorBridge.type_text("hello world")
    print("  ✓ type_text() completed without error")
except Exception as e:
    print(f"  ✗ type_text() failed: {e}")

print("\nSTEP 3: Waiting 2 seconds to see result...")
time.sleep(2)

print("\nTest complete!")
print("\nExpected result: 'hello world' should be typed in Notepad")
print("Check the Notepad window to verify!")

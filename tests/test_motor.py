import sys
import os
# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from brain.motor_bridge import MotorBridge
import time

print(">>> 🟢 TESTING LIZARD BODY...")

# Move to center of screen (approx)
print(">>> Moving to 500, 500...")
MotorBridge.move_to(500, 500)
time.sleep(0.5)

# Right Click context menu
print(">>> Right Clicking...")
MotorBridge.click("right")

print(">>> ✅ BODY IS ONLINE.")
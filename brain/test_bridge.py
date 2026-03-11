from motor_bridge import MotorBridge
import time

print("=== Testing C++ Motor Bridge ===")

print("1. Initializing drivers...")
MotorBridge.init()

print("2. Moving mouse to (500, 500)...")
MotorBridge.move_to(500, 500)
time.sleep(1)

print("3. Clicking left button...")
MotorBridge.click("left")
time.sleep(1)

print("4. Scrolling down...")
MotorBridge.scroll(-120)
time.sleep(1)

print("5. Typing text...")
MotorBridge.type_text("hello")
time.sleep(1)

print("✅ All tests passed!")

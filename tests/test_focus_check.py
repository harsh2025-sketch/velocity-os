#!/usr/bin/env python3
"""
Test TYPE action with window focus verification
"""
import sys
import os
import time
import ctypes

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from brain.motor_bridge import MotorBridge
from brain.ganglia.reflexes import open_app

# Windows API to get focused window
GetForegroundWindow = ctypes.windll.user32.GetForegroundWindow
GetWindowTextW = ctypes.windll.user32.GetWindowTextW

def get_focused_window():
    """Get the title of the currently focused window"""
    hwnd = GetForegroundWindow()
    length = GetWindowTextW(hwnd, None, 0)
    buf = ctypes.create_unicode_buffer(length)
    GetWindowTextW(hwnd, buf, length)
    return buf.value

print("=== TEST: TYPE WITH WINDOW FOCUS CHECK ===\n")

# Step 1: Check focus before
print("BEFORE: Focused window:", get_focused_window())

# Step 2: Open Notepad using the reflex (which uses Win+type+Enter)
print("\nOpening Notepad via reflex...")
open_app("Notepad")
time.sleep(3)

print("AFTER open_app: Focused window:", get_focused_window())

# Step 3: Click on Notepad to ensure focus
print("\nClicking to ensure Notepad has focus...")
MotorBridge.click()
time.sleep(0.5)

print("AFTER click: Focused window:", get_focused_window())

# Step 4: Type
print("\nTyping 'hello world'...")
MotorBridge.type_text("hello world")
time.sleep(1)

print("AFTER type: Focused window:", get_focused_window())

print("\nTest complete! Check Notepad to see if 'hello world' was typed.")

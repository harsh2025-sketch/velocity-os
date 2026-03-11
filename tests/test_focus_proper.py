#!/usr/bin/env python3
"""
Test TYPE action with proper window focus management
"""
import sys
import os
import time
import subprocess
import ctypes

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from brain.motor_bridge import MotorBridge

# Windows API functions
FindWindowW = ctypes.windll.user32.FindWindowW
SetForegroundWindow = ctypes.windll.user32.SetForegroundWindow
GetForegroundWindow = ctypes.windll.user32.GetForegroundWindow
GetWindowTextW = ctypes.windll.user32.GetWindowTextW
ShowWindow = ctypes.windll.user32.ShowWindow
SW_SHOW = 5

def get_focused_window():
    """Get the title of the currently focused window"""
    try:
        hwnd = GetForegroundWindow()
        length = GetWindowTextW(hwnd, None, 0)
        if length > 0:
            buf = ctypes.create_unicode_buffer(length)
            GetWindowTextW(hwnd, buf, length)
            return buf.value
    except:
        pass
    return "(unknown)"

def bring_window_to_front(window_title):
    """Use Windows API to find and focus a window by title"""
    try:
        hwnd = FindWindowW(None, window_title)
        if hwnd:
            SetForegroundWindow(hwnd)
            ShowWindow(hwnd, SW_SHOW)
            return True
    except:
        pass
    return False

print("=== TEST: TYPE WITH PROPER FOCUS ===\n")

# Step 1: Open Notepad directly
print("Opening Notepad...")
subprocess.Popen("notepad.exe", shell=True)
time.sleep(2)

print("Focused window:", get_focused_window())

# Step 2: Try to find and focus Notepad
print("\nSearching for Notepad window...")
# Try different window titles
for title in ["Untitled - Notepad", "Notepad", "Untitled"]:
    if bring_window_to_front(title):
        print(f"  Found and focused: {title}")
        break

time.sleep(0.5)
print("Focused window after focus attempt:", get_focused_window())

# Step 3: Type
print("\nTyping 'hello world'...")
MotorBridge.type_text("hello world")
time.sleep(1)

print("Focused window after type:", get_focused_window())

print("\n✓ Test complete! Check Notepad to see if 'hello world' was typed.")
print("  Expected: 'hello world' should appear in the Notepad window")

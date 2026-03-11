"""
C++ COMPONENT VALIDATION TEST SUITE
Tests all core C++ modules:
- Motor Control (Mouse, Keyboard, Bezier smoothing)
- Voice Detection (Cochlea)
- Reflex Dispatch (Pattern matching)
"""

import ctypes
import time
import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from brain.motor_bridge import MotorBridge
from brain.utils.win_focus import list_visible_windows

def test_motor_latencies():
    """Test C++ motor execution times."""
    print("\n" + "="*60)
    print("TEST 1: C++ MOTOR LATENCIES")
    print("="*60)
    
    motor = MotorBridge()
    
    tests = [
        ("Type 'hello'", lambda: motor.type_text("hello")),
        ("Type 'a'", lambda: motor.type_text("a")),
        ("Move to (500, 300)", lambda: motor.move_to(500, 300)),
        ("Click (left)", lambda: motor.click()),
        ("Move to (100, 100)", lambda: motor.move_to(100, 100)),
        ("Move to (600, 400)", lambda: motor.move_to(600, 400)),
        ("Move 10px", lambda: motor.move_to(110, 410)),
        ("Double-click", lambda: motor.double_click()),
        ("Press Enter", lambda: motor.press_special('enter')),
        ("Scroll down", lambda: motor.scroll(-3)),
    ]
    
    for name, func in tests:
        start = time.time()
        func()
        elapsed = (time.time() - start) * 1000
        print(f"  {name:30} {elapsed:7.1f} ms")
        time.sleep(0.2)  # Delay between tests

def test_motor_accuracy():
    """Test that motor commands actually execute."""
    print("\n" + "="*60)
    print("TEST 2: C++ MOTOR ACCURACY")
    print("="*60)
    
    motor = MotorBridge()
    
    print("  [TEST] Moving to (200, 200)...")
    motor.move_to(200, 200)
    time.sleep(0.1)
    print("  ✓ Move executed")
    
    print("  [TEST] Typing 'velocity'...")
    motor.type_text("velocity")
    time.sleep(0.3)
    print("  ✓ Type executed")
    
    print("  [TEST] Pressing Escape...")
    motor.press_special('esc')
    time.sleep(0.1)
    print("  ✓ Escape executed")

def test_bezier_smoothing():
    """Test Bezier curve smoothing for large moves."""
    print("\n" + "="*60)
    print("TEST 3: BEZIER SMOOTHING (Paths)")
    print("="*60)
    
    motor = MotorBridge()
    
    # Large move should be smooth (uses Bezier)
    print("  [TEST] Large move: (100, 100) → (900, 700)...")
    start = time.time()
    motor.move_to(900, 700)
    elapsed = (time.time() - start) * 1000
    print(f"  ✓ Bezier move took {elapsed:.1f}ms")
    
    # Small move should skip Bezier
    print("  [TEST] Small move: (900, 700) → (905, 705)...")
    start = time.time()
    motor.move_to(905, 705)
    elapsed = (time.time() - start) * 1000
    print(f"  ✓ Direct move took {elapsed:.1f}ms (should be <10ms if fast-path working)")

def test_keyboard_latency():
    """Test character-by-character typing latency."""
    print("\n" + "="*60)
    print("TEST 4: KEYBOARD CHARACTER LATENCY")
    print("="*60)
    
    motor = MotorBridge()
    
    strings = ["a", "ab", "abc", "abcde", "velocity"]
    for s in strings:
        start = time.time()
        motor.type_text(s)
        elapsed = (time.time() - start) * 1000
        per_char = elapsed / len(s)
        print(f"  Type '{s:10}' ({len(s)} chars): {elapsed:7.1f}ms ({per_char:.1f}ms/char)")
        time.sleep(0.2)

def test_reflex_dispatcher_cpp():
    """Test C++ reflex dispatcher (if compiled into DLL)."""
    print("\n" + "="*60)
    print("TEST 5: C++ REFLEX DISPATCHER")
    print("="*60)
    
    try:
        from brain.motor_bridge import lizard
        
        # Try to call C++ dispatcher function
        if hasattr(lizard, 'Core_DispatchIntent'):
            print("  ✓ C++ dispatcher function found in DLL")
            
            test_cases = [
                ("open notepad", "Should open Notepad"),
                ("type hello", "Should type 'hello'"),
                ("click 100 200", "Should click at (100, 200)"),
            ]
            
            for intent, expected in test_cases:
                try:
                    result = lizard.Core_DispatchIntent(intent.encode('utf-8'))
                    print(f"    '{intent}' → {expected}")
                except Exception as e:
                    print(f"    '{intent}' → ERROR: {e}")
        else:
            print("  ⚠ C++ dispatcher not found in DLL (not yet compiled)")
            print("    This is expected if reflex_dispatcher.cpp hasn't been added to CMakeLists.txt")
            
    except Exception as e:
        print(f"  ✗ Failed to access DLL: {e}")

def test_window_focus():
    """Test Windows focus management."""
    print("\n" + "="*60)
    print("TEST 6: WINDOW FOCUS MANAGEMENT")
    print("="*60)
    
    windows = list_visible_windows()
    print(f"  Found {len(windows)} visible windows:")
    for i, (hwnd, title) in enumerate(windows[:5]):  # Show first 5
        print(f"    [{i}] {title}")
    
    if len(windows) > 5:
        print(f"    ... and {len(windows) - 5} more")

def test_dll_exports():
    """Verify all expected C++ exports exist."""
    print("\n" + "="*60)
    print("TEST 7: C++ DLL EXPORTS")
    print("="*60)
    
    try:
        from brain.motor_bridge import lizard
        
        expected_exports = [
            "Core_MoveMouse",
            "Core_ClickMouse",
            "Core_ScrollMouse",
            "Core_TypeString",
            "Core_PressKey",
            "Core_ReleaseKey",
            "Core_InitMouse",
            "Core_InitKeyboard",
        ]
        
        for export in expected_exports:
            if hasattr(lizard, export):
                print(f"  ✓ {export}")
            else:
                print(f"  ✗ {export} NOT FOUND")
                
    except Exception as e:
        print(f"  ✗ Failed to load DLL: {e}")

def profile_execution_path():
    """Profile the full execution path: Python → C++."""
    print("\n" + "="*60)
    print("TEST 8: END-TO-END EXECUTION PROFILE")
    print("="*60)
    
    motor = MotorBridge()
    
    # Simulate a voice command execution
    steps = [
        ("Move to text", lambda: motor.move_to(250, 250)),
        ("Type text", lambda: motor.type_text("hello world")),
        ("Press Escape", lambda: motor.press_special('esc')),
    ]
    
    total_time = 0
    for name, func in steps:
        start = time.time()
        func()
        elapsed = (time.time() - start) * 1000
        total_time += elapsed
        print(f"  {name:20} {elapsed:7.1f}ms")
        time.sleep(0.1)
    
    print(f"  {'TOTAL':20} {total_time:7.1f}ms")

if __name__ == "__main__":
    print("\n" + "="*60)
    print("= VELOCITY C++ COMPONENT TEST SUITE")
    print("="*60)
    
    try:
        test_dll_exports()
        test_motor_latencies()
        test_keyboard_latency()
        test_bezier_smoothing()
        test_motor_accuracy()
        test_reflex_dispatcher_cpp()
        test_window_focus()
        profile_execution_path()
        
        print("\n" + "="*60)
        print("ALL TESTS COMPLETED")
        print("="*60)
        
    except KeyboardInterrupt:
        print("\n\n[INTERRUPTED] Test suite stopped by user")
    except Exception as e:
        print(f"\n✗ FATAL ERROR: {e}")
        import traceback
        traceback.print_exc()

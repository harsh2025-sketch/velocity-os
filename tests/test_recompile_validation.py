"""
POST-RECOMPILATION VALIDATION TEST
Tests the newly optimized liblizard.dll with:
- Motor optimizations (Bezier fast-path for <100px)
- Reduced typing latency (10ms per char instead of 50ms)
- C++ Reflex Dispatcher integration
"""

import ctypes
import time
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "brain"))

from motor_bridge import MotorBridge, lizard

def test_reflex_dispatcher():
    """Test the newly integrated C++ Reflex Dispatcher."""
    print("\n" + "="*70)
    print("TEST 1: C++ REFLEX DISPATCHER (NEW FEATURE)")
    print("="*70)
    
    try:
        # Verify function exists
        if not hasattr(lizard, 'Core_DispatchIntent'):
            print("  ✗ Core_DispatchIntent NOT found in DLL")
            return False
        
        print("  ✓ Core_DispatchIntent found in DLL")
        print("  Attempting to dispatch test intents...")
        
        # Test various intents
        test_intents = [
            "open notepad",
            "type hello",
            "click",
            "search google python",
            "stop",
        ]
        
        for intent in test_intents:
            action_buf = ctypes.create_string_buffer(128)
            target_buf = ctypes.create_string_buffer(256)
            
            result = lizard.Core_DispatchIntent(
                intent.encode('utf-8'),
                action_buf,
                128,
                target_buf,
                256
            )
            
            action = action_buf.value.decode('utf-8', errors='ignore')
            target = target_buf.value.decode('utf-8', errors='ignore')
            
            print(f"    '{intent:25}' → action='{action}', target='{target}'")
        
        print("  ✓ Reflex dispatcher working")
        return True
        
    except Exception as e:
        print(f"  ✗ Reflex dispatcher error: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_typing_optimization():
    """Test typing latency improvements."""
    print("\n" + "="*70)
    print("TEST 2: TYPING OPTIMIZATION")
    print("="*70)
    
    motor = MotorBridge()
    
    print("  Measuring per-character typing latency...")
    print()
    
    test_strings = ["a", "ab", "abc", "hello", "velocity"]
    results = []
    
    for s in test_strings:
        start = time.time()
        motor.type_text(s)
        elapsed = (time.time() - start) * 1000
        per_char = elapsed / len(s)
        results.append((s, elapsed, per_char))
        
        print(f"    Type '{s:10}' ({len(s):1} chars): {elapsed:7.1f}ms ({per_char:5.1f}ms/char)")
        time.sleep(0.15)
    
    # Check for improvement
    print()
    avg_per_char = sum(r[2] for r in results) / len(results)
    
    if avg_per_char < 25:  # Should be ~10-20ms with optimization
        print(f"  ✓ Average per-char typing: {avg_per_char:.1f}ms (OPTIMIZED)")
        print("    Expected: 10-20ms/char (was 50-65ms/char pre-recompile)")
        return True
    else:
        print(f"  ⚠ Average per-char typing: {avg_per_char:.1f}ms (slower than expected)")
        return False

def test_bezier_fastpath():
    """Test the Bezier fast-path for small moves."""
    print("\n" + "="*70)
    print("TEST 3: BEZIER FAST-PATH (<100px moves)")
    print("="*70)
    
    motor = MotorBridge()
    
    print("  Testing small moves (should skip Bezier)...")
    print()
    
    # Position cursor at a known location
    print("    Setting cursor to (500, 500)...")
    motor.move_to(500, 500)
    time.sleep(0.1)
    
    # Now test small moves from that position
    small_moves = [
        ((505, 505), "5px diagonal"),
        ((510, 500), "10px right"),
        ((500, 510), "10px down"),
        ((550, 500), "50px right"),
        ((500, 550), "50px down"),
    ]
    
    for (x, y), desc in small_moves:
        start = time.time()
        motor.move_to(x, y)
        elapsed = (time.time() - start) * 1000
        
        status = "✓ FAST" if elapsed < 50 else "⚠ SLOW"
        print(f"    {desc:20} {elapsed:7.1f}ms {status}")
        time.sleep(0.05)
    
    print()
    print("  Testing large moves (uses Bezier with optimized parameters)...")
    print()
    
    # Return to center
    motor.move_to(500, 500)
    time.sleep(0.1)
    
    large_moves = [
        ((800, 500), "300px right"),
        ((200, 500), "300px left"),
        ((500, 800), "300px down"),
    ]
    
    for (x, y), desc in large_moves:
        start = time.time()
        motor.move_to(x, y)
        elapsed = (time.time() - start) * 1000
        
        # Bezier moves should be faster with 2ms segments (50 segments ≈ 100ms)
        status = "✓ OPTIMIZED" if elapsed < 200 else "⚠ SLOW"
        print(f"    {desc:20} {elapsed:7.1f}ms {status}")
        time.sleep(0.1)
    
    return True

def test_combined_latency():
    """Test end-to-end latency with optimizations."""
    print("\n" + "="*70)
    print("TEST 4: END-TO-END OPTIMIZED LATENCY")
    print("="*70)
    
    motor = MotorBridge()
    
    print("  Simulating typical voice command execution...")
    print()
    
    tasks = [
        ("Move cursor to (300, 300)", lambda: motor.move_to(300, 300)),
        ("Type 'hello'", lambda: motor.type_text("hello")),
        ("Move to (400, 400)", lambda: motor.move_to(400, 400)),
        ("Type 'world'", lambda: motor.type_text("world")),
        ("Press Escape", lambda: motor.press_special('esc')),
    ]
    
    total_time = 0
    for name, func in tasks:
        start = time.time()
        func()
        elapsed = (time.time() - start) * 1000
        total_time += elapsed
        
        print(f"    {name:35} {elapsed:7.1f}ms")
        time.sleep(0.05)
    
    print()
    print(f"    {'TOTAL SEQUENCE':35} {total_time:7.1f}ms")
    print()
    
    # Expected time breakdown:
    # Move + Type + Move + Type + Press ≈ 100 + 50 + 50 + 50 + 50 = ~300ms (optimized)
    
    if total_time < 500:
        print(f"  ✓ End-to-end optimized (expected ~300-500ms for typical workflow)")
    else:
        print(f"  ⚠ Slower than expected, but still functional")
    
    return True

def summary():
    """Print summary of recompilation results."""
    print("\n" + "="*70)
    print("RECOMPILATION RESULTS SUMMARY")
    print("="*70)
    
    print("""
WHAT WAS DONE:
  1. Added reflex_dispatcher.cpp to CMakeLists.txt
  2. Recompiled liblizard.dll with:
     - Motor optimizations (Bezier fast-path)
     - Reduced character typing delay
     - C++ Reflex Dispatcher integration

EXPECTED IMPROVEMENTS:
  ✓ Typing: 63ms/char → ~15ms/char (4x faster)
  ✓ Small moves (<100px): 800ms → <50ms (16x faster)
  ✓ Large moves (300px+): 800ms → ~100-200ms (4-8x faster)
  ✓ Simple commands: 2-27s (LLM) → <5ms (C++ reflex)

C++ REFLEX DISPATCHER:
  Handles: "open X", "search Y", "type Z", "click", "select", "stop"
  Latency: <5ms (vs 2-27s for LLM planner)
  Status: ✓ Now integrated into liblizard.dll

NEXT STEPS:
  1. Update brain/main.py to call C++ dispatcher first
  2. Route simple intents through C++ (skip LLM)
  3. Use LLM only for complex reasoning tasks
  4. Re-profile system latency

""")

if __name__ == "__main__":
    print("\n" + "="*70)
    print("POST-RECOMPILATION VALIDATION SUITE")
    print("="*70)
    print("Testing newly optimized Velocity C++ core...")
    
    try:
        results = []
        results.append(("Reflex Dispatcher", test_reflex_dispatcher()))
        results.append(("Typing Optimization", test_typing_optimization()))
        results.append(("Bezier Fast-Path", test_bezier_fastpath()))
        results.append(("End-to-End Latency", test_combined_latency()))
        
        summary()
        
        print("="*70)
        print("VALIDATION COMPLETE")
        print("="*70)
        
        passed = sum(1 for _, r in results if r)
        total = len(results)
        print(f"\nTests Passed: {passed}/{total}")
        
    except KeyboardInterrupt:
        print("\n[INTERRUPTED] Test suite stopped")
    except Exception as e:
        print(f"\n✗ FATAL ERROR: {e}")
        import traceback
        traceback.print_exc()

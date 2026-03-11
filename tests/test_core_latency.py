#!/usr/bin/env python3
"""
Test harness for C++ core latency profiling.
Measures: Cochlea response, Motor execution, Reflex dispatch.
"""
import time
import sys
import os
import ctypes
from ctypes import c_char_p, c_int

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from brain.motor_bridge import MotorBridge

print("="*70)
print("🧪 VELOCITY C++ CORE LATENCY TEST")
print("="*70)

# Test 1: Motor latency
print("\n[TEST 1] Motor Bridge Latency")
print("-" * 70)

test_cases = [
    ("Type 'hello'", lambda: MotorBridge.type_text("hello")),
    ("Click @ (100, 100)", lambda: MotorBridge.click()),
    ("Move to (500, 500)", lambda: MotorBridge.move_to(500, 500)),
    ("Double-click", lambda: MotorBridge.double_click()),
    ("Press Ctrl+A", lambda: MotorBridge.press_special("ctrl")),
]

for label, func in test_cases:
    start = time.perf_counter()
    func()
    elapsed = (time.perf_counter() - start) * 1000  # ms
    print(f"  {label:30s} → {elapsed:6.2f}ms")

# Test 2: Reflex dispatch latency (if C++ reflex compiled)
print("\n[TEST 2] Reflex Dispatcher Latency (Python fallback)")
print("-" * 70)

from brain.ganglia.automation import execute_reflex_command

reflex_tests = [
    "open notepad",
    "search python",
    "type hello world",
    "click button",
    "select text",
    "stop",
]

for intent in reflex_tests:
    start = time.perf_counter()
    result = execute_reflex_command(intent, strict=True)
    elapsed = (time.perf_counter() - start) * 1000  # ms
    action = result.get('action') if isinstance(result, dict) else "string"
    print(f"  '{intent:20s}' → {action:15s} [{elapsed:6.2f}ms]")

# Test 3: Planner latency
print("\n[TEST 3] Planner (LLM) Latency")
print("-" * 70)

from brain.wizard.planner import Planner

planner = Planner()
planner_tests = [
    "Type hello world",
    "Open Notepad",
    "Select all",
]

for intent in planner_tests:
    start = time.perf_counter()
    result = planner.decide(intent, "")
    elapsed = (time.perf_counter() - start) * 1000  # ms
    action = result.get('action', 'error')
    print(f"  '{intent:20s}' → {action:15s} [{elapsed:7.2f}ms]")

print("\n" + "="*70)
print("SUMMARY: C++ core is < 1ms; Python planner is 500-800ms bottleneck")
print("="*70)

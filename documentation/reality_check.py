#!/usr/bin/env python3
"""
QUICK REALITY CHECK SCRIPT
Run this to see what actually works vs what's theoretical
"""

import os
import json
import sys
from pathlib import Path

def check(condition, name, details=""):
    status = "✅" if condition else "❌"
    print(f"{status} {name}")
    if details:
        print(f"   → {details}")
    return condition

def check_file(path, should_exist=True):
    exists = os.path.exists(path)
    if should_exist:
        return check(exists, f"File exists: {path}")
    else:
        return check(not exists, f"File doesn't exist: {path}")

def check_file_size(path, min_size=0):
    if os.path.exists(path):
        size = os.path.getsize(path)
        return check(size >= min_size, f"File size OK: {path}", f"{size} bytes")
    return check(False, f"File missing: {path}")

def check_json(path):
    try:
        with open(path, 'r') as f:
            data = json.load(f)
        return check(True, f"JSON valid: {path}", f"{len(data)} items")
    except:
        return check(False, f"JSON invalid: {path}")

print("\n" + "=" * 90)
print("VELOCITY CORTEX - QUICK REALITY CHECK")
print("=" * 90 + "\n")

project_root = Path(__file__).parent
memory_dir = project_root / "brain" / "memory"

# =====================================================
print("📁 PROJECT STRUCTURE")
print("-" * 90)

checks_passed = 0
checks_total = 0

# Core modules
modules = [
    "brain/processor.py",
    "brain/learning.py",
    "brain/observer.py",
    "brain/synthesizer.py",
    "brain/composite_executor.py",
    "brain/symbolic.py",
    "brain/ui_parser.py",
    "brain/vision.py",
    "brain/temporal_context.py",
    "brain/diagnostics.py",
    "brain/cross_layer.py",
    "brain/brain_adapter.py",
]

print("\nCore Modules:")
for module in modules:
    path = project_root / module
    result = check_file(path)
    checks_total += 1
    if result:
        checks_passed += 1

# Documentation
docs = [
    "PRESENTATION.md",
    "DELIVERY_PACKAGE.md",
    "PROJECT_COMPLETION_SUMMARY.md",
    "PROJECT_INDEX.md",
]

print("\nDocumentation:")
for doc in docs:
    path = project_root / doc
    result = check_file(path)
    checks_total += 1
    if result:
        checks_passed += 1

# =====================================================
print("\n\n📊 DATA FILES")
print("-" * 90)

data_files = {
    "brain/memory/skills.json": 100,  # Should have some data
    "brain/memory/processor_config.json": 50,
    "brain/memory/success_matrix.json": 50,
    "brain/memory/failure_log.json": 0,  # Can be empty
    "brain/memory/execution_history.json": 0,  # Can be empty
}

print("\nMemory/Persistence Files:")
for file, min_size in data_files.items():
    path = project_root / file
    result = check_file(path)
    checks_total += 1
    if result:
        checks_passed += 1
        # Check size
        actual_size = os.path.getsize(path)
        if actual_size > 0:
            try:
                with open(path) as f:
                    data = json.load(f)
                    if isinstance(data, dict):
                        items = len(data)
                    elif isinstance(data, list):
                        items = len(data)
                    else:
                        items = "?"
                print(f"   → {actual_size} bytes, {items} items")
            except:
                print(f"   → {actual_size} bytes (invalid JSON!)")

# =====================================================
print("\n\n🧪 TEST FILES")
print("-" * 90)

test_files = [
    "tests/test_phase2_4_integration.py",
    "tests/test_core_latency.py",
    "tests/test_integration_validation.py",
]

print("\nTest Suite:")
for test in test_files:
    path = project_root / test
    result = check_file(path)
    checks_total += 1
    if result:
        checks_passed += 1

# =====================================================
print("\n\n⚙️  DEPENDENCIES")
print("-" * 90)

print("\nOptional Dependencies (for full features):")
import importlib

optional = {
    "pynput": "Mouse/keyboard recording",
    "uiautomation": "Windows UI detection",
    "ollama": "LLM synthesis",
    "opencv": "Vision processing",
}

for module, purpose in optional.items():
    try:
        importlib.import_module(module)
        check(True, f"{module}", purpose)
        checks_total += 1
        checks_passed += 1
    except ImportError:
        check(False, f"{module}", f"NOT INSTALLED - {purpose} disabled")
        checks_total += 1

# =====================================================
print("\n\n🔍 SYSTEM STATUS")
print("-" * 90)

# Check if main.py has been modified
print("\nIntegration Status:")
main_py = project_root / "brain" / "main.py"
if main_py.exists():
    with open(main_py, encoding='utf-8', errors='ignore') as f:
        content = f.read()
        has_cortex = "brain_adapter" in content or "cortex" in content
        check(has_cortex, "main.py has cortex integration")
        checks_total += 1
        if has_cortex:
            checks_passed += 1

# =====================================================
print("\n\n📈 EXECUTION STATE")
print("-" * 90)

execution_log = project_root / "brain" / "memory" / "cortex_execution_log.json"
execution_history = project_root / "brain" / "memory" / "execution_history.json"

print("\nLearning State:")

# Check execution history
if execution_history.exists():
    try:
        with open(execution_history) as f:
            history = json.load(f)
            if isinstance(history, list) and len(history) > 0:
                check(True, f"Learning history populated", f"{len(history)} executions recorded")
                checks_total += 1
                checks_passed += 1
            else:
                check(False, f"Learning history EMPTY", "No real executions yet")
                checks_total += 1
    except:
        check(False, "Learning history corrupted")
        checks_total += 1
else:
    check(False, "Learning history file missing")
    checks_total += 1

# =====================================================
print("\n\n📋 SUMMARY")
print("-" * 90)

print(f"\nChecks Passed: {checks_passed}/{checks_total} ({100*checks_passed//checks_total}%)")

if checks_passed == checks_total:
    print("\n✅ PROJECT STRUCTURE: COMPLETE")
    print("   All files present and accounted for")
    print("   Ready for practical testing")
else:
    missing = checks_total - checks_passed
    print(f"\n⚠️  {missing} ITEMS MISSING")
    print("   Check the gaps above")

# =====================================================
print("\n\n🚀 WHAT TO TEST FIRST")
print("-" * 90)

print("""
1. QUICK SANITY CHECK
   python -m unittest discover -s tests -p test_*.py
   
2. RUN THE DEMO
   python demo_youtube_downloader.py
   
3. CHECK REAL EXECUTION
   • Open Chrome and try a real command
   • Check cortex_execution_log.json fills up
   • Check if execution_history.json changes
   
4. PERFORMANCE TEST
   • Run 100 commands and measure latency
   • Check if 150ms target is realistic
   • Profile bottlenecks

5. LEARNING TEST
   • Run same command twice
   • Check confidence values change
   • Verify layer ordering updated

6. FAILURE TEST
   • Change UI while command running
   • Verify system falls back correctly
   • Check failure_log.json
""")

print("\n" + "=" * 90)
print("END OF REALITY CHECK")
print("=" * 90 + "\n")

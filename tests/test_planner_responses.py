#!/usr/bin/env python3
"""
Debug the planner response for "Hello world"
"""
import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from brain.wizard.planner import Planner

planner = Planner()

test_inputs = [
    "Hello world",
    "Type hello world",
    "hello world",
    "open notepad",
    "Type hello",
    "Select hello",
    "Select all",
    "Stop",
]

print("=== TESTING PLANNER RESPONSES ===\n")

for user_input in test_inputs:
    print(f"Input: '{user_input}'")
    try:
        response = planner.decide(user_input, "No screen context")
        print(f"Response: {response}")
        print(f"Type: {type(response)}")
    except Exception as e:
        print(f"ERROR: {e}")
    print()

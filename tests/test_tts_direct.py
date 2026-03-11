#!/usr/bin/env python3
"""
Direct TTS test without Brain/STT/Stream pipeline
Tests if TTS can receive and play messages
"""
import zmq
import json
import subprocess
import os
import winsound
import time
import sys
import io

# Fix emoji encoding for Windows
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

PIPER_BINARY = os.path.join("bin", "piper.exe")
VOICE_MODEL = os.path.join("bin", "en_US-lessac-medium.onnx")
ESPEAK_DATA = os.path.join("bin", "espeak-ng-data")

print("🔧 DIRECT TTS TEST")
print("=" * 60)

# 1. Test Piper exists
print(f"✓ Checking Piper executable...")
if not os.path.exists(PIPER_BINARY):
    print(f"❌ Piper not found at {PIPER_BINARY}")
    sys.exit(1)
print(f"✓ Piper found at {PIPER_BINARY}")

# 2. Test Voice model exists
print(f"✓ Checking voice model...")
if not os.path.exists(VOICE_MODEL):
    print(f"❌ Voice model not found at {VOICE_MODEL}")
    sys.exit(1)
print(f"✓ Voice model found at {VOICE_MODEL}")

# 3. Test Piper can generate audio
print(f"✓ Testing Piper TTS generation...")
test_text = "Hello, I am Velocity."
env = os.environ.copy()
if os.path.isdir(ESPEAK_DATA):
    env["PIPER_PHONEMIZE_ESPEAK_PATH"] = os.path.abspath(ESPEAK_DATA)

output_file = "test_direct.wav"
try:
    result = subprocess.run(
        [PIPER_BINARY, "--model", VOICE_MODEL, "--output_file", output_file],
        input=test_text,
        text=True,
        capture_output=True,
        env=env,
    )
    
    if result.returncode != 0:
        print(f"❌ Piper generation failed: {result.stderr}")
        sys.exit(1)
    
    if not os.path.exists(output_file):
        print(f"❌ Audio file was not created at {output_file}")
        sys.exit(1)
    
    print(f"✓ Audio file generated: {output_file}")
    
    # 4. Test audio playback
    print(f"✓ Playing audio...")
    winsound.PlaySound(output_file, winsound.SND_FILENAME)
    print(f"✓ Audio played successfully!")
    
    os.remove(output_file)
    print(f"✓ Test cleanup complete")
    
except Exception as e:
    print(f"❌ Error: {e}")
    sys.exit(1)

print("=" * 60)
print("✅ ALL TESTS PASSED - TTS is working")

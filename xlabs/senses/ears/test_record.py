"""
Record audio for testing STT
Uses system default microphone
"""

import sys
import platform

print("=== Audio Recorder for STT Testing ===\n")

# Check for sounddevice
try:
    import sounddevice as sd
    import soundfile as sf
    import numpy as np
    has_sounddevice = True
    print("✅ sounddevice available")
except ImportError:
    has_sounddevice = False
    print("❌ sounddevice not installed")
    print("Install with: pip install sounddevice soundfile")

if not has_sounddevice:
    print("\nAlternative recording methods:")
    if platform.system() == "Windows":
        print("  - Use Windows Voice Recorder app")
        print("  - Or PowerShell: Add-Type -AssemblyName System.Speech")
    else:
        print("  - Use: arecord -d 5 -f S16_LE -r 16000 test.wav")
    sys.exit(1)

# Recording parameters
SAMPLE_RATE = 16000  # Whisper prefers 16kHz
DURATION = 5  # seconds
OUTPUT_FILE = "test_recording.wav"

print("\n" + "="*50)
print(f"Sample Rate: {SAMPLE_RATE} Hz")
print(f"Duration: {DURATION} seconds")
print(f"Output: {OUTPUT_FILE}")
print("="*50)

input("\nPress Enter to start recording...")

print(f"\n🎤 Recording for {DURATION} seconds...")
print("Speak clearly into your microphone!")

# Record
audio = sd.rec(int(DURATION * SAMPLE_RATE), 
               samplerate=SAMPLE_RATE, 
               channels=1, 
               dtype='float32')
sd.wait()

print("✅ Recording complete!")

# Save
sf.write(OUTPUT_FILE, audio, SAMPLE_RATE)
print(f"✅ Saved to: {OUTPUT_FILE}")

print(f"\nNow run STT test:")
print(f"  python test_stt.py")
print(f"  And enter: {OUTPUT_FILE}")

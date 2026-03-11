"""
Simple STT Test - No ZeroMQ required
Tests Faster-Whisper directly with a test audio file
"""

try:
    from faster_whisper import WhisperModel
    print("✅ Faster-Whisper installed")
except ImportError:
    print("❌ Faster-Whisper NOT installed")
    print("Install with: pip install faster-whisper")
    exit(1)

import os
import time

MODEL_SIZE = "tiny"  # Using tiny for fast testing
COMPUTE_TYPE = "int8"

print(f"\n=== STT Test ===")
print(f"Model: {MODEL_SIZE}")
print(f"Compute: {COMPUTE_TYPE}")

# Initialize model
print("\n1. Loading Whisper model...")
start = time.time()
model = WhisperModel(MODEL_SIZE, device="cpu", compute_type=COMPUTE_TYPE)
load_time = time.time() - start
print(f"   [OK] Loaded in {load_time:.2f}s")

# Test with audio file if provided
test_audio = input("\nEnter path to test audio file (or press Enter to skip): ").strip()

if test_audio and os.path.exists(test_audio):
    print(f"\n2. Transcribing: {test_audio}")
    start = time.time()
    segments, info = model.transcribe(test_audio, beam_size=5)
    
    print(f"\n   Language: {info.language} (probability: {info.language_probability:.2f})")
    print(f"\n   Transcription:")
    for segment in segments:
        print(f"   [{segment.start:.2f}s -> {segment.end:.2f}s] {segment.text}")
    
    transcribe_time = time.time() - start
    print(f"\n   ⚡ Transcribed in {transcribe_time:.2f}s")
else:
    print("\n⚠️  No audio file provided - skipping transcription test")
    print("   To test, record a .wav file and run again")

print("\n3. Recording instructions:")
print("   Windows: Use Sound Recorder app")
print("   Linux: Use arecord -d 5 -f S16_LE -r 16000 test.wav")
print("   Or use any audio file (.wav, .mp3, .m4a)")

print("\n✅ STT Test Complete")

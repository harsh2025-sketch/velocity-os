"""
Simple TTS Test - No ZeroMQ required
Tests text-to-speech with available engines
"""

import os
import sys
import platform

print("=== TTS Test ===\n")

# Check what's available
has_pyttsx3 = False
has_gtts = False
has_piper = False

try:
    import pyttsx3
    has_pyttsx3 = True
    print("[OK] pyttsx3 available (native OS TTS)")
except ImportError:
    print("[FAIL] pyttsx3 not installed")

try:
    from gtts import gTTS
    has_gtts = True
    print("[OK] gTTS available (Google TTS - requires internet)")
except ImportError:
    print("[FAIL] gTTS not installed")

# Check for Piper binary
piper_path = "./bin/piper.exe" if platform.system() == "Windows" else "./bin/piper"
if os.path.exists(piper_path):
    has_piper = True
    print(f"[OK] Piper binary found at {piper_path}")
else:
    print(f"[FAIL] Piper not found at {piper_path}")

if not (has_pyttsx3 or has_gtts or has_piper):
    print("\n[WARNING] No TTS engine available!")
    print("Install one with:")
    print("  pip install pyttsx3  # Fastest, works offline")
    print("  pip install gTTS     # Needs internet")
    exit(1)

print("\n" + "="*50)

# Test text
test_text = input("\nEnter text to speak (or press Enter for default): ").strip()
if not test_text:
    test_text = "Hello, I am Velocity A-OS. Testing text to speech."

print(f"\nText: {test_text}")

# Option 1: pyttsx3 (Fastest, native)
if has_pyttsx3:
    print("\n1. Testing pyttsx3 (Native OS TTS)...")
    try:
        engine = pyttsx3.init()
        
        # Get voices
        voices = engine.getProperty('voices')
        print(f"   Available voices: {len(voices)}")
        
        # Set properties
        rate = engine.getProperty('rate')
        engine.setProperty('rate', rate - 50)  # Slower
        
        volume = engine.getProperty('volume')
        engine.setProperty('volume', volume)
        
        print(f"   Speaking...")
        engine.say(test_text)
        engine.runAndWait()
        print("   [OK] pyttsx3 test passed")
    except Exception as e:
        print(f"   [FAIL] pyttsx3 failed: {e}")

# Option 2: gTTS (Google, needs internet)
if has_gtts:
    print("\n2. Testing gTTS (Google TTS)...")
    choice = input("   Requires internet. Continue? (y/n): ").strip().lower()
    if choice == 'y':
        try:
            import tempfile
            import subprocess
            
            tts = gTTS(text=test_text, lang='en', slow=False)
            
            # Save to temp file
            with tempfile.NamedTemporaryFile(delete=False, suffix='.mp3') as f:
                temp_file = f.name
                tts.save(temp_file)
            
            print(f"   Saved to: {temp_file}")
            print(f"   Playing...")
            
            # Play based on OS
            if platform.system() == "Windows":
                os.startfile(temp_file)
            elif platform.system() == "Darwin":  # macOS
                subprocess.call(["afplay", temp_file])
            else:  # Linux
                subprocess.call(["mpg123", temp_file])
            
            input("   Press Enter when done...")
            os.remove(temp_file)
            print("   [OK] gTTS test passed")
        except Exception as e:
            print(f"   [FAIL] gTTS failed: {e}")

# Option 3: Piper (Best quality, offline)
if has_piper:
    print("\n3. Testing Piper (High-quality offline TTS)...")
    print("   ⚠️  Requires Piper binary and model file")
    print("   Download from: https://github.com/rhasspy/piper")

print("\n" + "="*50)
print("✅ TTS Test Complete\n")

print("Installation commands:")
print("  pip install pyttsx3      # Recommended for quick testing")
print("  pip install gTTS         # For Google TTS")
print("  # For Piper: Download from rhasspy/piper releases")

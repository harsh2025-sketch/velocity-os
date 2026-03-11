#!/usr/bin/env python3
"""
🔧 VELOCITY COMPONENT TESTER
Test each part of the pipeline independently
"""
import sys
import os

# Add project root to path
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, PROJECT_ROOT)

# Fix encoding
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

def test_microphone():
    """Test if microphone can detect sound"""
    print("\n" + "="*60)
    print("🎤 TESTING MICROPHONE INPUT")
    print("="*60)
    
    try:
        import sounddevice as sd
        import numpy as np
        import torch
        
        print("✓ Dependencies loaded")
        print("✓ Loading Silero VAD...")
        
        model, utils = torch.hub.load(repo_or_dir='snakers4/silero-vad',
                                     model='silero_vad',
                                     force_reload=False,
                                     trust_repo=True)
        print("✓ VAD model loaded")
        
        SAMPLE_RATE = 16000
        THRESHOLD = 0.3
        
        print("\n🔴 RECORDING: Speak now for 3 seconds...")
        print("Watch for numbers above 0.3 when you talk:\n")
        
        def audio_callback(indata, frames, time_info, status):
            if status:
                print(status)
            
            audio_chunk = indata.copy().squeeze()
            tensor = torch.from_numpy(audio_chunk).float()
            speech_prob = model(tensor, SAMPLE_RATE).item()
            
            marker = "🎤" if speech_prob > THRESHOLD else "·"
            print(f"{marker} {speech_prob:.2f}", end="\r", flush=True)
        
        with sd.InputStream(samplerate=SAMPLE_RATE, channels=1, 
                           callback=audio_callback, blocksize=512):
            import time
            time.sleep(3)
        
        print("\n✅ Microphone test passed!")
        return True
        
    except Exception as e:
        print(f"❌ Microphone test failed: {e}")
        return False


def test_tts():
    """Test if Piper can generate and play audio"""
    print("\n" + "="*60)
    print("🔊 TESTING TEXT-TO-SPEECH (Piper)")
    print("="*60)
    
    try:
        import subprocess
        import winsound
        import time
        
        PIPER_BINARY = os.path.join(PROJECT_ROOT, "bin", "piper.exe")
        VOICE_MODEL = os.path.join(PROJECT_ROOT, "bin", "en_US-lessac-medium.onnx")
        ESPEAK_DATA = os.path.join(PROJECT_ROOT, "bin", "espeak-ng-data")
        
        if not os.path.exists(PIPER_BINARY):
            print(f"❌ Piper not found at {PIPER_BINARY}")
            return False
        
        print("✓ Piper executable found")
        
        if not os.path.exists(VOICE_MODEL):
            print(f"❌ Voice model not found")
            return False
        
        print("✓ Voice model found")
        print("🔄 Generating audio for 'Hello, Velocity is online'...")
        
        env = os.environ.copy()
        if os.path.isdir(ESPEAK_DATA):
            env["PIPER_PHONEMIZE_ESPEAK_PATH"] = os.path.abspath(ESPEAK_DATA)
        
        output_file = "test_voice.wav"
        result = subprocess.run(
            [PIPER_BINARY, "--model", VOICE_MODEL, "--output_file", output_file],
            input="Hello, Velocity is online",
            text=True,
            capture_output=True,
            env=env,
        )
        
        if result.returncode != 0:
            print(f"❌ Piper generation failed: {result.stderr}")
            return False
        
        if not os.path.exists(output_file):
            print(f"❌ Audio file was not created")
            return False
        
        print("✓ Audio generated")
        print("🔊 Playing audio...")
        winsound.PlaySound(output_file, winsound.SND_FILENAME)
        
        os.remove(output_file)
        print("✅ TTS test passed! (Did you hear audio?)")
        return True
        
    except Exception as e:
        print(f"❌ TTS test failed: {e}")
        return False


def test_stt():
    """Test if Faster-Whisper can transcribe"""
    print("\n" + "="*60)
    print("🗣️ TESTING SPEECH-TO-TEXT (Faster-Whisper)")
    print("="*60)
    
    try:
        from faster_whisper import WhisperModel
        import sounddevice as sd
        import numpy as np
        from scipy.io.wavfile import write
        import tempfile
        
        print("✓ Loading Faster-Whisper model...")
        model = WhisperModel("distil-large-v3", device="cpu", compute_type="int8")
        print("✓ Model loaded")
        
        print("\n🔴 RECORDING: Speak for 3 seconds...")
        
        SAMPLE_RATE = 16000
        frames = sd.rec(int(SAMPLE_RATE * 3), samplerate=SAMPLE_RATE, channels=1)
        sd.wait()
        
        print("✓ Audio recorded")
        print("🔄 Transcribing...")
        
        # Save to temp file
        tf = tempfile.NamedTemporaryFile(delete=False, suffix=".wav")
        write(tf.name, SAMPLE_RATE, frames.astype(np.float32))
        tf.close()
        
        segments, info = model.transcribe(tf.name, beam_size=5)
        text = " ".join([segment.text for segment in segments]).strip()
        
        os.remove(tf.name)
        
        if text:
            print(f"✅ STT test passed! Transcribed: '{text}'")
            return True
        else:
            print("⚠️ No speech detected. Try speaking louder.")
            return False
            
    except Exception as e:
        print(f"❌ STT test failed: {e}")
        return False


def test_brain():
    """Test if Brain/Planner can respond"""
    print("\n" + "="*60)
    print("🧠 TESTING BRAIN/PLANNER (Llama-3)")
    print("="*60)
    
    try:
        import ollama
        import requests
        
        # Check if Ollama is running
        print("🔍 Checking if Ollama service is running...")
        try:
            response = requests.get("http://localhost:11434/api/tags", timeout=2)
            if response.status_code != 200:
                print("❌ Ollama service not responding")
                return False
        except:
            print("❌ Ollama service not running. Start it with: ollama serve")
            return False
        
        print("✓ Ollama service is running")
        print("🤔 Asking Llama-3: 'What is your name?'")
        
        response = ollama.generate(model="llama3", prompt="What is your name?")
        text = response.get('response', '').strip()
        
        if text:
            print(f"✅ Brain test passed! Llama said: '{text[:100]}...'")
            return True
        else:
            print("❌ Llama returned empty response")
            return False
            
    except Exception as e:
        print(f"❌ Brain test failed: {e}")
        return False


def main():
    print("\n")
    print("███████████████████████████████████████████████████")
    print("   🚀 VELOCITY COMPONENT TESTER 🚀")
    print("███████████████████████████████████████████████████")
    
    results = {
        "Microphone": test_microphone(),
        "Text-to-Speech": test_tts(),
        "Speech-to-Text": test_stt(),
        "Brain/Planner": test_brain(),
    }
    
    print("\n" + "="*60)
    print("📊 TEST RESULTS SUMMARY")
    print("="*60)
    
    for component, passed in results.items():
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status}: {component}")
    
    all_passed = all(results.values())
    
    print("\n" + "="*60)
    if all_passed:
        print("✅ ALL TESTS PASSED! System is ready.")
        print("\nNow run: python launch_velocity.py")
    else:
        print("❌ Some tests failed. Fix them before running the full system.")
        print("\nFailed components:")
        for component, passed in results.items():
            if not passed:
                print(f"  - {component}")
    print("="*60 + "\n")


if __name__ == "__main__":
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    main()

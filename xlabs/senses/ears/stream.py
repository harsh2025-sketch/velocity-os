import time
import zmq
import json
import sounddevice as sd
import numpy as np
import torch
import tempfile
import os
import sys
import winsound  # For audio feedback beep
from scipy.io.wavfile import write

# Fix emoji encoding for Windows
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

# --- CONFIGURATION ---
SAMPLE_RATE = 16000
BLOCK_SIZE = 512
THRESHOLD = 0.3  # Sensitivity (0.1 = Very Sensitive, 0.9 = Strict) - LOWERED for daytime noise
MIN_SPEECH_DURATION_MS = 250
SILENCE_DURATION_MS = 250  # TURBO MODE: Cut from 700ms to 250ms - fire audio packet instantly
DEBUG_MIC_LEVEL = True  # Set to False to disable mic level debug output

class EarStream:
    def __init__(self):
        print("👂 STREAM: Loading Silero VAD (Voice Activity Detection)...")
        # Load small, fast VAD model from Torch Hub
        self.model, utils = torch.hub.load(repo_or_dir='snakers4/silero-vad',
                                         model='silero_vad',
                                         force_reload=False,
                                         trust_repo=True)
        self.get_speech_timestamps, _, self.read_audio, _, _ = utils
        
        # ZMQ Publisher (Sends audio paths to STT Drone)
        self.context = zmq.Context()
        self.socket = self.context.socket(zmq.PUB)
        self.socket.bind("tcp://*:5556") # STT Worker connects here
        
        self.buffer = []
        self.speaking = False
        self.silence_counter = 0

    def run(self):
        print("👂 STREAM: Listening to Microphone...")
        
        # Raw InputStream (Blocking)
        with sd.InputStream(samplerate=SAMPLE_RATE, channels=1, callback=self.audio_callback, blocksize=BLOCK_SIZE):
            while True:
                time.sleep(0.1) # Keep main thread alive

    def audio_callback(self, indata, frames, time_info, status):
        if status:
            print(status)
        
        # Convert to Tensor for VAD
        audio_chunk = indata.copy().squeeze()
        tensor = torch.from_numpy(audio_chunk).float()
        
        # Check for Speech probability
        speech_prob = self.model(tensor, SAMPLE_RATE).item()
        
        # DEBUG: Show microphone level
        if DEBUG_MIC_LEVEL:
            print(f"DEBUG: Mic Level: {speech_prob:.2f}", end='\r')
        
        if speech_prob > THRESHOLD:
            if not self.speaking:
                print("🎤 ...") # Visual indicator of speech start
                self.speaking = True
            self.silence_counter = 0
            self.buffer.append(audio_chunk)
        
        elif self.speaking:
            # We were speaking, now it's quiet. Wait for "SILENCE_DURATION" before cutting.
            self.buffer.append(audio_chunk)
            self.silence_counter += (BLOCK_SIZE / SAMPLE_RATE) * 1000
            
            if self.silence_counter > SILENCE_DURATION_MS:
                # CUT IT!
                self.speaking = False
                self.flush_buffer()

    def flush_buffer(self):
        # 1. Minimum duration check
        if not self.buffer:
            return
            
        duration_ms = (len(self.buffer) * BLOCK_SIZE / SAMPLE_RATE) * 1000
        if duration_ms < MIN_SPEECH_DURATION_MS:
            self.buffer = [] # Too short, probably a mouse click
            return

        print(f"[SEND] Sending Audio Clip ({len(self.buffer)} chunks)")
        
        # TURBO MODE: Audio feedback beep - let user know message was received
        try:
            winsound.Beep(1000, 100)  # 1000Hz beep for 100ms
        except:
            pass  # Beep might fail in some environments
        
        # 2. Save to Temp File (RAM Drive is best, but Temp is fine)
        # We flatten the list of arrays into one long array
        full_audio = np.concatenate(self.buffer)
        
        tf = tempfile.NamedTemporaryFile(delete=False, suffix=".wav")
        write(tf.name, SAMPLE_RATE, full_audio.astype(np.float32))
        tf.close()
        
        # 3. Publish to ZMQ
        payload = json.dumps({"path": tf.name})
        self.socket.send_string(f"AUDIO_SPEECH {payload}")
        
        # 4. Reset
        self.buffer = []

if __name__ == "__main__":
    ear = EarStream()
    ear.run()

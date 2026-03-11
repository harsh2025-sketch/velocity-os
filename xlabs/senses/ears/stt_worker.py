from faster_whisper import WhisperModel
import zmq
import json
import os
import time
import sys
import io

# Fix emoji encoding for Windows
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

MODEL_SIZE = "base.en"  # TURBO MODE: 10x faster than distil-large-v3
COMPUTE_TYPE = "int8"

def run(params):
    print(f"👂 STT Drone: Loading Faster-Whisper ({MODEL_SIZE})...")
    
    model = WhisperModel(MODEL_SIZE, device="cpu", compute_type=COMPUTE_TYPE)
    
    context = zmq.Context()
    
    # Subscribe to audio from stream (stream.py publishes on 5556)
    sub_socket = context.socket(zmq.SUB)
    sub_socket.connect("tcp://localhost:5556")
    sub_socket.setsockopt_string(zmq.SUBSCRIBE, "AUDIO_SPEECH")
    
    # Publish transcriptions to brain (bind here, brain connects)
    pub_socket = context.socket(zmq.PUB)
    pub_socket.bind("tcp://*:5557")  # STT publishes to brain on 5557
    
    print("👂 STT Drone: Listening for audio...")
    time.sleep(1)  # Let subscribers connect
    
    while True:
        try:
            message = sub_socket.recv_string()
            topic, payload_str = message.split(" ", 1)
            payload = json.loads(payload_str)
            audio_path = payload['path']
            
            print(f"📥 STT: Received audio packet from stream")
            segments, info = model.transcribe(audio_path, beam_size=5)
            
            text = " ".join([segment.text for segment in segments]).strip()
            
            if text:
                print(f"🗣️ STT: User Said: '{text}'")
                message_out = json.dumps({"text": text, "confidence": info.language_probability})
                pub_socket.send_string(f"USER_INTENT {message_out}")
                print(f"📨 STT: Publishing USER_INTENT to port 5557")
                print(f"📨 STT Publishing to Brain on 5557: {text}")
                
            os.remove(audio_path)
        except Exception as e:
            print(f"[ERROR] STT Error: {e}")

if __name__ == "__main__":
    run({})

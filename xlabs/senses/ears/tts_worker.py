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

# File logging
LOG_FILE = "tts.log"
log_file = open(LOG_FILE, "w", buffering=1, encoding='utf-8')

PIPER_BINARY = os.path.join("bin", "piper.exe")
VOICE_MODEL = os.path.join("bin", "en_US-lessac-medium.onnx")
ESPEAK_DATA = os.path.join("bin", "espeak-ng-data")

def run(params):
    msg = "👄 TTS Drone: Warming up vocal cords (Piper)..."
    print(msg)
    log_file.write(msg + "\n")
    log_file.flush()
    
    context = zmq.Context()
    pull_socket = context.socket(zmq.PULL)
    pull_socket.connect("tcp://localhost:5555")
    
    msg2 = "👄 TTS Drone: Connected to Brain PUSH on 5555, ready to speak!"
    print(msg2)
    log_file.write(msg2 + "\n")
    log_file.flush()
    time.sleep(1)  # Let connection stabilize
    msg3 = "👄 TTS Drone: Listening for messages..."
    print(msg3)
    log_file.write(msg3 + "\n")
    log_file.flush()
    
    while True:
        try:
            message = pull_socket.recv_string()
            msg = f"📨 TTS Received from Brain: {message[:50]}..."
            print(msg)
            log_file.write(msg + "\n")
            log_file.flush()
            # PULL receives pure JSON, no topic prefix
            text = json.loads(message)['text']
            
            msg2 = f"🤖 Agent Saying: {text}"
            print(msg2)
            log_file.write(msg2 + "\n")
            log_file.flush()
            
            env = os.environ.copy()
            if os.path.isdir(ESPEAK_DATA):
                env["PIPER_PHONEMIZE_ESPEAK_PATH"] = os.path.abspath(ESPEAK_DATA)
            
            output_file = "agent_speech.wav"
            result = subprocess.run(
                [PIPER_BINARY, "--model", VOICE_MODEL, "--output_file", output_file],
                input=text,
                text=True,
                capture_output=True,
                env=env,
            )
            
            if result.returncode == 0 and os.path.exists(output_file):
                winsound.PlaySound(output_file, winsound.SND_FILENAME)
                os.remove(output_file)
                msg3 = f"[OK] TTS: Audio played successfully"
                print(msg3)
                log_file.write(msg3 + "\n")
                log_file.flush()
            else:
                err = f"[ERROR] TTS Error: {result.stderr}"
                print(err)
                log_file.write(err + "\n")
                log_file.flush()
        except Exception as e:
            err = f"[ERROR] TTS Worker Error: {e}"
            print(err)
            log_file.write(err + "\n")
            log_file.flush()

if __name__ == "__main__":
    run({})

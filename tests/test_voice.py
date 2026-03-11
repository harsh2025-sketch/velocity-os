import os
import subprocess
import winsound

# Paths
piper = os.path.join("bin", "piper.exe")
model = os.path.join("bin", "en_US-lessac-medium.onnx")
espeak_data = os.path.join("bin", "espeak-ng-data")
output = "test_audio.wav"
text = "Velocity Operating System. Systems nominal."

print(f">>> 🟢 TESTING VOICE...")
print(f">>> Engine: {piper}")

if not os.path.exists(piper):
    print(f">>> ❌ ERROR: Piper binary missing at {piper}")
    raise SystemExit(1)

if not os.path.exists(model):
    print(f">>> ❌ ERROR: Voice model missing at {model}")
    raise SystemExit(1)

# Piper needs the espeak-ng data directory discoverable
env = os.environ.copy()
if os.path.isdir(espeak_data):
    env["PIPER_PHONEMIZE_ESPEAK_PATH"] = os.path.abspath(espeak_data)

result = subprocess.run(
    [piper, "--model", model, "--output_file", output],
    input=text,
    text=True,
    capture_output=True,
    env=env,
)

if result.returncode != 0:
    print(f">>> ❌ ERROR: {result.stderr or result.stdout}")
else:
    print(f">>> 🔊 Playing Audio...")
    winsound.PlaySound(output, winsound.SND_FILENAME)
    print(">>> ✅ VOICE IS ONLINE.")

# Cleanup
if os.path.exists(output):
    os.remove(output)
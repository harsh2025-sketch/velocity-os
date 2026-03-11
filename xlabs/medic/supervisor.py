import subprocess
import time
import sys
import os

BRAIN_PATH = os.path.join("brain", "main.py")

class Supervisor:
    def __init__(self):
        self.process = None
        self.restarts = 0

    def start_brain(self):
        print(f"❤️ Medic: Injecting Life into {BRAIN_PATH}...")
        self.process = subprocess.Popen(
            [sys.executable, BRAIN_PATH],
            shell=False
        )

    def monitor(self):
        while True:
            if self.process is None:
                self.start_brain()
            
            # Check if alive
            status = self.process.poll()
            
            if status is not None:
                print(f"💀 Medic: Brain Flatlined (Code {status}).")
                self.restarts += 1
                print("[ACTION] Medic: DEFIBRILLATING...")
                self.start_brain()
            
            time.sleep(1)

if __name__ == "__main__":
    medic = Supervisor()
    try:
        medic.monitor()
    except KeyboardInterrupt:
        if medic.process:
            medic.process.terminate()
        print("[SUPERVISOR] Shutdown requested. Brain terminated.")

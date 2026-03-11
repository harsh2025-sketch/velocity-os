import time
import zmq
import json
import sys

# Simple publisher to feed intents to Python Brain on tcp://localhost:5557
# Usage: python scripts/send_intents.py

ctx = zmq.Context()
pub = ctx.socket(zmq.PUB)
pub.bind("tcp://*:5557")

# Test intents that match reflex patterns
intents = [
    {"text": "open notepad", "description": "Open Notepad app"},
    {"text": "type hello world", "description": "Type text 'hello world'"},
    {"text": "search for python", "description": "Web search for python"},
    {"text": "open chrome", "description": "Open Chrome browser"},
    {"text": "stop", "description": "Stop execution"},
]

# Give subscriber time to connect
print("📡 Intent Publisher ready; waiting 1s for brain to subscribe...")
time.sleep(1)

try:
    for i, intent in enumerate(intents, 1):
        msg = f"USER_INTENT {json.dumps(intent)}"
        print(f"\n[{i}/{len(intents)}] Publishing: {intent['description']}")
        print(f"   Intent: {intent['text']}")
        pub.send_string(msg)
        time.sleep(2)  # Wait between intents for execution

    print("\n✓ All intents sent. Brain should have executed all actions.")
    print("  (Press Ctrl+C to stop brain)")
    
    # Keep alive so brain can continue running
    while True:
        time.sleep(1)
        
except KeyboardInterrupt:
    print("\n\n📡 Publisher shutting down...")
    pub.close()
    ctx.term()
    sys.exit(0)


"""
VELOCITY Brain Module
Main orchestration logic for neurosymbolic AI control system
Coordinates sensory input, reflexes, planning, and motor control
"""

import time
import sys
import os
import threading
import json
import zmq
import io
import queue
import ctypes
from typing import Dict, Optional, Any, Tuple

# Fix emoji encoding for Windows
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

# Add root to path so we can import modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import types and modules
from brain.types import (
    ActionType,
    SelectMode,
    ScreenPoint,
    UserIntent,
    ActionPlan,
)
from brain.wizard.planner import Planner
from brain.motor_bridge import MotorBridge
from brain.ganglia import automation
from brain.ganglia.reflexes import open_app

# PHASE 4: Import Cortex processor adapter for 3-layer defense
try:
    from brain.cortex.brain_adapter import BrainIntegrationAdapter
    HAS_CORTEX = True
except ImportError as e:
    print(f"⚠️ BRAIN: Cortex processor not available: {e}")
    HAS_CORTEX = False

# Add file logging
LOG_FILE: str = "brain.log"
log_file = open(LOG_FILE, "w", buffering=1, encoding='utf-8')

# Optional dependencies - gracefully degrade if missing
try:
    from brain.ganglia.shell_scripts import open_app_from_index
except ImportError:
    def open_app_from_index(index: int) -> Optional[str]:
        return None

try:
    from brain.ganglia.websearch import search_web
except ImportError:
    def search_web(query: str) -> Dict[str, Any]:
        print(f"[WebSearch] Would search: {query}")
        return {"results": []}

try:
    from xlabs.senses.eyes.ocr_worker import find_text_on_screen, find_phrase_region
except ImportError:
    def find_text_on_screen(text: str, debug: bool = False) -> Tuple[int, int]:
        print(f"[Vision] Would find: {text}")
        return (100, 100)  # Default center coords

    def find_phrase_region(phrase: str) -> Optional[Tuple[int, int, int, int]]:
        return None

try:
    from brain.utils.win_focus import bring_any_editor_to_front, bring_to_front_by_substring
except ImportError:
    def bring_any_editor_to_front() -> None:
        pass

    def bring_to_front_by_substring(substr: str) -> None:
        pass


def log(msg: str) -> None:
    """Log to both console and file"""
    print(msg)
    log_file.write(msg + "\n")
    log_file.flush()


class VelocityBrain:
    """
    Main brain orchestrator: coordinates sensing, planning, and action execution.
    
    Architecture:
    1. SENSING: Listen to STT input (ZMQ subscriber)
    2. COGNITION: Route through reflex → LLM planning
    3. EXECUTION: Execute actions via motor bridge
    4. FEEDBACK: Speak responses
    
    Conversion Note: This class should map to a C++ VelocityBrain struct/class
    with equivalent method signatures.
    """

    def __init__(self) -> None:
        """Initialize brain subsystems"""
        print("🧠 BRAIN: Awakening...")

        # Behavior controls
        self.strict_mode: bool = True  # Gate reflexes to explicit commands
        self.cancel_event: threading.Event = threading.Event()  # User interruption

        # Common STT mishearing corrections
        self.intent_corrections: Dict[str, str] = {
            # Notepad mishears
            "north bay": "notepad",
            "north baird": "notepad",
            "node pair": "notepad",
            "not bad": "notepad",
            # Chrome
            "crow": "chrome",
            "crone": "chrome",
            # Edge
            "age": "edge",
        }

        # Load known screen coordinates
        self.known_points: Dict[str, Dict[str, int]] = {}
        try:
            with open("brain/ganglia/points.json", 'r') as f:
                self.known_points = json.load(f)
                print(f"🗺️  BRAIN: Loaded {len(self.known_points)} known coordinates")
        except FileNotFoundError:
            self.known_points = {}
            print("⚠️  BRAIN: No coordinate map found. Run: python scripts/map_coords.py")

        # Communication setup
        self.context: zmq.Context = zmq.Context()
        self.action_queue: queue.Queue[Dict[str, Any]] = queue.Queue()
        worker: threading.Thread = threading.Thread(
            target=self.run_action_worker, daemon=True
        )
        worker.start()
        
        # 1. Subscribe to transcriptions from STT (stt_worker publishes on 5557)
        self.stt_sub: zmq.Socket = self.context.socket(zmq.SUB)
        self.stt_sub.connect("tcp://localhost:5557")
        self.stt_sub.setsockopt_string(zmq.SUBSCRIBE, "USER_INTENT")
        print("🧠 BRAIN: STT subscription connected (5557)")

        # 2. Publish speech commands (PUSH for guaranteed delivery)
        self.speak_push: zmq.Socket = self.context.socket(zmq.PUSH)
        self.speak_push.bind("tcp://*:5555")
        print("🧠 BRAIN: Speech PUSH socket bound (5555)")

        # 3. Initialize Cognitive Core
        self.planner: Optional[Planner] = None
        try:
            self.planner = Planner()
            print("🧠 BRAIN: Planner loaded.")
        except Exception as e:
            print(f"⚠️ BRAIN: Planner load warning: {e}")

        # PHASE 4: Initialize Cortex Processor Adapter
        self.cortex_adapter: Optional[BrainIntegrationAdapter] = None
        if HAS_CORTEX:
            try:
                self.cortex_adapter = BrainIntegrationAdapter()
                print("🧠 BRAIN: Cortex 3-layer processor loaded (Phase 4)")
            except Exception as e:
                print(f"⚠️ BRAIN: Cortex adapter failed: {e}")
                self.cortex_adapter = None

        # 4. Start listening to ears
        threading.Thread(target=self.listen_to_senses, daemon=True).start()

        print("🧠 BRAIN: Online & Waiting.")
        time.sleep(2)  # Wait for TTS to connect before publishing
        self.say("Velocity systems fully operational.")

    def say(self, text: str) -> None:
        """Send speech command to Mouth Drone"""
        try:
            message: str = json.dumps({"text": text})
            self.speak_push.send_string(message)
            msg: str = f"📢 BRAIN Publishing to TTS: {text}"
            print(msg)
            log_file.write(msg + "\n")
            log_file.flush()
        except Exception as e:
            err_msg: str = f"⚠️ BRAIN: Failed to broadcast speech: {e}"
            print(err_msg)
            log_file.write(err_msg + "\n")
            log_file.flush()

    def try_cpp_dispatcher(self, intent: str) -> Optional[Dict[str, Any]]:
        """
        Try C++ Reflex Dispatcher first (ultra-low latency <5ms).
        Returns action dict if matched, None otherwise.
        
        C++ dispatcher handles:
        - "open <app>" → open notepad, chrome, etc.
        - "type <text>" → type hello world
        - "search <query>" → web search
        - "click" → click at current position
        - "select <text>" → find and select text
        - "stop" → stop current action
        """
        try:
            from motor_bridge import lizard

            if not hasattr(lizard, 'Core_DispatchIntent'):
                return None  # C++ dispatcher not available

            # Call C++ dispatcher with output buffers
            action_buf: ctypes.Array[ctypes.c_char] = ctypes.create_string_buffer(128)
            target_buf: ctypes.Array[ctypes.c_char] = ctypes.create_string_buffer(256)

            result: int = lizard.Core_DispatchIntent(
                intent.encode('utf-8'),
                action_buf,
                128,
                target_buf,
                256,
            )

            if result != 0:
                return None  # Dispatcher returned error

            action: str = action_buf.value.decode('utf-8', errors='ignore').strip()
            target: str = target_buf.value.decode('utf-8', errors='ignore').strip()

            # If C++ dispatcher returned "none", try Python reflex instead
            if action == "none":
                return None

            # Map C++ dispatcher output to action format
            action_map: Dict[str, str] = {
                "open": "open",
                "type": "type",
                "search": "web_search",
                "web_search": "web_search",
                "click": "click",
                "select": "select",
                "stop": "stop",
            }

            if action not in action_map:
                return None
            
            # Return as action dict for execute_plan()
            return {
                "action": action_map[action],
                "text": target if action in ["type", "search", "web_search"] else None,
                "phrase": target if action == "select" else None,
            }
            
        except ImportError:
            return None  # ctypes not available
        except Exception as e:
            print(f"⚠️ C++ Dispatcher error: {e}")
            return None

    def listen_to_senses(self) -> None:
        """Listen for USER_INTENT from STT Worker"""
        print("🧠 BRAIN: Listening thread started...")
        log_file.write("🧠 BRAIN: Listening thread started...\n")
        log_file.flush()
        while True:
            try:
                message: str = self.stt_sub.recv_string()
                parts: list = message.split(" ", 1)
                topic: str = parts[0]
                payload_str: str = parts[1] if len(parts) > 1 else "{}"
                payload: Dict[str, Any] = json.loads(payload_str)
                self.process_sensory_input(topic, payload)
            except Exception as e:
                err_msg: str = f"❌ BRAIN: Listen error: {e}"
                print(err_msg)
                log_file.write(err_msg + "\n")
                log_file.flush()
                time.sleep(1)

    def process_sensory_input(self, topic: str, payload: Dict[str, Any]) -> None:
        """Process incoming sensory data (intents, events, etc)"""
        if topic == "USER_INTENT":
            user_text: str = payload.get('text', '')
            msg: str = f"🧠 COGNITION: User said '{user_text}'"
            print(msg)
            log_file.write(msg + "\n")
            log_file.flush()
            intent_lower: str = self.normalize_intent(user_text)

            # Immediate STOP handling
            if intent_lower in {"stop", "cancel", "abort", "halt"} or intent_lower.startswith(
                "stop"
            ):
                self.cancel_event.set()
                log("🛑 INTERRUPT: Stopping current actions by user request")
                self.execute_plan({"action": "stop"})
                return

            # 1a. Check C++ Reflex Dispatcher FIRST
            cpp_action: Optional[Dict[str, Any]] = self.try_cpp_dispatcher(intent_lower)
            if cpp_action:
                print(f"⚡ C++ REFLEX: Ultra-fast response ({cpp_action['action']})")
                log_file.write(f"⚡ C++ REFLEX: {cpp_action['action']}\n")
                log_file.flush()
                self.action_queue.put(cpp_action)
                return

            # 1b. Check Python Reflex as fallback
            reflex_response: Optional[str] = automation.execute_reflex_command(
                intent_lower, strict=self.strict_mode
            )
            if reflex_response:
                print(f"⚡ REFLEX: Fast response (no AI needed)")
                log_file.write(f"⚡ REFLEX: Fast response (no AI needed)\n")
                log_file.flush()
                if isinstance(reflex_response, dict):
                    self.action_queue.put(reflex_response)
                else:
                    self.say(reflex_response)
                return

            # PHASE 4: 2a. Try Cortex 3-layer processor (NEW)
            if self.cortex_adapter:
                try:
                    print(f"🧠 CORTEX: Running 3-layer processor (symbolic→structural→visual)...")
                    cortex_action = self.cortex_adapter.process_intent(
                        user_intent=intent_lower,
                        app_context="unknown",
                    )
                    if cortex_action:
                        print(f"✓ CORTEX: Action found via {cortex_action.get('_layer', 'unknown')} layer")
                        log_file.write(f"✓ CORTEX: {cortex_action}\n")
                        log_file.flush()
                        self.action_queue.put(cortex_action)
                        return
                    else:
                        print(f"⚠️ CORTEX: No action found, falling back to planner")
                except Exception as e:
                    print(f"⚠️ CORTEX: Error - {e}, falling back to planner")

            # PHASE 4: 2b. Ask the LLM (Planner - Deep Thinking) as final fallback
            if self.planner:
                try:
                    print(f"🤔 THINKING: Asking Llama-3 for response...")
                    action_plan: Dict[str, Any] = self.planner.decide(
                        intent_lower, "Screen Context Not Available Yet"
                    )
                    print(f"✓ THOUGHT: Llama responded with: {action_plan}")
                    log_file.write(f"✓ PLANNER OUTPUT: {action_plan}\n")
                    log_file.flush()
                    self.action_queue.put(action_plan)
                except Exception as e:
                    err_msg = f"⚠️ BRAIN: Planner error: {e}"
                    print(err_msg)
                    log_file.write(err_msg + "\n")
                    log_file.flush()
                    self.say("I encountered an error while thinking.")
            else:
                self.say("I cannot think right now.")

    def execute_plan(self, plan: Any) -> None:
        """
        Executes instructions using three-tier priority system:
        
        1. COORDINATES: Pre-mapped locations from points.json (fastest)
        2. APP INDEX: Known installed apps from scanner.py (fast)
        3. VISION: OCR text search on screen (flexible but slower)
        
        This balances speed vs. flexibility: 
        - Known targets are instant (no vision overhead)
        - Unknown apps use Windows Search (blind master)
        - Dynamic text uses OCR (when needed)
        """
        try:
            # Respect cancellation before executing any action
            if isinstance(plan, dict) and plan.get("action") != "stop" and self.cancel_event.is_set():
                print("⏸️  CANCELLED: Ignoring action due to stop signal")
                log_file.write("⏸️  CANCELLED: Ignoring action due to stop signal\n")
                log_file.flush()
                return
            # If the LLM returns pure text, just speak it
            if isinstance(plan, str):
                print(f"📝 SPEECH: {plan}")
                log_file.write(f"📝 SPEECH: {plan}\n")
                log_file.flush()
                self.say(plan)
                return

            # If JSON (System 2 Action)
            print(f"🎯 EXECUTING: {plan}")
            log_file.write(f"🎯 EXECUTING: {plan}\n")
            log_file.flush()
            
            if "speech" in plan:
                self.say(plan['speech'])
            
            if "action" in plan:
                action = plan['action']
                
                # ===== CLICK ACTION =====
                if action == "click":
                    target_name = plan.get('target_name') or plan.get('target')
                    target_text = plan.get('target_text') or plan.get('target')
                    x = plan.get('x', 0)
                    y = plan.get('y', 0)
                    
                    coords = None
                    
                    # TIER 1: Coordinate Map (Pre-mapped locations)
                    if target_name and target_name in self.known_points:
                        coords = self.known_points[target_name]
                        x, y = coords['x'], coords['y']
                        print(f"⚡ TIER 1 (Coordinates): Using known location '{target_name}' ({x}, {y})")
                    
                    # TIER 2: Vision (OCR text search)
                    elif target_text:
                        print(f"🔍 TIER 2 (Vision): Searching for text '{target_text}'...")
                        coords = find_text_on_screen(target_text, debug=True)
                        if coords:
                            x, y = coords
                            print(f"👁️  TIER 2 (Vision): Found '{target_text}' @ ({x}, {y})")
                        else:
                            print(f"❌ TIER 2 (Vision): Text '{target_text}' not visible")
                            self.say(f"I cannot find {target_text} on the screen.")
                            return
                    
                    # Execute the click if we have coordinates
                    if x > 0 and y > 0:
                        MotorBridge.move_to(x, y)
                        MotorBridge.click()
                        print(f"✓ MOTOR: Clicked at ({x}, {y})")
                    else:
                        print(f"⚠️ MOTOR: No valid coordinates provided")
                
                # ===== OPEN APP ACTION =====
                elif action == "open":
                    app_name = plan.get('app') or plan.get('target_name') or plan.get('target')
                    print(f"🚀 OPEN ACTION DETECTED")
                    print(f"  - App to open: '{app_name}'")
                    print(f"  - App type: {type(app_name)}")
                    log_file.write(f"🚀 OPEN ACTION DETECTED\n")
                    log_file.write(f"  - App to open: '{app_name}'\n")
                    log_file.write(f"  - App type: {type(app_name)}\n")
                    
                    if app_name:
                        try:
                            # Blind Master reflex: Win + type + Enter
                            open_app(app_name)
                            print(f"✓ OPEN SUCCESSFUL: '{app_name}'")
                            log_file.write(f"✓ OPEN SUCCESSFUL: '{app_name}'\n")
                        except Exception as e:
                            print(f"✗ OPEN FAILED: {e}")
                            log_file.write(f"✗ OPEN FAILED: {e}\n")
                    else:
                        self.say("Which app should I open?")
                        log_file.write(f"⚠️ OPEN: No app specified, asking user\n")
                    log_file.flush()
                
                # ===== TYPE ACTION =====
                elif action == "type":
                    text = plan.get('text', '')
                    # Attempt to focus an editor first for reliable typing
                    bring_any_editor_to_front()
                    print(f"⌨️  TYPE ACTION DETECTED")
                    print(f"  - Text to type: '{text}'")
                    print(f"  - Text length: {len(text)} chars")
                    print(f"  - Text type: {type(text)}")
                    log_file.write(f"⌨️  TYPE ACTION DETECTED\n")
                    log_file.write(f"  - Text to type: '{text}'\n")
                    log_file.write(f"  - Text length: {len(text)} chars\n")
                    log_file.write(f"  - Text type: {type(text)}\n")
                    
                    if text:
                        try:
                            MotorBridge.type_text(text)
                            print(f"✓ TYPE SUCCESSFUL: '{text}'")
                            log_file.write(f"✓ TYPE SUCCESSFUL: '{text}'\n")
                        except Exception as e:
                            print(f"✗ TYPE FAILED: {e}")
                            log_file.write(f"✗ TYPE FAILED: {e}\n")
                    else:
                        print(f"⚠️ TYPE: Empty text provided")
                        log_file.write(f"⚠️ TYPE: Empty text provided\n")
                    log_file.flush()
                
                # ===== PRESS SPECIAL KEY ACTION =====
                elif action == "press_special_key":
                    key_name = plan.get('key_name') or plan.get('key')
                    if key_name:
                        MotorBridge.press_special(key_name)
                        print(f"⌨️  MOTOR: Pressed special key '{key_name}'")
                        log_file.write(f"⌨️  MOTOR: Pressed special key '{key_name}'\n")
                        log_file.flush()
                    
                # ===== SELECT ACTION =====
                elif action == "select":
                    target = plan.get('target') or plan.get('text')
                    mode = plan.get('mode', 'word')
                    # Focus likely editor before selection
                    bring_any_editor_to_front()
                    print("🔎 SELECT ACTION DETECTED")
                    log_file.write(f"🔎 SELECT ACTION: target={target}, mode={mode}\n")
                    log_file.flush()

                    if mode == 'all':
                        # Attempt Ctrl+A selection
                        try:
                            MotorBridge.press_special('ctrl')
                            MotorBridge.type_text('a')
                            print("✓ SELECT ALL via Ctrl+A")
                            log_file.write("✓ SELECT ALL via Ctrl+A\n")
                        except Exception as e:
                            print(f"✗ SELECT ALL FAILED: {e}")
                            log_file.write(f"✗ SELECT ALL FAILED: {e}\n")
                        log_file.flush()
                    else:
                        if not target:
                            self.say("What text should I select?")
                            return
                        # Phrase selection if spaces present
                        if ' ' in target:
                            region = find_phrase_region(target)
                            if region:
                                x, y, w, h = region
                                start_x = x + 3
                                start_y = y + h // 2
                                end_x = x + w - 3
                                end_y = y + h // 2
                                # Click start to place caret, then Shift+Click end to extend selection
                                MotorBridge.move_to(start_x, start_y)
                                MotorBridge.click()
                                MotorBridge.shift_click(end_x, end_y)
                                print(f"✓ SELECTED phrase region ({x},{y},{w},{h}) for '{target}'")
                                log_file.write(f"✓ SELECTED phrase region ({x},{y},{w},{h}) for '{target}'\n")
                            else:
                                print(f"❌ SELECT PHRASE: '{target}' not found")
                                log_file.write(f"❌ SELECT PHRASE not found: {target}\n")
                        else:
                            coords = find_text_on_screen(target)
                            if coords:
                                x, y = coords
                                MotorBridge.move_to(x, y)
                                MotorBridge.double_click()
                                print(f"✓ SELECTED word near ({x},{y}) for '{target}'")
                                log_file.write(f"✓ SELECTED word near ({x},{y}) for '{target}'\n")
                            else:
                                print(f"❌ SELECT: '{target}' not found on screen")
                                log_file.write(f"❌ SELECT not found: {target}\n")
                        log_file.flush()

                # ===== STOP ACTION =====
                elif action == "stop":
                    self.cancel_event.set()
                    print("🛑 ACTION: Stop received, cancelling ongoing tasks")
                    log_file.write("🛑 ACTION: Stop received, cancelling ongoing tasks\n")
                    log_file.flush()
                    # Provide audible confirmation
                    self.say("Stopping now.")

        except Exception as e:
            err_msg = f"⚠️ BRAIN: Execution Error: {e}"
            print(err_msg)
            log_file.write(err_msg + "\n")
            log_file.flush()
            self.say("I failed to execute that command.")

    def run_action_worker(self) -> None:
        """Serialize execution to avoid overlapping actions; honor stop/cancel."""
        while True:
            plan: Dict[str, Any] = self.action_queue.get()
            try:
                if (
                    isinstance(plan, dict)
                    and plan.get("action") != "stop"
                    and self.cancel_event.is_set()
                ):
                    # Skip non-stop plans when cancelled
                    log_file.write("⏸️  QUEUE: Skipping plan due to cancel\n")
                    log_file.flush()
                    continue
                self.execute_plan(plan)
            finally:
                self.action_queue.task_done()

    def clear_action_queue(self) -> None:
        """Clear pending plans."""
        try:
            while not self.action_queue.empty():
                self.action_queue.get_nowait()
                self.action_queue.task_done()
        except Exception:
            pass

    def normalize_intent(self, text: str) -> str:
        """Normalize STT text: lower, remove filler, correct common mishearings."""
        t: str = (text or "").lower().strip()
        # Remove trailing dots and filler repeats
        t = t.replace("...", " ").replace(".  .  .", " ")
        # Basic filler removal
        for filler in ["please", "can you", "could you", "will you", "would you", "the", "a"]:
            if t.startswith(filler + " "):
                t = t[len(filler) + 1 :]
        # Correct known mishearings
        for wrong, right in self.intent_corrections.items():
            if wrong in t:
                t = t.replace(wrong, right)
        return t


if __name__ == "__main__":
    try:
        brain = VelocityBrain()
        # Keep main thread alive
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("🧠 BRAIN: Sleeping...")

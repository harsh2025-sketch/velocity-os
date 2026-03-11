"""
VELOCITY Planner Module
System-2 cognitive planning using Llama LLM
Transforms user intents into structured action plans
"""

import json
from typing import Dict, Optional, Any

try:
    import ollama
    HAS_OLLAMA: bool = True
except ImportError:
    HAS_OLLAMA = False
    print("[PLANNER] Ollama not installed. Using mock planner.")


# ============= SYSTEM PROMPT =============
PLANNER_SYSTEM_PROMPT: str = """
You are VELOCITY, a sovereign operating system agent. Execute commands, do NOT chat.

CRITICAL - OBEY THESE RULES:
1. Output ONLY raw JSON. No text, no explanations, no markdown, no prose.
2. Start response with { and end with }. Nothing else.
3. Never explain what you're doing. Never return anything except JSON.
4. If user says just text without a verb (e.g., "hello world"), interpret as TYPE command.

ACTION MAPPING - Map user intent to EXACTLY one of these:

IF user says "Open [APP]":
  → {"action": "open", "app": "[APP_NAME]"}

IF user says "Type [TEXT]" or "Write [TEXT]" OR just "[TEXT]" (any text without verb):
  → {"action": "type", "text": "[EXACT_TEXT]"}
  
IF user says "Click [TEXT]" or "Click the [TEXT]":
  → {"action": "click", "target": "[TEXT_TO_FIND]"}

IF user says "Select [TEXT]" or "Highlight [TEXT]":
  → {"action": "select", "target": "[TEXT_TO_FIND]"}

IF user says "Select all":
  → {"action": "select", "mode": "all"}

IF user says "Search [QUERY]" or asks a question:
  → {"action": "web_search", "query": "[QUERY]"}

IF user says "Stop", "Cancel", or "Abort":
  → {"action": "stop"}

CRITICAL EXAMPLES:
- User: "hello world"
  YOU MUST OUTPUT: {"action": "type", "text": "hello world"}

- User: "Type hello world" 
  YOU MUST OUTPUT: {"action": "type", "text": "hello world"}

- User: "Hello world"
  YOU MUST OUTPUT: {"action": "type", "text": "Hello world"}

- User: "Click the Login button"
  YOU MUST OUTPUT: {"action": "click", "target": "Login button"}

- User: "Select hello"
  YOU MUST OUTPUT: {"action": "select", "target": "hello"}

- User: "Select all"
  YOU MUST OUTPUT: {"action": "select", "mode": "all"}

- User: "Open Notepad"
  YOU MUST OUTPUT: {"action": "open", "app": "Notepad"}

- User: "Search for Python"
  YOU MUST OUTPUT: {"action": "web_search", "query": "Python"}

- User: "Stop"
  YOU MUST OUTPUT: {"action": "stop"}

REMEMBER: Output ONLY JSON. No chat. No prose. No explanations. ALWAYS return valid JSON.
"""


class Planner:
    """
    System-2 Planner: Deep cognitive processing using LLM.
    Turns user intents into structured JSON action plans.
    
    Conversion Note: For C++ translation, use embedded LLM inference library
    (e.g., llama.cpp) instead of external ollama service.
    """

    def __init__(self, model: str = "llama3") -> None:
        """
        Initialize planner with language model.
        
        Args:
            model: Name of ollama model to use
        """
        self.model: str = model
        self.system_prompt: str = PLANNER_SYSTEM_PROMPT

    def _clean_json(self, text: str) -> Dict[str, Any]:
        """
        Extract and parse JSON from model response.
        
        Args:
            text: Raw response text from LLM
            
        Returns:
            Parsed JSON dict, or fallback action if parsing fails
        """
        start: int = text.find("{")
        end: int = text.rfind("}") + 1
        if start == -1 or end <= start:
            # No JSON found - fallback to speech
            print(f"⚠️ NO JSON FOUND in response: {text[:100]}")
            return {"action": "speak", "text": text}
        try:
            parsed: Dict[str, Any] = json.loads(text[start:end])
            # If we got an empty dict, log it
            if not parsed:
                print(f"⚠️ EMPTY JSON DICT RETURNED")
                return {"action": "speak", "text": "I didn't understand that."}
            return parsed
        except json.JSONDecodeError as e:
            print(f"⚠️ JSON PARSE ERROR: {text} | Error: {e}")
            return {"action": "speak", "text": "I had a brain glitch."}

    def decide(self, user_intent: str, context: str = "") -> Dict[str, Any]:
        """
        Plan action based on user intent.
        
        Args:
            user_intent: User's command text
            context: Screen context (optional)
            
        Returns:
            Action plan as dict
            
        NOTE: For C++ conversion, integrate llama.cpp or similar
        inline inference instead of external ollama process
        """
        if not HAS_OLLAMA:
            return {"action": "speak", "text": user_intent}

        prompt: str = f"""
{self.system_prompt}

USER COMMAND: "{user_intent}"
SCREEN: "{context}"

RESPONSE (JSON ONLY):
"""

        try:
            response: Dict[str, Any] = ollama.generate(
                model=self.model, prompt=prompt
            )
            text: str = response.get("response", "").strip()
            return self._clean_json(text)
        except Exception as e:
            return {"action": "speak", "text": f"Planner error: {e}"}


# Legacy WizardPlanner retained for compatibility
class WizardPlanner:
    """Legacy planner for compatibility - may be removed in future"""

    def __init__(self, bridge: Optional[Any]) -> None:
        """
        Initialize wizard planner.
        
        Args:
            bridge: Optional async bridge for command execution
        """
        self.bridge: Optional[Any] = bridge
        self.model: str = "llama3"

    async def plan_and_execute(self, goal: str) -> None:
        """
        Plan and execute goal using async bridge.
        
        Args:
            goal: High-level goal description
        """
        if not HAS_OLLAMA:
            print(f"[WIZARD] Would plan for: {goal}")
            print("[WIZARD] Install ollama: pip install ollama")
            return

        prompt: str = f"""
Break this goal into robot commands: '{goal}'
Commands: MOVE X Y, CLICK, TYPE text
Respond ONLY with JSON: {{"steps": ["MOVE 100 100", "CLICK"]}}
"""

        try:
            response: Dict[str, Any] = ollama.generate(
                model=self.model, prompt=prompt
            )
            text: str = response.get("response", "{}")

            plan: Optional[Dict[str, Any]] = None
            start: int = text.find("{")
            end: int = text.rfind("}") + 1
            if start >= 0 and end > start:
                plan = json.loads(text[start:end])

            if plan:
                print(f"[WIZARD] Plan: {plan.get('steps')}")
                if self.bridge:
                    for step in plan.get("steps", []):
                        await self.bridge.send_command(step)
                else:
                    for step in plan.get("steps", []):
                        print(f"[WIZARD] Would execute: {step}")
            else:
                print(f"[WIZARD] No valid plan in response")
        except Exception as e:
            print(f"[WIZARD] Error: {e}")

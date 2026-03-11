#!/usr/bin/env python3
"""
Debug script to test what Llama-3 actually outputs for various commands.
This helps us understand why planner is misbehaving.
"""

import json
try:
    import ollama
except ImportError:
    print("❌ Ollama not installed. Install with: pip install ollama")
    exit(1)

# Test system prompt
system_prompt = """
You are VELOCITY, a sovereign operating system agent. Execute commands, do NOT chat.

CRITICAL - OBEY THESE RULES:
1. Output ONLY raw JSON. No text, no explanations, no markdown, no prose.
2. Start response with { and end with }. Nothing else.
3. Never explain what you're doing. Never return anything except JSON.

ACTION MAPPING - Map user intent to EXACTLY one of these:

IF user says "Open [APP]":
  → {"action": "open", "app": "[APP_NAME]"}

IF user says "Type [TEXT]" or "Write [TEXT]":
  → {"action": "type", "text": "[EXACT_TEXT]"}
  
IF user says "Click [TEXT]" or "Click the [TEXT]":
  → {"action": "click", "target": "[TEXT_TO_FIND]"}

IF user says "Search [QUERY]":
  → {"action": "web_search", "query": "[QUERY]"}

IF user asks a question or wants information:
  → {"action": "web_search", "query": "[QUESTION_AS_QUERY]"}

CRITICAL EXAMPLES:
- User: "Type hello world" 
  YOU MUST OUTPUT: {"action": "type", "text": "hello world"}
  NOT: definitions, explanations, or anything else

- User: "Click the Login button"
  YOU MUST OUTPUT: {"action": "click", "target": "Login button"}

- User: "Open Notepad"
  YOU MUST OUTPUT: {"action": "open", "app": "Notepad"}

REMEMBER: Output ONLY JSON. No chat. No prose. No explanations.
"""

test_commands = [
    "Type hello world",
    "Open Notepad",
    "Click the hello text",
    "Search weather today",
]

print("\n" + "="*70)
print("🧪 TESTING LLAMA-3 PLANNER OUTPUT")
print("="*70)

for command in test_commands:
    print(f"\n📝 User command: \"{command}\"")
    
    prompt = f"""
{system_prompt}

USER COMMAND: "{command}"
SCREEN: "Notepad open"

RESPONSE (JSON ONLY):
"""
    
    try:
        response = ollama.generate(model="llama3", prompt=prompt)
        text = response.get("response", "").strip()
        
        print(f"📤 Raw output:\n{text}\n")
        
        # Try to extract JSON
        start = text.find("{")
        end = text.rfind("}") + 1
        if start >= 0 and end > start:
            try:
                json_obj = json.loads(text[start:end])
                print(f"✅ Parsed JSON: {json_obj}")
            except json.JSONDecodeError as e:
                print(f"❌ JSON parse error: {e}")
                print(f"   Extracted text: {text[start:end]}")
        else:
            print(f"❌ No JSON found in response")
            
    except Exception as e:
        print(f"❌ Error: {e}")

print("\n" + "="*70)
print("If you see explanations or non-JSON output above, that's the problem!")
print("The system prompt needs to be stronger to force JSON-only output.")
print("="*70 + "\n")

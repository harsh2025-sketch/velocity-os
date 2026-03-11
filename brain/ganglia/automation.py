"""
VELOCITY Automation Module
Fast reflex logic for common commands without LLM overhead.
Implements pattern matching for: App opening, Web searches, System controls.

NOTE: Designed for direct C++ translation with explicit types and patterns.
"""

import os
import subprocess
import webbrowser
from typing import Optional, Dict, Union
from difflib import get_close_matches


# ============= CONFIGURATION CONSTANTS =============
# Fast, hardcoded map of common apps to their executables
APP_MAP: Dict[str, str] = {
    "notepad": "notepad.exe",
    "calculator": "calc.exe",
    "calc": "calc.exe",
    "chrome": "chrome.exe",
    "edge": "msedge.exe",
    "firefox": "firefox.exe",
    "explorer": "explorer.exe",
    "file explorer": "explorer.exe",
    "cmd": "cmd.exe",
    "command prompt": "cmd.exe",
    "terminal": "wt.exe",
    "windows terminal": "wt.exe",
    "powershell": "powershell.exe",
    "spotify": os.path.expandvars(r"%APPDATA%\Spotify\Spotify.exe")
    if os.path.exists(os.path.expandvars(r"%APPDATA%\Spotify\Spotify.exe"))
    else "spotify.exe",
    "vscode": "code",
    "visual studio code": "code",
    "vs code": "code",
    "paint": "mspaint.exe",
    "notepad++": "notepad++.exe",
    "vlc": "vlc.exe",
}

# Fuzzy matching threshold
FUZZY_MATCH_THRESHOLD: float = 0.6
MAX_FUZZY_MATCHES: int = 1

# System control key codes
VOLUME_MUTE_CODE: int = 0xAD
VOLUME_UP_CODE: int = 0xAF
VOLUME_DOWN_CODE: int = 0xAE
MEDIA_PLAY_PAUSE_CODE: int = 0xB3


def execute_reflex_command(
    intent: str, strict: bool = True
) -> Optional[Union[str, Dict[str, Union[str, int]]]]:
    """
    Fast reflex logic - no AI thinking required.
    Returns action dict for system execution or text response.
    Returns None if no reflex matches (fallback to LLM).
    
    Args:
        intent: User's command text (normalized/lowercased)
        strict: If True, require explicit verb prefixes (e.g., "open ")
        
    Returns:
        - String: Speech response
        - Dict: Action plan for execution
        - None: No reflex matched, try LLM
        
    NOTE: All control paths must return explicit types for C++ conversion
    """
    intent = intent.lower().strip()

    # ===== APP OPENING =====
    if intent.startswith("open "):
        target: str = intent[len("open "):].strip()
        return open_app(target)

    if not strict:
        # Non-strict mode allows softer phrasing
        if " open" in intent:
            target = intent.split("open")[-1].strip().rstrip("?")
            return open_app(target)

    # ===== WEB SEARCH =====
    if intent.startswith("search "):
        query: str = intent.replace("search", "").strip()
        webbrowser.open(f"https://www.google.com/search?q={query}")
        return f"Searching for {query}."

    if intent.startswith("google "):
        query = intent.replace("google", "").strip()
        webbrowser.open(f"https://www.google.com/search?q={query}")
        return f"Searching for {query}."

    if not strict:
        if " search for " in intent:
            query = intent.split("search for")[-1].strip()
            webbrowser.open(f"https://www.google.com/search?q={query}")
            return f"Searching for {query}."
        if " google " in intent:
            query = intent.split("google")[-1].strip()
            webbrowser.open(f"https://www.google.com/search?q={query}")
            return f"Searching for {query}."

    # ===== SYSTEM CONTROLS =====
    if "mute" in intent:
        return {"action": "press_special_key", "code": VOLUME_MUTE_CODE}

    if "unmute" in intent:
        return {"action": "press_special_key", "code": VOLUME_UP_CODE}

    if "volume up" in intent or "louder" in intent:
        return {"action": "press_special_key", "code": VOLUME_UP_CODE}

    if "volume down" in intent or "quieter" in intent:
        return {"action": "press_special_key", "code": VOLUME_DOWN_CODE}

    if "play" in intent and "music" in intent:
        return {"action": "press_special_key", "code": MEDIA_PLAY_PAUSE_CODE}

    # ===== SYSTEM ACTIONS =====
    if "lock" in intent or "sleep" in intent:
        os.system("rundll32.exe user32.dll,LockWorkStation")
        return "Locking system."

    if "shutdown" in intent or "turn off" in intent:
        return "Please confirm shutdown manually for safety."

    # No reflex matched
    return None


def open_app(app_name: str) -> Union[str, None]:
    """
    Smart app opener with fuzzy matching.
    
    Args:
        app_name: Name of application to open
        
    Returns:
        String response indicating success/failure, or None on error
        
    Conversion Note: When converting to C++, replace get_close_matches with
    a simple fuzzy string distance algorithm (e.g., Levenshtein distance)
    """
    app_name = app_name.lower().strip()

    # Find closest match in APP_MAP
    matches: list = get_close_matches(
        app_name, APP_MAP.keys(), n=MAX_FUZZY_MATCHES, cutoff=FUZZY_MATCH_THRESHOLD
    )

    if matches:
        executable: str = APP_MAP[matches[0]]
        try:
            # Popen is non-blocking - doesn't freeze the brain
            subprocess.Popen(executable, shell=True)
            return f"Opening {matches[0]}."
        except Exception as e:
            return f"Failed to open {matches[0]}: {str(e)}"
    else:
        # Fallback: Try generic Windows 'start' command
        try:
            subprocess.Popen(f"start {app_name}", shell=True)
            return f"Attempting to launch {app_name}."
        except Exception as e:
            return f"I don't know how to open {app_name}: {str(e)}"

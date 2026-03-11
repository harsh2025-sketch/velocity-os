"""
Velocity Reflex Module: Ultra-fast automated responses
Implements the "Blind Master" reflex for app launching via keyboard
"""

import time
from typing import Optional
from brain.motor_bridge import MotorBridge


# Configuration constants
DEFAULT_MENU_WAIT: float = 0.35  # Wait after Win key for Start menu
DEFAULT_SEARCH_WAIT: float = 0.7  # Wait after typing for search results


def open_app(
    app_name: str,
    wait_menu: float = DEFAULT_MENU_WAIT,
    wait_search: float = DEFAULT_SEARCH_WAIT,
) -> None:
    """
    Blind Master reflex: Open any app via keyboard (Win -> type -> Enter)
    
    This reflex doesn't require app registry lookups or vision.
    Works for any installed Windows application.
    
    Args:
        app_name: Application name to launch
        wait_menu: Pause time after Win key for Start menu to appear
        wait_search: Pause time after typing app name for search results
    
    NOTE: This function is designed to translate directly to C++ with:
    - Explicit parameter types
    - No dynamic behavior
    - Pure function semantics
    """
    print(f"🚀 REFLEX: Launching {app_name} via keyboard...")

    # 1. Open Start Menu (Windows key)
    MotorBridge.type_keys(["win"])
    time.sleep(wait_menu)

    # 2. Type app name
    MotorBridge.type_keys(app_name)
    time.sleep(wait_search)

    # 3. Hit Enter
    MotorBridge.type_keys(["enter"])

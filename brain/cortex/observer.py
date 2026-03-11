"""
VELOCITY Cortex - Observer
Phase 3: Record user actions for imitation learning.
"""

from __future__ import annotations

import json
import os
from datetime import datetime
from typing import Dict, List, Optional, Any

try:
    from pynput import mouse, keyboard
    HAS_PYNPUT: bool = True
except Exception:
    HAS_PYNPUT = False

from brain.senses.ui_parser import StructuralLayer


PROJECT_ROOT: str = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
OBSERVATIONS_DIR: str = os.path.join(PROJECT_ROOT, "brain", "memory", "observations")


class Observer:
    """
    Records mouse/keyboard events with UI element context.
    """

    def __init__(self) -> None:
        self.is_recording: bool = False
        self.actions: List[Dict[str, Any]] = []
        self.start_time: Optional[datetime] = None
        self.ui_parser = StructuralLayer()
        self.mouse_listener = None
        self.keyboard_listener = None

    def start_recording(self) -> None:
        if not HAS_PYNPUT:
            raise RuntimeError("pynput is not installed")
        self.is_recording = True
        self.actions = []
        self.start_time = datetime.now()

        self.mouse_listener = mouse.Listener(
            on_click=self._on_click,
            on_scroll=self._on_scroll,
        )
        self.keyboard_listener = keyboard.Listener(
            on_press=self._on_key_press,
        )
        self.mouse_listener.start()
        self.keyboard_listener.start()

    def stop_recording(self) -> Dict[str, Any]:
        if not self.is_recording:
            return {}
        self.is_recording = False
        if self.mouse_listener:
            self.mouse_listener.stop()
        if self.keyboard_listener:
            self.keyboard_listener.stop()
        return self._build_summary()

    def _build_summary(self) -> Dict[str, Any]:
        duration = 0.0
        if self.start_time:
            duration = (datetime.now() - self.start_time).total_seconds()
        return {
            "timestamp": self.start_time.isoformat() if self.start_time else datetime.now().isoformat(),
            "duration_seconds": duration,
            "action_count": len(self.actions),
            "actions": self.actions,
        }

    def save_observation(self, observation: Dict[str, Any], name: str) -> str:
        os.makedirs(OBSERVATIONS_DIR, exist_ok=True)
        filename = f"{name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        path = os.path.join(OBSERVATIONS_DIR, filename)
        with open(path, "w", encoding="utf-8") as f:
            json.dump(observation, f, indent=2)
        return path

    def _elapsed(self) -> float:
        if not self.start_time:
            return 0.0
        return (datetime.now() - self.start_time).total_seconds()

    def _on_click(self, x: int, y: int, button: Any, pressed: bool) -> None:
        if not self.is_recording or not pressed:
            return
        element = self.ui_parser.find_element_at(x, y)
        self.actions.append(
            {
                "type": "click",
                "x": x,
                "y": y,
                "button": str(button),
                "element": element,
                "timestamp": self._elapsed(),
            }
        )

    def _on_scroll(self, x: int, y: int, dx: int, dy: int) -> None:
        if not self.is_recording:
            return
        self.actions.append(
            {
                "type": "scroll",
                "x": x,
                "y": y,
                "dx": dx,
                "dy": dy,
                "timestamp": self._elapsed(),
            }
        )

    def _on_key_press(self, key: Any) -> None:
        if not self.is_recording:
            return
        self.actions.append(
            {
                "type": "key_press",
                "key": str(key),
                "timestamp": self._elapsed(),
            }
        )

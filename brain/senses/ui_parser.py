"""
VELOCITY Senses - UI Parser (Structural Layer)
Uses Windows UI Automation to locate UI elements by name/type.
Gracefully degrades if uiautomation is not installed.
"""

from __future__ import annotations

import json
import os
from datetime import datetime
from typing import Dict, Optional, Any


try:
    import uiautomation as auto
    HAS_UIAUTOMATION: bool = True
except Exception:
    HAS_UIAUTOMATION = False


PROJECT_ROOT: str = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
ELEMENT_CACHE_PATH: str = os.path.join(PROJECT_ROOT, "brain", "memory", "element_cache.json")


class StructuralLayer:
    """
    Structural layer for UI Automation parsing.
    """

    def __init__(self, cache_path: str = ELEMENT_CACHE_PATH, cache_ttl_seconds: int = 300) -> None:
        self.cache_path = cache_path
        self.cache_ttl_seconds = cache_ttl_seconds
        self.cache = self._load_cache()

    def _load_cache(self) -> Dict[str, Any]:
        if not os.path.exists(self.cache_path):
            return {"_cache": {}}
        try:
            with open(self.cache_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return {"_cache": {}}

    def _save_cache(self) -> None:
        with open(self.cache_path, "w", encoding="utf-8") as f:
            json.dump(self.cache, f, indent=2)

    def _cache_element(self, app_name: str, element_name: str, element_data: Dict[str, Any]) -> None:
        cache_root = self.cache.setdefault("_cache", {})
        app_cache = cache_root.setdefault(app_name, {})
        app_cache[element_name] = {
            "coords": [element_data["x"], element_data["y"]],
            "bounds": element_data.get("bounds"),
            "control_type": element_data.get("control_type"),
            "last_seen": element_data.get("timestamp"),
            "stable": True,
            "hit_count": app_cache.get(element_name, {}).get("hit_count", 0) + 1,
        }
        self._save_cache()

    def find_element(self, window_name: str, element_name: str, control_type: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """
        Find UI element by name/type using UIA.
        Returns a dict with coordinates and bounds, or None.
        """
        if not HAS_UIAUTOMATION:
            return None

        try:
            window = auto.WindowControl(searchDepth=1, Name=window_name)
            if not window.Exists(0.5):
                return None

            element = None
            if control_type == "Button":
                element = window.ButtonControl(Name=element_name)
            elif control_type == "TextBox":
                element = window.EditControl(Name=element_name)
            else:
                element = window.Control(Name=element_name)

            if not element or not element.Exists(0.5):
                return None

            rect = element.BoundingRectangle
            result = {
                "name": element.Name,
                "x": rect.xcenter(),
                "y": rect.ycenter(),
                "bounds": {
                    "left": rect.left,
                    "top": rect.top,
                    "right": rect.right,
                    "bottom": rect.bottom,
                },
                "control_type": element.ControlTypeName,
                "timestamp": datetime.now().isoformat(),
            }

            self._cache_element(window_name, element_name, result)
            return result
        except Exception:
            return None

    def find_element_at(self, x: int, y: int) -> Optional[Dict[str, Any]]:
        """Get element information from a screen coordinate."""
        if not HAS_UIAUTOMATION:
            return None
        try:
            control = auto.ControlFromPoint(x, y)
            if not control:
                return None
            rect = control.BoundingRectangle
            return {
                "name": control.Name,
                "control_type": control.ControlTypeName,
                "bounds": {
                    "left": rect.left,
                    "top": rect.top,
                    "right": rect.right,
                    "bottom": rect.bottom,
                },
            }
        except Exception:
            return None

    def try_structural(self, intent: str, window_name: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """
        Attempt a structural match for the given intent.
        This is a placeholder mapping that expects intent to contain the element name.
        """
        if not HAS_UIAUTOMATION:
            return None

        if not window_name:
            try:
                window_name = auto.GetForegroundControl().Name
            except Exception:
                window_name = ""

        target = intent.strip()
        if not target:
            return None

        result = self.find_element(window_name, target)
        if not result:
            return None

        return {
            "skill_id": f"{window_name}:{target}",
            "method": "structural",
            "coords": (result["x"], result["y"]),
            "confidence": 0.85,
            "avg_latency_ms": 120,
        }
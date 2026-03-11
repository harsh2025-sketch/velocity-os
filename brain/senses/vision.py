"""
VELOCITY Senses - Vision Layer
Template matching (OpenCV) + VLM fallback (Ollama).
Gracefully degrades if dependencies are unavailable.
"""

from __future__ import annotations

import base64
import os
import re
from typing import Optional, Tuple, Dict, Any


try:
    import cv2
    import numpy as np
    HAS_OPENCV: bool = True
except Exception:
    HAS_OPENCV = False

try:
    import pyautogui
    HAS_PYAUTOGUI: bool = True
except Exception:
    HAS_PYAUTOGUI = False

try:
    import ollama
    HAS_OLLAMA: bool = True
except Exception:
    HAS_OLLAMA = False


PROJECT_ROOT: str = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
TEMPLATES_DIR: str = os.path.join(PROJECT_ROOT, "brain", "memory", "vision_templates")


class VisualLayer:
    """
    Visual layer with template matching and VLM-based detection.
    """

    def __init__(self, model: str = "llava") -> None:
        self.model = model

    def _get_screenshot(self) -> Optional["np.ndarray"]:
        if not HAS_PYAUTOGUI or not HAS_OPENCV:
            return None
        screenshot = pyautogui.screenshot()
        image = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)
        return image

    def _find_template(self, screenshot: "np.ndarray", template_path: str, threshold: float = 0.8) -> Optional[Tuple[int, int]]:
        if not HAS_OPENCV:
            return None
        if not os.path.exists(template_path):
            return None
        template = cv2.imread(template_path)
        if template is None:
            return None
        result = cv2.matchTemplate(screenshot, template, cv2.TM_CCOEFF_NORMED)
        _, max_val, _, max_loc = cv2.minMaxLoc(result)
        if max_val >= threshold:
            h, w = template.shape[:2]
            return (max_loc[0] + w // 2, max_loc[1] + h // 2)
        return None

    def _find_vlm(self, description: str, screenshot: "np.ndarray") -> Optional[Tuple[int, int]]:
        if not HAS_OLLAMA or not HAS_OPENCV:
            return None
        _, buffer = cv2.imencode(".png", screenshot)
        image_b64 = base64.b64encode(buffer).decode("utf-8")

        prompt = (
            "Look at this screenshot and locate the UI element described below. "
            "Return ONLY coordinates in the format (x, y) for the center point, "
            "or NOT_FOUND if it is not visible.\n\n"
            f"Target: {description}"
        )

        try:
            response = ollama.generate(
                model=self.model,
                prompt=prompt,
                images=[image_b64],
                stream=False,
            )
            text = response.response.strip()
            if text == "NOT_FOUND":
                return None
            match = re.search(r"\((\d+),\s*(\d+)\)", text)
            if match:
                return (int(match.group(1)), int(match.group(2)))
        except Exception:
            return None
        return None

    def try_visual(self, intent: str) -> Optional[Dict[str, Any]]:
        if not HAS_PYAUTOGUI or not HAS_OPENCV:
            return None
        screenshot = self._get_screenshot()
        if screenshot is None:
            return None

        # Template matching first (fast)
        template_path = os.path.join(TEMPLATES_DIR, f"{intent}.png")
        coords = self._find_template(screenshot, template_path, threshold=0.8)
        if coords:
            return {
                "skill_id": f"visual:{intent}",
                "method": "visual_template",
                "coords": coords,
                "confidence": 0.85,
                "avg_latency_ms": 200,
            }

        # VLM fallback
        coords = self._find_vlm(intent, screenshot)
        if coords:
            return {
                "skill_id": f"visual:{intent}",
                "method": "visual_vlm",
                "coords": coords,
                "confidence": 0.70,
                "avg_latency_ms": 2000,
            }
        return None
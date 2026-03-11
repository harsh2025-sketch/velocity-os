"""
VELOCITY Cortex - Cross-Layer Learning (CLL)
Phase 2: Store visual hints when visual succeeds to speed future retries.
"""

from __future__ import annotations

import base64
import json
import os
from datetime import datetime
from typing import Dict, Optional


PROJECT_ROOT: str = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
SKILLS_PATH: str = os.path.join(PROJECT_ROOT, "brain", "memory", "skills.json")


class CrossLayerLearning:
    """
    Stores visual hints inside skills.json for faster future detection.
    """

    def __init__(self) -> None:
        self.skills = self._load_skills()

    def _load_skills(self) -> Dict:
        if not os.path.exists(SKILLS_PATH):
            return {}
        try:
            with open(SKILLS_PATH, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return {}

    def _save_skills(self) -> None:
        with open(SKILLS_PATH, "w", encoding="utf-8") as f:
            json.dump(self.skills, f, indent=2)

    def store_visual_hint(self, skill_id: str, screenshot_bytes: bytes, confidence: float) -> None:
        if skill_id not in self.skills:
            return
        skill = self.skills[skill_id]
        hints = skill.setdefault("cross_layer_hints", {})
        hints["visual_template"] = {
            "screenshot": base64.b64encode(screenshot_bytes).decode("utf-8"),
            "timestamp": datetime.now().isoformat(),
            "confidence": confidence,
            "use_count": 0,
        }
        self._save_skills()

    def get_visual_hint(self, skill_id: str, max_age_seconds: int = 300) -> Optional[bytes]:
        skill = self.skills.get(skill_id)
        if not skill:
            return None
        hint = skill.get("cross_layer_hints", {}).get("visual_template")
        if not hint:
            return None
        try:
            ts = datetime.fromisoformat(hint.get("timestamp"))
            age = (datetime.now() - ts).seconds
            if age > max_age_seconds:
                return None
        except Exception:
            return None

        hint["use_count"] = hint.get("use_count", 0) + 1
        self._save_skills()
        return base64.b64decode(hint.get("screenshot", ""))
"""
VELOCITY Cortex - Synthesizer
Phase 3: Convert observation logs into skills.json entries.
"""

from __future__ import annotations

import json
import os
from datetime import datetime
from typing import Dict, Any, Optional, List

try:
    import ollama
    HAS_OLLAMA: bool = True
except Exception:
    HAS_OLLAMA = False


PROJECT_ROOT: str = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
SKILLS_PATH: str = os.path.join(PROJECT_ROOT, "brain", "memory", "skills.json")


class Synthesizer:
    """
    Converts observation logs to structured skill entries.
    """

    def __init__(self, model: str = "llama3") -> None:
        self.model = model
        self.skills = self._load_skills()

    def _load_skills(self) -> Dict[str, Any]:
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

    def _format_actions(self, actions: List[Dict[str, Any]]) -> str:
        lines: List[str] = []
        for idx, action in enumerate(actions, 1):
            if action.get("type") == "click":
                element = action.get("element", {}) or {}
                name = element.get("name") or f"({action.get('x')},{action.get('y')})"
                lines.append(f"{idx}. Clicked {name}")
            elif action.get("type") == "key_press":
                lines.append(f"{idx}. Pressed {action.get('key')}")
            elif action.get("type") == "scroll":
                lines.append(f"{idx}. Scrolled ({action.get('dx')},{action.get('dy')})")
        return "\n".join(lines)

    def generate_skill(self, observation: Dict[str, Any], skill_name: str) -> Optional[Dict[str, Any]]:
        if not HAS_OLLAMA:
            return None
        actions_text = self._format_actions(observation.get("actions", []))
        prompt = (
            "You are converting user action logs into a JSON skill.\n"
            "Return ONLY valid JSON.\n\n"
            f"Actions:\n{actions_text}\n\n"
            "Schema:\n"
            "{\n"
            "  \"name\": \"skill_name\",\n"
            "  \"description\": \"what this does\",\n"
            "  \"type\": \"composite\",\n"
            "  \"steps\": [ {\"action\": \"click_element\"} ],\n"
            "  \"parameters\": {},\n"
            "  \"success_conditions\": []\n"
            "}\n"
        )
        try:
            response = ollama.generate(model=self.model, prompt=prompt, stream=False)
            skill_json = json.loads(response.response)
            skill = self._enhance_skill(skill_json, skill_name)
            self.skills[skill_name] = skill
            self._save_skills()
            return skill
        except Exception:
            return None

    def _enhance_skill(self, skill: Dict[str, Any], skill_name: str) -> Dict[str, Any]:
        skill["name"] = skill_name
        skill["created"] = datetime.now().isoformat()
        skill["confidence"] = 0.3
        skill["success_count"] = 0
        skill["fail_count"] = 0
        if skill.get("type") == "composite":
            skill["methods"] = [
                {
                    "type": "composite",
                    "action": "sequence_execute",
                    "steps": skill.get("steps", []),
                    "confidence": 0.3,
                }
            ]
        return skill

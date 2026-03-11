"""
VELOCITY Cortex - Learning Engine
Phase 2: RL confidence updates with context modifiers and failure logging.
"""

from __future__ import annotations

import json
import os
from datetime import datetime
from typing import Any, Dict, Optional


PROJECT_ROOT: str = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
SKILLS_PATH: str = os.path.join(PROJECT_ROOT, "brain", "memory", "skills.json")
CONFIG_PATH: str = os.path.join(PROJECT_ROOT, "brain", "memory", "processor_config.json")
FAILURE_LOG_PATH: str = os.path.join(PROJECT_ROOT, "brain", "memory", "failure_log.json")


class LearningEngine:
    """
    Reinforcement Learning engine for confidence updates.
    Implements:
    - AFML: Adaptive Failure Mode Learning
    - TCA: Temporal Context Awareness (via context modifiers)
    - FMR: Failure Mode Recommendation logging
    """

    def __init__(self) -> None:
        self.skills = self._load_json(SKILLS_PATH)
        self.config = self._load_json(CONFIG_PATH)
        self.learning_cfg = self.config.get("learning", {})

    def _load_json(self, path: str) -> Dict[str, Any]:
        if not os.path.exists(path):
            return {}
        try:
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return {}

    def _save_skills(self) -> None:
        with open(SKILLS_PATH, "w", encoding="utf-8") as f:
            json.dump(self.skills, f, indent=2)

    def _append_failure_log(self, entry: Dict[str, Any]) -> None:
        log = {"failures": []}
        if os.path.exists(FAILURE_LOG_PATH):
            try:
                with open(FAILURE_LOG_PATH, "r", encoding="utf-8") as f:
                    log = json.load(f)
            except Exception:
                log = {"failures": []}
        log["failures"].append(entry)
        if len(log["failures"]) > 100:
            log["failures"] = log["failures"][-100:]
        with open(FAILURE_LOG_PATH, "w", encoding="utf-8") as f:
            json.dump(log, f, indent=2)

    def _context_modifier(self, context: Optional[Dict[str, Any]]) -> float:
        if not context:
            return 0.0
        modifier = 0.0
        hour = context.get("hour")
        if isinstance(hour, int):
            if 9 <= hour <= 17:
                modifier += 0.05
            elif hour >= 22 or hour <= 6:
                modifier -= 0.1
        if context.get("network_state") == "offline":
            modifier -= 0.2
        if context.get("app_state") == "logged_out":
            modifier -= 0.15
        return modifier

    def update_confidence(
        self,
        skill_id: str,
        success: bool,
        failure_mode: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None,
    ) -> None:
        if skill_id not in self.skills:
            return

        skill = self.skills[skill_id]
        methods = skill.get("methods", [])
        if not methods:
            return

        # Update the first method by default; callers can extend to choose method
        method = methods[0]
        base_conf = method.get("confidence", 0.5)

        # AFML penalties/rewards
        if success:
            delta = self.learning_cfg.get("success_reward", 0.1)
        else:
            if failure_mode == "timeout":
                delta = -0.1
            elif failure_mode == "element_not_found":
                delta = -0.2
            elif failure_mode == "vlm_nonsense":
                delta = -0.4
            elif failure_mode == "access_denied":
                delta = -0.3
            else:
                delta = -self.learning_cfg.get("failure_penalty", 0.2)

        # TCA modifier
        delta += self._context_modifier(context)

        # Clamp confidence
        min_c = self.learning_cfg.get("min_confidence", 0.1)
        max_c = self.learning_cfg.get("max_confidence", 1.0)
        new_conf = max(min_c, min(max_c, base_conf + delta))
        method["confidence"] = new_conf

        # Update counts
        if success:
            method["success_count"] = method.get("success_count", 0) + 1
        else:
            method["fail_count"] = method.get("fail_count", 0) + 1

            if failure_mode:
                self._append_failure_log(
                    {
                        "timestamp": datetime.now().isoformat(),
                        "skill_id": skill_id,
                        "failure_mode": failure_mode,
                        "context": context or {},
                    }
                )

        self._save_skills()
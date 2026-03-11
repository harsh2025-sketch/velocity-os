"""
VELOCITY Cortex - Composite Executor
Phase 3: Execute multi-step composite skills.
"""

from __future__ import annotations

from typing import Dict, Any, List, Optional

from brain.senses.ui_parser import StructuralLayer


class CompositeExecutor:
    """
    Executes composite skills step-by-step.
    """

    def __init__(self) -> None:
        self.ui_parser = StructuralLayer()

    def execute(self, skill: Dict[str, Any], params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        steps: List[Dict[str, Any]] = skill.get("steps", [])
        results: List[Dict[str, Any]] = []
        for step in steps:
            result = self._execute_step(step, params or {})
            results.append(result)
            if not result.get("success"):
                return {
                    "success": False,
                    "steps_executed": len(results),
                    "steps_total": len(steps),
                    "results": results,
                }
        return {
            "success": True,
            "steps_executed": len(results),
            "steps_total": len(steps),
            "results": results,
        }

    def _execute_step(self, step: Dict[str, Any], params: Dict[str, Any]) -> Dict[str, Any]:
        action = step.get("action")
        if action == "click_element":
            window = step.get("window")
            target = step.get("target")
            element = self.ui_parser.find_element(window or "", target or "")
            return {
                "action": action,
                "success": element is not None,
                "coords": (element.get("x"), element.get("y")) if element else None,
            }
        if action == "type_text":
            return {
                "action": action,
                "success": True,
                "text": step.get("text") or params.get("text"),
            }
        return {
            "action": action,
            "success": False,
            "error": "unsupported_action",
        }

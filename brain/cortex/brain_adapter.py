"""
VELOCITY Cortex - Brain Integration Adapter
Phase 4: Wire 3-layer processor into main.py while preserving backward compatibility.
"""

from __future__ import annotations

import json
import os
from typing import Any, Dict, Optional

from brain.cortex.processor import CortexProcessor


PROJECT_ROOT: str = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
EXECUTION_LOG_PATH: str = os.path.join(PROJECT_ROOT, "brain", "memory", "cortex_execution_log.json")


class BrainIntegrationAdapter:
    """
    Adapter between main.py (old reflex→LLM) and new CortexProcessor.
    
    Purpose:
    - Wrap CortexProcessor to return action_plan format compatible with main.py
    - Log all executions for Phase 4+ analytics
    - Provide fallback to old planner if processor fails
    
    Flow:
    1. Intent arrives in process_sensory_input()
    2. Adapter.process_intent() calls CortexProcessor
    3. Returns action_plan {action, target, params} for motor_bridge
    4. Main logs execution to execution_history.json
    """

    def __init__(self) -> None:
        self.processor = CortexProcessor()
        self.execution_count = 0
        self.failure_count = 0

    def process_intent(
        self,
        user_intent: str,
        app_context: str = "unknown",
    ) -> Optional[Dict[str, Any]]:
        """
        Route intent through 3-layer processor.
        
        Args:
            user_intent: User's spoken intent (e.g., "open chrome")
            app_context: Currently active application
            
        Returns:
            action_plan dict compatible with main.py's execute_plan()
            {
                "action": "click_element" | "type_text" | "hotkey" | ...,
                "target": element_id or coordinates,
                "params": {},
                "_source": "cortex",  # Track origin
                "_skill_id": "chrome_new_tab",  # For learning
                "_confidence": 0.85,  # For priority
            }
        """
        try:
            self.execution_count += 1

            # Execute through processor
            context = {"app": app_context}
            result = self.processor.execute_with_fallback(
                intent=user_intent,
                context=context,
            )

            if result.get("success"):
                # Convert processor result → action_plan
                action_plan = self._convert_result_to_action(result, user_intent)
                self._log_execution(user_intent, action_plan, "success")
                return action_plan
            else:
                # Processor failed
                self.failure_count += 1
                self._log_execution(user_intent, None, "processor_failed", result.get("reason"))
                return None

        except Exception as e:
            self.failure_count += 1
            self._log_execution(user_intent, None, "exception", str(e))
            return None

    def _convert_result_to_action(
        self, processor_result: Dict[str, Any], original_intent: str
    ) -> Dict[str, Any]:
        """Convert processor output to action_plan format for motor_bridge"""
        return {
            "action": processor_result.get("action", "none"),
            "target": processor_result.get("target"),
            "params": processor_result.get("params", {}),
            "_source": "cortex",
            "_skill_id": processor_result.get("skill_id"),
            "_confidence": processor_result.get("confidence", 0.5),
            "_layer": processor_result.get("layer"),  # Which layer succeeded
            "_original_intent": original_intent,
        }

    def _log_execution(
        self,
        intent: str,
        action: Optional[Dict[str, Any]],
        status: str,
        reason: str = "",
    ) -> None:
        """Log execution to cortex_execution_log.json for analytics"""
        try:
            log_data = {"executions": []}
            if os.path.exists(EXECUTION_LOG_PATH):
                try:
                    with open(EXECUTION_LOG_PATH, "r", encoding="utf-8") as f:
                        log_data = json.load(f)
                except Exception:
                    log_data = {"executions": []}

            entry = {
                "timestamp": self.execution_count,
                "intent": intent,
                "status": status,
                "reason": reason,
                "action": action,
            }
            log_data["executions"].append(entry)

            # Keep last 500 entries
            if len(log_data["executions"]) > 500:
                log_data["executions"] = log_data["executions"][-500:]

            with open(EXECUTION_LOG_PATH, "w", encoding="utf-8") as f:
                json.dump(log_data, f, indent=2)

        except Exception:
            pass  # Silent fail on logging errors

    def get_stats(self) -> Dict[str, Any]:
        """Return adapter statistics for monitoring"""
        return {
            "total_executions": self.execution_count,
            "failures": self.failure_count,
            "success_rate": (
                (self.execution_count - self.failure_count) / self.execution_count
                if self.execution_count > 0
                else 0.0
            ),
        }

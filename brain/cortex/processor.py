"""
VELOCITY Cortex Processor
Implements 3-layer defense with predictive ordering (PLS) and
adaptive failure categorization (AFML scaffolding).
"""

from __future__ import annotations

import json
import os
import time
from typing import Any, Dict, List, Optional, Tuple

from brain.cortex.symbolic import SymbolicLayer
from brain.cortex.learning import LearningEngine
from brain.cortex.temporal_context import TemporalContext
from brain.cortex.diagnostics import FailureDiagnostics
from brain.cortex.cross_layer import CrossLayerLearning
from brain.senses.ui_parser import StructuralLayer
from brain.senses.vision import VisualLayer


PROJECT_ROOT: str = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
SUCCESS_MATRIX_PATH: str = os.path.join(PROJECT_ROOT, "brain", "memory", "success_matrix.json")
EXECUTION_HISTORY_PATH: str = os.path.join(PROJECT_ROOT, "brain", "memory", "execution_history.json")


class CortexProcessor:
    """
    Master loop that tries Symbolic → Structural → Visual (or predicted order).
    """

    def __init__(self) -> None:
        self.symbolic = SymbolicLayer()
        self.structural = StructuralLayer()
        self.visual = VisualLayer()
        self.success_matrix = self._load_success_matrix()
        self.learning = LearningEngine()
        self.context_manager = TemporalContext()
        self.diagnostics = FailureDiagnostics()
        self.cross_layer = CrossLayerLearning()

    def _load_success_matrix(self) -> Dict[str, Any]:
        try:
            with open(SUCCESS_MATRIX_PATH, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return {}

    def _predict_layer_order(self, intent: str, app: str = "unknown") -> List[Tuple[str, Any]]:
        """
        Algorithm 5: Predictive Layer Selection (PLS)
        Returns layer order based on success probabilities.
        """
        app_stats = self.success_matrix.get(app, {})
        intent_key = self._extract_intent_type(intent)
        success_scores = app_stats.get(intent_key, {
            "symbolic": 0.6,
            "structural": 0.7,
            "visual": 0.8,
        })

        layers = [
            ("symbolic", self.symbolic.try_symbolic),
            ("structural", self.structural.try_structural),
            ("visual", self.visual.try_visual),
        ]

        return sorted(layers, key=lambda l: success_scores.get(l[0], 0.5), reverse=True)

    def _extract_intent_type(self, intent: str) -> str:
        lowered = intent.lower().strip()
        if lowered.startswith("new tab") or lowered.startswith("new"):
            return "new_tab"
        verbs = ["open", "close", "play", "pause", "find", "search", "save", "type", "click"]
        for verb in verbs:
            if lowered.startswith(verb):
                return verb
        return "unknown"

    def _categorize_failure(self, error: Exception) -> str:
        """
        Algorithm 1: Adaptive Failure Mode Learning (AFML) scaffolding.
        """
        msg = str(error).lower()
        if "timeout" in msg:
            return "timeout"
        if "not found" in msg or "element" in msg:
            return "element_not_found"
        if "permission" in msg or "access" in msg:
            return "access_denied"
        return "unknown"

    def _append_execution_history(self, entry: Dict[str, Any]) -> None:
        try:
            with open(EXECUTION_HISTORY_PATH, "r", encoding="utf-8") as f:
                history = json.load(f)
        except Exception:
            history = {"executions": []}

        history.setdefault("executions", []).append(entry)
        if len(history["executions"]) > 1000:
            history["executions"] = history["executions"][-1000:]

        with open(EXECUTION_HISTORY_PATH, "w", encoding="utf-8") as f:
            json.dump(history, f, indent=2)

    def execute_with_fallback(self, intent: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Execute intent using 3-layer defense system.
        Returns a result dict describing the chosen method or a request for demonstration.
        """
        context = context or self.context_manager.get_context()
        app = context.get("app", "unknown")
        order = self._predict_layer_order(intent, app=app)

        start = time.time()
        last_failure = None

        for layer_name, layer_fn in order:
            try:
                if layer_name == "structural":
                    result = layer_fn(intent, context.get("window"))
                else:
                    result = layer_fn(intent)

                if result:
                    result.update({
                        "method_used": layer_name,
                        "latency_ms": int((time.time() - start) * 1000),
                        "success": True,
                        "context": context,
                    })
                    self._append_execution_history({
                        "timestamp": time.time(),
                        "intent": intent,
                        "skill_id": result.get("skill_id"),
                        "method_used": layer_name,
                        "latency_ms": result.get("latency_ms"),
                        "success": True,
                    })
                    return result
            except Exception as exc:
                last_failure = self._categorize_failure(exc)
                continue

        failure_payload = {
            "action": "request_demonstration",
            "intent": intent,
            "success": False,
            "failure_mode": last_failure or "unknown",
            "message": f"I couldn't complete '{intent}'. Please show me how to do it.",
        }
        failure_payload["context"] = context
        failure_payload["diagnostic"] = self.diagnostics.diagnose(
            failure_payload["failure_mode"],
            skill_id="unknown",
            context=context,
        )
        self._append_execution_history({
            "timestamp": time.time(),
            "intent": intent,
            "skill_id": "unknown",
            "method_used": "none",
            "latency_ms": int((time.time() - start) * 1000),
            "success": False,
            "error": failure_payload.get("failure_mode"),
        })
        return failure_payload

    def update_with_result(
        self,
        skill_id: str,
        success: bool,
        failure_mode: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Update learning engine with execution outcome."""
        self.learning.update_confidence(
            skill_id=skill_id,
            success=success,
            failure_mode=failure_mode,
            context=context,
        )
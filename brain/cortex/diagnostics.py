"""
VELOCITY Cortex - Failure Diagnostics
Phase 2: Failure Mode Recommendation (FMR).
"""

from __future__ import annotations

from datetime import datetime
from typing import Dict, Any


class FailureDiagnostics:
    """
    Provides remediation guidance based on failure modes.
    """

    def diagnose(self, failure_mode: str, skill_id: str, context: Dict[str, Any]) -> Dict[str, Any]:
        recommendation = self._recommendation_map().get(
            failure_mode,
            self._recommendation_map()["timeout"],
        )
        recommendation.update(
            {
                "skill_id": skill_id,
                "context": context,
                "timestamp": datetime.now().isoformat(),
            }
        )
        return recommendation

    def _recommendation_map(self) -> Dict[str, Dict[str, Any]]:
        return {
            "timeout": {
                "probable_cause": "App is slow or unresponsive",
                "recommendations": [
                    "Increase timeout threshold",
                    "Check if app is responsive",
                    "Restart the app",
                ],
                "remediation": "retry_with_backoff",
            },
            "element_not_found": {
                "probable_cause": "UI layout changed",
                "recommendations": [
                    "Show me the new element location",
                    "Try a different element name",
                    "Use visual detection",
                ],
                "remediation": "observer.record_demonstration",
            },
            "vlm_nonsense": {
                "probable_cause": "VLM misinterpreted the screen",
                "recommendations": [
                    "Record a clearer example",
                    "Use template matching",
                    "Improve screenshot quality",
                ],
                "remediation": "observer.record_demonstration",
            },
            "access_denied": {
                "probable_cause": "Permission issue",
                "recommendations": [
                    "Run as administrator",
                    "Check user permissions",
                ],
                "remediation": "run_as_admin",
            },
        }
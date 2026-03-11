"""
VELOCITY A-OS: TRIAGE
Error analysis and diagnosis logic
"""

import asyncio
from typing import Dict, List


class Triage:
    """Analyzes errors and determines response"""
    
    def __init__(self):
        self.error_history = []
        
    async def analyze_error(self, error: Exception) -> Dict:
        """Analyze error and determine severity"""
        error_dict = {
            "type": type(error).__name__,
            "message": str(error),
            "severity": self._classify_severity(error),
            "action": self._determine_action(error)
        }
        
        self.error_history.append(error_dict)
        return error_dict
    
    def _classify_severity(self, error: Exception) -> str:
        """Classify error severity"""
        if isinstance(error, KeyboardInterrupt):
            return "normal"
        elif isinstance(error, Exception):
            return "error"
        else:
            return "unknown"
    
    def _determine_action(self, error: Exception) -> str:
        """Determine recovery action"""
        # In production: More sophisticated logic
        if "timeout" in str(error).lower():
            return "retry"
        elif "offline" in str(error).lower():
            return "reconnect"
        else:
            return "restart"

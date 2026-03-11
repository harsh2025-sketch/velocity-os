"""
VELOCITY Cortex - Temporal Context Awareness
Phase 2: Provide context signals for confidence modifiers.
"""

from __future__ import annotations

from datetime import datetime
from typing import Dict


class TemporalContext:
    """
    Collects context signals such as time-of-day and network availability.
    """

    def get_context(self) -> Dict[str, object]:
        now = datetime.now()
        return {
            "timestamp": now.isoformat(),
            "hour": now.hour,
            "is_business_hours": 9 <= now.hour <= 17,
            "network_state": self._check_network(),
            "app_state": "unknown",
        }

    def _check_network(self) -> str:
        try:
            import socket
            with socket.create_connection(("8.8.8.8", 53), timeout=2):
                pass
            return "online"
        except Exception:
            return "offline"
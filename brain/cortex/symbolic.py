"""
VELOCITY Cortex - Symbolic Layer
L4: Fast symbolic lookup using skills.json + intent clustering.
"""

from __future__ import annotations

import hashlib
import json
import os
import re
from typing import Dict, List, Optional, Tuple, Any


PROJECT_ROOT: str = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
SKILLS_PATH: str = os.path.join(PROJECT_ROOT, "brain", "memory", "skills.json")
APP_PROFILES_PATH: str = os.path.join(PROJECT_ROOT, "brain", "memory", "app_profiles.json")


def _semantic_hash(verb: str, app: str) -> str:
    normalized = f"{verb.strip().lower()}:{app.strip().lower()}"
    return hashlib.sha256(normalized.encode("utf-8")).hexdigest()


def _normalize_verb(verb: str) -> str:
    verb_map = {
        "start": "play",
        "resume": "play",
        "begin": "play",
        "launch": "open",
        "open": "open",
        "create": "create",
        "new": "create",
        "close": "close",
        "exit": "close",
        "save": "save",
        "write": "type",
        "type": "type",
        "search": "search",
        "find": "find",
    }
    v = verb.strip().lower()
    return verb_map.get(v, v)


def _extract_verb(intent: str) -> str:
    match = re.match(r"^([a-zA-Z]+)", intent.strip())
    if not match:
        return "unknown"
    return _normalize_verb(match.group(1))


def _extract_app(intent: str, app_profiles: Dict[str, Any]) -> str:
    lowered = intent.lower()
    for app_name in app_profiles.keys():
        if app_name.lower() in lowered:
            return app_name
    return "universal"


class SymbolicLayer:
    """
    Symbolic layer for fast intent lookup and execution.
    Implements Algorithm 3: Intent Clustering via Semantic Hashing (ICSH).
    """

    def __init__(self, skills_path: str = SKILLS_PATH, app_profiles_path: str = APP_PROFILES_PATH) -> None:
        self.skills_path = skills_path
        self.app_profiles_path = app_profiles_path
        self.skills: Dict[str, Any] = self._load_json(skills_path)
        self.app_profiles: Dict[str, Any] = self._load_json(app_profiles_path)
        self.clusters: Dict[str, List[str]] = {}
        self._build_clusters()

    def _load_json(self, path: str) -> Dict[str, Any]:
        if not os.path.exists(path):
            return {}
        try:
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return {}

    def _build_clusters(self) -> None:
        # Use explicit clusters if present
        if "_clusters" in self.skills:
            clusters = self.skills.get("_clusters", {})
            for cluster_id, skill_ids in clusters.items():
                self.clusters[cluster_id] = list(skill_ids)
            return

        # Otherwise build clusters from skill aliases
        for skill_id, skill in self.skills.items():
            if skill_id.startswith("_"):
                continue
            aliases = skill.get("aliases", [])
            app = skill.get("app", "universal")
            if not aliases:
                continue
            verb = _extract_verb(aliases[0])
            cluster_id = _semantic_hash(verb, app)
            self.clusters.setdefault(cluster_id, []).append(skill_id)

    def _select_best_skill(self, skill_ids: List[str]) -> Optional[Tuple[str, Dict[str, Any]]]:
        best_id = None
        best_conf = -1.0
        for sid in skill_ids:
            skill = self.skills.get(sid)
            if not skill:
                continue
            methods = skill.get("methods", [])
            if not methods:
                continue
            # Prefer symbolic methods when available
            symbolic_methods = [m for m in methods if m.get("type") == "symbolic"]
            candidate = symbolic_methods[0] if symbolic_methods else methods[0]
            conf = candidate.get("confidence", 0.5)
            if conf > best_conf:
                best_conf = conf
                best_id = sid
        if not best_id:
            return None
        return best_id, self.skills.get(best_id, {})

    def try_symbolic(self, intent: str) -> Optional[Dict[str, Any]]:
        """
        Try to resolve intent using symbolic skills.
        Returns a structured action dict or None if no match.
        """
        if not intent:
            return None

        verb = _extract_verb(intent)
        app = _extract_app(intent, self.app_profiles)
        cluster_id = _semantic_hash(verb, app)
        raw_cluster_id = f"{verb}:{app}".lower()

        if cluster_id not in self.clusters and raw_cluster_id not in self.clusters:
            return None

        cluster_key = cluster_id if cluster_id in self.clusters else raw_cluster_id
        selection = self._select_best_skill(self.clusters[cluster_key])
        if not selection:
            return None

        skill_id, skill = selection
        methods = skill.get("methods", [])
        if not methods:
            return None

        # Pick best method (prefer symbolic)
        symbolic_methods = [m for m in methods if m.get("type") == "symbolic"]
        method = max(symbolic_methods or methods, key=lambda m: m.get("confidence", 0.5))

        return {
            "skill_id": skill_id,
            "app": skill.get("app", app),
            "intent": intent,
            "method": "symbolic",
            "action": method.get("action"),
            "key": method.get("key"),
            "confidence": method.get("confidence", 0.5),
            "avg_latency_ms": method.get("avg_latency_ms", 10),
        }
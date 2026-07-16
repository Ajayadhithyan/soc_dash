"""
Declarative Playbook Engine.
Evaluates YAML-based conditional automation rules against enriched events
and returns a list of actions that should be auto-triggered.
"""

import os
import logging
from datetime import datetime

logger = logging.getLogger("soc_backend")

try:
    import yaml
    HAS_YAML = True
except ImportError:
    HAS_YAML = False
    logger.warning("[Playbook] PyYAML not installed. Playbook engine disabled.")


class PlaybookEngine:
    """
    Evaluates declarative automation playbooks against incoming events.
    Each playbook defines conditions and a set of actions to execute.
    """

    def __init__(self, playbooks_dir=None):
        """
        Args:
            playbooks_dir: Path to YAML playbook files.
                          Defaults to backend/playbooks/
        """
        if playbooks_dir is None:
            playbooks_dir = os.path.join(
                os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                "playbooks"
            )
        self.playbooks_dir = playbooks_dir
        self.playbooks = []
        self._load_playbooks()

    def _load_playbooks(self):
        """Load all YAML playbook definitions."""
        if not HAS_YAML:
            return

        if not os.path.isdir(self.playbooks_dir):
            logger.info(f"[Playbook] Playbooks directory not found: {self.playbooks_dir}")
            return

        self.playbooks = []
        for filename in os.listdir(self.playbooks_dir):
            if filename.endswith((".yaml", ".yml")):
                filepath = os.path.join(self.playbooks_dir, filename)
                try:
                    with open(filepath, "r", encoding="utf-8") as f:
                        data = yaml.safe_load(f)
                    if data and isinstance(data, dict):
                        rules = data.get("rules", [])
                        self.playbooks.extend(rules)
                except Exception as e:
                    logger.error(f"[Playbook] Failed to load {filename}: {e}")

        logger.info(f"[Playbook] Loaded {len(self.playbooks)} automation rules.")

    def _evaluate_condition(self, condition, event):
        """Evaluate a single condition against an event."""
        field = condition.get("field", "")
        operator = condition.get("operator", "eq")
        expected = condition.get("value")

        # Support nested field access
        actual = event
        for key in field.split("."):
            if isinstance(actual, dict):
                actual = actual.get(key)
            else:
                actual = None
                break

        if actual is None:
            return False

        try:
            if operator == "eq":
                return str(actual).upper() == str(expected).upper()
            elif operator == "gt":
                return float(actual) > float(expected)
            elif operator == "gte":
                return float(actual) >= float(expected)
            elif operator == "lt":
                return float(actual) < float(expected)
            elif operator == "in":
                if isinstance(expected, list):
                    return str(actual).upper() in [str(v).upper() for v in expected]
                return False
            else:
                return False
        except (ValueError, TypeError):
            return False

    def evaluate(self, event):
        """
        Evaluate an enriched event against all playbook rules.

        Args:
            event: Enriched security event dict.

        Returns:
            list: List of auto-triggered action dicts.
        """
        triggered = []

        for rule in self.playbooks:
            conditions = rule.get("conditions", [])
            logic = rule.get("logic", "AND").upper()
            actions = rule.get("actions", [])
            rule_name = rule.get("name", "Unnamed Rule")

            if not conditions or not actions:
                continue

            # Evaluate conditions
            if logic == "AND":
                matched = all(self._evaluate_condition(c, event) for c in conditions)
            elif logic == "OR":
                matched = any(self._evaluate_condition(c, event) for c in conditions)
            else:
                matched = False

            if matched:
                now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                for action in actions:
                    triggered.append({
                        "playbook_rule": rule_name,
                        "action": action,
                        "triggered_at": now,
                        "auto_triggered": True,
                    })
                logger.info(
                    f"[Playbook] Rule '{rule_name}' triggered → Actions: {actions}"
                )

        return triggered

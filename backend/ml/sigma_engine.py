"""
SIGMA Rule Engine.
Loads YAML-based detection rules and evaluates incoming events against them.
Rules are hot-reloadable — no server restart required.
"""

import os
import logging
from datetime import datetime

logger = logging.getLogger("soc_backend")

# Try importing yaml, fallback gracefully
try:
    import yaml
    HAS_YAML = True
except ImportError:
    HAS_YAML = False
    logger.warning("[SIGMA] PyYAML not installed. SIGMA rule engine disabled.")


class SigmaEngine:
    """
    YAML-based detection rule engine.
    Loads rules from a directory and evaluates security events against them.
    """

    def __init__(self, rules_dir=None):
        """
        Args:
            rules_dir: Path to directory containing .yaml rule files.
                       Defaults to backend/rules/ relative to this file.
        """
        if rules_dir is None:
            rules_dir = os.path.join(
                os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                "rules"
            )
        self.rules_dir = rules_dir
        self.rules = []
        self._last_load_time = None
        self._last_check_time = datetime.now()
        self._load_rules()

    def _load_rules(self):
        """Load all YAML rule files from the rules directory."""
        if not HAS_YAML:
            logger.warning("[SIGMA] Skipping rule load — PyYAML not available.")
            return

        if not os.path.isdir(self.rules_dir):
            logger.info(f"[SIGMA] Rules directory not found: {self.rules_dir}")
            return

        self.rules = []
        for filename in os.listdir(self.rules_dir):
            if filename.endswith((".yaml", ".yml")):
                filepath = os.path.join(self.rules_dir, filename)
                try:
                    with open(filepath, "r", encoding="utf-8") as f:
                        rule = yaml.safe_load(f)
                    if rule and isinstance(rule, dict):
                        rule["_filename"] = filename
                        self.rules.append(rule)
                except Exception as e:
                    logger.error(f"[SIGMA] Failed to load rule {filename}: {e}")

        self._last_load_time = datetime.now()
        logger.info(f"[SIGMA] Loaded {len(self.rules)} detection rules from {self.rules_dir}")

    def _hot_reload_if_needed(self):
        """Re-load rules if files have been modified since last load. Rate-limited to check at most once every 30 seconds."""
        now = datetime.now()
        if self._last_check_time:
            if (now - self._last_check_time).total_seconds() < 30:
                return
        self._last_check_time = now

        if not self._last_load_time or not os.path.isdir(self.rules_dir):
            return

        # Check if any file was modified since last load
        for filename in os.listdir(self.rules_dir):
            if filename.endswith((".yaml", ".yml")):
                filepath = os.path.join(self.rules_dir, filename)
                mod_time = datetime.fromtimestamp(os.path.getmtime(filepath))
                if mod_time > self._last_load_time:
                    logger.info(f"[SIGMA] Hot-reloading rules (file changed: {filename})")
                    self._load_rules()
                    return

    def _evaluate_condition(self, condition, event):
        """
        Evaluate a single condition against an event.

        Condition format:
            field: event field name
            operator: eq, neq, contains, gt, lt, gte, lte, in, regex
            value: comparison value
        """
        field = condition.get("field", "")
        operator = condition.get("operator", "eq")
        expected = condition.get("value")

        # Get the event field value (support nested fields with dot notation)
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
            elif operator == "neq":
                return str(actual).upper() != str(expected).upper()
            elif operator == "contains":
                return str(expected).lower() in str(actual).lower()
            elif operator == "gt":
                return float(actual) > float(expected)
            elif operator == "lt":
                return float(actual) < float(expected)
            elif operator == "gte":
                return float(actual) >= float(expected)
            elif operator == "lte":
                return float(actual) <= float(expected)
            elif operator == "in":
                if isinstance(expected, list):
                    return str(actual).upper() in [str(v).upper() for v in expected]
                return False
            elif operator == "regex":
                import re
                return bool(re.search(str(expected), str(actual)))
            else:
                return False
        except (ValueError, TypeError):
            return False

    def _evaluate_rule(self, rule, event):
        """
        Evaluate a complete rule against an event.

        Rule logic can be:
            - logic: "AND" — all conditions must match
            - logic: "OR" — any condition must match
        """
        conditions = rule.get("conditions", [])
        logic = rule.get("logic", "AND").upper()

        if not conditions:
            return False

        if logic == "AND":
            return all(self._evaluate_condition(c, event) for c in conditions)
        elif logic == "OR":
            return any(self._evaluate_condition(c, event) for c in conditions)

        return False

    def evaluate(self, event):
        """
        Evaluate an event against all loaded SIGMA rules.

        Args:
            event: Security event dict.

        Returns:
            list: List of matched rule dicts with id, name, severity, description.
        """
        # Hot-reload rules if files changed
        self._hot_reload_if_needed()

        matches = []
        for rule in self.rules:
            if self._evaluate_rule(rule, event):
                matches.append({
                    "rule_id": rule.get("id", "UNKNOWN"),
                    "rule_name": rule.get("name", "Unnamed Rule"),
                    "severity": rule.get("severity", "MEDIUM"),
                    "description": rule.get("description", ""),
                    "tags": rule.get("tags", []),
                })

        if matches:
            rule_names = ", ".join(m["rule_name"] for m in matches)
            logger.info(f"[SIGMA] {len(matches)} rule(s) matched: {rule_names}")

        return matches

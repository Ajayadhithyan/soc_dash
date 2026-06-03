"""
MITRE ATT&CK Mapper.
Maps security events to ATT&CK technique IDs using either
Google Gemini (zero-shot classification) or a deterministic fallback table.
"""

import os

# -----------------------------------
# DETERMINISTIC MAPPING TABLE
# -----------------------------------

MITRE_MAPPINGS = {
    "SSH_BRUTE_FORCE": {
        "technique_id": "T1110",
        "technique_name": "Brute Force",
        "tactic": "Credential Access",
        "description": "Adversary uses brute-force methods to attempt login by systematically trying passwords.",
        "sub_techniques": ["T1110.001 - Password Guessing", "T1110.003 - Password Spraying"],
        "severity_boost": 0.1,
    },
    "PORT_SCAN": {
        "technique_id": "T1046",
        "technique_name": "Network Service Discovery",
        "tactic": "Discovery",
        "description": "Adversary scans for open ports and services to identify attack surfaces.",
        "sub_techniques": ["T1046 - Network Service Scanning"],
        "severity_boost": 0.0,
    },
    "FAILED_LOGIN": {
        "technique_id": "T1078",
        "technique_name": "Valid Accounts",
        "tactic": "Defense Evasion, Persistence",
        "description": "Adversary may attempt to use valid account credentials to gain access.",
        "sub_techniques": ["T1078.001 - Default Accounts", "T1078.003 - Local Accounts"],
        "severity_boost": 0.0,
    },
    "MALWARE_DETECTION": {
        "technique_id": "T1204",
        "technique_name": "User Execution",
        "tactic": "Execution",
        "description": "Malicious code executed on the endpoint, possibly via user interaction or exploit.",
        "sub_techniques": ["T1204.002 - Malicious File", "T1059 - Command and Scripting Interpreter"],
        "severity_boost": 0.15,
    },
    "DATA_EXFILTRATION": {
        "technique_id": "T1041",
        "technique_name": "Exfiltration Over C2 Channel",
        "tactic": "Exfiltration",
        "description": "Adversary exfiltrates data from the network through the command-and-control channel.",
        "sub_techniques": ["T1041 - Exfiltration Over C2", "T1048 - Exfiltration Over Alternative Protocol"],
        "severity_boost": 0.2,
    },
}


class MitreMapper:
    """
    Maps security events to MITRE ATT&CK techniques.
    Uses Gemini API for zero-shot classification when available,
    otherwise falls back to deterministic table.
    """

    def __init__(self, gemini_api_key=None):
        self.gemini_api_key = gemini_api_key or os.getenv("GEMINI_API_KEY", "")
        self.use_llm = bool(self.gemini_api_key)
        self._gemini_model = None

        if self.use_llm:
            try:
                import google.generativeai as genai
                genai.configure(api_key=self.gemini_api_key)
                self._gemini_model = genai.GenerativeModel("gemini-2.5-flash")
                print("[MITRE] Gemini API configured for zero-shot classification.")
            except Exception as e:
                print(f"[MITRE] Gemini init failed: {e}. Using fallback mapping.")
                self.use_llm = False

    def map_event(self, event):
        """
        Map a security event to MITRE ATT&CK technique.

        Args:
            event: dict with event_type, raw_log, etc.

        Returns:
            dict with technique_id, technique_name, tactic, description, sub_techniques.
        """
        event_type = event.get("event_type", "")

        # Always use deterministic mapping for speed and reliability
        # LLM is used only for enrichment / unknown event types
        if event_type in MITRE_MAPPINGS:
            mapping = MITRE_MAPPINGS[event_type].copy()

            # If LLM is available, try to get additional context
            if self.use_llm and self._gemini_model:
                try:
                    enrichment = self._llm_enrich(event)
                    if enrichment:
                        mapping["llm_analysis"] = enrichment
                except Exception:
                    pass

            return mapping

        # Unknown event type — try LLM or return generic
        if self.use_llm and self._gemini_model:
            return self._llm_classify(event)

        return {
            "technique_id": "T1059",
            "technique_name": "Command and Scripting Interpreter",
            "tactic": "Execution",
            "description": "Unknown event type — generic classification applied.",
            "sub_techniques": [],
            "severity_boost": 0.0,
        }

    def _llm_classify(self, event):
        """Use Gemini for zero-shot MITRE ATT&CK classification."""
        try:
            prompt = f"""You are a cybersecurity analyst. Classify this security event into the most likely MITRE ATT&CK technique.

Event Type: {event.get('event_type', 'Unknown')}
Raw Log: {event.get('raw_log', 'No log available')}
Severity: {event.get('severity', 'Unknown')}

Respond in exactly this format:
Technique ID: T[XXXX]
Technique Name: [name]
Tactic: [tactic name]
Description: [one sentence description]"""

            response = self._gemini_model.generate_content(prompt)
            text = response.text.strip()

            # Parse response
            lines = text.split("\n")
            result = {
                "technique_id": "T1059",
                "technique_name": "Unknown",
                "tactic": "Unknown",
                "description": text,
                "sub_techniques": [],
                "severity_boost": 0.0,
            }

            for line in lines:
                if "Technique ID:" in line:
                    result["technique_id"] = line.split(":", 1)[1].strip()
                elif "Technique Name:" in line:
                    result["technique_name"] = line.split(":", 1)[1].strip()
                elif "Tactic:" in line:
                    result["tactic"] = line.split(":", 1)[1].strip()
                elif "Description:" in line:
                    result["description"] = line.split(":", 1)[1].strip()

            return result
        except Exception as e:
            print(f"[MITRE] LLM classify error: {e}")
            return {
                "technique_id": "T1059",
                "technique_name": "Command and Scripting Interpreter",
                "tactic": "Execution",
                "description": "LLM classification failed — fallback applied.",
                "sub_techniques": [],
                "severity_boost": 0.0,
            }

    def _llm_enrich(self, event):
        """Use Gemini to add extra analyst context to the mapping."""
        try:
            prompt = f"""In one sentence, explain the tactical significance of this security event for a SOC analyst:

Event: {event.get('event_type', '')}
Log: {event.get('raw_log', '')}"""

            response = self._gemini_model.generate_content(prompt)
            return response.text.strip()
        except Exception:
            return None

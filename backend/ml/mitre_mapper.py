"""
MITRE ATT&CK Mapper.
Maps security events to ATT&CK technique IDs using either
Google Gemini (zero-shot classification) or a deterministic fallback table.
"""

import os
import logging
import httpx

logger = logging.getLogger("soc_backend")

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
    def __init__(self, opencode_api_key=None):
        self.opencode_api_key = opencode_api_key or os.getenv("OPENCODE_API_KEY", "")
        self.use_llm = bool(self.opencode_api_key)

        if self.use_llm:
            logger.info("[MITRE] OpenCode API configured for zero-shot classification.")

    def _call_llm(self, prompt):
        if not self.use_llm:
            raise Exception("LLM mode is disabled.")
        url = "https://opencode.ai/zen/go/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {self.opencode_api_key}",
            "Content-Type": "application/json"
        }
        payload = {
            "model": "deepseek-v4-flash",
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.2
        }
        try:
            with httpx.Client(timeout=3.0) as client:
                response = client.post(url, headers=headers, json=payload)
                if response.status_code == 200:
                    data = response.json()
                    return data["choices"][0]["message"]["content"].strip()
                else:
                    if response.status_code in [401, 403]:
                        logger.error(f"[MITRE] Disabling LLM due to auth/credit error {response.status_code}")
                        self.use_llm = False
                    raise Exception(f"OpenCode API returned status {response.status_code}: {response.text}")
        except (httpx.ConnectTimeout, httpx.ConnectError, httpx.ReadTimeout) as e:
            logger.error(f"[MITRE] Connection failed: {e}. Disabling LLM mode to prevent freezes.")
            self.use_llm = False
            raise e

    def map_event(self, event):
        event_type = event.get("event_type", "")

        if event_type in MITRE_MAPPINGS:
            mapping = MITRE_MAPPINGS[event_type].copy()
            if self.use_llm:
                try:
                    enrichment = self._llm_enrich(event)
                    if enrichment:
                        mapping["llm_analysis"] = enrichment
                except Exception:
                    pass
            return mapping

        if self.use_llm:
            return self._llm_classify(event)

        return {
            "technique_id": "T1059",
            "technique_name": "Command and Scripting Interpreter",
            "tactic": "Execution",
            "description": "Unknown event type: generic classification applied.",
            "sub_techniques": [],
            "severity_boost": 0.0,
        }

    def _llm_classify(self, event):
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

            text = self._call_llm(prompt)
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
            logger.error(f"[MITRE] LLM classify error: {e}")
            return {
                "technique_id": "T1059",
                "technique_name": "Command and Scripting Interpreter",
                "tactic": "Execution",
                "description": "LLM classification failed: fallback applied.",
                "sub_techniques": [],
                "severity_boost": 0.0,
            }

    def _llm_enrich(self, event):
        try:
            prompt = f"""In one sentence, explain the tactical significance of this security event for a SOC analyst:

Event: {event.get('event_type', '')}
Log: {event.get('raw_log', '')}"""

            return self._call_llm(prompt)
        except Exception:
            return None

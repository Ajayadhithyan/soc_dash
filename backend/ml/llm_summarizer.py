"""
LLM Alert Summarizer.
Generates plain-English summaries of raw security alerts using
Google Gemini API or a smart rule-based fallback.
"""

import os
import random
import logging

logger = logging.getLogger("soc_backend")

SUMMARY_TEMPLATES = {
    "SSH_BRUTE_FORCE": [
        "A brute-force SSH attack was detected from {src_ip} targeting {dest_ip}, with multiple failed login attempts against the '{user}' account. Immediate investigation is recommended to determine if any credentials were compromised.",
        "Repeated SSH login failures from {src_ip} indicate a credential-stuffing or brute-force attack against host {dest_ip}. The targeted account '{user}' should be temporarily locked and the source IP blocked at the firewall.",
        "An external host {src_ip} is aggressively attempting SSH authentication against {dest_ip} using the '{user}' account. This pattern is consistent with automated brute-force tooling and warrants immediate containment.",
    ],
    "PORT_SCAN": [
        "Network reconnaissance activity detected from {src_ip} scanning multiple ports on {dest_ip}. This is typically a precursor to exploitation and the source should be monitored for follow-up attacks.",
        "A systematic port scan from {src_ip} against {dest_ip} was identified, probing for exposed services. Verify that all non-essential ports are firewalled and assess if this IP has conducted prior scanning activity.",
        "Host {src_ip} is performing active network enumeration against {dest_ip}, testing multiple service ports. This reconnaissance behavior often precedes targeted exploitation attempts.",
    ],
    "FAILED_LOGIN": [
        "A failed authentication attempt was recorded for user '{user}' from IP {src_ip}. While isolated failures are common, a pattern of failures from this source should trigger account lockout policies.",
        "User '{user}' failed to authenticate from {src_ip}. Monitor for additional failures from this source: repeated attempts may indicate credential compromise or unauthorized access attempts.",
    ],
    "MALWARE_DETECTION": [
        "Malware was detected on endpoint {dest_ip} with traffic originating from {src_ip}. The affected host should be immediately isolated from the network, and a full forensic scan should be initiated.",
        "A malicious payload was identified on {dest_ip}, likely delivered from external source {src_ip}. Quarantine the endpoint immediately, collect forensic artifacts, and check for lateral movement indicators.",
        "Critical malware detection on {dest_ip} traced to {src_ip}. Immediate host isolation and incident response procedures are required to prevent potential lateral spread across the network.",
    ],
    "DATA_EXFILTRATION": [
        "Anomalous outbound data transfer detected from {dest_ip} to external host {src_ip}, transferring an unusually large volume of data. This may indicate active data exfiltration requiring immediate investigation.",
        "A potential data exfiltration event was identified with {dest_ip} sending significant data to {src_ip}. Verify whether this transfer was authorized and check for signs of compromised credentials or insider threat.",
    ],
}


class AlertSummarizer:
    def __init__(self, gemini_api_key=None):
        self.gemini_api_key = gemini_api_key or os.getenv("GEMINI_API_KEY", "")
        self.use_llm = bool(self.gemini_api_key)
        self._gemini_model = None

        if self.use_llm:
            try:
                import google.generativeai as genai
                genai.configure(api_key=self.gemini_api_key)
                self._gemini_model = genai.GenerativeModel("gemini-2.5-flash")
                logger.info("[Summarizer] Gemini API configured for alert summarization.")
            except Exception as e:
                logger.error(f"[Summarizer] Gemini init failed: {e}. Using fallback templates.")
                self.use_llm = False

    def summarize(self, event):
        if self.use_llm and self._gemini_model:
            return self._llm_summarize(event)
        return self._fallback_summarize(event)

    def _llm_summarize(self, event):
        try:
            prompt = f"""You are a senior SOC analyst. Summarize this security alert in exactly 2 concise sentences for an analyst dashboard. Be specific about the threat and recommended action.

Event Type: {event.get('event_type', 'Unknown')}
Severity: {event.get('severity', 'Unknown')}
Source IP: {event.get('src_ip', 'Unknown')}
Destination IP: {event.get('dest_ip', 'Unknown')}
User: {event.get('user', 'Unknown')}
Raw Log: {event.get('raw_log', 'No log available')}

Summary:"""

            response = self._gemini_model.generate_content(prompt)
            summary = response.text.strip()
            sentences = summary.split(". ")
            if len(sentences) > 3:
                summary = ". ".join(sentences[:2]) + "."
            return summary
        except Exception as e:
            logger.error(f"[Summarizer] LLM error: {e}. Using fallback.")
            return self._fallback_summarize(event)

    def _fallback_summarize(self, event):
        event_type = event.get("event_type", "FAILED_LOGIN")
        templates = SUMMARY_TEMPLATES.get(event_type, SUMMARY_TEMPLATES["FAILED_LOGIN"])
        template = random.choice(templates)
        return template.format(
            src_ip=event.get("src_ip", "unknown"),
            dest_ip=event.get("dest_ip", "unknown"),
            user=event.get("user", "unknown"),
        )

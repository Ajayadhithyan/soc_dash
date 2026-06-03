"""
RAG Chat Assistant.
Retrieves recent high-severity alerts from MongoDB, injects them
as context into a Gemini prompt, and answers analyst questions.
Falls back to keyword-based aggregation without an API key.
"""

import os
from datetime import datetime


class ChatAssistant:
    """
    AI chat assistant for SOC analysts.
    Uses RAG (Retrieval-Augmented Generation) with recent alerts as context.
    """

    def __init__(self, db=None, gemini_api_key=None):
        """
        Args:
            db: MongoDB database instance (motor async db).
            gemini_api_key: Optional Gemini API key.
        """
        self.db = db
        self.gemini_api_key = gemini_api_key or os.getenv("GEMINI_API_KEY", "")
        self.use_llm = bool(self.gemini_api_key)
        self._gemini_model = None

        if self.use_llm:
            try:
                import google.generativeai as genai
                genai.configure(api_key=self.gemini_api_key)
                self._gemini_model = genai.GenerativeModel("gemini-2.5-flash")
                print("[Chat] Gemini API configured for RAG chat assistant.")
            except Exception as e:
                print(f"[Chat] Gemini init failed: {e}. Using fallback mode.")
                self.use_llm = False

    async def get_context_alerts(self, limit=20):
        """Retrieve recent high-severity alerts from MongoDB as context."""
        if self.db is None:
            return []

        cursor = self.db["security_events"].find(
            {"severity": {"$in": ["HIGH", "CRITICAL"]}},
            {"_id": 0, "timestamp": 1, "event_type": 1, "severity": 1,
             "src_ip": 1, "dest_ip": 1, "raw_log": 1, "risk_score": 1,
             "ai_summary": 1, "mitre": 1}
        ).sort("timestamp", -1).limit(limit)

        alerts = []
        async for doc in cursor:
            alerts.append(doc)
        return alerts

    async def chat(self, question):
        """
        Answer an analyst's question using RAG.

        Args:
            question: Natural language question string.

        Returns:
            str: AI-generated answer.
        """
        context_alerts = await self.get_context_alerts()

        if self.use_llm and self._gemini_model:
            return await self._llm_chat(question, context_alerts)
        return self._fallback_chat(question, context_alerts)

    async def _llm_chat(self, question, context_alerts):
        """Use Gemini with RAG context to answer the question."""
        try:
            # Format alerts as context
            context_lines = []
            for i, alert in enumerate(context_alerts, 1):
                mitre_id = ""
                if isinstance(alert.get("mitre"), dict):
                    mitre_id = alert["mitre"].get("technique_id", "")
                context_lines.append(
                    f"{i}. [{alert.get('timestamp', 'N/A')}] "
                    f"{alert.get('event_type', 'N/A')} ({alert.get('severity', 'N/A')}) "
                    f"from {alert.get('src_ip', 'N/A')} → {alert.get('dest_ip', 'N/A')} "
                    f"| Risk: {alert.get('risk_score', 'N/A')} "
                    f"| MITRE: {mitre_id}"
                )

            context_str = "\n".join(context_lines) if context_lines else "No recent alerts available."

            prompt = f"""You are an AI SOC analyst assistant embedded in a Security Operations Centre dashboard. Answer the analyst's question using the recent alert data provided below.

Be concise, specific, and actionable. Reference specific alerts, IPs, or patterns when relevant. If the data doesn't contain enough information to answer fully, say so.

=== RECENT HIGH-SEVERITY ALERTS ===
{context_str}

=== ANALYST QUESTION ===
{question}

=== YOUR RESPONSE ==="""

            response = self._gemini_model.generate_content(prompt)
            return response.text.strip()
        except Exception as e:
            print(f"[Chat] LLM error: {e}")
            return self._fallback_chat(question, context_alerts)

    def _fallback_chat(self, question, context_alerts):
        """Keyword-based answer engine when no LLM is available."""
        question_lower = question.lower()
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        if not context_alerts:
            # Check for greetings even if no database context is ready
            greetings = {"hi", "hello", "hey", "yoo", "yo", "greetings", "good morning", "good afternoon", "good evening", "sup", "howdy", "hi there"}
            cleaned_question = question_lower.strip().rstrip("!?.,")
            if cleaned_question in greetings or any(cleaned_question.startswith(g + " ") for g in greetings):
                return (
                    "Hello! I am the Aegis AI Copilot, your virtual SOC assistant. "
                    "I am ready to help you analyze security alerts, investigate threat actors, "
                    "or recommend response playbooks. How can I assist you today?"
                )
            return (
                f"As of {now}, I don't have enough alert data to answer your question. "
                "The system is still collecting events. Please check back shortly."
            )

        total = len(context_alerts)
        critical_count = sum(1 for a in context_alerts if a.get("severity") == "CRITICAL")
        high_count = sum(1 for a in context_alerts if a.get("severity") == "HIGH")

        # Count event types
        type_counts = {}
        for a in context_alerts:
            t = a.get("event_type", "UNKNOWN")
            type_counts[t] = type_counts.get(t, 0) + 1

        # Collect unique source IPs
        src_ips = list(set(a.get("src_ip", "") for a in context_alerts if a.get("src_ip")))

        # Check for simple greetings
        greetings = {"hi", "hello", "hey", "yoo", "yo", "greetings", "good morning", "good afternoon", "good evening", "sup", "howdy", "hi there"}
        cleaned_question = question_lower.strip().rstrip("!?.,")
        if cleaned_question in greetings or any(cleaned_question.startswith(g + " ") for g in greetings):
            has_other_keywords = any(
                any(kw in question_lower for kw in kw_list)
                for kw_list in [
                    ["top threat", "biggest threat", "main threat", "worst", "most dangerous"],
                    ["how many", "count", "total", "number"],
                    ["ip", "source", "attacker", "origin"],
                    ["recommend", "suggest", "action", "what should", "next step"]
                ]
            )
            if not has_other_keywords:
                return (
                    "Hello! I am the Aegis AI Copilot, your virtual SOC assistant. "
                    "I can help you analyze security alerts, investigate threat actors, "
                    "or recommend response playbooks. How can I assist you today?"
                )

        # Top threats / summary
        if any(kw in question_lower for kw in ["top threat", "biggest threat", "main threat", "worst", "most dangerous"]):
            top_type = max(type_counts, key=type_counts.get)
            return (
                f"Based on the last {total} high-severity alerts, the most frequent threat type is "
                f"**{top_type}** ({type_counts[top_type]} occurrences). "
                f"There are {critical_count} CRITICAL and {high_count} HIGH severity alerts. "
                f"Top attacking IPs include: {', '.join(src_ips[:5])}. "
                "I recommend focusing on the CRITICAL alerts first and checking for any correlated attack patterns."
            )

        if any(kw in question_lower for kw in ["how many", "count", "total", "number"]):
            type_summary = ", ".join(f"{k}: {v}" for k, v in type_counts.items())
            return (
                f"In the recent alert window, there are **{total}** high-severity alerts: "
                f"{critical_count} CRITICAL, {high_count} HIGH. "
                f"Breakdown by type: {type_summary}."
            )

        if any(kw in question_lower for kw in ["ip", "source", "attacker", "origin"]):
            return (
                f"The following source IPs have been flagged in recent alerts: "
                f"{', '.join(src_ips[:10])}. "
                f"Total unique attacking IPs: {len(src_ips)}. "
                "Consider blocking repeat offenders at the perimeter firewall."
            )

        if any(kw in question_lower for kw in ["recommend", "suggest", "action", "what should", "next step"]):
            return (
                f"Based on {total} recent high-severity alerts ({critical_count} CRITICAL), I recommend:\n"
                "1. **Triage CRITICAL alerts first** — focus on malware detections and data exfiltration events.\n"
                "2. **Block repeat source IPs** at the firewall for IPs with multiple attack attempts.\n"
                "3. **Isolate affected endpoints** that show malware detection or brute-force compromise.\n"
                "4. **Review user accounts** targeted in brute-force attacks for credential reset.\n"
                "5. **Correlate events** to identify coordinated attack campaigns."
            )

        # Default summary
        type_summary = ", ".join(f"{k}: {v}" for k, v in type_counts.items())
        return (
            f"Here's what I see in the recent alert data: {total} high-severity alerts "
            f"({critical_count} CRITICAL, {high_count} HIGH). "
            f"Event breakdown: {type_summary}. "
            f"Unique source IPs: {len(src_ips)}. "
            "Ask me about specific threats, top attackers, or recommended actions for more detail."
        )

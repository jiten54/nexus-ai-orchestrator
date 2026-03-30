import os
import logging
import random
from datetime import datetime, timezone
from typing import List, Dict, Any, Optional
import asyncio

logger = logging.getLogger(__name__)

class AIBrain:
    """AI Brain for log analysis, anomaly detection, and predictions using OpenAI GPT-5.2"""
    
    def __init__(self):
        self.api_key = os.environ.get("EMERGENT_LLM_KEY")
        self.chat = None
        self._initialize_chat()
    
    def _initialize_chat(self):
        """Initialize the LLM chat instance"""
        try:
            from emergentintegrations.llm.chat import LlmChat
            self.chat = LlmChat(
                api_key=self.api_key,
                session_id=f"nexus-ai-brain-{datetime.now().timestamp()}",
                system_message="""You are NEXUS_AI, an intelligent system monitoring and analysis engine. 
Your role is to:
1. Analyze system logs and identify patterns, anomalies, and potential issues
2. Predict system failures before they occur
3. Suggest remediation actions for detected problems
4. Provide clear, concise explanations for detected issues

Always respond in a structured format with:
- Summary: Brief overview of findings
- Anomalies: List of detected anomalies with severity (critical/warning/info)
- Root Cause: Most likely root cause if applicable
- Prediction: Failure probability and time-to-failure estimate
- Recommendation: Suggested actions to prevent or fix issues

Be direct and technical. Focus on actionable insights."""
            ).with_model("openai", "gpt-5.2")
            logger.info("AI Brain initialized with GPT-5.2")
        except Exception as e:
            logger.error(f"Failed to initialize AI Brain: {e}")
            self.chat = None
    
    async def analyze_logs(self, logs: List[Dict]) -> Dict[str, Any]:
        """Analyze logs using AI to detect patterns and anomalies"""
        if not logs:
            return self._generate_empty_analysis()
        
        # Prepare log summary for analysis
        log_summary = self._prepare_log_summary(logs)
        
        if self.chat:
            try:
                from emergentintegrations.llm.chat import UserMessage
                
                prompt = f"""Analyze the following system logs and provide insights:

{log_summary}

Provide analysis in the following JSON format:
{{
    "summary": "Brief overview",
    "anomalies": [
        {{"type": "string", "severity": "critical|warning|info", "description": "string", "affected_component": "string"}}
    ],
    "root_cause": "string or null",
    "prediction": {{
        "failure_probability": 0.0-1.0,
        "time_to_failure_minutes": number or null,
        "confidence": 0.0-1.0
    }},
    "recommendations": ["string"]
}}"""
                
                message = UserMessage(text=prompt)
                response = await self.chat.send_message(message)
                
                # Parse response
                return self._parse_ai_response(response)
            except Exception as e:
                logger.error(f"AI analysis failed: {e}")
                return self._generate_fallback_analysis(logs)
        else:
            return self._generate_fallback_analysis(logs)
    
    def _prepare_log_summary(self, logs: List[Dict]) -> str:
        """Prepare a summary of logs for AI analysis"""
        lines = []
        error_count = 0
        warning_count = 0
        
        for log in logs[:50]:  # Limit to 50 logs
            level = log.get("level", "INFO")
            message = log.get("message", "")
            timestamp = log.get("timestamp", "")
            component = log.get("component", "system")
            
            lines.append(f"[{timestamp}] [{level}] [{component}] {message}")
            
            if level == "ERROR":
                error_count += 1
            elif level == "WARNING":
                warning_count += 1
        
        summary = f"Total logs: {len(logs)}, Errors: {error_count}, Warnings: {warning_count}\n\n"
        summary += "\n".join(lines)
        return summary
    
    def _parse_ai_response(self, response: str) -> Dict[str, Any]:
        """Parse AI response into structured format"""
        import json
        try:
            # Try to extract JSON from response
            start = response.find("{")
            end = response.rfind("}") + 1
            if start >= 0 and end > start:
                json_str = response[start:end]
                return json.loads(json_str)
        except Exception as e:
            logger.warning(f"Failed to parse AI response as JSON: {e}")
        
        # Return structured response with AI text
        return {
            "summary": response[:500] if len(response) > 500 else response,
            "anomalies": [],
            "root_cause": None,
            "prediction": {
                "failure_probability": 0.1,
                "time_to_failure_minutes": None,
                "confidence": 0.5
            },
            "recommendations": ["Review logs manually for detailed analysis"]
        }
    
    def _generate_empty_analysis(self) -> Dict[str, Any]:
        """Generate empty analysis when no logs available"""
        return {
            "summary": "No logs available for analysis",
            "anomalies": [],
            "root_cause": None,
            "prediction": {
                "failure_probability": 0.0,
                "time_to_failure_minutes": None,
                "confidence": 1.0
            },
            "recommendations": ["System is healthy, no action required"]
        }
    
    def _generate_fallback_analysis(self, logs: List[Dict]) -> Dict[str, Any]:
        """Generate analysis using heuristics when AI is unavailable"""
        error_logs = [l for l in logs if l.get("level") == "ERROR"]
        warning_logs = [l for l in logs if l.get("level") == "WARNING"]
        
        anomalies = []
        
        # Check for error patterns
        if len(error_logs) > 5:
            anomalies.append({
                "type": "high_error_rate",
                "severity": "critical",
                "description": f"High error rate detected: {len(error_logs)} errors in recent logs",
                "affected_component": "system"
            })
        
        if len(warning_logs) > 10:
            anomalies.append({
                "type": "elevated_warnings",
                "severity": "warning",
                "description": f"Elevated warning count: {len(warning_logs)} warnings",
                "affected_component": "system"
            })
        
        # Check for specific patterns
        timeout_errors = [l for l in error_logs if "timeout" in l.get("message", "").lower()]
        if timeout_errors:
            anomalies.append({
                "type": "timeout_pattern",
                "severity": "warning",
                "description": f"Timeout errors detected: {len(timeout_errors)} occurrences",
                "affected_component": "network"
            })
        
        memory_issues = [l for l in logs if "memory" in l.get("message", "").lower()]
        if memory_issues:
            anomalies.append({
                "type": "memory_pressure",
                "severity": "warning",
                "description": "Memory-related issues detected in logs",
                "affected_component": "resources"
            })
        
        failure_prob = min(1.0, len(error_logs) * 0.05 + len(warning_logs) * 0.02)
        
        return {
            "summary": f"Analyzed {len(logs)} logs. Found {len(error_logs)} errors and {len(warning_logs)} warnings.",
            "anomalies": anomalies,
            "root_cause": "Multiple factors detected" if anomalies else None,
            "prediction": {
                "failure_probability": round(failure_prob, 2),
                "time_to_failure_minutes": 30 if failure_prob > 0.5 else None,
                "confidence": 0.7
            },
            "recommendations": self._generate_recommendations(anomalies)
        }
    
    def _generate_recommendations(self, anomalies: List[Dict]) -> List[str]:
        """Generate recommendations based on detected anomalies"""
        recommendations = []
        
        for anomaly in anomalies:
            if anomaly["type"] == "high_error_rate":
                recommendations.append("Investigate error logs and consider scaling resources")
            elif anomaly["type"] == "timeout_pattern":
                recommendations.append("Check network connectivity and increase timeout thresholds")
            elif anomaly["type"] == "memory_pressure":
                recommendations.append("Consider increasing memory allocation or optimizing memory usage")
            elif anomaly["type"] == "elevated_warnings":
                recommendations.append("Review warning patterns to prevent escalation to errors")
        
        if not recommendations:
            recommendations.append("System operating normally, continue monitoring")
        
        return recommendations
    
    async def predict_failure(self, metrics: List[Dict]) -> Dict[str, Any]:
        """Predict system failures based on metrics trends"""
        if not metrics:
            return {
                "probability": 0.0,
                "time_to_failure": None,
                "confidence": 1.0,
                "factors": []
            }
        
        # Simple trend analysis
        cpu_values = [m.get("cpu", 0) for m in metrics]
        memory_values = [m.get("memory", 0) for m in metrics]
        latency_values = [m.get("latency", 0) for m in metrics]
        
        factors = []
        probability = 0.0
        
        # CPU trend
        if cpu_values:
            avg_cpu = sum(cpu_values) / len(cpu_values)
            if avg_cpu > 80:
                factors.append({"factor": "high_cpu", "value": avg_cpu, "weight": 0.3})
                probability += 0.3
        
        # Memory trend
        if memory_values:
            avg_memory = sum(memory_values) / len(memory_values)
            if avg_memory > 85:
                factors.append({"factor": "high_memory", "value": avg_memory, "weight": 0.3})
                probability += 0.3
        
        # Latency trend
        if latency_values:
            avg_latency = sum(latency_values) / len(latency_values)
            if avg_latency > 500:
                factors.append({"factor": "high_latency", "value": avg_latency, "weight": 0.2})
                probability += 0.2
        
        time_to_failure = None
        if probability > 0.5:
            time_to_failure = int(60 * (1 - probability))  # Minutes
        
        return {
            "probability": min(1.0, probability),
            "time_to_failure": time_to_failure,
            "confidence": 0.75,
            "factors": factors
        }
    
    def detect_anomalies(self, metrics: Dict[str, float]) -> List[Dict[str, Any]]:
        """Detect anomalies in current metrics"""
        anomalies = []
        
        cpu = metrics.get("cpu", 0)
        memory = metrics.get("memory", 0)
        latency = metrics.get("latency", 0)
        error_rate = metrics.get("error_rate", 0)
        
        if cpu > 90:
            anomalies.append({
                "type": "cpu_critical",
                "severity": "critical",
                "value": cpu,
                "threshold": 90,
                "message": f"CPU usage critical at {cpu}%"
            })
        elif cpu > 75:
            anomalies.append({
                "type": "cpu_warning",
                "severity": "warning",
                "value": cpu,
                "threshold": 75,
                "message": f"CPU usage elevated at {cpu}%"
            })
        
        if memory > 90:
            anomalies.append({
                "type": "memory_critical",
                "severity": "critical",
                "value": memory,
                "threshold": 90,
                "message": f"Memory usage critical at {memory}%"
            })
        elif memory > 80:
            anomalies.append({
                "type": "memory_warning",
                "severity": "warning",
                "value": memory,
                "threshold": 80,
                "message": f"Memory usage elevated at {memory}%"
            })
        
        if latency > 1000:
            anomalies.append({
                "type": "latency_critical",
                "severity": "critical",
                "value": latency,
                "threshold": 1000,
                "message": f"Latency critical at {latency}ms"
            })
        elif latency > 500:
            anomalies.append({
                "type": "latency_warning",
                "severity": "warning",
                "value": latency,
                "threshold": 500,
                "message": f"Latency elevated at {latency}ms"
            })
        
        if error_rate > 5:
            anomalies.append({
                "type": "error_rate_critical",
                "severity": "critical",
                "value": error_rate,
                "threshold": 5,
                "message": f"Error rate critical at {error_rate}%"
            })
        elif error_rate > 2:
            anomalies.append({
                "type": "error_rate_warning",
                "severity": "warning",
                "value": error_rate,
                "threshold": 2,
                "message": f"Error rate elevated at {error_rate}%"
            })
        
        return anomalies

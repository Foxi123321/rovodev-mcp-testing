"""Failure classification engine using local AI (Gemma/Qwen)."""
import asyncio
import httpx
import json
from typing import Dict, Any, List, Optional


class FailureClassifier:
    """Classifies failures and suggests recovery strategies using local Ollama models."""
    
    def __init__(self, model_name: str = "gemma2:9b", ollama_url: str = "http://localhost:11434"):
        self.model_name = model_name
        self.ollama_url = ollama_url
        self.client = httpx.AsyncClient(timeout=120.0)
    
    async def _call_ollama(self, prompt: str, system_prompt: str) -> str:
        """Call local Ollama API."""
        try:
            response = await self.client.post(
                f"{self.ollama_url}/api/generate",
                json={
                    "model": self.model_name,
                    "prompt": prompt,
                    "system": system_prompt,
                    "stream": False,
                    "temperature": 0.2,  # Slightly higher for reasoning
                    "top_p": 0.9
                }
            )
            response.raise_for_status()
            result = response.json()
            return result.get("response", "")
        except Exception as e:
            return f"ERROR: Failed to call Ollama: {str(e)}"
    
    async def classify_failure(
        self,
        failure_description: str,
        audit_results: Dict[str, Any],
        original_plan: str,
        error_logs: str = ""
    ) -> Dict[str, Any]:
        """
        Classify failure into one of three categories:
        
        1. EXECUTION_ERROR: Implementation bug, transient error, wrong approach
           → Recovery: Fix and retry the same step
        
        2. PLAN_GAP: Plan was incomplete, missing steps, wrong sequence
           → Recovery: Partial replan (affected steps only)
        
        3. MISSING_CAPABILITY: Tool/API/dependency doesn't exist or isn't available
           → Recovery: Stop and report blocker
        """
        
        system_prompt = """You are a failure classification expert.
Your job is to determine WHY something failed and what to do about it.

CATEGORIES (choose exactly ONE):

1. EXECUTION_ERROR
   - The plan was good, but execution had a bug
   - Transient error (network timeout, race condition)
   - Wrong implementation approach
   - Code has a bug that needs fixing
   → RECOVERY: Fix the code/approach and retry the same step

2. PLAN_GAP
   - The plan was incomplete or wrong
   - Missing prerequisite steps
   - Steps in wrong order
   - Assumptions in the plan were invalid
   → RECOVERY: Revise the plan (partial replan of affected steps)

3. MISSING_CAPABILITY
   - Required tool/API/library doesn't exist
   - External dependency unavailable
   - Fundamental blocker (can't be fixed without new capability)
   → RECOVERY: Stop and report blocker

Be decisive. Pick ONE category."""

        audit_text = json.dumps(audit_results, indent=2)

        prompt = f"""Classify this failure.

FAILURE DESCRIPTION:
{failure_description}

AUDIT RESULTS:
```json
{audit_text}
```

ORIGINAL PLAN:
```
{original_plan}
```

ERROR LOGS:
```
{error_logs if error_logs else "No logs provided"}
```

Analyze the failure and classify it.

Respond in this EXACT format:

CLASSIFICATION: [EXECUTION_ERROR, PLAN_GAP, or MISSING_CAPABILITY]
CONFIDENCE: [HIGH, MEDIUM, or LOW]
REASONING: [explain why this classification]
RECOVERY_STRATEGY: [what to do]
AFFECTED_STEPS: [which steps need attention]"""

        response = await self._call_ollama(prompt, system_prompt)
        
        # Parse response
        classification = "EXECUTION_ERROR"  # Default
        confidence = "LOW"
        reasoning = ""
        recovery_strategy = ""
        affected_steps = []
        
        for line in response.split('\n'):
            line = line.strip()
            
            if line.startswith("CLASSIFICATION:"):
                class_text = line.replace("CLASSIFICATION:", "").strip().upper()
                if "PLAN_GAP" in class_text:
                    classification = "PLAN_GAP"
                elif "MISSING_CAPABILITY" in class_text:
                    classification = "MISSING_CAPABILITY"
                else:
                    classification = "EXECUTION_ERROR"
            
            elif line.startswith("CONFIDENCE:"):
                conf_text = line.replace("CONFIDENCE:", "").strip().upper()
                if "HIGH" in conf_text:
                    confidence = "HIGH"
                elif "LOW" in conf_text:
                    confidence = "LOW"
                else:
                    confidence = "MEDIUM"
            
            elif line.startswith("REASONING:"):
                reasoning = line.replace("REASONING:", "").strip()
            
            elif line.startswith("RECOVERY_STRATEGY:"):
                recovery_strategy = line.replace("RECOVERY_STRATEGY:", "").strip()
            
            elif line.startswith("AFFECTED_STEPS:"):
                steps_text = line.replace("AFFECTED_STEPS:", "").strip()
                if steps_text and steps_text.lower() != "none":
                    affected_steps.append(steps_text)
        
        return {
            "classification": classification,
            "confidence": confidence,
            "reasoning": reasoning,
            "recovery_strategy": recovery_strategy,
            "affected_steps": affected_steps,
            "raw_response": response
        }
    
    async def suggest_recovery_action(
        self,
        failure_type: str,
        failure_context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Get specific recovery actions based on failure type."""
        
        system_prompt = """You are a recovery strategy advisor.
Given a failure type and context, provide CONCRETE, ACTIONABLE recovery steps.

Be specific. No vague advice."""

        context_text = json.dumps(failure_context, indent=2)

        prompt = f"""Provide recovery actions for this failure.

FAILURE TYPE: {failure_type}

CONTEXT:
```json
{context_text}
```

Based on the failure type, provide specific recovery actions.

Respond in this format:

ACTION: [primary action to take]
STEPS:
1. [concrete step 1]
2. [concrete step 2]
...

PRECAUTIONS:
- [what to watch out for]
- [potential issues]

STOP_CONDITIONS:
- [when to stop trying]
"""

        response = await self._call_ollama(prompt, system_prompt)
        
        return {
            "failure_type": failure_type,
            "recovery_action": response
        }
    
    async def should_retry(
        self,
        failure_description: str,
        retry_count: int,
        error_pattern: str = ""
    ) -> Dict[str, Any]:
        """Determine if a failed step should be retried."""
        
        system_prompt = """You are a retry decision engine.
Decide if retrying makes sense or if it's futile.

RULES:
- Transient errors (network, timeout): YES, retry
- Deterministic bugs: NO, don't retry (fix first)
- After 3 retries: NO (stop wasting time)
- Random/intermittent errors: YES, but max 2 retries"""

        prompt = f"""Should we retry this failure?

FAILURE:
{failure_description}

RETRY COUNT: {retry_count}
ERROR PATTERN: {error_pattern if error_pattern else "Unknown"}

Respond in this format:

SHOULD_RETRY: [YES or NO]
MAX_RETRIES: [number]
REASONING: [why retry or not]
SUGGESTED_CHANGES: [what to change before retrying, if any]"""

        response = await self._call_ollama(prompt, system_prompt)
        
        should_retry = "YES" in response and "SHOULD_RETRY: YES" in response
        
        # Parse max retries
        max_retries = 3
        for line in response.split('\n'):
            if line.startswith("MAX_RETRIES:"):
                try:
                    max_retries = int(line.replace("MAX_RETRIES:", "").strip())
                except:
                    max_retries = 3
        
        return {
            "should_retry": should_retry,
            "max_retries": max_retries,
            "current_retry_count": retry_count,
            "retries_remaining": max(0, max_retries - retry_count),
            "recommendation": response
        }
    
    async def identify_root_cause(
        self,
        failure_chain: List[str],
        error_logs: str = ""
    ) -> Dict[str, Any]:
        """Identify root cause, not just symptoms."""
        
        system_prompt = """You are a root cause analyst.
Don't just report symptoms. Find the UNDERLYING cause.

Examples:
- Symptom: "File not found"
  Root cause: "File path variable not initialized"

- Symptom: "Test failed"
  Root cause: "Test expects mock data that wasn't set up"

Dig deeper."""

        chain_text = "\n".join([f"{i+1}. {event}" for i, event in enumerate(failure_chain)])

        prompt = f"""Identify the root cause of this failure.

FAILURE CHAIN (sequence of events):
{chain_text}

ERROR LOGS:
```
{error_logs if error_logs else "No logs provided"}
```

Analyze and identify the ROOT CAUSE (not just symptoms).

Respond in this format:

SYMPTOMS: [what we observe]
ROOT_CAUSE: [underlying problem]
WHY: [explanation of how symptoms relate to root cause]
FIX: [how to address the root cause]"""

        response = await self._call_ollama(prompt, system_prompt)
        
        return {
            "analysis": response,
            "failure_chain_length": len(failure_chain)
        }
    
    async def close(self):
        """Close HTTP client."""
        await self.client.aclose()

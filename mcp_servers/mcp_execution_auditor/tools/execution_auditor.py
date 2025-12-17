"""Execution auditing engine using local AI (Qwen)."""
import asyncio
import httpx
import json
from typing import Dict, Any, List, Optional


class ExecutionAuditor:
    """Audits execution against approved plans using local Ollama models."""
    
    def __init__(self, model_name: str = "qwen3-coder:30b", ollama_url: str = "http://localhost:11434"):
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
                    "temperature": 0.1,  # Low temperature for consistent auditing
                    "top_p": 0.9
                }
            )
            response.raise_for_status()
            result = response.json()
            return result.get("response", "")
        except Exception as e:
            return f"ERROR: Failed to call Ollama: {str(e)}"
    
    async def audit_execution(
        self,
        approved_plan: str,
        execution_summary: str,
        artifacts: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Audit execution against the approved plan.
        
        Returns step-by-step audit with status: DONE, FAILED, or BLOCKED
        """
        
        system_prompt = """You are a strict execution auditor.
Your job is to compare what was PLANNED vs what was actually DONE.

You are NOT helpful. You are NOT encouraging. You ONLY judge based on evidence.

Rules:
- DONE: Clear evidence that the step was completed as planned
- FAILED: Evidence shows the step was attempted but failed
- BLOCKED: Step was not attempted (missing from execution)

If there's no evidence, it's BLOCKED or FAILED, never DONE.
Be harsh. Demand proof."""

        artifacts_text = json.dumps(artifacts, indent=2) if artifacts else "No artifacts provided"

        audit_prompt = f"""Compare the approved plan against what was actually executed.

APPROVED PLAN:
```
{approved_plan}
```

EXECUTION SUMMARY:
```
{execution_summary}
```

ARTIFACTS (Evidence):
```json
{artifacts_text}
```

For EACH step in the approved plan, determine its status.

Respond in this EXACT format:

STEP: [step description from plan]
STATUS: [DONE, FAILED, or BLOCKED]
EVIDENCE: [what evidence proves this status]
REASON: [brief explanation]

STEP: [next step]
STATUS: [DONE, FAILED, or BLOCKED]
EVIDENCE: [evidence]
REASON: [explanation]

...

OVERALL: [PASS if all DONE, FAIL if any FAILED/BLOCKED]
COMPLETION: [X/Y steps completed]"""

        response = await self._call_ollama(audit_prompt, system_prompt)
        
        # Parse the audit response
        result = self._parse_audit_response(response, approved_plan)
        return result
    
    def _parse_audit_response(self, response: str, original_plan: str) -> Dict[str, Any]:
        """Parse the AI's audit response into structured data."""
        
        steps = []
        current_step = {}
        overall_status = "FAIL"
        completion = "0/0"
        
        for line in response.split('\n'):
            line = line.strip()
            
            if line.startswith("STEP:"):
                # Save previous step if exists
                if current_step:
                    steps.append(current_step)
                current_step = {"step": line.replace("STEP:", "").strip()}
            
            elif line.startswith("STATUS:"):
                status = line.replace("STATUS:", "").strip().upper()
                current_step["status"] = status if status in ["DONE", "FAILED", "BLOCKED"] else "BLOCKED"
            
            elif line.startswith("EVIDENCE:"):
                current_step["evidence"] = line.replace("EVIDENCE:", "").strip()
            
            elif line.startswith("REASON:"):
                current_step["reason"] = line.replace("REASON:", "").strip()
            
            elif line.startswith("OVERALL:"):
                overall_text = line.replace("OVERALL:", "").strip().upper()
                overall_status = "PASS" if "PASS" in overall_text else "FAIL"
            
            elif line.startswith("COMPLETION:"):
                completion = line.replace("COMPLETION:", "").strip()
        
        # Add last step
        if current_step:
            steps.append(current_step)
        
        # Calculate statistics
        done_count = sum(1 for s in steps if s.get("status") == "DONE")
        failed_count = sum(1 for s in steps if s.get("status") == "FAILED")
        blocked_count = sum(1 for s in steps if s.get("status") == "BLOCKED")
        
        return {
            "overall_status": overall_status,
            "completion": f"{done_count}/{len(steps)}",
            "steps": steps,
            "statistics": {
                "total_steps": len(steps),
                "done": done_count,
                "failed": failed_count,
                "blocked": blocked_count
            },
            "raw_response": response
        }
    
    async def verify_definition_of_done(
        self,
        definition_of_done: str,
        artifacts: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Verify if Definition of Done criteria were met."""
        
        system_prompt = """You are a Definition of Done verifier.
Check if EVERY criterion in the DoD has evidence proving it was met.

Be strict. If there's no evidence, the criterion is NOT met."""

        artifacts_text = json.dumps(artifacts, indent=2)

        prompt = f"""Verify if the Definition of Done criteria were met.

DEFINITION OF DONE:
```
{definition_of_done}
```

AVAILABLE EVIDENCE:
```json
{artifacts_text}
```

For each DoD criterion, check if there's evidence.

Respond in this format:

CRITERION: [criterion text]
MET: [YES or NO]
EVIDENCE: [what proves it or what's missing]

CRITERION: [next criterion]
MET: [YES or NO]
EVIDENCE: [evidence]

OVERALL: [PASS if all YES, FAIL if any NO]"""

        response = await self._call_ollama(prompt, system_prompt)
        
        # Parse response
        criteria = []
        current = {}
        overall = "FAIL"
        
        for line in response.split('\n'):
            line = line.strip()
            
            if line.startswith("CRITERION:"):
                if current:
                    criteria.append(current)
                current = {"criterion": line.replace("CRITERION:", "").strip()}
            
            elif line.startswith("MET:"):
                met_text = line.replace("MET:", "").strip().upper()
                current["met"] = "YES" in met_text
            
            elif line.startswith("EVIDENCE:"):
                current["evidence"] = line.replace("EVIDENCE:", "").strip()
            
            elif line.startswith("OVERALL:"):
                overall_text = line.replace("OVERALL:", "").strip().upper()
                overall = "PASS" if "PASS" in overall_text else "FAIL"
        
        if current:
            criteria.append(current)
        
        met_count = sum(1 for c in criteria if c.get("met", False))
        
        return {
            "overall_status": overall,
            "criteria_met": f"{met_count}/{len(criteria)}",
            "criteria": criteria,
            "all_criteria_met": met_count == len(criteria)
        }
    
    async def compare_plan_vs_execution(
        self,
        plan_steps: List[str],
        executed_steps: List[str]
    ) -> Dict[str, Any]:
        """Simple step-by-step comparison."""
        
        system_prompt = """You are a plan vs execution comparator.
Match executed steps to planned steps.

Report:
- Which planned steps were executed
- Which planned steps were skipped
- Which executed steps were not in the plan (scope creep)"""

        plan_text = "\n".join([f"{i+1}. {step}" for i, step in enumerate(plan_steps)])
        exec_text = "\n".join([f"{i+1}. {step}" for i, step in enumerate(executed_steps)])

        prompt = f"""Compare planned steps vs executed steps.

PLANNED STEPS:
{plan_text}

EXECUTED STEPS:
{exec_text}

Report:
1. Which planned steps were executed?
2. Which planned steps were SKIPPED?
3. Which executed steps were NOT in the plan?

Format:
EXECUTED: [list]
SKIPPED: [list]
OUT_OF_SCOPE: [list]"""

        response = await self._call_ollama(prompt, system_prompt)
        
        return {
            "comparison": response,
            "plan_step_count": len(plan_steps),
            "executed_step_count": len(executed_steps)
        }
    
    async def check_evidence_quality(
        self,
        claim: str,
        evidence: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Check if evidence is sufficient to support a claim."""
        
        system_prompt = """You are an evidence quality assessor.
Determine if the provided evidence is SUFFICIENT to prove the claim.

Standards:
- STRONG: Clear, direct evidence that proves the claim
- WEAK: Indirect or partial evidence
- NONE: No relevant evidence provided

Be harsh. Vague evidence = WEAK or NONE."""

        evidence_text = json.dumps(evidence, indent=2)

        prompt = f"""Assess the quality of evidence for this claim.

CLAIM:
{claim}

EVIDENCE PROVIDED:
```json
{evidence_text}
```

Assess the evidence quality.

Respond in this format:
QUALITY: [STRONG, WEAK, or NONE]
REASONING: [why this quality rating]
MISSING: [what additional evidence would strengthen this]"""

        response = await self._call_ollama(prompt, system_prompt)
        
        # Parse quality
        quality = "NONE"
        if "QUALITY: STRONG" in response:
            quality = "STRONG"
        elif "QUALITY: WEAK" in response:
            quality = "WEAK"
        
        return {
            "quality": quality,
            "sufficient": quality == "STRONG",
            "assessment": response
        }
    
    async def close(self):
        """Close HTTP client."""
        await self.client.aclose()

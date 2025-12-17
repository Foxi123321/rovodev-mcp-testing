"""Plan validation engine using local AI (Qwen/Gemma)."""
import asyncio
import httpx
import json
from typing import Dict, Any, List, Optional


class PlanValidator:
    """Validates execution plans using local Ollama models."""
    
    def __init__(self, model_name: str = "gemma2:9b", ollama_url: str = "http://localhost:11434"):
        self.model_name = model_name
        self.ollama_url = ollama_url
        self.client = httpx.AsyncClient(timeout=None)  # No timeout - let it run as long as needed
    
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
                    "temperature": 0.1,  # Low temperature for consistent validation
                    "top_p": 0.9,
                    "num_ctx": 32768,  # INCREASED: 32K context window (was default 2K)
                    "num_predict": 2048  # Allow longer responses
                }
            )
            response.raise_for_status()
            result = response.json()
            return result.get("response", "")
        except httpx.TimeoutException as e:
            return f"ERROR: Failed to call Ollama: Timeout (this shouldn't happen with no timeout set). Exception: {type(e).__name__}: {str(e) or 'No details'}"
        except httpx.HTTPStatusError as e:
            return f"ERROR: Failed to call Ollama: HTTP {e.response.status_code} - {str(e)}"
        except httpx.ConnectError as e:
            return f"ERROR: Failed to call Ollama: Connection refused - Is Ollama running at {self.ollama_url}? Exception: {str(e) or 'No details'}"
        except Exception as e:
            return f"ERROR: Failed to call Ollama: {type(e).__name__}: {str(e) or repr(e)}"
    
    async def validate_plan_from_file(
        self,
        file_path: str,
        context: Optional[str] = None,
        strict_mode: bool = True
    ) -> Dict[str, Any]:
        """Validate a plan from a file (for large plans)."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                plan = f.read()
            return await self.validate_plan(plan, context, strict_mode)
        except FileNotFoundError:
            return {
                "status": "ERROR",
                "score": 0,
                "issues": [f"File not found: {file_path}"],
                "strict_mode": strict_mode
            }
        except Exception as e:
            return {
                "status": "ERROR",
                "score": 0,
                "issues": [f"Failed to read file: {str(e)}"],
                "strict_mode": strict_mode
            }

    async def validate_plan(
        self, 
        plan: str, 
        context: Optional[str] = None,
        strict_mode: bool = True
    ) -> Dict[str, Any]:
        """
        Validate an execution plan.
        
        Returns:
            {
                "status": "PASS" or "FAIL",
                "issues": [list of issues if FAIL],
                "score": 0-100,
                "details": {...}
            }
        """
        
        system_prompt = """You are a plan validation engine for OPERATIONAL PLANS, not code.
You evaluate PLANS (what will be done), not IMPLEMENTATIONS (how code works).

Focus on:
- Is the PLAN structure clear?
- Are the STEPS defined?
- Are the GOALS measurable?
- Is the WORKFLOW logical?

DO NOT focus on:
- Whether code is fully implemented
- Whether helper functions have bodies
- Whether every function has try/catch blocks
- Code quality or completeness

You are validating a PLAN DOCUMENT, not production code."""

        validation_prompt = f"""Validate this EXECUTION PLAN (operational document, not code).

Check ONLY these aspects:

CRITICAL (must have):
1. Clear phases/tasks defined
2. Measurable success criteria for each phase
3. Tools/APIs are named (implementation details not required)
4. Workflow order is logical (dependencies clear)
5. Final outcome is defined

IMPORTANT (for high score):
6. Error handling STRATEGY mentioned (full implementation not required)
7. Verification steps included
8. Rollback/recovery STRATEGY mentioned
9. Time estimates provided

IGNORE these (NOT part of plan validation):
- Whether code blocks are complete or stubs
- Whether helper functions have full implementations
- Whether every tool call has try/catch
- Markdown syntax issues like missing backticks

{'STRICT MODE: Plan must be detailed and specific, but code completeness is NOT required.' if strict_mode else ''}

Context:
{context if context else 'None'}

Plan to validate:
{plan[:50000]}{'...(truncated for length)' if len(plan) > 50000 else ''}

Respond EXACTLY:
STATUS: [PASS or FAIL]
SCORE: [0-100]
ISSUES:
- [issue 1]
- [issue 2]

If PASS: ISSUES: None

Focus on PLAN QUALITY, not code completeness."""

        response = await self._call_ollama(validation_prompt, system_prompt)
        
        # Parse response
        result = self._parse_validation_response(response, strict_mode)
        return result
    
    def _parse_validation_response(self, response: str, strict_mode: bool) -> Dict[str, Any]:
        """Parse the AI's validation response."""
        lines = response.strip().split('\n')
        
        status = "FAIL"  # Default to fail
        score = 0
        issues = []
        
        for line in lines:
            line = line.strip()
            if line.startswith("STATUS:"):
                status_text = line.replace("STATUS:", "").strip().upper()
                if "PASS" in status_text:
                    status = "PASS"
                else:
                    status = "FAIL"
            
            elif line.startswith("SCORE:"):
                try:
                    score = int(line.replace("SCORE:", "").strip())
                except:
                    score = 0
            
            elif line.startswith("- ") or line.startswith("* "):
                issue = line[2:].strip()
                if issue and issue.lower() != "none":
                    issues.append(issue)
        
        # In strict mode, score < 80 is a fail
        if strict_mode and score < 80:
            status = "FAIL"
            if not issues:
                issues.append("Score below strict mode threshold (80)")
        
        return {
            "status": status,
            "score": score,
            "issues": issues if issues else None,
            "strict_mode": strict_mode,
            "raw_response": response
        }
    
    async def validate_against_available_tools(
        self, 
        plan: str, 
        available_tools: List[str]
    ) -> Dict[str, Any]:
        """Check if plan only uses tools that actually exist."""
        
        system_prompt = """You are a tool verification engine.
Extract all tool/function/API calls mentioned in the plan and check if they exist in the available tools list.
Be precise - exact name matching only."""

        prompt = f"""Extract all tools/functions/APIs that this plan tries to use.

Available tools:
{json.dumps(available_tools, indent=2)}

Plan:
```
{plan}
```

List any tools mentioned in the plan that are NOT in the available tools list.

Respond in this format:
MISSING_TOOLS:
- [tool name 1]
- [tool name 2]

If all tools exist, write:
MISSING_TOOLS: None"""

        response = await self._call_ollama(prompt, system_prompt)
        
        # Parse missing tools
        missing_tools = []
        in_missing = False
        
        for line in response.split('\n'):
            line = line.strip()
            if line.startswith("MISSING_TOOLS:"):
                in_missing = True
                rest = line.replace("MISSING_TOOLS:", "").strip()
                if rest.lower() != "none" and rest:
                    missing_tools.append(rest)
            elif in_missing and (line.startswith("- ") or line.startswith("* ")):
                tool = line[2:].strip()
                if tool.lower() != "none":
                    missing_tools.append(tool)
        
        if missing_tools:
            return {
                "status": "FAIL",
                "missing_tools": missing_tools,
                "message": f"Plan references {len(missing_tools)} tools that don't exist"
            }
        else:
            return {
                "status": "PASS",
                "missing_tools": None,
                "message": "All referenced tools are available"
            }
    
    async def check_definition_of_done(self, plan: str) -> Dict[str, Any]:
        """Check if plan has clear success criteria."""
        
        system_prompt = """You are a Definition of Done validator.
Check if the plan has MEASURABLE, SPECIFIC success criteria.

Bad: "Make it work", "Fix the bug", "Complete the feature"
Good: "All tests pass", "API returns 200 status", "File created at /path/to/file"
"""

        prompt = f"""Does this plan have a clear, measurable Definition of Done?

Plan:
```
{plan}
```

Answer in this format:
HAS_DOD: [YES or NO]
CRITERIA:
- [criterion 1 if found]
- [criterion 2 if found]

If NO, explain what's missing."""

        response = await self._call_ollama(prompt, system_prompt)
        
        has_dod = "NO" in response.upper() and "HAS_DOD: NO" in response.upper()
        
        if "HAS_DOD: YES" in response.upper():
            return {
                "status": "PASS",
                "has_definition_of_done": True,
                "details": response
            }
        else:
            return {
                "status": "FAIL",
                "has_definition_of_done": False,
                "message": "Plan lacks measurable success criteria",
                "details": response
            }
    
    async def suggest_improvements(
        self, 
        plan: str, 
        validation_errors: List[str]
    ) -> Dict[str, Any]:
        """Suggest how to fix a failed plan."""
        
        system_prompt = """You are a plan improvement advisor.
Given a plan and its validation errors, suggest SPECIFIC, ACTIONABLE fixes.

Do NOT rewrite the entire plan.
Do NOT be vague.
Give concrete suggestions for each error."""

        errors_text = "\n".join([f"- {err}" for err in validation_errors])
        
        prompt = f"""This plan failed validation with these errors:
{errors_text}

Original plan:
```
{plan}
```

For EACH error above, provide a specific fix.

Format:
ERROR: [error text]
FIX: [concrete suggestion]

ERROR: [next error]
FIX: [concrete suggestion]
"""

        response = await self._call_ollama(prompt, system_prompt)
        
        return {
            "suggestions": response,
            "original_errors": validation_errors
        }
    
    async def close(self):
        """Close HTTP client."""
        await self.client.aclose()

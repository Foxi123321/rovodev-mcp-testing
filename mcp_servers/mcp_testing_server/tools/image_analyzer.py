"""Image analysis tools for screenshot review."""
import asyncio
import subprocess
import json
import re
import uuid
from pathlib import Path
from typing import Dict, Any, Optional
from datetime import datetime


class ImageAnalyzer:
    """Analyzes screenshots using vision models."""
    
    def __init__(self):
        self.vision_model = None
        self._check_available_models()
        self.jobs = {}  # Track async jobs
    
    def _check_available_models(self):
        """Check which vision models are available."""
        try:
            ollama_path = r"C:\Users\ggfuc\AppData\Local\Programs\Ollama\ollama.exe"
            result = subprocess.run(
                [ollama_path, "list"],
                capture_output=True,
                text=True,
                timeout=5
            )
            
            # Check for vision models
            if "llava" in result.stdout.lower() or "bakllava" in result.stdout.lower():
                if "llava:13b" in result.stdout:
                    self.vision_model = "llava:13b"
                elif "llava:7b" in result.stdout or "llava:latest" in result.stdout:
                    self.vision_model = "llava:latest"
                elif "bakllava" in result.stdout:
                    self.vision_model = "bakllava"
        except Exception:
            pass
    
    def _clean_output(self, text: str) -> str:
        """Remove ANSI escape codes and other noise from output."""
        # Remove ANSI escape codes
        ansi_escape = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')
        text = ansi_escape.sub('', text)
        
        # Remove progress indicators and other noise
        text = re.sub(r'\[?\?\d+[hl]', '', text)
        text = re.sub(r'\[\d+G', '', text)
        text = re.sub(r'\[K', '', text)
        text = re.sub(r'⠙|⠹|⠸|⠼|⠴|⠦|⠧|⠇|⠋', '', text)
        
        # Remove "Added image" line
        lines = text.split('\n')
        lines = [l for l in lines if not l.strip().startswith('Added image')]
        
        return '\n'.join(lines).strip()
    
    async def _run_analysis(self, job_id: str, image_path: str, prompt: str):
        """Run analysis in background."""
        try:
            ollama_path = r"C:\Users\ggfuc\AppData\Local\Programs\Ollama\ollama.exe"
            
            process = await asyncio.create_subprocess_exec(
                ollama_path, "run", self.vision_model, prompt, image_path,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            stdout, stderr = await process.communicate()
            cleaned_output = self._clean_output(stdout.decode('utf-8', errors='ignore'))
            
            self.jobs[job_id] = {
                "status": "completed",
                "result": cleaned_output,
                "completed_at": datetime.now().isoformat()
            }
            
            # Also save to file for easy retrieval
            result_file = Path(__file__).parent.parent / "screenshots" / f"analysis_{job_id}.txt"
            result_file.parent.mkdir(exist_ok=True)
            result_file.write_text(cleaned_output, encoding='utf-8')
        except Exception as e:
            self.jobs[job_id] = {
                "status": "error",
                "error": str(e),
                "completed_at": datetime.now().isoformat()
            }
    
    async def analyze_screenshot(self, image_path: str, prompt: Optional[str] = None, wait: bool = False) -> Dict[str, Any]:
        """Analyze a screenshot using a vision model.
        
        Args:
            image_path: Path to image
            prompt: Analysis prompt
            wait: If True, wait for result. If False, return job_id immediately.
        """
        if not Path(image_path).exists():
            return {
                "status": "error",
                "message": f"Image not found: {image_path}"
            }
        
        if not self.vision_model:
            return {
                "status": "no_vision_model",
                "message": "No vision model installed. Install with: ollama pull llava:latest",
                "suggestion": "Vision models can 'see' screenshots and describe UI issues"
            }
        
        # Default prompt if none provided
        if not prompt:
            prompt = """Analyze this screenshot and describe:
1. What type of page/app is shown
2. Main UI elements (buttons, forms, text)
3. Any visual issues (broken layout, missing content, errors)
4. Overall quality assessment"""
        
        # Create job
        job_id = str(uuid.uuid4())[:8]
        self.jobs[job_id] = {
            "status": "running",
            "started_at": datetime.now().isoformat(),
            "image": image_path
        }
        
        # Start async task
        task = asyncio.create_task(self._run_analysis(job_id, image_path, prompt))
        # Keep reference to prevent garbage collection
        if not hasattr(self, "_tasks"):
            self._tasks = set()
        self._tasks.add(task)
        task.add_done_callback(self._tasks.discard)
        
        if wait:
            # Wait for completion (old behavior)
            while self.jobs[job_id]["status"] == "running":
                await asyncio.sleep(0.5)
            
            if self.jobs[job_id]["status"] == "completed":
                return {
                    "status": "success",
                    "image": image_path,
                    "model": self.vision_model,
                    "analysis": self.jobs[job_id]["result"]
                }
            else:
                return {
                    "status": "error",
                    "message": self.jobs[job_id].get("error", "Unknown error")
                }
        else:
            # Return immediately with job ID
            return {
                "status": "started",
                "job_id": job_id,
                "message": f"Analysis started. Use get_analysis_result with job_id={job_id} to check status.",
                "image": image_path,
                "model": self.vision_model
            }
    
    async def get_analysis_result(self, job_id: str) -> Dict[str, Any]:
        """Get result of a running analysis job."""
        if job_id not in self.jobs:
            return {
                "status": "error",
                "message": f"Job {job_id} not found"
            }
        
        job = self.jobs[job_id]
        
        if job["status"] == "running":
            return {
                "status": "running",
                "job_id": job_id,
                "message": "Analysis still in progress..."
            }
        elif job["status"] == "completed":
            return {
                "status": "success",
                "job_id": job_id,
                "analysis": job["result"],
                "completed_at": job["completed_at"]
            }
        else:
            return {
                "status": "error",
                "job_id": job_id,
                "message": job.get("error", "Unknown error")
            }
    
    async def compare_screenshots(self, image1: str, image2: str) -> Dict[str, Any]:
        """Compare two screenshots to find differences."""
        if not self.vision_model:
            return {
                "status": "no_vision_model",
                "message": "No vision model installed"
            }
        
        prompt = f"""Compare these two screenshots and identify:
1. What changed between them
2. Any new errors or issues
3. Visual differences in layout or content

First image: {image1}
Second image: {image2}"""
        
        return await self.analyze_screenshot(image1, prompt, wait=True)
    
    async def detect_ui_issues(self, image_path: str) -> Dict[str, Any]:
        """Specialized check for common UI problems."""
        if not self.vision_model:
            return {
                "status": "no_vision_model",
                "message": "No vision model installed"
            }
        
        prompt = """You are a UI/UX expert. Analyze this screenshot for:
1. Broken layouts or overlapping elements
2. Missing images or icons
3. Text readability issues
4. Error messages or warnings visible
5. Console error indicators
6. Responsive design problems

Rate severity: LOW/MEDIUM/HIGH for each issue found."""
        
        return await self.analyze_screenshot(image_path, prompt, wait=False)
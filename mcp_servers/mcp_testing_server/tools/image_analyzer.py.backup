"""Image analysis tools for screenshot review."""
import subprocess
import json
from pathlib import Path
from typing import Dict, Any, Optional


class ImageAnalyzer:
    """Analyzes screenshots using vision models."""
    
    def __init__(self):
        self.vision_model = None
        self._check_available_models()
    
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
    
    def analyze_screenshot(self, image_path: str, prompt: Optional[str] = None) -> Dict[str, Any]:
        """Analyze a screenshot using a vision model."""
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
        
        try:
            # Call Ollama vision model with image
            ollama_path = r"C:\Users\ggfuc\AppData\Local\Programs\Ollama\ollama.exe"
            result = subprocess.run(
                [ollama_path, "run", self.vision_model, prompt, image_path],
                capture_output=True,
                text=True,
                timeout=60
            )
            
            return {
                "status": "success",
                "image": image_path,
                "model": self.vision_model,
                "analysis": result.stdout.strip()
            }
        
        except subprocess.TimeoutExpired:
            return {
                "status": "timeout",
                "message": "Vision model took too long (>60s)"
            }
        except Exception as e:
            return {
                "status": "error",
                "message": str(e)
            }
    
    def compare_screenshots(self, image1: str, image2: str) -> Dict[str, Any]:
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
        
        try:
            ollama_path = r"C:\Users\ggfuc\AppData\Local\Programs\Ollama\ollama.exe"
            result = subprocess.run(
                [ollama_path, "run", self.vision_model, prompt],
                capture_output=True,
                text=True,
                timeout=60
            )
            
            return {
                "status": "success",
                "images": [image1, image2],
                "model": self.vision_model,
                "comparison": result.stdout.strip()
            }
        
        except Exception as e:
            return {
                "status": "error",
                "message": str(e)
            }
    
    def detect_ui_issues(self, image_path: str) -> Dict[str, Any]:
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
        
        return self.analyze_screenshot(image_path, prompt)

"""Desktop application testing tools using PyAutoGUI."""
import subprocess
import time
import pyautogui
from pathlib import Path
from typing import Dict, Any, Optional, Tuple
from PIL import ImageGrab


class AppTester:
    """Tests desktop applications via UI automation."""
    
    def __init__(self):
        self.current_process = None
        self.app_window = None
        # Safety settings
        pyautogui.PAUSE = 0.5  # 0.5 second pause between actions
        pyautogui.FAILSAFE = True  # Move mouse to corner to abort
        
    def launch_app(self, command: str, wait_time: int = 3) -> Dict[str, Any]:
        """Launch a desktop application."""
        try:
            # Launch the app
            self.current_process = subprocess.Popen(
                command,
                shell=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            
            # Wait for app to start
            time.sleep(wait_time)
            
            return {
                "status": "success",
                "pid": self.current_process.pid,
                "message": f"App launched with PID {self.current_process.pid}"
            }
        except Exception as e:
            return {
                "status": "error",
                "message": str(e)
            }
    
    def find_and_click(self, image_path: str, confidence: float = 0.8) -> Dict[str, Any]:
        """Find an image on screen and click it."""
        try:
            location = pyautogui.locateOnScreen(image_path, confidence=confidence)
            
            if location:
                x, y = pyautogui.center(location)
                pyautogui.click(x, y)
                return {
                    "status": "success",
                    "position": {"x": x, "y": y},
                    "message": f"Clicked at ({x}, {y})"
                }
            else:
                return {
                    "status": "not_found",
                    "message": f"Image not found: {image_path}"
                }
        except Exception as e:
            return {
                "status": "error",
                "message": str(e)
            }
    
    def click_at(self, x: int, y: int) -> Dict[str, Any]:
        """Click at screen coordinates."""
        try:
            pyautogui.click(x, y)
            return {
                "status": "success",
                "position": {"x": x, "y": y}
            }
        except Exception as e:
            return {
                "status": "error",
                "message": str(e)
            }
    
    def move_to(self, x: int, y: int, duration: float = 0.5) -> Dict[str, Any]:
        """Move mouse to coordinates."""
        try:
            pyautogui.moveTo(x, y, duration=duration)
            return {
                "status": "success",
                "position": {"x": x, "y": y}
            }
        except Exception as e:
            return {
                "status": "error",
                "message": str(e)
            }
    
    def send_keys(self, keys: str, interval: float = 0.1) -> Dict[str, Any]:
        """Send keyboard input."""
        try:
            pyautogui.write(keys, interval=interval)
            return {
                "status": "success",
                "keys": keys
            }
        except Exception as e:
            return {
                "status": "error",
                "message": str(e)
            }
    
    def press_key(self, key: str) -> Dict[str, Any]:
        """Press a single key (e.g., 'enter', 'space', 'tab')."""
        try:
            pyautogui.press(key)
            return {
                "status": "success",
                "key": key
            }
        except Exception as e:
            return {
                "status": "error",
                "message": str(e)
            }
    
    def hotkey(self, *keys) -> Dict[str, Any]:
        """Press a combination of keys (e.g., 'ctrl', 'c')."""
        try:
            pyautogui.hotkey(*keys)
            return {
                "status": "success",
                "combination": " + ".join(keys)
            }
        except Exception as e:
            return {
                "status": "error",
                "message": str(e)
            }
    
    def take_screenshot(self, region: Optional[Tuple[int, int, int, int]] = None, 
                       save_path: Optional[str] = None) -> Dict[str, Any]:
        """Take a screenshot of the screen or a region."""
        try:
            if region:
                screenshot = ImageGrab.grab(bbox=region)
            else:
                screenshot = ImageGrab.grab()
            
            if save_path:
                screenshot.save(save_path)
                return {
                    "status": "success",
                    "path": save_path,
                    "size": screenshot.size
                }
            else:
                return {
                    "status": "success",
                    "size": screenshot.size,
                    "message": "Screenshot taken (not saved)"
                }
        except Exception as e:
            return {
                "status": "error",
                "message": str(e)
            }
    
    def get_screen_size(self) -> Dict[str, Any]:
        """Get the screen resolution."""
        try:
            size = pyautogui.size()
            return {
                "status": "success",
                "width": size.width,
                "height": size.height
            }
        except Exception as e:
            return {
                "status": "error",
                "message": str(e)
            }
    
    def get_mouse_position(self) -> Dict[str, Any]:
        """Get current mouse position."""
        try:
            pos = pyautogui.position()
            return {
                "status": "success",
                "x": pos.x,
                "y": pos.y
            }
        except Exception as e:
            return {
                "status": "error",
                "message": str(e)
            }
    
    def close_app(self) -> Dict[str, Any]:
        """Close the launched application."""
        try:
            if self.current_process:
                self.current_process.terminate()
                self.current_process.wait(timeout=5)
                return {
                    "status": "success",
                    "message": "App closed"
                }
            else:
                return {
                    "status": "warning",
                    "message": "No app process to close"
                }
        except Exception as e:
            if self.current_process:
                self.current_process.kill()
            return {
                "status": "error",
                "message": str(e)
            }

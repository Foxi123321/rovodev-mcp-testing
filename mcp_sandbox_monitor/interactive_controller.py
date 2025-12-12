"""
Interactive Controller - Sends input to running PowerShell processes
And launches monitored processes in visible windows
"""
import subprocess
import psutil
import time
from typing import Optional, List
from pathlib import Path

try:
    import pyautogui
    import pygetwindow as gw
    PYAUTOGUI_AVAILABLE = True
except ImportError:
    PYAUTOGUI_AVAILABLE = False
    print("⚠️ pyautogui not available - install with: pip install pyautogui pygetwindow")

class InteractiveController:
    """Controls interactive PowerShell sessions"""
    
    def __init__(self):
        self.monitored_processes = {}  # PID -> process info
    
    def send_input_pyautogui(self, pid: int, input_text: str) -> bool:
        """Send input using pyautogui (simpler, more reliable)"""
        if not PYAUTOGUI_AVAILABLE:
            print("❌ pyautogui not installed")
            return False
        
        try:
            # Find ALL windows
            all_windows = gw.getAllWindows()
            powershell_windows = [w for w in all_windows if w.title and ('PowerShell' in w.title or 'powershell' in w.title.lower())]
            
            print(f"   Found {len(powershell_windows)} PowerShell windows")
            
            if powershell_windows:
                # Get the most recent one (last in list)
                target_window = powershell_windows[-1]
                print(f"   Targeting: {target_window.title}")
                
                # Bring to foreground
                target_window.activate()
                time.sleep(0.5)
                
                # Type the input (use write for strings, not typewrite)
                print(f"   Typing: {input_text}")
                pyautogui.write(input_text, interval=0.1)
                time.sleep(0.2)
                pyautogui.press('enter')
                
                print(f"✅ Sent '{input_text}' + Enter")
                return True
            else:
                print("⚠️ No PowerShell windows found")
                return False
                
        except Exception as e:
            print(f"❌ pyautogui error: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def send_input_to_process(self, pid: int, input_text: str) -> bool:
        """Send input to a PowerShell process window"""
        try:
            # Find all PowerShell windows and their PIDs
            ps_command = f"""
            $wshell = New-Object -ComObject wscript.shell
            
            # Get the window by finding PowerShell with matching PID
            $procs = Get-Process powershell -ErrorAction SilentlyContinue | Where-Object {{ $_.Id -eq {pid} -or $_.Parent.Id -eq {pid} }}
            
            if ($procs) {{
                foreach ($proc in $procs) {{
                    if ($proc.MainWindowHandle -ne 0) {{
                        # Bring window to front
                        $wshell.AppActivate($proc.Id)
                        Start-Sleep -Milliseconds 200
                        
                        # Send the text
                        $wshell.SendKeys("{input_text}")
                        Start-Sleep -Milliseconds 100
                        
                        # Send Enter
                        $wshell.SendKeys("{{ENTER}}")
                        
                        Write-Host "SUCCESS: Sent '{input_text}' to PID $($proc.Id)"
                        exit 0
                    }}
                }}
            }}
            
            Write-Host "FAILED: No window found for PID {pid}"
            exit 1
            """
            
            result = subprocess.run(
                ["powershell", "-NoProfile", "-Command", ps_command],
                capture_output=True,
                text=True,
                timeout=5
            )
            
            success = result.returncode == 0 and "SUCCESS" in result.stdout
            
            if success:
                print(f"✅ Sent '{input_text}' to PID {pid}")
            else:
                print(f"⚠️ Failed: {result.stdout}")
            
            return success
            
        except Exception as e:
            print(f"❌ Error sending input: {e}")
            return False
    
    def launch_monitored_process(self, command: str, visible: bool = True) -> Optional[int]:
        """Launch a process in a visible PowerShell window for monitoring"""
        try:
            if visible:
                # Launch in new visible PowerShell window
                # Write command to temp script file to avoid escaping issues
                temp_script = Path.home() / ".rovodev" / "temp_script.ps1"
                temp_pid_file = Path.home() / ".rovodev" / "temp_pid.txt"
                
                # Write the command to a script file
                temp_script.write_text(command, encoding='utf-8')
                
                # Launch PowerShell with the script file (use -NoProfile to prevent Ollama hang)
                ps_command = f"""
                $p = Start-Process powershell -ArgumentList '-NoProfile', '-NoExit', '-ExecutionPolicy', 'Bypass', '-File', '{str(temp_script)}' -WindowStyle Normal -PassThru
                $p.Id | Out-File -FilePath '{str(temp_pid_file)}' -Encoding utf8 -NoNewline
                """
                
                subprocess.run(
                    ["powershell", "-NoProfile", "-Command", ps_command],
                    capture_output=True,
                    timeout=10
                )
                
                # Read PID from file
                time.sleep(0.5)  # Give it a moment to write
                
                if temp_pid_file.exists():
                    try:
                        # Read as UTF-8 bytes and strip BOM if present
                        pid_text = temp_pid_file.read_text(encoding='utf-8-sig').strip()
                        pid = int(pid_text)
                        temp_pid_file.unlink()  # Clean up
                        temp_script.unlink()  # Clean up script file too
                        
                        print(f"✅ Launched process PID {pid} in visible window")
                        self.monitored_processes[pid] = {
                            'command': command,
                            'start_time': time.time(),
                            'visible': True
                        }
                        return pid
                    except (ValueError, FileNotFoundError) as e:
                        print(f"⚠️ Could not read PID: {e}")
                        return None
                
                print("⚠️ Temp file not created")
                return None
            else:
                # Launch hidden (background)
                process = subprocess.Popen(
                    ["powershell", "-NoProfile", "-Command", command],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    stdin=subprocess.PIPE,
                    text=True
                )
                
                pid = process.pid
                self.monitored_processes[pid] = {
                    'command': command,
                    'start_time': time.time(),
                    'visible': False,
                    'process': process
                }
                return pid
            
            return None
            
        except Exception as e:
            print(f"❌ Error launching process: {e}")
            return None
    
    def detect_prompts(self, pid: int) -> List[str]:
        """Detect if a process is waiting for input (prompts)"""
        try:
            # Check if process has low CPU and is waiting
            process = psutil.Process(pid)
            cpu_percent = process.cpu_percent(interval=0.5)
            
            if cpu_percent < 1.0:
                # Low CPU might mean waiting for input
                return ["Process may be waiting for input (low CPU)"]
            
            return []
            
        except Exception as e:
            return []
    
    def answer_prompt(self, pid: int, answer: str) -> bool:
        """Answer a detected prompt"""
        print(f"📝 Answering prompt for PID {pid} with: {answer}")
        
        # Try PowerShell SendKeys first (more reliable for specific PIDs)
        success = self.send_input_to_process(pid, answer)
        if success:
            return True
        
        # Fallback to pyautogui if PowerShell method fails
        if PYAUTOGUI_AVAILABLE:
            print("   PowerShell method failed, trying pyautogui...")
            return self.send_input_pyautogui(pid, answer)
        
        return False
    
    def get_process_output(self, pid: int) -> str:
        """Get recent output from a monitored process"""
        if pid in self.monitored_processes:
            proc_info = self.monitored_processes[pid]
            
            if not proc_info.get('visible') and 'process' in proc_info:
                # Can read from pipe
                process = proc_info['process']
                try:
                    # Non-blocking read
                    output = process.stdout.readline()
                    return output if output else ""
                except:
                    return ""
        
        return ""
    
    def is_waiting_for_input(self, pid: int) -> bool:
        """Check if process appears to be waiting for input"""
        try:
            process = psutil.Process(pid)
            
            # Check CPU usage
            cpu = process.cpu_percent(interval=0.5)
            
            # Check threads - waiting processes often have idle threads
            num_threads = process.num_threads()
            
            # Low CPU + multiple threads = likely waiting
            if cpu < 2.0 and num_threads > 1:
                return True
            
            return False
            
        except:
            return False

# Test if run directly
if __name__ == "__main__":
    print("🎮 Testing Interactive Controller...")
    
    controller = InteractiveController()
    
    # Test 1: Launch a visible process
    print("\n🚀 Test 1: Launching visible PowerShell window...")
    pid = controller.launch_monitored_process(
        "Write-Host 'Test process running...'; Start-Sleep -Seconds 5; Write-Host 'Done!'",
        visible=True
    )
    
    if pid:
        print(f"✅ Launched PID {pid} - check for new PowerShell window!")
        print("   (Window should show output and close after 5 seconds)")
        
        # Wait a bit
        time.sleep(2)
        
        # Check if waiting for input
        waiting = controller.is_waiting_for_input(pid)
        print(f"\n🔍 Is process waiting? {waiting}")
        
        print("\n⏳ Waiting for process to finish...")
        time.sleep(4)
    
    # Test 2: Simulating sending input
    print("\n🧪 Test 2: Simulating prompt answer...")
    print("   (This tests the mechanism, but needs a real interactive process)")
    
    # Example of how it would work:
    # 1. Detect process is waiting: controller.is_waiting_for_input(pid)
    # 2. Ask user (or Rex): "Process asks: Continue? (Y/N)"
    # 3. User approves: "Yes"
    # 4. Send input: controller.answer_prompt(pid, "Y")
    
    print("\n✅ Interactive Controller working!")
    print("\n📝 Usage flow:")
    print("   1. Launch visible process: pid = controller.launch_monitored_process(cmd, visible=True)")
    print("   2. Monitor: controller.is_waiting_for_input(pid)")
    print("   3. Answer: controller.answer_prompt(pid, 'Y')")

"""
Sandbox Monitor MCP Server
Provides process monitoring and auto-response capabilities to RovoDev/Rex
"""
import asyncio
import json
from typing import Any, Optional
from mcp.server import Server
from mcp.types import Tool, TextContent, ImageContent, EmbeddedResource
from background_monitor_daemon import BackgroundMonitor
from process_monitor import ProcessMonitor
from interactive_controller import InteractiveController
from ai_decision_engine import AIDecisionEngine
from knowledge_db_interface import KnowledgeDBInterface

# Initialize server
app = Server("sandbox-monitor")

# Global instances
monitor_daemon: Optional[BackgroundMonitor] = None
process_monitor = ProcessMonitor()
controller = InteractiveController()
ai_engine = AIDecisionEngine()
knowledge_db = KnowledgeDBInterface()

@app.list_tools()
async def list_tools() -> list[Tool]:
    """List available tools"""
    return [
        Tool(
            name="launch_monitored_process",
            description="""Launch a process in a visible window with automatic monitoring.
            The process will be tracked for stuck/waiting behavior and can receive automated responses.
            Perfect for interactive scripts that need confirmation (builds, deployments, etc.)""",
            inputSchema={
                "type": "object",
                "properties": {
                    "command": {
                        "type": "string",
                        "description": "PowerShell script or command to execute"
                    },
                    "visible": {
                        "type": "boolean",
                        "description": "Launch in visible window (default: true)",
                        "default": True
                    },
                    "auto_monitor": {
                        "type": "boolean",
                        "description": "Automatically monitor with background daemon (default: true)",
                        "default": True
                    }
                },
                "required": ["command"]
            }
        ),
        Tool(
            name="check_process_status",
            description="""Check the status of a running process.
            Returns CPU usage, memory, runtime, and whether it appears stuck/waiting.""",
            inputSchema={
                "type": "object",
                "properties": {
                    "pid": {
                        "type": "integer",
                        "description": "Process ID to check"
                    }
                },
                "required": ["pid"]
            }
        ),
        Tool(
            name="send_input_to_process",
            description="""Send keyboard input to a waiting process.
            Use this when a process is stuck waiting for user input.""",
            inputSchema={
                "type": "object",
                "properties": {
                    "pid": {
                        "type": "integer",
                        "description": "Process ID to send input to"
                    },
                    "input_text": {
                        "type": "string",
                        "description": "Text to send (e.g., 'Y', 'yes', 'n', etc.)"
                    }
                },
                "required": ["pid", "input_text"]
            }
        ),
        Tool(
            name="get_stuck_processes",
            description="""Get all currently stuck/waiting processes.
            Returns list of processes that appear to be waiting for input.""",
            inputSchema={
                "type": "object",
                "properties": {},
                "required": []
            }
        ),
        Tool(
            name="start_background_monitor",
            description="""Start the autonomous background monitoring daemon.
            It will continuously watch all registered processes and auto-respond to stuck situations.""",
            inputSchema={
                "type": "object",
                "properties": {
                    "check_interval": {
                        "type": "number",
                        "description": "How often to check processes (seconds, default: 2.0)",
                        "default": 2.0
                    }
                },
                "required": []
            }
        ),
        Tool(
            name="stop_background_monitor",
            description="""Stop the background monitoring daemon.""",
            inputSchema={
                "type": "object",
                "properties": {},
                "required": []
            }
        ),
        Tool(
            name="get_monitor_status",
            description="""Get status of the background monitor.
            Shows what processes are being tracked and if any are stuck.""",
            inputSchema={
                "type": "object",
                "properties": {},
                "required": []
            }
        ),
        Tool(
            name="search_knowledge_db",
            description="""Search the knowledge database for similar past decisions.
            Useful for learning from previous situations.""",
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Search query (e.g., 'deployment confirmation', 'stuck build')"
                    },
                    "limit": {
                        "type": "integer",
                        "description": "Max results to return (default: 5)",
                        "default": 5
                    }
                },
                "required": ["query"]
            }
        ),
        Tool(
            name="kill_process",
            description="""Force kill a process by PID.
            Use as last resort when process is truly stuck and unresponsive.""",
            inputSchema={
                "type": "object",
                "properties": {
                    "pid": {
                        "type": "integer",
                        "description": "Process ID to kill"
                    }
                },
                "required": ["pid"]
            }
        ),
        Tool(
            name="analyze_process_behavior",
            description="""Analyze a process's behavior pattern.
            Returns detailed metrics and AI insights about what the process is doing.""",
            inputSchema={
                "type": "object",
                "properties": {
                    "pid": {
                        "type": "integer",
                        "description": "Process ID to analyze"
                    }
                },
                "required": ["pid"]
            }
        )
    ]

@app.call_tool()
async def call_tool(name: str, arguments: Any) -> list[TextContent]:
    """Handle tool calls"""
    global monitor_daemon
    
    try:
        if name == "launch_monitored_process":
            command = arguments["command"]
            visible = arguments.get("visible", True)
            auto_monitor = arguments.get("auto_monitor", True)
            
            pid = controller.launch_monitored_process(command, visible=visible)
            
            if not pid:
                return [TextContent(
                    type="text",
                    text=json.dumps({
                        "success": False,
                        "error": "Failed to launch process"
                    })
                )]
            
            # Register with background monitor if requested
            if auto_monitor and monitor_daemon and monitor_daemon.running:
                monitor_daemon.register_process(pid, command)
            
            return [TextContent(
                type="text",
                text=json.dumps({
                    "success": True,
                    "pid": pid,
                    "monitoring": auto_monitor and monitor_daemon is not None,
                    "message": f"Process launched with PID {pid}"
                })
            )]
        
        elif name == "check_process_status":
            pid = arguments["pid"]
            proc_info = process_monitor.get_process_by_pid(pid)
            
            if not proc_info:
                return [TextContent(
                    type="text",
                    text=json.dumps({
                        "success": False,
                        "exists": False,
                        "error": f"Process {pid} not found (may have finished)"
                    })
                )]
            
            is_waiting = controller.is_waiting_for_input(pid)
            
            return [TextContent(
                type="text",
                text=json.dumps({
                    "success": True,
                    "exists": True,
                    "pid": pid,
                    "name": proc_info.name,
                    "cpu_percent": proc_info.cpu_percent,
                    "memory_mb": proc_info.memory_mb,
                    "runtime_seconds": proc_info.duration_seconds,
                    "is_waiting": is_waiting,
                    "status": "waiting for input" if is_waiting else "running normally"
                })
            )]
        
        elif name == "send_input_to_process":
            pid = arguments["pid"]
            input_text = arguments["input_text"]
            
            success = controller.answer_prompt(pid, input_text)
            
            # Log to knowledge DB
            if success:
                knowledge_db.store_decision(
                    scenario="Manual input to process",
                    context=f"PID {pid}, sent '{input_text}'",
                    decision=f"User/Rex sent: {input_text}",
                    outcome="Input sent successfully"
                )
            
            return [TextContent(
                type="text",
                text=json.dumps({
                    "success": success,
                    "pid": pid,
                    "input_sent": input_text,
                    "message": "Input sent successfully" if success else "Failed to send input"
                })
            )]
        
        elif name == "get_stuck_processes":
            all_procs = process_monitor.get_all_processes()
            stuck_procs = []
            
            for proc in all_procs:
                if proc.name.lower() == "powershell" and controller.is_waiting_for_input(proc.pid):
                    stuck_procs.append({
                        "pid": proc.pid,
                        "name": proc.name,
                        "cpu_percent": proc.cpu_percent,
                        "memory_mb": proc.memory_mb,
                        "runtime_seconds": proc.duration_seconds
                    })
            
            return [TextContent(
                type="text",
                text=json.dumps({
                    "success": True,
                    "stuck_count": len(stuck_procs),
                    "processes": stuck_procs
                })
            )]
        
        elif name == "start_background_monitor":
            check_interval = arguments.get("check_interval", 2.0)
            
            if monitor_daemon and monitor_daemon.running:
                return [TextContent(
                    type="text",
                    text=json.dumps({
                        "success": False,
                        "error": "Background monitor already running"
                    })
                )]
            
            monitor_daemon = BackgroundMonitor(check_interval=check_interval)
            monitor_daemon.start()
            
            return [TextContent(
                type="text",
                text=json.dumps({
                    "success": True,
                    "message": f"Background monitor started (checking every {check_interval}s)",
                    "check_interval": check_interval
                })
            )]
        
        elif name == "stop_background_monitor":
            if not monitor_daemon or not monitor_daemon.running:
                return [TextContent(
                    type="text",
                    text=json.dumps({
                        "success": False,
                        "error": "Background monitor not running"
                    })
                )]
            
            monitor_daemon.stop()
            
            return [TextContent(
                type="text",
                text=json.dumps({
                    "success": True,
                    "message": "Background monitor stopped"
                })
            )]
        
        elif name == "get_monitor_status":
            if not monitor_daemon:
                return [TextContent(
                    type="text",
                    text=json.dumps({
                        "running": False,
                        "message": "Background monitor not initialized"
                    })
                )]
            
            status = monitor_daemon.get_status()
            
            # Get detailed process info
            processes = []
            for pid, tracked in monitor_daemon.tracked_processes.items():
                processes.append({
                    "pid": pid,
                    "name": tracked.name,
                    "runtime": tracked.last_check_time - tracked.start_time,
                    "stuck": tracked.stuck_detected
                })
            
            return [TextContent(
                type="text",
                text=json.dumps({
                    "running": status["running"],
                    "tracked_processes": status["tracked_processes"],
                    "stuck_processes": status["stuck_processes"],
                    "processes": processes
                })
            )]
        
        elif name == "search_knowledge_db":
            query = arguments["query"]
            limit = arguments.get("limit", 5)
            
            results = knowledge_db.search_decisions(query, limit)
            
            return [TextContent(
                type="text",
                text=json.dumps({
                    "success": True,
                    "query": query,
                    "result_count": len(results),
                    "results": results
                })
            )]
        
        elif name == "kill_process":
            pid = arguments["pid"]
            
            success = process_monitor.kill_process(pid)
            
            return [TextContent(
                type="text",
                text=json.dumps({
                    "success": success,
                    "pid": pid,
                    "message": f"Process {pid} terminated" if success else "Failed to kill process"
                })
            )]
        
        elif name == "analyze_process_behavior":
            pid = arguments["pid"]
            proc_info = process_monitor.get_process_by_pid(pid)
            
            if not proc_info:
                return [TextContent(
                    type="text",
                    text=json.dumps({
                        "success": False,
                        "error": f"Process {pid} not found"
                    })
                )]
            
            # Analyze behavior
            is_waiting = controller.is_waiting_for_input(pid)
            
            analysis = {
                "pid": pid,
                "name": proc_info.name,
                "metrics": {
                    "cpu_percent": proc_info.cpu_percent,
                    "memory_mb": proc_info.memory_mb,
                    "runtime_seconds": proc_info.duration_seconds
                },
                "behavior": {
                    "appears_stuck": is_waiting,
                    "cpu_pattern": "idle" if proc_info.cpu_percent < 2.0 else "active",
                    "likely_waiting_for_input": is_waiting
                },
                "recommendations": []
            }
            
            if is_waiting:
                analysis["recommendations"].append("Process appears to be waiting for keyboard input")
                analysis["recommendations"].append("Consider using send_input_to_process to respond")
            
            if proc_info.cpu_percent > 80:
                analysis["recommendations"].append("High CPU usage - process is actively working")
            
            if proc_info.memory_mb > 1000:
                analysis["recommendations"].append("High memory usage - monitor for memory leaks")
            
            return [TextContent(
                type="text",
                text=json.dumps({
                    "success": True,
                    "analysis": analysis
                })
            )]
        
        else:
            return [TextContent(
                type="text",
                text=json.dumps({
                    "success": False,
                    "error": f"Unknown tool: {name}"
                })
            )]
    
    except Exception as e:
        return [TextContent(
            type="text",
            text=json.dumps({
                "success": False,
                "error": str(e)
            })
        )]

async def main():
    """Run the MCP server"""
    from mcp.server.stdio import stdio_server
    
    async with stdio_server() as (read_stream, write_stream):
        print("🤖 Sandbox Monitor MCP Server started", flush=True)
        await app.run(read_stream, write_stream, app.create_initialization_options())

if __name__ == "__main__":
    asyncio.run(main())

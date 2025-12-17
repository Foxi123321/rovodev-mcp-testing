"""
Rex Task Orchestrator MCP Server
Main server that exposes all orchestration capabilities
"""
import asyncio
import json
import logging
import os
from typing import Any, Dict, Optional
from mcp.server import Server
from mcp.types import Tool, TextContent

from task_queue import TaskQueue, TaskPriority
from workflow_engine import WorkflowEngine
from visual_tester import VisualTester
from decision_engine import DecisionEngine
from auto_healer import AutoHealer
from resource_monitor import ResourceMonitor
from event_listeners import EventListeners

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize MCP server
app = Server("rex-task-orchestrator")

# Load configuration (use absolute path)
CONFIG_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "config.json")
with open(CONFIG_PATH, "r") as f:
    CONFIG = json.load(f)

# Initialize components
task_queue = TaskQueue(max_parallel=CONFIG["task_orchestrator"]["max_parallel_tasks"])
workflow_engine = WorkflowEngine()
resource_monitor = ResourceMonitor(CONFIG["resource_monitoring"])
decision_engine = DecisionEngine()
auto_healer = AutoHealer(CONFIG["auto_healing"])
event_listeners = EventListeners(CONFIG["event_listeners"])

# Visual tester will be initialized with MCP clients later
visual_tester = None

# Store MCP client references for inter-server communication
mcp_clients = {}


@app.list_tools()
async def list_tools() -> list[Tool]:
    """List all available tools"""
    return [
        # Task Queue Tools
        Tool(
            name="add_task",
            description="Add a task to the execution queue with priority",
            inputSchema={
                "type": "object",
                "properties": {
                    "name": {"type": "string", "description": "Task name"},
                    "function_name": {"type": "string", "description": "Function to execute"},
                    "priority": {
                        "type": "string",
                        "enum": ["CRITICAL", "HIGH", "NORMAL", "LOW"],
                        "default": "NORMAL"
                    },
                    "args": {"type": "array", "description": "Function arguments", "default": []},
                    "kwargs": {"type": "object", "description": "Function keyword arguments", "default": {}},
                    "max_retries": {"type": "integer", "default": 3}
                },
                "required": ["name", "function_name"]
            }
        ),
        Tool(
            name="get_task_status",
            description="Get the status of a specific task",
            inputSchema={
                "type": "object",
                "properties": {
                    "task_id": {"type": "string", "description": "Task ID"}
                },
                "required": ["task_id"]
            }
        ),
        Tool(
            name="list_all_tasks",
            description="List all tasks grouped by status (pending, active, completed, failed)",
            inputSchema={"type": "object", "properties": {}}
        ),
        Tool(
            name="cancel_task",
            description="Cancel a pending task",
            inputSchema={
                "type": "object",
                "properties": {
                    "task_id": {"type": "string", "description": "Task ID to cancel"}
                },
                "required": ["task_id"]
            }
        ),
        
        # Workflow Tools
        Tool(
            name="create_workflow",
            description="Create a multi-step workflow with conditional logic",
            inputSchema={
                "type": "object",
                "properties": {
                    "name": {"type": "string", "description": "Workflow name"},
                    "description": {"type": "string", "default": ""},
                    "steps": {
                        "type": "array",
                        "description": "List of workflow steps",
                        "items": {
                            "type": "object",
                            "properties": {
                                "name": {"type": "string"},
                                "action": {"type": "string", "description": "Function name to execute"},
                                "args": {"type": "array", "default": []},
                                "kwargs": {"type": "object", "default": {}},
                                "retry_on_failure": {"type": "boolean", "default": False},
                                "max_retries": {"type": "integer", "default": 3}
                            }
                        }
                    }
                },
                "required": ["name"]
            }
        ),
        Tool(
            name="execute_workflow",
            description="Execute a workflow",
            inputSchema={
                "type": "object",
                "properties": {
                    "workflow_id": {"type": "string", "description": "Workflow ID to execute"}
                },
                "required": ["workflow_id"]
            }
        ),
        Tool(
            name="get_workflow_status",
            description="Get workflow execution status and results",
            inputSchema={
                "type": "object",
                "properties": {
                    "workflow_id": {"type": "string"}
                },
                "required": ["workflow_id"]
            }
        ),
        Tool(
            name="list_workflows",
            description="List all workflows",
            inputSchema={"type": "object", "properties": {}}
        ),
        
        # Visual Testing Tools
        Tool(
            name="run_visual_test",
            description="Run visual test: browser → screenshot → llava analysis → validation",
            inputSchema={
                "type": "object",
                "properties": {
                    "url": {"type": "string", "description": "URL to test"},
                    "expected_description": {"type": "string", "description": "What you expect to see"},
                    "test_id": {"type": "string", "description": "Optional test ID"},
                    "elements_to_test": {
                        "type": "array",
                        "description": "Interactive elements to test",
                        "items": {
                            "type": "object",
                            "properties": {
                                "selector": {"type": "string"},
                                "action": {"type": "string", "enum": ["click", "fill"]},
                                "value": {"type": "string"}
                            }
                        }
                    }
                },
                "required": ["url", "expected_description"]
            }
        ),
        Tool(
            name="get_visual_test_result",
            description="Get results from a visual test",
            inputSchema={
                "type": "object",
                "properties": {
                    "test_id": {"type": "string"}
                },
                "required": ["test_id"]
            }
        ),
        Tool(
            name="get_visual_test_stats",
            description="Get overall visual testing statistics",
            inputSchema={"type": "object", "properties": {}}
        ),
        
        # Decision Engine Tools
        Tool(
            name="make_decision",
            description="Make an autonomous decision based on context",
            inputSchema={
                "type": "object",
                "properties": {
                    "context": {"type": "object", "description": "Decision context data"},
                    "decision_type": {
                        "type": "string",
                        "enum": ["rule_based", "pattern_based", "threshold_based"],
                        "default": "rule_based"
                    }
                },
                "required": ["context"]
            }
        ),
        Tool(
            name="add_decision_rule",
            description="Add a decision rule to the engine",
            inputSchema={
                "type": "object",
                "properties": {
                    "name": {"type": "string"},
                    "description": {"type": "string"},
                    "priority": {"type": "integer", "default": 0}
                },
                "required": ["name"]
            }
        ),
        Tool(
            name="list_decision_rules",
            description="List all decision rules",
            inputSchema={"type": "object", "properties": {}}
        ),
        
        # Auto-Healing Tools
        Tool(
            name="detect_and_heal",
            description="Automatically detect and heal an issue",
            inputSchema={
                "type": "object",
                "properties": {
                    "error_info": {
                        "type": "object",
                        "properties": {
                            "type": {"type": "string", "description": "Error type"},
                            "message": {"type": "string", "description": "Error message"},
                            "context": {"type": "object", "description": "Additional context"}
                        },
                        "required": ["type", "message"]
                    }
                },
                "required": ["error_info"]
            }
        ),
        Tool(
            name="get_healing_history",
            description="Get auto-healing history",
            inputSchema={
                "type": "object",
                "properties": {
                    "last_n": {"type": "integer", "default": 10}
                }
            }
        ),
        Tool(
            name="get_healing_stats",
            description="Get auto-healing statistics",
            inputSchema={"type": "object", "properties": {}}
        ),
        
        # Resource Monitoring Tools
        Tool(
            name="get_system_health",
            description="Get current system health snapshot",
            inputSchema={"type": "object", "properties": {}}
        ),
        Tool(
            name="get_resource_history",
            description="Get resource monitoring history",
            inputSchema={
                "type": "object",
                "properties": {
                    "last_n": {"type": "integer", "default": 10}
                }
            }
        ),
        Tool(
            name="get_process_info",
            description="Get detailed process information",
            inputSchema={
                "type": "object",
                "properties": {
                    "pid": {"type": "integer", "description": "Process ID (optional)"}
                }
            }
        ),
        Tool(
            name="get_alerts",
            description="Get system alerts",
            inputSchema={
                "type": "object",
                "properties": {
                    "last_n": {"type": "integer", "default": 10}
                }
            }
        ),
        
        # Event Listener Tools
        Tool(
            name="trigger_event",
            description="Manually trigger an event",
            inputSchema={
                "type": "object",
                "properties": {
                    "event_type": {"type": "string"},
                    "source": {"type": "string"},
                    "data": {"type": "object"}
                },
                "required": ["event_type", "source", "data"]
            }
        ),
        Tool(
            name="get_event_history",
            description="Get event history",
            inputSchema={
                "type": "object",
                "properties": {
                    "event_type": {"type": "string", "description": "Filter by event type"},
                    "last_n": {"type": "integer", "default": 10}
                }
            }
        ),
        Tool(
            name="get_event_stats",
            description="Get event statistics",
            inputSchema={"type": "object", "properties": {}}
        ),
        
        # Orchestrator Control Tools
        Tool(
            name="start_orchestrator",
            description="Start the task orchestrator and all subsystems",
            inputSchema={"type": "object", "properties": {}}
        ),
        Tool(
            name="stop_orchestrator",
            description="Stop the task orchestrator",
            inputSchema={"type": "object", "properties": {}}
        ),
        Tool(
            name="get_orchestrator_status",
            description="Get overall orchestrator status",
            inputSchema={"type": "object", "properties": {}}
        )
    ]


@app.call_tool()
async def call_tool(name: str, arguments: Any) -> list[TextContent]:
    """Handle tool calls"""
    try:
        result = None
        
        # Task Queue Tools
        if name == "add_task":
            priority = TaskPriority[arguments.get("priority", "NORMAL")]
            # Note: In real implementation, function_name would be resolved to actual function
            task_id = task_queue.add_task(
                name=arguments["name"],
                function=lambda: None,  # Placeholder
                priority=priority,
                args=tuple(arguments.get("args", [])),
                kwargs=arguments.get("kwargs", {}),
                max_retries=arguments.get("max_retries", 3)
            )
            result = {"task_id": task_id, "status": "added"}
        
        elif name == "get_task_status":
            result = task_queue.get_task_status(arguments["task_id"])
        
        elif name == "list_all_tasks":
            result = task_queue.get_all_tasks()
        
        elif name == "cancel_task":
            success = task_queue.cancel_task(arguments["task_id"])
            result = {"cancelled": success}
        
        # Workflow Tools
        elif name == "create_workflow":
            workflow_id = workflow_engine.create_workflow(
                name=arguments["name"],
                description=arguments.get("description", ""),
                steps=arguments.get("steps", [])
            )
            result = {"workflow_id": workflow_id}
        
        elif name == "execute_workflow":
            result = await workflow_engine.execute_workflow(arguments["workflow_id"])
        
        elif name == "get_workflow_status":
            result = workflow_engine.get_workflow_status(arguments["workflow_id"])
        
        elif name == "list_workflows":
            result = workflow_engine.list_workflows()
        
        # Visual Testing Tools
        elif name == "run_visual_test":
            if visual_tester:
                test_result = await visual_tester.run_visual_test(
                    url=arguments["url"],
                    expected_description=arguments["expected_description"],
                    test_id=arguments.get("test_id"),
                    elements_to_test=arguments.get("elements_to_test")
                )
                result = test_result.to_dict()
            else:
                result = {"error": "Visual tester not initialized"}
        
        elif name == "get_visual_test_result":
            result = visual_tester.get_test_result(arguments["test_id"]) if visual_tester else None
        
        elif name == "get_visual_test_stats":
            result = visual_tester.get_test_stats() if visual_tester else {}
        
        # Decision Engine Tools
        elif name == "make_decision":
            from decision_engine import DecisionType
            decision_type_str = arguments.get("decision_type", "rule_based")
            decision_type = DecisionType[decision_type_str.upper()]
            decision = decision_engine.make_decision(arguments["context"], decision_type)
            result = decision.to_dict()
        
        elif name == "add_decision_rule":
            # Simplified - in real impl, would need to pass actual functions
            result = {"message": "Rule addition not yet implemented"}
        
        elif name == "list_decision_rules":
            result = decision_engine.get_rule_list()
        
        # Auto-Healing Tools
        elif name == "detect_and_heal":
            healing_action = await auto_healer.detect_and_heal(arguments["error_info"])
            result = healing_action.to_dict()
        
        elif name == "get_healing_history":
            result = auto_healer.get_healing_history(arguments.get("last_n", 10))
        
        elif name == "get_healing_stats":
            result = auto_healer.get_healing_stats()
        
        # Resource Monitoring Tools
        elif name == "get_system_health":
            result = resource_monitor.get_summary()
        
        elif name == "get_resource_history":
            result = resource_monitor.get_history(arguments.get("last_n", 10))
        
        elif name == "get_process_info":
            result = resource_monitor.get_process_info(arguments.get("pid"))
        
        elif name == "get_alerts":
            result = resource_monitor.get_alerts(arguments.get("last_n", 10))
        
        # Event Listener Tools
        elif name == "trigger_event":
            event_listeners.trigger_event(
                event_type=arguments["event_type"],
                source=arguments["source"],
                data=arguments["data"]
            )
            result = {"triggered": True}
        
        elif name == "get_event_history":
            result = event_listeners.get_event_history(
                event_type=arguments.get("event_type"),
                last_n=arguments.get("last_n", 10)
            )
        
        elif name == "get_event_stats":
            result = event_listeners.get_event_stats()
        
        # Orchestrator Control
        elif name == "start_orchestrator":
            event_listeners.start()
            result = {"status": "started", "message": "Task orchestrator started"}
        
        elif name == "stop_orchestrator":
            event_listeners.stop()
            task_queue.stop()
            result = {"status": "stopped", "message": "Task orchestrator stopped"}
        
        elif name == "get_orchestrator_status":
            result = {
                "task_queue": {
                    "running": task_queue.running,
                    "active_tasks": len(task_queue.active_tasks),
                    "pending_tasks": task_queue.queue.qsize()
                },
                "event_listeners": {
                    "running": event_listeners.running,
                    "active_handlers": sum(len(h) for h in event_listeners.event_handlers.values())
                },
                "resource_monitor": resource_monitor.get_summary(),
                "workflows": len(workflow_engine.workflows),
                "healing_stats": auto_healer.get_healing_stats()
            }
        
        else:
            result = {"error": f"Unknown tool: {name}"}
        
        return [TextContent(type="text", text=json.dumps(result, indent=2))]
    
    except Exception as e:
        logger.error(f"Tool execution error: {name} - {e}")
        return [TextContent(type="text", text=json.dumps({"error": str(e)}, indent=2))]


async def main():
    """Main entry point"""
    from mcp.server.stdio import stdio_server
    
    logger.info("Starting Rex Task Orchestrator MCP Server")
    
    async with stdio_server() as (read_stream, write_stream):
        await app.run(read_stream, write_stream, app.create_initialization_options())


if __name__ == "__main__":
    asyncio.run(main())

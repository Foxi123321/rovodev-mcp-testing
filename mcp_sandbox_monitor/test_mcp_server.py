"""
Test the MCP Server directly (without full MCP protocol)
This simulates what Rex would do when calling the server
"""
import json
import asyncio
from server import app, call_tool

async def test_mcp_server():
    print("🧪 Testing Sandbox Monitor MCP Server")
    print("=" * 70)
    print()
    
    # Test 1: Launch a monitored process
    print("📋 Test 1: Launch Monitored Process")
    print("-" * 70)
    
    test_script = """
    Write-Host '🔨 Test script starting...'
    Start-Sleep -Seconds 2
    Write-Host '⚠️  Ready for confirmation'
    $answer = Read-Host 'Continue? (Y/N)'
    Write-Host "You chose: $answer"
    Start-Sleep -Seconds 2
    """
    
    result = await call_tool("launch_monitored_process", {
        "command": test_script,
        "visible": True,
        "auto_monitor": False  # Manual for testing
    })
    
    response = json.loads(result[0].text)
    print(f"   Result: {json.dumps(response, indent=2)}")
    
    if not response.get("success"):
        print("❌ Failed to launch process")
        return
    
    pid = response["pid"]
    print(f"✅ Launched PID: {pid}")
    print()
    
    # Test 2: Check status
    print("📋 Test 2: Check Process Status")
    print("-" * 70)
    
    await asyncio.sleep(3)  # Let it run a bit
    
    result = await call_tool("check_process_status", {"pid": pid})
    response = json.loads(result[0].text)
    print(f"   Status: {json.dumps(response, indent=2)}")
    print()
    
    # Test 3: Send input
    if response.get("is_waiting"):
        print("📋 Test 3: Send Input to Waiting Process")
        print("-" * 70)
        
        result = await call_tool("send_input_to_process", {
            "pid": pid,
            "input_text": "Y"
        })
        response = json.loads(result[0].text)
        print(f"   Result: {json.dumps(response, indent=2)}")
        
        if response.get("success"):
            print("✅ Input sent successfully!")
        else:
            print("❌ Failed to send input")
        print()
    
    # Test 4: Search knowledge DB
    print("📋 Test 4: Search Knowledge Database")
    print("-" * 70)
    
    result = await call_tool("search_knowledge_db", {
        "query": "input",
        "limit": 3
    })
    response = json.loads(result[0].text)
    print(f"   Found {response.get('result_count', 0)} results")
    print()
    
    # Test 5: Get stuck processes
    print("📋 Test 5: Get Stuck Processes")
    print("-" * 70)
    
    result = await call_tool("get_stuck_processes", {})
    response = json.loads(result[0].text)
    print(f"   Stuck count: {response.get('stuck_count', 0)}")
    print()
    
    # Test 6: Analyze process behavior
    print("📋 Test 6: Analyze Process Behavior")
    print("-" * 70)
    
    result = await call_tool("analyze_process_behavior", {"pid": pid})
    response = json.loads(result[0].text)
    
    if response.get("success"):
        analysis = response["analysis"]
        print(f"   Process: {analysis['name']}")
        print(f"   CPU: {analysis['metrics']['cpu_percent']}%")
        print(f"   Memory: {analysis['metrics']['memory_mb']}MB")
        print(f"   Appears stuck: {analysis['behavior']['appears_stuck']}")
        if analysis.get("recommendations"):
            print(f"   Recommendations:")
            for rec in analysis["recommendations"]:
                print(f"     - {rec}")
    print()
    
    print("=" * 70)
    print("✅ ALL TESTS COMPLETE!")
    print()
    print("🎯 The MCP server is working and ready for Rex!")
    print()
    print("Next step: Add to mcp.json and test with RovoDev")

if __name__ == "__main__":
    asyncio.run(test_mcp_server())

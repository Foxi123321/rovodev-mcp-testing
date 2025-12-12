import asyncio
import sys
sys.path.insert(0, r"C:\Users\ggfuc\.rovodev\mcp_testing_server\tools")
from image_analyzer import ImageAnalyzer

async def test():
    analyzer = ImageAnalyzer()
    
    # Start analysis
    result1 = await analyzer.analyze_screenshot(
        r"C:\Users\ggfuc\OneDrive\Desktop\mission repair windows\screenshot for llava\Screenshot 2025-11-30 104704.png",
        "Describe this briefly"
    )
    print("Start result:", result1)
    
    if result1["status"] == "started":
        job_id = result1["job_id"]
        
        # Check status immediately
        result2 = await analyzer.get_analysis_result(job_id)
        print("\nImmediate check:", result2)
        
        # Wait and check again
        await asyncio.sleep(15)
        result3 = await analyzer.get_analysis_result(job_id)
        print("\nAfter 15s:", result3)

asyncio.run(test())

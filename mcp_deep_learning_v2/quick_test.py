"""Quick test to verify system is working"""
import asyncio
from ollama_client import OllamaClient
from database_manager import DatabaseManager
from code_parser import CodeParser

async def main():
    print("Testing Deep Learning Intelligence v2...")
    
    # Test 1: Database
    print("\n[1/3] Database...")
    db = DatabaseManager()
    stats = db.get_stats()
    print(f"  ✓ DB initialized: {stats}")
    
    # Test 2: Parser
    print("\n[2/3] Code Parser...")
    parser = CodeParser()
    from config import SUPPORTED_EXTENSIONS
    print(f"  ✓ Parser ready (supports: {len(SUPPORTED_EXTENSIONS)} languages)")
    
    # Test 3: Ollama
    print("\n[3/3] Ollama Connection...")
    async with OllamaClient() as client:
        has_deepseek = await client.check_model_available("deepseek-coder:33b")
        has_qwen = await client.check_model_available("qwen3-coder:30b")
        
        print(f"  {'✓' if has_deepseek else '✗'} deepseek-coder:33b")
        print(f"  {'✓' if has_qwen else '✗'} qwen3-coder:30b")
        
        if has_deepseek and has_qwen:
            print("\n✓ ALL SYSTEMS GO! Ready to analyze code!")
        else:
            print("\n⚠ Models missing - pull them with ollama")

if __name__ == "__main__":
    asyncio.run(main())

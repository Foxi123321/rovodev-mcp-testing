import asyncio
from ollama_client import OllamaClient

async def test():
    print("Testing Ollama connection and models...\n")
    
    async with OllamaClient() as client:
        # Test simple generation
        print("1. Testing DeepSeek generation...")
        result = await client.generate(
            model="deepseek-coder:33b",
            prompt="Explain what this function does in one sentence: def add(a, b): return a + b",
            temperature=0.1
        )
        
        print(f"Success: {result['success']}")
        if result['success']:
            print(f"Response: {result['response'][:200]}")
        else:
            print(f"Error: {result['error']}")
        
        print("\n2. Testing Qwen generation...")
        result2 = await client.generate(
            model="qwen3-coder:30b",
            prompt="What is the purpose of this code: def add(a, b): return a + b",
            temperature=0.1
        )
        
        print(f"Success: {result2['success']}")
        if result2['success']:
            print(f"Response: {result2['response'][:200]}")
        else:
            print(f"Error: {result2['error']}")

asyncio.run(test())

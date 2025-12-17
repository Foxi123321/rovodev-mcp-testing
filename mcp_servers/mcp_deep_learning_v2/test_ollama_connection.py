import asyncio
from ollama_client import OllamaClient
from config import EMBEDDING_MODEL

async def test():
    print("Testing Ollama connection...")
    client = OllamaClient()
    print(f"Base URL: {client.base_url}")
    print(f"Embedding model: {EMBEDDING_MODEL}")
    
    print("\nTesting embedding request...")
    try:
        emb = await client.get_embedding("test code snippet")
        if emb:
            print(f"✓ SUCCESS: Got {len(emb)} dimensions")
        else:
            print("✗ FAILED: No embedding returned")
    except Exception as e:
        print(f"✗ ERROR: {e}")
    
    if hasattr(client, 'session') and client.session:
        await client.session.close()

if __name__ == "__main__":
    asyncio.run(test())

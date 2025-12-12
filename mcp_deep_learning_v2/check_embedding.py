import asyncio
from ollama_client import OllamaClient

async def test():
    async with OllamaClient() as c:
        emb = await c.get_embedding('test code sample')
        if emb:
            print(f'Embedding dimension: {len(emb)}')
            print(f'Sample values: {emb[:5]}')
        else:
            print('Failed to get embedding')

asyncio.run(test())

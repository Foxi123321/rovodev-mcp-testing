"""
Minimal test to see if we can index just a few files
"""
import asyncio
import sys
import os
from pathlib import Path

# Set environment variables BEFORE importing config
os.environ["DEEP_LEARNING_DB_PATH"] = str(Path.home() / ".rovodev" / "deep_learning_v2" / "knowledge_new.db")
os.environ["DEEP_LEARNING_VECTOR_PATH"] = str(Path.home() / ".rovodev" / "deep_learning_v2" / "vectors_new.faiss")

from database_manager import DatabaseManager
from code_parser import CodeParser
from vector_store import VectorStore, CodeEmbedder
from ollama_client import OllamaClient

async def main():
    print("Testing minimal indexing...")
    print(f"DB Path: {os.environ['DEEP_LEARNING_DB_PATH']}")
    print(f"Vector Path: {os.environ['DEEP_LEARNING_VECTOR_PATH']}")
    
    # Delete old files
    db_path = Path(os.environ['DEEP_LEARNING_DB_PATH'])
    vec_path = Path(os.environ['DEEP_LEARNING_VECTOR_PATH'])
    
    if db_path.exists():
        db_path.unlink()
        print(f"Deleted old DB")
    if vec_path.exists():
        vec_path.unlink()
        print(f"Deleted old vectors")
    
    # Initialize
    print("\nInitializing components...")
    db = DatabaseManager()
    parser = CodeParser()
    vector_store = VectorStore()
    
    print(f"DB initialized at: {db.db_path}")
    print(f"Vector store dimension: {vector_store.dimension}")
    
    # Parse just ONE file
    print("\nParsing a single test file...")
    test_file = Path(__file__).parent / "config.py"
    
    parsed_files = parser.parse_directory(test_file.parent, recursive=False)
    parsed_files = [f for f in parsed_files if f['file_path'] == str(test_file)][:1]
    
    print(f"Found {len(parsed_files)} files")
    
    if not parsed_files:
        print("No files found!")
        return
    
    async with OllamaClient() as client:
        embedder = CodeEmbedder(client)
        
        for file_data in parsed_files:
            print(f"\nIndexing: {file_data['file_path']}")
            
            # Store file
            file_id = db.store_file(
                file_data["file_path"],
                file_data["language"],
                file_data["size_bytes"],
                file_data["last_modified"],
                file_data["content_hash"]
            )
            print(f"  File ID: {file_id}")
            
            # Store just first 3 entities
            entities = file_data.get("entities", [])[:3]
            print(f"  Processing {len(entities)} entities...")
            
            for entity in entities:
                print(f"    - {entity['name']}...", end="", flush=True)
                
                entity_id = db.store_entity(
                    file_id,
                    entity.get("entity_type", entity.get("type")),
                    entity["name"],
                    entity.get("signature"),
                    entity.get("start_line"),
                    entity.get("end_line"),
                    entity.get("code_snippet")
                )
                
                # Create embedding
                try:
                    embedding = await embedder.embed_code(
                        entity.get("code_snippet", ""),
                        context=f"File: {file_data['file_path']}\nType: {entity.get('entity_type', entity.get('type'))}\nName: {entity['name']}"
                    )
                    
                    if embedding:
                        vector_id = await vector_store.add_embedding(
                            embedding,
                            {
                                "entity_id": entity_id,
                                "name": entity["name"],
                                "type": entity.get("entity_type", entity.get("type")),
                                "file": file_data["file_path"],
                                "line": entity.get("start_line")
                            }
                        )
                        print(f" OK (vector {vector_id})")
                    else:
                        print(" FAILED (no embedding)")
                except Exception as e:
                    print(f" ERROR: {e}")
    
    # Save vector store
    print("\nSaving vector store...")
    vector_store.save()
    
    # Check stats
    stats = db.get_stats()
    print(f"\n✓ COMPLETE")
    print(f"  Files: {stats['files']}")
    print(f"  Entities: {stats['entities']}")
    print(f"  Vectors: {vector_store.get_stats()['total_vectors']}")
    
    # Verify files exist
    if db_path.exists():
        size_mb = db_path.stat().st_size / (1024 * 1024)
        print(f"\n✓ DB file: {size_mb:.2f} MB")
    else:
        print("\n❌ DB file NOT created!")
    
    if vec_path.exists():
        size_mb = vec_path.stat().st_size / (1024 * 1024)
        print(f"✓ Vector file: {size_mb:.2f} MB")
    else:
        print("❌ Vector file NOT created!")

if __name__ == "__main__":
    asyncio.run(main())

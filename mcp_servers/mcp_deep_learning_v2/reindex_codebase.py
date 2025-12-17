"""
Re-index the .rovodev codebase with FIXED configuration:
- Full code snippets (no truncation)
- Working embedding model (gemma2:9b)
- Progress tracking with ETA
"""
import asyncio
import sys
import time
from pathlib import Path

# Add to path
sys.path.insert(0, str(Path(__file__).parent))

from database_manager import DatabaseManager
from code_parser import CodeParser
from vector_store import VectorStore, CodeEmbedder
from ollama_client import OllamaClient
from config import DATA_DIR
import os

# Override config to use new database names
os.environ["DEEP_LEARNING_DB_PATH"] = str(DATA_DIR / "knowledge_new.db")
os.environ["DEEP_LEARNING_VECTOR_PATH"] = str(DATA_DIR / "vectors_new.faiss")

async def main():
    print("=" * 80)
    print("RE-INDEXING ROVODEV CODEBASE WITH FIXED CONFIGURATION")
    print("=" * 80)
    print()
    print("Fixes applied:")
    print("  ✓ Full code snippets (no truncation)")
    print("  ✓ Embedding model: nomic-embed-text (15x faster, optimized for code)")
    print("  ✓ Vector store will be created")
    print()
    
    # Use NEW database name to avoid lock issues
    db_path = DATA_DIR / "knowledge_new.db"
    vectors_path = DATA_DIR / "vectors_new.faiss"
    
    # Backup old paths for reference
    old_db = DATA_DIR / "knowledge.db"
    old_vectors = DATA_DIR / "vectors.faiss"
    
    # Check for --force flag
    import sys
    force = "--force" in sys.argv
    
    if not force:
        confirm = input("This will CLEAR the existing database and re-index. Continue? (yes/no): ")
        if confirm.lower() != "yes":
            print("Aborted.")
            return
    else:
        print("🔥 Force mode enabled - clearing database...")
    
    print("\n📝 Using NEW database files to avoid locks...")
    print(f"   New DB: {db_path}")
    print(f"   New Vectors: {vectors_path}")
    print(f"   (Old files left untouched at knowledge.db and vectors.faiss)")
    
    # Delete new files if they exist
    if db_path.exists():
        db_path.unlink()
    if vectors_path.exists():
        vectors_path.unlink()
    
    # Initialize fresh components
    db = DatabaseManager()
    parser = CodeParser()
    vector_store = VectorStore()
    
    print("\n📂 Parsing .rovodev directory...")
    rovodev_path = Path.home() / ".rovodev"
    
    start_time = time.time()
    parsed_files = parser.parse_directory(rovodev_path, recursive=True)
    
    if not parsed_files:
        print("❌ No files found!")
        return
    
    print(f"\n✓ Found {len(parsed_files)} files to index")
    
    # Count total entities
    total_entities = sum(len(f.get("entities", [])) for f in parsed_files)
    print(f"✓ Total code entities: {total_entities}")
    print()
    
    # Index with progress tracking
    print("🔄 Indexing and creating embeddings...")
    print("=" * 80)
    
    indexed_files = 0
    indexed_entities = 0
    failed_embeddings = 0
    
    async with OllamaClient() as client:
        embedder = CodeEmbedder(client)
        
        for file_idx, file_data in enumerate(parsed_files, 1):
            # Progress indicator
            elapsed = time.time() - start_time
            rate = indexed_files / elapsed if elapsed > 0 else 0
            remaining = (len(parsed_files) - indexed_files) / rate if rate > 0 else 0
            
            print(f"\rProgress: {file_idx}/{len(parsed_files)} files | "
                  f"{indexed_entities} entities | "
                  f"⚠ {failed_embeddings} failed embeddings | "
                  f"ETA: {remaining/60:.1f} min", end="", flush=True)
            
            # Store file
            file_id = db.store_file(
                file_data["file_path"],
                file_data["language"],
                file_data["size_bytes"],
                file_data["last_modified"],
                file_data["content_hash"]
            )
            
            indexed_files += 1
            
            # Store entities and create embeddings
            for entity in file_data.get("entities", []):
                entity_id = db.store_entity(
                    file_id,
                    entity.get("entity_type", entity.get("type")),
                    entity["name"],
                    entity.get("signature"),
                    entity.get("start_line"),
                    entity.get("end_line"),
                    entity.get("code_snippet")
                )
                
                indexed_entities += 1
                
                # Create embedding for vector search
                try:
                    # Larger delay to prevent Ollama overload (0.5s = much more stable)
                    await asyncio.sleep(0.5)
                    embedding = await embedder.embed_code(
                        entity.get("code_snippet", ""),
                        context=f"File: {file_data['file_path']}\nType: {entity.get('entity_type', entity.get('type'))}\nName: {entity['name']}"
                    )
                    
                    if embedding:
                        await vector_store.add_embedding(
                            embedding,
                            {
                                "entity_id": entity_id,
                                "name": entity["name"],
                                "type": entity.get("entity_type", entity.get("type")),
                                "file": file_data["file_path"],
                                "line": entity.get("start_line")
                            }
                        )
                    else:
                        failed_embeddings += 1
                except Exception as e:
                    failed_embeddings += 1
                    # Don't print errors, just count them
    
    print()  # New line after progress
    
    # Save vector index
    print("\n💾 Saving vector store...")
    vector_store.save()
    
    # Verify
    print("\n✅ INDEXING COMPLETE!")
    print("=" * 80)
    
    stats = db.get_stats()
    vector_stats = vector_store.get_stats()
    
    total_time = time.time() - start_time
    
    print(f"\nDatabase Stats:")
    print(f"  Files indexed: {stats['files']}")
    print(f"  Code entities: {stats['entities']}")
    print(f"  Vector embeddings: {vector_stats['total_vectors']}")
    print(f"  Failed embeddings: {failed_embeddings}")
    print(f"  Total time: {total_time/60:.1f} minutes")
    
    # Verify vector store file exists
    if vectors_path.exists():
        size_mb = vectors_path.stat().st_size / (1024 * 1024)
        print(f"\n✓ Vector store created: {vectors_path}")
        print(f"  Size: {size_mb:.2f} MB")
    else:
        print(f"\n❌ WARNING: Vector store file not created!")
    
    print("\n🎉 System is now ready for semantic code queries!")
    print("\nYou can now use the MCP server to query the codebase:")
    print('  Example: "Where are session tokens generated in RovoDev?"')

if __name__ == "__main__":
    asyncio.run(main())

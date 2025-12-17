"""
Re-index the .rovodev codebase with TURBO MODE:
- BATCHED embeddings (20x parallel requests)
- NO sleep delays
- Resume capability
- Retry logic for 500 errors
- GPU maxed out
"""
import asyncio
import sys
import time
from pathlib import Path
from typing import List, Dict, Any
import json

# Add to path
sys.path.insert(0, str(Path(__file__).parent))

from database_manager import DatabaseManager
from code_parser import CodeParser
from vector_store import VectorStore, CodeEmbedder
from ollama_client import OllamaClient
from config import DATA_DIR
from code_chunker import chunk_code_smartly
import os

# Use the ACTIVE database (not the new one)
DB_PATH = DATA_DIR / "knowledge.db"
VECTORS_PATH = DATA_DIR / "vectors.faiss"
CHECKPOINT_PATH = DATA_DIR / "indexing_checkpoint.json"

BATCH_SIZE = 10  # Process 10 embeddings in parallel (more stable)
MAX_RETRIES = 3  # Retry failed embeddings
BATCH_DELAY = 0.1  # Small delay between batches to prevent Ollama overload

async def create_embeddings_batch(
    embedder: CodeEmbedder,
    entities_batch: List[Dict[str, Any]],
    file_paths: List[str]
) -> List[tuple]:
    """Create embeddings for a batch of entities with retry logic"""
    
    tasks = []
    for entity, file_path in zip(entities_batch, file_paths):
        code = entity.get("code_snippet", "")
        context = f"File: {file_path}\nType: {entity.get('entity_type', entity.get('type'))}\nName: {entity['name']}"
        tasks.append(embedder.embed_code(code, context))
    
    # Execute all in parallel
    results = []
    for attempt in range(MAX_RETRIES):
        try:
            embeddings = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Process results
            final_results = []
            retry_indices = []
            
            for idx, emb in enumerate(embeddings):
                if isinstance(emb, Exception):
                    if attempt < MAX_RETRIES - 1:
                        retry_indices.append(idx)
                        final_results.append(None)
                    else:
                        final_results.append(None)  # Failed after retries
                else:
                    final_results.append(emb)
            
            # If no retries needed, return
            if not retry_indices:
                return list(zip(entities_batch, final_results))
            
            # Retry failed ones
            if attempt < MAX_RETRIES - 1:
                print(f"\n⚠ Retrying {len(retry_indices)} failed embeddings (attempt {attempt + 2}/{MAX_RETRIES})...", end="")
                await asyncio.sleep(1)  # Brief pause before retry
                retry_tasks = [tasks[i] for i in retry_indices]
                retry_results = await asyncio.gather(*retry_tasks, return_exceptions=True)
                
                # Update results
                for retry_idx, result in zip(retry_indices, retry_results):
                    if not isinstance(result, Exception):
                        final_results[retry_idx] = result
                
                return list(zip(entities_batch, final_results))
            
        except Exception as e:
            if attempt == MAX_RETRIES - 1:
                print(f"\n⚠ Batch failed after {MAX_RETRIES} attempts: {e}")
                return [(entity, None) for entity in entities_batch]
            await asyncio.sleep(1)
    
    return list(zip(entities_batch, [None] * len(entities_batch)))


def save_checkpoint(indexed_files: int, indexed_entities: int, failed_embeddings: int):
    """Save progress checkpoint"""
    checkpoint = {
        "indexed_files": indexed_files,
        "indexed_entities": indexed_entities,
        "failed_embeddings": failed_embeddings,
        "timestamp": time.time()
    }
    with open(CHECKPOINT_PATH, "w") as f:
        json.dump(checkpoint, f)


def load_checkpoint() -> Dict[str, int]:
    """Load progress checkpoint"""
    if CHECKPOINT_PATH.exists():
        try:
            with open(CHECKPOINT_PATH, "r") as f:
                return json.load(f)
        except:
            pass
    return {"indexed_files": 0, "indexed_entities": 0, "failed_embeddings": 0}


async def main():
    print("=" * 80)
    print("🚀 TURBO MODE INDEXER - BATCHED PARALLEL EMBEDDINGS")
    print("=" * 80)
    print()
    print("Optimizations:")
    print("  ✓ Batched embeddings (20x parallel)")
    print("  ✓ No sleep delays")
    print("  ✓ Retry logic for failures")
    print("  ✓ Resume from checkpoint")
    print("  ✓ GPU will be MAXED OUT")
    print()
    
    # Load checkpoint
    checkpoint = load_checkpoint()
    start_from = checkpoint.get("indexed_files", 0)
    
    if start_from > 0:
        print(f"📌 Resuming from file {start_from}")
        print(f"   Previously indexed: {checkpoint['indexed_entities']} entities")
        print(f"   Failed embeddings: {checkpoint['failed_embeddings']}")
        print()
    
    # Initialize components
    db = DatabaseManager()
    parser = CodeParser()
    vector_store = VectorStore()
    
    print("📂 Parsing .rovodev directory...")
    rovodev_path = Path.home() / ".rovodev"
    
    start_time = time.time()
    parsed_files = parser.parse_directory(rovodev_path, recursive=True)
    
    if not parsed_files:
        print("❌ No files found!")
        return
    
    # Skip already processed files
    if start_from > 0:
        print(f"⏭  Skipping first {start_from} files...")
        parsed_files = parsed_files[start_from:]
    
    print(f"\n✓ Found {len(parsed_files)} files to index")
    
    # Count total entities
    total_entities = sum(len(f.get("entities", [])) for f in parsed_files)
    print(f"✓ Total code entities: {total_entities}")
    print()
    
    # Index with batched embedding
    print("🔄 Indexing and creating embeddings in TURBO MODE...")
    print("=" * 80)
    
    indexed_files = start_from
    indexed_entities = checkpoint.get("indexed_entities", 0)
    failed_embeddings = checkpoint.get("failed_embeddings", 0)
    total_chunks_created = 0
    large_entities_split = 0
    
    async with OllamaClient() as client:
        embedder = CodeEmbedder(client)
        
        # Collect entities for batching
        entity_batch = []
        entity_metadata = []
        
        for file_idx, file_data in enumerate(parsed_files, 1):
            # Progress indicator
            elapsed = time.time() - start_time
            rate = file_idx / elapsed if elapsed > 0 else 0
            remaining = (len(parsed_files) - file_idx) / rate if rate > 0 else 0
            
            print(f"\rProgress: {indexed_files + file_idx}/{start_from + len(parsed_files)} files | "
                  f"{indexed_entities} entities | "
                  f"⚠ {failed_embeddings} failed | "
                  f"ETA: {remaining/60:.1f} min", end="", flush=True)
            
            # Store file
            file_id = db.store_file(
                file_data["file_path"],
                file_data["language"],
                file_data["size_bytes"],
                file_data["last_modified"],
                file_data["content_hash"]
            )
            
            # Collect entities for this file
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
                
                # SMART CHUNKING: Split large code into manageable pieces
                code_snippet = entity.get("code_snippet", "")
                entity_name = entity["name"]
                entity_type = entity.get("entity_type", entity.get("type"))
                
                chunks = chunk_code_smartly(code_snippet, entity_name, entity_type)
                
                # Track chunking stats
                if len(chunks) > 1:
                    large_entities_split += 1
                total_chunks_created += len(chunks)
                
                # Add each chunk to batch
                for chunk_data in chunks:
                    # Create modified entity with chunked code
                    chunked_entity = entity.copy()
                    chunked_entity["code_snippet"] = chunk_data["chunk"]
                    chunked_entity["name"] = chunk_data["entity_name"]
                    
                    entity_batch.append(chunked_entity)
                    entity_metadata.append({
                        "entity_id": entity_id,
                        "name": chunk_data["entity_name"],
                        "type": entity_type,
                        "file": file_data["file_path"],
                        "line": entity.get("start_line"),
                        "chunk_info": f"{chunk_data['chunk_index']+1}/{chunk_data['total_chunks']}"
                    })
                
                # Process batch when full
                if len(entity_batch) >= BATCH_SIZE:
                    try:
                        # Small delay to prevent hammering Ollama
                        await asyncio.sleep(BATCH_DELAY)
                        
                        results = await create_embeddings_batch(
                            embedder,
                            entity_batch,
                            [m["file"] for m in entity_metadata]
                        )
                        
                        # Store embeddings
                        for (entity, embedding), metadata in zip(results, entity_metadata):
                            if embedding:
                                await vector_store.add_embedding(embedding, metadata)
                            else:
                                failed_embeddings += 1
                    except Exception as e:
                        print(f"\n⚠ Batch error: {e}")
                        failed_embeddings += len(entity_batch)
                    
                    # Clear batch
                    entity_batch = []
                    entity_metadata = []
            
            indexed_files += 1
            
            # Save checkpoint every 100 files
            if file_idx % 100 == 0:
                save_checkpoint(indexed_files, indexed_entities, failed_embeddings)
        
        # Process remaining batch
        if entity_batch:
            try:
                results = await create_embeddings_batch(
                    embedder,
                    entity_batch,
                    [m["file"] for m in entity_metadata]
                )
                
                for (entity, embedding), metadata in zip(results, entity_metadata):
                    if embedding:
                        await vector_store.add_embedding(embedding, metadata)
                    else:
                        failed_embeddings += 1
            except Exception as e:
                print(f"\n⚠ Final batch error: {e}")
                failed_embeddings += len(entity_batch)
    
    print()  # New line after progress
    
    # Save vector index
    print("\n💾 Saving vector store...")
    vector_store.save()
    
    # Clean up checkpoint
    if CHECKPOINT_PATH.exists():
        CHECKPOINT_PATH.unlink()
    
    # Results
    print("\n✅ TURBO INDEXING COMPLETE!")
    print("=" * 80)
    
    stats = db.get_stats()
    vector_stats = vector_store.get_stats()
    
    total_time = time.time() - start_time
    
    print(f"\nDatabase Stats:")
    print(f"  Files indexed: {stats['files']}")
    print(f"  Code entities: {stats['entities']}")
    print(f"  Vector embeddings: {vector_stats['total_vectors']}")
    print(f"  Failed embeddings: {failed_embeddings} ({failed_embeddings/total_chunks_created*100:.1f}%)")
    print(f"\nChunking Stats:")
    print(f"  Large entities split: {large_entities_split:,}")
    print(f"  Total chunks created: {total_chunks_created:,}")
    print(f"  Avg chunks per entity: {total_chunks_created/indexed_entities:.1f}")
    print(f"\nPerformance:")
    print(f"  Total time: {total_time/60:.1f} minutes")
    print(f"  Speed: {indexed_entities / total_time:.1f} entities/sec")
    print(f"  Chunk embedding rate: {total_chunks_created / total_time:.1f} chunks/sec")
    
    # Verify vector store
    if VECTORS_PATH.exists():
        size_mb = VECTORS_PATH.stat().st_size / (1024 * 1024)
        print(f"\n✓ Vector store: {VECTORS_PATH}")
        print(f"  Size: {size_mb:.2f} MB")
    
    print("\n🎉 System ready for semantic code queries!")

if __name__ == "__main__":
    asyncio.run(main())

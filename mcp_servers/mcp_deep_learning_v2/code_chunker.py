"""
Smart code chunker - splits large code blocks into embeddable chunks
Preserves context while keeping chunks under safe limits for Ollama
"""
from typing import List, Dict, Any
import re

MAX_CHUNK_SIZE = 3000  # Safe limit for embedding models (conservative)
OVERLAP_SIZE = 200     # Overlap between chunks for context continuity


def estimate_tokens(text: str) -> int:
    """Rough token estimation: ~4 chars per token"""
    return len(text) // 4


def chunk_code_smartly(code: str, entity_name: str, entity_type: str) -> List[Dict[str, Any]]:
    """
    Split large code blocks into smaller chunks intelligently
    
    Strategy:
    1. If small enough (<= MAX_CHUNK_SIZE), return as-is
    2. For classes: split by methods/functions
    3. For large functions: split by logical blocks (loops, conditionals)
    4. Last resort: split by lines with overlap
    
    Returns list of chunks with metadata
    """
    
    if not code or len(code) <= MAX_CHUNK_SIZE:
        return [{
            "chunk": code,
            "chunk_index": 0,
            "total_chunks": 1,
            "entity_name": entity_name,
            "entity_type": entity_type
        }]
    
    # Strategy: Try to split by methods/functions first
    if entity_type == "class":
        chunks = _split_class_by_methods(code, entity_name)
        if chunks:
            return chunks
    
    # Fallback: Split by logical blocks (functions, loops, etc.)
    chunks = _split_by_logical_blocks(code, entity_name, entity_type)
    if chunks:
        return chunks
    
    # Last resort: Split by lines with overlap
    return _split_by_lines(code, entity_name, entity_type)


def _split_class_by_methods(code: str, class_name: str) -> List[Dict[str, Any]]:
    """Split a class by its methods"""
    chunks = []
    
    # Find all method definitions (works for Python, JS, TS, etc.)
    # Patterns: "def method", "function method", "method() {", "method: function"
    method_patterns = [
        r'\n\s+(def\s+\w+)',           # Python
        r'\n\s+(function\s+\w+)',      # JS function
        r'\n\s+(\w+\s*\([^)]*\)\s*\{)', # JS/TS method
        r'\n\s+(\w+\s*:\s*function)',  # Object method
        r'\n\s+(async\s+\w+)',         # Async methods
    ]
    
    # Find all method starts
    method_positions = []
    for pattern in method_patterns:
        for match in re.finditer(pattern, code):
            method_positions.append(match.start())
    
    if len(method_positions) < 2:
        return []  # Not enough methods to split
    
    method_positions = sorted(set(method_positions))
    
    # Extract class header (everything before first method)
    class_header = code[:method_positions[0]].strip()
    
    # Split by methods
    for i, start in enumerate(method_positions):
        end = method_positions[i + 1] if i + 1 < len(method_positions) else len(code)
        method_code = code[start:end].strip()
        
        # Include class header with each method for context
        chunk_code = f"{class_header}\n\n{method_code}"
        
        # If still too large, split this method further
        if len(chunk_code) > MAX_CHUNK_SIZE:
            # Just take the method without full header
            chunk_code = method_code
            if len(chunk_code) > MAX_CHUNK_SIZE:
                # Split this large method by lines
                sub_chunks = _split_by_lines(chunk_code, f"{class_name}[method_{i}]", "function")
                chunks.extend(sub_chunks)
                continue
        
        chunks.append({
            "chunk": chunk_code,
            "chunk_index": i,
            "total_chunks": len(method_positions),
            "entity_name": f"{class_name}[method_{i}]",
            "entity_type": "class_method"
        })
    
    # Update total_chunks for all
    for chunk in chunks:
        chunk["total_chunks"] = len(chunks)
    
    return chunks


def _split_by_logical_blocks(code: str, entity_name: str, entity_type: str) -> List[Dict[str, Any]]:
    """Split by logical blocks (functions, loops, etc.)"""
    chunks = []
    
    # Find major block starts
    block_patterns = [
        r'\n(def\s+\w+)',
        r'\n(function\s+\w+)',
        r'\n(class\s+\w+)',
        r'\n(for\s+)',
        r'\n(while\s+)',
        r'\n(if\s+)',
    ]
    
    block_positions = [0]  # Start with beginning
    for pattern in block_patterns:
        for match in re.finditer(pattern, code):
            block_positions.append(match.start())
    
    if len(block_positions) < 2:
        return []
    
    block_positions = sorted(set(block_positions))
    block_positions.append(len(code))  # Add end
    
    current_chunk = ""
    chunk_index = 0
    
    for i in range(len(block_positions) - 1):
        block = code[block_positions[i]:block_positions[i + 1]]
        
        if len(current_chunk) + len(block) <= MAX_CHUNK_SIZE:
            current_chunk += block
        else:
            # Save current chunk
            if current_chunk:
                chunks.append({
                    "chunk": current_chunk.strip(),
                    "chunk_index": chunk_index,
                    "total_chunks": 0,  # Will update later
                    "entity_name": f"{entity_name}[part_{chunk_index}]",
                    "entity_type": entity_type
                })
                chunk_index += 1
            
            # Start new chunk
            current_chunk = block
    
    # Add final chunk
    if current_chunk.strip():
        chunks.append({
            "chunk": current_chunk.strip(),
            "chunk_index": chunk_index,
            "total_chunks": 0,
            "entity_name": f"{entity_name}[part_{chunk_index}]",
            "entity_type": entity_type
        })
    
    # Update total_chunks
    for chunk in chunks:
        chunk["total_chunks"] = len(chunks)
    
    return chunks if len(chunks) > 1 else []


def _split_by_lines(code: str, entity_name: str, entity_type: str) -> List[Dict[str, Any]]:
    """Last resort: split by lines with overlap"""
    lines = code.split('\n')
    chunks = []
    chunk_index = 0
    
    current_chunk_lines = []
    current_size = 0
    
    for line in lines:
        line_size = len(line) + 1  # +1 for newline
        
        if current_size + line_size > MAX_CHUNK_SIZE and current_chunk_lines:
            # Save current chunk
            chunk_code = '\n'.join(current_chunk_lines)
            chunks.append({
                "chunk": chunk_code,
                "chunk_index": chunk_index,
                "total_chunks": 0,  # Will update later
                "entity_name": f"{entity_name}[chunk_{chunk_index}]",
                "entity_type": entity_type
            })
            chunk_index += 1
            
            # Start new chunk with overlap (last few lines)
            overlap_lines = current_chunk_lines[-5:] if len(current_chunk_lines) >= 5 else current_chunk_lines
            current_chunk_lines = overlap_lines + [line]
            current_size = sum(len(l) + 1 for l in current_chunk_lines)
        else:
            current_chunk_lines.append(line)
            current_size += line_size
    
    # Add final chunk
    if current_chunk_lines:
        chunk_code = '\n'.join(current_chunk_lines)
        chunks.append({
            "chunk": chunk_code,
            "chunk_index": chunk_index,
            "total_chunks": 0,
            "entity_name": f"{entity_name}[chunk_{chunk_index}]",
            "entity_type": entity_type
        })
    
    # Update total_chunks
    for chunk in chunks:
        chunk["total_chunks"] = len(chunks)
    
    return chunks


if __name__ == "__main__":
    # Test with a large code sample
    test_code = """
class LargeClass:
    def __init__(self):
        self.data = []
        
    def method1(self):
        # Lots of code here
        """ + ("x" * 5000) + """
        
    def method2(self):
        # More code
        """ + ("y" * 5000) + """
        
    def method3(self):
        # Even more
        """ + ("z" * 5000)
    
    chunks = chunk_code_smartly(test_code, "LargeClass", "class")
    print(f"Split into {len(chunks)} chunks:")
    for chunk in chunks:
        print(f"  - {chunk['entity_name']}: {len(chunk['chunk'])} chars")

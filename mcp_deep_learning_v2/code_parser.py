"""
Code Parser - Extract functions, classes, and relationships from code
Uses tree-sitter for robust parsing
"""

import logging
from pathlib import Path
from typing import Dict, List, Any, Optional
import hashlib
import os

try:
    from tree_sitter import Language, Parser
    TREE_SITTER_AVAILABLE = True
except ImportError:
    TREE_SITTER_AVAILABLE = False
    logging.warning("tree-sitter not available - using fallback parser")

from config import SUPPORTED_EXTENSIONS, CONTEXT_EXTENSIONS, IGNORE_PATTERNS

logger = logging.getLogger(__name__)


class CodeParser:
    """Parse code files and extract structure"""
    
    def __init__(self):
        self.parsers = {}
        if TREE_SITTER_AVAILABLE:
            self._init_tree_sitter()
        else:
            logger.warning("Using fallback regex-based parser")
    
    def _init_tree_sitter(self):
        """Initialize tree-sitter parsers for supported languages"""
        try:
            import tree_sitter_python
            import tree_sitter_javascript
            import tree_sitter_typescript
            import tree_sitter_go
            
            # Initialize parsers for each language
            self.parsers['python'] = Parser(Language(tree_sitter_python.language()))
            self.parsers['javascript'] = Parser(Language(tree_sitter_javascript.language()))
            
            # TypeScript has tsx() and typescript() methods
            try:
                self.parsers['typescript'] = Parser(Language(tree_sitter_typescript.language_typescript()))
            except:
                pass  # Skip if not available
            
            self.parsers['go'] = Parser(Language(tree_sitter_go.language()))
            
            logger.info(f"Tree-sitter initialized for {len(self.parsers)} languages")
        except Exception as e:
            logger.error(f"Failed to initialize tree-sitter: {e}")
            self.parsers = {}
    
    def should_ignore(self, path: Path) -> bool:
        """Check if path should be ignored"""
        path_str = str(path)
        
        for pattern in IGNORE_PATTERNS:
            if pattern in path_str:
                return True
        
        return False
    
    def get_language(self, file_path: Path) -> Optional[str]:
        """Determine language from file extension"""
        suffix = file_path.suffix.lower()
        # Check code files first
        lang = SUPPORTED_EXTENSIONS.get(suffix)
        if lang:
            return lang
        # Check context/doc files
        return CONTEXT_EXTENSIONS.get(suffix)
    
    def is_context_file(self, file_path: Path) -> bool:
        """Check if file is a context/documentation file"""
        suffix = file_path.suffix.lower()
        return suffix in CONTEXT_EXTENSIONS
    
    def compute_file_hash(self, file_path: Path) -> str:
        """Compute MD5 hash of file content"""
        hasher = hashlib.md5()
        with open(file_path, 'rb') as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hasher.update(chunk)
        return hasher.hexdigest()
    
    def parse_file(self, file_path: Path) -> Dict[str, Any]:
        """
        Parse a file and extract code entities
        Returns structured data about the file
        """
        if not file_path.exists():
            return {"error": "File not found"}
        
        if self.should_ignore(file_path):
            return {"ignored": True}
        
        language = self.get_language(file_path)
        if not language:
            return {"error": "Unsupported language"}
        
        try:
            content = file_path.read_text(encoding='utf-8')
        except Exception as e:
            logger.error(f"Error reading {file_path}: {e}")
            return {"error": str(e)}
        
        # Get file metadata
        stat = file_path.stat()
        metadata = {
            "file_path": str(file_path),
            "language": language,
            "size_bytes": stat.st_size,
            "last_modified": stat.st_mtime,
            "content_hash": self.compute_file_hash(file_path),
            "line_count": len(content.split('\n'))
        }
        
        # Check if this is a context file (don't parse for functions)
        if self.is_context_file(file_path):
            # Store the whole file as context, don't extract entities
            metadata["entities"] = []
            metadata["is_context"] = True
            metadata["content_preview"] = content[:2000]  # First 2000 chars for context
            return metadata
        
        # Parse entities - use tree-sitter if available
        if self.parsers and language in self.parsers:
            entities = self._parse_with_tree_sitter(content, language)
        elif language == "python":
            entities = self._parse_python(content)
        elif language in ["javascript", "typescript"]:
            entities = self._parse_javascript(content)
        else:
            entities = []
        
        metadata["entities"] = entities
        metadata["is_context"] = False
        return metadata
    
    def _parse_with_tree_sitter(self, content: str, language: str) -> List[Dict[str, Any]]:
        """Parse code using tree-sitter"""
        entities = []
        
        try:
            parser = self.parsers.get(language)
            if not parser:
                return []
            
            tree = parser.parse(bytes(content, 'utf8'))
            root = tree.root_node
            
            # Query patterns based on language
            if language == 'python':
                function_types = ['function_definition']
                class_types = ['class_definition']
            elif language == 'go':
                function_types = ['function_declaration', 'method_declaration']
                class_types = ['type_declaration']  # Go uses types instead of classes
            elif language in ['javascript', 'typescript']:
                function_types = ['function_declaration', 'method_definition', 'arrow_function']
                class_types = ['class_declaration']
            else:
                return []
            
            # Walk the tree and extract entities
            def walk_tree(node):
                if node.type in function_types:
                    name_node = node.child_by_field_name('name')
                    if name_node:
                        # Extract full code snippet (up to 1000 chars for analysis)
                        code_snippet = content[node.start_byte:min(node.end_byte, node.start_byte + 1000)]
                        signature = content[node.start_byte:min(node.end_byte, node.start_byte + 200)]
                        
                        entities.append({
                            'type': 'function',
                            'name': content[name_node.start_byte:name_node.end_byte],
                            'start_line': node.start_point[0] + 1,
                            'end_line': node.end_point[0] + 1,
                            'signature': signature,
                            'code_snippet': code_snippet
                        })
                
                elif node.type in class_types:
                    name_node = node.child_by_field_name('name')
                    if name_node:
                        # Extract full code snippet
                        code_snippet = content[node.start_byte:min(node.end_byte, node.start_byte + 1000)]
                        signature = content[node.start_byte:min(node.end_byte, node.start_byte + 200)]
                        
                        entities.append({
                            'type': 'class',
                            'name': content[name_node.start_byte:name_node.end_byte],
                            'start_line': node.start_point[0] + 1,
                            'end_line': node.end_point[0] + 1,
                            'signature': signature,
                            'code_snippet': code_snippet
                        })
                
                for child in node.children:
                    walk_tree(child)
            
            walk_tree(root)
            
        except Exception as e:
            logger.error(f"Tree-sitter parsing error for {language}: {e}")
        
        return entities
    
    def _parse_python(self, content: str) -> List[Dict[str, Any]]:
        """Parse Python code (fallback regex-based)"""
        import re
        
        entities = []
        lines = content.split('\n')
        
        # Find functions (with optional type hints)
        func_pattern = r'^(\s*)def\s+(\w+)\s*\((.*?)\)\s*(->\s*\S+)?:'
        for i, line in enumerate(lines):
            match = re.match(func_pattern, line)
            if match:
                groups = match.groups()
                indent, name, params = groups[0], groups[1], groups[2]
                
                # Determine if it's a method (indented) or function
                entity_type = "method" if indent else "function"
                
                # Find end of function (next def/class at same or lower indentation level)
                end_line = len(lines)
                indent_len = len(indent)
                
                for j in range(i + 1, len(lines)):
                    line_stripped = lines[j].lstrip()
                    if not line_stripped:  # Empty line, continue
                        continue
                    
                    current_indent = len(lines[j]) - len(line_stripped)
                    
                    # If we find a def or class at same or lower indentation, that's the end
                    if current_indent <= indent_len:
                        if re.match(r'^(def|class)\s+', line_stripped):
                            end_line = j
                            break
                
                # Extract code snippet
                snippet_lines = lines[i:min(i+20, end_line)]
                snippet = '\n'.join(snippet_lines)
                
                entities.append({
                    "entity_type": entity_type,
                    "name": name,
                    "signature": f"def {name}({params})",
                    "start_line": i + 1,
                    "end_line": end_line,
                    "code_snippet": snippet
                })
        
        # Find classes
        class_pattern = r'^class\s+(\w+)(\(.*?\))?:'
        for i, line in enumerate(lines):
            match = re.match(class_pattern, line)
            if match:
                name = match.group(1)
                
                # Find end of class
                end_line = i + 1
                for j in range(i + 1, len(lines)):
                    if lines[j].strip() and not lines[j].startswith(' ') and not lines[j].startswith('\t'):
                        if re.match(r'^class\s+', lines[j]):
                            end_line = j
                            break
                else:
                    end_line = len(lines)
                
                snippet_lines = lines[i:min(i+20, end_line)]
                snippet = '\n'.join(snippet_lines)
                
                entities.append({
                    "entity_type": "class",
                    "name": name,
                    "signature": line.strip(),
                    "start_line": i + 1,
                    "end_line": end_line,
                    "code_snippet": snippet
                })
        
        return entities
    
    def _parse_javascript(self, content: str) -> List[Dict[str, Any]]:
        """Parse JavaScript/TypeScript code (fallback regex-based)"""
        import re
        
        entities = []
        lines = content.split('\n')
        
        # Find functions (function declarations and arrow functions)
        patterns = [
            r'^(\s*)function\s+(\w+)\s*\((.*?)\)',
            r'^(\s*)const\s+(\w+)\s*=\s*\((.*?)\)\s*=>',
            r'^(\s*)(\w+)\s*:\s*function\s*\((.*?)\)',
        ]
        
        for i, line in enumerate(lines):
            for pattern in patterns:
                match = re.match(pattern, line)
                if match:
                    groups = match.groups()
                    indent = groups[0] if len(groups) > 0 else ""
                    name = groups[1] if len(groups) > 1 else "anonymous"
                    params = groups[2] if len(groups) > 2 else ""
                    
                    # Find end (look for closing brace)
                    end_line = i + 1
                    brace_count = line.count('{') - line.count('}')
                    for j in range(i + 1, len(lines)):
                        brace_count += lines[j].count('{') - lines[j].count('}')
                        if brace_count <= 0:
                            end_line = j + 1
                            break
                    
                    snippet_lines = lines[i:min(i+20, end_line)]
                    snippet = '\n'.join(snippet_lines)
                    
                    entities.append({
                        "entity_type": "function",
                        "name": name,
                        "signature": line.strip()[:100],
                        "start_line": i + 1,
                        "end_line": end_line,
                        "code_snippet": snippet
                    })
                    break
        
        # Find classes
        class_pattern = r'^(\s*)class\s+(\w+)'
        for i, line in enumerate(lines):
            match = re.match(class_pattern, line)
            if match:
                name = match.group(2)
                
                # Find end
                end_line = i + 1
                brace_count = line.count('{') - line.count('}')
                for j in range(i + 1, len(lines)):
                    brace_count += lines[j].count('{') - lines[j].count('}')
                    if brace_count <= 0:
                        end_line = j + 1
                        break
                
                snippet_lines = lines[i:min(i+20, end_line)]
                snippet = '\n'.join(snippet_lines)
                
                entities.append({
                    "entity_type": "class",
                    "name": name,
                    "signature": line.strip(),
                    "start_line": i + 1,
                    "end_line": end_line,
                    "code_snippet": snippet
                })
        
        return entities
    
    def parse_directory(self, directory: Path, recursive: bool = True) -> List[Dict[str, Any]]:
        """
        Parse all supported files in a directory
        """
        results = []
        
        if not directory.exists() or not directory.is_dir():
            logger.error(f"Directory not found: {directory}")
            return results
        
        # Collect all files
        if recursive:
            files = list(directory.rglob('*'))
        else:
            files = list(directory.glob('*'))
        
        # Filter to supported files (code + context files)
        all_extensions = {**SUPPORTED_EXTENSIONS, **CONTEXT_EXTENSIONS}
        supported_files = [
            f for f in files
            if f.is_file() and f.suffix.lower() in all_extensions
            and not self.should_ignore(f)
        ]
        
        logger.info(f"Found {len(supported_files)} files to parse in {directory}")
        
        for file_path in supported_files:
            try:
                result = self.parse_file(file_path)
                if "error" not in result and not result.get("ignored"):
                    results.append(result)
            except Exception as e:
                logger.error(f"Error parsing {file_path}: {e}")
        
        return results


if __name__ == "__main__":
    # Test the parser
    parser = CodeParser()
    
    # Test on current file
    current_file = Path(__file__)
    result = parser.parse_file(current_file)
    
    print(f"Parsed {current_file.name}:")
    print(f"Language: {result.get('language')}")
    print(f"Entities found: {len(result.get('entities', []))}")
    
    for entity in result.get('entities', [])[:3]:
        print(f"  - {entity['entity_type']}: {entity['name']} (line {entity['start_line']})")

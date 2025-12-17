"""Code review tools for static analysis and quality checks."""
import os
import re
from pathlib import Path
from typing import Dict, List, Any


class CodeReviewer:
    """Analyzes code for bugs, security issues, and quality."""
    
    def __init__(self):
        self.security_patterns = [
            (r'eval\(', 'Dangerous eval() usage detected'),
            (r'exec\(', 'Dangerous exec() usage detected'),
            (r'__import__\(', 'Dynamic import detected'),
            (r'pickle\.loads?\(', 'Unsafe pickle usage'),
            (r'os\.system\(', 'Shell command execution'),
            (r'subprocess\.call\(.*shell=True', 'Shell injection risk'),
            (r'password\s*=\s*["\'].*["\']', 'Hardcoded password'),
            (r'api[_-]?key\s*=\s*["\'].*["\']', 'Hardcoded API key'),
        ]
        
        self.bug_patterns = [
            (r'except\s*:', 'Bare except clause - catches all exceptions'),
            (r'== None', 'Use "is None" instead of "== None"'),
            (r'!= None', 'Use "is not None" instead of "!= None"'),
            (r'from .* import \*', 'Wildcard import - bad practice'),
        ]
    
    def review_file(self, file_path: str) -> Dict[str, Any]:
        """Review a single code file."""
        if not os.path.exists(file_path):
            return {"error": f"File not found: {file_path}"}
        
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
        
        return {
            "file": file_path,
            "security_issues": self._check_security(content),
            "bug_risks": self._check_bugs(content),
            "code_smells": self._check_smells(content),
            "stats": self._get_stats(content)
        }
    
    def _check_security(self, content: str) -> List[Dict[str, Any]]:
        """Check for security vulnerabilities."""
        issues = []
        lines = content.split('\n')
        
        for pattern, message in self.security_patterns:
            for i, line in enumerate(lines, 1):
                if re.search(pattern, line):
                    issues.append({
                        "line": i,
                        "issue": message,
                        "code": line.strip(),
                        "severity": "HIGH"
                    })
        
        return issues
    
    def _check_bugs(self, content: str) -> List[Dict[str, Any]]:
        """Check for common bug patterns."""
        issues = []
        lines = content.split('\n')
        
        for pattern, message in self.bug_patterns:
            for i, line in enumerate(lines, 1):
                if re.search(pattern, line):
                    issues.append({
                        "line": i,
                        "issue": message,
                        "code": line.strip(),
                        "severity": "MEDIUM"
                    })
        
        return issues
    
    def _check_smells(self, content: str) -> List[str]:
        """Check for code smells."""
        smells = []
        lines = content.split('\n')
        
        # Long functions
        in_function = False
        function_lines = 0
        
        for line in lines:
            if re.match(r'\s*def ', line):
                in_function = True
                function_lines = 0
            elif in_function:
                function_lines += 1
                if function_lines > 50:
                    smells.append("Function longer than 50 lines detected")
                    in_function = False
        
        # Long lines
        long_lines = [i+1 for i, line in enumerate(lines) if len(line) > 120]
        if long_lines:
            smells.append(f"Lines longer than 120 chars: {len(long_lines)}")
        
        return smells
    
    def _get_stats(self, content: str) -> Dict[str, int]:
        """Get basic code statistics."""
        lines = content.split('\n')
        return {
            "total_lines": len(lines),
            "code_lines": len([l for l in lines if l.strip() and not l.strip().startswith('#')]),
            "comment_lines": len([l for l in lines if l.strip().startswith('#')]),
            "blank_lines": len([l for l in lines if not l.strip()])
        }

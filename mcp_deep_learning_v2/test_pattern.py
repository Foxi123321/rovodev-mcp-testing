import re

# Test different patterns
patterns = [
    r'^(\s*)def\s+(\w+)\s*\((.*?)\):',  # Original
    r'^(\s*)def\s+(\w+)\s*\((.*?)\)\s*(->\s*\S+)?:',  # My attempt
    r'^(\s*)def\s+(\w+)\s*\((.*?)\)\s*(->\s*.+?)?:',  # Better?
    r'^(\s*)def\s+(\w+)\s*\(.*?\).*?:',  # Simplified
]

test_lines = [
    "def hash_password(password: str) -> str:",
    "def check_rate_limit(username: str) -> bool:",
    "def login(username: str, password: str) -> dict:",
    "def logout(session_id: str):",
    "def record_failed_attempt(username: str):",
    "    def __init__(self):",
]

for i, pattern in enumerate(patterns, 1):
    print(f"\n=== Pattern {i}: {pattern} ===")
    for line in test_lines:
        match = re.match(pattern, line)
        if match:
            print(f"  ✓ {line[:40]}")
        else:
            print(f"  ✗ {line[:40]}")

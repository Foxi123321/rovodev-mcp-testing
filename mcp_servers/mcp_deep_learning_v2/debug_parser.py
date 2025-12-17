import re

content = open(r'C:\Users\ggfuc\.rovodev\mcp_deep_learning_v2\TEST\auth.py').read()
lines = content.split('\n')

func_pattern = r'^(\s*)def\s+(\w+)\s*\((.*?)\):'

print("Testing regex pattern on each line:\n")

for i, line in enumerate(lines[:80], 1):
    match = re.match(func_pattern, line)
    if match:
        indent, name, params = match.groups()
        print(f"Line {i}: Found '{name}' with indent '{indent}' (len={len(indent)})")
    elif 'def ' in line:
        print(f"Line {i}: Contains 'def' but didn't match: {line[:60]}")

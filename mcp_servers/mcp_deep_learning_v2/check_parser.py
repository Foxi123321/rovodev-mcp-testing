from code_parser import CodeParser
from pathlib import Path

p = CodeParser()
result = p.parse_file(Path(r'C:\Users\ggfuc\.rovodev\mcp_deep_learning_v2\TEST\auth.py'))

print(f"Parsed auth.py - found {len(result['entities'])} entities\n")

for e in result['entities']:
    print(f"{e['entity_type']}: {e['name']} (line {e['start_line']})")

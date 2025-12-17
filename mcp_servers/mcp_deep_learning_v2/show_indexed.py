from database_manager import DatabaseManager

db = DatabaseManager()
entities = db.search_entities()

print(f"Total entities: {len(entities)}\n")

print("Functions:")
for e in entities:
    if e['entity_type'] == 'function':
        fname = e['file_path'].split('\\')[-1]
        print(f"  - {e['name']} (in {fname}, line {e['start_line']})")

print("\nClasses:")
for e in entities:
    if e['entity_type'] == 'class':
        fname = e['file_path'].split('\\')[-1]
        print(f"  - {e['name']} (in {fname}, line {e['start_line']})")

print("\nMethods:")
for e in entities:
    if e['entity_type'] == 'method':
        fname = e['file_path'].split('\\')[-1]
        print(f"  - {e['name']} (in {fname}, line {e['start_line']})")

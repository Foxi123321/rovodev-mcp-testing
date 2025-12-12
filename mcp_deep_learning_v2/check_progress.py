from database_manager import DatabaseManager

db = DatabaseManager()
stats = db.get_stats()

print(f"Analysis Progress:")
print(f"  Files indexed: {stats['files']}")
print(f"  Code entities: {stats['entities']}")
print(f"  Analyses completed: {stats['analyses']}")
print(f"  Progress: {stats['analyses']}/{stats['entities']} ({stats['analyses']/stats['entities']*100:.1f}%)")

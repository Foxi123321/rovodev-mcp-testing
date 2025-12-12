from database_manager import DatabaseManager

db = DatabaseManager()

# Get all analyses
conn = db.conn
cursor = conn.cursor()

cursor.execute("""
    SELECT e.name, e.entity_type, f.file_path, a.consensus_summary, a.consensus_confidence, a.agreement_score
    FROM analysis_results a
    JOIN code_entities e ON a.entity_id = e.id
    JOIN files f ON e.file_id = f.id
    ORDER BY a.created_at DESC
""")

rows = cursor.fetchall()

print(f"Completed Analyses: {len(rows)}\n")

for row in rows:
    name, etype, fpath, summary, confidence, agreement = row
    fname = fpath.split('\\')[-1]
    
    print("=" * 80)
    print(f"{etype}: {name} (in {fname})")
    print("=" * 80)
    print(f"Confidence: {confidence:.0%} | Agreement: {agreement:.0%}")
    print(f"\n{summary[:500]}")
    print("...\n")

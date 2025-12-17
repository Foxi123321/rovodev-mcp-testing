from database_manager import DatabaseManager

db = DatabaseManager()

# Get login function
entities = db.search_entities(name="login", file_path="auth.py")

if entities:
    entity = entities[0]
    print(f"Found: {entity['name']} in {entity['file_path']}")
    
    # Get analysis
    analysis = db.get_entity_analysis(entity['id'])
    
    if analysis:
        print("\n" + "=" * 80)
        print("ANALYSIS RESULT:")
        print("=" * 80)
        print(f"\n{analysis['consensus_summary']}")
        print(f"\nConfidence: {analysis['consensus_confidence']:.0%}")
        print(f"Agreement: {analysis['agreement_score']:.0%}")
        print(f"Needs Review: {analysis['needs_review']}")
    else:
        print("\nNo analysis found yet - still processing")
else:
    print("Function not found")

"""Test script for AI Database Curator"""
import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from mcp_knowledge_db.database import KnowledgeDatabase
from mcp_knowledge_db.curator import AIDatabaseCurator
from mcp_knowledge_db.models import CodeFile, CodeKnowledge, CommandPattern, ErrorSolution


async def setup_test_data(db: KnowledgeDatabase):
    """Setup some test data for curator to work with"""
    print("📝 Setting up test data...")
    
    # Add some code entries
    file_id = db.store_code_file(CodeFile(
        file_path="test/auth.py",
        project_name="TestApp",
        language="python"
    ))
    
    db.store_code_knowledge(CodeKnowledge(
        file_id=file_id,
        symbol_name="authenticate_user",
        symbol_type="function",
        purpose="Validates user credentials and returns JWT token"
    ))
    
    # Add some duplicate-like entries (for testing)
    db.store_code_knowledge(CodeKnowledge(
        file_id=file_id,
        symbol_name="authenticate_user",
        symbol_type="function",
        purpose="Authenticates user with username and password"
    ))
    
    # Add command patterns
    for i in range(5):
        db.store_command_pattern(CommandPattern(
            command="gradle build",
            duration_ms=180000 + (i * 5000),
            success=True,
            cpu_avg=65.0 + i
        ))
    
    # Add a slow command
    db.store_command_pattern(CommandPattern(
        command="gradle build",
        duration_ms=450000,  # Way too long!
        success=True,
        cpu_avg=45.0
    ))
    
    # Add error solutions
    db.store_error_solution(ErrorSolution(
        error_pattern="ModuleNotFoundError: No module named 'requests'",
        solution="Run: pip install requests",
        error_type="import",
        success_count=5,
        failure_count=1
    ))
    
    print("✅ Test data created")


async def test_database_health(curator: AIDatabaseCurator):
    """Test database health check"""
    print("\n🏥 Testing database health check...")
    
    health = await curator.get_database_health()
    
    print(f"✅ Health Score: {health['health_score']}/100")
    print(f"   Status: {health['status']}")
    print(f"   Code entries: {health['total_code_entries']}")
    print(f"   Commands: {health['total_commands']}")
    print(f"   Reliable solutions: {health['reliable_solutions']}")


async def test_anomaly_detection(curator: AIDatabaseCurator):
    """Test anomaly detection"""
    print("\n🔍 Testing anomaly detection...")
    
    result = await curator.detect_anomalies()
    
    print(f"✅ Anomalies found: {result['anomalies_found']}")
    if result['anomalies']:
        for anomaly in result['anomalies']:
            print(f"   - {anomaly['type']}: {anomaly['count']} instances (severity: {anomaly['severity']})")
    
    if result.get('ai_analysis'):
        print(f"   AI Analysis: {result['ai_analysis']}")


async def test_insights_generation(curator: AIDatabaseCurator):
    """Test AI insights generation"""
    print("\n💡 Testing AI insights generation...")
    
    result = await curator.generate_insights()
    
    print(f"✅ Insights generated")
    print(f"   Statistics: {result['statistics']}")
    if result.get('insights'):
        print(f"   AI Insights: {result['insights']}")


async def test_full_curation(curator: AIDatabaseCurator):
    """Test full curation cycle"""
    print("\n🤖 Testing full AI curation cycle...")
    print("   (This will take a minute - AI is analyzing everything)")
    
    result = await curator.run_full_curation()
    
    print(f"✅ Curation completed")
    print(f"   Started: {result['started_at']}")
    print(f"   Completed: {result['completed_at']}")
    print(f"   Status: {result['status']}")
    
    print("\n📊 Task Results:")
    for task_name, task_result in result['tasks'].items():
        print(f"   {task_name}:")
        if isinstance(task_result, dict):
            for key, value in task_result.items():
                if key != 'details':  # Skip details for brevity
                    print(f"      {key}: {value}")


async def main():
    """Run all curator tests"""
    print("=" * 60)
    print("AI DATABASE CURATOR - TEST SUITE")
    print("Using Gemma 2 9B for intelligent database management")
    print("=" * 60)
    
    # Check if Gemma 2 9B is available
    try:
        import requests
        response = requests.get("http://localhost:11434/api/tags", timeout=5)
        models = [m['name'] for m in response.json().get('models', [])]
        if 'gemma2:9b' not in models:
            print("\n⚠️  WARNING: gemma2:9b model not found in Ollama")
            print("   Run: ollama pull gemma2:9b")
            print("   Continuing anyway (some tests may fail)...\n")
    except:
        print("\n⚠️  WARNING: Cannot connect to Ollama")
        print("   Make sure Ollama is running")
        print("   Continuing anyway (AI features will fail)...\n")
    
    try:
        # Initialize
        db = KnowledgeDatabase()
        curator = AIDatabaseCurator(db)
        
        # Setup test data
        await setup_test_data(db)
        
        # Run tests
        await test_database_health(curator)
        await test_anomaly_detection(curator)
        await test_insights_generation(curator)
        
        # Ask user before running full curation (it's slow)
        print("\n" + "=" * 60)
        print("Ready to run FULL CURATION (takes 1-2 minutes)")
        response = input("Continue? (y/n): ").strip().lower()
        
        if response == 'y':
            await test_full_curation(curator)
        else:
            print("Skipped full curation test")
        
        print("\n" + "=" * 60)
        print("✅ AI CURATOR TESTS COMPLETED!")
        print("=" * 60)
        print("\nThe AI Database Curator is ready to manage your database! 🤖🔥")
        
        db.close()
        
    except Exception as e:
        print(f"\n❌ TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())

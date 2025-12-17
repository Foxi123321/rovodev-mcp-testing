"""Test script for Knowledge Database MCP Server"""
import asyncio
import json
from pathlib import Path
import sys

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from mcp_knowledge_db.database import KnowledgeDatabase
from mcp_knowledge_db.search import KnowledgeSearchEngine
from mcp_knowledge_db.models import (
    CodeFile, CodeKnowledge, CommandPattern, 
    ErrorSolution, SystemMetric
)


def test_database_init():
    """Test database initialization"""
    print("🔧 Testing database initialization...")
    db = KnowledgeDatabase()
    assert db.connection is not None
    print("✅ Database initialized successfully")
    db.close()


def test_code_storage():
    """Test code intelligence storage and retrieval"""
    print("\n📝 Testing code storage...")
    db = KnowledgeDatabase()
    
    # Store a code file
    code_file = CodeFile(
        file_path="test/auth.py",
        project_name="TestProject",
        language="python",
        size_bytes=1024
    )
    file_id = db.store_code_file(code_file)
    print(f"✅ Stored code file with ID: {file_id}")
    
    # Store code knowledge
    knowledge = CodeKnowledge(
        file_id=file_id,
        symbol_name="authenticate_user",
        symbol_type="function",
        line_start=10,
        line_end=25,
        purpose="Validates user credentials and returns JWT token",
        complexity="moderate",
        docstring="Authenticates user with username and password"
    )
    knowledge_id = db.store_code_knowledge(knowledge)
    print(f"✅ Stored code knowledge with ID: {knowledge_id}")
    
    # Query code knowledge
    results = db.query_code_knowledge("authenticate")
    print(f"✅ Query returned {len(results)} result(s)")
    if results:
        print(f"   Found: {results[0]['symbol_name']} - {results[0]['purpose']}")
    
    db.close()


def test_command_patterns():
    """Test command execution pattern storage"""
    print("\n⚡ Testing command patterns...")
    db = KnowledgeDatabase()
    
    # Store multiple command executions
    commands = [
        CommandPattern(
            command="gradle build",
            command_type="build",
            duration_ms=180000,
            success=True,
            exit_code=0,
            cpu_avg=65.5,
            memory_peak_mb=512
        ),
        CommandPattern(
            command="gradle build",
            command_type="build",
            duration_ms=175000,
            success=True,
            exit_code=0,
            cpu_avg=68.2,
            memory_peak_mb=498
        ),
        CommandPattern(
            command="gradle build",
            command_type="build",
            duration_ms=182000,
            success=True,
            exit_code=0,
            cpu_avg=62.8,
            memory_peak_mb=520
        )
    ]
    
    for cmd in commands:
        db.store_command_pattern(cmd)
    print(f"✅ Stored {len(commands)} command executions")
    
    # Get baseline
    baseline = db.get_command_baseline("gradle build")
    if baseline:
        print(f"✅ Baseline calculated:")
        print(f"   Average duration: {baseline['avg_duration_ms']}ms")
        print(f"   Sample count: {baseline['sample_count']}")
        print(f"   Success rate: {baseline['success_rate'] * 100:.1f}%")
        print(f"   Confidence: {baseline['confidence']:.2f}")
    
    db.close()


def test_error_solutions():
    """Test error solution storage and retrieval"""
    print("\n🔍 Testing error solutions...")
    db = KnowledgeDatabase()
    
    # Store error solutions
    solution = ErrorSolution(
        error_pattern="ModuleNotFoundError: No module named 'requests'",
        error_type="import",
        solution="Run: pip install requests",
        context="Python dependency missing",
        source="manual",
        success_count=1,
        confidence=1.0
    )
    solution_id = db.store_error_solution(solution)
    print(f"✅ Stored error solution with ID: {solution_id}")
    
    # Query error solution
    solutions = db.get_error_solution("ModuleNotFoundError")
    print(f"✅ Query returned {len(solutions)} solution(s)")
    if solutions:
        print(f"   Solution: {solutions[0]['solution']}")
        print(f"   Confidence: {solutions[0]['confidence']}")
    
    db.close()


def test_system_metrics():
    """Test system metrics storage"""
    print("\n📊 Testing system metrics...")
    db = KnowledgeDatabase()
    
    # Store some system metrics
    metrics = [
        SystemMetric(metric_name="cpu_usage", metric_value=45.5, unit="%", category="cpu"),
        SystemMetric(metric_name="memory_usage", metric_value=8192, unit="MB", category="memory"),
        SystemMetric(metric_name="disk_io_read", metric_value=150.5, unit="MB/s", category="disk"),
    ]
    
    for metric in metrics:
        db.store_system_metric(metric)
    print(f"✅ Stored {len(metrics)} system metrics")
    
    # Get baseline
    baseline = db.get_system_baseline()
    print(f"✅ System baseline retrieved:")
    for category, metrics in baseline.items():
        print(f"   {category}:")
        for metric_name, values in metrics.items():
            print(f"      {metric_name}: avg={values['avg']:.1f} {values['unit']}")
    
    db.close()


def test_search_engine():
    """Test search engine"""
    print("\n🔎 Testing search engine...")
    db = KnowledgeDatabase()
    search = KnowledgeSearchEngine(db)
    
    # General search
    results = search.search("gradle", limit=10)
    total = sum(len(v) for v in results.values())
    print(f"✅ Search returned {total} total result(s)")
    
    for category, items in results.items():
        if items:
            print(f"   {category}: {len(items)} result(s)")
    
    db.close()


def test_full_workflow():
    """Test a complete workflow"""
    print("\n🎯 Testing complete workflow...")
    db = KnowledgeDatabase()
    
    print("1. Store code analysis...")
    file_id = db.store_code_file(CodeFile(
        file_path="src/utils.py",
        project_name="MyApp",
        language="python"
    ))
    
    db.store_code_knowledge(CodeKnowledge(
        file_id=file_id,
        symbol_name="calculate_hash",
        symbol_type="function",
        purpose="Calculates SHA256 hash of input data"
    ))
    
    print("2. Store command execution...")
    db.store_command_pattern(CommandPattern(
        command="npm install",
        duration_ms=12500,
        success=True,
        cpu_avg=35.5
    ))
    
    print("3. Store error solution...")
    db.store_error_solution(ErrorSolution(
        error_pattern="ENOENT: no such file or directory",
        solution="Ensure the file path exists before accessing",
        error_type="filesystem"
    ))
    
    print("4. Search across all types...")
    search = KnowledgeSearchEngine(db)
    results = search.search("hash", limit=5)
    
    print(f"✅ Complete workflow successful!")
    print(f"   Found results in {len([k for k, v in results.items() if v])} categories")
    
    db.close()


def main():
    """Run all tests"""
    print("=" * 60)
    print("KNOWLEDGE DATABASE MCP - TEST SUITE")
    print("=" * 60)
    
    try:
        test_database_init()
        test_code_storage()
        test_command_patterns()
        test_error_solutions()
        test_system_metrics()
        test_search_engine()
        test_full_workflow()
        
        print("\n" + "=" * 60)
        print("✅ ALL TESTS PASSED!")
        print("=" * 60)
        print("\nThe Knowledge Database MCP is ready to rock! 🔥")
        print(f"Database location: {Path.home() / '.rovodev' / 'knowledge_db' / 'knowledge.db'}")
        
    except Exception as e:
        print(f"\n❌ TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()

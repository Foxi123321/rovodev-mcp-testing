"""Quick test of full AI curation"""
import asyncio
from database import KnowledgeDatabase
from curator import AIDatabaseCurator

async def main():
    print('🚀 Running FULL AI Curation Cycle...')
    print('(This will take 1-2 minutes - Gemma is analyzing everything)\n')
    
    db = KnowledgeDatabase()
    curator = AIDatabaseCurator(db)
    
    result = await curator.run_full_curation()
    
    print('\n' + '='*60)
    print('✅ FULL CURATION COMPLETED!')
    print('='*60)
    print('Started:', result['started_at'])
    print('Completed:', result['completed_at'])
    print('Status:', result['status'])
    print('\nTask Results:')
    for task, data in result['tasks'].items():
        print(f'  {task}: {str(data)[:200]}...')
    
    db.close()
    print('\n🎉 AI Database Curator is FULLY OPERATIONAL!')

if __name__ == "__main__":
    asyncio.run(main())

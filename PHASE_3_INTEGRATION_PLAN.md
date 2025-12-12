# Phase 3: Integration Layer - Detailed Plan

**Status**: 🚧 Starting Now
**Goal**: Connect all MCP servers to share knowledge via Knowledge Database

---

## 🎯 Integration Task 1: Deep Learning ↔ Knowledge DB (HIGH PRIORITY)

### Current State
- Deep Learning MCP: Analyzes code, indexes files, extracts patterns
- Knowledge DB: Has generic storage but no code-specific integration

### What to Build

#### 1. Add Code Analysis Tables to Knowledge DB
```sql
CREATE TABLE code_analysis_cache (
    id INTEGER PRIMARY KEY,
    file_path TEXT NOT NULL,
    file_hash TEXT NOT NULL,
    analysis_type TEXT, -- 'function', 'class', 'module'
    content TEXT,       -- JSON with analysis results
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(file_path, file_hash, analysis_type)
);

CREATE TABLE code_relationships (
    id INTEGER PRIMARY KEY,
    source_file TEXT,
    target_file TEXT,
    relationship_type TEXT, -- 'imports', 'calls', 'extends'
    confidence REAL,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE code_patterns (
    id INTEGER PRIMARY KEY,
    pattern_type TEXT,  -- 'design_pattern', 'anti_pattern', 'idiom'
    description TEXT,
    code_example TEXT,
    frequency INTEGER,
    projects TEXT       -- JSON array of projects using this
);
```

#### 2. Add Methods to Knowledge DB Interface
```python
# In knowledge_db_interface.py

def store_code_analysis(file_path, file_hash, analysis_type, content):
    """Store code analysis results"""
    
def get_code_analysis(file_path, file_hash=None):
    """Get cached analysis for a file"""
    
def store_code_relationship(source, target, rel_type, confidence):
    """Store code dependencies/relationships"""
    
def query_code_relationships(file_path):
    """Get all relationships for a file"""
    
def store_code_pattern(pattern_type, description, example):
    """Store discovered code patterns"""
    
def search_code(query):
    """Search code analysis with semantic search"""
```

#### 3. Modify Deep Learning MCP to Use Knowledge DB
```python
# In mcp_deep_learning_v2/server.py

from knowledge_db_interface import KnowledgeDBInterface

knowledge_db = KnowledgeDBInterface()

# Before analyzing, check cache
cached = knowledge_db.get_code_analysis(file_path, file_hash)
if cached and not force_refresh:
    return cached

# After analyzing, store results
knowledge_db.store_code_analysis(
    file_path=file_path,
    file_hash=file_hash,
    analysis_type='full',
    content=analysis_results
)
```

#### 4. Add New MCP Tools
- `query_cached_analysis(file_path)` - Check if already analyzed
- `store_analysis_result(data)` - Save analysis to shared DB
- `find_similar_code(query)` - Semantic search across all analyzed code

### Benefits
✅ Avoid re-analyzing same files
✅ Share knowledge across sessions
✅ Build up code intelligence over time
✅ Fast lookups (< 100ms)

### Implementation Steps
1. Add tables to Knowledge DB schema ✅
2. Add methods to knowledge_db_interface.py ✅
3. Test new methods ✅
4. Integrate with Deep Learning MCP ✅
5. Add new MCP tools ✅
6. Test end-to-end ✅

**Estimated Time**: 30-45 minutes

---

## 🎯 Integration Task 2: Browser ↔ Knowledge DB (MEDIUM PRIORITY)

### Current State
- Browser MCP: Can search web, scrape pages, extract data
- Knowledge DB: No web research caching

### What to Build

#### 1. Add Web Research Tables
```sql
CREATE TABLE web_research_cache (
    id INTEGER PRIMARY KEY,
    query TEXT NOT NULL,
    url TEXT,
    title TEXT,
    content TEXT,
    relevance_score REAL,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE solutions (
    id INTEGER PRIMARY KEY,
    problem TEXT NOT NULL,      -- Error message or issue
    solution TEXT,               -- What worked
    source_url TEXT,             -- Where we found it
    success_rating INTEGER,      -- How well it worked (1-5)
    times_used INTEGER DEFAULT 1,
    last_used DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE stackoverflow_cache (
    id INTEGER PRIMARY KEY,
    question_id TEXT UNIQUE,
    question_title TEXT,
    question_body TEXT,
    accepted_answer TEXT,
    votes INTEGER,
    cached_date DATETIME DEFAULT CURRENT_TIMESTAMP
);
```

#### 2. Add Methods to Knowledge DB Interface
```python
def cache_web_search(query, url, content, relevance):
    """Cache web search results"""
    
def get_cached_search(query):
    """Get cached search results"""
    
def store_solution(problem, solution, source_url, success_rating):
    """Store a working solution"""
    
def find_solution(problem):
    """Search for similar solved problems"""
    
def cache_stackoverflow(question_id, title, body, answer, votes):
    """Cache Stack Overflow Q&A"""
    
def search_stackoverflow_cache(query):
    """Search cached Stack Overflow"""
```

#### 3. Modify Browser MCP
```python
# Before searching web, check cache
cached = knowledge_db.get_cached_search(query)
if cached and is_recent(cached):
    return cached

# After finding solution, store it
knowledge_db.store_solution(
    problem=error_message,
    solution=found_fix,
    source_url=url,
    success_rating=5
)
```

### Benefits
✅ Avoid redundant web searches
✅ Remember what worked
✅ Build solution library
✅ Offline access to past research

**Estimated Time**: 30 minutes

---

## 🎯 Integration Task 3: Enhanced Sandbox Monitor Integration

### Current State
✅ Already stores AI decisions
✅ Already searches past decisions

### What to Add

#### 1. Store Process Execution Patterns
```python
def store_process_execution(command, duration, cpu_avg, memory_avg, exit_code):
    """Store execution metrics for learning"""
    
def get_process_baseline(command):
    """Get expected behavior for this command"""
```

#### 2. Cross-Reference with Web Research
```python
# When process is stuck, check if solution is known
if process_stuck:
    solution = knowledge_db.find_solution(f"stuck process {process_name}")
    if solution:
        apply_solution(solution)
    else:
        web_search_for_solution()
```

**Estimated Time**: 15 minutes

---

## 📊 Integration Architecture

```
┌─────────────────────────────────────────┐
│     KNOWLEDGE DATABASE (THE HUB)        │
│  ┌─────────────────────────────────┐   │
│  │ Code Analysis Cache             │   │
│  │ Web Research Cache              │   │
│  │ Solutions Library               │   │
│  │ Process Execution Patterns      │   │
│  └─────────────────────────────────┘   │
└─────────────────────────────────────────┘
         ↑           ↑           ↑
         │           │           │
    ┌────┴────┐ ┌───┴────┐ ┌───┴────────┐
    │  Deep   │ │Browser │ │  Sandbox   │
    │Learning │ │  MCP   │ │  Monitor   │
    │   MCP   │ │        │ │    MCP     │
    └─────────┘ └────────┘ └────────────┘
         │           │           │
         └───────────┴───────────┘
                   │
           ┌───────┴────────┐
           │   REX / USER   │
           └────────────────┘
```

---

## 🚀 Implementation Order

### Phase 3.1: Deep Learning Integration (START HERE)
1. Add code analysis tables to Knowledge DB
2. Add storage/retrieval methods
3. Integrate with Deep Learning MCP
4. Test with real code analysis

### Phase 3.2: Browser Integration
1. Add web research tables
2. Add caching methods
3. Integrate with Browser MCP
4. Test with real searches

### Phase 3.3: Enhanced Sandbox Integration
1. Add process baseline tracking
2. Cross-reference with solutions
3. Test with stuck process scenarios

---

## ✅ Success Criteria

**Integration is successful when**:
- ✅ Deep Learning doesn't re-analyze same files
- ✅ Browser returns cached results instantly
- ✅ Sandbox Monitor learns from past executions
- ✅ All systems share knowledge seamlessly
- ✅ Rex gets smarter over time
- ✅ Token usage decreases (cached results)

---

## 🎯 Let's Start with Phase 3.1!

Ready to build the Deep Learning ↔ Knowledge DB integration?

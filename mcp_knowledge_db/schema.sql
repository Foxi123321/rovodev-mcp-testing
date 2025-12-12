-- Knowledge Database Schema
-- The Heart of the MCP Ecosystem

-- ============================================================================
-- CODE INTELLIGENCE
-- ============================================================================

-- Code files metadata
CREATE TABLE IF NOT EXISTS code_files (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    file_path TEXT UNIQUE NOT NULL,
    project_name TEXT,
    language TEXT,
    size_bytes INTEGER,
    last_indexed DATETIME DEFAULT CURRENT_TIMESTAMP,
    checksum TEXT,  -- To detect changes
    UNIQUE(file_path)
);

CREATE INDEX IF NOT EXISTS idx_code_files_project ON code_files(project_name);
CREATE INDEX IF NOT EXISTS idx_code_files_language ON code_files(language);

-- Code knowledge - functions, classes, methods
CREATE TABLE IF NOT EXISTS code_knowledge (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    file_id INTEGER NOT NULL,
    symbol_name TEXT NOT NULL,
    symbol_type TEXT NOT NULL,  -- function, class, method, variable
    line_start INTEGER,
    line_end INTEGER,
    purpose TEXT,  -- AI-analyzed purpose
    complexity TEXT,  -- simple, moderate, complex
    parameters TEXT,  -- JSON array
    return_type TEXT,
    docstring TEXT,
    code_snippet TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (file_id) REFERENCES code_files(id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_code_knowledge_symbol ON code_knowledge(symbol_name);
CREATE INDEX IF NOT EXISTS idx_code_knowledge_type ON code_knowledge(symbol_type);
CREATE INDEX IF NOT EXISTS idx_code_knowledge_file ON code_knowledge(file_id);

-- Code dependencies
CREATE TABLE IF NOT EXISTS code_dependencies (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    from_symbol_id INTEGER NOT NULL,
    to_symbol_id INTEGER NOT NULL,
    dependency_type TEXT NOT NULL,  -- calls, imports, inherits, uses
    confidence REAL DEFAULT 1.0,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (from_symbol_id) REFERENCES code_knowledge(id) ON DELETE CASCADE,
    FOREIGN KEY (to_symbol_id) REFERENCES code_knowledge(id) ON DELETE CASCADE,
    UNIQUE(from_symbol_id, to_symbol_id, dependency_type)
);

CREATE INDEX IF NOT EXISTS idx_deps_from ON code_dependencies(from_symbol_id);
CREATE INDEX IF NOT EXISTS idx_deps_to ON code_dependencies(to_symbol_id);

-- Full-text search for code
CREATE VIRTUAL TABLE IF NOT EXISTS code_fts USING fts5(
    symbol_name,
    purpose,
    docstring,
    code_snippet,
    content='code_knowledge',
    content_rowid='id'
);

-- Triggers to keep FTS in sync
CREATE TRIGGER IF NOT EXISTS code_fts_insert AFTER INSERT ON code_knowledge BEGIN
    INSERT INTO code_fts(rowid, symbol_name, purpose, docstring, code_snippet)
    VALUES (new.id, new.symbol_name, new.purpose, new.docstring, new.code_snippet);
END;

CREATE TRIGGER IF NOT EXISTS code_fts_delete AFTER DELETE ON code_knowledge BEGIN
    DELETE FROM code_fts WHERE rowid = old.id;
END;

CREATE TRIGGER IF NOT EXISTS code_fts_update AFTER UPDATE ON code_knowledge BEGIN
    DELETE FROM code_fts WHERE rowid = old.id;
    INSERT INTO code_fts(rowid, symbol_name, purpose, docstring, code_snippet)
    VALUES (new.id, new.symbol_name, new.purpose, new.docstring, new.code_snippet);
END;

-- ============================================================================
-- COMMAND EXECUTION INTELLIGENCE
-- ============================================================================

-- Command execution history
CREATE TABLE IF NOT EXISTS command_patterns (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    command TEXT NOT NULL,
    command_type TEXT,  -- build, install, test, run
    duration_ms INTEGER NOT NULL,
    exit_code INTEGER,
    cpu_avg REAL,
    cpu_max REAL,
    memory_peak_mb INTEGER,
    disk_read_mb REAL,
    disk_write_mb REAL,
    network_sent_mb REAL,
    network_recv_mb REAL,
    success BOOLEAN NOT NULL,
    output_snippet TEXT,  -- First/last 500 chars
    error_snippet TEXT,
    working_directory TEXT,
    environment_hash TEXT,  -- To group by environment
    executed_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_cmd_command ON command_patterns(command);
CREATE INDEX IF NOT EXISTS idx_cmd_type ON command_patterns(command_type);
CREATE INDEX IF NOT EXISTS idx_cmd_success ON command_patterns(success);
CREATE INDEX IF NOT EXISTS idx_cmd_executed ON command_patterns(executed_at);

-- Command baselines (expected behavior)
CREATE TABLE IF NOT EXISTS command_baselines (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    command TEXT UNIQUE NOT NULL,
    command_type TEXT,
    sample_count INTEGER DEFAULT 0,
    avg_duration_ms INTEGER,
    stddev_duration_ms REAL,
    min_duration_ms INTEGER,
    max_duration_ms INTEGER,
    avg_cpu REAL,
    avg_memory_mb INTEGER,
    typical_exit_code INTEGER,
    success_rate REAL,  -- 0.0 to 1.0
    last_updated DATETIME DEFAULT CURRENT_TIMESTAMP,
    confidence REAL DEFAULT 0.0  -- Based on sample_count
);

CREATE INDEX IF NOT EXISTS idx_baseline_command ON command_baselines(command);

-- System metrics baseline (per machine)
CREATE TABLE IF NOT EXISTS system_metrics (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    metric_name TEXT NOT NULL,
    metric_value REAL NOT NULL,
    unit TEXT,
    category TEXT,  -- cpu, memory, disk, network
    recorded_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_metrics_name ON system_metrics(metric_name);
CREATE INDEX IF NOT EXISTS idx_metrics_category ON system_metrics(category);

-- ============================================================================
-- PROBLEM SOLVING INTELLIGENCE
-- ============================================================================

-- Known error patterns and solutions
CREATE TABLE IF NOT EXISTS error_solutions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    error_pattern TEXT NOT NULL,
    error_type TEXT,  -- syntax, runtime, build, network
    solution TEXT NOT NULL,
    context TEXT,  -- When this solution applies
    command_context TEXT,  -- Related command if any
    success_count INTEGER DEFAULT 0,
    failure_count INTEGER DEFAULT 0,
    confidence REAL DEFAULT 0.0,
    source TEXT,  -- manual, web_research, ai_generated
    source_url TEXT,  -- If from Stack Overflow, etc.
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    last_used DATETIME
);

CREATE INDEX IF NOT EXISTS idx_error_pattern ON error_solutions(error_pattern);
CREATE INDEX IF NOT EXISTS idx_error_type ON error_solutions(error_type);
CREATE INDEX IF NOT EXISTS idx_error_confidence ON error_solutions(confidence);

-- Full-text search for errors
CREATE VIRTUAL TABLE IF NOT EXISTS error_fts USING fts5(
    error_pattern,
    solution,
    context,
    content='error_solutions',
    content_rowid='id'
);

CREATE TRIGGER IF NOT EXISTS error_fts_insert AFTER INSERT ON error_solutions BEGIN
    INSERT INTO error_fts(rowid, error_pattern, solution, context)
    VALUES (new.id, new.error_pattern, new.solution, new.context);
END;

CREATE TRIGGER IF NOT EXISTS error_fts_delete AFTER DELETE ON error_solutions BEGIN
    DELETE FROM error_fts WHERE rowid = old.id;
END;

CREATE TRIGGER IF NOT EXISTS error_fts_update AFTER UPDATE ON error_solutions BEGIN
    DELETE FROM error_fts WHERE rowid = old.id;
    INSERT INTO error_fts(rowid, error_pattern, solution, context)
    VALUES (new.id, new.error_pattern, new.solution, new.context);
END;

-- Troubleshooting history
CREATE TABLE IF NOT EXISTS troubleshooting_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    problem_description TEXT NOT NULL,
    solution_id INTEGER,
    resolution TEXT,
    success BOOLEAN,
    time_to_resolve_minutes INTEGER,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (solution_id) REFERENCES error_solutions(id)
);

CREATE INDEX IF NOT EXISTS idx_troubleshoot_success ON troubleshooting_logs(success);
CREATE INDEX IF NOT EXISTS idx_troubleshoot_solution ON troubleshooting_logs(solution_id);

-- Web research cache
CREATE TABLE IF NOT EXISTS web_research_cache (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    query TEXT NOT NULL,
    source_url TEXT NOT NULL,
    content TEXT,
    summary TEXT,
    relevance_score REAL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(query, source_url)
);

CREATE INDEX IF NOT EXISTS idx_research_query ON web_research_cache(query);
CREATE INDEX IF NOT EXISTS idx_research_relevance ON web_research_cache(relevance_score);

-- ============================================================================
-- METADATA & SYSTEM
-- ============================================================================

-- Schema version for migrations
CREATE TABLE IF NOT EXISTS schema_version (
    version INTEGER PRIMARY KEY,
    applied_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

INSERT OR IGNORE INTO schema_version (version) VALUES (1);

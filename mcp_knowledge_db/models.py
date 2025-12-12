"""Data models for Knowledge Database"""
from dataclasses import dataclass, field, asdict
from datetime import datetime
from typing import Optional, List, Dict, Any
import json


@dataclass
class CodeFile:
    """Represents a code file in the database"""
    file_path: str
    project_name: Optional[str] = None
    language: Optional[str] = None
    size_bytes: Optional[int] = None
    last_indexed: Optional[datetime] = None
    checksum: Optional[str] = None
    id: Optional[int] = None

    def to_dict(self) -> Dict[str, Any]:
        d = asdict(self)
        if d['last_indexed']:
            d['last_indexed'] = d['last_indexed'].isoformat()
        return d


@dataclass
class CodeKnowledge:
    """Represents code intelligence for a symbol"""
    file_id: int
    symbol_name: str
    symbol_type: str  # function, class, method, variable
    line_start: Optional[int] = None
    line_end: Optional[int] = None
    purpose: Optional[str] = None
    complexity: Optional[str] = None
    parameters: Optional[List[Dict[str, Any]]] = None
    return_type: Optional[str] = None
    docstring: Optional[str] = None
    code_snippet: Optional[str] = None
    id: Optional[int] = None
    created_at: Optional[datetime] = None

    def to_dict(self) -> Dict[str, Any]:
        d = asdict(self)
        if d['parameters']:
            d['parameters'] = json.dumps(d['parameters'])
        if d['created_at']:
            d['created_at'] = d['created_at'].isoformat()
        return d


@dataclass
class CodeDependency:
    """Represents a dependency between code symbols"""
    from_symbol_id: int
    to_symbol_id: int
    dependency_type: str  # calls, imports, inherits, uses
    confidence: float = 1.0
    id: Optional[int] = None
    created_at: Optional[datetime] = None


@dataclass
class CommandPattern:
    """Represents a command execution record"""
    command: str
    duration_ms: int
    success: bool
    command_type: Optional[str] = None
    exit_code: Optional[int] = None
    cpu_avg: Optional[float] = None
    cpu_max: Optional[float] = None
    memory_peak_mb: Optional[int] = None
    disk_read_mb: Optional[float] = None
    disk_write_mb: Optional[float] = None
    network_sent_mb: Optional[float] = None
    network_recv_mb: Optional[float] = None
    output_snippet: Optional[str] = None
    error_snippet: Optional[str] = None
    working_directory: Optional[str] = None
    environment_hash: Optional[str] = None
    id: Optional[int] = None
    executed_at: Optional[datetime] = None

    def to_dict(self) -> Dict[str, Any]:
        d = asdict(self)
        if d['executed_at']:
            d['executed_at'] = d['executed_at'].isoformat()
        return d


@dataclass
class CommandBaseline:
    """Represents expected behavior for a command"""
    command: str
    sample_count: int = 0
    avg_duration_ms: Optional[int] = None
    stddev_duration_ms: Optional[float] = None
    min_duration_ms: Optional[int] = None
    max_duration_ms: Optional[int] = None
    avg_cpu: Optional[float] = None
    avg_memory_mb: Optional[int] = None
    typical_exit_code: Optional[int] = None
    success_rate: Optional[float] = None
    confidence: float = 0.0
    command_type: Optional[str] = None
    id: Optional[int] = None
    last_updated: Optional[datetime] = None

    def to_dict(self) -> Dict[str, Any]:
        d = asdict(self)
        if d['last_updated']:
            d['last_updated'] = d['last_updated'].isoformat()
        return d


@dataclass
class SystemMetric:
    """Represents a system metric measurement"""
    metric_name: str
    metric_value: float
    unit: Optional[str] = None
    category: Optional[str] = None  # cpu, memory, disk, network
    id: Optional[int] = None
    recorded_at: Optional[datetime] = None


@dataclass
class ErrorSolution:
    """Represents a known error and its solution"""
    error_pattern: str
    solution: str
    error_type: Optional[str] = None
    context: Optional[str] = None
    command_context: Optional[str] = None
    success_count: int = 0
    failure_count: int = 0
    confidence: float = 0.0
    source: Optional[str] = None  # manual, web_research, ai_generated
    source_url: Optional[str] = None
    id: Optional[int] = None
    created_at: Optional[datetime] = None
    last_used: Optional[datetime] = None

    def to_dict(self) -> Dict[str, Any]:
        d = asdict(self)
        if d['created_at']:
            d['created_at'] = d['created_at'].isoformat()
        if d['last_used']:
            d['last_used'] = d['last_used'].isoformat()
        return d


@dataclass
class TroubleshootingLog:
    """Represents a troubleshooting session"""
    problem_description: str
    resolution: Optional[str] = None
    success: Optional[bool] = None
    time_to_resolve_minutes: Optional[int] = None
    solution_id: Optional[int] = None
    id: Optional[int] = None
    created_at: Optional[datetime] = None


@dataclass
class WebResearchCache:
    """Represents cached web research results"""
    query: str
    source_url: str
    content: Optional[str] = None
    summary: Optional[str] = None
    relevance_score: Optional[float] = None
    id: Optional[int] = None
    created_at: Optional[datetime] = None

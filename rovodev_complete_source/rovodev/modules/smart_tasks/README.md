# Smart Tasks Foundation

This module provides a minimal, extensible foundation for discovering and presenting actionable developer tasks in Rovo Dev CLI.

## Design Goals

- **Simplicity:** Minimal task model with clear responsibilities
- **Extensibility:** Pluggable discovery via Python protocols
- **Cohesion:** Tasks encapsulate their own agent context (`get_context`)
- **Separation of concerns:** Formatting lives outside task models

## Architecture Overview

```
smart_tasks/
├── models.py           # Task, BuildFailureTask, DiscoveryContext
├── protocol.py         # TaskDiscoverer protocol + registration
├── manager.py          # Tasks singleton for orchestration
├── formatter.py        # TaskFormatter for CLI and agent output
└── discoverers/
    └── filesystem.py   # FileSystemTaskDiscoverer
```

## Usage Example

```python
from rovodev.modules.smart_tasks import tasks, DiscoveryContext

# 1. Initialize discoverers (only filesystem for now)
tasks.initialize_discoverers(["filesystem"])

# 2. Discover tasks based on workspace context
context = DiscoveryContext(workspace_path="/path/to/workspace")
tasks.discover_tasks(context)

# 3. Render output for CLI or agent
print(tasks.to_cli())
print(tasks.to_agent_prompt())
```

## Task Model

- `Task`: Base class with `id`, `name`, and `get_context()` for agent enrichment
- `BuildFailureTask`: Adds `command` and `package`, overrides `get_context`

## Discoverers

Implement the `TaskDiscoverer` protocol and register with `@task_discoverer("name")`. Only `filesystem` discoverer is provided by default.

## Configuration

Tasks are read from `.rovodev/smart-tasks.yml`. Example:

```yaml
tasks:
  - id: "build-001"
    name: "Fix failing build in CLI package"
    task_type: "build_failure"
    command: "uv run ruff format --check ."
    package: "cli-rovodev"
```

## Future Extensions

- Implement real discoverers: Jira, NBT, Bitbucket
- Add task filtering and detailed CLI commands
- Integrate analytics for discovery and usage tracking
```
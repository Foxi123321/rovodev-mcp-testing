---
title: Use Memory in Rovo Dev CLI
description: Understand memory files, structure, commands, and best practices in Rovo Dev CLI.
platform: platform
product: rovodev-cli
category: devguide
subcategory: using-the-cli
date: '2025-10-09'
---
# Use Memory in Rovo Dev CLI

Rovo Dev CLI provides a powerful memory system that helps the agent remember important information about your project and preferences across sessions. This documentation covers how to use and manage memory files effectively.

## Overview

Memory files store contextual information that Rovo Dev references when working on your projects. There are two types of memory:

- **Project Memory**: Stored in your workspace directory (AGENTS.md and AGENTS.local.md). AGENTS.local.md is repo-specific personal memory and is typically not checked into version control.
- **User Memory**: Global memory stored in your home directory (~/.rovodev/AGENTS.md)

## Memory Commands

### `/memory` - Memory File Management

Opens the preferred memory file in the current directory for editing. Preference order:
- AGENTS.md (if exists)
- .agent.md (legacy)
- Otherwise creates AGENTS.md if none exist.

```bash
/memory
```

### `/memory user` - User Memory

Opens your global user memory file for editing.

```bash
/memory user
```

### `/memory init` - Initialize Memory

Uses AI to automatically generate or update the current directory's memory file based on your project structure and content.

```bash
/memory init
```

### `/memory reflect` - Memory Reflection

Analyzes the current conversation and intelligently integrates useful insights into your workspace memory file.

```bash
# Update default AGENTS.md file
/memory reflect

# Update a custom file path
/memory reflect docs/PROJECT_MEMORY.md
```

The custom file path can be:
- Relative to the current directory (e.g., `docs/memory.md`)
- Absolute paths (e.g., `/home/user/project/memory.md`)

When a custom file path is specified, insights will be integrated into that file instead of the default AGENTS.md file.

## Memory File Structure

Memory files are written in Markdown and can contain:

- **Project-specific context and conventions**
- **Coding standards and preferences**
- **Important architectural decisions**
- **Frequently used patterns or snippets**
- **Development workflow and best practices**

### Example Memory File

```markdown
# Project Memory

## Architecture

- This is a React application with TypeScript
- Uses Redux for state management
- API calls are made through RTK Query

## Coding Standards

- Use functional components with hooks
- Follow the established folder structure in src/
- All components should have TypeScript interfaces
- Use CSS modules for styling

## Important Notes

- Database migrations are in the /migrations folder
- Testing strategy focuses on integration tests
- Always update the API documentation when adding endpoints

# Workspace notes

- Feature X is deprecated and should not be extended
- New components should follow the design system patterns
```

## Memory File Discovery

Rovo Dev automatically discovers memory files in the following order:

### Workspace Memory Files

1. Current directory and parent directories:
   - `AGENTS.md` (preferred)
   - `AGENTS.local.md`
   - `.agent.md` (legacy support)
   - `.agent.local.md` (legacy support)

### User Memory Files

2. User's home directory:
   - `~/.rovodev/AGENTS.md`
   - `~/.rovodev/.agent.md` (legacy support)

## Memory File Hierarchy

When multiple memory files exist, Rovo Dev loads them in a specific hierarchy:

1. **User memory** - Applied globally across all projects
2. **Workspace memory** - Applied from parent directories (furthest to closest)
3. **Local memory** - Applied from the current directory (highest priority)

Files closer to your current working directory take precedence over those further away.

## Legacy File Support

Rovo Dev maintains backward compatibility with several legacy memory file formats:

- `CLAUDE.md`, `CLAUDE.local.md`
- `codex.md`, `.codex/*.md`
- `.cursor/rules/*.mdc`, `.cursorrules.md`, `.cursorrules`
- `rules.md`, `.rules.md`
- `.agent.md`, `.agent.local.md`

When using `/memory init`, content from these legacy files will be migrated to the new AGENTS.md format. Only files present at the repository root are considered; files in subdirectories are ignored.

## Best Practices

### Writing Effective Memory

1. **Be Specific**: Include concrete examples and specific patterns rather than generic advice
2. **Keep It Current**: Update memory files as your project evolves
3. **Use Structure**: Organize information with clear headers and sections
4. **Include Context**: Explain why certain decisions were made

### Project Memory Tips

- Document unusual project setup or configuration requirements
- Include information about external dependencies and their versions
- Note any temporary workarounds or technical debt
- Describe the testing strategy and important test patterns

### User Memory Tips

- Store your general coding preferences and style guidelines
- Include frequently used code snippets or templates
- Document your preferred project structures and naming conventions
- Note any global tools or utilities you commonly use

## Memory Initialization

The `/memory init` command analyzes your workspace and creates a comprehensive memory file that includes:

- **Project Purpose**: Automatically detected language, frameworks, and technologies
- **Important Files**: Key configuration files, entry points, and directories
- **Conventions**: Observed patterns in code structure, naming, and organization
- **Best Practices**: Inferred from existing code quality and patterns

This is particularly useful when:

- Starting work on a new project
- Onboarding team members
- Refreshing memory files for existing projects
- Migrating from legacy memory file formats

## Memory and Session Context

Memory files are loaded automatically when Rovo Dev starts and are included in the agent's context. This means:

- The agent references memory content when making decisions
- Memory information influences code generation and suggestions
- Changes to memory files take effect in new sessions

## Troubleshooting

### Memory File Not Loading

If your memory file isn't being recognized:

1. Check the file name matches supported patterns (AGENTS.md, AGENTS.local.md, .agent.md)
2. Ensure the file is in the current directory or a parent directory
3. Verify the file contains valid Markdown content
4. Use `/memory` to check if the file opens correctly

### Memory Content Not Applied

If the agent isn't following memory instructions:

1. Check memory file syntax and formatting
2. Ensure instructions are clear and specific
3. Try starting a new session to reload memory content
4. Use `/memory` to verify the current memory file content


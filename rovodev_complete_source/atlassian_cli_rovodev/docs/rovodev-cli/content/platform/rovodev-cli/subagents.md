---
title: Sub Agents
description: Create Sub Agents to delegate tasks
platform: platform
product: rovodev-cli
category: devguide
subcategory: using-the-cli
date: '2025-10-09'
---
# Subagents

(internal) Subagents are specialized AI agents that can be invoked by Rovo Dev to handle specific types of work. Each subagent has its own configuration, specialized capabilities, and can use different models and tool configurations.

## Overview

The subagents feature allows you to:

- Create specialized agent profiles for different types of tasks
- Configure custom system prompts and tool sets for each subagent
- Delegate specific work to specialized agents through the `invoke_subagent` tool
- Use different AI models for different types of work

## Managing Subagents

Access the subagent management interface inside a running Rovo Dev session:

```bash
acli rovodev run
# then in the session prompt
then type: /subagents
```

This opens an interactive menu where you can:

- View existing subagent profiles
- Create new subagent configurations
- Edit existing subagent settings

Note: This feature is gated in configuration and may be disabled in some environments. If the `/subagents` command is not available, the feature may be disabled for your environment.

## Creating a Subagent

When creating a new subagent, you'll be prompted to configure:

### 1. Subagent Name

A unique identifier for your subagent (e.g., "commit-summarizer", "code-reviewer").

### 2. Description

A brief description of what this subagent does.

### 3. Scope

Choose where the subagent configuration is stored and applied:

- Project: Saved under `.rovodev/subagents/` in the current workspace and applies to that project
- User: Saved under `~/.rovodev/subagents/` and available across all workspaces

### 4. Model Selection

Choose the AI model for this subagent:

- Use the parent agent’s model (default)
- Select a specific model optimized for the subagent’s tasks

If no model is selected, the parent agent’s model will be used.

### 5. System Prompt

Configure the specialized instructions for your subagent:

- Write a custom system prompt that defines the subagent’s role and behavior
- Optionally use AI-assisted prompt generation and tool pre-selection, which suggests a system prompt and initial tool set based on your description
- Define specific guidelines and constraints for the subagent

### 6. Tool Configuration

Select which tools the subagent can access:

- Choose from available MCP server tools
- Limit tools to only what's necessary for the subagent’s specific role
- Or inherit the parent agent’s tools (default)

If no tools are selected, the parent agent’s tool set will be used.

## Using Subagents

Once configured, subagents can be invoked through the `invoke_subagent` tool available to the main Rovo Dev agent. The main agent will automatically delegate appropriate tasks to specialized subagents when needed.

Example workflow:

1. You ask Rovo Dev to analyze git commits and generate summaries
2. Rovo Dev recognizes this as a task suitable for a specialized subagent
3. It invokes the "commit-summarizer" subagent with the relevant context
4. The subagent processes the request and returns results
5. Rovo Dev incorporates the subagent's response into the overall solution

## Subagent Storage

Subagent configurations are stored as Markdown files with YAML frontmatter:

- User scope: `~/.rovodev/subagents/<name>.md`
- Project scope: `.rovodev/subagents/<name>.md`

Each file contains a frontmatter block with the subagent configuration and a body containing the system prompt.

### Discovery and Precedence

Subagents are discovered from multiple locations and the first definition found for a given name takes precedence:

1. Built-in subagents (available to all users)
2. Built-in internal subagents (available only to internal users)
3. User scope: `~/.rovodev/subagents/`
4. Project scope: All ancestor directories that contain `.rovodev/subagents/`, starting from the current workspace and walking up to the filesystem root (the nearest ancestor has higher precedence than farther ancestors)

If duplicate subagent names are found in multiple locations, the first one discovered is used and a warning is shown indicating which definition took precedence.

## Best Practices

### Naming Conventions

- Use descriptive, hyphenated names (e.g., "code-reviewer", "documentation-writer")
- Keep names concise but clear about the subagent's purpose

### System Prompts

- Be specific about the subagent's role and responsibilities
- Include examples of expected input and output formats
- Define clear boundaries for what the subagent should and shouldn't do
- Use the AI-assisted generation feature for initial prompt suggestions

### Tool Selection

- Only grant access to tools that the subagent actually needs
- Consider security implications when selecting tools
- Test subagent configurations with different scenarios

### Scope Configuration

- Choose "Project" for subagents that work with project files in a specific workspace
- Choose "User" for subagents that should be available across all workspaces
- Consider the subagent's intended use cases when setting scope

## Availability

(internal) The subagents feature is available when enabled in your Rovo Dev configuration. If the `/subagents` command is not available, the feature may be disabled in your current environment.

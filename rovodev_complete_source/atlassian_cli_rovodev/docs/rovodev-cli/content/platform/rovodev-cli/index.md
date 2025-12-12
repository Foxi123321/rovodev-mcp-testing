---
title: Rovo Dev CLI Quickstart
description: Get started quickly with Rovo Dev CLI interactive and non-interactive modes, commands, and example prompts.
platform: platform
product: rovodev-cli
category: devguide
subcategory: getting-started
date: '2025-10-09'
---
# Rovo Dev CLI Quickstart Guide

Once you install Rovo Dev CLI on your device, run it in interactive mode using `acli rovodev` (defaults to `run`) or `acli rovodev run`.

## Commands

While in interactive mode, you can enter `/` at any time to see the list of available commands.

### Core Session Management

- **`/sessions`** - Switch between sessions, and view session details
  - **`/sessions new [title]`** - Create a new session with optional custom title
  - **`/sessions fork [title]`** - Fork the current session with optional custom title
  - **`/sessions rename <new_title>`** - Rename the current session
  - **`/sessions rename <session_id> <new_title>`** - Rename a specific session
- **`/clear`** - Clear the current session's message history
- **`/prune`** - Reduce the token size of the current session's message history while retaining context

### Configuration and Tools

- **`/models`** - View and select from available models
- **`/prompts`** - Run saved prompts (supports custom prompts via `.rovodev/prompts.yml`)
- **`/memory`** - Memory file management
  - **`/memory user`** - Create/open your user-level memory file
  - **`/memory init`** - Generate or update the current directory's memory file using AI
  - **`/memory reflect [file_path]`** - Analyze current conversation and intelligently integrate insights into the workspace memory file (optionally specify custom file path)
### Productivity Features

- **`/copy`** - Copy the last agent response to clipboard
  - **`/copy conversation [limit]`** - Copy conversation history to clipboard (optionally last N messages)
- **`/yolo`** - Toggle on/off yolo mode which runs all file CRUD operations and bash commands without confirmation. Use with caution!

### System and Integration Commands

- **`/status`** - Show Rovo Dev CLI status including version, account details and model
- **`/feedback`** - Provide feedback or report a bug on Rovo Dev CLI
- **`/usage`** - Show your daily LLM token usage (API token authentication only). On sites with monthly credit entitlements, shows your monthly credits usage instead.
- **`/usage site`** - Switch between sites that have Rovo Dev. Available only when monthly credit entitlement is enabled.
- **`/mcp`** - Manage MCP servers
- **`/directories`** - Manage allowed external directories for file access
- _(internal)_ **`/subagents`** - Manage subagent profiles
- _(internal)_ **`/ide`** - Install Rovo Dev IDE plugin (when enabled)

### Jira Integration _(when enabled)_

- **`/jira`** - Configure Jira project connection (use `/jira global` or `/jira local`)
  - **`/jira global`** - Configure global Jira project for all workspaces
  - **`/jira local`** - Configure local workspace Jira project override
  - **`/jira local remove`** - Remove local workspace override
  - **`/jira disable`** - Disable Jira integration

### Help and Exit

- **`/help`** - Show help and available commands. For AI-powered help, use `/help <query>` (when enabled)
- **`/exit`** - Quit Rovo Dev (also accepts `/quit`, `/q`, `exit`, `quit`, or `q`)

## Tips for Working with Rovo Dev

- **Start small** - Rovo Dev works best with small changes, about 10 or 20 lines at a time
- **Break down your tasks** - Break bigger changes into smaller steps for Rovo Dev to tackle one at a time
- **Review and iterate** - Treat Rovo Dev like a teammate you're collaborating with, give feedback on the code it generates with what to change and improve
- **Change gears** - Use the `/sessions` command to start a new session if the current approach isn't working and you need a fresh perspective from Rovo Dev
- **Save frequently** - Regularly commit changes to track your progress and avoid losing work if something goes wrong
- **Check your work** - You can ask Rovo Dev to review its own changes, compare the changes against a parent commit for linting errors, and submit draft pull requests to verify CI/CD logs

## Token Usage and Credits

Rovo Dev CLI resource usage is metered. Depending on your site’s entitlement, usage is tracked as either daily tokens or monthly Rovo Dev credits.

- Daily token limits reset at midnight UTC (legacy entitlement)
- Monthly credits apply on sites with the new entitlement model

Use `/usage` in interactive mode to view your current usage. If you have access to multiple Atlassian sites and site entitlement is enabled, use `/usage site` to switch the active site — you’ll use credits from the site you choose.

## Modes and Command-Line Options

### Interactive Mode

Interactive mode is Rovo Dev's default mode. It lets you use natural language to work with the agent so it can answer questions, iterate on code, and problem solve with you.

Run interactive mode from the command line using:

```bash
acli rovodev run
```

Note: You can also start interactive mode with:

```bash
acli rovodev
```

Top-level help and version:

```bash
acli rovodev --help
acli rovodev --version
```

### Non-Interactive Mode

In non-interactive mode, Rovo Dev updates files in your codebase directly without interaction. This is useful for automating repetitive tasks once you're happy with results of an instruction.

Run non-interactive mode from the command line using either of the following forms:

```bash
# Explicitly specify the run command
acli rovodev run <instruction>

# Or omit "run" (the CLI defaults to the run command)
acli rovodev "<instruction>"
```

**Examples:**

```bash
acli rovodev run "Create unit tests for all components without tests"
acli rovodev "Create unit tests for all components without tests"
```

### Command-Line Flags

You can customize Rovo Dev's behavior using these command-line flags:

- **`--config-file`** - Specify a custom config file path (default: `~/.rovodev/config.yml`)
- **`--shadow`** - Enable/disable shadow mode (runs on temporary workspace clone)
- **`--verbose`** - Enable/disable verbose tool output
- **`--restore`** - Continue the last session instead of starting a new one
- **`--yolo`** - Enable yolo mode (no confirmations for file operations and bash commands)

**Examples:**

```bash
# Run with custom config file
acli rovodev run --config-file ./custom-config.yml

# Run in shadow mode with verbose output
acli rovodev run --shadow --verbose "Refactor the authentication module"

# Restore the last session
acli rovodev run --restore

# Run with yolo mode enabled
acli rovodev run --yolo "Fix all linting errors"
```

## Example Prompts

### Explore Your Codebase

Rovo Dev reads your codebase and answers questions in clear language, helping you quickly navigate familiar codebases and decipher new ones.

- `Explain this repository to me`
- `Where is the authentication logic defined?`
- `What input validation happens during user registration?`

### Work with Atlassian Apps

Rovo Dev integrates with Jira and Confluence, so you can access your team's knowledge and manage your work without switching contexts. Specify the URL of your site in the prompt.

- `Which Jira work items in site vitafleet.atlassian.net are assigned to me and in To Do status?`
- `Implement code changes for Jira work item ABC-123 in site vitafleet.atlassian.net`
- `Create a list of changes needed to implement dark mode and publish to Confluence in site vitafleet.atlassian.net`

### Ideate and Plan

Rovo Dev analyzes your codebase to help you brainstorm and plan technical solutions.

- `Suggest new features to add that would improve the user experience`
- `How can I improve performance of this app?`
- `Create a coding plan for adding international currencies to the shopping cart, don't implement any changes yet`

### Generate Code

Rovo Dev generates consistent, structured code to help you build and transform your applications.

- `Review this modal component and add missing ARIA attributes`
- `Migrate code in this repository from C++ to Java`
- `Add search suggestions to search bar: trigger after 3 characters, include keyboard navigation (up/down/enter), filter on a predefined list of popular products`

### Analyze and Iterate on Code

Rovo Dev analyzes code, both existing code and code it has generated, and refines it based on your feedback.

- `Review this repository and make suggestions to improve readability and performance`
- `I'm getting a 500 error when fetching data from the backend API using Axios - find the issue and fix it`
- `The error handling you generated for this function is too simple - add more specific error cases and retry logic`

### Write Code Documentation

Rovo Dev generates documentation based on the latest changes to your codebase.

- `Write detailed documentation for this REST API, including available endpoints, parameters, and expected responses - publish to Confluence space "Vitafleet"`
- `Write JSDoc-style comments for this JavaScript function that handles form validation`
- `Write a README.md file for this project - include sections "Setup", "Features", and "Deployment information"`

### Test and Deploy

Rovo Dev helps you build comprehensive test suites and configure your deployment pipelines.

- `Generate 100 rows of synthetic user data with: name, email, age, location, and signup date - output it as a CSV`
- `Write a test using React Testing Library to verify if the form shows appropriate error messages when trying to submit with empty mandatory fields`
- `Modify bitbucket-pipelines.yml to add a step for running Jest tests before deploying`

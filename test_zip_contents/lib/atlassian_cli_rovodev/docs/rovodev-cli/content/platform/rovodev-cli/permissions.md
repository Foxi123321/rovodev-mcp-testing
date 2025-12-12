---
title: Tool Permissions in Rovo Dev CLI
description: Control and configure tool permissions, scopes, yolo mode, and command execution safety.
platform: platform
product: rovodev-cli
category: devguide
subcategory: configuration
date: '2025-12-01'
---
# Tool Permissions in Rovo Dev CLI

Rovo Dev CLI implements a granular permission system to give you control over which tools the AI agent can execute. This ensures safety and predictability when working with file operations, bash commands, and external integrations.

## Permission Levels

There are three permission levels available for any tool:

- **`allow`** - The tool executes automatically without prompting
- **`ask`** - The tool requires your approval before execution (default)
- **`deny`** - The tool is blocked and cannot be executed

## Permission Scopes

When you're prompted to grant permission for a tool, you can choose from several scopes:

- **Once** - Grants or denies permission for this single execution only
- **Session** - Grants or denies permission for the entire current session
- **Always** - Saves the permission to your config file for all future sessions

## Configuring Tool Permissions

Tool permissions are configured in your `~/.rovodev/config.yml` file under the `toolPermissions` section. You can edit this file using:

```bash
acli rovodev config
```

### Default Permission

Set the default permission level for tools that aren't explicitly configured:

```yaml
toolPermissions:
  default: "ask"  # Options: "allow", "ask", "deny"
```

### Specific Tool Permissions

Configure permissions for individual tools:

```yaml
toolPermissions:
  tools:
    # File operations that modify the workspace
    create_file: "ask"
    delete_file: "ask"
    move_file: "ask"
    find_and_replace_code: "ask"
    
    # Read-only operations
    open_files: "allow"
    expand_code_chunks: "allow"
    expand_folder: "allow"
    grep: "allow"
    
    # Planning and analysis tools
    create_technical_plan: "allow"
    
    # Subagent integration
    invoke_subagent: "allow"
    
    # Atlassian integration - read operations
    getJiraIssue: "allow"
    getConfluencePage: "allow"
    searchJiraIssuesUsingJql: "allow"
    searchConfluenceUsingCql: "allow"
    
    # Atlassian integration - write operations
    createJiraIssue: "ask"
    editJiraIssue: "ask"
    createConfluencePage: "ask"
    updateConfluencePage: "ask"
```

### Bash and PowerShell Command Permissions

Bash commands have their own permission system that supports pattern matching. PowerShell commands use exact command matching. Both shells share the same commands list.

- On macOS/Linux, the configuration section is `bash:`
- On Windows, the configuration section is serialized as `powershell:`

```yaml
toolPermissions:
  bash:  # use 'powershell' on Windows
    # Default permission for shell commands not explicitly listed
    default: "ask"
    
    # Specific commands with permissions
    commands:
      - command: "ls.*"      # Pattern: allows 'ls' with any arguments (bash only)
        permission: "allow"
      - command: "cat.*"     # Pattern: allows 'cat' with any arguments (bash only)
        permission: "allow"
      - command: "echo.*"    # Pattern: allows 'echo' with any arguments (bash only)
        permission: "allow"
      - command: "pwd"       # Exact match: only 'pwd' without arguments
        permission: "allow"
      - command: "npm test"  # Exact match: specific command
        permission: "allow"
      - command: "git.*"     # Pattern: allows all git commands (bash only)
        permission: "allow"
    
    # Run commands in a sandboxed environment (macOS and Linux only). On Windows, enabling this disables PowerShell commands.
    runInSandbox: false
```

#### Environment variables for shell commands

You can define environment variables that will be set when running bash or PowerShell commands. Variables are inherited from your environment by default (sensitive variables like tokens are filtered out), and you can add or override values here. You may also reference other environment variables with the ${VAR_NAME} syntax.

```yaml
toolPermissions:
  bash:  # use 'powershell' on Windows
    env:
      NODE_OPTIONS: "--max-old-space-size=4096"
      PATH: "${PATH}:/opt/tools/bin"
      MY_SECRET: "${MY_SECRET}"
```

Notes:
- On Windows, this configuration is serialized under `powershell` instead of `bash`.
- Referenced variables that are not set will remain uninterpolated (e.g., ${UNDEFINED_VAR} stays as-is).
- In Windows, ensure path separators are appropriate for your shell.


**Pattern Matching:**
- Bash: Commands ending with `.*` match the base command with any arguments (e.g., `ls.*` matches `ls`, `ls -la`, `ls /home`). Commands without `.*` require an exact match (e.g., `pwd` only matches `pwd`, not `pwd /home`).
- PowerShell: Patterns are ignored; only exact command entries are honored. Add specific commands (e.g., `npm test`) to the list to allow them. The first time a PowerShell command is attempted, an entry using the default permission may be added in-memory for that exact command; persist it by choosing an "always" scope.

**Auto-Allowed Safe Commands:**
Certain read-only commands are automatically allowed for security and usability, including: `ls`, `ll`, `la`, `cat`, `head`, `tail`, `less`, `more`, `echo`, `pwd`, `grep`, `wc`, `sort`, `uniq`, `which`, `whereis`, `type`, `file`, `stat`, `du`, `df`, `ps`, `top`, `htop`, `jobs`, `date`, `whoami`, `uname`, `uptime`, `sleep`, `man`, `help`, `true`, `false`, and various package manager read operations (`npm list`, `npm view`, `pip show`, `yarn info`, `poetry show`, `cargo check`, etc.). These commands bypass permission checks entirely.

**Auto-Denied Unsafe Commands:**
Some commands are automatically blocked for safety, including file deletion commands (`rm`, `rmdir`, `unlink`, `shred`) and file overwriting operations (`dd of=`). Additionally, complex deletion patterns like `find ... -delete`, `find ... -exec rm`, and `xargs rm` are also automatically denied. These commands will be denied with helpful messages suggesting the use of appropriate file tools instead.

**Compound Commands:**
When the agent attempts to run compound bash commands (using `&&`, `||`, `;`, or pipes), each subcommand is evaluated independently. You'll be prompted for permission for each subcommand that hasn't been explicitly allowed. Commands containing complex features like redirections, command substitutions, or process substitutions will default to requiring permission.

Note: Very long commands may not offer the "Allow (always)" option in the prompt to avoid bloating your configuration file.

### Allowed External Paths

By default, Rovo Dev CLI can only access files within your current workspace. You can grant access to additional paths:

```yaml
toolPermissions:
  allowedExternalPaths:
    - "/Users/username/shared-configs"
    - "~/Documents/templates"
```

Paths are resolved and validated when the configuration is loaded. You'll see a warning if a path doesn't exist.

## Yolo Mode

Yolo mode is a special permission mode that bypasses all confirmations for file CRUD operations and bash commands. **Use with extreme caution** as it allows the agent to make changes without your approval.

### Enabling Yolo Mode

**In interactive mode:**
```
/yolo
```

**From command line:**
```bash
acli rovodev run --yolo "Fix all linting errors"
```

**Toggle in session:**
Use `/yolo` to enable yolo mode, and `/yolo` again to disable it.

When yolo mode is enabled:
- All file operations (create, delete, modify, move) execute without confirmation
- All bash and PowerShell commands execute without confirmation
- The agent can work faster but with less safety

When yolo mode is active, you'll see the message:
```
Yolo engaged: No confirmations, just consequences.
```

When you disable it:
```
Yolo disabled: Tool call confirmations restored.
```

## Interactive Permission Prompts

When a tool requires permission and is set to `ask`, you'll see an interactive prompt like:

```
Requesting permission to use tool bash with command:
````
npm install
````
Would you like to allow this tool?

> Allow (once)
  Allow (session)
  Allow (always)
  Allow (always) for all 'npm' commands
  Deny (once)
  Deny (session)
  Deny (always)
```

**Options explained:**
- **Allow (once)** - Execute this specific command now
- **Allow (session)** - Allow this command for the rest of this session
- **Allow (always)** - Save permission to config file for future sessions
- **Allow (always) for all 'X' commands** - Save a pattern permission (e.g., `npm.*`) to allow all variations
- **Deny (once)** - Block this execution only
- **Deny (session)** - Block this command for the rest of this session
- **Deny (always)** - Save denial to config file to always block this command

## Permission Resolution

The permission system resolves permissions in the following order:

1. **Yolo mode check**: If yolo mode is enabled, all Nautilus tools and bash/PowerShell commands are allowed
2. **Always-allowed tools**: Certain tools like `update_todo` are always allowed regardless of configuration
3. **Background process retrieval**: Bash and PowerShell commands that retrieve logs from background processes (using PID) are automatically allowed
4. **MCP schema/list calls**: Tool schema and listing calls are always allowed
5. **Auto-denied unsafe commands**: Commands like `rm`, `rmdir`, file deletion patterns are automatically blocked
6. **Auto-allowed safe commands**: Read-only commands like `ls`, `cat`, `pwd`, etc. are automatically allowed
7. **Exact command match**: For bash/PowerShell, checks for exact command match
8. **Pattern match**: For bash commands, checks for pattern matches (e.g., `git.*`)
9. **Tool-specific permission**: Checks the `tools` dictionary for the specific tool
10. **Default permission**: Falls back to the `default` permission setting

## Non-Interactive Mode

When running Rovo Dev in non-interactive mode (e.g., in CI/CD pipelines), permission prompts automatically default to `deny` to prevent blocking. Make sure to pre-configure appropriate permissions in your config file for automated workflows.

## MCP Server Tools

Tools from MCP (Model Context Protocol) servers inherit the same permission system. When an MCP tool is called for the first time, it uses the `default` permission setting. You can configure specific MCP tool permissions just like any other tool in the `tools` section.

## Best Practices

1. **Start restrictive**: Keep the default permission as `ask` to maintain control
2. **Allow safe reads**: Set read-only operations like `grep`, `open_files`, and `expand_code_chunks` to `allow`
3. **Be cautious with write operations**: Keep `create_file`, `delete_file`, and `find_and_replace_code` as `ask`
4. **Use patterns wisely**: Bash patterns like `git.*` can be convenient but grant broad permissions
5. **Review your config**: Periodically review your `~/.rovodev/config.yml` to ensure permissions align with your needs
6. **Use yolo mode sparingly**: Only enable yolo mode when you're confident in the agent's actions or working in a safe environment
7. **Session scope for experiments**: Use session scope when testing, then promote to "always" if the tool proves safe

## Security Considerations

- **Bash commands**: Be especially careful with bash permissions as they can execute arbitrary system commands
- **External paths**: Only add trusted directories to `allowedExternalPaths`
- **Write operations**: Consider keeping Atlassian write operations (creating/updating Jira issues or Confluence pages) as `ask` to review before publishing
- **Pattern matching**: Broad patterns like `.*` effectively grant unlimited access to a command

## Troubleshooting

**Tools being denied unexpectedly:**
- Check your `default` permission setting in `toolPermissions`
- Verify the tool name in your `tools` configuration matches exactly
- For bash commands, ensure your pattern includes `.*` if you want to match arguments

**Permission prompts not appearing:**
- Ensure you're running in interactive mode (not non-interactive or CI/CD)
- Check if yolo mode is enabled with `/status`
- Verify your terminal supports interactive input (`stdin.isatty()`)

**Config changes not taking effect:**
- Restart Rovo Dev CLI after editing the config file
- Verify your YAML syntax is correct using `acli rovodev config`
- Check for typos in tool names (they are case-sensitive)



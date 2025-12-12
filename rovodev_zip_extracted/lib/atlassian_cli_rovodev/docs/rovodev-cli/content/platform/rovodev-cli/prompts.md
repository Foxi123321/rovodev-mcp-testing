---
title: Save and reuse prompts in Rovo Dev CLI
description: Use built-in and custom saved prompts, configuration hierarchy, and best practices.
platform: platform
product: rovodev-cli
category: devguide
subcategory: using-the-cli
date: '2025-11-24'
---
# Save and reuse prompts in Rovo Dev CLI

Saved prompts help you speed up your development flow with pre-created prompts that can be run anytime.

## Using Saved Prompts

### Running Prompts Interactively

Use the `/prompts` command to view and select from available saved prompts:

```bash
/prompts
```

This opens an interactive menu where you can browse and select from built-in and custom prompts. In the menu, the `create-prompt` entry appears first so you can quickly add a new prompt.

**Note:** The legacy `/instructions` command is still supported but deprecated and will show a warning message. Please use `/prompts` instead.

### Running Specific Prompts

Run a specific prompt by name:

```bash
/prompts <name>
```

**Examples:**

```bash
/prompts local-code-review
/prompts unit-test-coverage
/prompts improve-documentation
```

### Running Prompts with Additional Context

Add extra instructions or context to any prompt:

```bash
/prompts <name> <additional instructions>
```

**Example:**

```bash
/prompts local-code-review Focus on security vulnerabilities
```

## Built-in Prompts

The CLI comes with several built-in prompts for common development tasks:

- **`create-prompt`** - Create a new saved prompt within your current folder
- **`commit`** - Commit pending changes with a descriptive message
- **`local-code-review`** - Perform a code review of your local changes
- **`unit-test-coverage`** - Analyze and increase unit test coverage
- **`improve-documentation`** - Update or improve the codebase documentation
- **`summarize-jira-issues`** - Provide a summary of Jira issues assigned to the current user
- **`summarize-confluence-page`** - Generate a summary of a specified Confluence page

## Creating Custom Prompts

You can create your own custom prompts by setting up configuration files in your project.

### 1. Create Prompts Configuration

Create a `prompts.yml` file in your `.rovodev` directory (you can also use `instructions.yml` for backwards compatibility):

```yaml
prompts:
  - name: my-custom-prompt
    description: My custom prompt description
    content_file: my_custom_prompt.md
  - name: another-prompt
    description: Another custom prompt
    content_file: another_prompt.md
```

**Backwards Compatibility**: You can also use `instructions:` instead of `prompts:` for backwards compatibility:

```yaml
instructions:  # legacy format, still supported
  - name: my-legacy-prompt
    description: My legacy prompt description
    content_file: my_legacy_prompt.md
```

### 2. Create Prompt Content Files

Create Markdown files in the `.rovodev` folder containing your prompt content:

**.rovodev/my_custom_prompt.md:**

```markdown
# My Custom Prompt

Please analyze the current codebase and:

1. Check for any code smells or anti-patterns
2. Suggest improvements for code organization
3. Identify any potential performance issues

Focus specifically on the following areas:

- Function complexity
- Code duplication
- Error handling patterns
```

## Configuration Hierarchy

The CLI loads prompts from multiple locations in order of precedence:

1. **Built-in prompts** - Shipped with the CLI (highest precedence, cannot be overridden)
2. **Repository root** - `.rovodev/prompts.yml` (or `.rovodev/instructions.yml`) in your Git repository root
3. **Current directory** - `.rovodev/prompts.yml` (or `.rovodev/instructions.yml`) in your current working directory
4. **User home** - `~/.rovodev/prompts.yml` (or `~/.rovodev/instructions.yml`) for global user prompts (lowest precedence)

The first location to define a prompt wins. This means that built-in prompts cannot be overridden by custom prompts with the same name.

Note on compatibility:
- The CLI loads `prompts.yml` (new format) before `instructions.yml` (legacy format). If the same prompt name exists in both files within the same location, the version from `prompts.yml` takes precedence.

## File Path Resolution

When loading prompt content files, the CLI searches for files in this order:

1. Relative to the `prompts.yml` (or `instructions.yml`) file location
2. Relative to the repository root (parent of `.rovodev` folder)
3. As an absolute path

This flexibility allows you to organize your prompt files in the way that works best for your project structure.

## Referencing Saved Prompts in Your Messages

You can reference saved prompts directly in any message by prefixing the prompt name with `!`. This will include the referenced prompt's content as contextual input to the AI.

- Use `!<name>` to include a saved prompt by name (e.g., `!local-code-review`).
- Reference multiple prompts in the same message (e.g., `!local-code-review !unit-test-coverage`).
- Prompts can reference other prompts; nested references are expanded recursively while preventing cycles.
- You can also reference a markdown file path that exists on disk (e.g., `!./.rovodev/my_custom_prompt.md`).
- When typing `!`, the CLI shows suggestions for available prompts.

Examples:

- "Please review the latest changes using !local-code-review and pay attention to security."
- "Create tests with !unit-test-coverage and then improve docs with !improve-documentation."

## Non-Interactive Mode

You can also run prompts in non-interactive mode from the command line:

```bash
acli rovodev run "/prompts local-code-review"
```

This is useful for automation scripts or CI/CD pipelines.

**Note:** The legacy `/instructions` command is still supported but will show a deprecation warning.

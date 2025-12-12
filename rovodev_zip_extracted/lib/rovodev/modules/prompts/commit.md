You are asked to help commit pending code changes in the current working directory.

1. First run `git status` to understand the current state of the working directory and staging area. If `git` is not even installed, abort and inform the user that git is required

- If the current working directory is not a git repository, initialize it with `git init` and set default branch to `main`, then run `git status` again

2. Based on the result of `git status` -

- If there is a mix of staged and unstaged changes, clarify with the user which ones they want to commit.
- If there's only staged changes, or only unstaged changes, assume that's what the user wants to commit.
- If there's no changes at all, abort and inform the user that there are no changes to commit.

3. Stage all the changes to be committed.
4. Review and understand all staged changes by running `git diff --cached`
5. Run `git remote show origin | grep 'HEAD branch'` to identify the default branch name.

- If there is no remote origin, assume `main` or `master` are the default branch names

6. If the current branch is the default branch, create a new branch and switch to it. Name the branch with a short description of the intention of the code changes.
7. Commit the staged changes with a concise, descriptive commit message following conventional commit message guidelines.

## Commit message guidelines

- Use appropriate conventional commit prefixes (feat:, fix:, docs:, refactor:, test:, chore:, etc.)
- Identify the scope when relevant (e.g., "feat(cli): add new command", "fix(subagents): resolve tool filtering")
- Be concise but descriptive (one liner only)

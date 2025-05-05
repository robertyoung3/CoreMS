# Git Guide for CoreMS Development

## Basic Git Commands

| Command | Description |
|---------|-------------|
| `git init` | Initialize a new Git repository |
| `git clone <url>` | Clone a repository from a URL |
| `git add <file>` | Add file(s) to staging area |
| `git commit -m "message"` | Commit staged changes with a message |
| `git status` | Show working tree status |
| `git log` | Show commit history |
| `git pull` | Fetch and merge changes from remote repository |
| `git push` | Push local commits to remote repository |
| `git branch` | List branches |
| `git branch <name>` | Create a new branch |
| `git checkout <branch>` | Switch to a specific branch |
| `git checkout -b <branch>` | Create and switch to a new branch |
| `git merge <branch>` | Merge a branch into current branch |
| `git diff` | Show changes between commits, commit and working tree, etc. |

## Advanced Git Commands

| Command | Description |
|---------|-------------|
| `git stash` | Stash changes in a dirty working directory |
| `git stash pop` | Apply stashed changes and remove from stash |
| `git reset <file>` | Unstage a file |
| `git reset --soft HEAD~1` | Undo the last commit, keeping changes staged |
| `git reset --hard HEAD~1` | Undo the last commit and all changes |
| `git reset --hard <commit>` | Reset to a specific commit, discarding all changes after it |
| `git rebase <branch>` | Reapply commits on top of another base |
| `git cherry-pick <commit>` | Apply changes from specific commits |
| `git tag <name>` | Create a tag |
| `git blame <file>` | Show who changed what and when in a file |
| `git remote -v` | Show remote repositories |

## Important Warning: Using Git Reset Hard

⚠️ **CAUTION**: `git reset --hard HEAD` followed by `git clean -fdx` is a destructive operation that:
- Resets the working directory exactly to HEAD commit state
- Removes ALL untracked files and directories (`-fdx` flags)
- **Ignores .gitignore rules when cleaning**

This means that even if files and directories are in your `.gitignore`, they will be deleted with the `git clean -fdx` command. 

### How to Safely Reset Your Repository

To avoid losing data in ignored directories, use one of these approaches:

1. **Back up important data** before running destructive git commands
2. Use selective cleaning instead:
   - `git clean -n` to see what will be deleted (dry run)
   - `git clean -fd` to delete untracked files/directories (but not ignored ones)

3. **To protect important ignored files/directories**:
   - Move them outside the repository temporarily
   - Use `git clean -fX` to only clean ignored files (not what you want)
   - Use `git clean -f` to only clean untracked, non-ignored files

## Common Git Workflows

### Feature Branch Workflow

```bash
git checkout -b feature/new-feature
# Make changes
git add .
git commit -m "Add new feature"
git push origin feature/new-feature
# Create pull request on GitHub
# After PR is approved and merged:
git checkout main
git pull
```

### GitHub Flow

```bash
# Start from the main branch
git checkout main
git pull origin main
# Create a branch for your feature or bugfix
git checkout -b descriptive-branch-name
# Make changes and commit
git add .
git commit -m "Descriptive message"
# Push to GitHub
git push origin descriptive-branch-name
# Create pull request, discuss, and merge on GitHub
# Clean up after merge
git checkout main
git pull
git branch -d descriptive-branch-name
```

### Git Fork Workflow

```bash
# Fork repository on GitHub first, then clone your fork
git clone https://github.com/yourusername/repository.git
# Add upstream remote
git remote add upstream https://github.com/original-owner/repository.git
# Create feature branch
git checkout -b feature-name
# Make changes and commit
git add .
git commit -m "Description of changes"
# Push to your fork
git push origin feature-name
# Create pull request from your fork to upstream repository
# Keep your fork in sync with upstream
git checkout main
git fetch upstream
git merge upstream/main
git push origin main
```

## Best Practices for CoreMS Development

1. **Commit Messages**: Write meaningful commit messages that explain why a change was made
2. **Pull Requests**: Keep PRs focused on a single issue or feature
3. **Code Reviews**: Request reviews from appropriate team members
4. **Testing**: Ensure all tests pass before submitting a PR
5. **Documentation**: Update documentation to reflect code changes
6. **Rebasing**: Prefer rebasing over merging to maintain a clean history

## Handling Merge Conflicts

When you encounter merge conflicts:

```bash
git status  # Identify conflicted files
# Edit files to resolve conflicts
git add <resolved-files>
git commit  # Complete the merge
```

Or abort the merge/rebase if needed:

```bash
git merge --abort
# or
git rebase --abort
```

## Using Git with VS Code

VS Code has excellent Git integration that can help visualize:
- Changed files
- Diffs between versions
- Merge conflicts
- Commit history

Use the Source Control panel (Ctrl+Shift+G) to stage, commit, and sync changes.

## Troubleshooting

### Recovering Lost Work

If you accidentally ran `git reset --hard` and lost changes:
1. Check `git reflog` to find the SHA of the commit before the reset
2. Use `git checkout <SHA>` to recover your work
3. Create a new branch from there: `git checkout -b recovery`

Note that this only works for committed changes. Uncommitted changes deleted by `git clean -fdx` cannot be recovered through Git.

### Restoring Deleted Ignored Files

If ignored files were deleted by `git clean -fdx`:
1. Restore from backup if available
2. Check if your system has file recovery tools
3. For future protection, keep important data outside the Git repository

### Handling Merge Conflicts

When you get merge conflicts:
1. Run `git status` to see conflicted files
2. Edit the files to resolve conflicts (look for `<<<<<<<`, `=======`, `>>>>>>>` markers)
3. `git add` the resolved files
4. Complete the merge with `git commit`

## Troubleshooting

### Recovering Lost Work

If you accidentally ran `git reset --hard` and lost changes:
1. Check `git reflog` to find the SHA of the commit before the reset
2. Use `git checkout <SHA>` to recover your work
3. Create a new branch from there: `git checkout -b recovery`

Note that this only works for committed changes. Uncommitted changes deleted by `git clean -fdx` cannot be recovered through Git.

### Restoring Deleted Ignored Files

If ignored files were deleted by `git clean -fdx`:
1. Restore from backup if available
2. Check if your system has file recovery tools
3. For future protection, keep important data outside the Git repository

### Handling Merge Conflicts

When you get merge conflicts:
1. Run `git status` to see conflicted files
2. Edit the files to resolve conflicts (look for `<<<<<<<`, `=======`, `>>>>>>>` markers)
3. `git add` the resolved files
4. Complete the merge with `git commit`

## Git and DevContainers (Docker)

When working with Docker and Git:

1. Add Docker-specific files to .gitignore if needed:

```python
.docker/data/ 
.docker/logs/
```

2. Mount important directories as volumes to prevent data loss

3. Consider keeping data directories outside the git repository entirely

4. When using VS Code DevContainers:
- The entire repository is typically mounted in the container
- Changes inside the container affect the host repository
- Running git commands inside the container is equivalent to running them on the host
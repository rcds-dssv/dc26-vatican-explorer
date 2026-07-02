This directory can hold example pre-commit hooks scripts.  

To use a given script, place it in your `.git/hooks/pre-commit/` directory (which is only local and not tracked by GitHub, hence this directory here to store them).

**Note:** `git commit --no-verify` skips all hooks. Useful when you're mid-work and committing a checkpoint.

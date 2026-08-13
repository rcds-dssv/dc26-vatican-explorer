This directory can hold example pre-commit hooks scripts.

To use a given script, copy it to `.git/hooks/pre-commit` (a single file, not a directory — `.git/hooks/` is only local and not tracked by GitHub, hence this directory here to store them) and make it executable:

```bash
cp -i precommit_hooks_examples/run-ruff.sh .git/hooks/pre-commit
chmod +x .git/hooks/pre-commit
```

Git only recognizes a hook named exactly `pre-commit` (no extension) directly inside `.git/hooks/`; it will not run a `pre-commit/` directory or an unnamed/non-executable script.

**Note:** `git commit --no-verify` skips all hooks. Useful when you're mid-work and committing a checkpoint.

#!/bin/bash

# Run ruff on committed file

# possible modifications: could run ruff check --fix $STAGED so it auto-fixes what it can and only fails on things it can't fix automatically. Just be aware you'd then need to re-stage those files with git add.

# Get only staged Python files
#    diff --cached --name-only, lists only the files staged for the current commit
#   --diff-filter=ACM limits to Added, Copied, and Modified files (skips deleted files, which ruff can't check anyway).
STAGED=$(git diff --cached --name-only --diff-filter=ACM | grep '\.py$')

if [ -z "$STAGED" ]; then
  exit 0
fi

# Run ruff on only those files
ruff check $STAGED

if [ $? -ne 0 ]; then
  echo "ruff found issues. Fix them or use --no-verify to skip."
  exit 1
fi
#!/bin/sh

display_usage() {
    echo "Usage: ./check_changes.sh [BASEBRANCH]"
    echo "For all files that are different between the current branch and BASEBRANCH, lint them with Flake8 and run MyPy on them."
    echo ""
    echo "With no BASEBRANCH, compare current branch to dev."
}

if [ $# -eq 0 ]; then
    base_branch="dev"
elif [ $# -gt 1 ]; then
    display_usage
    exit 1
else
    base_branch=$1
fi

changed_files=$(git diff --name-only --diff-filter=AM "$(git merge-base ${base_branch} HEAD)" | grep -E '\.py$')

if [ -z "$changed_files" ]; then
    # Exit if there are no Python files to check.
    echo "No Python files modified on this branch yet."
    exit 0
fi

flake8 $changed_files
mypy $changed_files

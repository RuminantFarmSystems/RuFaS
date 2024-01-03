#!/bin/sh

display_usage() {
    echo "Usage: ./cleanup.sh [BASEBRANCH]"
    echo "Lint all files different between current branch and BASEBRANCH with Flake8."
    echo ""
    echo "With no BASEBRANCH, compare current branch to main."
}

if [ $# -eq 0 ]; then
    base_branch="main"
elif [ $# -gt 1 ]; then
    display_usage
    exit 1
else
    base_branch=$1
fi

changed_files=$(git diff --name-only --diff-filter=AM "$(git merge-base ${base_branch} HEAD)" | grep -E '\.py$')

if [ -z "$changed_files" ]; then
    # Exit if there are no Python files to lint
    echo "No Python files modified on this branch yet."
    exit 0
fi

flake8 $changed_files

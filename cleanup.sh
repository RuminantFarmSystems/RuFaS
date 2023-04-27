#!/bin/sh

display_usage() {
    echo "Usage: ./runflake8onbranch.sh [BASEBRANCH]"
    echo "Lint all files different between current branch and BASEBRANCH with Flake8."
    echo ""
    echo "With no BASEBRANCH, compare current branch to master."
}

if [ $# -eq 0 ]; then
    base_branch="master"
elif [ $# -gt 1 ]; then
    display_usage
    exit 1
else
    base_branch=$1
fi

flake8 $(git diff --name-only $(git merge-base ${base_branch} HEAD) | grep -E '\.py$')
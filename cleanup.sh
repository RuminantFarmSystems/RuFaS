# !/bin/bash
# git status -s collects all modified files both committed and uncommitted. -s gives the shortened version just listing the files
# grep -E part filters out all the files from the git status that don't end with .py
# cut -c 4- makes sure to capture just the names of the files so erases out all the git status info

# flake8 $(git status -s | grep -E '\.py$' | cut -c 4-)
flake8 $(git diff --name-only | grep -E '\.py$')
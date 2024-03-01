#! /bin/bash

# Pass the mypy error count as an argument
if [ $# -eq 0 ]; then
  echo "Please provide the mypy error count as an argument"
  exit 1
fi
error_count=$1
echo "Mypy errors: $error_count"

# Assign color accordingly
if [ "$error_count" -eq 0 ]; then
  color="brightgreen"
elif [ "$error_count" -le 5 ]; then
  color="green"
elif [ "$error_count" -le 10 ]; then
  color="yellowgreen"
elif [ "$error_count" -le 20 ]; then
  color="yellow"
elif [ "$error_count" -le 30 ]; then
  color="orange"
else
  color="red"
fi
echo "$color"

# Build the URL for badge
message="${error_count}%20errors"
badge_url="https://img.shields.io/badge/mypy-${message}-${color}"
markdown_str="![Mypy](${badge_url})"
echo "$markdown_str"

# Update the mypy badge in README.md using sed
sed -i "s|\[\!\[Mypy\]\(.*\)\]|\[${markdown_str}\]|" ./README.md

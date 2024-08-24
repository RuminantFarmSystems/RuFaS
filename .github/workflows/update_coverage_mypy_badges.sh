#! /bin/bash

# Parse coverage report JSON file to find the coverage percentage
coverage_percentage=$( jq -r '.totals.percent_covered_display' ./.github/workflows/coverage.json )
echo "Coverage: $coverage_percentage%"

# Assign color for coverage badge
coverage_color=$(case $((coverage_percentage)) in
  ([0-9]|[1-3][0-9])  echo "red";;          # 0 %  - 39 %
  ([4-5][0-9])        echo "orange";;       # 40%  - 59 %
  (6[0-9]|7[0-4])     echo "yellow";;       # 60%  - 74 %
  (7[5-9]|8[0-9])     echo "yellowgreen";;  # 75%  - 89 %
  (9[0-4])            echo "green";;        # 90%  - 94 %
  (9[5-9]|100)        echo "brightgreen";;  # 95%  - 100%
  esac)
echo "Coverage color: $coverage_color"

# Build the URL for coverage badge
coverage_markdown_str="![Coverage](https://img.shields.io/badge/Coverage-${coverage_percentage}%25-${coverage_color})"
echo "Coverage badge: $coverage_markdown_str"

# Get the mypy error count
error_count=$(cat mypy_current_branch_error_count.txt)
echo "Mypy errors: $error_count"

# Assign color for mypy badge
if [ "$error_count" -eq 0 ]; then
  mypy_color="brightgreen"
elif [ "$error_count" -le 5 ]; then
  mypy_color="green"
elif [ "$error_count" -le 10 ]; then
  mypy_color="yellowgreen"
elif [ "$error_count" -le 20 ]; then
  mypy_color="yellow"
elif [ "$error_count" -le 30 ]; then
  mypy_color="orange"
else
  mypy_color="red"
fi
echo "Mypy color: $mypy_color"

# Build the URL for mypy badge
mypy_message="${error_count}%20errors"
mypy_badge_url="https://img.shields.io/badge/Mypy-${mypy_message}-${mypy_color}"
mypy_markdown_str="![Mypy](${mypy_badge_url})"
echo "Mypy badge: $mypy_markdown_str"

# Update the coverage and mypy badges in README.md using sed
sed -i "s|\[\!\[Coverage\]\(.*\)\]|\[${coverage_markdown_str}\]|" ./README.md
sed -i "s|\[\!\[Mypy\]\(.*\)\]|\[${mypy_markdown_str}\]|" ./README.md
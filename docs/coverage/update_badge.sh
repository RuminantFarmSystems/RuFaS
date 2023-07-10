#! /bin/bash

# Parse coverage report JSON file to find the coverage percentage
coverage_percentage=$( jq -r '.totals.percent_covered_display' ./docs/coverage/coverage.json )
echo "$coverage_percentage"

# Assign color accordingly
color=$(case $((coverage_percentage)) in
  ([0-9]|[1-3][0-9])  echo "red";;          # 0 %  - 39 %
  ([4-5][0-9])        echo "orange";;       # 40%  - 59 %
  (6[0-9]|7[0-4])     echo "yellow";;       # 60%  - 74 %
  (7[5-9]|8[0-9])     echo "yellowgreen";;  # 75%  - 89 %
  (9[0-4])            echo "green";;        # 90%  - 94 %
  (9[5-9]|100)        echo "brightgreen";;  # 95%  - 100%
  esac)
echo "$color"

# Build the URL for badge
markdown_str="![Coverage](https://img.shields.io/badge/coverage-${coverage_percentage}%-${color})"
echo "$markdown_str"

# Update the coverage badge in README.md using sed
sed -i "s|\[\!\[Coverage\]\(.*\)\]|\[${markdown_str}\]|" ./README.md

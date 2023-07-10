#! /bin/bash

coverage_percentage=$( jq -r '.totals.percent_covered_display' ./docs/coverage/coverage.json )
echo "$coverage_percentage"

color=$(case $((coverage_percentage)) in
  ([0-9]|1[0-5]) echo "red";;
  (1[6-9]|[2-3][0-9]|4[0-5]) echo "orange";;
  (4[6-9]|5[0-9]|6[0-5]) echo "yellow";;
  (6[6-9]|7[0-9]|80) echo "yellowgreen";;
  (8[1-9]|9[0-3]) echo "green";;
  (9[4-9]|100) echo "brightgreen";;
  *) echo "grey"
esac)

echo "$color"


markdown_str="![Coverage](https://img.shields.io/badge/coverage-${coverage_percentage}-${color})"
echo "$markdown_str"

sed -i "s|\[\!\[Coverage\]\(.*\)\]|\[\!\[Coverage\]\(${markdown_str}\)\]|" ./README.md
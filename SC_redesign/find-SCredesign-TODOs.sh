#!/bin/bash
# Script to list all lines in files of the SC_redesign folder that contain TODOs
# usage: bash find-SCredesign-TODOs.sh

# list all lines that match the "todo" string, regardless of case, and include the line number.
grep todo "$(dirname "$0")" --ignore-case --recursive --word-regexp --line-number --exclude=*.pyc \
  --exclude=find-SCredesign-TODOs.sh --color

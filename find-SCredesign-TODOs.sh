#!/bin/bash
# usage: bash find-SCredesign-TODOs.sh
# run from MASM directory
grep todo SC_redesign/ --ignore-case --recursive --word-regexp --line-number --exclude=*.pyc

#!/bin/sh
set -e -x
git stash
git checkout submission
git reset --hard master
git push -f origin submission
git checkout master
git stash pop

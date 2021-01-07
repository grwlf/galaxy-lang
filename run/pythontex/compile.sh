#!/bin/sh

set -e -x

F="$1"

pdflatex -interaction=nonstopmode "$F"
pythontex "$F"
pdflatex -interaction=nonstopmode "$F"

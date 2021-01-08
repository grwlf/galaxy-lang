#!/bin/sh

set -e -x

F="$1"

pdflatex --shell-escape -interaction=nonstopmode "$F"
pythontex "$F"
pdflatex --shell-escape -interaction=nonstopmode "$F"

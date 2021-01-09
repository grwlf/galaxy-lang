#!/bin/sh

set -e -x

F="$1"
FD="`dirname $F`/`basename $F .tex`_de.tex"

pdflatex --shell-escape -interaction=nonstopmode "$F"
pythontex "$F"
pdflatex --shell-escape -interaction=nonstopmode "$F"

# depythontex \
#   "$F" \
#   --listing=minted \
#   --preamble='linenos,escapeinside=!!,breaklines,breakafter=0123456789-' \
#   > "$FD" || true

# pdflatex --shell-escape -interaction=nonstopmode "$FD"

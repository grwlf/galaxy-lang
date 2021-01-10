#!/bin/sh

set -e -x

F="$1"

rm -rf pythontex-files-* || true
pdflatex --shell-escape -interaction=nonstopmode "$F"
pythontex "$F"
pdflatex --shell-escape -interaction=nonstopmode "$F" || true
pdflatex --shell-escape -interaction=nonstopmode "$F"

# FD="`dirname $F`/`basename $F .tex`_de.tex"
# depythontex \
#   "$F" \
#   --listing=minted \
#   --preamble='linenos,escapeinside=!!,breaklines,breakafter=0123456789-' \
#   > "$FD" || true

# pdflatex --shell-escape -interaction=nonstopmode "$FD"

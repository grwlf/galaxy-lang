#!/bin/sh
export PYTHONPATH=`pwd`/src:$PYTHONPATH
exec python app/main.py "$@"

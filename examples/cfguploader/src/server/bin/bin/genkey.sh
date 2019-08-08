#! /bin/bash
root=$(cd `dirname $0` && pwd)
python $root/../lib/genidentity.py "$1" "$2"


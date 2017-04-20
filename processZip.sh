#!/bin/bash
#set -euxo pipefail
set -x

f=$1

rm -fr tmp
unzip $f -d tmp 1>/dev/null

entityCount=`find tmp -name '*.a1' | xargs grep -h ^T| wc -l`
relationCount=`find tmp -name '*.a2' | xargs grep -h ^E | grep -vF ":E" | wc -l`
fileCount=`find tmp/ -name '*.txt' | wc -l`

echo "$f $fileCount $relationCount $entityCount"


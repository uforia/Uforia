#!/usr/bin/env bash

FILE="$1"
PREFIX="$2"

if [ -z "$FILE" ]; then
    echo "Command-line arguments: $0 <file> <prefix>."
    exit 1
fi
if [ -z "$PREFIX" ]; then
    echo "Command-line arguments: $0 <file> <prefix>."
    exit 1
fi

tail -n +2 "$FILE" | split -l 1 - "$PREFIX"
for splitfile in "$PREFIX_"*
do
    head -n 1 "$FILE" > tmp_file
    cat "$splitfile" >> tmp_file
    mv -f tmp_file "$splitfile"
done

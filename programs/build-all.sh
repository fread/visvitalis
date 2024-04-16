#!/usr/bin/bash

mkdir -p out

for file in *.s;
do
    ../assembler/assembler.py $file -o out/${file/%.s/.o}
done

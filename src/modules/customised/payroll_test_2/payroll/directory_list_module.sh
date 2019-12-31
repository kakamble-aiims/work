#!/bin/bash
i=0
array=("lal")
for d in */ ; do
    array[$i]="$d"
    (( i++ ))
done

for dr in "${array[@]}" ; do
    cd $dr
    pwd
    cd ..
done

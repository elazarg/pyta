#!/bin/bash
pyexec=python3
cd ../src
function run {
	$pyexec pyta.py $1
}

for i in $(find ../examples/*.py)
do
	echo -----------
	echo $i
	echo -----------
	run $i
done
cd ../scripts
#!/bin/bash
echo 'Blanking screens (putting them into sleep and keeping it that way) by unfa 2023-10-19'
echo 'Press ANY KEY to STOP'

echo -n "3."
sleep 1
echo -n "2."
sleep 1
echo -n "1."
sleep 1
echo -n "BLANK"
sleep 1

blank(){
	while [ 1==1 ]; do
		xset dpms force off
		sleep 1
	done
}

anykey(){
	read -n 1 -s -r -p ''
}

blank &
PID_BLANK=$!
anykey
kill $PID_BLANK



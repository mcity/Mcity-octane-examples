#!/bin/bash

# to run this obu generator, use the command:
# ./make-followers.sh [id-1] [id-2] [id-3] ... [id-x]
# for as many obus as you want. IDs have to be 8 digits long, use alpha-numeric characters

# ctrl+c won't kill all your processes. you have to run ./kill-all-followers to do that

echo "starting up all followers"

for arg in "$@"
do
    ./follow-path.py aroundMCity.json --v2x-type vehicle --speed 10 --octane-server http://localhost:5000 --auth reticulatingsplines --id $arg &
done

echo "all followers started!"

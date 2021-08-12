#!/bin/bash

echo "starting up all followers"

for arg in "$@"
do
    ./follow-path.py aroundMCity.json --v2x-type vehicle --speed 10 --octane-server http://localhost:5000 --auth reticulatingsplines --id $arg &
done

echo "all followers started!"

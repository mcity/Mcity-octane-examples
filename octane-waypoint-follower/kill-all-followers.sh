#!/bin/bash

# run just using ./kill-all-followers.sh

echo "killing all followers"

pkill -9 -f follow-path.py

echo "killed all followers"

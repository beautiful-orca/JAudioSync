#!/bin/bash

host=$(hostname)
tmux new-session -d -s $host
tmux send-keys -t $host "cd JAudioSync" C-m
#tmux send-keys -t $host "python3 JAudioSync.py" C-m
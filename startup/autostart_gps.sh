#!/bin/bash

tmux new-session -d -s jas
tmux send-keys -t jas "cd JAudioSync" C-m
#tmux send-keys -t jas "python3 JAudioSync.py" C-m
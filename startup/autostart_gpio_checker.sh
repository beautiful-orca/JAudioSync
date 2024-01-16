#!/bin/bash
host=$(hostname)
GPIO_PIN=26
GPIO_VALUE=$(gpio read $GPIO_PIN)
tmux new-session -d -s $host
tmux send-keys -t $host "cd JAudioSync" C-m
sleep 2
if [ "$GPIO_VALUE" -eq 1 ]; then
    # GPIO is high, start your service
    tmux send-keys -t $host "python3 JAudioSync.py" C-m
fi
#!/bin/bash
timedatectl set-ntp true
sudo systemctl restart systemd-timesyncd
sleep 10
sudo timedatectl set-ntp false


tmux new-session -d -s jas
tmux send-keys -t jas "cd JAudioSync" C-m
#tmux send-keys -t jas "python3 JAudioSync.py" C-m

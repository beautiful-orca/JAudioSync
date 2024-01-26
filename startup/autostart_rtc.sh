#!/bin/bash
timedatectl set-ntp true
sudo systemctl restart systemd-timesyncd
sleep 10
sudo timedatectl set-ntp false
sudo hwclock -systohc

host=$(hostname)
tmux new-session -d -s $host
tmux send-keys -t $host "cd JAudioSync" C-m
#tmux send-keys -t $host "python3 JAudioSync.py" C-m

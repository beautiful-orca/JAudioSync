#!/bin/bash
echo "Installing packages and services for JAudioSync"

sudo apt update
sudo apt upgrade -y
sudo apt -y install git-all tmux python3 python3-pygame python3-mutagen python3-apscheduler

utas_source="./startup/update_time_autostart.service"
utas_dest="/etc/systemd/system/update_time_autostart.service"
agcs_source="./startup/autostart_gpio_checker.sh"
agcs_dest="/usr/local/bin/autostart_gpio_checker.sh"

cp -f  "$utas_source" "$utas_dest"
cp -f  "$agcs_source" "$agcs_dest"
sudo systemctl enable update_time_autostart.service

sudo sed -i 's/^#NTP=/NTP=pool.ntp.org/' /etc/systemd/timesyncd.conf

echo "Do you use a USB DAC audio interface? (yes/no)"
read dac

asound_dac_source="./startup/.asoundrc_dac"
asound_snd_source="./startup/.asoundrc_snd"
asound_dest="~/.asoundrc"

if [ "$dac" == "yes" ]; then
    echo "blacklist snd_bcm2835" | sudo tee /etc/modprobe.d/alsa-blacklist.conf > /dev/null
    cp -f "$asound_dac_source" "$asound_dest"
else
    sudo rm -f /etc/modprobe.d/alsa-blacklist.conf
    cp -f "$asound_snd_source" "$asound_dest"
fi

echo "Finished. Please restart."
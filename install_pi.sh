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


read -p "Do you use a USB DAC audio interface? (yes/no): " dac_opt

asound_dac_source="./startup/.asoundrc_dac"
asound_snd_source="./startup/.asoundrc_snd"
asound_dest="$HOME/.asoundrc"

if [ "$dac_opt" == "yes" ]; then
    echo "blacklist snd_bcm2835" | sudo tee /etc/modprobe.d/alsa-blacklist.conf > /dev/null
    cp -f "$asound_dac_source" "$asound_dest"
elif [ "$dac_opt" == "no" ]; then
    sudo rm -f /etc/modprobe.d/alsa-blacklist.conf
    cp -f "$asound_snd_source" "$asound_dest"
else
    echo "Invalid input. Please enter 'yes' or 'no'."
    exit 1
fi

sudo raspi-config nonint do_i2c 0

read -p "Do you use DS3231 RTC (yes/no): " rtc_opt

config_file="/boot/config.txt"
rtc_param="dtoverlay=i2c-rtc,ds3231"

if [ "$rtc_opt" == "yes" ]; then
    if grep -q "$rtc_param" "$config_file"; then
        echo "RTC is acative."
    else
        echo "$rtc_param" | sudo tee -a "$config_file"
        echo "RTC activated."
    fi
elif [ "$rtc_opt" == "no" ]; then
    if grep -q "$rtc_param" "$config_file"; then
        sed -i "/$rtc_param/d" "$config_file"
        echo "RTC deactivated."
    else
        echo "RTC not active."
    fi
else
    echo "Invalid input. Please enter 'yes' or 'no'."
    exit 1
fi


echo "Finished. Please restart."
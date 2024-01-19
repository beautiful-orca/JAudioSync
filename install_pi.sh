#!/bin/bash
echo "Installing packages and services for JAudioSync"

sudo apt update
sudo apt upgrade -y
sudo apt -y install git-all tmux python3 python3-pygame python3-mutagen python3-apscheduler

read -p "Do you use a USB DAC audio interface? (yes/no): " dac_opt

asound_dac_source="./startup/.asoundrc_dac"
asound_snd_source="./startup/.asoundrc_snd"
asound_dest="$HOME/.asoundrc"

if [ "$dac_opt" == "yes" ]; then
    echo "blacklist snd_bcm2835" | sudo tee /etc/modprobe.d/alsa-blacklist.conf > /dev/null
    sudo cp -f "$asound_dac_source" "$asound_dest"
elif [ "$dac_opt" == "no" ]; then
    sudo rm -f /etc/modprobe.d/alsa-blacklist.conf
    sudo cp -f "$asound_snd_source" "$asound_dest"
else
    echo "Invalid input. Please enter 'yes' or 'no'."
    exit 1
fi

read -p "Do you use DS3231 RTC (yes/no), no for gps: " rtc_opt

as_source="./startup/autostart.service"
as_dest="/etc/systemd/system/autostart.service"

ast_source="./startup/autostart.sh"
ast_rtc_source="./startup/autostart_rtc.sh"
ast_gps_source="./startup/autostart_gps.sh"
ast_dest="/usr/local/bin/autostart.sh"

config_file="/boot/config.txt"
rtc_param="dtoverlay=i2c-rtc,ds3231"

if [ "$rtc_opt" == "yes" ]; then
    sudo systemctl enable systemd-timesyncd
    sudo sed -i '/^#NTP=/s/.*/NTP=pool.ntp.org/' /etc/systemd/timesyncd.conf
    sudo sed -i '/^NTP=/s/.*/NTP=pool.ntp.org/' /etc/systemd/timesyncd.conf
    sudo raspi-config nonint do_i2c 0
    echo "$rtc_param" | sudo tee -a "$config_file"
    sudo cp -f  "$ast_rtc_source" "$ast_dest"
    sudo cp -f  "$as_source" "$as_dest"

    sudo apt -y remove fake-hwclock
    sudo update-rc.d -f fake-hwclock remove
    sudo systemctl disable fake-hwclock
    sed -i '/if \[ -e \/run\/systemd\/system \] ; then/,/fi/ s/^/#/' /lib/udev/hwclock-set
    echo "*/5 * * * * /path/to/hwclock -hctosys" | crontab -

    echo "RTC activated."
elif [ "$rtc_opt" == "no" ]; then
    sudo systemctl enable systemd-timesyncd
    sudo sed -i '/^#NTP=/s/.*/NTP=pool.ntp.org/' /etc/systemd/timesyncd.conf
    sudo sed -i '/^NTP=/s/.*/NTP=pool.ntp.org/' /etc/systemd/timesyncd.conf
    sudo raspi-config nonint do_i2c 1
    sed -i "/$rtc_param/d" "$config_file"
    sudo cp -f  "$ast_source" "$ast_dest"
    sudo cp -f  "$as_source" "$as_dest"

    sudo apt install fake-hwclock
    sudo update-rc.d -f fake-hwclock defaults
    sudo systemctl enable fake-hwclock
    sed -i '/if \[ -e \/run\/systemd\/system \] ; then/,/fi/ s/^#//' /lib/udev/hwclock-set
    (crontab -l | grep -v "/path/to/hwclock -hctosys" ; echo) | crontab -

    echo "RTC deactivated."
    

    read -p "Do you use gps module (yes/no): " gps_opt
    if [ "$gps_opt" == "yes" ]; then
        sudo raspi-config nonint do_serial_hw 0
        sudo raspi-config nonint do_serial_cons 1

        sudo apt install gpsd gpsd-clients python-gps chrony
        sudo systemctl disable systemd-timesyncd --now
        sudo cp -f  "$ast_gps_source" "$ast_dest"


    
    
    fi
else
    echo "Invalid input. Please enter 'yes' or 'no'."
    exit 1
fi

sudo systemctl enable autostart.service

echo "Finished. Please restart."

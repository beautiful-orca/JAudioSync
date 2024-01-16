## JAudioSync  
Project is in **very early developement!** :cowboy_hat_face:  

Play a (m3u8) playlist of music in perfect sync on multiple devices.  
Syncing NTP time over wireless network first and then start pygame.mixer.music playback at exact choosen time (using apscheduler), which then doesn't need network anymore because it depends on system clock. RTC (RealTimeClock) helps keeping correct time.  

### Use Cases
[Critical Mass Bike Ride](https://en.wikipedia.org/wiki/Critical_Mass_(cycling))
   - Multiple speakers distributed on Cargo Bikes and trailers
   - Moving with changing conditions, mostly network independant solution
   - [CM Duisburg](https://criticalmass.in/duisburg)
#### Similar Projects
- [Claudiosync](https://claudiosync.de/)
    - Announced plans to publish soon

### How to use
- `git clone https://github.com/beautiful-orca/JAudioSync.git`
    - cloning dev branch: `git clone -b dev https://github.com/beautiful-orca/JAudioSync.git`
- `cd JAudioSync`
    - get updates: `git pull origin dev`

`python JAudioSync.py [-h] [-t 18:55:00] [-p 0 | res] [-l | -playlist_name Playlist]`
    - `-t`, optional: Time the playback should be scheduled today in the format hh:mm:ss, default: in 5-20 seconds (at 5,20,35,50)  
    - `-p`, optional: Start track number in playlist, 0 - (number of tracks), or "res" to resume from last played track, default: starting from 0  
    - `-l`, optional flag: Fast-loading last saved playlist (when present), default: reading new playlist from storage
    - `-playlist_name`, optional: Pick custom playlist name in ./Music, default: "Playlist"

### Example
```
python3 JAudioSync.py
pygame 2.5.2 (SDL 2.28.2, Python 3.11.5)
Hello from the pygame community. https://www.pygame.org/contribute.html
Playlist: ./Music/Playlist.m3u8 | Tracks: 3 | Runtime: 0:00:34
Starting with track: 0 , at: 2024-01-13 00:02:05
Playing: Oymaldonado Bluesy Rock Guitar 3 Enveloped Reverbed - Timbre
At: 2024-01-13 00:02:05.000790
Playing: Remix of Reverendblack Rev Loops Metal Guitar 12 Brighter Buzzier Old 1 - Timbre
At: 2024-01-13 00:02:16.000901
Playing: Tweaked Version of Fastdash99s freesound 484749 - Timbre
At: 2024-01-13 00:02:28.000729
Playlist finished playing.
```

### ToDo, Future Ideas, Challenges and Notes
- music playback on Pi 3A+ and Pi 3B+ is in sync when starting with synced time
    - Software clock drifts after a while without network connection
    - audible when both sources are close to each other
    - RTC is nessessary
- Add DS3231 Real Time Clock Module to avoid system clock drift when without network connection to NTP Server
    - [https://www.berrybase.de/ds3231-real-time-clock-modul-fuer-raspberry-pi](https://www.berrybase.de/ds3231-real-time-clock-modul-fuer-raspberry-pi)
    - Enable I2C and rtc:
        - config.txt: dtparam=i2c_arm=on ; i2c-dev ; dtoverlay=i2c-rtc,ds3231
        - add to install_pi.sh
```
if ! grep -q "dtparam=i2c_arm=on" /boot/config.txt; then
    echo "dtparam=i2c_arm=on" | sudo tee -a /boot/config.txt
fi

if ! grep -q "dtoverlay=i2c-dev" /boot/config.txt; then
    echo "dtoverlay=i2c-dev" | sudo tee -a /boot/config.txt
fi
```
```
#!/bin/bash

config_file="/boot/config.txt"
rtc_overlay="dtoverlay=i2c-rtc,ds3231"

# Check if the line is already present in the config.txt file
if grep -q "$rtc_overlay" "$config_file"; then
    echo "The line '$rtc_overlay' is already present in $config_file."
    read -p "Do you want to remove it? (yes/no): " choice
    if [[ $choice == "yes" ]]; then
        sudo sed -i "/$rtc_overlay/d" "$config_file"
        echo "Line removed. Rebooting..."
        sudo reboot
    else
        echo "No changes made."
    fi
else
    read -p "The line '$rtc_overlay' is not present. Do you want to add it? (yes/no): " choice
    if [[ $choice == "yes" ]]; then
        echo "$rtc_overlay" | sudo tee -a "$config_file"
        echo "Line added. Rebooting..."
        sudo reboot
    else
        echo "No changes made."
    fi
fi
```



- NTP
    - internet ntp sync via mobile phone wifi hotspot
    - `sudo timedatectl timesync-status`
    - `timedatectl status`

- install_pi.sh , install all dependencies and services
    - `update_time_autostart.service`
    - `autostart_gpio_checker.sh`

- update_time_autostart.service , systemd service, runs after wifi is connected

- Autostart based on jumper on GPIO
    - autostart script if GPIO 26 is connected to ground with a jumper
autostart_gpio_checker.sh
```
tmux new-session -d -s $host
tmux send-keys -t $host "cd JAudioSync" C-m
    tmux send-keys -t $host "python3 JAudioSync.py"C-m
```


- control script(s)
    - python parallel-ssh
    - jas0, jas1, ...; host parameter `-h 0`
- tmux session is present if using autostart
    - otherwise create a new session with name=hostname
    - create_session.py
    - `sshpass -p secret ssh jas@($host).local 'tmux new-session -d -s $host'`
- keep script running
    - install sshpass on controlling device
    - with tmux the terminal session can be kept up

- start.py
    - `sshpass -p secret ssh jas@($host).local 'tmux send-keys -t $host "python3 JAudioSync.py" C-m'`
    - add custom options parsing
- stop.py
    - pkill: `"pkill -2 -f JAudioSync.py"`
    - `sshpass -p secret ssh jas@($host).local 'tmux send-keys -t $host  C-c'`
- resume.py
    - `sshpass -p secret ssh jas@($host).local 'tmux send-keys -t $host "python3 JAudioSync.py -p res -l" C-m'`
- volume.py -i [- v 25 | -up | -dn]
    - i = interface [Audio | Headphones]
        - USB Audio or analog
    - -v volume % ; set PCM 25%
    - -up = volume up by ; set PCM 5%+
    - -dn = volume down by ; set PCM 5%-
    - `sshpass -p secret ssh jas@$host.local "amixer -c "$i" set PCM ($v)%($c)"`
- manually view session:
    - view_session.sh
    - `sshpass -p secret ssh jas@($host).local`
    - `tmux attach-session -t $host`

- GPS Time Sync (5-10€ per gps module)
    - [https://www.haraldkreuzer.net/en/news/using-gps-module-set-correct-time-raspberry-pi-3-a-plus-without-network](https://www.haraldkreuzer.net/en/news/using-gps-module-set-correct-time-raspberry-pi-3-a-plus-without-network)
    - [https://austinsnerdythings.com/2021/09/29/millisecond-accurate-chrony-ntp-with-a-usb-gps-for-12-usd/](https://austinsnerdythings.com/2021/09/29/millisecond-accurate-chrony-ntp-with-a-usb-gps-for-12-usd/)
- Maybe rename project
- Move git to privacy friendly hoster?


### Based on
- [Python 3](https://www.python.org/)
- [pygame](https://www.pygame.org/docs/ref/mixer.html)
- [mutagen](https://mutagen.readthedocs.io/)
- [apscheduler](https://apscheduler.readthedocs.io/en/latest/)
- [tmux](https://github.com/tmux/tmux/wiki)

### Install and use on Raspberry Pi
(Other Linux installs similar, use e.g. balena-etcher to flash and config files on flash memory)  
- Install Pi OS Lite 64bit with Raspberry Pi Imager
    - Set hostname jas
    - set username and password, jas:secret  
    - Wifi config: Hotspot:jassecret
    - Set locale  
    - Enable ssh password authentication
- Place mp3 and m3u8 fies in [./Music/](./Music/)  
    - make sure music is mp3 and is tagged with title, artist(, comment)  and has the property length
    - Use VLC (or similar music player) to create a "m3u8" playlist, eg. Playlist.m3u8, in [./Music/](./Music/)

- Configure system
    - `ssh jas@jas.local`
    - `sudo apt -y install git`
    - `git clone https://github.com/beautiful-orca/JAudioSync.git`
    - `cd JAudioSync`
    - `./install_pi.sh`
        - choose USB Audio or headphones
    - optional push prepared Music folder: 
        - `exit` first
        - `sshpass -p secret scp -r ~/Music jas@jas.local:/home/jas/JAudioSync/Music`
        - back to: `ssh jas@jas.local`
    - `sudo raspi-config`
        - Set hostname jas0 , jas1, jas3, ...
        - change Wifi
    - Install jumper cable GPIO 26 to ground
    - `sudo reboot now`
    
### Distribute prepared image?
- flash with imager
- copy mp3 and playlist to folder
- `ssh jas@jas.local`
- optional push prepared Music folder: 
        - `exit` first
        - `sshpass -p secret scp -r ~/Music jas@jas.local:/home/jas/JAudioSync/Music`
        - back to: `ssh jas@jas.local`
- `sudo raspi-config`
    - Set hostname jas0 , jas1, jas3, ...
- Optional: USB Audio ./audio_config-md
- Install jumper cable GPIO 26 to ground
    - `sudo reboot now`

### Thanks
- All components and their developers
- Chris
- People of Hackspace Duisburg: [https://www.space47.ruhr/](https://www.space47.ruhr/)
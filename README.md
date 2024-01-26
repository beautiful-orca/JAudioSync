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
- raspi-config & noint: https://github.com/raspberrypi/documentation/blob/develop/documentation/asciidoc/computers/configuration/raspi-config.adoc
- Volume Control with buttons
    - GPIO, controls amixer
- NTP
    - internet ntp sync via mobile phone wifi hotspot
    - `sudo timedatectl timesync-status`
    - `timedatectl status`
    - dmesg -T | grep clock
- Add DS3231SN Real Time Clock Module to avoid system clock drift when without network connection to NTP Server
    - [https://www.berrybase.de/ds3231-real-time-clock-modul-fuer-raspberry-pi](https://www.berrybase.de/ds3231-real-time-clock-modul-fuer-raspberry-pi)
    - [https://learn.adafruit.com/adding-a-real-time-clock-to-raspberry-pi/set-rtc-time](https://learn.adafruit.com/adding-a-real-time-clock-to-raspberry-pi/set-rtc-time)
    
    - https://github.com/skiselev/rpi_rtc_ds3231
    - https://spellfoundry.com/docs/setting-up-the-real-time-clock-on-raspbian-jessie-or-stretch/


- install_pi.sh
    - !!! chmod +x scripts
    - install all dependencies and services
    - copy and enable services
        - `autostart.service`
            - runs after wifi is connected
            - executes bash script
        - `autostart.sh`
            - sets up time
            - initiates tmux session
            - starts JAudioSync
    - in case of rtc option
        - enable I2C
        - enable rtc module: dtoverlay=i2c-rtc,ds3231
        - disable fake-hwclock:
        - comment out lines in /lib/udev/hwclock-set
        - add cronjob setting system time from RTC every 5 minutes `hwclock -hctosys`
    - in case of no rtc
        - disable I2C
        - disable rtc module: dtoverlay=i2c-rtc,ds3231
        - re-enable fake-hwclock:
        - uncomment in `/lib/udev/hwclock-set`
        - disable cronjob hwclock
    - in case of gps:
        - ntpd waits for gps fix (at least 1) until it accepts time


- GPS Time Sync (5-10€ per gps module, u-blox NEO-6M, better with pps pin)
    - **NOT FINISHED**
    - u-blox NEO-6M via UART but without PPS pin
    - VCC to Pin 1, which is 3.3v
    - TX to Pin 10, which is RX (GPIO15)
    - RX to Pin 8, Which is TX (GPIO14)
    - Gnd to Pin 6, which is Gnd
    - timedatectl set-ntp true
    - enable serial port: `sudo raspi-config nonint do_serial_hw 0`
    - Turn Off the debug Serial Console: `sudo raspi-config nonint do_serial_cons 1`
    - `dtoverlay=disable-bt`
        - if ! grep -q "^dtoverlay=disable-bt$" /boot/config.txt; then
            - echo "dtoverlay=disable-bt" | sudo tee -a /boot/config.txt
    - `sudo systemctl disable hciuart --now`
    - `sudo systemctl disable bluetooth.service --now`
    - `sudo apt install gpsd gpsd-clients python-gps chrony`
    - `cat /dev/ttyAMA0`
    - `stty -F /dev/ttyAMA0 9600`
    - `sudo gpsd /dev/ttyAMA0 -F /var/run/gpsd.sock`
    - `cgps -s`
    - `sudo nano /etc/default/gpsd`
        ```
        # Start the gpsd daemon automatically at boot time
        START_DAEMON="true"
        DEVICES="/dev/ttyAMA0"
        GPSD_OPTIONS="-n -G"
        ```
    - `sudo systemctl enable gpsd --now`
    - disable conflicting timesyncd
        - `sudo systemctl disable systemd-timesyncd --now`

    - chrony.conf /etc/chrony/chrony.conf
    - `pool pool.ntp.org iburst`
    - `allow all`
    - `refclock SHM 0 refid NMEA precision 1e-3 offset 0.125`
    - `refid GPS precision 1e-3 offset 0.125`
    - `offset 0.0424 delay 0.2`
    - `poll 2 offset 0.128`
    - `stratum 0`

    - `sudo systemctl enable chrony --now`

    - `sudo systemctl status chronyd`
    - `chronyc sources`
    - `chronyc tracking`
    - `sudo chronyc makestep` forces your system clock to immediately sync with the Chrony time



- Hardware control via GPIO buttons
    - Volume up
    - Volume Down
    - Start
    - Stop

- network control script(s)
    - python parallel-ssh (https://pypi.org/project/parallel-ssh/)
    - 
    - jas0, jas1, ...; host parameter `-h 0`
- tmux session is present if using autostart
    - otherwise create a new session
    - create_session.py
    - if not tmux has-session -t $host
    - `sshpass -p secret ssh -o StrictHostKeyChecking=no jas@$host.local 'tmux new-session -d -s $host'`
    - `sshpass -p secret ssh -o StrictHostKeyChecking=no jas@jas0.local 'tmux new-session -d -s jas0'`
- keep script running
    - install sshpass on controlling device
    - with tmux the terminal session can be kept up
- start.py
    - add custom options parsing
    - `sshpass -p secret ssh -o StrictHostKeyChecking=no jas@$host.local 'tmux send-keys -t $host "python3 JAudioSync.py" C-m'`
    - `sshpass -p secret ssh -o StrictHostKeyChecking=no jas@jas0.local 'tmux send-keys -t jas0 "python3 JAudioSync.py" C-m'`
- stop.py
    - pkill: `"pkill -2 -f JAudioSync.py"`
    - `sshpass -p secret ssh -o StrictHostKeyChecking=no jas@$host.local 'tmux send-keys -t $host  C-c'`
- resume.py
    - `sshpass -p secret ssh -o StrictHostKeyChecking=no jas@$host.local 'tmux send-keys -t $host "python3 JAudioSync.py -p res -l" C-m'`
- volume.py -i [- v 25 | -up | -dn]
    - i = interface [Audio | Headphones]
        - USB Audio or analog
    - -v volume % ; set PCM 25%
    - -up = volume up by ; set PCM 5%+
    - -dn = volume down by ; set PCM 5%-
    - `sshpass -p secret ssh -o StrictHostKeyChecking=no jas@$host.local "amixer -c "$i" set PCM ($v)%($c)"`
- manually view session:
    - view_session.sh
    - `sshpass -p secret ssh -o StrictHostKeyChecking=no jas@$host.local`
    - `tmux attach-session -t $host`
    - `sshpass -p secret ssh -o StrictHostKeyChecking=no jas@jas0.local`
    - `tmux attach-session -t jas0`




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


sudo rpi-update

- Configure system
    - `ssh jas@jas.local`
    - `sudo apt -y install git-all`
    - `git clone https://github.com/beautiful-orca/JAudioSync.git`
    - `cd JAudioSync`
    - `./install_pi.sh`
        - choose USB Audio or headphones
        - choose RTc,GPS or fake clock 
    - optional push prepared Music folder: 
        - `exit` first
        - `sshpass -p secret scp -r ~/Music jas@jas.local:/home/jas/JAudioSync/Music`
        - back to: `ssh jas@jas.local`
    - Set hostname jas0 , jas1, jas3, ...
        - `sudo raspi-config nonint do_hostname <hostname>`
    - change Wifi: `sudo raspi-config nonint do_wifi_ssid_passphrase <ssid> <passphrase>`
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
- Set hostname jas0 , jas1, jas3, ...
        - `sudo raspi-config nonint do_hostname <hostname>`
    - change Wifi: `sudo raspi-config nonint do_wifi_ssid_passphrase <ssid> <passphrase>`
- Optional: USB Audio ./audio_config-md or run `./install_pi.sh`
- Install jumper cable GPIO 26 to ground
- `sudo reboot now`

### Thanks
- All components and their developers
- Chris
- People of Hackspace Duisburg: [https://www.space47.ruhr/](https://www.space47.ruhr/)
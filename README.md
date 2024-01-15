## JAudioSync  
Project is in **very early developement!** :cowboy_hat_face:  

Play a (m3u8) playlist of music in perfect sync on multiple devices.  
Syncing NTP time over wireless network first and then start pygame.mixer.music playback at exact choosen time (using apscheduler), which then doesn't need network anymore because it depends on system clock. RTC (RealTimeClock) helps keeping correct time.  

**Example music with different license is present at ./Music at the moment**  
- See [./Music/music_license.md](./Music/music_license.md)  

### Use Cases
[Critical Mass Bike Ride](https://en.wikipedia.org/wiki/Critical_Mass_(cycling))
   - Multiple speakers distributed on Cargo Bikes and trailers
   - Moving with changing conditions which make a network dependant solution hard or costly to implement (Mesh Wifi problems)
   - [CM Duisburg](https://criticalmass.in/duisburg)

### Similar Projects
- [Claudiosync](https://claudiosync.de/)
    - Announced plans to publish soon

### How to use (dev version)
- `git clone -b dev https://github.com/beautiful-orca/JAudioSync.git`
- `cd JAudioSync`
    - get updates: `git pull origin dev`
- Place mp3 fies in [./Music/](./Music/)  
    - make sure they are mp3 and are properly tagged title, artist and have the property length
- Use VLC (or similar music player) to create a "m3u8" playlist, eg. party.m3u8, in [./Music/](./Music/)  
- Run: `python JAudioSync.py [-h] [-t 18:55:00] [-p 0 | res] [-l | -playlist_name Playlist]`
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
- NTP Server on leader
    - chrony
    - sync from pool.ntp.org over mobile phone wifi hotspot with internet
- forcing resync on `timedatectl`:
    - `sudo systemctl restart systemd-timesyncd`

- keep script running
    - install sshpass
    - with tmux the terminal session can be kept up
    - `sshpass -p secret ssh jas@jasl.local "tmux new-session -d -s jasl 'cd JAudioSync && python3 JAudioSync.py'"`
    - `sshpass -p secret ssh jas@jasm1.local "tmux new-session -d -s jasm1 'cd JAudioSync && python3 JAudioSync.py'"`
    - manually view session: 
    - `sshpass -p secret ssh jas@jasl.local` `tmux attach-session -t jasl`
    - `sshpass -p secret ssh jas@jasm1.local` `tmux attach-session -t jasm1`
- Stopping music playback on demand
    - `sshpass -p secret ssh jas@jasl.local 'tmux send-keys -t jasl "pkill -2 -f JAudioSync.py" C-m'`
    - `sshpass -p secret ssh jas@jasm1.local 'tmux send-keys -t jasm1 "pkill -2 -f JAudioSync.py" C-m'`
- Volume control
    - `alsamixer` (interactive shell), identify audio cards
    - amixer -c "Audio" set PCM 25%
    - use "Headphones" when using analog audio

    - `sshpass -p secret ssh jas@jasl.local "amixer -c "Audio" set PCM 25%"`
    - `sshpass -p secret ssh jas@jasl.local "amixer -c "Audio" set PCM 25%"`


- Server and Client model
    - Auto-discovery, based on hostnames (server "leader" scans for hostnames "member(n)")
    - Command control server, "leader" copies comands it gets and distributes them to every member by discovered hostnames
- Common interface: distribute commands to all clients at the same time
   - hostname pattern, eg jasm1, jasm2, jasm(n)

- GPS Time Sync (5-10€ per gps module)
    - [https://www.haraldkreuzer.net/en/news/using-gps-module-set-correct-time-raspberry-pi-3-a-plus-without-network](https://www.haraldkreuzer.net/en/news/using-gps-module-set-correct-time-raspberry-pi-3-a-plus-without-network)
    - [https://austinsnerdythings.com/2021/09/29/millisecond-accurate-chrony-ntp-with-a-usb-gps-for-12-usd/](https://austinsnerdythings.com/2021/09/29/millisecond-accurate-chrony-ntp-with-a-usb-gps-for-12-usd/)
- Maybe rename project
- Move git to privacy friendly hoster?






### Dependencies needed to be installed
I am using Python 3.11.5 in a anaconda venv  
- [pygame](https://www.pygame.org/docs/ref/mixer.html)
- [mutagen](https://mutagen.readthedocs.io/)
- [apscheduler](https://apscheduler.readthedocs.io/en/latest/)
- tmux

### Install and use on (multiple) Raspberry Pi 3 
(Other Linux installs similar, use e.g. balena-etcher to flash and config files on flash memory)  
- Install Pi OS Lite 64bit with Raspberry Pi Imager  
    - 3 B+ as leader and 3 A+ as member in my case
    - Set hostname for "leader" and "member[n]" jasl, jasm1
    - set username and password, jas:secret  
    - Wifi config with internet access or use wired internet for install and update  
    - Set locale  
    - Enable ssh password authentication  
    - `ssh jas@jasl.local`
    - `sudo apt update && sudo apt upgrade`
    - `sudo apt install git tmux python3 python3-pygame python3-mutagen python3-apscheduler`
    
### Configuration in live system
- Wifi configuration: 
    - use `sudo raspi-config`
    - or `/etc/wpa_supplicant/wpa_supplicant.conf`
- Set Hostname in live system (single word, without domain ".local")
    - use `sudo raspi-config`
    - `ping hostname.local`

### Audio Setup (USB Audio)
- Test sounds: `speaker-test -c 1`
- Find USB-AUDIO device: `aplay -l`
```
**** List of PLAYBACK Hardware Devices ****
card 0: Headphones [bcm2835 Headphones], device 0: bcm2835 Headphones [bcm2835 Headphones]
card 1: Audio [KM_B2 Digital Audio], device 0: USB Audio [USB Audio]
card 2: vc4hdmi [vc4-hdmi], device 0: MAI PCM i2s-hifi-0 [MAI PCM i2s-hifi-0]
```

#### (optional) Disable onboard analog audio
- Avoid conflicts for default device when using USB Audio
`sudo nano /etc/modprobe.d/alsa-blacklist.conf`  
```
# Add
blacklist snd_bcm2835
```

##### Stereo with USB Audio as Default Audio Device
`sudo nano ~/.asoundrc`
```
pcm.!default {
   type hw
   card Audio
}

ctl.!default {
   type hw
   card Audio
}
```

#### Two Mono Channels
`~/.asoundrc`
```
pcm.!default {
    type plug
    slave.pcm "mono"
}

pcm.mono {
    type route
    slave.pcm "hw:Audio"
    ttable.0.0 0.5  # Left channel to left output
    ttable.1.0 0.5  # Right channel to left output
    ttable.0.1 0.5  # Left channel to right output
    ttable.1.1 0.5  # Right channel to right output
}

ctl.mono {
    type hw
    card Audio
}
```

#### Mono Channel (left)
```
pcm.!default {
    type plug
    slave.pcm "mono"
}

pcm.mono {
    type route
    slave.pcm "hw:Audio"
    ttable.0.0 1  # Left channel to left channel
    ttable.1.0 1  # Right channel to left channel
}

ctl.mono {
    type hw
    card Audio
}
```

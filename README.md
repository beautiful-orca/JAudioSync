## JAudioSync  
Project is in **very early developement!** :cowboy_hat_face:  

Play a (m3u8) playlist of music in perfect sync on multiple devices.  
Syncing NTP time over wireless network first and then start playback at exact choosen time (using apscheduler), which then doesn't need network anymore because it depends on system clock.  
Using pygame.mixer.sound to load music files into Ram memory before playback to reduce delay and variability.  


**Sadly it is too resource heavy to run on Raspberry Pi 3A+ 1G**


### How to use  
- `git clone https://github.com/beautiful-orca/JAudioSync.git`  
- `cd JAudioSync`  
- Place music fies in [./Music/](./Music/)  
- Using VLC (or similar music player) to create a playlist of songs in [./Music/](./Music/)  
    - Save Playlist as [./Music/Playlist.m3u8](./Music/Playlist.m3u8)  
- Run: `python JAudioSync.py [-h] [--s_time 18:55:00] [--pl_pos 1|resume]`
    - `--s_time`, optional: Time the playback should be scheduled today in the format hh:mm:ss, default: now + 10 seconds  
    - `--pl_pos`, optional: Start track number in playlist, 1 - [number of tracks], or "resume" to resume from last played track, default: starting from 1  
    - `--tz` , optional: Choose timezone, default: system timezone

**Example music with different license is present at ./Music at the moment**  
- See [./Music/music_license.md](./Music/music_license.md)  

#### Example output:
```
python JAudioSync.py --s_time 22:21:50 --pl_pos resume

pygame 2.5.2 (SDL 2.28.2, Python 3.11.5)
Hello from the pygame community. https://www.pygame.org/contribute.html
Resuming with track 2.
Start Playback at:  2024-01-01 22:21:50 , Playlist Posotion:  2
./Music/102818__timbre__remix-of-41967__reverendblack__rev_loops_metal_guitar_12_brighter_buzzier-old1.mp3
loaded:  22:21:49.012694
length:  0:00:11
playing:  22:21:50.000653
./Music/485980__timbre__tweaked-version-of-fastdash99s-freesound-484749.mp3
loaded:  22:22:01.027689
length:  0:00:10
playing:  22:22:02.000608
Playlist finished playing
```

### Dependencies needed to be installed  
I am using Python 3.11.5 with JupyterLab in a Anaconda venv  
```
pip install pygame
pip install pydub
pip install apscheduler
```


### ToDo, Future Ideas, Challenges and Notes  

- GPS Time Sync
    - https://www.haraldkreuzer.net/en/news/using-gps-module-set-correct-time-raspberry-pi-3-a-plus-without-network

- Reduce resource demand
    - BlockingScheduler
    - prepare playlist to dataframe
    - pygame.mixer.init [samplerate/resample]
    - pygame.mixer.music [streammusic from file] 

- Before playing (silent): "ALSA underrun occurred" on Raspberry Pi 3B
- Stopping music playback on demand (local possible, remote needs to be implemented)
- Common interface: distribute commands to all clients at the same time
   - ssh password auth, common password to add all hostnames found with pattern, eg jasm1, jasm2, jasmn
   - key auth from phone (Termux) to leader to control without need for password
- Additional flags for Music path and Playlist path
- Maybe rename project
- Move git to privacy friendly hoster?

- Using Central Wifi Access Point, Raspi hotspot/mesh or mobile Wifi hotspot?  
    - What if every playing device (raspi) is connected to a mobile phone wifi hotspot to sync ntp.org time seperately
    - Tailscale VPN connection for network commands (script control)
- Server and Client model  
    - Auto-discovery, based on hostnames (server "leader" scans for hostnames "member[n]")  
    - NTP Server on leader
        - might sync time from internet (mobile [phone] wifi hotspot with 4G internet), de.pool.ntp.org
    - Command control server, "leader" copies comands it gets and distributes them to every member by discovered hostnames  
- Add DS3231 Real Time Clock Module to avoid system clock drift when without network connection to NTP Server  
    - System clock drift needs testing (without network connection) 
    - [https://www.berrybase.de/ds3231-real-time-clock-modul-fuer-raspberry-pi](https://www.berrybase.de/ds3231-real-time-clock-modul-fuer-raspberry-pi)
    - Can a GPS clock be a viable option?


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
    - `sudo apt install git python-pygame python-pydub python-apscheduler`
    - `python --version`
    - `cd ~/`
    - `git clone https://github.com/beautiful-orca/JAudioSync.git`
    - `cd JAudioSync`
    
### Configuration in live system
- Wifi configuration: 
    - use `sudo raspi-config`
- Set Hostname in live system (single word, without domain ".local")
    - use `sudo raspi-config`
    - `ping hostname.local`  
- Volume control
    - amixer -c 1 set Speaker 50%
    - alsamixer (interactive shell)

### Audio Setup

#### Test sounds
```
wget https://www.kozco.com/tech/piano2.wav
aplay piano2.wav
```

`speaker-test -c 1`

#### Find USB-AUDIO device:
`aplay -l`

```
**** List of PLAYBACK Hardware Devices ****
card 0: Headphones [bcm2835 Headphones], device 0: bcm2835 Headphones [bcm2835 Headphones]
card 1: Audio [KM_B2 Digital Audio], device 0: USB Audio [USB Audio]
card 2: vc4hdmi [vc4-hdmi], device 0: MAI PCM i2s-hifi-0 [MAI PCM i2s-hifi-0]
```

#### Disable onboard audio (not needed)  
`sudo nano /etc/modprobe.d/alsa-blacklist.conf`  
```
# Add
blacklist snd_bcm2835
```

##### Set USB Audio as Default Audio Device
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


#### Mono Channel (optional)
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

### Use Cases
[Critical Mass Bike Ride](https://en.wikipedia.org/wiki/Critical_Mass_(cycling))
   - Multiple speakers distributed on Cargo Bikes and trailers
   - Moving with changing conditions which make a network dependant solution hard or costly to implement (Mesh Wifi problems)
   - [CM Duisburg](https://criticalmass.in/duisburg)

### Similar Projects
- [Claudiosync](https://claudiosync.de/)
    - Announced plans to publish soon

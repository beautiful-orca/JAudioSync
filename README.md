## JAudioSync  
Project is in **very early developement!** :cowboy_hat_face:  

Play a (m3u8) playlist of music in perfect sync on multiple devices.  
Syncing NTP time over wireless network first and then scheduling pygame.mixer.music playback at exact choosen time (using apscheduler), which then doesn't need network anymore because it depends on system clock. RTC (RealTimeClock) helps keeping correct time.  
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

### How to use  
- `git clone https://github.com/beautiful-orca/JAudioSync.git`  
- `cd JAudioSync`  
- Place music fies in [./Music/](./Music/)  
- Using VLC (or similar music player) to create a playlist of songs in [./Music/](./Music/)  
    - Save Playlist as [./Music/Playlist.m3u8](./Music/Playlist.m3u8)  
- Run: `python JAudioSync.py [-h] [-t 18:55:00] [-p 1 | res]`
    - `-t`, optional: Time the playback should be scheduled today in the format hh:mm:ss, default: at half or full minute  
    - `-p`, optional: Start track number in playlist, 0 - [number of tracks], or "res" to resume from last played track, default: starting from 0  

### Example
```
python3 JAudioSync.py --p 2
pygame 2.5.2 (SDL 2.28.2, Python 3.11.5)
Hello from the pygame community. https://www.pygame.org/contribute.html
Starting with Track: 2
Playlist:
                                                Path            LoadTime           StartTime
2  ./Music/485980__timbre__tweaked-version-of-fas... 2024-01-10 22:51:48 2024-01-10 22:51:49
Playing: ./Music/485980__timbre__tweaked-version-of-fastdash99s-freesound-484749.mp3
At: 2024-01-10 22:51:49.001153
Playlist finished playing.
```


### ToDo, Future Ideas, Challenges and Notes  
- Reduce resource demand
    - pygame.mixer.init (samplerate/resampling necessary?)
    - Raspberry Pi 3B+ 1GB cannot prepare playlist in 1.5 minutes
 
- Add DS3231 Real Time Clock Module to avoid system clock drift when without network connection to NTP Server  
    - System clock drift needs testing (without network connection) 
    - [https://www.berrybase.de/ds3231-real-time-clock-modul-fuer-raspberry-pi](https://www.berrybase.de/ds3231-real-time-clock-modul-fuer-raspberry-pi)
- GPS Time Sync
    - [https://www.haraldkreuzer.net/en/news/using-gps-module-set-correct-time-raspberry-pi-3-a-plus-without-network](https://www.haraldkreuzer.net/en/news/using-gps-module-set-correct-time-raspberry-pi-3-a-plus-without-network)

- Stopping music playback on demand (local possible, remote needs to be implemented)
- Common interface: distribute commands to all clients at the same time
   - ssh password auth, common password to add all hostnames found with pattern, eg jasm1, jasm2, jasm(n)
   - key auth from phone (Termux) to leader to control without need for password
- Maybe rename project
- Move git to privacy friendly hoster?

- Using Central Wifi Access Point, Raspi hotspot/mesh or mobile Wifi hotspot?  
    - What if every playing device (raspi) is connected to a mobile phone wifi hotspot to sync ntp.org time seperately
    - Tailscale VPN connection for network commands (script control)
- Server and Client model  
    - Auto-discovery, based on hostnames (server "leader" scans for hostnames "member(n)")  
    - NTP Server on leader
        - might sync time from internet (mobile (phone) wifi hotspot with 4G internet), de.pool.ntp.org
    - Command control server, "leader" copies comands it gets and distributes them to every member by discovered hostnames  

### Dependencies needed to be installed  
I am using Python 3.11.5 in a anaconda venv  
- [pygame](https://www.pygame.org/docs/ref/mixer.html)
- [pydub](https://github.com/jiaaro/pydub)
   - [needs ffmpeg](http://www.ffmpeg.org/)
- [apscheduler](https://apscheduler.readthedocs.io/en/latest/)
- [pandas](https://pandas.pydata.org/)

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
    - `sudo apt install git ffmpeg python3-pygame python3-pydub python3-apscheduler python3-pandas`
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

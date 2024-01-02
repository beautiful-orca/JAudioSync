## JAudioSync  
Project is in **very early developement!** :cowboy_hat_face:  

Play a (m3u8) playlist of music in perfect sync on multiple devices.  
Syncing NTP time over wireless network first and then start playback at exact choosen time (using apscheduler), which then doesn't need network anymore because it depends on system clock.  
Using pygame.mixer.sound to load music files into Ram memory before playback to reduce delay and variability.  


Currently broken because of unfinished argparse rewrite.  

### How to use (may not be up to date)  
- `git clone https://github.com/beautiful-orca/JAudioSync.git`  
- `cd JAudioSync`  
- Place music fies in [./Music/](./Music/)  
- Using VLC (or similar music player) to create a playlist of songs in [./Music/](./Music/)  
    - Save Playlist as [./Music/Playlist.m3u8](./Music/Playlist.m3u8)  
- Run: `JAudioSync.py [-h] [--s_time 18:55:00] [--pl_pos 1|resume]`  
    - `--s_time`, optional: Time the playback should be scheduled today in the format hh:mm:ss, default: now + 5 seconds  
    - `--pl_pos`, optional: Start track number in playlist, 1 - [number of tracks], or "resume" to resume from last played track, default: starting from 1 (write .resume not ready to use)   

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

- Resume after stopping from last played track number
    - needs to write a file after (ending?) playback (or after loading)   
- Stopping music playback on demand (local possible, remote needs to be implemented)
- Common interface: distribute commands to all clients at the same time
   - Alternatively copy prewritten commands (for each client IP) to Termux (needs ssh key auth), e.g ssh 192.10.10.2 python JAudioSync.py "18:55:00"  
- Volume control
- Additional flags for Music path and playlist path
- Maybe rename project
- Move git to privacy friendly hoster?

### Install and use on (multiple) Raspberry Pi 3 
#### (Other Linux installs similar, use e.g. balena-etcher to flash and config files on flash memory)  
- Install Pi OS Lite 64bit with Pi Image Flasher
    - set username and password
    - Wifi config with internet access or use wired internet for install and update  
    - Set hostname "leader" and "member[n]"
- Using Central Wifi Access Point, Raspi hotspot or mobile Wifi hotspot?  
    - Wifi configuration: /etc/wpa_supplicant/wpa_supplicant.conf  
- Set Hostname in live system (single word, without domain ".local")
    Replace in: `sudo nano /etc/hostname`
    `sudo nano /etc/hosts` 
    (find line that starts with 127.0.1.1 and update the hostname to match the one you set)
    `sudo reboot`
    `ping hostname.local`
- Server and Client model  
    - Auto-discovery, based on hostnames (server "leader" scans for hostnames "member[n]"?  
    - NTP Server on leader
        - might sync time from internet (mobile [phone] wifi hotspot with 4G internet), de.pool.ntp.org
    - Command control server, "leader" copies comands it gets and distributes them to every member by discovered hostnames  
- Audio Setup - USB DAC  
    - ALSA is standard on Raspi?  
    - Optional: combine audio channels to left channel mono  
- Add DS3231 Real Time Clock Module toavoid system clock drift when without network connection to NTP Server  
    - System clock drift needs testing (without network connection) 
    - [https://www.berrybase.de/ds3231-real-time-clock-modul-fuer-raspberry-pi](https://www.berrybase.de/ds3231-real-time-clock-modul-fuer-raspberry-pi)
    - Can a GPS clock be a viable option?
- What if every playing device (raspi) is connected to a mobile phone wifi hotspot to sync ntp.org time seperately
    - Tailscale VPN connection for network commands (script control)

### Use Cases
[Critical Mass Bike Ride](https://en.wikipedia.org/wiki/Critical_Mass_(cycling))
   - Multiple speakers distributed on Cargo Bikes and trailers
   - Moving with changing conditions which make a network dependant solution hard or costly to implement (Mesh Wifi problems)
   - [CM Duisburg](https://criticalmass.in/duisburg)

### Similar Projects
- [Claudiosync](https://claudiosync.de/)
    - Announced plans to publish soon
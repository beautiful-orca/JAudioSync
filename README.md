## JAudioSync  
Project is in **very early developement!** :cowboy_hat_face:  

Play a (m3u8) playlist of music in perfect sync on multiple devices.  
Syncing NTP time over wireless network first and then start playback at exact choosen time (using apscheduler), which then doesn't need network anymore because it depends on system clock.  
Using pygame.mixer.sound to load music files into Ram memory before playback to reduce delay and variability.  


Currently broken because of unfinished argparse rewrite.  

### How to use     
- `git clone https://github.com/beautiful-orca/JAudioSync.git`  
- `cd JAudioSync`  
- Place music fies in [./Music/](./Music/)  
- Using VLC (or similar music player) to create a playlist of songs in [./Music/](./Music/)  
    - Save Playlist as [./Music/Playlist.m3u8](./Music/Playlist.m3u8)  
- Run: `python JAudioSync.py 18:55:00`  
    - Argument is the time the playlist should start playing  
    - **For debug purposes, the time is assumed now + 2 seconds**  

**Example music with different license is present at ./Music at the moment**  
- See [./Music/music_license.md](./Music/music_license.md)  


### Dependencies needed to be installed  
I am using Python 3.11.5 with JupyterLab in a Anaconda venv  
```
pip install pygame
pip install pydub
pip install apscheduler
```


### ToDo / Future Ideas  
- Stopping music playback on demand (local possible, remote needs to be implemented)
- Start (resume after stopping) playback from any number of track in "playlist" (checking if number is playlist item)

- Common interace: distribute commands to all clients at the same time
   - Alternatively copy prewritten commands (for each client IP) to Termux (needs ssh key auth), e.g ssh 192.10.10.2 python JAudioSync.py "18:55:00"  
- Volume control

### Install and use on (multiple) Raspberry Pi 3 (Other Linux installs similar, use e.g. balena-etcher to flash and config files on flash memory)  
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


### Similar Projects
- [Claudiosync](https://claudiosync.de/)
    - Announced plans to publish soon
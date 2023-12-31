# JAudioSync  
Project is in **very early developement!** :cowboy_hat_face:  

Play a (m3u8) playlist of music in perfect sync on multiple devices.  
Syncing NTP time over wireless network first and then start playback at exact choosen time, which then doesn't need network anymore because it depends on system clock.  
Using pygame.mixer.sound to load music files into Ram memory to reduce delay and variability of playback.  

## How to use  

- `git clone https://github.com/beautiful-orca/JAudioSync.git`  
- `cd JAudioSync`  
- Place music fies in `./Music/`  
- Using VLC (or similar music player) to create a playlist of songs in `./Music/`  
    - Save Playlist as `./Music/Playlist.m3u8`  
- Run: `python JAudioSync.py 18:55:00`  
    - Argument is the time the playlist should start playing  
    - **For debug purposes, the time is assumed now + 2 seconds**  

**Example music with different license is present at ./Music at the moment**  
- See `./Music/music_license.md`  


### Dependencies needed to be installed  
```
pip install pygame
pip install pydub
pip install apscheduler
```



## Install and use on (multiple) Raspberry Pi 3  
- Install Pi OS Lite 64bit  
- Set different Hostnames  
- Connect to internet for install and update  
- Using Central Wifi Access Point, Raspi hotspot or mobile Wifi hotspot?  
- Server and Client model?  
    - Auto-discovery?  
    - NTP Server  
    - Command control server

## ToDo / Future Ideas  
- Stopping music playback on demand (local possible, remote needs to be implemented)
- Start (resume after stopping) playback from any number of track in "playlist" (checking if number is playlist item)

- Common interace: distribute commands to all clients at the same time
   - Alternatively copy prewritten commands (for each client IP) to Termux (needs ssh key auth), e.g ssh 192.10.10.2 python JAudioSync.py "18:55:00"  
- Volume control


### Similar Projects
- [Claudiosync](https://claudiosync.de/)
    - Announced plans to publish soon
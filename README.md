# JAudioSync
Project is in **very early developement!**

Play a (m3u8) playlist of music in perfect sync on multiple devices.
Syncing NTP time over wireless network first and then start playback at exact choosen time, which then doesn't need network anymore because it depends on system clock.
Using pygame.mixer.sound to load music files into Ram memmory to reduce delay and variability of playback.

- Place music fies in "./Music/"
- Using VLC to create a playlist of songs in "./Music"
- Save Playlist as "./Music/Playlist.m3u8"

## How to run:

JupyterLab with JAudioSync.ipynb is used for developement

In the future you can run:
```
python JAudioSync.py
```

### Dependencies needed to be installed:
```
pip install pygame
pip install pydub
pip install apscheduler
```

## Future Ideas

- Choose start time from calling script: python JAudioSync.py "18:55:00"
- Stopping music playback inbetween
- Resume playback from any number of track in "playlist"

- Common interace: distribute commands to all clients at the same time
   - Alternatively copy prewritten commands (for each client IP) to Termux (needs ssh key auth), e.g ssh 192.10.10.2 python JAudioSync.py "18:55:00"


# JAudioSync
Project is in **very early developement!** :cowboy_hat_face:

Play a (m3u8) playlist of music in perfect sync on multiple devices.
Syncing NTP time over wireless network first and then start playback at exact choosen time, which then doesn't need network anymore because it depends on system clock.
Using pygame.mixer.sound to load music files into Ram memory to reduce delay and variability of playback.

- Place music fies in "./Music/"
- Using VLC to create a playlist of songs in "./Music"
- Save Playlist as "./Music/Playlist.m3u8"

**Example music with different license is present at ./Music at the moment**  

## How to run:
```
python JAudioSync.py 18:55:00
```
Where the argument is the time the playlist should start playing
For debug purposes, the time is assumed now + 2 seconds

### Dependencies needed to be installed:
```
pip install pygame
pip install pydub
pip install apscheduler
```

## Future Ideas

- Stopping music playback on demand (local possible, remote needs to be implemented)
- Resume playback from any number of track in "playlist" (checking if number is playlist item)

- Common interace: distribute commands to all clients at the same time
   - Alternatively copy prewritten commands (for each client IP) to Termux (needs ssh key auth), e.g ssh 192.10.10.2 python JAudioSync.py "18:55:00"


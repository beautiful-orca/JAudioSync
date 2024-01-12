import sys
import re
import os
import pickle
import argparse
from functools import partial
from pygame import mixer
from urllib.parse import unquote
from datetime import timedelta, datetime
import time
from mutagen.mp3 import MP3
from math import ceil
from apscheduler.schedulers.blocking import BlockingScheduler

def get_next_time():    
    second = datetime.now().second
    minute = datetime.now().minute
    
    if 0 <= second <= 15:
        next_time = datetime.now()
        next_time = next_time.replace(second=20,  microsecond=0).strftime('%H:%M:%S')
        return next_time
    if 16 <= second <= 30:
        next_time = datetime.now()
        next_time = next_time.replace(second=35,  microsecond=0).strftime('%H:%M:%S')
        return next_time
    if 30 < second <= 45:
        next_time = datetime.now()
        next_time = next_time.replace(second=50,  microsecond=0).strftime('%H:%M:%S')
        return next_time
    if 45 < second <= 59:
        next_time = datetime.now() + timedelta(minutes=1)
        next_time = next_time.replace(second=5,  microsecond=0).strftime('%H:%M:%S')
        return next_time

# Validate hh:mm:ss time format for t input
def validate_time_string(time_str):
    # Regular expression to validate the format hh:mm:ss
    pattern = re.compile(r'^([01]?[0-9]|2[0-3]):[0-5][0-9]:[0-5][0-9]$')
    if not pattern.match(time_str):
        raise argparse.ArgumentTypeError(f"Invalid time format: {time_str} , use valid hh:mm:ss")
    return time_str

# Convert time string to a datetime object with date of today
def string_to_datetime(time_string):
    format_str = "%H:%M:%S"
    today_date = datetime.now().date()
    datetime_str = f"{today_date} {time_string}"
    dt = datetime.strptime(datetime_str, f"%Y-%m-%d {format_str}")
    return dt

def read_resume_position():
    try:
        with open('resume_pos.pkl', 'rb') as file:
            global resume_pos
            resume_pos = pickle.load(file)
        return resume_pos
    except FileNotFoundError:
        return 0
    
# Try to convert pl_pos string to int and check if valid playlist position
def validate_pl_pos(pos):
    if pos.lower() == "res":
        resume_pos = read_resume_position()
        print(f"Resuming with track {resume_pos}.")
        return resume_pos
    try:
        pos = int(pos)
        return pos
    except ValueError:
        raise argparse.ArgumentTypeError(f"Invalid playlist position: {pos}.")

def validate_playlist_name(pl_str):
    pattern = re.compile(r'^[a-zA-Z0-9_-]+$')
    if not pattern.match(pl_str):
        raise argparse.ArgumentTypeError(f"Invalid Plalist name: {pl_str} , use [a-zA-Z0-9_-] without extension")
    playlist_name = os.path.join("./Music/", pl_str + ".m3u8")
    return playlist_name

def is_mp3_file(file_path):
    return file_path.lower().endswith(".mp3")

# Read .m3u8 playlist file and extract music file paths to "playlist"
def read_playlist(playlist_file):
    try:
        with open(playlist_file, mode='r') as file:
            lines = file.readlines()
            # Filter out comments and empty lines, clean, add ./Music
        path = [os.path.join("./Music", unquote(line.strip())) for line in lines if line.strip() and not line.startswith('#') and is_mp3_file(line.strip())]
        if path is None:
            raise ValueError(f"Playlist {playlist_file} is empty.")
        return path
    except FileNotFoundError:
        print(f'The playlist file {playlist_file} is not present.')
    except Exception as e:
        print(f'An error occurred: {e}')

def load_p_t_a_l():
    try:
        with open('path.pkl', 'rb') as file:
            path = pickle.load(file)
    except FileNotFoundError:
        raise FileNotFoundError("Playlist cannot be loaded, run without '-l'")
    try:
        with open('title.pkl', 'rb') as file:
            title = pickle.load(file)
    except FileNotFoundError:
        raise FileNotFoundError("Playlist cannot be loaded, run without '-l'")
    try:
        with open('artist.pkl', 'rb') as file:
            artist = pickle.load(file)
    except FileNotFoundError:
        raise FileNotFoundError("Playlist cannot be loaded, run without '-l'")
    try:
        with open('length.pkl', 'rb') as file:
            length = pickle.load(file)
    except FileNotFoundError:
        raise FileNotFoundError("Playlist cannot be loaded, run without '-l'")
    return path, title, artist, length

def create_t_a_l(path):
    title = []
    artist = []
    length = []
    
    for file_path in path:
        audio = MP3(file_path)
    
        if 'TIT2' in audio and 'TPE1' in audio:
            t = audio['TIT2'][0]
            a = audio['TPE1'][0]
        else:
            t = path
            a = ""
        rounded_length = ceil(audio.info.length)
        l = timedelta(seconds=rounded_length)

        title.append(t)
        artist.append(a)
        length.append(l)
    
    return title, artist, length
    
def load_playlist(l, playlist_name):
    if l:
        try:
            # pickle load path, title, artist, length
            path, title, artist, length = load_p_t_a_l()
            return path, title, artist, length
        
        except:
            path = read_playlist(playlist_name)
            #create variables title, artist, length
            title, artist, length = create_t_a_l(path)
            return path, title, artist, length
    else:
        path = read_playlist(playlist_name)
        #create variables title, artist, length
        title, artist, length = create_t_a_l(path)
        return path, title, artist, length

def load_lts_sts_et():
    try:
        with open('lts.pkl', 'rb') as file:
            lts = pickle.load(file)
    except FileNotFoundError:
        raise FileNotFoundError("Playlist cannot be loaded, run without '-l'")
    try:
        with open('sts.pkl', 'rb') as file:
            sts = pickle.load(file)
    except FileNotFoundError:
        raise FileNotFoundError("Playlist cannot be loaded, run without '-l'")
    try:
        with open('et.pkl', 'rb') as file:
            et = pickle.load(file)
    except FileNotFoundError:
        raise FileNotFoundError("Playlist cannot be loaded, run without '-l'")
    return lts, sts, et

def create_lts_sts_et(length, pl_start, pl_len): #pl_start 1 pl_len 3
    print(f"pl_len: {pl_len}")
    lts = []
    sts = []
    for _ in range(0,pl_start):
        lts.append(timedelta(seconds=0))
        sts.append(timedelta(seconds=0))
    for i in range(pl_start, pl_len):
        if i == pl_start:
            lts.append(timedelta(seconds=0))
            sts.append(timedelta(seconds=1))
        elif i > pl_start:
            t = sts[i-1] + length[i-1]  # JAudioSync.py -p 1 sts[i-1] list index out of range
            lts.append(t)
            sts.append(t + timedelta(seconds=1))
    et = sts[-1] + length[-1]
    return lts, sts, et

def load_runtime_matrix(l, length, pl_start, pl_len):
    if l:
        try:
            lts, sts, et = load_lts_sts_et()
            return lts, sts, et
        
        except:
            lts, sts, et = create_lts_sts_et(length, pl_start, pl_len)
            return lts, sts, et
    else:
        lts, sts, et =  create_lts_sts_et(length, pl_start, pl_len)
        return lts, sts, et

# Load a music file with pygame.mixer.music
def load_music(path, title, artist):
    global sound
    sound = mixer.Sound(path)
    # mixer.music.load(path)
    print(f"Playing: {title} - {artist}")
    #mixer.music.set_volume(0.9)

# Start playback of music from RAM memory
def play_music():
    sound.play()
    #mixer.music.play()
    print(f"At: {datetime.now()}")
    while mixer.get_busy() == True:
        continue
    global pl_pos
    pl_pos += 1

def save_p_t_a_l(path, title, artist, length ):
    with open('path.pkl', 'wb') as file:
        pickle.dump(path, file)
    with open('title.pkl', 'wb') as file:
        pickle.dump(title, file)
    with open('artist.pkl', 'wb') as file:
        pickle.dump(artist, file)
    with open('length.pkl', 'wb') as file:
        pickle.dump(length, file)

def save_resume_pos(resume_pos):
    with open('resume_pos.pkl', 'wb') as file:
        pickle.dump(resume_pos, file)

def save_lts_sts_et(lts, sts, et):
    with open('lts.pkl', 'wb') as file:
        pickle.dump(lts, file)
    with open('sts.pkl', 'wb') as file:
        pickle.dump(sts, file)
    with open('et.pkl', 'wb') as file:
        pickle.dump(et, file)

def end(path, title, artist, length, lts, sts, et):
        print("Playlist finished playing.")
        # pickle save path, title, artist, length
        save_p_t_a_l(path, title, artist, length)
        save_lts_sts_et(lts, sts, et)
        scheduler.shutdown(wait=False)
        mixer.quit()
    
if __name__ == "__main__":
    next_time = get_next_time()
    timezone = time.tzname[time.localtime().tm_isdst]
    resume_pos = 0
    
    # Create ArgumentParser object
    parser = argparse.ArgumentParser(description="""
                                    Play a (m3u8) playlist of music in perfect sync on multiple devices.  
                                    Syncing NTP time over wireless network first and then start pygame.mixer.music
                                    playback at exact choosen time (using apscheduler),which then doesn't need network
                                    anymore because it depends on system clock.
                                    RTC (RealTimeClock) helps keeping correct time. 
                                    
                                    usage: JAudioSync.py [-h] [-t 18:55:00] [-p 0 | res] [-l | -playlist_name Playlist]
                                    """
                                    )
    
    # Add optional arguments
    parser.add_argument('-t', type=validate_time_string, help='Time the playback should be scheduled today in the format hh:mm:ss, default: in 5-20 seconds (at 5,20,35,50)', nargs='?', const=next_time, default=next_time)
    parser.add_argument('-p', type=validate_pl_pos, help='Start track number in playlist 0 - (number of tracks), or "res" to resume from last played track, default: starting from 0', nargs='?', const=0, default=0)
    parser.add_argument('-l', action='store_true', help='Fast-loading last saved playlist (when present), default: reading new playlist from storage')
    parser.add_argument('-playlist_name', type=validate_playlist_name, help='Pick custom playlist name in ./Music', nargs='?', const='Playlist', default='Playlist')
 
    args = parser.parse_args()  # Parse the command-line arguments
    
    sched_time_str = args.t # Access parsed start time argument
    sched_time = string_to_datetime(sched_time_str) # Convert time string to a datetime object
    
    pl_pos = args.p # Access parsed playlist position, starting with 0
    l = args.l
    playlist_name = args.playlist_name
    
    path, title, artist, length = load_playlist(l, playlist_name)
    pl_len = len(path)
    
    if 0 <= pl_pos < pl_len:
        pl_start = int(pl_pos)
    else:
        raise argparse.ArgumentTypeError(f"Invalid playlist position: {pl_pos}.")

    lts, sts, et = load_runtime_matrix(l, length, pl_start, pl_len)
    
    print(f"Playlist: {playlist_name} | Tracks: {pl_len} | Runtime: {et}")
    print(f"Starting with track: {pl_start} , at: {sched_time}")
    
    scheduler = BlockingScheduler(timezone=timezone) # Create a scheduler
    sched_time = sched_time - timedelta(seconds=1)
 
    for pos in range(pl_start, pl_len):
        p = path[pos]
        t = title [pos]
        a = artist [pos]
        
        load_time = sched_time + lts[pos] # lts pl_pos list index out of range JAudioSync.py -p 1
        start_time = sched_time + sts[pos]

        scheduler.add_job(load_music, 'date', run_date=load_time, args=[p,t,a])
        scheduler.add_job(play_music, 'date', run_date=start_time)
    
    # Scheduling shutdown after last played track
    end_time = sched_time + et
    scheduler.add_job(end, 'date', run_date=end_time, args=[path, title, artist, length, lts, sts, et])
    
    try:
        mixer.init()
        scheduler.start()
    except (KeyboardInterrupt, SystemExit):
        # pickle save path, title, artist, length
        save_p_t_a_l(path, title, artist, length)
        # pickle save pl_pos
        save_resume_pos(resume_pos)
        save_lts_sts_et(lts, sts, et)
        print("Script interrupted by user.")
        scheduler.shutdown(wait=False)
        mixer.quit()

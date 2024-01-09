import sys
import re
import os
import argparse
from functools import partial
import pytz
import pygame.mixer
from urllib.parse import unquote
from datetime import timedelta, datetime
import time
from pydub import AudioSegment
from math import ceil
from apscheduler.schedulers.blocking import BlockingScheduler
import pandas as pd

def get_next_time():    
    second = datetime.now().second
    minute = datetime.now().minute

    if second < 30:
        next_time = datetime.now() + timedelta(minutes=1)
        next_time = next_time.replace(second=0,  microsecond=0).strftime('%H:%M:%S')

    if second > 30:
        next_time = datetime.now() + timedelta(minutes=1)
        next_time = next_time.replace(second=30,  microsecond=0).strftime('%H:%M:%S')
    return next_time
        
# Validate hh:mm:ss time format for start_time input
def validate_time_string(time_str):
    # Regular expression to validate the format hh:mm:ss
    pattern = re.compile(r'^([01]?[0-9]|2[0-3]):[0-5][0-9]:[0-5][0-9]$')
    if not pattern.match(time_str):
        raise argparse.ArgumentTypeError(f"Invalid time format: {time_str} , use valid hh:mm:ss")
    return time_str

# Try to convert pl_pos string to int and check if valid playlist position
def validate_pl_pos(pl_len, resume_pos, pos):
    if pos.lower() == "res":
        print(f"Resuming with track {resume_pos}.")
        return resume_pos
    try:
        pos = int(pos)
        if not (0 <= pos < pl_len):
            raise ValueError(f"Playlist position out of range. Use 0 - {pl_len - 1}") 
        return pos
    except ValueError:
        raise argparse.ArgumentTypeError(f"Invalid playlist position: {pos}.")

def is_valid_timezone(tz):
    try:
        pytz.timezone(tz)
        return tz
    except pytz.UnknownTimeZoneError:
        raise argparse.ArgumentTypeError(f'{tz} is not a valid timezone.')


def read_resume_position(pl_len):
    try:
        with open("./.resume", "r") as file:
            resume_pos = int(file.readline().strip())
        if not (0 <= resume_pos < pl_len):
            return 0
        return resume_pos
    except (FileNotFoundError, ValueError):
        print(f".resume not valid, 0 - {pl_len - 1}")
        return 0

# Convert time string to a datetime object with date of today
def string_to_datetime(time_string):
    format_str = "%H:%M:%S"
    today_date = datetime.now().date()
    datetime_str = f"{today_date} {time_string}"
    return datetime.strptime(datetime_str, f"%Y-%m-%d {format_str}")

# Get the rounded up playback length of a music file as timedelta (seconds)
def get_music_length(file_path):
    audio = AudioSegment.from_file(file_path)
    length_in_seconds = len(audio) / 1000  # Convert milliseconds to seconds
    rounded_length = ceil(length_in_seconds)
    return timedelta(seconds=rounded_length)

# Read .m3u8 playlist file and extract music file paths to "playlist"
def load_playlist(playlist_file):
    try:
        with open(playlist_file, mode='r') as file:
            lines = file.readlines()
            # Filter out comments and empty lines, clean, add ./Music
        path = [os.path.join("./Music", unquote(line.strip())) for line in lines if line.strip() and not line.startswith('#')]
        if playlist is None:
            raise ValueError(f"Playlist {playlist_file} is empty.")
        return playlist
    except FileNotFoundError:
        print(f'The playlist file {file_path} is not present.')
    except Exception as e:
        print(f'An error occurred: {e}')

def pl_fill_start_times(start_times, path, pl_pos, pl_len):
    for i in range(pl_pos+1,pl_len):
        s =  start_times[i-1] + get_music_length(path[i-1]) + timedelta(seconds=1)
        start_times.append(s)
    df = pd.DataFrame({'Path': path[pl_pos:], 'StartTime': start_times})
    return df

# Load a music file into RAM memory with pygame.mixer.Sound, available globally as "music", enabeling fast playback time compared to streaming from storage
def load_music(pos, df):
    global music
    music = pygame.mixer.Sound(df.loc[pos, "Path"])
    music.set_volume(0.8)
    with open("./.resume", 'w') as file: # Write current pl_pos to .resume file
        file.write(str(pl_pos))

# Start playback of music from RAM memory
def play_music(music, pl, i, pl_pos):
    music.play()
    while pygame.mixer.get_busy() == True:
        continue
    pl_pos += 1
    load_music(i+1, pl)

def end():
    scheduler.shutdown()
    pygame.mixer.quit()
    print("Playlist finished playing")

if __name__ == "__main__":
    playlist_file = "./Music/Playlist.m3u8" # Location of .m3u8 playlist file
    path = load_playlist(playlist_file)
    pl_len = len(path)
    timezone = time.tzname[time.localtime().tm_isdst]
    next_time = get_next_time()
    start_times = []
    
    try:
        resume_pos = read_resume_position(pl_len)
    except Exception as e:
        print(f"Error: {e}")

    # Create ArgumentParser object
    parser = argparse.ArgumentParser(description="""
                                    Play a (m3u8) playlist of music in perfect sync on multiple devices.  
                                    Syncing NTP time over wireless network first and then start playback at exact choosen time (using apscheduler),  
                                    which then doesn't need network anymore because it depends on system clock.  
                                    Using pygame.mixer.sound to load music files into Ram memory before playback to reduce delay and variability.  
                                    
                                    usage: JAudioSync.py [-h] [--t 18:55:00] [--p 0 | res]
                                    """
                                    )
    
    # Add optional arguments
    parser.add_argument('--t', type=validate_time_string, help='Time the playback should be scheduled today in the format hh:mm:ss, default: next full minute', nargs='?', default=next_time)
    parser.add_argument('--p', type=partial(validate_pl_pos, pl_len, resume_pos), help='Start track number in playlist [0 - number of tracks], or "resume" to resume from last played track, default: starting from 0', nargs='?', const=0, default=0)

    args = parser.parse_args()  # Parse the command-line arguments
    start_time_str = args.t # Access parsed start time argument
    start_time = string_to_datetime(start_time_str) # Convert time string to a datetime object
    start_times.append(start_time)
    global pl_pos
    pl_pos = args.p # Access parsed playlist position, starting with 0
    
    scheduler = BlockingScheduler(timezone=timezone) # Create a scheduler
    
    pl = pl_fill_start_times(start_times, path, pl_pos, pl_len)
    
    load_music(0, pl)
    
    for i in range(0, pl.shape[0]):
        scheduler.add_job(play_music, 'date', run_date=pl.loc[i, 'StartTime'], args=[music, pl, i, pl_pos])

    try:
        scheduler.start()
        if(pl_pos >= pl.shape[0]):
            end()
    except (KeyboardInterrupt, SystemExit):
        pass
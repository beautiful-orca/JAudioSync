import sys
import re
import os
import argparse
from functools import partial
from pygame import mixer
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
    # debug
    #next_time = datetime.now() + timedelta(seconds=10)
    #next_time = next_time.replace(microsecond=0).strftime('%H:%M:%S')
    return next_time

# Validate hh:mm:ss time format for start_time input
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
    return datetime.strptime(datetime_str, f"%Y-%m-%d {format_str}")

def read_resume_position(pl_len):
    try:
        with open("./.resume", "r") as file:
            resume_pos = int(file.readline().strip())
        if not (0 <= resume_pos <= pl_len):
            return 0
        return resume_pos
    except (FileNotFoundError, ValueError):
        print(f".resume not valid, 0 - {pl_len}")
        return 0
    
# Try to convert pl_pos string to int and check if valid playlist position
def validate_pl_pos(pl_len, pos):
    if pos.lower() == "res":
        resume_pos = read_resume_position(pl_len)
        print(f"Resuming with track {resume_pos}.")
        return resume_pos
    try:
        pos = int(pos)
        if not (0 <= pos < pl_len):
            raise ValueError(f"Playlist position out of range. Use 0 - {pl_len - 1}") 
        return pos
    except ValueError:
        raise argparse.ArgumentTypeError(f"Invalid playlist position: {pos}.")

# Get the rounded up playback length of a music file as timedelta (seconds)
def get_music_length(file_path):
    audio = AudioSegment.from_mp3(file_path)
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
        if path is None:
            raise ValueError(f"Playlist {playlist_file} is empty.")
        return path
    except FileNotFoundError:
        print(f'The playlist file {playlist_file} is not present.')
    except Exception as e:
        print(f'An error occurred: {e}')

def pl_fill_times(pl, start_time, pl_start, pl_len):
    for i in range(pl_start, pl_len):
        if i == pl_start:
            pl.at[i, 'LoadTime'] = start_time - timedelta(seconds=1)
            pl.at[i, 'StartTime'] = start_time
        elif pl_start < i:
            pl.at[i, 'LoadTime'] = pl.at[i-1, 'StartTime'] + get_music_length(pl.at[i-1, 'Path'])
            pl.at[i, 'StartTime'] = pl.at[i, 'LoadTime'] + timedelta(seconds=1)
    return pl

# Load a music file with pygame.mixer.music
def load_music(path):
    global pl_pos
    pl_pos += 1
    mixer.music.load(path)
    print(f"Playing: {path}")
    #mixer.music.set_volume(0.8)

# Start playback of music from RAM memory
def play_music():
    mixer.music.play()
    print(f"At: {datetime.now()}")
    while mixer.get_busy() == True:
        continue

def end():
        print("Playlist finished playing.")
        mixer.quit()
        scheduler.shutdown(wait=False)
    
if __name__ == "__main__":
    playlist_file = "./Music/Playlist.m3u8" # Location of .m3u8 playlist file
    pl = load_playlist(playlist_file)
    print("pl: ")
    print(pl)
    pl_len = pl.len()
    print(f"pl_len: {pl_len}")
    timezone = time.tzname[time.localtime().tm_isdst]
    next_time = get_next_time()
    print(f"next_time: {next_time}")
    
    # Create ArgumentParser object
    parser = argparse.ArgumentParser(description="""
                                    Play a (m3u8) playlist of music in perfect sync on multiple devices.  
                                    Syncing NTP time over wireless network first and then start playback at exact choosen time (using apscheduler),  
                                    which then doesn't need network anymore because it depends on system clock.  
                                    Using pygame.mixer.music to play.
                                    
                                    usage: JAudioSync.py [-h] [-t 18:55:00] [-p 0 | res]
                                    """
                                    )
    
    # Add optional arguments
    parser.add_argument('-t', type=validate_time_string, help='Time the playback should be scheduled today in the format hh:mm:ss, default: next full minute', nargs='?', default=next_time)
    parser.add_argument('-p', type=partial(validate_pl_pos, pl_len), help='Start track number in playlist [0 - number of tracks], or "resume" to resume from last played track, default: starting from 0', nargs='?', const=0, default=0)

    args = parser.parse_args()  # Parse the command-line arguments
    start_time_str = args.t # Access parsed start time argument
    start_time = string_to_datetime(start_time_str) # Convert time string to a datetime object
    global pl_pos
    pl_pos = args.p # Access parsed playlist position, starting with 0
    pl_start = int(pl_pos)
    print(f"Starting with Track: {pl_start}")
    
    # fill playlist DataFrame with load_times and start_times
    pl = pl_fill_times(pl, start_time, pl_start, pl_len)
    print(f"Playlist:")
    print(pl.iloc[pl_start:])
    
    scheduler = BlockingScheduler(timezone=timezone) # Create a scheduler
    
    for i in range(pl_start, pl_len):
        path = pl.at[i, "Path"]
        load_time = pl.at[i, 'LoadTime']
        start_time = pl.at[i, 'StartTime']
        scheduler.add_job(load_music, 'date', run_date=load_time, args=[path])
        scheduler.add_job(play_music, 'date', run_date=start_time)
    
    # Scheduling shutdown after last played track
    end_time = pl.at[pl_len-1, 'StartTime'] + get_music_length(pl.at[pl_len-1, 'Path'])
    scheduler.add_job(end, 'date', run_date=end_time)
    
    try:
        mixer.init()
        scheduler.start()
    except (KeyboardInterrupt, SystemExit):
        with open("./.resume", 'w') as file: # Write current pl_pos to .resume file
            file.write(str(pl_pos))
        print("Script interrupted by user.")
        mixer.quit()
        scheduler.shutdown(wait=False)


'''
make timing table with timedeltas representing playback length
can be generated beforehand, stored and read for fast start on less powerful devices
'''
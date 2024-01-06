import sys
import re
import os
import argparse
from functools import partial
import pygame.mixer
from urllib.parse import unquote
from datetime import timedelta, datetime
import time
from pydub import AudioSegment
from math import ceil
from apscheduler.schedulers.background import BackgroundScheduler

# Read .m3u8 playlist file and extract music file paths to "playlist"
def load_playlist(playlist_file):
    try:
        with open(playlist_file, mode='r') as file:
            lines = file.readlines()
            # Filter out comments and empty lines, clean, add ./Music
        playlist = [os.path.join("./Music", unquote(line.strip())) for line in lines if line.strip() and not line.startswith('#')]
        if playlist is None:
            raise ValueError(f"Playlist {playlist_file} is empty.")
        return playlist
    except FileNotFoundError:
        print(f'The playlist file {file_path} is not present.')
    except Exception as e:
        print(f'An error occurred: {e}')
        
# Validate hh:mm:ss time format for start_time input
def validate_time_string(time_str):
    # Regular expression to validate the format hh:mm:ss
    pattern = re.compile(r'^([01]?[0-9]|2[0-3]):[0-5][0-9]:[0-5][0-9]$')
    if not pattern.match(time_str):
        raise argparse.ArgumentTypeError(f"Invalid time format: {time_str} , use valid hh:mm:ss")
    return time_str

# Try to convert pl_pos string to int and check if valid playlist position
def validate_pl_pos(pl_len, resume_pos, pos):
    if pos.lower() == "resume":
        print(f"Resuming with track {resume_pos+1}.")
        return resume_pos
    try:
        pos = int(pos)
        if not (1 <= pos <= pl_len):
            raise ValueError(f"Playlist position out of range. Use 1 - {pl_len}") 
        return pos - 1
    except ValueError:
        raise argparse.ArgumentTypeError(f"Invalid playlist position: {pos}.")

def read_resume_position(pl_len):
    try:
        with open("./.resume", "r") as file:
            resume_pos = int(file.readline().strip())
        if not (0 <= resume_pos < pl_len):
            return 0
        return resume_pos
    except (FileNotFoundError, ValueError):
        print(".resume not valid, starting with track 1")
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

# Load a music file into RAM memory with pygame.mixer.Sound, available globally as "music", enabeling fast playback time compared to streaming from storage
def load_music(music_file):
    global music
    music = pygame.mixer.Sound(music_file)
    print(music_file)
    print(f"Loaded: {datetime.now().time()}")
    print(f"Length: {get_music_length(music_file)}")

# Start playback of music from RAM memory
def play_music(pl_pos):
    music.play()
    # Write current pl_pos to .resume file
    with open("./.resume", 'w') as file:
        file.write(str(pl_pos))
    print(f"playing: {datetime.now().time()}")
    print(f"Playlist Position: {pl_pos+1}")
    while pygame.mixer.get_busy() == True:
        continue

if __name__ == "__main__":
    
    # Location of .m3u8 playlist file
    playlist_file = "./Music/Playlist.m3u8"
    # Create list of file paths from playlist
    playlist = load_playlist(playlist_file)
    pl_len = len(playlist)

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
                                    
                                    usage: JAudioSync.py [-h] [--s_time 18:55:00] [--pl_pos 1 | resume]
                                    """
                                    )
  
    # Add optional arguments
    parser.add_argument('--s_time', type=validate_time_string, help='Time the playback should be scheduled today in the format hh:mm:ss, default: now + 5 seconds', nargs='?', default=(datetime.now() + timedelta(seconds=5)).strftime('%H:%M:%S'))
    parser.add_argument('--pl_pos', type=partial(validate_pl_pos, pl_len, resume_pos), help='Start track number in playlist [1 - number of tracks], or "resume" to resume from last played track, default: starting from 1', nargs='?', const=0, default=0)
    
    # Parse the command-line arguments
    args = parser.parse_args()

    # Access parsed start time argument
    start_time_str = args.s_time
    # Convert time string to a datetime object
    start_time = string_to_datetime(start_time_str)
    
    # Access parsed playlist position (including resume position if given) argument
    pl_pos = args.pl_pos # 0-2, user facing numbers is 1-3 ( +1 for printing to user)

    # Initializing audio output of pygame.mixer, detects mode automatically, using standard audio interface
    #pygame.mixer.init()
    pygame.mixer.pre_init(48000, -16, 2, 512) # frequency, size, channels, buffer
    
    play_time = start_time
    load_time = play_time - timedelta(seconds=1)
    print(f"Start Playback at: {play_time} , Track Number: {pl_pos + 1}")
    
    # Create a scheduler
    scheduler = BackgroundScheduler()
    
    # Schedule tasks
    for i in range(pl_pos, pl_len):
        music_file_path = playlist[i]
        # Schedule the task at the specified datetime
        scheduler.add_job(load_music, 'date', run_date=load_time, args=[music_file_path])
        scheduler.add_job(play_music, 'date', run_date=play_time, args=[i])
        music_length = get_music_length(music_file_path)
        load_time = play_time + music_length
        play_time = load_time + timedelta(seconds=1)
        
    try:
        scheduler.start()

        while True:
            # Check if there are any jobs
            if not scheduler.get_jobs():
                break

            time.sleep(1)

        # Shut down the scheduler and mixer when done
        scheduler.shutdown()
        pygame.mixer.quit()
        print("Playlist finished playing")

    except (KeyboardInterrupt, SystemExit):
        print("Script interrupted by user.")
        pygame.mixer.quit()
        scheduler.shutdown()
        

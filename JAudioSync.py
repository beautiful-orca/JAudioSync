import sys
import re
import os
import pygame.mixer
from urllib.parse import unquote
from datetime import timedelta, datetime
import time
from pydub import AudioSegment
from math import ceil
from apscheduler.schedulers.background import BackgroundScheduler

def is_valid_time_format(arg):
    time_pattern = re.compile(r'^[0-2][0-9]:[0-5][0-9]:[0-5][0-9]$')
    return bool(time_pattern.match(arg))

# Convert time string to a datetime object with date of today
def string_to_datetime(time_string):
    format_str = "%H:%M:%S"
    today_date = datetime.now().date()
    datetime_str = f"{today_date} {time_string}"
    return datetime.strptime(datetime_str, f"%Y-%m-%d {format_str}")

# Read .m3u8 playlist file and extract file path to "playlist"
def load_playlist(playlist_file):
    with open(playlist_file, 'r') as file:
        lines = file.readlines()
    # Filter out comments and empty lines, clean, add ./Music
    playlist = [os.path.join("./Music", unquote(line.strip())) for line in lines if line.strip() and not line.startswith('#')]
    return playlist

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
    print("loaded: ", datetime.now().time())
    print("length: ", get_music_length(music_file))

# Start playback of music from RAM memory
def play_music():
    music.play()
    print("playing: ", datetime.now().time())
    while pygame.mixer.get_busy() == True:
        continue

def is_valid_start_time(start_time):
    # Get the current time
    current_time = datetime.now()
    # Check if start_time is more than 2 seconds from now
    return start_time > current_time + timedelta(seconds=1)

if __name__ == "__main__":
    
    if len(sys.argv) != 2:
        print("Argument mismatch, Usage: python JAudioSync.py 18:55:00")
        sys.exit(1)
        
    start_time_str = sys.argv[1]
        
    if not is_valid_time_format(start_time_str):
        print("Invalid start time format. Please use the format hh:mm:ss")
        sys.exit(1)
        
    start_time = string_to_datetime(start_time_str)
    
    # debug only
    start_time = datetime.now().replace(microsecond=0) + timedelta(seconds=2)
    
    if not is_valid_start_time(start_time):
        print("Invalid start time, needs to be more than 1 second in the future, better 1 minute to start script on all devices")
        sys.exit(1)
    
    # Location of .m3u8 playlist file
    playlist_file = "./Music/Playlist.m3u8"
    # Create python list of file paths from playlist
    playlist = load_playlist(playlist_file)
    
    # Initializing audio output of pygame.mixer, detects mode automatically, using standard audio interface
    pygame.mixer.init()
    
    play_time = start_time
    load_time = play_time - timedelta(seconds=1)
    print("Start Playback at: ", play_time)
    
    # Create a scheduler
    scheduler = BackgroundScheduler()
    
    # Schedule tasks
    for music_file_path in playlist:
        # Schedule the task at the specified datetime
        scheduler.add_job(load_music, 'date', run_date=load_time, args=[music_file_path])
        scheduler.add_job(play_music, 'date', run_date=play_time)
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
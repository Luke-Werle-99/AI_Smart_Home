import os
import subprocess
import time
from yt_dlp import YoutubeDL

def play_song(query, stop_flag):
    """
    Search for a song on YouTube and play it using mpv.

    Args:
        query (str): Song name or search query.
        stop_flag (bool): If True, stop playing song.
    """

    print(f"Searching for '{query}' on YouTube...")
    ydl_opts = {
        'format': 'bestaudio/best',
        'noplaylist': True,
        'quiet': True,
        'default_search': 'ytsearch',
        'extract_flat': False,
    }

    try:
        with YoutubeDL(ydl_opts) as ydl:
            results = ydl.extract_info(query, download=False)
            if 'entries' in results and results['entries']:
                video_url = results['entries'][0]['url']
                print(f"Playing: {results['entries'][0]['title']}")

                stop_flag.value = False
                # Store the new process using the shared namespace
                sp = subprocess.Popen(['mpv', '--no-video', video_url])

                while sp.poll() is None and not stop_flag.value:
                    time.sleep(0.5)
                sp.terminate()
                sp.wait()

            else:
                print("No results found.")
    except Exception as e:
        print(f"An error occurred: {e}")

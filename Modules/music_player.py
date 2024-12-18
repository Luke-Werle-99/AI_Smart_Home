import os
import subprocess
from yt_dlp import YoutubeDL

def play_song(query):
    """
    Search for a song on YouTube and play it using mpv.

    Args:
        query (str): Song name or search query.
    """
    print(f"Searching for '{query}' on YouTube...")
    # YouTube search options
    ydl_opts = {
        'format': 'bestaudio/best',
        'noplaylist': True,
        'quiet': True,
        'default_search': 'ytsearch',
        'extract_flat': False,  # Extract metadata only
    }

    try:
        with YoutubeDL(ydl_opts) as ydl:
            results = ydl.extract_info(query, download=False)
            if 'entries' in results and results['entries']:
                # Get the first result URL
                video_url = results['entries'][0]['url']
                print(f"Playing: {results['entries'][0]['title']}")
                # Play using mpv
                subprocess.run(['mpv', '--no-video', video_url])
            else:
                print("No results found.")
    except Exception as e:
        print(f"An error occurred: {e}")

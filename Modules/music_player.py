import os
import subprocess
import time
import signal
from yt_dlp import YoutubeDL

def play_song(query, stop_flag):
    """
    Search for a song on YouTube and play it using mpv.

    Args:
        query (str): Song name or search query.
        stop_flag (multiprocessing.Value): Shared flag to indicate stop.
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
                video_info = results['entries'][0]
                video_url = video_info['url']
                print(f"Playing: {video_info['title']}")

                # Clear the flag for this process.
                stop_flag.value = False

                # Launch mpv in a new process group so that we can kill the entire group later.
                sp = subprocess.Popen(
                    ['mpv', '--no-video', video_url],
                    preexec_fn=os.setsid  # This makes mpv the leader of a new process group.
                )

                while sp.poll() is None and not stop_flag.value:
                    time.sleep(0.1)

                if stop_flag.value:
                    print("Stop flag detected. Terminating mpv process group.")
                    os.killpg(os.getpgid(sp.pid), signal.SIGTERM)
                    # Optionally, force kill if needed:
                    time.sleep(0.5)
                    if sp.poll() is None:
                        os.killpg(os.getpgid(sp.pid), signal.SIGKILL)
                else:
                    sp.terminate()
                sp.wait()
            else:
                print("No results found.")
    except Exception as e:
        print(f"An error occurred: {e}")

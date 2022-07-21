"""Use youtube_dl to extract videos and streams data from Twitch channels."""
from typing import Optional

# from urllib.parse import urljoin

import youtube_dl

BASE_URL = "https://www.twitch.tv"


class Logger(object):
    """Logger for youtube-dl."""

    def __init__(self, verbosity):
        """Take the verbosity mode."""
        self.verbosity = verbosity

    def debug(self, msg):
        """Don't print debug messages."""
        pass

    def warning(self, msg):
        """Don't print warning messages, unless verbosity is enabled."""
        if self.verbosity:
            print(msg)

    def error(self, msg):
        """Handle error messages."""
        if msg.endswith(" does not exist"):
            print(msg)
        elif msg.endswith(" is offline"):
            pass


def extract_channel_videos(
    channel_name: str,
    count: int,
    playlist_start: int,
    filter: str = "all",
    sort_method: str = "time",
    reverse: bool = False,
    random: bool = False,
    verbosity: bool = False,
) -> dict:
    """Return a channel's videos data."""
    ydl_opts = {
        "simulate": True,
        "quiet": True,
        "logger": Logger(verbosity),
        "playliststart": playlist_start,
        "playlistend": playlist_start + count - 1,
        "playlistreverse": reverse,
        "playlistrandom": random,
    }

    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        return ydl.extract_info(
            f"{BASE_URL}/{channel_name}/videos?filter={filter}&sort={sort_method}"
        )


def extract_stream(channel_name: str, verbosity: bool = False) -> Optional[dict]:
    """Return data about a steam if there was an active one on the input channel."""
    ydl_opts = {
        "simulate": True,
        "quiet": True,
        "ignoreerrors": True,
        "logger": Logger(verbosity),
    }

    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        try:
            return ydl.extract_info(f"{BASE_URL}/{channel_name}")
        except youtube_dl.utils.DownloadError:
            return None


def extract_video(video_id: str, verbosity: bool = False) -> dict:
    """Return data about a video from it's id."""
    ydl_opts = {
        "simulate": True,
        "quiet": True,
        "ignoreerrors": True,
        "logger": Logger(verbosity),
    }

    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        return ydl.extract_info(f"{BASE_URL}/videos/{video_id}")

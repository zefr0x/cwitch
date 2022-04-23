"""Use youtube_dl to extract videos and streams data from Twitch channels."""
from __future__ import unicode_literals
from typing import Optional

# from urllib.parse import urljoin

import youtube_dl

BASE_URL = "https://www.twitch.tv"


def extract_channel_videos(
    channel_name: str,
    count: int,
    filter: str = "all",
    sort_method: str = "time",
    reverse: bool = False,
    random: bool = False,
) -> dict:
    """Return a channel's videos data."""
    ydl_opts = {
        "simulate": True,
        "quiet": True,
        "playliststart": 1,
        "playlistend": count,
        "playlistreverse": reverse,
        "playlistrandom": random,
    }

    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        return ydl.extract_info(
            f"{BASE_URL}/{channel_name}/videos?filter={filter}&sort={sort_method}"
        )


def extract_stream(channel_name: str) -> Optional[dict]:
    """Return data about a steam if there was an active one on the input channel."""
    ydl_opts = {"simulate": True, "quiet": True, "ignoreerrors": True}

    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        try:
            return ydl.extract_info(f"{BASE_URL}/{channel_name}")
        except youtube_dl.utils.DownloadError:
            return None


def extract_video(video_id: str) -> dict:
    """Return data about a video from it's id."""
    ydl_opts = {"simulate": True, "quiet": True, "ignoreerrors": True}

    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        return ydl.extract_info(f"{BASE_URL}/videos/{video_id}")

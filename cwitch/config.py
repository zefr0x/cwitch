"""Parse the config and the channels list."""
from configparser import ConfigParser, NoOptionError, NoSectionError
from pathlib import Path
from typing import Optional, TextIO

from __init__ import __name__ as prog_name


def get_config(config_file: Optional[TextIO] = None) -> dict:
    """Parse a config file."""
    config = ConfigParser()

    try:
        if config_file is None:
            config_file = open(
                Path.joinpath(Path.home(), f".config/{prog_name}/config.ini"), "r"
            )

        config.read_file(config_file)
    except FileNotFoundError:
        pass

    options = {"playlist_fetching": {"max_videos_count": 5}}

    try:
        options["playlist_fetching"]["max_videos_count"] = config.getint(
            "playlist_fetching", "max_videos_count"
        )
    except (NoOptionError, NoSectionError):
        pass

    return options


def get_following_channels(channels_file: Optional[TextIO] = None) -> tuple:
    """Parse the following channels' list from a file."""
    channels = ConfigParser()

    try:
        if channels_file is None:
            channels_file = open(
                Path.joinpath(Path.home(), ".config/cwitch/channels.ini"), "r"
            )

        channels.read_file(channels_file)
    except FileNotFoundError:
        pass

    channels_list = []

    for channel in channels.sections():
        try:
            channels_list.append({"name": channel, "id": channels.get(channel, "id")})
        except NoOptionError:
            continue

    return tuple(channels_list)

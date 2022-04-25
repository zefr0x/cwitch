"""Parse the config and the channels list."""
from configparser import ConfigParser, NoOptionError, NoSectionError
from pathlib import Path
from typing import Optional

from __init__ import __name__ as prog_name


def get_config(config_file: Optional[str] = None) -> dict:
    """Parse a config file."""
    if config_file is None:
        config_file_path = Path.joinpath(Path.home(), f".config/{prog_name}/config.ini")
    else:
        config_file_path = Path(config_file)

    config = ConfigParser()
    config.read(config_file_path)

    options = {"playlist_fetching": {"max_videos_count": 5}}

    try:
        options["playlist_fetching"]["max_videos_count"] = config.getint(
            "playlist_fetching", "max_videos_count"
        )
    except (NoOptionError, NoSectionError):
        pass

    return options


def get_following_channels(channels_file: Optional[str] = None) -> tuple:
    """Parse the following channels' list from a file."""
    if channels_file is None:
        channels_file_path = Path.joinpath(Path.home(), ".config/cwitch/channels.ini")
    else:
        channels_file_path = Path(channels_file)

    channels = ConfigParser()
    channels.read(channels_file_path)

    channels_list = []

    for channel in channels.sections():
        try:
            channels_list.append({"name": channel, "id": channels[channel]["id"]})
        except NoOptionError:
            continue

    return tuple(channels_list)

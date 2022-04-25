"""Command line interface for cwitch."""
import argparse
from datetime import datetime, timedelta

import mpv

from __init__ import __version__ as prog_version, __name__ as prog_name
import extractors
from config import get_config, get_following_channels


def get_parser():
    """Return a parser object."""
    parser = argparse.ArgumentParser(
        prog=prog_name,
        description="Watch Twitch live streams and videos and track channels' activities",
        epilog="",
    )

    parser.add_argument(
        "-v", "--verbosity", action="store_true", help="Toggle verbosity."
    )
    parser.add_argument(
        "-V", "--version", action="store_true", help="Print %(prog)s version."
    )
    parser.add_argument(
        "--config-file", type=argparse.FileType("r"), help="An alternative config file."
    )

    # Create a second layer parsers
    subparsers = parser.add_subparsers(
        title="Subcommands",
        description="Pick a subcommand for the operation you want",
        dest="subcommand",
    )

    # The channel command
    channel_parser = subparsers.add_parser(
        "c", help="To play a live stream or search in the previous videos of a channel"
    )
    # TODO Auto completion for channels names from the channels list file.
    channel_parser.add_argument(
        "-n", "--channel-id", type=str, required=True, help="The channel ID"
    )
    # Tow mutually exclusive flags for different actions
    group1 = channel_parser.add_mutually_exclusive_group(required=True)
    group1.add_argument(
        "-s", "--stream", action="store_true", help="Watch live stream if there was"
    )
    group1.add_argument(
        "-l",
        "--list-videos",
        action="store_true",
        help="List the channel's videos",
    )

    channel_parser.add_argument(
        "-q",
        "--quality",
        type=str,
        nargs="?",
        metavar="format",
        choices=["audio", "best", "middle", "worst"],
        const="best",
        help="Pick one of the folowing: %(choices)s (defaults to: best)",
    )

    # The Following channels command
    following_channels_parser = subparsers.add_parser(
        "s", help="List and view the status of the channels that you follow"
    )
    following_channels_parser.add_argument(
        "-o",
        "--online",
        action="store_true",
        help="Show only online channels",
    )
    following_channels_parser.add_argument(
        "--channels-file",
        type=argparse.FileType("r"),
        help="An alternative channels list file.",
    )
    following_channels_parser.add_argument(
        "-q",
        "--quality",
        type=str,
        nargs="?",
        metavar="format",
        choices=["audio", "best", "middle", "worst"],
        const="best",
        help="Pick one of the folowing: %(choices)s (defaults to: best)",
    )

    # The video command
    video_parser = subparsers.add_parser("v", help="To watch a video with it's ID")
    video_parser.add_argument(
        "-d",
        "--videos-ids",
        type=str,
        nargs="+",
        metavar="VIDEO",
        help="One or more video ID. They will be opened as a playlist",
        required=True,
    )
    video_parser.add_argument(
        "-q",
        "--quality",
        type=str,
        nargs="?",
        metavar="format",
        choices=["audio", "best", "middle", "worst"],
        const="best",
        help="Pick one of the folowing: %(choices)s (defaults to: best)",
    )

    return parser


def channel_actions(args, config):
    """Run the channel subcommand according to it's options."""
    if args.stream:
        data = extractors.extract_stream(args.channel_id)
        if data:
            play_media(args, [data])
        # TODO Error handling when the channel is offline.
    elif args.list_videos:
        data = extractors.extract_channel_videos(
            args.channel_id, config["playlist_fetching"]["max_videos_count"]
        )

        for video in data["entries"]:
            print_video_data(video, args)

        print("-" * 23)
        videos_to_watch = input(
            f"Pick videos to watch: {list(range(1, len(data['entries'])+1))}\n==> "
        ).split(" ")
        print("-" * 23)

        play_media(
            args,
            [x for i, x in enumerate(data["entries"]) if str(i + 1) in videos_to_watch],
        )


def following_channels_actions(args, config):
    """Run the video subcommand according to it's options."""
    channels = get_following_channels(args.channels_file)

    data = []

    for channel in channels:
        if args.verbosity:
            print("Checking for:", channel["id"])

        channel_stream_data = extractors.extract_stream(channel["id"])
        # TODO color the output
        if channel_stream_data:
            print(f"[{len(data)}] ({channel['name']}) is online")
            data.append(channel_stream_data)
        elif not args.online:
            print(f"[---] ({channel['name']}) is offline")

    if data:
        to_watch = input(
            f"Pick streams to watch: {list(range(len(data)))}\n==> "
        ).split()

        to_watch_data = [d for i, d in enumerate(data) if str(i) in to_watch]
        play_media(args, to_watch_data)


def play_media(args, data=None):
    """Play a list of videos or streams."""
    if data is None:
        # When using the v command.
        data = [extractors.extract_video(i) for i in args.videos_ids]

    player = mpv.MPV(
        input_default_bindings=True,
        input_vo_keyboard=True,
        osc=True,
        title=prog_name,
    )

    # script_dir = str(Path.home())+'/.config/mpv/scripts/'
    # [self.player.command('load-script', script_dir+script) for script in os.listdir(script_dir)]

    # @player.property_observer("time-pos")
    # def time_observer(_name, value):
    #     ...

    for video in data:
        print_video_data(video, args)

        video_formats = [v["format_id"] for v in video["formats"]]
        if args.quality and len(video_formats) >= 2:
            if args.quality == "audio":
                video_format = 0
            elif args.quality == "best":
                video_format = -1
            elif args.quality == "middle":
                video_format = -2
            elif args.quality == "worst":
                video_format = 1
        else:
            try:
                video_format = video_formats.index(
                    input(f"Pick a format: {video_formats}\n==> ")
                )
            except ValueError:
                # By default it will pick the best format.
                video_format = -1

        player.playlist_append(
            # Since mpv discards what is beyond the #, we can use it as a title in the playlist
            video["formats"][video_format]["url"] + "#" + video["title"],
            media_title=video["title"],
        )

    player.playlist_pos = 0

    player.wait_until_playing()
    if args.verbosity:
        print(player.playlist)

    player.wait_for_shutdown()


def print_video_data(video, args):
    """Print video data in a readable way."""
    print(f"---- {video['webpage_url_basename']} ----[{video['playlist_index'] or 0}]")
    print("Title:", video["title"])
    print("Date:", datetime.fromtimestamp(int(video["timestamp"])))
    try:
        print("Duration:", timedelta(seconds=video["duration"]))
    except KeyError:
        # If it was a live stream there will be no duration
        pass
    print("View count:", video["view_count"])
    if args.verbosity:
        print("Uploader:", video["uploader"])
        print("Webpage URL:", video["webpage_url"])
        print("Thumbnails URLs:", video["thumbnail"], video["thumbnails"])
        print("Stream URLs:", [(x["format_id"], x["url"]) for x in video["formats"]])
        print("Subtitles:", video["subtitles"])
        print("URL:", video["url"])
        print("FPS:", video["fps"])
        print("width & height:", video["width"], video["height"])
        print("Format:", video["format"])


def main():
    """Run cwitch from the command line."""
    parser = get_parser()
    args = parser.parse_args()

    if args.verbosity:
        print(args)

    if args.version:
        print(f"{prog_name} {prog_version}")
        exit(0)
    elif not args.subcommand:
        parser.print_help()
        exit(0)

    config = get_config(args.config_file)

    if args.subcommand == "c":
        channel_actions(args, config)
    elif args.subcommand == "s":
        following_channels_actions(args, config)
    elif args.subcommand == "v":
        play_media(args)

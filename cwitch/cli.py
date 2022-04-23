"""Command line interface for cwitch."""
import argparse
from datetime import datetime

import mpv

from __init__ import __version__, __name__
import extractors
from config import get_config, get_following_channels


def get_args():
    """Parse the args from stdin then return them in a readable way for python."""
    parser = argparse.ArgumentParser(
        prog=__name__,
        description="Watch Twitch live streams and videos and track channels' activities",
        epilog="",
    )

    parser.add_argument(
        "-v", "--verbosity", action="store_true", help="Toggle verbosity."
    )
    parser.add_argument(
        "-V", "--version", action="store_true", help="Print %(prog)s version."
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
        "-s",
        "--status",
        action="store_true",
        help=(
            "List the statue of every channel you are following,"
            + "whether it's streaming or it's offline"
        ),
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

    return parser, parser.parse_args()


def channel_actions(args, config):
    """Run the channel subcommand according to it's options."""
    if args.stream:
        data = extractors.extract_stream(args.channel_id)
        if data:
            play_media(args, [data])
    elif args.list_videos:
        data = extractors.extract_channel_videos(
            args.channel_id, config["max_videos_count"]
        )

        for i, video in enumerate(data["entries"]):
            print_video_data(video, i)

        videos_to_watch = input(
            f"Pick videos to watch: {list(range(len(data['entries'])))}\n==> "
        ).split(" ")
        print("-" * 23)

        play_media(
            args,
            [x for i, x in enumerate(data["entries"]) if str(i) in videos_to_watch],
        )


def following_channels_actions(args, config):
    """Run the video subcommand according to it's options."""
    ...


def play_media(args, data=None):
    """Play a list of videos or streams."""
    if not data:
        # When using the v command.
        data = [extractors.extract_video(i) for i in args.videos_ids]

    player = mpv.MPV(input_default_bindings=True, input_vo_keyboard=True, osc=True)

    for i, video in enumerate(data):
        print_video_data(video, i)

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

        player.playlist_append(video["formats"][video_format]["url"])

    player.playlist_pos = 0

    if args.verbosity:
        print(player.playlist)

    player.wait_for_shutdown()


def print_video_data(video, i):
    """Print video data in a readable way."""
    print(f"---- {video['id'][1:]} ----[{i}]")
    print("Title:", video["title"])
    print("Date:", datetime.fromtimestamp(int(video["timestamp"])))
    print("Uploader:", video["uploader"])
    try:
        print("Duration:", video["duration"])
    except KeyError:
        # If it was a live stream there will be no duration
        pass
    print("View count:", video["view_count"])
    print("Thumbnail:", video["thumbnail"])


def main():
    """Run cwitch from the command line."""
    parser, args = get_args()

    if args.verbosity:
        print(args)

    if args.version:
        print(f"{__name__} {__version__}")
        exit(0)
    elif not args.subcommand:
        parser.print_help()
        exit(0)

    config = get_config("")

    if args.subcommand == "c":
        channel_actions(args, config)
    elif args.subcommand == "s":
        following_channels_actions(args, config)
    elif args.subcommand == "v":
        play_media(args)

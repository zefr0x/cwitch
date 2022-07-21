"""Command line interface for cwitch."""
import argparse

# from mpv import MPV
from prompt_toolkit import print_formatted_text, HTML

from .__init__ import __version__, prog_name
from . import subcommands
from . import printers
from . import prompts


def get_parser() -> argparse.ArgumentParser:
    """Return a parser object."""
    parser = argparse.ArgumentParser(
        prog=prog_name,
        description="watch Twitch live streams and videos and track channels' activities.",
        # epilog="v" + __version__,
    )

    parser.add_argument(
        "-v", "--verbosity", action="store_true", help="toggle verbosity."
    )
    parser.add_argument(
        "-V", "--version", action="store_true", help="print %(prog)s version."
    )
    parser.add_argument(
        "--config-file", type=argparse.FileType("r"), help="an alternative config file."
    )

    # Create a second layer parsers
    subparsers = parser.add_subparsers(
        title="subcommands",
        description="pick a subcommand for the operation you want.",
        dest="subcommand",
    )

    # The channel command
    channel_parser = subparsers.add_parser(
        "c", help="to play a live stream or search in the previous videos of a channel."
    )
    # TODO Tap auto completion for channel name from the channels list file.
    channel_parser.add_argument(
        "channel_id",
        type=str,
        metavar="CHANNEL-ID",
        help="the channel ID.",
    )
    # Two mutually exclusive flags for different actions
    group1 = channel_parser.add_mutually_exclusive_group(required=True)
    group1.add_argument(
        "-s",
        "--stream",
        action="store_true",
        help="play the live stream if there was.",
    )
    # TODO Add filter, sort, reverse and random options.
    group1.add_argument(
        "-l",
        "--list-videos",
        action="store_true",
        help="list the channel's videos.",
    )

    channel_parser.add_argument(
        "-n",
        "--max-list-length",
        type=int,
        metavar="integer",
        help="Maximum number of listed videos",
    )

    channel_parser.add_argument(
        "-q",
        "--quality",
        type=str,
        nargs="?",
        metavar="format",
        choices=["audio", "best", "middle", "worst"],
        const="best",
        help="pick one of the folowing: %(choices)s (defaults to: best).",
    )

    # The Following channels command
    following_channels_parser = subparsers.add_parser(
        "s", help="list and view the status of the channels that you follow."
    )
    following_channels_parser.add_argument(
        "-o",
        "--online",
        action="store_true",
        help="show only online channels.",
    )
    following_channels_parser.add_argument(
        "--channels-file",
        type=argparse.FileType("r"),
        help="an alternative channels list file.",
    )
    following_channels_parser.add_argument(
        "-q",
        "--quality",
        type=str,
        nargs="?",
        metavar="format",
        choices=["audio", "best", "middle", "worst"],
        const="best",
        help="pick one of the folowing: %(choices)s (defaults to: best).",
    )

    # The video command
    video_parser = subparsers.add_parser(
        "v", help="watch one or more video with the ID."
    )
    video_parser.add_argument(
        "videos_ids",
        type=str,
        nargs="+",
        metavar="VIDEO-ID",
        help="one or more video ID. they will be opened as a playlist.",
    )
    video_parser.add_argument(
        "-q",
        "--quality",
        type=str,
        nargs="?",
        metavar="format",
        choices=["audio", "best", "middle", "worst"],
        const="best",
        help="pick one of the folowing: %(choices)s (defaults to: best).",
    )

    return parser


def play_media(args: argparse.Namespace, medias_data: tuple) -> None:
    """Play a list of videos or streams."""
    from mpv import MPV

    player = MPV(
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

    for media in medias_data:
        if media is None:
            continue

        printers.print_media_data(args, media)

        media_formats = [m["format_id"] for m in media["formats"]]
        if args.quality and len(media_formats) >= 2:
            if args.quality == "audio":
                media_format = 0
            elif args.quality == "best":
                media_format = -1
            elif args.quality == "middle":
                media_format = -2
            elif args.quality == "worst":
                media_format = 1
        else:
            media_format = prompts.formats_prompt(media_formats)

        player.playlist_append(
            # Since mpv discards what is beyond the #, we can use it as a title in the playlist
            media["formats"][media_format]["url"] + "#" + media["title"],
            media_title=media["title"],
        )

    player.playlist_pos = 0

    player.wait_until_playing()
    if args.verbosity:
        print_formatted_text(HTML("<orange>#</orange>"), player.playlist)

    player.wait_for_shutdown()


def main() -> int:
    """Run cwitch from the command line."""
    parser = get_parser()
    args = parser.parse_args()

    if args.verbosity:
        print_formatted_text(HTML("<orange>#</orange>"), args)

    if args.version:
        print(f"{prog_name} {__version__}")
        return 0
    elif not args.subcommand:
        parser.print_help()
        return 0

    if args.subcommand == "c":
        media_data, displayed_videos_count, extra_count = subcommands.channels_command(
            args
        )
        if displayed_videos_count:
            while displayed_videos_count:
                (
                    sub_media_data,
                    displayed_videos_count,
                    extra_count,
                ) = subcommands.channels_command(
                    args, displayed_videos_count, extra_count
                )
                if media_data:
                    media_data.extend(sub_media_data or [])
                else:
                    media_data = sub_media_data
        elif displayed_videos_count == 0:
            print_formatted_text(HTML("<red>Error</red>: There is no more videos."))
    elif args.subcommand == "s":
        media_data = subcommands.following_channels_command(args)
    elif args.subcommand == "v":
        media_data = subcommands.videos_command(args)

    if media_data:
        play_media(args, tuple(media_data))
    return 1


if __name__ == "__main__":
    raise SystemExit(main())

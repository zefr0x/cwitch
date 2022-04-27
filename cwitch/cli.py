"""Command line interface for cwitch."""
import argparse

# from datetime import datetime, timedelta

# import mpv
from prompt_toolkit import print_formatted_text, HTML, prompt
from prompt_toolkit.shortcuts import ProgressBar

from __init__ import __version__ as prog_version, prog_name
import extractors
from config import get_config, get_following_channels
import auto_completion
import input_validation


def get_parser():
    """Return a parser object."""
    parser = argparse.ArgumentParser(
        prog=prog_name,
        description="Watch Twitch live streams and videos and track channels' activities.",
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
        description="Pick a subcommand for the operation you want.",
        dest="subcommand",
    )

    # The channel command
    channel_parser = subparsers.add_parser(
        "c", help="To play a live stream or search in the previous videos of a channel."
    )
    # TODO Auto completion for channels names from the channels list file.
    channel_parser.add_argument(
        "channels_ids",
        type=str,
        nargs="+",
        metavar="CHANNEL-ID",
        help="The channel ID.",
    )
    # Tow mutually exclusive flags for different actions
    group1 = channel_parser.add_mutually_exclusive_group(required=True)
    group1.add_argument(
        "-s",
        "--stream",
        action="store_true",
        help="Play the live stream if there was.",
    )
    group1.add_argument(
        "-l",
        "--list-videos",
        action="store_true",
        help="List the channel's videos.",
    )

    channel_parser.add_argument(
        "-q",
        "--quality",
        type=str,
        nargs="?",
        metavar="format",
        choices=["audio", "best", "middle", "worst"],
        const="best",
        help="Pick one of the folowing: %(choices)s (defaults to: best).",
    )

    # The Following channels command
    following_channels_parser = subparsers.add_parser(
        "s", help="List and view the status of the channels that you follow."
    )
    following_channels_parser.add_argument(
        "-o",
        "--online",
        action="store_true",
        help="Show only online channels.",
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
        help="Pick one of the folowing: %(choices)s (defaults to: best).",
    )

    # The video command
    video_parser = subparsers.add_parser(
        "v", help="Watch one or more video with the ID."
    )
    video_parser.add_argument(
        "videos_ids",
        type=str,
        nargs="+",
        metavar="VIDEO-ID",
        help="One or more video ID. They will be opened as a playlist.",
    )
    video_parser.add_argument(
        "-q",
        "--quality",
        type=str,
        nargs="?",
        metavar="format",
        choices=["audio", "best", "middle", "worst"],
        const="best",
        help="Pick one of the folowing: %(choices)s (defaults to: best).",
    )

    return parser


def channel_actions(args, config):
    """Run the channel subcommand according to it's options."""
    if args.stream:
        data = []

        with ProgressBar(
            title=HTML(
                f"<style bg='white' fg='black'>Fetching {len(args.channels_ids)} "
                + "streams data...</style>"
            )
        ) as pb:
            for channel in pb(args.channels_ids):
                stream_data = extractors.extract_stream(channel)
                if stream_data:
                    data.append(stream_data)
                else:
                    print_formatted_text(
                        HTML(f"<red>Error:</red> ({channel}) is <b>offline</b>.")
                    )

        if data:
            play_media(args, data)

    elif args.list_videos:
        data = []
        with ProgressBar(
            title=HTML(
                f"<style bg='white' fg='black'>Fetching {len(args.channels_ids)} "
                + "videos list...</style>"
            )
        ) as pb:
            for channel_id in pb(args.channels_ids):
                if args.verbosity:
                    print("Fetching data for", channel_id)

                data.append(
                    extractors.extract_channel_videos(
                        channel_id, config["playlist_fetching"]["max_videos_count"]
                    )
                )

        to_watch_data = []
        for sub_data in data:
            video_titles = {}
            for video in sub_data["entries"]:
                video_titles.update({str(video["playlist_index"]): video["title"]})
                print_video_data(video, args)

            videos_to_watch = tuple(
                map(
                    int,
                    prompt(
                        HTML(
                            "<b>Pick videos to watch:</b> "
                            + f"<gray>{list(range(1, len(sub_data['entries']) + 1))}</gray>"
                            + "\n<green>==></green> "
                        ),
                        completer=auto_completion.VideoTitlesCompleter(video_titles),
                        validator=input_validation.NumbersListValidator(
                            video_titles.keys()
                        ),
                    ).split(),
                )
            )

            to_watch_data += [
                x for i, x in enumerate(sub_data["entries"]) if i + 1 in videos_to_watch
            ]

        if to_watch_data:
            play_media(
                args,
                to_watch_data,
            )


def following_channels_actions(args, config):
    """Run the video subcommand according to it's options."""
    channels = get_following_channels(args.channels_file)

    if not channels:
        # TODO color the output
        print_formatted_text(
            HTML(
                (
                    "<red>Error:</red> Can't find any channel on your list! "
                    + "Add some channels to use this command."
                ),
            )
        )
        return False

    data = []
    streams_titles = {}

    with ProgressBar(
        title=HTML(
            f"<style bg='white' fg='black'>Fetching {len(channels)} streams data...</style>"
        )
    ) as pb:
        for channel in pb(channels):
            if args.verbosity:
                print("Checking for:", channel["id"])

            channel_stream_data = extractors.extract_stream(channel["id"])
            # TODO color the output
            if channel_stream_data:
                print_formatted_text(
                    HTML(
                        f"<lime>[{len(data) + 1}]</lime> ({channel['name']}) "
                        + "is <green><b>online</b></green>"
                    )
                )
                data.append(channel_stream_data)
                streams_titles.update({str(len(data)): channel["name"]})
            elif not args.online:
                print_formatted_text(
                    HTML(
                        f"<red>[-]</red> ({channel['name']}) is <red><b>offline</b></red>"
                    )
                )

    if data:
        to_watch = tuple(
            map(
                int,
                prompt(
                    HTML(
                        "<b>Pick streams to watch:</b> "
                        + f"<gray>{list(range(1, len(data)+1))}</gray>"
                        + "\n<green>==></green> "
                    ),
                    completer=auto_completion.VideoTitlesCompleter(streams_titles),
                    validator=input_validation.NumbersListValidator(
                        streams_titles.keys()
                    ),
                ).split(),
            )
        )

        to_watch_data = [d for i, d in enumerate(data) if i + 1 in to_watch]
        if to_watch_data:
            play_media(args, to_watch_data)


def play_media(args, data=None):
    """Play a list of videos or streams."""
    import mpv

    if data is None:
        # When using the v command.
        data = [extractors.extract_video(i) for i in args.videos_ids]

        if all([not x for x in data]):
            # When all videos doesn't exist.
            return None

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
        if video is None:
            continue

        print_video_data(video, args)

        media_formats = [v["format_id"] for v in video["formats"]]
        if args.quality and len(media_formats) >= 2:
            if args.quality == "audio":
                video_format = 0
            elif args.quality == "best":
                video_format = -1
            elif args.quality == "middle":
                video_format = -2
            elif args.quality == "worst":
                video_format = 1
        else:
            video_format = media_formats.index(
                prompt(
                    HTML(
                        "<b>Pick a format:</b> "
                        + f"<gray>{media_formats}</gray>"
                        + "\n<green>==></green> "
                    ),
                    default=media_formats[-1],
                    completer=auto_completion.MediaFormatCompleter(media_formats),
                    validator=input_validation.MediaFormatsValidator(media_formats),
                ).strip()
            )

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
    from datetime import datetime, timedelta

    print_formatted_text(
        HTML(f"---- <aqua>{video['webpage_url_basename']}</aqua> ----"), end=""
    )
    if video["playlist_index"]:
        print_formatted_text(HTML(f"<lime>[{video['playlist_index']}]</lime>"))
    else:
        print()
    print_formatted_text(HTML("<b>Title:</b>"), video["title"])
    print_formatted_text(
        HTML("<b>Date:</b>"), datetime.fromtimestamp(int(video["timestamp"]))
    )
    try:
        print_formatted_text(
            HTML("<b>Duration:</b>"), timedelta(seconds=video["duration"])
        )
    except KeyError:
        # If it was a live stream there will be no duration
        pass
    if video["view_count"]:
        print_formatted_text(HTML("<b>View count:</b>"), video["view_count"])
    if args.verbosity:
        print_formatted_text(HTML("<b>Uploader:</b>"), video["uploader"])
        print_formatted_text(HTML("<b>Webpage URL:</b>"), video["webpage_url"])
        print_formatted_text(
            HTML("<b>Thumbnails URLs:</b>"), video["thumbnail"], video["thumbnails"]
        )
        print_formatted_text(
            HTML("<b>Stream URLs:</b>"),
            [(x["format_id"], x["url"]) for x in video["formats"]],
        )
        print_formatted_text(HTML("<b>Subtitles:</b>"), video["subtitles"])
        print_formatted_text(HTML("<b>URL:</b>"), video["url"])
        print_formatted_text(HTML("<b>FPS:</b>"), video["fps"])
        print_formatted_text(
            HTML("<b>width & height:</b>"), video["width"], video["height"]
        )
        print_formatted_text(HTML("<b>Format:</b>"), video["format"])


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

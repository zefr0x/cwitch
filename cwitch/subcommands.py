"""CLI subcommands functions."""
from typing import Optional, Tuple
import threading

from prompt_toolkit import print_formatted_text, HTML
from prompt_toolkit.shortcuts import ProgressBar

from . import extractors
from . import printers
from . import prompts
from .config import get_config, get_following_channels


def channels_command(
    args, playlist_start: int = 0, extra_count: Optional[int] = None
) -> Tuple[Optional[list], Optional[int], Optional[int]]:
    """Run the channel subcommand."""
    # TODO Remove multiple channel support.
    if args.stream:
        data = []

        def fetch_stream_data(channel_id: str) -> None:
            stream_data = extractors.extract_stream(channel_id, args.verbosity)
            if stream_data:
                data.append(stream_data)
            else:
                print_formatted_text(
                    HTML(f"<red>Error:</red> ({channel_id}) is <b>offline</b>.")
                )

        threads = {}
        for channel_id in args.channels_ids:
            threads.update(
                {
                    channel_id: threading.Thread(
                        target=fetch_stream_data, args=(channel_id,)
                    )
                }
            )
            threads[channel_id].daemon = True
            threads[channel_id].start()

        with ProgressBar(
            title=HTML("<style bg='white' fg='black'>Fetching streams data...</style>")
        ) as pb:
            for channel_id, thread in pb(threads.items()):
                if thread.is_alive():
                    thread.join()

        if data:
            return data, None, None

    elif args.list_videos:
        config = get_config(args.config_file)
        data = []

        def fetch_channel_videos_list(channel_id: str) -> None:
            data.append(
                extractors.extract_channel_videos(
                    channel_id,
                    extra_count
                    or args.max_list_length
                    or config["playlist_fetching"]["max_videos_count"],
                    playlist_start + 1,
                    verbosity=args.verbosity,
                )
            )

        threads = {}
        for channel_id in args.channels_ids:
            threads.update(
                {
                    channel_id: threading.Thread(
                        target=fetch_channel_videos_list, args=(channel_id,)
                    )
                }
            )
            threads[channel_id].daemon = True
            threads[channel_id].start()

        with ProgressBar(
            title=HTML("<style bg='white' fg='black'>Fetching videos data...</style>")
        ) as pb:
            for channel_id, thread in pb(threads.items()):
                if thread.is_alive():
                    thread.join()

        to_watch_data = []
        for sub_data in data:
            video_titles = {}
            for video in sub_data["entries"]:
                video_titles.update({str(video["playlist_index"]): video["title"]})
                printers.print_media_data(args, video)

            videos_to_watch, show_extra, extra_count = prompts.pick_videos_prompt(
                video_titles
            )

            to_watch_data += [
                x
                for i, x in enumerate(sub_data["entries"])
                if i + playlist_start + 1 in videos_to_watch
            ]

        if show_extra:
            return to_watch_data, len(sub_data["entries"]) + playlist_start, extra_count
        elif to_watch_data:
            return to_watch_data, None, None

    return None, None, None


def following_channels_command(args) -> Optional[list]:
    """Run the following channels subcommand."""
    channels = get_following_channels(args.channels_file)

    if not channels:
        print_formatted_text(
            HTML(
                (
                    "<red>Error:</red> Can't find any channel on your list! "
                    + "Add some channels to use this command."
                ),
            )
        )
        return None

    data: list = []
    streams_titles = {}

    def fetch_stream_data(channel: dict) -> None:
        stream_data = extractors.extract_stream(channel["id"], args.verbosity)
        if stream_data:
            print_formatted_text(
                HTML(
                    f"<lime>[{len(data) + 1}]</lime> ({channel['name']}) "
                    + "is <green><b>online</b></green>"
                )
            )
            data.append(stream_data)
            streams_titles.update({str(len(data)): channel["name"]})
        elif not args.online:
            print_formatted_text(
                HTML(f"<red>[-]</red> ({channel['name']}) is <red><b>offline</b></red>")
            )

    threads = {}
    for channel in channels:
        threads.update(
            {channel["id"]: threading.Thread(target=fetch_stream_data, args=(channel,))}
        )
        threads[channel["id"]].daemon = True
        threads[channel["id"]].start()

    with ProgressBar(
        title=HTML("<style bg='white' fg='black'>Checking for channels...</style>")
    ) as pb:
        for channel_id, thread in pb(threads.items()):
            if thread.is_alive():
                thread.join()

    if data:
        to_watch = prompts.pick_streams_prompt(streams_titles)

        to_watch_data = [d for i, d in enumerate(data) if i + 1 in to_watch]
        if to_watch_data:
            return to_watch_data
    return []


def videos_command(args) -> Optional[list]:
    """Run the videos subcommand."""
    data = []

    def fetch_video_data(video_id: str) -> None:
        data.append(extractors.extract_video(video_id, args.verbosity))

    threads = {}
    for video_id in args.videos_ids:
        threads.update(
            {video_id: threading.Thread(target=fetch_video_data, args=(video_id,))}
        )
        threads[video_id].daemon = True
        threads[video_id].start()

    with ProgressBar(
        title=HTML("<style bg='white' fg='black'>Fetching videos data...</style>")
    ) as pb:
        for video_id, thread in pb(threads.items()):
            if thread.is_alive():
                thread.join()

    if all([not x for x in data]):
        # When all videos doesn't exist.
        return None

    return data

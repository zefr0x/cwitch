"""CLI prompts."""
from typing import Optional

from prompt_toolkit import prompt, HTML

from . import auto_completion
from . import input_validation


def formats_prompt(media_formats: list) -> int:
    """Prompt for picking a media fromat."""
    return media_formats.index(
        prompt(
            HTML(
                "<b>Pick a format:</b> "
                + "<gray>"
                + str(media_formats).replace("'", "")
                + "</gray>"
                + "\n<green>==></green> "
            ),
            default=media_formats[-1],
            completer=auto_completion.MediaFormatCompleter(media_formats),
            validator=input_validation.MediaFormatsValidator(media_formats),
        ).strip()
    )


def pick_videos_prompt(video_titles: dict) -> tuple[tuple[int, ...], bool, Optional[int]]:
    """Prompt to pick a video from a videos list."""
    results = prompt(
        HTML(
            "<b>Pick videos to watch:</b> "
            + "<gray>"
            + str(video_titles.keys()).replace("'", "")[10:-1]
            + "</gray>"
            + "\n<green>==></green> "
        ),
        completer=auto_completion.MediaTitlesCompleter(video_titles),
        validator=input_validation.NumbersListValidator(video_titles.keys()),
    ).split()

    show_extra = False
    extra_count = None

    for result in results:
        if result[0] == "x" and (result[1:].isdigit() or result[1:] == ""):
            results.remove(result)
            show_extra = True
            try:
                extra_count = int(result[1:])
            except ValueError:
                extra_count = None

    return tuple(map(int, results)), show_extra, extra_count


def pick_streams_prompt(streams_titles: dict) -> tuple:
    """Prompt to Pick a stream from a streams list."""
    return tuple(
        map(
            int,
            prompt(
                HTML(
                    "<b>Pick streams to watch:</b> "
                    + f"<gray>{list(range(1, len(streams_titles)+1))}</gray>"
                    + "\n<green>==></green> "
                ),
                completer=auto_completion.MediaTitlesCompleter(streams_titles),
                validator=input_validation.NumbersListValidator(streams_titles.keys()),
            ).split(),
        )
    )

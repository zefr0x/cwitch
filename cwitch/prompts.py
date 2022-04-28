"""CLI prompts."""
from prompt_toolkit import prompt, HTML

import auto_completion
import input_validation


def formats_prompt(media_formats: list) -> int:
    """Prompt for picking a media fromat."""
    return media_formats.index(
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


def pick_videos_prompt(video_titles: dict) -> tuple:
    """Prompt to pick a video from a videos list."""
    return tuple(
        map(
            int,
            prompt(
                HTML(
                    "<b>Pick videos to watch:</b> "
                    + f"<gray>{list(range(1, len(video_titles) + 1))}</gray>"
                    + "\n<green>==></green> "
                ),
                completer=auto_completion.MediaTitlesCompleter(video_titles),
                validator=input_validation.NumbersListValidator(video_titles.keys()),
            ).split(),
        )
    )


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

"""Auto completion classes for prompt-toolkit prompts."""
from prompt_toolkit.completion import Completer, Completion
from prompt_toolkit import HTML


class MediaTitlesCompleter(Completer):
    """Auto completion for media prompt when picking from a streams/videos list."""

    def __init__(self, media_titles: dict):
        """Take some data about the list."""
        self.media_titles = media_titles

    def get_completions(self, document, complete_event):
        """Yield a completion for every item."""
        for i, title in self.media_titles.items():
            if i not in document.text.split():
                # If the value was already picked no need to show it in the tap completion.
                yield Completion(
                    i, display=HTML(f"<b>[{i}]</b> {title}"), start_position=0
                )

        yield Completion(
            "x",
            display=HTML("<b>x[n]</b> Extra videos (e.g. 'x2' or 'x13')."),
            start_position=0,
        )


class MediaFormatCompleter(Completer):
    """Auto completion for media formats prompt when picking a format."""

    def __init__(self, media_formats: list):
        """Take a formats list."""
        self.media_formats = media_formats

    def get_completions(self, document, complete_event):
        """Yield a completion for every format."""
        for media_format in self.media_formats:
            yield Completion(media_format, start_position=-len(document.text))

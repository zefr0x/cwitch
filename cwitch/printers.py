"""Data printers."""
from prompt_toolkit import print_formatted_text, HTML


def print_media_data(args, media) -> None:
    """Print media data in a readable way."""
    from datetime import datetime, timedelta

    print_formatted_text(
        HTML(f"---- <aqua>{media['webpage_url_basename']}</aqua> ----"), end=""
    )
    if media["playlist_index"]:
        print_formatted_text(HTML(f"<lime>[{media['playlist_index']}]</lime>"))
    else:
        print()
    print_formatted_text(HTML("<b>Title:</b>"), media["title"])
    print_formatted_text(
        HTML("<b>Date:</b>"), datetime.fromtimestamp(int(media["timestamp"]))
    )
    try:
        print_formatted_text(
            HTML("<b>Duration:</b>"), timedelta(seconds=media["duration"])
        )
    except KeyError:
        # If it was a live stream there will be no duration
        pass
    if media["view_count"]:
        print_formatted_text(HTML("<b>View count:</b>"), media["view_count"])
    if args.verbosity:
        print_formatted_text(
            HTML("<orange>#</orange><b>Uploader:</b>"), media["uploader"]
        )
        print_formatted_text(
            HTML("<orange>#</orange><b>Webpage URL:</b>"), media["webpage_url"]
        )
        print_formatted_text(
            HTML("<orange>#</orange><b>Thumbnails URLs:</b>"),
            media["thumbnail"],
            media["thumbnails"],
        )
        print_formatted_text(
            HTML("<orange>#</orange><b>Stream URLs:</b>"),
            [(x["format_id"], x["url"]) for x in media["formats"]],
        )
        try:
            print_formatted_text(
                HTML("<orange>#</orange><b>Subtitles:</b>"), media["subtitles"]
            )
        except KeyError:
            pass
        print_formatted_text(HTML("<orange>#</orange><b>URL:</b>"), media["url"])
        print_formatted_text(HTML("<orange>#</orange><b>FPS:</b>"), media["fps"])
        print_formatted_text(
            HTML("<orange>#</orange><b>width and height:</b>"),
            media["width"],
            media["height"],
        )
        print_formatted_text(HTML("<orange>#</orange><b>Format:</b>"), media["format"])

"""Input validation classes for prompt-toolkit prompts."""
from typing import KeysView

from prompt_toolkit.validation import Validator, ValidationError


class NumbersListValidator(Validator):
    """Input validation when asking for the media indexes."""

    def __init__(self, existing_media: KeysView):
        """Take a list of the existing media."""
        self.existing_media = existing_media

    def validate(self, document):
        """Check if the input contains only numbers from the media list."""
        text = document.text
        values = text.split()

        if text and not all(
            [
                v.isdigit() or (v[0] == "x" and (v[1:].isdigit() or v[1:] == ""))
                for v in values
            ]
        ):
            # Get index of first non numeric character.
            # We want to move the cursor here.
            for i, c in enumerate(text):
                if not c.isdigit() and c not in (" ", "x"):
                    break

            raise ValidationError(
                message="This input contains not allowed non-numeric characters",
                cursor_position=i,
            )
        elif text and not all(
            [
                v in self.existing_media
                or (v[0] == "x" and (v[1:].isdigit()) or v[1:] == "")
                for v in values
            ]
        ):
            # Get index of first non existing media.
            # We want to move the cursor here.
            for value in values:
                if value not in self.existing_media:
                    i = text.index(value)
                    break

            raise ValidationError(
                message=f"Media number {value} does not exist", cursor_position=i
            )


class MediaFormatsValidator(Validator):
    """Input validation when asking for the media format."""

    def __init__(self, media_formats):
        """Take a list of the available formats."""
        self.media_formats = media_formats

    def validate(self, document):
        """Check if the format is valid."""
        if not document.text:
            raise ValidationError(message="You should pick a format")
        elif document.text.strip() not in self.media_formats:
            raise ValidationError(
                message=f"{document.text.strip()} is not a valid format"
            )

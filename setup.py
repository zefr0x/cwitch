"""Setup file for the library."""
from setuptools import setup, find_packages
from pathlib import Path

from cwitch import prog_name, __version__, __author__, __license__

HERE = Path(__file__).parent

README = (HERE / "README.md").read_text()

URL = "https://github.com/zer0-x/cwitch"
ISSUES = "https://github.com/zer0-x/cwitch/issues"
CHANGELOG = "https://github.com/zer0-x/cwitch/blob/main/CHANGELOG.md"

DESCRIPTION = "A CLI tool to watch Twitch live streams and videos."

setup(
    name=prog_name,
    version=__version__,
    author=__author__,
    license=__license__,
    description=DESCRIPTION,
    long_description_content_type="text/markdown",
    long_description=README,
    url=URL,
    project_urls={
        "Issues": ISSUES,
        "Changelog": CHANGELOG,
    },
    packages=find_packages(),
    install_requires=["youtube-dl", "python-mpv", "prompt-toolkit"],
    entry_points={"console_scripts": [f"{prog_name} = cwitch.cli:main"]},
    keywords=["twitch", "mpv", "youtube-dl", "stream", "cli", "live", "video"],
    classifiers=[
        "Environment :: Console",
        "Programming Language :: Python :: 3",
        "Intended Audience :: End Users/Desktop",
        "Topic :: Games/Entertainment",
        "Topic :: Internet",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
    ],
)

"""Setup file for the library."""
from pathlib import Path

from pkg_resources import parse_requirements
from setuptools import find_packages
from setuptools import setup

from cwitch import __about__ as about

HERE = Path(__file__).parent

README = (HERE / "README.md").read_text()

URL = "https://github.com/zefr0x/cwitch"
ISSUES = "https://github.com/zefr0x/cwitch/issues"
CHANGELOG = "https://github.com/zefr0x/cwitch/blob/main/CHANGELOG.md"

DESCRIPTION = "A CLI tool to watch Twitch live streams and videos."

with open("requirements/requirements.in", "r") as requirements_in:
    dependencies = [
        str(requirement) for requirement in parse_requirements(requirements_in)
    ]

setup(
    name=about.APP_NAME,
    version=about.VERSION,
    author=about.AUTHOR,
    license=about.LICENSE,
    description=DESCRIPTION,
    long_description_content_type="text/markdown",
    long_description=README,
    url=URL,
    project_urls={
        "Issues": ISSUES,
        "Changelog": CHANGELOG,
    },
    packages=find_packages(),
    install_requires=dependencies,
    entry_points={"console_scripts": [f"{about.APP_NAME} = cwitch.cli:main"]},
    keywords=[
        "twitch",
        "mpv",
        "youtube-dl",
        "yt-dlp",
        "stream",
        "cli",
        "live",
        "video",
    ],
    classifiers=[
        "Environment :: Console",
        "Programming Language :: Python :: 3",
        "Intended Audience :: End Users/Desktop",
        "Topic :: Games/Entertainment",
        "Topic :: Internet",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
    ],
)

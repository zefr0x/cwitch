# cwitch

A CLI tool for watching Twitch live streams and videos with the help of [mpv](https://mpv.io/) and [youtube-dl](https://youtube-dl.org/).

## Features

-   Watch one or more video with the ID.
-   Play a live stream with the channel's ID.
-   List a channel's videos and choose one or more to watch in a playlist form.
-   Check for the status of a channels list from a file and show who is online and who is offline, then choose some live streams to play.
-   Select a media format (e.g. 1080p60, 480p, Audio_Only) for every live stream or video you want to watch.

## Installation

### From pypi

To be added soon...

### From github

```shell
$ pip3 install https://github.com/zer0-x/cwitch/archive/refs/tags/v0.1.0.zip
```

> > > You might need to use `python3 -m pip` instead of just `pip3`

## Usage

Use the `--help` or `-h` option to see the help menu.

```shell
$ cwitch -h
```

There are three subcommands `c`, `s` and `v`. Choose a subcommand and then you can use the `-h` option to see the help menu for the subcommand.

### Creating a channels list

Create a file in you home directory with the path: `.config/cwitch/channels.ini` if there wasn't . Then add your channels list as following:

```ini
[Display Name]
id=channel_id

[Display Name]
id=channel_id
```

### Change the configurations

Create a file on you home directory with the path: `.config/cwitch/config.ini` if there wasn't. Then overwrite an existing option, like this:

```ini
[playlist_fetching]
# The default number of fetched videos when listing a channel's videos.
max_videos_count=5
```

> > There are no option other than this for now.

> For both config and channels list there is an example file in the repo.

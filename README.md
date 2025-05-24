# playlist-creator

## Description

Automating the management of M3U(8) playlists. Tests the streams availability and scoring the video output to get the best instances to software like Threadfin, TVHeadend, ChannelsDVR, Jellyfin, Plex, etc.

Multiple configuration files can be used to manage alternate lists and settings:

`python3 playlist-creator.py --config {path_to_alternate_config}`

## Installation

It is recommended to set up a virtual environment: https://docs.python.org/3/library/venv.html

- Clone this repo
- pip3 install -r requirements

## Usage

`usage: playlist_creator.py [-h] [--config CONFIG] [--git] [--trim] [--process]`

Create tailored M3U8 playlists.

options:
  -h, --help       show this help message and exit
  --config CONFIG  Use a different configuration file. Default is ./config/config.yaml
  --git            Upload the playlist and EPGs to GitHub/GitLab.
  --trim           Trims long files based on filters.
  --process        Processes the streams on the raw list to database.

## Using Git

The --git flag is used to upload the M3U and EPG files to a Git repo. You have to first create an empty repo and a key with write capabilities to use this.

## Overriding scores

By default the script uses:
```
        codec_score = {
            'hevc': 10,
            'h264': 7,
            'mpeg2video': 4,
        }
        resolution_score = {
            '1080': 10,
            '720': 4,
            '2160': 7,
            '576': 2,
        }
```
You can set any other scoring you need based on your M3U8 file.

## Trim filter

```
trim_filter: ['group-title="testing"',
              'group-title=another"']
```
This can be used to only score and evaluate streams in these groups. Useful for large lists.

## Dummy URL

The script will inject a random URL to keep # of instances consistent. This is important to pass the same number of streams (in the same order) to your player. This helps to prevent errors with mixed IDs.
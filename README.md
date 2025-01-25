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

`
usage: playlist_creator.py [-h] [--config CONFIG] [--git] [--trim] [--process]

Create tailored M3U8 playlists.

options:
  -h, --help       show this help message and exit
  --config CONFIG  Use a different configuration file. Default is ./config/config.yaml
  --git            Upload the playlist and EPGs to GitHub/GitLab.
  --trim           Trims long files based on filters.
  --process        Processes the streams on the raw list to database.
`
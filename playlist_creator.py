import os
import yaml
import argparse
from src.database_management import create_database, add_channels
from src.classesStream import Channel
from src.playlist_organizer import trim_playlist, process_playlist, scoring_streams, write_playlist
from src.misc_functions import FileDownloader, clean_episode_numbers, update_threadfin_api, replace_in_playlist
from src.upload_github import upload_files_to_github

def import_configuration(config_location):
    try:
        with open(config_location) as config_file:
            config = yaml.safe_load(config_file)
            minimum_config = ['database', 'output_file', 'playlist', 'EPG_1', 'channels']
            if set(minimum_config).issubset(set(list(config.keys()))) is False:
                print(f'Minimum config keys missing: {minimum_config}')
                print(config.keys())
                exit()
            return config
    except FileNotFoundError:
        print('Config file not found.')
        exit()
    except yaml.YAMLError:
        print(f'Error parsing {config_location}.')
        exit()

def print_config(_version, config_file, database_path, channels, playlist_url, download_path):
    print(f'Playlist creator {_version}.')
    number_channels = len(channels.keys())
    print(f"""
        Loaded config: {config_file}
        Database: {database_path}
        Channels: {number_channels}
        Playlist: {playlist_url}
        Download path: {download_path}
        \n""")

def main():
    parser =  argparse.ArgumentParser(description='Create tailored M3U8 playlists.')
    parser.add_argument('--config', nargs=1, help='Use a different configuration file. Default is ./config/config.yaml', type=str)
    parser.add_argument('--git', help='Upload the playlist and EPGs to GitHub/GitLab.', action='store_true')
    parser.add_argument('--trim', help='Trims long files based on filters.', action='store_true')
    parser.add_argument('--process', help='Processes the streams on the raw list to database.', action='store_true')
    args = parser.parse_args()
    upload_to_github = args.git
    config_other = args.config
    trim = args.trim
    process = args.process

    print('Importing configuration...')
    script_path = os.path.abspath(os.path.dirname(__file__))
    if config_other:
        config_file = config_other[0]
        loaded_config = import_configuration(config_location=f'{script_path}/{config_file}')
    else:
        config_file = 'config/config.yaml'
        loaded_config = import_configuration(config_location=f'{script_path}/{config_file}')

    """
    Important variables:
    """
    _version = 'v0.1'
    database = loaded_config['database']['path']
    database_path = f'{script_path}/{database}'
    channels = loaded_config['channels']
    download_path = f'{script_path}/assets'
    playlist_url = loaded_config['playlist']['url']

    print_config(_version, config_file, database_path, channels, playlist_url, download_path)

    """
    Create database:
    """

    create_database(database_path)

    """
    Load channels and add them to the database:
    """
    print('\nAdding channels:')
    for name in channels:
        aliases = channels[name]['aliases']
        channel = Channel(name, aliases)
        channel_tuple = [(channel.aliases, channel.picon)]
        add_channels(database_path, channel_tuple)

    """
    Downloading EPG and M3U to /assets/:
    """
    print('\nDownloading assets:')
    playlist = FileDownloader(download_path, playlist_url, loaded_config['playlist']['name']).download_file()
    if not playlist:
        print('Playlist failed to download, aborting.')
        exit()
    EPG_1 = FileDownloader(download_path, loaded_config['EPG_1']['url'], loaded_config['EPG_1']['name']).download_file()
    if EPG_1:
        clean_episode_numbers(EPG_1)
    
    try:
        EPG_2 = FileDownloader(download_path, loaded_config['EPG_2']['url'], loaded_config['EPG_2']['name']).download_file()
    except KeyError:
        print('Only 1 EPG was specified in the config file.')

    try:
        modify = loaded_config['playlist']['modify']['active']
        replacements = loaded_config['playlist']['modify']['modifier']
        if modify is True:
            replace_in_playlist(playlist, replacements)
    except KeyError:
        pass

    """
    Trimming the list. Useful for long playlists that might include unwanted streams that should not go to the DB.
    After adding the streams to the database after checking the details with FFProbe.
    """

    print('\nProcessing playlist, testing with FFProbe:')

    try:
        splitter = loaded_config['playlist']['splitter']
    except KeyError:
        print('Splitter is not defined in playlist config, using default.')
        splitter = '|'
    if trim is True and process is not True:
        playlist_name = trim_playlist(download_path, playlist, loaded_config['trim_filter'])
        process_playlist(database_path, playlist_name, channels, splitter)
    elif process is True and trim is not True:
        process_playlist(database_path, playlist, channels, splitter)
    elif process is True and trim is True:
        print(f'Both trim and process cannot be used.')
    
    """
    Scoring and sorting all of the streams found on the database.
    """
    print(f'\nRetrieving streams from {database_path} and scoring to write the final playlist:')
    streams = scoring_streams(database_path, channels)
    try:
        output_file = loaded_config['output_file']
    except KeyError:
        output_file = None
    if output_file:
        write_playlist(database_path, streams, f'{script_path}/assets/{output_file}', channels)
    else:
        write_playlist(database_path, streams, f'{script_path}/assets/playlist.m3u8', channels)


    """
    Uploading to GitHub/GitLab for easier management of the EPG and playlist. This is not necessary, it is added as a flag.
    """
    if upload_to_github is True:
        print('\nUploading to Git repo:')
        try:
            token = loaded_config['github']['token']
            repo_url = loaded_config['github']['url']
            upload_files_to_github(token, repo_url, download_path, f'Updating playlist and guides')
        except KeyError:
            print('Error uploading to GitHub. Check token and URL.')
    
    """
    If using Threadfin, the API can help update the info in real time.
    """
    try:
        threadfin = loaded_config['threadfin']['active']
        if threadfin is True:
            print('\nUpdating Threadfin:')
            update_threadfin_api(loaded_config['threadfin']['url'], 'epg')
            update_threadfin_api(loaded_config['threadfin']['url'], 'm3u')
    except KeyError:
        pass

    print('All done!')



if __name__ == '__main__':
    main()






import os
import yaml
import argparse
import logging
from logging.handlers import RotatingFileHandler
from src.tasks import initial_tasks, assets_download, run_tasks, score_playlist, upload_to_github, update_threadfin

def import_configuration(config_location):
    try:
        with open(config_location) as config_file:
            config = yaml.safe_load(config_file)
            minimum_config = ['database', 'output_file', 'playlist', 'EPG_1', 'channels']
            if set(minimum_config).issubset(set(list(config.keys()))) is False:
                print(f'Minimum config keys missing: {minimum_config}')
                print(config.keys())
                exit(1)
            return config
    except FileNotFoundError:
        print('Config file not found.')
        exit(1)
    except yaml.YAMLError:
        print(f'Error parsing {config_location}.')
        exit(1)

def setup_logging(loaded_config, script_path):
    log_path = f'{script_path}/logs'
    if not os.path.exists(log_path):
        os.makedirs(log_path)
    log_file = loaded_config['logging'].get('log_file', None)
    log_level = loaded_config['logging'].get('log_level', None)
    max_log_size = loaded_config['logging'].get('max_log_size', None)
    backup_count = loaded_config['logging'].get('backup_count', None)
    numeric_level = getattr(logging, log_level.upper(), logging.INFO)
    log_file_location = f'{log_path}/{log_file}'
    handler = RotatingFileHandler(log_file_location, maxBytes=max_log_size, backupCount=backup_count)
    handler.setFormatter(logging.Formatter("%(asctime)s - %(levelname)s - %(message)s", datefmt="%Y-%m-%d %H:%M:%S"))

    logging.basicConfig(
        level=numeric_level,
        format="%(asctime)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
        handlers=[handler, logging.StreamHandler()]
    )

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
    parser.add_argument('--score', help='Scores playlist based on existing DB.', action='store_true')
    args = parser.parse_args()
    git_enabled = args.git
    config_other = args.config
    trim = args.trim
    process = args.process
    score = args.score

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
    _version = 'v1.0'
    database = loaded_config['database']['path']
    database_path = f'{script_path}/{database}'
    channels = loaded_config['channels']
    download_path = f'{script_path}/assets'
    playlist_url = loaded_config['playlist']['url']
    picon_url = loaded_config['picon']['url']

    print_config(_version, config_file, database_path, channels, playlist_url, download_path)
    setup_logging(loaded_config, script_path)
    initial_tasks(database_path, channels, picon_url)

    playlist = assets_download(download_path, playlist_url, loaded_config)

    if score is True:
        score_playlist(database_path, channels, script_path, loaded_config)
    else:
        run_tasks(trim, process, database_path, download_path, playlist, channels, loaded_config)
        score_playlist(database_path, channels, script_path, loaded_config)

    if git_enabled is True:
        upload_to_github(download_path, loaded_config)

    update_threadfin(loaded_config)

    print('All done!')



if __name__ == '__main__':
    main()
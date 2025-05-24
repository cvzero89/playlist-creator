import logging
from src.database_management import create_database, add_channels
from src.classesStream import Channel
from src.playlist_organizer import trim_playlist, process_playlist, scoring_streams, write_playlist
from src.misc_functions import FileDownloader, clean_episode_numbers, update_threadfin_api, replace_in_playlist
from src.upload_github import upload_files_to_github

logger = logging.getLogger(__name__)

def initial_tasks(database_path, channels, picon_url):
    """
    Create database:
    """

    create_database(database_path)

    """
    Load channels and add them to the database:
    """
    logger.info('Adding channels...')
    for name in channels:
        aliases = channels[name]['aliases']
        channel = Channel(name, aliases, picon_url)
        channel_tuple = [(channel.aliases, channel.picon)]
        add_channels(database_path, channel_tuple)
    logger.info('Done!')

def assets_download(download_path, playlist_url, loaded_config):

    """
    Downloading EPG and M3U to /assets/:
    """
    logger.info('Downloading assets...')
    playlist = FileDownloader(download_path, playlist_url, loaded_config['playlist']['name']).download_file()
    if not playlist:
        print('Playlist failed to download, aborting.')
        logger.error('Playlist failed to download.')
        exit(1)
    EPG_1 = FileDownloader(download_path, loaded_config['EPG_1']['url'], loaded_config['EPG_1']['name']).download_file()
    if EPG_1:
        clean_episode_numbers(EPG_1)
    
    EPG_2_get = loaded_config.get('EPG_2', None)
    if EPG_2_get:
        EPG_2 = FileDownloader(download_path, loaded_config['EPG_2']['url'], loaded_config['EPG_2']['name']).download_file()
    else:
        print('Only 1 EPG has been defined.')

    modify = loaded_config['playlist']['modify']['active']
    if modify is True:
        replacements = loaded_config['playlist']['modify']['modifier']
        if modify is True:
            replace_in_playlist(playlist, replacements)
    logger.info('Playlist retrieved.')
    return playlist


def run_tasks(trim, process, database_path, download_path, playlist, channels, loaded_config):
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
        logger.error('Both trim and process cannot be used.')
    
def score_playlist(database_path, channels, script_path, loaded_config):
    """
    Scoring and sorting all of the streams found on the database.
    """
    print(f'\nRetrieving streams from {database_path} and scoring to write the final playlist:')
    override_scoring = loaded_config.get('override_scoring', None)
    dummy_url = loaded_config.get('dummy_url', 'https://streaming.rtvc.gov.co/TV_Senal_Colombia_live/smil:live.smil/playlist.m3u8')
    streams = scoring_streams(database_path, channels, override_scoring, dummy_url)
    try:
        output_file = loaded_config['output_file']
    except KeyError:
        output_file = None
    if output_file:
        write_playlist(database_path, streams, f'{script_path}/assets/{output_file}', channels, loaded_config['playlist']['writing'].values())
    else:
        write_playlist(database_path, streams, f'{script_path}/assets/playlist.m3u8', channels, loaded_config['playlist']['writing'].values())

def upload_to_github(download_path, loaded_config):
    """
    Uploading to GitHub/GitLab for easier management of the EPG and playlist. This is not necessary, it is added as a flag.
    """
    print('\nUploading to Git repo:')
    try:
        token = loaded_config['github']['token']
        repo_url = loaded_config['github']['url']
        upload_files_to_github(token, repo_url, download_path, f'Updating playlist and guides')
    except KeyError:
        print('Error uploading to Git. Check token and URL.')
        logger.error('Error uploading to Git.')
        

def update_threadfin(loaded_config):
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
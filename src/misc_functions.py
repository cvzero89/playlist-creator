from difflib import SequenceMatcher
import xml.etree.ElementTree as ET
import re
import logging
import os
import requests
import gzip
import shutil
import time
import random

logger = logging.getLogger(__name__)
script_path = os.path.abspath(os.path.dirname(__file__))

def similar(a, b, threshold=0.98, return_score=False):
    """
    Receives a list to compare with a name. Used for picon and streams matching.
    """
    if not return_score:
        for item in a:
            score = SequenceMatcher(None, item.lower(), b.lower()).ratio()
            if score >= threshold and return_score is False:
                logger.debug(f'Match {item} with {b} score: {score}')
                return True
    elif return_score:
        best_match = None
        best_score = 0
        for alias in a:
            score = SequenceMatcher(None, alias.lower(), b.lower()).ratio()
            if score > best_score:
                best_match = alias
                best_score = score
        return best_match, best_score
    return False

def get_picon_names():
    icon_path = f'{script_path}/../icon'
    icon_assets = f'{script_path}/../assets/icon'
    shutil.copytree(icon_path, icon_assets, dirs_exist_ok=True)
    files = os.walk(icon_path)
    filenames = sorted(next(files)[2])
    return filenames

picons = get_picon_names()

class FileDownloader:
    """
    A class to handle file downloads and processing based on file type or content.
    """

    def __init__(self, directory, url, rename):
        self.directory = directory
        os.makedirs(self.directory, exist_ok=True)
        self.url = url
        self.rename = rename
        self.skip_download = self._check_timestamps()

    def download_file(self):

        user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36'
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36'
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36'
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36'
            'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36'
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.1 Safari/605.1.15'
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 13_1) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.1 Safari/605.1.15'
        ]

        headers = {'User-Agent': random.choice(user_agents)}

        filename = os.path.basename(self.url)
        if not filename:
            logger.error("Invalid URL: No filename could be determined.")
            return None
        elif self.skip_download is True:
            return os.path.join(self.directory, self.rename)
        file_path = os.path.join(self.directory, filename)
        try:
            response = requests.get(self.url, stream=True, headers=headers)
            response.raise_for_status()
            with open(file_path, 'wb') as file:
                for chunk in response.iter_content(chunk_size=8192):
                    file.write(chunk)
            logger.info(f"Downloaded: {filename}")
            filename = self.process_file(filename)
            return filename
        except requests.exceptions.RequestException as e:
            logger.info(f"Failed to download {filename}: {e}")
            return None

    def process_file(self, filename):
        """
        Extracts .gz files for XMLs, renames everything else.
        """
        file_path = os.path.join(self.directory, filename)
        if filename.endswith('.gz'):
            return self._extract_gzip(file_path, self.rename)
        else:
            logger.debug(f"No processing needed for {filename}. Just renaming...")
            return self._rename_file(file_path, self.rename)

    def _extract_gzip(self, source, target_name):
        """
        Extracts a gzip-compressed file and saves it with a new name.
        """
        target_path = os.path.join(self.directory, target_name)
        try:
            with gzip.open(source, 'rb') as file_in, open(target_path, 'wb') as file_out:
                shutil.copyfileobj(file_in, file_out)
            os.remove(source)
            logger.debug(f"Extracted {source} to {target_path}")
            return target_path
        except Exception as e:
            logger.error(f"Failed to extract {source}: {e}")
            return None

    def _rename_file(self, source, target_name):
        """
        Renames a file.
        """
        target_path = os.path.join(self.directory, target_name)
        try:
            os.rename(source, target_path)
            logger.debug(f"Renamed {source} to {target_path}")
            return target_path
        except Exception as e:
            logger.error(f"Failed to rename {source} to {target_path}: {e}")
            return None
    
    def _check_timestamps(self):
        """
        Reduces unnecesary downloads (because the script could be rate-limited) when running it multiple times.
        """
        rename_path = os.path.join(self.directory, self.rename)
        if os.path.isfile(rename_path):
            creation_time = os.path.getctime(rename_path)
            current_time = time.time()
            return current_time - creation_time <= 24 * 60 * 60
        else:
            logger.info(f'File has not been downloaded recently.')
            return False

def clean_episode_numbers(xml_file):
    # Parse the XML file
    tree = ET.parse(xml_file)
    root = tree.getroot()

    # Iterate through each programme element
    for programme in root.findall('programme'):
        # Check if the title is "La Resistencia"
        title = programme.find('title')
        if title is not None and title.text == 'La revuelta':
            # Find all episode-num elements
            episode_nums = programme.findall('episode-num')

            # Keep only the correct episode-num format
            for episode_num in episode_nums:
                if 'system' in episode_num.attrib and episode_num.attrib['system'] == 'onscreen':
                    episode_num_text = episode_num.text
                    if not (episode_num_text and episode_num_text.startswith('S') and 'E' in episode_num_text):
                        programme.remove(episode_num)

    # Save the modified XML
    tree.write(xml_file, encoding='UTF-8', xml_declaration=True)

def sort_dictionary(channels):
    """
    Used to sort the scoring dictionary.
    """
    sorted_channels = {}
    for channel, streams in channels.items():
        sorted_streams = dict(sorted(streams.items(), key=lambda item: item[1][1], reverse=True))
        sorted_channels[channel] = sorted_streams
    return sorted_channels

def replace_in_playlist(playlist, replace_list):
    """
    Replaces strings in a file. Useful when the link does not match the service Acestream or other streaming service is running.
    """
    try:
        with open(playlist, 'r', encoding='utf-8') as file:
            content = file.read()

        pattern, replacement = replace_list
        updated_content = re.sub(pattern, replacement, content)

        with open(playlist, 'w', encoding='utf-8') as file:
            file.write(updated_content)

        logger.info(f"Replacements completed successfully in {playlist}.")

    except FileNotFoundError:
        logger.error(f"Error: The file '{playlist}' does not exist.")
    except Exception as e:
        logger.error(f"An error occurred: {e}")


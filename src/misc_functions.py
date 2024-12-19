from difflib import SequenceMatcher
import xml.etree.ElementTree as ET
import json
import re

def similar(a, b, threshold=0.98, return_score=False):
    """
    Receives a list to compare with a name. Used for picon and streams matching.
    """
    for item in a:
        score = SequenceMatcher(None, item.lower(), b.lower()).ratio()
        if score >= threshold and return_score is False:
            print(f'Match {item} with {b} score: {score}')
            return True
        elif return_score is True:
            return score
    return False

picons = [
"CANAL+ Premier League",
"CANAL+ Sport",
"DAZN 1 BAR",
"DAZN 1 HD",
"DAZN 1",
"DAZN 2 BAR",
"DAZN 2 HD",
"DAZN 2",
"DAZN 3 HD",
"DAZN 3",
"DAZN 4 HD",
"DAZN 4",
"DAZN 5",
"DAZN 6",
"DAZN LaLiga 2 HD",
"DAZN LaLiga 2",
"DAZN LaLiga 3",
"DAZN LaLiga 4",
"DAZN LaLiga 5",
"DAZN LaLiga Femenina 1",
"DAZN LaLiga Femenina 10",
"DAZN LaLiga Femenina 2",
"DAZN LaLiga Femenina 3",
"DAZN LaLiga Femenina 4",
"DAZN LaLiga Femenina 5",
"DAZN LaLiga Femenina 6",
"DAZN LaLiga Femenina 7",
"DAZN LaLiga Femenina 8",
"DAZN LaLiga Femenina 9",
"DAZN LaLiga Femenina",
"DAZN LaLiga HD",
"DAZN LaLiga",
"DAZN Women`s Football",
"Das Erste",
"ESPN 2",
"ESPN 3",
"ESPN Deportes",
"ESPN International",
"ESPN",
"Eurosport 1 HD",
"Eurosport 1",
"Eurosport 2 HD Xtra",
"Eurosport 2 HD",
"Eurosport 2",
"Eurosport 3 HD",
"Eurosport 3",
"Eurosport 360 1",
"Eurosport 360 2",
"Eurosport 360 3",
"Eurosport 360 4",
"Eurosport 360 5",
"Eurosport 360 6",
"Eurosport 360 7",
"Eurosport 360 8",
"Eurosport 360",
"Eurosport 4",
"Eurosport 4K",
"Eurosport 5",
"Eurosport 6",
"Eurosport 7",
"Eurosport 8",
"Eurosport 9",
"FOX SPORTS 2",
"FOX SPORTS 3",
"FOX SPORTS PREMIUM",
"FOX SPORTS",
"FOX",
"Gol Mundial 1",
"Gol Mundial 2 HD",
"Gol Mundial 2 UHD",
"Gol Mundial 2",
"Gol Mundial 3",
"Gol Mundial 4",
"Gol Mundial 5",
"Gol Mundial HD",
"Gol Mundial UHD",
"Gol Mundial",
"La 1 HD",
"La 1 UHD",
"LaLiga Plus FAST",
"LaLiga Plus",
"LaLiga SmartbankTV HD",
"LaLiga SmartbankTV M2 HD",
"LaLiga SmartbankTV M2",
"LaLiga SmartbankTV M3 HD",
"LaLiga SmartbankTV M3",
"LaLiga SmartbankTV M4 HD",
"LaLiga SmartbankTV M4",
"LaLiga SmartbankTV",
"LaLiga TV BAR 2",
"LaLiga TV BAR 3",
"LaLiga TV BAR 4",
"LaLiga TV BAR 5",
"LaLiga TV BAR 6",
"LaLiga TV BAR 7",
"LaLiga TV BAR 8",
"LaLiga TV BAR 9",
"LaLiga TV BAR HD",
"LaLiga TV BAR",
"LaLiga TV Hypermotion 10",
"LaLiga TV Hypermotion 11",
"LaLiga TV Hypermotion 12",
"LaLiga TV Hypermotion 2 HD",
"LaLiga TV Hypermotion 2",
"LaLiga TV Hypermotion 3 HD",
"LaLiga TV Hypermotion 3",
"LaLiga TV Hypermotion 4",
"LaLiga TV Hypermotion 5",
"LaLiga TV Hypermotion 6",
"LaLiga TV Hypermotion 7",
"LaLiga TV Hypermotion 8",
"LaLiga TV Hypermotion 9",
"LaLiga TV Hypermotion HD",
"LaLiga TV Hypermotion",
"LaLiga+ BARES",
"LaLiga+",
"Liga de Campeones BAR 10",
"Liga de Campeones BAR 11",
"Liga de Campeones BAR 12",
"Liga de Campeones BAR 2",
"Liga de Campeones BAR 3",
"Liga de Campeones BAR 4",
"Liga de Campeones BAR 5",
"Liga de Campeones BAR 6",
"Liga de Campeones BAR 7",
"Liga de Campeones BAR 8",
"Liga de Campeones BAR 9",
"Liga de Campeones BAR",
"M+ #0 HD",
"M+ #0",
"M+ #Vamos HD",
"M+ #Vamos",
"M+ Copa América 2 HD",
"M+ Copa América HD",
"M+ Cracks HD",
"M+ Cracks",
"M+ Deportes 1 HD",
"M+ Deportes 1",
"M+ Deportes 2 HD",
"M+ Deportes 2",
"M+ Deportes 3 HD",
"M+ Deportes 3",
"M+ Deportes 4",
"M+ Deportes 5",
"M+ Deportes 6",
"M+ Deportes 7",
"M+ Deportes 8",
"M+ Deportes HD",
"M+ Deportes",
"M+ Documentales HD",
"M+ Documentales",
"M+ Drama HD",
"M+ Drama",
"M+ Ellas #V HD",
"M+ Ellas #V",
"M+ Ellas Vamos HD",
"M+ Ellas Vamos",
"M+ LaLiga TV  BAR 4K",
"M+ LaLiga TV 2 HD",
"M+ LaLiga TV 2",
"M+ LaLiga TV 3 HD",
"M+ LaLiga TV 3",
"M+ LaLiga TV 4",
"M+ LaLiga TV 5",
"M+ LaLiga TV 6",
"M+ LaLiga TV 7",
"M+ LaLiga TV BAR 2",
"M+ LaLiga TV BAR 3",
"M+ LaLiga TV BAR 4",
"M+ LaLiga TV BAR 5",
"M+ LaLiga TV BAR",
"M+ LaLiga TV HD",
"M+ LaLiga TV UHD",
"M+ LaLiga TV",
"M+ Liga de Campeones 1 HD",
"M+ Liga de Campeones 1",
"M+ Liga de Campeones 10",
"M+ Liga de Campeones 11",
"M+ Liga de Campeones 12",
"M+ Liga de Campeones 13",
"M+ Liga de Campeones 2 BAR",
"M+ Liga de Campeones 2 HD",
"M+ Liga de Campeones 2 UHD",
"M+ Liga de Campeones 2",
"M+ Liga de Campeones 3 BAR",
"M+ Liga de Campeones 3 HD",
"M+ Liga de Campeones 3",
"M+ Liga de Campeones 4",
"M+ Liga de Campeones 5",
"M+ Liga de Campeones 6",
"M+ Liga de Campeones 7",
"M+ Liga de Campeones 8",
"M+ Liga de Campeones 9",
"M+ Liga de Campeones BAR",
"M+ Liga de Campeones HD",
"M+ Liga de Campeones UHD",
"M+ Liga de Campeones",
"M+ Los Goya",
"M+ Música HD",
"M+ Música",
"M+ Orgullo",
"M+ Originales HD",
"M+ Originales",
"M+ Oscars",
"M+ PopUp 2 HD",
"M+ PopUp 2",
"M+ PopUp HD",
"M+ PopUp",
"M+ San Sebastián",
"M+ Series 2 HD",
"M+ Series 2",
"M+ Series HD",
"M+ Series",
"M+ Superagentes",
"M+ Supercopa HD",
"M+ Supercopa de España",
"M+ Supercopa",
"M+ Suspense HD",
"M+ Suspense",
"M+ Terror",
"M+ Universo Tarantino",
"M+ Vacaciones",
"M+ Vamos HD",
"M+ Vamos",
"M+ Wimbledon UHD",
"M+ Woody Allen",
"M6",
"Movistar Plus+ 2 HD",
"Movistar Plus+ 2",
"Movistar Plus+ HD",
"Movistar Plus+",
"Premier Sports 1",
"Premier Sports 2",
"Premier Sports",
"Real Madrid TV",
"Sky Sport 1",
"Sky Sport 10",
"Sky Sport 11",
"Sky Sport 12",
"Sky Sport 13",
"Sky Sport 14",
"Sky Sport 2",
"Sky Sport 3",
"Sky Sport 4",
"Sky Sport 5",
"Sky Sport 6",
"Sky Sport 7",
"Sky Sport 8",
"Sky Sport 9",
"Sky Sport Action",
"Sky Sport Arena",
"Sky Sport Austria",
"Sky Sport Bundesliga 1",
"Sky Sport Bundesliga 10",
"Sky Sport Bundesliga 2",
"Sky Sport Bundesliga 3",
"Sky Sport Bundesliga 4",
"Sky Sport Bundesliga 5",
"Sky Sport Bundesliga 6",
"Sky Sport Bundesliga 7",
"Sky Sport Bundesliga 8",
"Sky Sport Bundesliga 9",
"Sky Sport Bundesliga",
"Sky Sport Cricket",
"Sky Sport F1",
"Sky Sport Football",
"Sky Sport Golf",
"Sky Sport Main Event",
"Sky Sport Mix",
"Sky Sport News",
"Sky Sport Premier League",
"Sky Sport Racing",
"Sky Sport Tennis",
"Sky Sport Top Event",
"Vamos BAR 2",
"Vamos BAR 3",
"Vamos BAR",
"beIN SPORTS 1",
"beIN SPORTS 2",
"beIN SPORTS 3",
"beIN SPORTS 4",
"beIN SPORTS MAX 10",
"beIN SPORTS MAX 4",
"beIN SPORTS MAX 5",
"beIN SPORTS MAX 6",
"beIN SPORTS MAX 7",
"beIN SPORTS MAX 8",
"beIN SPORTS MAX 9",
"beIN SPORTS XTRA ñ",
"beIN SPORTS XTRA",
"beIN SPORTS ñ",
"beIN SPORTS"
]

import os
import requests
import gzip
import shutil
import time

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
        filename = os.path.basename(self.url)
        if not filename:
            print("Invalid URL: No filename could be determined.")
            return None
        elif self.skip_download is True:
            return os.path.join(self.directory, self.rename)
        file_path = os.path.join(self.directory, filename)
        try:
            response = requests.get(self.url, stream=True)
            response.raise_for_status()
            with open(file_path, 'wb') as file:
                for chunk in response.iter_content(chunk_size=8192):
                    file.write(chunk)
            print(f"Downloaded: {filename}")
            filename = self.process_file(filename)
            return filename
        except requests.exceptions.RequestException as e:
            print(f"Failed to download {filename}: {e}")
            return None

    def process_file(self, filename):
        """
        Extracts .gz files for XMLs, renames everything else.
        """
        file_path = os.path.join(self.directory, filename)
        if filename.endswith('.gz'):
            return self._extract_gzip(file_path, self.rename)
        else:
            print(f"No processing needed for {filename}. Just renaming...")
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
            print(f"Extracted {source} to {target_path}")
            return target_path
        except Exception as e:
            print(f"Failed to extract {source}: {e}")
            return None

    def _rename_file(self, source, target_name):
        """
        Renames a file.
        """
        target_path = os.path.join(self.directory, target_name)
        try:
            os.rename(source, target_path)
            print(f"Renamed {source} to {target_path}")
            return target_path
        except Exception as e:
            print(f"Failed to rename {source} to {target_path}: {e}")
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
            print(f'File has not been downloaded recently.')
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

def update_threadfin_api(url, mode):

    # Define the URL and payload
    if mode == 'epg':
        payload = {
          "cmd": "update.xepg"
        }
    else:
        payload = {
          "cmd": "update.m3u"
        }      

    # Convert the payload to JSON
    payload_json = json.dumps(payload)

    # Set the headers to specify JSON content
    headers = {
        "Content-Type": "application/json"
    }

    # Send the POST request
    response = requests.post(url, data=payload_json, headers=headers)

    # Check the response
    if response.status_code == 200:
        # Request was successful
        print(f"POST request was successful: {mode}")
        print("Response JSON:", response.json())
    else:
        print(f"POST request failed with status code: {response.status_code} {mode}")
        print("Response text:", response.text)

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

        print(f"Replacements completed successfully in {playlist}.")

    except FileNotFoundError:
        print(f"Error: The file '{playlist}' does not exist.")
    except Exception as e:
        print(f"An error occurred: {e}")


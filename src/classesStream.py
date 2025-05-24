from datetime import datetime
import re
import logging
from src.prober import probing
from src.misc_functions import similar, picons
from src.database_management import find_channel_id

logger = logging.getLogger(__name__)

"""
Stream class to standarize the naming, cleaning up a lot that comes on the playlists and
finding the video information to add to the database.
"""
class Stream():
    def __init__(self, name, link, database_path):
        self.name = self.cleanup_name(name)
        self.link = link
        self.database_path = database_path
        

    def get_video_info(self):
        video_stream = probing(self.link)
        now = datetime.now().strftime("%m/%d/%Y, %H:%M:%S")
        if not video_stream:
            logger.debug(f'{self.link} contained no video information.')
            self.availability = False
            self.last_seen = False
            self.resolution = None
            self.video_codec = None
        else:
            self.video_codec = video_stream.get('codec_name', 'Unknown codec')
            self.video_width = int(video_stream.get('width', 0))
            self.video_height = int(video_stream.get('height', 0))
            self.resolution = f'{self.video_width}x{self.video_height}'
            self.availability = True
            self.last_seen = now

    def cleanup_name(self, name):
        cleaning = re.sub(r'(#####)?(U?F?HD)?( #####)?|4K|ᴴᴰ\ ᵐᶻ|HEVC|RAW|SD|\[LIVEEVENT\]|\(SOLO EVENTOS\)|(1080p|1080P|1080|1080 MultiAudio|720|720p)?  \w{1,4}$', '', name).strip()
        return cleaning
    
    def channel_id_finder(self, channel):
        self.channel_name = channel
        self.channel_id = find_channel_id(self.database_path, self.name)


"""
Used to add the channels to the database. 
"""
class Channel():
    def __init__(self, name, aliases, picon_url):
        self.name = name
        self.aliases = aliases
        self.picon_url = picon_url
        self.picon = self.get_icon()
    
    def get_icon(self):
        best_match = None
        best_score = 0
        for icon in picons:
            score = similar(self.aliases, icon, threshold=0.8, return_score=True)
            if score > best_score:
                best_match = icon
                best_score = score
        if best_score >= 0.60:
            return self.picon_url + best_match + '.png'
        else:
            logger.info(f"No match for channel: {self.name} (Best match: {best_match}, Score: {best_score})")
            return self.picon_url + '404.png'


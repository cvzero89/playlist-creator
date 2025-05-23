import logging
from src.classesStream import Stream
from src.misc_functions import similar, sort_dictionary
from src.database_management import add_stream, fetch_stream_details, fetch_logo

logger = logging.getLogger(__name__)

"""
Iterates through a playlist matching the name of the stream with the aliases on the configuration file.
The stream info is added to the database, including if it is available and details about the video.
"""

def process_playlist(database_path, playlist_name, channels, splitter='|'):
    matched_links = set()  # Use a set for faster lookups
    with open(playlist_name) as playlist_template:
        lines = playlist_template.readlines()
    
    i = 1
    while i < len(lines) - 1:  # Iterate through the lines
        if lines[i].startswith('#EXTINF:-1'):
            stream_name = lines[i].split(f"{splitter}")[-1].strip()
            stream_link = lines[i + 1].strip()
            stream = Stream(stream_name, stream_link, database_path)
            if stream_link in matched_links:  # Skip already matched links
                i += 1
                continue
            
            for channel, channel_data in channels.items():
                aliases = channel_data["aliases"]
                channel_wanted = channel_data["wanted"]
                
                if similar(aliases, stream.name):  # Match using the `similar` function
                    if channel_wanted:
                        logger.debug(f'{stream.name} with {stream.link}')
                        stream.get_video_info()  # Fetch additional info
                        stream.channel_id_finder(channel)
                        add_stream(database_path, stream)
                        matched_links.add(stream.link)  # Add to matched links
                        break  
                    else: 
                        print(f'{stream.name}, does not match {aliases}')
                        logger.info(f'{stream.name}, does not match {aliases}')
        i += 1  

"""
Long lists will take longer to complete, this function will reduce the number of streams to only what it is needed.
"""

def trim_playlist(path, name, trim_filter):
    input_file = name
    output_file = f'{path}/filtered_playlist.m3u8'

    with open(input_file, "r", encoding="utf-8") as infile, open(output_file, "w", encoding="utf-8") as outfile:
        outfile.write("#EXTM3U\n")  # Write the M3U8 header
        include_next_line = False
        
        for line in infile:
            if line.startswith('#EXTINF:-1') and any(target in line for target in trim_filter):
                outfile.write(line)
                include_next_line = True
            elif include_next_line and not line.startswith("#"):
                outfile.write(line)
                include_next_line = False
    return output_file

"""
Scoring the streams to only add the best ones to the actual playlist.
"""

def scoring_streams(database_path, channels):
    scored_streams = {}
    codec_score = {
        'hevc': 10,
        'h264': 7,
        'mpeg2video': 4,
    }
    resolution_score = {
        '1080': 10,
        '720': 7,
        '2160': 4,
        '576': 2,
    }
    for name in channels:
        aliases = channels[name]['aliases']
        aliases_formatted = "[" + ", ".join(f'"{name}"' for name in aliases) + "]"
        available_streams = fetch_stream_details(database_path, aliases_formatted)
        if not available_streams:
            logger.info(f'{name} has no available streams.')
            scored_streams[name] = {}
            scored_streams[name][0] = []
            data = 'https://streaming.rtvc.gov.co/TV_Senal_Colombia_live/smil:live.smil/playlist.m3u8', 20
            scored_streams[name][0].extend(data)
        else:
            for number, result in enumerate(available_streams):
                link, codec, resolution = result
                stream_score = codec_score.get(codec, 2) + resolution_score.get(resolution.split('x')[-1], 1)
                data = link, stream_score
                if name not in scored_streams.keys():
                    scored_streams[name] = {}
                scored_streams[name][number] = []
                scored_streams[name][number].extend(data)
    sorted_dictionary = sort_dictionary(scored_streams)
    return sorted_dictionary

"""
Writes a playlist taking into account the position on the configuration file to make sure they always retain the same tv_id.
"""

def write_playlist(database_path, streams, output_name, channels, writing_mod):
    if writing_mod:
        tv_id, group_title = writing_mod
    else:
        tv_id = 0
        group_title = 'IPTV'
    with open(output_name, 'w') as playlist:
        playlist.write('#EXTM3U\n')
        for channel in channels:
            if channels[channel]['wanted'] is not True:
                continue
            aliases = channels[channel]['aliases']
            aliases_formatted = "[" + ", ".join(f'"{channel}"' for channel in aliases) + "]"
            tv_logo = fetch_logo(database_path, aliases_formatted)
            instances = channels[channel]['instances']
            for x in range(instances):
                try:
                    stream_link = streams[channel][x][0]
                    stream_name = channel
                    tv_id = tv_id + 1
                    info = f'''\n#EXTINF:{tv_id} channelID="x-ID.{tv_id}" tvg-id=\"{tv_id}\" tvg-name="{stream_name}" tvg-logo="{tv_logo}" group-title="{group_title}", {stream_name}\n{stream_link}\n'''
                    playlist.write(info)
                except KeyError:
                    logger.info(f'Number of instances wanted {instances} for {channel}, but found {x} streams.')
                    continue

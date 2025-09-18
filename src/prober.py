import ffmpeg
import subprocess
import logging

logger = logging.getLogger(__name__)

def probing(link):
    timeout = 30000000
    try:
        probe = ffmpeg.probe(link, timeout=timeout)
        video_stream = next((stream for stream in probe['streams'] if stream['codec_type'] == 'video'), None)
        if video_stream is None:
            logger.debug('No video stream found')
        return video_stream
    except ffmpeg.Error as e:
        logger.debug(e)
    except subprocess.TimeoutExpired:
            timeout_seconds = timeout / 1000
            logger.debug(f"Timeout expired after {timeout_seconds} seconds while probing the link.")



import ffmpeg
import sys
import subprocess

def probing(link):
    timeout = 30000000
    try:
        probe = ffmpeg.probe(link, timeout=timeout)
        video_stream = next((stream for stream in probe['streams'] if stream['codec_type'] == 'video'), None)
        if video_stream is None:
            print('No video stream found', file=sys.stderr)
        return video_stream
    except ffmpeg.Error as e:
        print(e.stderr, file=sys.stderr)
    except subprocess.TimeoutExpired:
            timeout_seconds = timeout / 1000
            print(f"Timeout expired after {timeout_seconds} seconds while probing the link.", file=sys.stderr)



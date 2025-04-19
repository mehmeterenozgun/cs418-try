import os
import subprocess
from config import SEGMENT_DIR, THUMBNAIL_DIR

def generate_thumbnails():
    """
    For each video segment (e.g. .m4s or .mp4) in your DASH output,
    extract the first frame as a JPEG thumbnail.
    """
    os.makedirs(THUMBNAIL_DIR, exist_ok=True)
    for root, _, files in os.walk(SEGMENT_DIR):
        for f in files:
            if f.endswith(('.m4s', '.mp4')):
                seg_path = os.path.join(root, f)
                thumb_path = os.path.join(THUMBNAIL_DIR, f"{f}.jpg")
                subprocess.run([
                    'ffmpeg', '-y', '-i', seg_path,
                    '-vf', 'thumbnail', '-frames:v', '1',
                    thumb_path
                ])
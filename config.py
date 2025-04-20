import os

import os, platform

if platform.system() == 'Darwin':
    INPUT_FORMAT = 'avfoundation'
    VIDEO_DEVICE = 0           # integer, not string
    AUDIO_DEVICE = 0
else:
    INPUT_FORMAT = 'v4l2'
    VIDEO_DEVICE = '/dev/video0'
    AUDIO_DEVICE = 'default'

# … rest of config unchanged …

# ... the rest of your constants (OUTPUT_DIR, CODECS, etc.) stay the same# ——— Output Paths ———
OUTPUT_DIR     = os.getenv('OUTPUT_DIR', './output')
SEGMENT_DIR    = os.path.join(OUTPUT_DIR, 'dash')
THUMBNAIL_DIR  = os.path.join(OUTPUT_DIR, 'thumbnails')

# ——— HTTP Server Settings ———
HOST           = '0.0.0.0'
PORT           = 8000

# ——— DASH Encoding Parameters ———
VIDEO_CODEC    = 'libx264'   # H.264/AVC
AUDIO_CODEC    = 'aac'       # AAC audio
SEGMENT_SIZES  = [2, 4, 6]   # seconds, to test latency with different segment durations
STREAM_PROFILES = [
    {'resolution': '1920x1080', 'bitrate': '5000k'},
    {'resolution': '1280x720',  'bitrate': '3000k'},
    {'resolution': '640x360',   'bitrate': '1000k'},
]

# ——— Motion Detection ———
MOTION_MIN_AREA = 2000
MOTION_THRESHOLD = 0.05# min contour area in pixels to count as motion
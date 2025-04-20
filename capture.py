import subprocess
import os
from config import INPUT_FORMAT, VIDEO_DEVICE, AUDIO_DEVICE, SEGMENT_SIZES, VIDEO_CODEC, AUDIO_CODEC, SEGMENT_DIR, STREAM_PROFILES

def ensure_dirs():
    os.makedirs(SEGMENT_DIR, exist_ok=True)


def build_single_bitrate_command(seg_size):
    # ensure output folder exists
    out_dir = os.path.join(SEGMENT_DIR, f'{seg_size}s')
    os.makedirs(out_dir, exist_ok=True)
    mpd_path = os.path.join(out_dir, 'stream.mpd')

    # on macOS with avfoundation you can capture A+V in one input
    input_spec = f"{VIDEO_DEVICE}:{AUDIO_DEVICE}" if INPUT_FORMAT == 'avfoundation' else VIDEO_DEVICE
    # on macOS live‑DASH you must force wallclock timestamps and genpts
    common_flags = [
            '-hide_banner',
            '-fflags', '+genpts',
            '-use_wallclock_as_timestamps', '1',
            '-thread_queue_size', '4096',
    ]
    cmd = [
            'ffmpeg',
            *common_flags,
            '-f', INPUT_FORMAT,
            '-framerate', '30',
            '-video_size', STREAM_PROFILES[0]['resolution'],  # ← capture at max resolution (e.g. 1920x1080)
            '-i', input_spec,
            '-preset', 'ultrafast',
            '-tune', 'zerolatency',
            '-g', '60',
            '-keyint_min', '60',
            '-sc_threshold', '0',
            '-vf', 'fps=fps=30',
            '-pix_fmt', 'yuv420p',
            '-c:v', VIDEO_CODEC,
            '-c:a', AUDIO_CODEC,
            '-vsync', 'passthrough',
            '-async', '1',
            '-f', 'dash',
            '-use_template', '1',
            '-use_timeline', '1',
            '-live', '1',
            '-window_size', '300',  # 300 * seg_size(2s) = 600 s = 10 min
            '-extra_window_size', '50',
            '-seg_duration', str(seg_size),
            mpd_path,
        ]

    return cmd
def build_adaptive_dash_command(seg_size):
    ensure_dirs()

    # output folder & MPD path
    out_dir  = os.path.join(SEGMENT_DIR, f'adaptive_{seg_size}s')
    os.makedirs(out_dir, exist_ok=True)
    mpd_path = os.path.join(out_dir, 'stream.mpd')

    # 1) build the filter graph to split+scale video into three outputs
    #    labels: [v0out] 1920x1080, [v1out] 1280x720, [v2out] 640x360
    # split → scale → enforce 30 fps & yuv420p on each rendition
    filter_complex_string = (
         "[0:v]fps=fps=30,split=3[v0][v1][v2];"
         "[v0]scale={res0},format=yuv420p[v0out];"
         "[v1]scale={res1},format=yuv420p[v1out];"
         "[v2]scale={res2},format=yuv420p[v2out]"
        ).format(
            res0 = STREAM_PROFILES[0]['resolution'],  # 1920x1080
            res1 = STREAM_PROFILES[1]['resolution'],  # 1280x720
            res2 = STREAM_PROFILES[2]['resolution']  # 640x360
        )

    common_flags = [
        '-hide_banner',
        '-fflags', '+genpts',
        '-use_wallclock_as_timestamps', '1',
        '-thread_queue_size', '4096',
    ]
    # 2) assemble the ffmpeg command
    cmd = [
        'ffmpeg',
        # ——— inputs ———
        *common_flags,
        '-f', INPUT_FORMAT,
        '-framerate', '30',
        '-video_size', STREAM_PROFILES[0]['resolution'],  # pick a capture size
        '-i', f'{VIDEO_DEVICE}',      # <-- input 0: video-only
        '-f', INPUT_FORMAT,
        '-i', f':{AUDIO_DEVICE}',      # <-- input 1: audio-only

        # ——— filtering & mapping ———
        '-filter_complex', filter_complex_string,
        # video renditions:+
        # per‑stream bitrate specifiers (match streams to profiles)  [oai_citation_attribution:0‡Stack Overflow](https://stackoverflow.com/questions/48256686/how-to-create-multi-bit-rate-dash-content-using-ffmpeg-dash-muxer?utm_source=chatgpt.com)
        '-map', '[v0out]', '-c:v:0', VIDEO_CODEC, '-b:v:0', STREAM_PROFILES[0]['bitrate'],
        '-map', '[v1out]', '-c:v:1', VIDEO_CODEC, '-b:v:1', STREAM_PROFILES[1]['bitrate'],
        '-map', '[v2out]', '-c:v:2', VIDEO_CODEC, '-b:v:2', STREAM_PROFILES[2]['bitrate'],
        # audio from input 1:
        '-map', '1:a',       '-c:a', AUDIO_CODEC,

        # ——— DASH live settings ———
        '-f', 'dash',
        '-use_template',     '1',
        '-use_timeline',     '1',
        '-live',             '1',
        '-window_size',      '300',
        '-extra_window_size','50',
        '-adaptation_sets', "id=0,streams=0,1,2 id=1,streams=3",
        '-seg_duration',     str(seg_size),

        mpd_path
    ]

    print(f"Starting adaptive DASH ({seg_size}s segments):", " ".join(cmd))
    return cmd

def start_dash_stream():
    """
    Launches one single‑bitrate and one adaptive‑bitrate FFmpeg process
    for each segment size in parallel.
    """
    ensure_dirs()
    #for seg in SEGMENT_SIZES:
        # Single‑bitrate live DASH
    #cmd1 = build_single_bitrate_command(6)
    #print(f"Starting DASH ({6}s segments):", " ".join(cmd1))
    #subprocess.Popen(cmd1)

        # Adaptive‑bitrate live DASH
    cmd2 = build_adaptive_dash_command(2)
    print(f"Starting adaptive DASH ({2}s segments):", " ".join(cmd2))
    subprocess.Popen(cmd2)

if __name__ == '__main__':
    start_dash_stream()
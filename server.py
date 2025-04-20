import threading, time, subprocess
from flask import (
    Flask, send_from_directory,
    jsonify, render_template,
    Response, request
)
from config import HOST, PORT, SEGMENT_DIR
from motion import MotionDetector

app = Flask(
    __name__,
    static_folder=SEGMENT_DIR,
    template_folder='templates'
)
STREAM_START = None
# shared motion event state
motion_event = {'detected': False, 'timestamp': None, 'offset': None}

@app.route('/')
def index():
    return render_template('player.html')

@app.route('/dash/<path:filename>')
def dash_files(filename):
    return send_from_directory(SEGMENT_DIR, filename)

@app.route('/motion')
def motion_status():
    global motion_event
    resp = motion_event.copy()
    motion_event['detected'] = False
    motion_event['timestamp'] = None
    return jsonify(resp)

def motion_callback(timestamp):
    motion_event['detected'] = True
    # wall‑clock
    ts = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(timestamp))
    # offset from stream start, in seconds
    off = timestamp - STREAM_START
    motion_event['detected'] = True
    motion_event['timestamp'] = ts
    motion_event['offset'] = off

def start_motion_detector():
    md = MotionDetector(callback=motion_callback)
    t = threading.Thread(target=md.start, daemon=True)
    t.start()

if __name__ == '__main__':
    import capture

    STREAM_START = time.time()
    capture.start_dash_stream()
    start_motion_detector()
    app.run(host=HOST, port=PORT, threaded=True)
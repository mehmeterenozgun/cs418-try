import threading, time
from flask import (
    Flask, send_from_directory,
    jsonify, render_template
)
from config import HOST, PORT, SEGMENT_DIR, THUMBNAIL_DIR
from motion import MotionDetector

app = Flask(
    __name__,
    static_folder=SEGMENT_DIR,
    template_folder='templates'
)

# shared motion event state
motion_event = {'detected': False, 'timestamp': None}

@app.route('/')
def index():
    return render_template('player.html')

@app.route('/dash/<path:filename>')
def dash_files(filename):
    return send_from_directory(SEGMENT_DIR, filename)

@app.route('/thumbnails/<path:filename>')
def thumbnails(filename):
    return send_from_directory(THUMBNAIL_DIR, filename)

@app.route('/motion')
def motion_status():
    global motion_event
    resp = motion_event.copy()
    motion_event['detected'] = False
    motion_event['timestamp'] = None
    return jsonify(resp)

def motion_callback():
    global motion_event
    motion_event['detected'] = True
    motion_event['timestamp'] = time.strftime("%Y-%m-%d %H:%M:%S")

def start_motion_detector():
    md = MotionDetector(callback=motion_callback)
    md.start()

if __name__ == '__main__':
    import capture

    # 1) start DASH segmenters
    capture.start_dash_stream()


    # run Flask in a background thread
    flask_thread = threading.Thread(
        target=lambda: app.run(host=HOST, port=PORT, threaded=True),
        daemon=True
    )
    flask_thread.start()

    start_motion_detector()
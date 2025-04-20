import os
os.environ['OPENCV_AVFOUNDATION_SKIP_AUTH'] = '1'
import cv2
from config import VIDEO_DEVICE, MOTION_MIN_AREA
import platform
import time

class MotionDetector:
    def __init__(self, callback):
        if platform.system() == 'Darwin':
            # use AVFoundation; VIDEO_DEVICE must be an int
            self.cam = cv2.VideoCapture(int(VIDEO_DEVICE), cv2.CAP_AVFOUNDATION)
        else:
            # on Linux use the v4l2 path
            self.cam = cv2.VideoCapture(VIDEO_DEVICE)
        self.callback = callback
        self.avg = None
        self._last_alert = 0

    def start(self):
        while True:
            ret, frame = self.cam.read()
            if not ret:
                continue
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            gray = cv2.GaussianBlur(gray, (21, 21), 0)

            if self.avg is None:
                self.avg = gray.copy().astype("float")
                continue

            # accumulate background model
            cv2.accumulateWeighted(gray, self.avg, 0.5)
            # find difference between current frame and running average
            delta = cv2.absdiff(gray, cv2.convertScaleAbs(self.avg))
            thresh = cv2.threshold(delta, 5, 255, cv2.THRESH_BINARY)[1]
            thresh = cv2.dilate(thresh, None, iterations=2)

            # detect contours
            contours, _ = cv2.findContours(
                thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE
            )
            for c in contours:
                if cv2.contourArea(c) < MOTION_MIN_AREA:
                    continue
                # motion detected!
                now = time.time()
                if now - self._last_alert > 5:
                    self.callback()
                    self._last_alert = now
                break